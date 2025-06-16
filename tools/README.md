# Tools Directory

This directory contains utilities for the recipe-tool project.

## Core Utilities

### AI Context Generation

- `build_ai_context_files.py` - Main orchestrator for collecting project files into AI context documents
- `collect_files.py` - Core utility for pattern-based file collection with glob support
- `build_git_collector_files.py` - Downloads external documentation using git-collector

### Other Tools

- `execute_prompt_file.py` - Execute prompt files directly
- `list_by_filesize.py` - List files sorted by size for analysis

## Documentation Generation

### Generate AI Context System Guide

Generate comprehensive implementation documentation for the AI Context System:

```bash
# Generate with default settings
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=tools/ai-context-system-guide-outline.json

# Generate to specific output directory with specific model
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=tools/ai-context-system-guide-outline.json \
   output_root=output/docs \
   model=azure/o4-mini
```

This generates a practical implementation guide based on the actual working system in this repository.

See the [document_generator](../recipes/document_generator/README.md) recipe documentation for more details on the parameters you can specify.
