repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Project-specific test coverage
PYTEST_ARGS += --cov=doc_builder_v2_app

.PHONY: run dev

# Run the doc-builder-v2 app
run:
	@echo "Starting Document Builder V2..."
	uv run python -m doc_builder_v2_app.app

# Run in development mode with auto-reload
dev:
	@echo "Starting Document Builder V2 in development mode..."
	uv run python -m doc_builder_v2_app.app