import time
import uuid

import osparc_client
import urllib3

configuration = osparc_client.Configuration(
    username="test_5327822f7d18bd826a65",
    password="082b31fe901ab48acc33377c5493bc2f060eeeb2",
    host="http://localhost:8006",
)


with osparc_client.ApiClient(configuration) as api_client:
    api_instance = osparc_client.FunctionsApi(api_client)
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
        osparc_client.StudyFunction(
            title="Sinc",
            description="2D Sinc",
            input_schema=input_schema.dict(),
            output_schema=output_schema.dict(),
            study_url="http://osparc.io/studies/3fa85f64-5717-4562-b3fc-2c963f66afa6",
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

    function_job = api_instance.run_function(
         function_id, function_inputs={"inputs_dict": {"x": 1.0, "y": 10.0}}
    )

    print(f"Running function, created function job: {function_job}\n")

    # print(f"Function job status: {function_job.to_dict()["status"]}")
    # job_status = api_instance.function_job_status(function_job.id)
    #
    # print(f"Job status: {job_status}")
    #
    # job_output = api_instance.function_job_output(function_job.id)
    #
    # print(f"Job output: {job_output}")
    #
    # params_list = [None]
    #
    # function_job_coll = api_instance.map_function(function.uid, params_list)
    #
    # collection_status = api_instance.function_job_collection_status(
    #     function_job_coll.id
    # )
