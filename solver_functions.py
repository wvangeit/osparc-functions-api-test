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

with osparc.ApiClient(configuration) as api_client:
    api_instance = osparc_client.FunctionsApi(api_client)
    job_api_instance = osparc_client.FunctionJobsApi(api_client)
    file_client_instance = osparc_client.FilesApi(api_client)
    file_instance = osparc.FilesApi(api_client)

    inputs_file = file_client_instance.upload_file(
        file="./solver_files/function_inputs.json"
    )
    print(f"Uploaded inputs file {inputs_file}\n")

    main_file = file_client_instance.upload_file(file="./solver_files/main.py")
    print(f"Uploaded main file {main_file}\n")

    pythoncode_file = file_client_instance.upload_file(
        file="./solver_files/function_code.py"
    )
    print(f"Uploaded function code file {pythoncode_file}\n")

    solver_function = osparc_client.Function(
        osparc_client.SolverFunction(
            title="SincSolver",
            description="2D sinc using solver",
            solver_key=SOLVER_KEY,
            solver_version=SOLVER_VERSION,
        )
    )
    print(f"Built function: {solver_function.to_dict()}\n")

    while True:
        try:
            registered_function = api_instance.register_function(solver_function)
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

    function_job = api_instance.run_function(
        function_id,
        {
            "input_1": osparc_client.ValuesValue(main_file),
            "input_2": osparc_client.ValuesValue(pythoncode_file),
            "input_3": osparc_client.ValuesValue(inputs_file),
        },
    )

    function_job_uid = function_job.to_dict()["uid"]

    job_status = ""
    while "SUCCESS" not in str(job_status):
        job_status = job_api_instance.function_job_status(function_job_uid)
        print(f"Job status: {job_status}")
        time.sleep(1)

    job_output_dict = job_api_instance.function_job_outputs(function_job_uid)
    print(f"\nJob output: {job_output_dict}")

    downloaded_file = file_instance.download_file(
        job_output_dict["output_1"]["id"], destination_folder=pl.Path("./solver_files")
    )
    print(f"Downloaded file: {downloaded_file}")
    with zipfile.ZipFile(downloaded_file, "r") as zip_file:
        job_output = json.loads(zip_file.read("function_outputs.json").decode("utf-8"))

    print(f"Job output: {job_output}")
