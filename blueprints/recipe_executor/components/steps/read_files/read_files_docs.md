# ReadFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.read_files import ReadFilesStep, ReadFilesConfig
```

## Configuration

The ReadFilesStep is configured with a ReadFilesConfig:

```python
class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name to store the file content in context (may be templated).
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + content
            - "dict": Store a dictionary with filenames as keys and content as values
    """
    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"
```

## Step Registration

The ReadFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_files import ReadFilesStep

STEP_REGISTRY["read_files"] = ReadFilesStep
```

## Basic Usage in Recipes

### Reading a Single File

The ReadFilesStep can be used to read a single file (just like the original `read_file` step):

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md",
        "content_key": "component_spec"
      }
    }
  ]
}
```

### Reading Multiple Files

You can read multiple files by providing a comma-separated string of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md,specs/component_docs.md",
        "content_key": "component_specs"
      }
    }
  ]
}
```

You can also read multiple files by providing a list of path strings:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/component_spec.md", "specs/component_docs.md"],
        "content_key": "component_specs",
        "merge_mode": "concat"
      }
    }
  ]
}
```

### Reading Multiple Files as a Dictionary

You can store multiple files as a dictionary with filenames as keys:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/component_spec.md", "specs/component_docs.md"],
        "content_key": "component_specs",
        "merge_mode": "dict"
      }
    }
  ]
}
```

## Template-Based Paths

The `path` parameter can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/{{ component_id }}_spec.md",
        "content_key": "component_spec"
      }
    }
  ]
}
```

Template variables can also be used within list paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": [
          "specs/{{ component_id }}_spec.md",
          "specs/{{ component_id }}_docs.md"
        ],
        "content_key": "{{ component_id }}_files"
      }
    }
  ]
}
```

## Optional Files

You can specify that files are optional. If an optional file doesn't exist, execution will continue:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/required_file.md", "specs/optional_file.md"],
        "content_key": "component_files",
        "optional": true
      }
    }
  ]
}
```

If an optional file is not found:

- For a single file: an empty string is stored in the context
- For multiple files with `merge_mode: "concat"`: the missing file is skipped in the concatenated result
- For multiple files with `merge_mode: "dict"`: the missing file is omitted from the dictionary

## Common Use Cases

**Loading Multiple Related Specifications**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "specs/{{ component_id }}_spec.md",
      "specs/{{ component_id }}_docs.md"
    ],
    "content_key": "component_files",
    "merge_mode": "concat"
  }
}
```

**Loading Templates with Optional Components**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "templates/email_base.txt",
      "templates/email_header.txt",
      "templates/email_footer.txt"
    ],
    "content_key": "email_templates",
    "optional": true,
    "merge_mode": "dict"
  }
}
```

**Dynamic Path Resolution with Multiple Files**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "docs/{{ project }}/{{ component }}/README.md",
      "docs/{{ project }}/{{ component }}/USAGE.md"
    ],
    "content_key": "documentation",
    "merge_mode": "dict"
  }
}
```

**Command Line Integration**:

You can also supply paths via command-line context values:

```bash
recipe-tool --execute recipes/generate.json files_to_read="specs/component_a.md,specs/component_b.md"
```

Then in the recipe you can use that context value:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ files_to_read.split(',') | default: 'specs/default.md' }}",
        "content_key": "input_files"
      }
    }
  ]
}
```

## Important Notes

- The step uses UTF-8 encoding by default for all files
- If the file is JSON, it will be parsed and stored as a dictionary
- When a file is optional and missing, it is handled according to the specified `merge_mode`
- Template variables in all paths are resolved before reading the files
- When using `merge_mode: "dict"`, the keys in the output are the full paths of the files
- All paths support template rendering (including each path in a list)
