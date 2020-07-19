# Mutation Maker

Application for mutagenic primer design. Facilitates development of biocatalysts (Green Chemistry) and new therapeutic proteins.

This application is described in the following paper:
> **Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and *De Novo* Gene Synthesis Experiments**
>
>Authors: Kaori Hiraga, Petr Mejzlik, Matej Marcisin, Nikita Vostrosablin, Anna Gromek, Jakub Arnold, Sebastian Wiewiora, Rastislav Svarba, David Prihoda, Kamila Clarova, Ondrej Klempir, Josef Navratil, Ondrej Tupa, Alejandro Vazquez-Otero, Marcin W. Walas, Lukas Holy, Martin Spale, Jakub Kotowski, David Dzamba, Gergely Temesi, Jay H. Russell, Nicholas M. Marshall, Keith A. Canada and Danny A. Bitton

Copyright© 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.

# Makefile

Many useful commands are managed using the provided [Makefile](Makefile).

Run `make help` to show all available commands for building, running and deploying Mutation Maker.

# Installation

First clone or download the repository from Github.

The application can be run either in [Docker containers](#running-in-docker)
with the [Docker Compose](https://docs.docker.com/compose/) tool utilizing the provided [docker-compose.yml](docker-compose.yml).  

We also provide an [example configuration](#example-deployment-on-ubuntu) when using a dedicated Ubuntu server.

For development, the application can also be [run locally](#running-locally) given that all of the application dependencies are installed.

# Running in Docker

It is necessary to install Docker engine and Docker Compose tool first in order to use this installation method.  
For installation instructions specific to your platform please refer to the official Docker documentation:
- Docker Engine: https://docs.docker.com/engine/install/
- Docker Compose: https://docs.docker.com/compose/install/

Mutation Maker is setup to run with `docker-compose`.  
To start everything, simply run:

```bash
make docker-run
```
    
Or directly using:

```bash
docker-compose up --build
```

This will build and start all docker containers:
- Webserver: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000](http://localhost:8000)
- Frontend (live-reload or production build - see below)
- Celery worker
- Redis server
- AWS Lambda worker

You can open an interactive shell for each of the running services using (in a separate terminal):
```bash
docker-compose exec frontend sh
docker-compose exec api sh
docker-compose exec worker sh
docker-compose exec redis sh
docker-compose exec lambda sh
```

The `docker-compose` definition is stored in [docker-compose.yml](docker-compose.yml).

Additional details regarding the setup can be found in the respective
Dockerfiles under [backend](backend), [frontend](frontend), [api](api) and [lambda](lambda) directories.

### Configuring Docker frontend: live-reload or production ready build

Docker frontend container uses npm live-reload development server.  
You can also execute it as a production build by changing the frontend `target` field 
in [docker-compose.yml](docker-compose.yml) file.

# Example deployment on Ubuntu

Follow these steps to setup Mutation Maker on Ubuntu with root access using systemctl services. This makes sure that all required services keep runing on server restart.

## 1) Install required packages

```bash
sudo apt update; sudo apt install software-properties-common;
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7 python3-pip redis-server nodejs npm nginx
# If applicable, enable nginx in ufw
sudo ufw allow 'Nginx HTTP'
sudo ufw status
```

## 2) Clone Mutation Maker repository

```bash
sudo git clone https://github.com/Merck/Mutation_Maker /opt/mutationmaker

cd /opt/mutationmaker
sudo chmod -R a+rX .
sudo -H pip3 install -r backend/requirements.txt
sudo -H pip3 install -r api/requirements.txt
```

## 3) Adjust config files

Use your local IP (e.g. 127.0.0.1 or where you want to bind your service):
- for `upstream-api` in: `frontend/resources/local-nginx-frontend.conf`
- for `--bind` in `api/resources/gunicorn.service`

## 4) Register and start all services

```bash
make services
```

Status of all services should be displayed. Please report any issues [here](https://github.com/Merck/Mutation_Maker/issues).

# Running locally

Alternatively, all the services can be run locally in development mode using a local Python environment.

## Local dependencies

### Redis

Redis is an in-memory database that serves as a task queue from the API to the Celery worker.
 
Install Redis using Homebrew (macOS):
```bash
brew install redis
```

Run Redis as a brew service:

    brew services start redis

Or using: 

    redis-server /usr/local/etc/redis.conf
    
Use `redis-cli flushall` to clean existing task queues.

### Backend dependencies

Backend dependencies are specified separately with `requirements.txt` under
`api`, `backend` and `lambda` directories. It is possible to install all the dependencies under
a single virtual environment.

For platform specific instructions to install Conda, please refer to the official documentation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/

Create `mutationmaker` environment using Conda:
```bash
make conda-env
```

Or install the requirements directly:

```bash
pip install -r backend/requirements.txt
pip install -r api/requirements.txt
pip install -r lambda/requirements.txt
```

### Frontend dependencies 

Install `Node.js` and `NPM` (macOS):

```bash
brew install node
```

Initialize the multi-package frontend repository and install all packages using:

```bash
make env-frontend
```

Or directly using:

```bash
cd frontend/
npm ci
```

## Running local services

Run all services locally using:

```bash
make run
```
    
Or run each service manually:

```bash
# Run these in separate terminals
# API
make run-api
# Frontend
make run-frontend
# Backend Celery worker
make run-worker
# AWS Lambda worker
make run-lambda
# Celery monitor (only for monitoring Celery queues)
make run-monitor
```

# Repository structure

- [api](api): Server that accepts tasks from the frontend and schedules them using the `backend` worker.
- [backend](backend): Celery worker that processes the tasks.
- [frontend](frontend): Frontend app. It contains package [feature-viewer](frontend/feature-viewer) - fork of [calipho-sib/feature-viewer](https://github.com/calipho-sib/feature-viewer).
  - added eslint and prettier and fixed/added workaround for all problems
  - added object type `arrow` for primer visualisation
  - added `showSelectedBox` and `hideSelectedBox`
  - removed `onSelect` coloring
  - added `colorFeature` to externally control color of features
- [webserver](webserver): Main entrypoint for the user. Simple nginx proxy of requests to the application API and frontend.
- [lambda](lambda): Provides AWS Lambda endpoint running Primer3 binary locally in a Docker container by [SAM CLI](https://github.com/awslabs/aws-sam-cli).


## AWS Lambda settings

AWS Lambda is leveraged for parallel execution of [Primer3](https://github.com/primer3-org/primer3) binary.
Primer3 is a command line tool to select primers for polymerase chain reaction (PCR).
This option can be selected as one of the parameters in the SSSM workflow, by default it is disabled.

This AWS Lambda function can be run in three different modes of execution.
- [Local deployment](#local-deployment)
- [Docker deployment](#docker-deployment)
- [Cloud deployment](#cloud-deployment)

### Local deployment

Local deployment is enabled in the application by exporting the following environment variable:
```bash
RUN_LAMBDA_LOCAL=1
```

To start the Lambda endpoint locally, you can run the following command:
```bash
make run-lambda
```

### Docker deployment

Docker deployment is enabled in the application by exporting the following environment variable:
```bash
RUN_LAMBDA_DOCKER=1
```

To start the Lambda endpoint in Docker container, you can run the following command:
```bash
docker-compose up lambda
```

### Cloud deployment

It's possible to create a deployment package to AWS Lambda service in the AWS cloud using the provided [Makefile commands](lambda/Makefile) in the [lambda](lambda) directory.

Please refer to the official AWS documentation for more details: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

AWS Lambda service cloud deployment is enabled in the application by exporting the following environment variables:
```bash
RUN_LAMBDA_LOCAL=0
RUN_LAMBDA_DOCKER=0
LAMBDA_FN_NAME
```

To use your own Lambda function in AWS, please export the function name into `LAMBDA_FN_NAME` environment variable.
Additionally, you'll need to export the AWS Region where the function resides and the respective AWS credentials authorized to run this function.

Exporting AWS Credentials:
```bash
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```


## Testing

All Mutation Maker workflows (SSSM, MSDM, PAS) are covered with unit tests of the backend features.  

### Unit tests
Basic unit test for Mutation Maker backend. These require user to specify their own sequences and mutations for testing.

### Unit tests requirements
Same as for Mutation Maker application however you need to run the Python interpreter with a following variable:
```bash
# Run from backend
PYTHONHASHSEED=0 python -m unittest tests/unit_tests/*
```

# Contributing

We welcome contributions from the community.

For more information check the following resources:
  * [Mailing list](mailto:mutationm@merck.com)
  * [Reporting bugs](#reporting-bugs)
  * [Submitting changes](#submitting-changes)

## Reporting bugs

Bugs are tracked as [GitHub issues](https://github.com/Merck/Mutation_Maker/issues).
Please explain the problem and include additional details to help maintainers reproduce the issue. Use a clear and descriptive title for the issue to identify the problem, 
and describe the exact steps which reproduce the problem.

## Submitting changes

Please send a [GitHub Pull Request to Mutation Maker](https://github.com/Merck/Mutation_Maker/pull/new/master) with a clear list of what you've done. Please make sure all of your commits are atomic (one feature per commit).

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."

# License

Mutation Maker is licensed under [GPLv3+](https://www.gnu.org/licenses/gpl-3.0.en.html).
