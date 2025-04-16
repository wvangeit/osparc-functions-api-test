import io
import time
import zipfile

import osparc_client

configuration = osparc_client.Configuration(
    username="test_172e6803b18ece31db58",
    password="72c0a88656e93672d0ad62f1d20d40722fa07de5",
    host="http://localhost:8006",
)

SOLVER_KEY = "simcore/services/comp/osparc-python-runner"
SOLVER_VERSION = "1.2.0"

with osparc_client.ApiClient(configuration) as api_client:
    solver_instance = osparc_client.SolversApi(api_client)
    file_instance = osparc_client.FilesApi(api_client)

    inputs_file = file_instance.upload_file(file="function_inputs.json")
    print(f"Uploaded inputs file {inputs_file}\n")

    main_file = file_instance.upload_file(file="main.py")
    print(f"Uploaded main file {main_file}\n")

    pythoncode_file = file_instance.upload_file(file="function_code.py")
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
    job_outputs = solver_instance.get_job_outputs(
        solver_key=SOLVER_KEY,
        version=SOLVER_VERSION,
        job_id=solver_job.id,
    )

    print(f"Output: {job_outputs}\n")

    output_file_bytes = file_instance.download_file(
        job_outputs.results["output_1"].actual_instance.id
    )

    with zipfile.ZipFile(io.BytesIO(output_file_bytes)) as zip_file:
        for file_name in zip_file.namelist():
            print(f"- {file_name}")
