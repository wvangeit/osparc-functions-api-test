import json
import pathlib as pl
import random
import time
from collections.abc import Mapping

import osparc_client
import urllib3

conf_path = pl.Path("./conf.json")
conf_dict = json.loads(conf_path.read_text("utf-8"))
configuration = osparc_client.Configuration(**conf_dict)


function_id = "887394ef-f940-40bc-9d1a-275ad5979a08"

with osparc_client.ApiClient(configuration) as api_client:
    api_instance = osparc_client.FunctionsApi(api_client)
    studies_instance = osparc_client.StudiesApi(api_client)
    job_api_instance = osparc_client.FunctionJobsApi(api_client)
    job_collection_api_instance = osparc_client.FunctionJobCollectionsApi(api_client)

    print(f"Function id: {function_id}\n")

    received_function = api_instance.get_function(function_id)
    print(f"Received function: {received_function.to_dict()}\n")

    functions_list_len = api_instance.list_functions().total
    print(f"{functions_list_len} functions in the database\n")

    function_job = api_instance.run_function(function_id, {"X": 1.5, "Y": 10})

    for i_run in range(1):
        if i_run > 0:
            print("RERUNNING same function")
        print(f"Running function, created function job: {function_job}\n")
        function_job_uid = function_job.to_dict()["uid"]

        print(
            f"Received function job: {job_api_instance.get_function_job(function_job_uid)}\n"
        )

        job_status = ""
        while "SUCCESS" not in str(job_status):
            job_status = job_api_instance.function_job_status(function_job_uid)
            print(f"Job status: {job_status}")
            time.sleep(5)

        job_output = job_api_instance.function_job_outputs(function_job_uid)
        print(f"\nJob output: {job_output}")

    # print("Mapping function:")
    # # function_inputs_list = [
    # #     {"x": random.uniform(1, 10), "y": random.uniform(1, 10)} for _ in range(5)
    # # ]
    # function_inputs_list = [
    #     {"x": int(random.uniform(1,10)), "y": int(random.uniform(1,10))} for _ in range(5)
    # ]
    # for inputs in function_inputs_list:
    #     print(f"Validation: {api_instance.validate_function_inputs(function_id, inputs)}")
    # print(f"Map inputs list: {function_inputs_list}\n")
    # map_job_collection = api_instance.map_function(function_id, function_inputs_list)
    # print(f"Map job collection: {map_job_collection}\n")
    #
    # job_collection_status = ""
    #
    # while True:
    #     job_collection_status = job_collection_api_instance.function_job_collection_status(map_job_collection.uid)
    #     statuses = job_collection_status.status
    #     print(f"Job collection statuses: {statuses}")
    #     # Loop until all statuses are either "SUCCESS" or "FAILED"
    #     if statuses and all(s in {"SUCCESS", "FAILED"} for s in statuses):
    #         break
    #     time.sleep(5)
    #
    # for job_id, status in zip(map_job_collection.job_ids, statuses):
    #     print(f"Job {job_id} output: {job_api_instance.function_job_outputs(job_id)}")
