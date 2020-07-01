PRIMER3_BUILD_DIR=primer3-build-env
PRIMER3_BINARY=$(PRIMER3_BUILD_DIR)/primer3_core
# Please fill in the AWS Lambda function name and AWS region
LAMBDA_FUNCTION_NAME=cyb-mutation-maker-primer3
AWS_REGION=us-east-1


# Default option builds AWS Lambda deployment package
default: build-zip
	echo "Deploy .zip ready, upload \`build/deploy-package.zip\` to AWS"

## Clean built primer3 binary artifact and AWS Lambda deployment package
clean:
	rm -f build/deploy-package.zip deploy-package/primer3_core

## Invoke AWS Lambda function locally with test data input JSON
local-invoke:
	sam local invoke "DesignPrimersFunction" -e test_event.json

## Start local AWS Lambda function endpoint
local-lambda:
	sam local start-lambda

## Invoke AWS Lambda function in the cloud
invoke:
	aws lambda invoke --invocation-type RequestResponse \
		--function-name $(LAMBDA_FUNCTION_NAME) \
		--region $(AWS_REGION) \
		--log-type Tail \
		--payload '' output.txt
	cat output.txt

# Build primer3 binary
$(PRIMER3_BINARY):
	cd $(PRIMER3_BUILD_DIR) && $(MAKE) build-primer3

## Build AWS Lambda deployment package
build-zip: $(PRIMER3_BINARY)
	rm -f build/deploy-package.zip
	cp $(PRIMER3_BINARY) deploy-package
	(cd deploy-package && zip -r deploy-package.zip *)
	mv deploy-package/deploy-package.zip build/deploy-package.zip

## Open ipython CLI to run AWS Lambda debug module
repl:
	@command -v ipython && \
		PYTHONSTARTUP=debug_helpers.py ipython || \
		PYTHONSTARTUP=debug_helpers.py python

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
