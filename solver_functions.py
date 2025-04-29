import json
import pathlib as pl
import time
import zipfile

import osparc
import osparc_client
import urllib3

conf_path = pl.Path("./conf.json")
conf_dict = json.loads(conf_path.read_text("utf-8"))
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
        job_collection_api_instance = osparc_client.FunctionJobCollectionsApi(api_client)
        file_client_instance = osparc_client.FilesApi(api_client)
        file_instance = osparc.FilesApi(api_client)

        inputs_file = file_client_instance.upload_file(
            file="./solver_files/function_inputs.json"
        )
        if not inputs_file or not hasattr(inputs_file, "id"):
            raise ValueError("Failed to upload inputs file or missing 'id' attribute.")
        print(f"Uploaded inputs file {inputs_file}\n")

        main_file = file_client_instance.upload_file(file="./solver_files/main.py")
        print(f"Uploaded main file {main_file}\n")

        function_code_path = pl.Path("solver_files") / "function_code.py"
        function_code_path.write_text(function_code)

        pythoncode_file = file_client_instance.upload_file(file=str(function_code_path))

        print(f"Uploaded function code file {pythoncode_file}\n")

        solver_function = osparc_client.Function(
            osparc_client.SolverFunction(
                function_class="solver",
                title="SincSolver",
                description="2D sinc using solver",
                solver_key=SOLVER_KEY,
                solver_version=SOLVER_VERSION,
                default_inputs={"input_1": main_file, "input_2": pythoncode_file}
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
            f"{len(functions_list)} functions in the database\n"
        )

        function_jobs_list = job_api_instance.list_function_jobs()
        print(
            f"{len(function_jobs_list)} function_jobs in the database\n"
        )

        # function_job = api_instance.run_function(function_id, {"input_3": inputs_file})

        # function_job_uid = function_job.to_dict()["uid"]

        # while (
        #     job_status := job_api_instance.function_job_status(function_job_uid).status
        # ) not in ("SUCCESS", "FAILED"):
        #     print(f"Job status: {job_status}")
        #     time.sleep(5)
        # print(f"Job status: {job_status}")

        # job_output_dict = job_api_instance.function_job_outputs(function_job_uid)
        # print(f"\nJob output: {job_output_dict}")

        # downloaded_file = file_instance.download_file(
        #     job_output_dict["output_1"]["id"],
        #     destination_folder=pl.Path("./solver_files"),
        # )
        # print(f"Downloaded file: {downloaded_file}")
        # with zipfile.ZipFile(downloaded_file, "r") as zip_file:
        #     job_output = json.loads(
        #         zip_file.read("function_outputs.json").decode("utf-8")
        #     )

        # print(f"Job output: {job_output}")

        map_function_job_collection = api_instance.map_function(function_id, [{"input_3": inputs_file}, {"input_3": inputs_file}])
        print(f"Map function: {map_function_job_collection}\n")

        while not all(s in {"SUCCESS", "FAILED"} for s in job_collection_api_instance.function_job_collection_status(map_function_job_collection.uid).status):
            print(f"Map function job collection status: {job_collection_api_instance.function_job_collection_status(map_function_job_collection.uid).status}")
            time.sleep(5)
        print(f"Map function job collection status: {job_collection_api_instance.function_job_collection_status(map_function_job_collection.uid).status}")

        for job_id in map_function_job_collection.job_ids:
            job_status = job_api_instance.function_job_status(job_id).status
            if job_status == "SUCCESS":
                job_output_dict = job_api_instance.function_job_outputs(job_id)

                downloaded_file = file_instance.download_file(
                    job_output_dict["output_1"]["id"],
                    destination_folder=pl.Path("./solver_files"),
                )
                with zipfile.ZipFile(downloaded_file, "r") as zip_file:
                    job_output = json.loads(
                        zip_file.read("function_outputs.json").decode("utf-8")
                    )

                print(f"Job {job_id } output: {job_output}")


if __name__ == "__main__":
    main()
