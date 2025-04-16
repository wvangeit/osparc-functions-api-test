import json
import os
import pathlib as pl

import function_code


def main():
    print("\n".join(os.listdir()))
    print(os.environ)
    input_json = pl.Path(os.environ["INPUT_FOLDER"]) / "function_inputs.json"
    output_json = pl.Path("function_outputs.json")
    inputs = json.loads(input_json.read_text())
    print(f"Received inputs: {inputs}")

    outputs = function_code.main(**inputs)

    output_json.write_text(json.dumps(outputs))

    print(f"Generated outputs: {outputs}")


if __name__ == "__main__":
    main()
