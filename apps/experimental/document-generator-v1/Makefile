repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Document Generator specific targets
.PHONY: refresh-examples build
refresh-examples:  ## Refresh example docpacks from source JSON files
	python scripts/refresh_examples.py

build:  ## Build deployment package (bundle recipes + refresh examples)
	python scripts/build_deployment.py
