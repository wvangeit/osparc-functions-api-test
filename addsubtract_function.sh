#!/bin/bash

set -e

rm -rf .venv
uv venv .venv

source .venv/bin/activate

uv pip install ../osparc-simcore-clients/clients/python/artifacts/dist/osparc_client-0.8.3.post0.dev25-py3-none-any.whl
uv pip install ../osparc-simcore-clients/clients/python/artifacts/dist/osparc-0.8.3.post0.dev25-py3-none-any.whl

python addsubtract_function.py
