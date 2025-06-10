# AI Context System Implementation Guide

[document-generator]

**Date:** 6/2/2025 10:23:59 PM

## Overview

An AI context generation system automates the collection and organization of codebase artifacts and library documentation into structured Markdown files that are optimized for AI-driven development tools. By automatically rolling up scattered source files, API references, and external docs into focused context bundles, the system ensures that large-language models (LLMs) always see a complete, up-to-date view of the project without manual prompt assembly.

Why It’s Valuable
- **Consistent Context**  
  Every module or library is presented in a self-contained Markdown roll-up, reducing missing dependencies or out-of-sync code in AI prompts.
- **Developer Efficiency**  
  Eliminates the need to manually gather files or update prompts when code changes.  
- **Modular Clarity**  
  Aligns with the project’s minimalist, modular design philosophy by producing only what’s needed now.

Recipe-Tool Implementation
In the recipe-tool project, AI context generation lives under the `ai_context/` directory and is driven by the built-in document generation pipeline:

  ai_context/
  ├── git_collector/   # External library documentation for reference
  └── generated/       # Project file roll-ups for LLM consumption (auto-generated)

1. **Ingest**: The pipeline reads all supported files in `ai_context/git_collector/` alongside selected code artifacts.  
2. **Transform**: It applies naming and grouping conventions—no extra abstractions, just direct Markdown summaries.  
3. **Emit**: Consolidated `.md` files are written to `ai_context/generated/`, ready for LLM ingestion.

This implementation leverages the project’s core design principles—ruthless simplicity, minimal abstractions, and end-to-end thinking—to deliver a practical, self-maintaining context layer for AI development workflows.

## What This System Does

This system automates rolling up your code and recipe definitions into self-contained Markdown documents for AI consumption. At its core, it uses two components:

1. Collect-Files Utility (tools/collect_files.py)
   - Recursively scans directories and patterns, applies default and user-supplied `--exclude`/`--include` filters, and formats each file with a header and its content.
   - For example, running:
     ```bash
     python tools/collect_files.py recipe-executor/recipe_executor \
       --exclude ".venv,node_modules,*.lock,.git,__pycache__,*.pyc,*.ruff_cache,logs,output" \
       --include "README.md,pyproject.toml,.env.example" \
       --format markdown > ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md
     ```
     produces `ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md` starting with:
     # recipe-executor/recipe_executor
     [collect-files]
     **Search:** ['recipe-executor/recipe_executor']
     **Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
     **Include:** ['README.md', 'pyproject.toml', '.env.example']
     **Date:** 5/28/2025, 12:47:25 PM
     **Files:** 26
     
     And individual file sections such as:
     === File: .env.example ===
     # Optional for the project
     #LOG_LEVEL=DEBUG
     ...

2. Build Script (tools/build_ai_context_files.py)
   - Imports `collect_files` and defines a list of tasks, each mapping `patterns`, `exclude`, `include`, and an `output` path under `ai_context/generated/`.
   - Example task for document-generator recipes:
     {
       "patterns": ["recipes/document_generator"],
       "output": "ai_context/generated/DOCUMENT_GENERATOR_RECIPE_FILES.md",
       "exclude": collect_files.DEFAULT_EXCLUDE,
       "include": []
     }
   - Running `python tools/build_ai_context_files.py` (or `make ai-context-files`) iterates tasks, collects matching files, and writes headers plus file contents. For instance, `DOCUMENT_GENERATOR_RECIPE_FILES.md` begins with:
     # recipes/document_generator
     [collect-files]
     **Search:** ['recipes/document_generator']
     **Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
     **Include:** []
     **Date:** 5/27/2025, 2:32:39 PM
     **Files:** 11

Resulting Markdown roll-ups (e.g., `RECIPE_EXECUTOR_CODE_FILES.md` and `DOCUMENT_GENERATOR_RECIPE_FILES.md`) are committed under `ai_context/generated/`. These files provide complete, up-to-date context bundles—every source file, config, and recipe definition—ready for downstream LLM-driven document generation or analysis.

## Implementation Steps

Follow these steps to stand up the AI context generation system in your own project. We’ll copy the core scripts, tailor the task list, hook it into your Makefile, and then run a smoke test.

1. Copy the core modules
   • Create a `tools/` folder (if you don’t already have one) and copy in the two Python scripts that drive collection and build:
     ```bash
     mkdir -p tools
     cp path/to/original/collect_files.py tools/collect_files.py
     cp path/to/original/build_ai_context_files.py tools/build_ai_context_files.py
     ```
   • These provide:
     - `collect_files.py` → recursively scans your code, applies default and custom `--exclude`/`--include` filters, and formats output.
     - `build_ai_context_files.py` → defines a tasks array and invokes `collect_files.collect_files` to emit per-pattern Markdown roll-ups.

2. Customize the task list
   • Open `tools/build_ai_context_files.py` and locate the `tasks = [ … ]` block near the top.  
   • Replace or extend it with exactly the modules you want to ship to LLMs. For example, to collect your document-generator recipes and the recipe-tool app:
     ```python
     tasks = [
         {
             "patterns": ["recipes/document_generator"],
             "output": f"{OUTPUT_DIR}/DOCUMENT_GENERATOR_RECIPE_FILES.md",
             "exclude": collect_files.DEFAULT_EXCLUDE,
             "include": [],
         },
         {
             "patterns": ["apps/recipe-tool/recipe_tool_app"],
             "output": f"{OUTPUT_DIR}/RECIPE_TOOL_APP_CODE_FILES.md",
             "exclude": collect_files.DEFAULT_EXCLUDE,
             "include": [],
         },
         # …add more entries for recipe-executor, blueprints, examples, etc.
     ]
     ```
   • Each task maps:
     - `patterns`: glob or directory path(s) to collect
     - `exclude`: usually `collect_files.DEFAULT_EXCLUDE`
     - `include`: any additional files (e.g. `README.md`, `pyproject.toml`)
     - `output`: target file under `ai_context/generated/`

3. Wire up the Makefile target
   • In your root `Makefile`, add (or confirm you have) an `ai-context-files` target that invokes both build scripts.  For example:
     ```makefile
     .PHONY: ai-context-files
     ai-context-files: ## Build AI context files for development
      	@echo "Building AI context files..."
      	@python tools/build_ai_context_files.py
      	@python tools/build_git_collector_files.py
      	@echo "→ Outputs: ai_context/generated/ and ai_context/git_collector/"
     ```
   • This ensures `make ai-context-files`:
     - Creates `ai_context/generated/` if missing
     - Runs each task, skipping unchanged files
     - Falls back to `git-collector` via NPX if needed for external docs

4. Run and verify
   • From your repo root, simply run:
     ```bash
     make ai-context-files
     ```
   • You should see output like:
     ```text
     Building AI context files...
     Collecting files for patterns: ['recipes/document_generator']
     Found 11 files.
     Written to ai_context/generated/DOCUMENT_GENERATOR_RECIPE_FILES.md
     Collecting files for patterns: ['apps/recipe-tool/recipe_tool_app']
     Found 8 files.
     Written to ai_context/generated/RECIPE_TOOL_APP_CODE_FILES.md
     → Outputs: ai_context/generated/ and ai_context/git_collector/
     ```
   • Validate one of the generated roll-ups:
     ```bash
     head -n 20 ai_context/generated/DOCUMENT_GENERATOR_RECIPE_FILES.md
     ```
   • You should see the metadata header and first file section:
     ```markdown
     # recipes/document_generator
     [collect-files]
     **Search:** ['recipes/document_generator']
     **Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
     **Include:** []
     **Date:** 6/2/2025, 11:15:03 AM
     **Files:** 11

     === File: recipe_generator.py ===
     ```

That’s it – you now have an automated AI context layer that rolls up exactly the code and docs your LLMs need, on demand and in lock-step with your repository.

## Configuration and Customization

Once the core scripts are in place, you can tailor exactly **what** and **how** files are rolled up for your AI contexts. Below are the most common customization patterns using the actual task format from `tools/build_ai_context_files.py` and the `collect_files.py` implementation.

### 1. Editing the Task List
Open `tools/build_ai_context_files.py` and locate the `tasks = [ … ]` list. Each task is a dict with four keys:

```python
tasks = [
  {
    "patterns": ["recipes/document_generator"],
    "output": f"{OUTPUT_DIR}/DOCUMENT_GENERATOR_RECIPE_FILES.md",
    "exclude": collect_files.DEFAULT_EXCLUDE,
    "include": [],
  },
  {
    "patterns": ["apps/recipe-tool/recipe_tool_app"],
    "output": f"{OUTPUT_DIR}/RECIPE_TOOL_APP_CODE_FILES.md",
    "exclude": collect_files.DEFAULT_EXCLUDE,
    "include": ["README.md", "pyproject.toml"],
  },
  # … add more entries for each module or directory
]
```

– **patterns**: glob(s) or directories to scan
– **exclude**: a list of fnmatch-style patterns (combine your own with `DEFAULT_EXCLUDE`)
– **include**: overrides to re-include files that would otherwise match an exclude
– **output**: target Markdown under `ai_context/generated`

### 2. Fine-Tuning Exclude/Include
The default exclude list lives in `collect_files.py`:

```python
DEFAULT_EXCLUDE = [
  ".venv", "node_modules", "*.lock", ".git",
  "__pycache__", "*.pyc", "*.ruff_cache", "logs", "output"
]
```

To add project-specific ignores, pass a custom exclude string or list:

```bash
python tools/collect_files.py src/**/*.py \
  --exclude "${DEFAULT_EXCLUDE},tests/slow,legacy/*" \
  --include "legacy/readme.md" \
  --format markdown > my_src_rollup.md
```

Or in your build script:
```python
my_excludes = collect_files.DEFAULT_EXCLUDE + ["tests/slow", "legacy/*"]
tasks.append({
  "patterns": ["src"],
  "output": f"{OUTPUT_DIR}/SRC_CODE_FILES.md",
  "exclude": my_excludes,
  "include": ["README.md"],
})
```

### 3. Splitting Strategies for Performance
When your repo grows large, split collections into smaller tasks so each `collect_files` invocation scans a narrower tree:

```python
# Instead of one giant scan:
#   patterns=["."]
# do two parallel tasks:
tasks = [
  {"patterns": ["src/core/**"], ...},
  {"patterns": ["src/plugins/**"], ...},
]
```

This reduces I/O overhead and lets you track which layer changed when rerunning only the affected roll-up.

### 4. Pattern Resolution and Recursion
`collect_files` uses `glob.glob(..., recursive=True)` combined with `fnmatch` on absolute and component paths. You can target subtrees directly:

```python
# Collect only Python and Markdown in docs/:
tasks.append({
  "patterns": ["docs/**/*.py", "docs/**/*.md"],
  "exclude": collect_files.DEFAULT_EXCLUDE,
  "include": [],
  "output": f"{OUTPUT_DIR}/DOCS_FILES.md",
})
```

If you need to handle relative paths with `..`, the `resolve_pattern` helper will normalize them for you.

### 5. Putting It All Together
1. **Define granular tasks** in `build_ai_context_files.py`—one per logical component.
2. **Leverage `DEFAULT_EXCLUDE`** but extend it for your legacy, test, or generated folders.
3. **Use `include`** to pull in important top-level files (e.g., `README.md`, `LICENSE`, `pyproject.toml`).
4. **Partition large code trees** into multiple tasks to speed up scanning and minimize rebuild scope.

With these patterns in place, your AI context pipeline remains both **powerful** and **fast**, producing just the right roll-ups for downstream LLM-driven document generation or analysis.

## Setup and Usage

This section shows how to hook AI context generation into your day-to-day workflow using the `ai-context-files` Make target and the underlying build scripts. You’ll learn how to run, force-regenerate, and maintain your context bundle without touching any of your usual CI/development commands.

### 1. Hook into Your Makefile

Ensure you have the following `ai-context-files` target in the root Makefile (this is the one from the recipe-tool workspace):

```makefile
.PHONY: ai-context-files
ai-context-files: ## Build AI context files for development
	@echo ""
	@echo "Building AI context files..."
	@python tools/build_ai_context_files.py
	@python tools/build_git_collector_files.py
	@echo "AI context files generated"
	@echo ""
```

This target will:
- Run `build_ai_context_files.py` to collect your code/recipe files into `ai_context/generated/`.
- Run `build_git_collector_files.py` to fetch external docs into `ai_context/git_collector/`.

### 2. Basic Commands

Once the Makefile is in place, here’s your daily driver:

  • **Generate or update all contexts**

    ```bash
    make ai-context-files
    ```

    *Output example:*  
    ```text
    Building AI context files...
    Collecting files for patterns: ['recipes/document_generator']
    Found 11 files.
    Written to ai_context/generated/DOCUMENT_GENERATOR_RECIPE_FILES.md
    → git-collector → success
    AI context files generated
    ```

  • **Inspect the diff** (Git):

    ```bash
    git diff ai_context/generated/
    ```

### 3. Force Regeneration

By default, the build script skips writing files whose content (aside from the timestamp) hasn’t changed. To override this and regenerate everything:

  1. **Direct script flag**

     ```bash
     python tools/build_ai_context_files.py --force
     ```

  2. **Remove outputs then rebuild**

     ```bash
     rm -rf ai_context/generated/* ai_context/git_collector/*
     make ai-context-files
     ```

Use `--force` or a clean-and-make cycle when you:
- Add or remove tasks in `build_ai_context_files.py`.
- Change header formats or metadata logic.

### 4. Maintenance Tasks

Keep your AI context system healthy with these routines:

  • **Update your task list**  
    Edit `tools/build_ai_context_files.py` → `tasks = [ … ]` → add/remove patterns, adjust `exclude`/`include` lists.

  • **Prune stale files**  
    If you remove a module or rename a directory, manually delete its Markdown under `ai_context/generated/` before rerunning.

  • **Verify external docs**  
    Occasionally re-run `build_git_collector_files.py` alone:
    ```bash
    python tools/build_git_collector_files.py
    ```

  • **CI integration**  
    Add `make ai-context-files` as a lightweight check in your CI pipeline to ensure context docs stay up to date.

With these commands and habits in place, your AI context layer remains in lock-step with your repository—always fresh, accurate, and ready for LLM-powered tooling.

## Examples and Templates

Below are ready-to-use code templates and command examples based on the real `recipe-tool` patterns. Copy, paste, and customize these snippets to stand up your own AI context generation pipeline.

### 1. build_ai_context_files.py – Task List Template

In `tools/build_ai_context_files.py`, define a `tasks` array mapping your project modules to generated Markdown roll-ups. Reuse `collect_files.DEFAULT_EXCLUDE` and add project-specific excludes or includes as needed.

```python
# tools/build_ai_context_files.py

from tools import collect_files

OUTPUT_DIR = "ai_context/generated"

tasks = [
    {
        "patterns": ["src/core/**/*"],
        "output": f"{OUTPUT_DIR}/CORE_CODE_FILES.md",
        "exclude": collect_files.DEFAULT_EXCLUDE + ["tests/*", "legacy/**"],
        "include": ["README.md", "pyproject.toml"],
    },
    {
        "patterns": ["src/plugins/**"],
        "output": f"{OUTPUT_DIR}/PLUGINS_CODE_FILES.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
]

# (keep the rest of the script unchanged)
```

**Key fields**
- `patterns`: glob or directory path(s) to scan (supports `**`, `*`, relative navigation).
- `exclude`: list of fnmatch patterns to skip (defaults in `collect_files.py`).
- `include`: override exclusions to re-include files (e.g. docs, configs).
- `output`: Markdown file under your `OUTPUT_DIR`.


### 2. One-Off collect_files Command

If you need ad-hoc roll-ups, call `collect_files.py` directly from your shell:

```bash
python tools/collect_files.py \
  "src/**/*.py" \
  --exclude ".venv,node_modules,*.pyc,build" \
  --include "README.md,pyproject.toml" \
  --format markdown \
  > ai_context/generated/SRC_CODE_ROLLUP.md
```

- Use commas to separate multiple exclude/include patterns.
- `--format markdown` wraps each file in triple-backtick fences and headers.


### 3. Makefile Integration Snippet

Add an `ai-context-files` target to your root `Makefile` so teammates can regenerate contexts with one command:

```makefile
.PHONY: ai-context-files
ai-context-files:  ## Generate AI context bundles
	@echo "→ Building code roll-ups..."
	@python tools/build_ai_context_files.py
	@python tools/build_git_collector_files.py
	@echo "✓ AI context files written to ai_context/generated/ and ai_context/git_collector/"
```


### 4. Troubleshooting Tips

• **No files found**: Check your `patterns` syntax—ensure globs match your directory structure and you’re running from the repo root.

• **Excluded files still appear**: Verify that your `exclude` list is being applied component-wise (folder names, file names). Use `--include` to re-include specific files.

• **Output not updating**: By default, the build script skips writes when only the timestamp changed. Use `--force` on `build_ai_context_files.py` to overwrite everything.

• **Permission errors**: Ensure your Python process has write access to `ai_context/generated/`. On Unix, you may need `chmod -R u+w ai_context/generated/`.

• **Slow scans**: Split a large codebase into multiple smaller tasks (e.g., core vs. plugins) to reduce I/O per invocation.


### 5. Best Practices

- Leverage `collect_files.DEFAULT_EXCLUDE` and only extend it sparingly for project-specific folders (e.g. `legacy/`, `tests/slow`).
- Always include top-level docs (`README.md`, `LICENSE`, `pyproject.toml`) via the `include` list.
- Group logically related modules into separate tasks to speed up incremental runs and isolate changes.
- Hook the Makefile target into your CI pipeline (e.g. `make ai-context-files`) to guard against stale context docs.
- Use descriptive output filenames (`CORE_CODE_FILES.md`, `PLUGINS_CODE_FILES.md`) so LLM prompts can reference them unambiguously.

With these examples and templates in place, you’ll have a turn-key AI context generation system that mirrors the `recipe-tool` implementation—automated, maintainable, and optimized for AI workflows.