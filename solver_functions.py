import json
import pathlib as pl
import time
import zipfile

import osparc
import osparc_client
import urllib3

conf_path = pl.Path("./conf.json")
conf_dict = json.loads(conf_path.read_text())
configuration = osparc.Configuration(**conf_dict)

SOLVER_KEY = "simcore/services/comp/osparc-python-runner"
SOLVER_VERSION = "1.2.0"

function_code = """
import numpy as np

def main(x=None,y=None):
    return np.sinc(x) * np.sinc(y)
"""


def main():
    with osparc.ApiClient(configuration) as api_client:
        api_instance = osparc_client.FunctionsApi(api_client)
        job_api_instance = osparc_client.FunctionJobsApi(api_client)
        file_client_instance = osparc_client.FilesApi(api_client)
        file_instance = osparc.FilesApi(api_client)

        inputs_file = file_client_instance.upload_file(
            file="./solver_files/function_inputs.json"
        )
        if not inputs_file or not hasattr(inputs_file, "id"):
            raise ValueError("Failed to upload inputs file or missing 'id' attribute.")
        print(f"Uploaded inputs file {inputs_file}\n")

        main_file = file_client_instance.upload_file(file="./solver_files/main.py")
        print(f"Uploaded main file {main_file.model_dump()}\n")

        function_code_path = pl.Path("solver_files") / "function_code.py"
        function_code_path.write_text(function_code)

        pythoncode_file = file_client_instance.upload_file(file=str(function_code_path))

        print(f"Uploaded function code file {pythoncode_file}\n")

        solver_function = osparc_client.Function(
            osparc_client.SolverFunction(
                title="SincSolver",
                description="2D sinc using solver",
                solver_key=SOLVER_KEY,
                solver_version=SOLVER_VERSION,
                default_inputs={"input_1": main_file, "input_2": pythoncode_file},
            )
        )
        print(f"Built function: {solver_function.to_dict()}\n")

        while True:
            try:
                registered_function = api_instance.register_function(
                    solver_function.model_dump()
                )
            except urllib3.exceptions.MaxRetryError:
                print("Waiting for a connection ...")
                time.sleep(5)
            else:
                break
        print(f"Registered function: {registered_function.to_dict()}\n")

        function_id = registered_function.to_dict()["uid"]

        print(f"Function id: {function_id}\n")

        received_function = api_instance.get_function(function_id)
        print(f"Received function: {received_function.to_dict()}\n")

        functions_list = api_instance.list_functions()
        print(
            f"{len(functions_list)} functions in the database: {[(function.to_dict()['uid'], function.to_dict()['title']) for function in functions_list]}\n"
        )

        function_jobs_list = job_api_instance.list_function_jobs()
        print(
            f"{len(function_jobs_list)} function_jobs in the database: {[(function_job.to_dict()['uid'], function_job.to_dict()['title']) for function_job in function_jobs_list]}\n"
        )

        function_job = api_instance.run_function(function_id, {"input_3": inputs_file})

        function_job_uid = function_job.to_dict()["uid"]

        while (
            job_status := job_api_instance.function_job_status(function_job_uid).status
        ) not in ("SUCCESS", "FAILED"):
            print(f"Job status: {job_status}")
            time.sleep(1)
        print(f"Job status: {job_status}")

        job_output_dict = job_api_instance.function_job_outputs(function_job_uid)
        print(f"\nJob output: {job_output_dict}")

        downloaded_file = file_instance.download_file(
            job_output_dict["output_1"]["id"],
            destination_folder=pl.Path("./solver_files"),
        )
        print(f"Downloaded file: {downloaded_file}")
        with zipfile.ZipFile(downloaded_file, "r") as zip_file:
            job_output = json.loads(
                zip_file.read("function_outputs.json").decode("utf-8")
            )

        print(f"Job output: {job_output}")


if __name__ == "__main__":
    main()

# import tkinter as tk
# from tkinter import ttk, messagebox
# class SolverGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Solver Function GUI")

#         # Status display
#         self.status_label = ttk.Label(root, text="Status: Idle", anchor="w")
#         self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

#         # Buttons
#         self.upload_inputs_button = ttk.Button(root, text="Upload Inputs", command=self.upload_inputs)
#         self.upload_inputs_button.grid(row=1, column=0, padx=5, pady=5)

#         self.register_function_button = ttk.Button(root, text="Register Function", command=self.register_function)
#         self.register_function_button.grid(row=1, column=1, padx=5, pady=5)

#         self.run_function_button = ttk.Button(root, text="Run Function", command=self.run_function)
#         self.run_function_button.grid(row=2, column=0, padx=5, pady=5)

#         self.view_results_button = ttk.Button(root, text="View Results", command=self.view_results)
#         self.view_results_button.grid(row=2, column=1, padx=5, pady=5)

#         # Output display
#         self.output_text = tk.Text(root, height=15, width=50, state="disabled")
#         self.output_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")

#     def log_output(self, message):
#         self.output_text.config(state="normal")
#         self.output_text.insert("end", f"{message}\n")
#         self.output_text.config(state="disabled")
#         self.output_text.see("end")

#     def upload_inputs(self):
#         self.update_status("Uploading inputs...")
#         self.log_output("Uploading input files...")
#         # Simulate upload process
#         self.log_output("Inputs uploaded successfully.")
#         self.update_status("Idle")

#     def register_function(self):
#         self.update_status("Registering function...")
#         self.log_output("Registering function with the solver...")
#         # Simulate registration process
#         self.log_output("Function registered successfully.")
#         self.update_status("Idle")

#     def run_function(self):
#         self.update_status("Running function...")
#         self.log_output("Running function...")
#         # Simulate function execution
#         self.log_output("Function executed successfully.")
#         self.update_status("Idle")

#     def view_results(self):
#         self.update_status("Fetching results...")
#         self.log_output("Fetching results...")
#         # Simulate result fetching
#         self.log_output("Results fetched successfully.")
#         self.update_status("Idle")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SolverGUI(root)
#     root.mainloop()
