repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Project-specific test coverage
PYTEST_ARGS += --cov=doc_constructor_app

.PHONY: run dev

# Run the doc-constructor app
run:
	@echo "Starting Document Constructor..."
	uv run python -m doc_constructor_app.app

# Run in development mode with auto-reload
dev:
	@echo "Starting Document Constructor in development mode..."
	uv run python -m doc_constructor_app.app