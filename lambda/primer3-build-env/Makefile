IMAGE_NAME=amazon-binary-build-env
BUILD_DIR=$(shell pwd)/primer3/src

ZIP_NAME=v2.4.0.tar.gz
PRIMER3_DIR=primer3

## Build primer3 binary in Docker
build-primer3: prepare-primer3 build-image
	docker run --rm -v $(BUILD_DIR):/build_dir -it $(IMAGE_NAME) make
	cp $(PRIMER3_DIR)/src/primer3_core primer3_core

## Run shell in primer3 Docker image
run-container:
	docker run --rm -v $(BUILD_DIR):/build_dir -it $(IMAGE_NAME)

## Build primer3 Docker image
build-image:
	docker build -t $(IMAGE_NAME) .

## Clean primer3 build artifacts
clean:
	rm -f $(ZIP_NAME) primer3_core
	rm -rf $(PRIMER3_DIR)

## Download primer3 tarball from Github
$(ZIP_NAME):
	wget https://github.com/primer3-org/primer3/archive/$(ZIP_NAME)
	touch $(ZIP_NAME)

## Patch primer3 source
prepare-primer3: $(ZIP_NAME)
	mkdir -p $(PRIMER3_DIR)
	tar xf $(ZIP_NAME) -C $(PRIMER3_DIR) --strip-components=1
	cp primer3_patch $(PRIMER3_DIR)
	(cd $(PRIMER3_DIR) && patch -p1 < primer3_patch)

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
