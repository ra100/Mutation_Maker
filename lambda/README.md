# Deployment

## Primer3

The folder `primer3-build-env` contains a simple setup for building primer3 on
the Amazon Linux which is what runs on AWS Lambda. To get just a `primer3_core`
binary simply `cd primer3-build-env` and run `make build-primer3`. Docker is
required for this step.

## Local testing

Lambda can be run locally without the need to deploy on AWS. This requires the
[SAM CLI](https://docs.aws.amazon.com/lambda/latest/dg/test-sam-cli.html),
which runs each lambda invocation inside a docker container.

## Performance

AWS Lambda performance depends on the memory setting, regardless of how much
memory is the lambda function actually consuming. See
https://github.com/epsagon/lambda-memory-performance-benchmark for more
details.

## Useful links

- Docker images with AWS Lambda execution environments https://hub.docker.com/r/lambci/lambda/
