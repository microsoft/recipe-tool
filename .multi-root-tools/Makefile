repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/shell.mk

VENV_DIR := .venv
PYTHON_VERSION := 3.11

.PHONY: install

install: $(VENV_DIR)

$(VENV_DIR):
	uv venv --python $(PYTHON_VERSION) $(VENV_DIR)

.PHONY: clean test format lint type-check lock
clean:
	$(rm_dir) $(VENV_DIR) $(ignore_failure)

# No-op targets for recursive make compatibility
test format lint type-check lock:
	@echo "No $@ target needed for .multi-root-tools"
