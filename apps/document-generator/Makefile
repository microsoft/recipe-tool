repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Override all test-related targets to skip testing for this app
.PHONY: test pytest type-check
test:
	@echo "Testing disabled for document-generator"
	@true

pytest:
	@echo "Pytest disabled for document-generator"
	@true

# Build deployment package
.PHONY: build
build:
	@echo "Building deployment package..."
	@python scripts/build_deployment.py
