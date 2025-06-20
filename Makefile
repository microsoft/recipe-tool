# Recipe Tool Workspace Root Makefile
# Uses recursive.mk to run targets across all project subdirectories

# Include the recursive system
this_dir = $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(this_dir)/tools/makefiles/recursive.mk


# Helper function to list available commands
ifeq ($(OS),Windows_NT)
define list_commands
	@echo "Available project commands:"
	@if exist .venv\Scripts\ ( \
		dir /b .venv\Scripts\ | findstr /I "recipe document" || echo "  (run 'make install' first)" \
	) else ( \
		echo "  (run 'make install' first)" \
	)
	@echo ""
endef
else
define list_commands
	@echo "Available project commands:"
	@ls .venv/bin/ 2>/dev/null | grep -E "(recipe|document|doc|app)" | sed 's/^/  /' || echo "  (run 'make install' first)"
	@echo ""
endef



# Helper function to list discovered projects
define list_projects
	@echo "Projects discovered: $(words $(MAKE_DIRS))"
	@for dir in $(MAKE_DIRS); do echo "  - $$dir"; done
	@echo ""
endef

endif


# Workspace-specific targets that don't need to be recursive
.PHONY: ai-context-files doctor install activate workspace-info

# AI Context Files (workspace-level only)
ai-context-files: ## Build AI context files for development
	@echo ""
	@echo "Building AI context files..."
	uv run python tools/build_ai_context_files.py
	uv run python tools/build_git_collector_files.py
	@echo "AI context files generated"
	@echo ""

# Show workspace info including available commands
workspace-info: ## Show workspace info and available commands
	@echo ""
	@echo "Recipe Tool Workspace"
	@echo "===================="
	@echo ""
	$(call list_projects)
	$(call list_commands)

# Workspace health check
doctor: ## Check workspace overall health
	@echo ""
	@echo "Checking workspace health..."
	@uv --version || (echo "❌ uv not found" && exit 1)
	@test -f uv.lock && echo "✅ Lock file exists" || echo "❌ Lock file missing"
	@test -d .venv && echo "✅ Virtual environment exists" || echo "❌ Virtual environment missing"
	@echo "Projects with Makefiles: $(words $(MAKE_DIRS))"
	@echo "Health check completed"
	@echo ""

# Workspace-level install (installs all dependencies)
install: ## Install/update all workspace dependencies
	@echo ""
	@echo "Installing workspace dependencies..."
	uv sync --group dev
	@echo "Workspace dependencies installed"
	@echo ""
	$(call list_commands)
	@$(MAKE) -s activate

ifeq ($(OS),Windows_NT)
activate: ## Show command to activate virtual environment
	@if exist .venv\Scripts\activate @echo "→ Run this command in your shell: .venv\Scripts\activate"
	@if not exist .venv\Scripts\activate @echo "✗ No virtual environment found. Run 'make install' first."
else
activate: ## Show command to activate virtual environment
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "\033[32m✓ Virtual environment already active\033[0m"; \
		echo ""; \
	elif [ -f .venv/bin/activate ]; then \
		echo "\033[33m→ Run this command: source .venv/bin/activate\033[0m"; \
		echo ""; \
	else \
		echo "\033[31m✗ No virtual environment found. Run 'make install' first.\033[0m"; \
	fi
endif

# Default goal is to show help
.DEFAULT_GOAL := help
help: ## Show available targets
	@echo ""
	@echo "Recipe Tool Workspace"
	@echo "====================="
	@echo ""
	@echo "Workspace targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Recursive targets (run across all projects):"
	@echo "  test                 Run tests in all projects"
	@echo "  lint                 Lint code in all projects"
	@echo "  format               Format code in all projects"
	@echo "  clean                Clean all projects"
	@echo ""
	@echo "Usage: make install  # Set up workspace dependencies"
	@echo ""
