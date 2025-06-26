repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Project-specific test coverage
PYTEST_ARGS += --cov=document_generator_v2_app

.PHONY: run dev

# Run the document-generator-v2 app
run:
	@echo "Starting Document Generator V2..."
	uv run python -m document_generator_v2_app.app

# Run in development mode with auto-reload
dev:
	@echo "Starting Document Generator V2 in development mode..."
	uv run python -m document_generator_v2_app.app