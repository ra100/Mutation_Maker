#
#    This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
#
#    Mutation Maker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import boto3
import json
import os

from concurrent.futures import ThreadPoolExecutor

RUN_LAMBDA_LOCAL = os.getenv("RUN_LAMBDA_LOCAL", "1")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FN_NAME", "cyb-mutation-maker-primer3")


if RUN_LAMBDA_LOCAL == "1":
    FUNCTION_NAME = "DesignPrimersFunction"
    print("\nRunning client against LOCAL deployment of AWS Lambda.")
    print("\nIf it is not running, execute `make local-lambda` in a different terminal window.")

    # Creates a client against a LOCAL instance of AWS Lambda
    # created by SAM CLI.
    client = boto3.client('lambda',
                          endpoint_url="http://127.0.0.1:3001",
                          use_ssl=False,
                          verify=False)
else:
    FUNCTION_NAME = LAMBDA_FUNCTION_NAME
    print("\nRunning client against CLOUD deployment of AWS Lambda function.")
    client = boto3.client('lambda')


def invoke_with_file(filename, client=client):
    with open(filename, "r") as f:
        contents = f.read()
        return invoke_design_primers(contents)


def invoke_design_primers(json_payload, client=client):
    json_str = json.dumps(json_payload)
    return client.invoke(FunctionName=FUNCTION_NAME,
                         Payload=json_str.encode("ascii"))


def invoke_multiple(payloads, client=client):
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = []

        for payload in payloads:
            futures.append(
                executor.submit(invoke_design_primers, payload, client)
            )

        # For now we're assuming the calls succeeded
        results = [future.result()["Payload"].read() for future in futures]

        return results
