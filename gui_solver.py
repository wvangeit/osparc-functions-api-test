import json
import pathlib as pl
import time
import zipfile

import osparc
import osparc_client
import tkinter as tk
from tkinter import ttk

conf_path = pl.Path("./conf.json")
conf_dict = json.loads(conf_path.read_text(encoding="utf-8"))
configuration = osparc.Configuration(**conf_dict)

SOLVER_KEY = "simcore/services/comp/osparc-python-runner"
SOLVER_VERSION = "1.2.0"

DEFAULT_FUNCTION_CODE = \
"""
import numpy as np

def main(x=None,y=None):
    return {'2D Sinc': np.sinc(x) * np.sinc(y)}
"""
DEFAULT_FUNCTION_INPUTS = \
"""
{"x": 0.1, "y": 2.0}
"""

FILES_DIR = pl.Path("./gui_solver_files")


class SolverGUI:
    def __init__(self, tk_root, client_instance):
        self.root = tk_root
        self.root.title("Solver Function GUI")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#f5f5f5")

        self.api_instance = osparc_client.FunctionsApi(client_instance)
        self.job_api_instance = osparc_client.FunctionJobsApi(client_instance)
        self.file_client_instance = osparc_client.FilesApi(client_instance)
        self.file_instance = osparc.FilesApi(client_instance)

        # Initialize attributes used later
        self.inputs_file = None
        self.main_file = None
        self.pythoncode_file = None
        self.registered_function = None
        self.registered_function_id = None

        # Status display
        self.status_label = ttk.Label(self.root, text="Status: Idle", anchor="w", background="#f5f5f5", font=("Arial", 12))
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Buttons
        self.upload_code_button = ttk.Button(self.root, text="Upload Code", command=self.upload_code)
        self.upload_code_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.upload_inputs_button = ttk.Button(self.root, text="Upload Inputs", command=self.upload_inputs)
        self.upload_inputs_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.register_function_button = ttk.Button(self.root, text="Register Function", command=self.register_function)
        self.register_function_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.run_function_button = ttk.Button(self.root, text="Run Function", command=self.run_function)
        self.run_function_button.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Multiline text input for function code
        self.input_label = ttk.Label(self.root, text="Function Code:", background="#f5f5f5", font=("Arial", 12))
        self.input_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.input_code = tk.Text(self.root, height=10, width=80, bg="#eaeaea", font=("Courier", 14))
        self.input_code.insert("1.0", DEFAULT_FUNCTION_CODE)
        self.input_code.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # Multiline text input for function inputs
        self.inputs_label = ttk.Label(self.root, text="Function Inputs (JSON):", background="#f5f5f5", font=("Arial", 12))
        self.inputs_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.inputs_text = tk.Text(self.root, height=10, width=80, bg="#eaeaea", font=("Courier", 14))
        self.inputs_text.insert("1.0", DEFAULT_FUNCTION_INPUTS)
        self.inputs_text.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # Add a scrollable frame for the output text
        self.output_frame = ttk.LabelFrame(self.root, text="Output Log", padding=(10, 10))
        self.output_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.output_scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical")
        self.output_scrollbar.pack(side="right", fill="y")

        self.output_text = tk.Text(self.output_frame, height=15, width=80, state="disabled", yscrollcommand=self.output_scrollbar.set, bg="#eaeaea", font=("Courier", 14))
        self.output_text.pack(side="left", fill="both", expand=True)

        self.output_scrollbar.config(command=self.output_text.yview)

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(7, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def log_output(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", f"{message}\n")
        self.output_text.config(state="disabled")
        self.output_text.see("end")

    def upload_code(self):
        self.update_status("Uploading code...")

        self.main_file = self.file_client_instance.upload_file(file=str(pl.Path(FILES_DIR) / "main.py"))
        self.log_output(f"Uploaded main file {self.main_file}\n")

        function_code_path = pl.Path(FILES_DIR) / "function_code.py"
        function_code = self.input_code.get("1.0", "end").strip()
        self.log_output(f"Received function code: [{function_code}]\nSaving to file and uploading..\n")

        function_code_path.write_text(function_code)

        self.pythoncode_file = self.file_client_instance.upload_file(file=str(function_code_path))

        self.log_output(f"Uploaded function code file {self.pythoncode_file}\n")
        self.log_output("Code uploaded successfully.\n")
        self.update_status("Idle")

    def upload_inputs(self):
        self.update_status("Uploading inputs...")
        function_inputs = self.inputs_text.get("1.0", "end").strip()

        function_inputs_path = pl.Path(FILES_DIR) / "function_inputs.json"
        function_inputs_path.write_text(function_inputs)
        self.inputs_file = self.file_client_instance.upload_file(
            str(function_inputs_path),
        )

        self.log_output(f"Uploaded inputs file {self.inputs_file}\n")

        self.log_output("Inputs uploaded successfully.\n")
        self.update_status("Idle")

    def register_function(self):
        self.update_status("Registering function...")

        solver_function = osparc_client.Function(
            osparc_client.SolverFunction(
                title="SincSolver",
                description="2D sinc using solver",
                solver_key=SOLVER_KEY,
                solver_version=SOLVER_VERSION,
                default_inputs={"input_1": self.main_file, "input_2": self.pythoncode_file},
            )
        )
        self.log_output(f"Built function: {solver_function.to_dict()}\n")

        self.registered_function = self.api_instance.register_function(
            solver_function.model_dump()
        )
        self.registered_function_id = self.registered_function.to_dict()['uid']
        self.log_output("Registering function with the solver...")
        self.log_output("Function registered successfully.\n")
        self.update_status("Idle")

    def run_function(self):
        self.update_status("Running function...")
        self.log_output("Running function...")
        function_job = self.api_instance.run_function(self.registered_function_id, {"input_3": self.inputs_file})

        function_job_uid = function_job.to_dict()["uid"]

        import threading

        def monitor_job():
            while (
                job_status := self.job_api_instance.function_job_status(function_job_uid).status
            ) not in ("SUCCESS", "FAILED"):
                self.log_output(f"Job status: {job_status}")
                time.sleep(5)
            self.log_output(f"Job status: {job_status}")
            job_output_dict = self.job_api_instance.function_job_outputs(function_job_uid)

            downloaded_file = self.file_instance.download_file(
                job_output_dict["output_1"]["id"],
                destination_folder=pl.Path(FILES_DIR),
            )
            self.log_output(f"Downloaded file: {downloaded_file}")
            with zipfile.ZipFile(downloaded_file, "r") as zip_file:
                job_output = json.loads(
                    zip_file.read("function_outputs.json").decode("utf-8")
                )

            self.log_output(f"Job output: {job_output}")

            # Simulate function execution
            self.log_output("Function executed successfully.")
            self.update_status("Idle")

        monitor_thread = threading.Thread(target=monitor_job, daemon=True)
        monitor_thread.start()

if __name__ == "__main__":
    with osparc.ApiClient(configuration) as api_client:
        root = tk.Tk()
        app = SolverGUI(root, api_client)
        root.mainloop()


# def main():
#     with osparc.ApiClient(configuration) as api_client:

#         received_function = api_instance.get_function(function_id)
#         print(f"Received function: {received_function.to_dict()}\n")

#         functions_list = api_instance.list_functions()
#         print(
#             f"{len(functions_list)} functions in the database: {[(function.to_dict()['uid'], function.to_dict()['title']) for function in functions_list]}\n"
#         )

#         function_jobs_list = job_api_instance.list_function_jobs()
#         print(
#             f"{len(function_jobs_list)} function_jobs in the database: {[(function_job.to_dict()['uid'], function_job.to_dict()['title']) for function_job in function_jobs_list]}\n"
#         )

      
