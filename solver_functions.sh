#!/bin/bash

set -e

rm -rf .venv
uv venv .venv

curl https://api.osparc-master.speag.com/api/v0/openapi.json -o openapi.json
uv pip install openapi-generator-cli
uv run openapi-generator-cli generate \
    -i openapi.json \
    -g python \
    -o ./flaskapi/functions-api-python-client \
    --package-name osparc_client
uv pip install ./flaskapi/functions-api-python-client

uv run python solver_functions.py
