import time

import osparc_client
import urllib3

configuration = osparc_client.Configuration(
    username="test_172e6803b18ece31db58",
    password="72c0a88656e93672d0ad62f1d20d40722fa07de5",
    host="http://localhost:8006",
)


with osparc_client.ApiClient(configuration) as api_client:
    api_instance = osparc_client.FunctionsApi(api_client)
    job_api_instance = osparc_client.FunctionJobsApi(api_client)
    # print(osparc_client.UsersApi(api_client).get_my_profile())

    input_schema = osparc_client.FunctionInputSchema(
        schema_dict={
            "type": "object",
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"},
            },
            "required": ["x", "y"],
        }
    )

    output_schema = osparc_client.FunctionOutputSchema(
        schema_dict={
            "type": "object",
            "properties": {"result": {"type": "number"}},
            "required": ["result"],
        }
    )

    study_function = osparc_client.Function(
        osparc_client.ProjectFunction(
            title="Sinc",
            description="2D Sinc",
            input_schema=input_schema.dict(),
            output_schema=output_schema.dict(),
            project_id="2988be64-1916-11f0-ba30-0242ac14020e",
        )
    )
    print(f"Built function: {study_function.to_dict()}\n")

    while True:
        try:
            registered_function = api_instance.register_function(study_function)
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
    print(f"{len(functions_list)} functions in the database: {[(function.to_dict()['uid'], function.to_dict()['title']) for function in functions_list]}")

    function_job = job_api_instance.create_function_job(
        function_id=function_id,
        function_inputs={"inputs_dict": {"x": 1.0, "y": 10.0}},
    )
    print(f"Created function job: {function_job.to_dict()}\n")

    function_job = api_instance.run_function(
          function_id, function_inputs={"inputs_dict": {"x": 1.0, "y": 10.0}}
    )

    print(f"Running function, created function job: {function_job}\n")
    function_job_uid = function_job.uid
    
    print(f"Received function job: {job_api_instance.get_function_job(function_job.uid)}\n")

    job_status = ''
    while 'SUCCESS' not in str(job_status):
        job_status = job_api_instance.function_job_status(function_job_uid)
        print(f"Job status: {job_status}")
        time.sleep(1)

    # # function_job_uid = '30523096-1555-11f0-a8c6-0242ac14050e'
    job_output = job_api_instance.function_job_outputs(function_job_uid)
    print(f"\nJob output: {job_output}")
    #
    # params_list = [None]
    #
    # function_job_coll = api_instance.map_function(function.uid, params_list)
    #
    # collection_status = api_instance.function_job_collection_status(
    #     function_job_coll.id
    # )
