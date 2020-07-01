CONDA_ENV_NAME = mutationmaker
CONDA_INIT := eval "$$(conda shell.bash hook)"

default: help

## Create Conda environment and install all backend dependencies
env:
	@$(CONDA_INIT); conda activate $(CONDA_ENV_NAME) 2>/dev/null || conda create -y -n $(CONDA_ENV_NAME) python=3.7
	@echo "Installing requirements..."
	$(CONDA_INIT); conda activate $(CONDA_ENV_NAME) && \
		pip install -r backend/requirements.txt -r api/requirements.txt -r lambda/requirements.txt
	@echo "Conda environment ready, activate it using:\n\nconda activate $(CONDA_ENV_NAME)\n"

## Install (or update) frontend packages using NPM CI
env-frontend:
	cd frontend && npm ci

## Run all backend unit tests
test:
	cd backend; PYTHONHASHSEED=0 python -m unittest tests/unit_tests/*

## Run Mutation Maker locally (requires active Python environment)
run:
	@echo "Please remember to activate the Mutation Maker environment"
	@echo "Using python executable: $$(which python)"
	@sleep 2
	@{ \
		@set -Eeuo pipefail; \
		trap "exit" INT TERM ERR; \
		trap "kill -9 0" EXIT; \
		pids=""; \
		make run-worker & pids="$$pids $!"; \
		make run-monitor & pids="$$pids $!"; \
		make run-frontend & pids="$$pids $!"; \
		make run-api & pids="$$pids $$!"; \
		make run-lambda & pids="$$pids $$!"; \
		while [[ ! -z "$$pids" ]]; do \
		  for pid in $$pids; do \
			kill -0 "$$pid" 2>/dev/null || exit 1; \
		  done; \
		  sleep 1; \
		done; \
	}

## Run frontend live-reload NPM server locally
run-frontend:
	cd frontend && npm start

## Run API server locally
run-api:
	cd api && gunicorn server:app

## Run Celery worker locally
run-worker:
	cd backend && celery -A tasks worker --loglevel=INFO

## Run AWS Lambda locally via SAM CLI
run-lambda:
	cd lambda && RUN_LAMBDA_LOCAL=1 && sam local start-lambda --debug

## Run Celery queue monitor locally
run-monitor:
	cd backend && celery -A tasks flower --loglevel=INFO

## Create frontend production build
build-frontend:
	cd frontend && npm ci && npm run build

## Run all Docker containers using docker-compose (rebuild if changed)
docker-run:
	docker-compose up --build

## Build all Docker containers using docker-compose
docker-build:
	docker-compose build

# Auto-generated help
# Adapted from: https://raw.githubusercontent.com/nestauk/patent_analysis/3beebda/Makefile
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
