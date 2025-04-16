import json
import pathlib as pl
import time
import zipfile

import osparc
import osparc_client

conf_path = pl.Path("./conf.json")
conf_dict = json.loads(conf_path.read_text())
configuration = osparc.Configuration(**conf_dict)

SOLVER_KEY = "simcore/services/comp/osparc-python-runner"
SOLVER_VERSION = "1.2.0"

with osparc.ApiClient(configuration) as api_client:
    solver_instance = osparc_client.SolversApi(api_client)
    file_instance = osparc.FilesApi(api_client)
    file_client_instance = osparc_client.FilesApi(api_client)

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

    print(
        f"Ports: {solver_instance.list_solver_ports(solver_key=SOLVER_KEY, version=SOLVER_VERSION)}\n"
    )

    solver_job = solver_instance.create_solver_job(
        solver_key=SOLVER_KEY,
        version=SOLVER_VERSION,
        job_inputs=osparc_client.JobInputs(
            values={
                "input_1": osparc_client.ValuesValue(main_file),
                "input_2": osparc_client.ValuesValue(pythoncode_file),
                "input_3": osparc_client.ValuesValue(inputs_file),
            }
        ),
    )

    print(f"Create solver job {solver_job}\n")

    job_status = solver_instance.start_job(
        solver_key=SOLVER_KEY,
        version=SOLVER_VERSION,
        job_id=solver_job.id,
    )

    print(f"Started solver job {job_status}\n")

    # print(f"Log stream: {solver_instance.get_log_stream(solver_key=SOLVER_KEY,version=SOLVER_VERSION,job_id=solver_job.id,)}.content\n")

    while (
        job_status := solver_instance.inspect_job(
            solver_key=SOLVER_KEY,
            version=SOLVER_VERSION,
            job_id=solver_job.id,
        )
    ).state not in (
        osparc_client.RunningState.SUCCESS,
        osparc_client.RunningState.FAILED,
    ):
        print(f"Job status: {job_status.state}")
        time.sleep(1)
    print(f"Final job status: {job_status.state}")

    print(
        f"Log: {solver_instance.get_job_output_logfile(solver_key=SOLVER_KEY, version=SOLVER_VERSION, job_id=solver_job.id).decode('utf-8', errors='replace')}\n"
    )

    output_results = solver_instance.get_job_outputs(
        solver_key=SOLVER_KEY, version=SOLVER_VERSION, job_id=job_status.job_id
    )
    for output_name, result in output_results.results.items():
        print(output_name, "=", result)
        downloaded_file = file_instance.download_file(
            result.actual_instance.id, destination_folder=pl.Path("./solver_files")
        )
        print(f"Downloaded file: {downloaded_file}")
        with zipfile.ZipFile(downloaded_file, 'r') as zip_file:
            job_output = json.loads(zip_file.read('function_outputs.json').decode('utf-8'))
    
    print(f"Job output: {job_output}")

