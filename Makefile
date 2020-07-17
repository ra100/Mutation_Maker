CONDA_ENV_NAME = mutationmaker
CONDA_INIT := eval "$$(conda shell.bash hook)"

HOST ?= localhost

default: help

## Create Conda environment and install all backend dependencies
conda-env:
	@$(CONDA_INIT); conda activate $(CONDA_ENV_NAME) 2>/dev/null || conda create -y -n $(CONDA_ENV_NAME) python=3.7
	@echo "Installing requirements..."
	$(CONDA_INIT); conda activate $(CONDA_ENV_NAME) && \
		pip install -r backend/requirements.txt -r api/requirements.txt -r lambda/requirements.txt
	@echo "Conda environment ready, activate it using:\n\nconda activate $(CONDA_ENV_NAME)\n"

## Install (or update) frontend packages using NPM CI
env-frontend:
	cd frontend && npm ci

## Create frontend production build for nginx
build-frontend:
	cd frontend && npm ci && npm run build

## Run all backend unit tests
test:
	cd backend; PYTHONHASHSEED=0 python -m unittest tests/unit_tests/*

#
# Local development servers
#

## Run Mutation Maker locally (requires active Python environment)
run:
	./runlocal.sh

## Run frontend live-reload NPM server locally
run-frontend:
	cd frontend && npm start

## Run API server locally
run-api:
	cd api && gunicorn server:app --bind $(HOST)

## Run Celery worker locally
run-worker:
	cd backend && celery -A tasks worker --loglevel=INFO

## Run AWS Lambda locally via SAM CLI
run-lambda:
	cd lambda && RUN_LAMBDA_LOCAL=1 && sam local start-lambda --debug

## Run Celery queue monitor locally
run-monitor:
	cd backend && celery -A tasks flower --loglevel=INFO

#
# Systemctl services
#

## Install all services
services: service-redis service-frontend service-worker service-api
	sudo systemctl status --no-pager nginx celery gunicorn redis-server

## Restart redis service (should be available after installing redis-server)
service-redis:
	sudo systemctl enable redis-server.service
	sudo systemctl restart redis-server.service
	sleep 3; sudo systemctl status --no-pager redis-server.service

## Install built frontend into nginx dir
service-frontend:
	sudo cp frontend/resources/local-nginx-frontend.conf /etc/nginx/sites-enabled/default
	sudo rm -rf /var/www/html; sudo mkdir -p /var/www/; sudo cp -r frontend/build /var/www/html
	sudo systemctl restart nginx
	sleep 3; sudo systemctl status --no-pager nginx

## Install celery as service
service-worker:
	sudo useradd celery -d /home/celery -b /bin/bash || true
	sudo mkdir -p /etc/conf.d; sudo cp backend/resources/celery.config /etc/conf.d/celery
	sudo cp backend/resources/celery.service /etc/systemd/system/celery.service
	sudo mkdir -p /etc/tmpfiles.d; sudo cp backend/resources/celery.tmpfiles /etc/tmpfiles.d/celery.conf
	sudo systemd-tmpfiles --create
	sudo systemctl daemon-reload
	sudo systemctl restart celery
	sleep 3; sudo systemctl status --no-pager celery

## Install api gunicorn service
service-api:
	sudo cp api/resources/gunicorn.service /etc/systemd/system/gunicorn.service
	sudo systemctl daemon-reload
	sudo systemctl restart gunicorn
	sleep 3; sudo systemctl status --no-pager gunicorn

#
# Docker
#

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
