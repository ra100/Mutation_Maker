#    Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
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
from botocore import UNSIGNED
from botocore.config import Config
import json
import os
from concurrent.futures import ThreadPoolExecutor

RUN_LAMBDA_LOCAL = os.getenv("RUN_LAMBDA_LOCAL", "0")
RUN_LAMBDA_DOCKER = os.getenv("RUN_LAMBDA_DOCKER", "0")


def create_client():
    if RUN_LAMBDA_LOCAL == "1":
        print("\nRunning client against LOCAL deployment of AWS Lambda.\n")

        # Creates a client against a local instance of AWS Lambda
        # created by SAM CLI running on localhost.
        client = boto3.client('lambda',
                              endpoint_url="http://localhost:3001",
                              use_ssl=False,
                              verify=False,
                              config=Config(signature_version=UNSIGNED, max_pool_connections=200,
                                            read_timeout=900))

        return client
    elif RUN_LAMBDA_DOCKER == "1":
        print("\nRunning client against DOCKER deployment of AWS Lambda.\n")

        # Creates a client against a local instance of AWS Lambda
        # created by SAM CLI running in `lambda` Docker Compose service.
        client = boto3.client('lambda',
                              endpoint_url="http://lambda:3001",
                              use_ssl=False,
                              verify=False,
                              config=Config(signature_version=UNSIGNED, max_pool_connections=200,
                                            read_timeout=900))

        return client
    else:
        print("\nRunning client against CLOUD deployment of AWS Lambda.\n")
        client = boto3.client('lambda')

        return client


def invoke_design_primers(client, json_payload):

    if RUN_LAMBDA_LOCAL == "1" or RUN_LAMBDA_DOCKER == "1":
        function_name = "DesignPrimersFunction"
    else:
        function_name = os.environ.get('LAMBDA_FN_NAME', 'cyb-mutation-maker-primer3')

    json_str = json.dumps(json_payload)
    return client.invoke(FunctionName=function_name,
                         Payload=json_str.encode("ascii"))


def invoke_multiple(payloads):
    client = create_client()

    # TODO: better way than 200 threads?
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = []

        for payload in payloads:
            print("CALL Primer3 AWS Lambda function")
            futures.append(
                executor.submit(invoke_design_primers, client, payload)
            )

        # TODO: For now we're assuming the calls succeed. However,
        # AWS Lambda can fail, not just because of network errors,
        # but also in case we use all the concurrency which is shared
        # by all the lambda instances running under one AWS account.
        results = [json.loads(future.result()["Payload"].read().decode("ascii"))
                   for future in futures]

        print("INVOKE_MULTIPLE DONE ...")

        return results