# Docpack

A package format for document outlines and resources. Docpack files (`.docpack`) are zip archives containing an outline JSON file and associated resource files.

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Create a docpack from an outline
docpack_file create --outline outline.json --output document.docpack

# Extract a docpack
docpack_file extract document.docpack --dir extracted/

# Validate a docpack
docpack_file validate document.docpack

# List docpack contents
docpack_file list document.docpack
```

### Python API

```python
from docpack import DocpackHandler
from pathlib import Path

# Create a docpack
outline_data = {"title": "My Document", "sections": [...]}
resource_files = [Path("file1.txt"), Path("file2.md")]
DocpackHandler.create_package(outline_data, resource_files, Path("output.docpack"))

# Extract a docpack
outline_data, resource_files = DocpackHandler.extract_package(
    Path("document.docpack"),
    Path("extract_dir")
)
```

## Outline Format

The outline JSON should follow the document generator format with:

- `title`: Document title
- `general_instruction`: Overall instructions for document generation
- `resources`: Array of resource objects with `key`, `path`, `title`, and `description`
- `sections`: Array of section objects with `title`, `prompt`, `sections` (for nesting), and `refs`
