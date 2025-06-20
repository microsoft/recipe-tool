# ReadFilesStep Component Specification

## Purpose

The ReadFilesStep component reads one or more files from the filesystem and stores their content in the execution context. It serves as a foundational step for loading data into recipes (such as specifications, templates, and other input files) with support for both single-file and multi-file operations.

## Core Requirements

- Read a file or multiple files from specified path(s)
- Support input specified as a single path string, a comma-separated string of paths, or a list of path strings
- If a single string is provided, detect commas to determine if it represents multiple paths and split accordingly
- Support template-based path resolution for all paths
- Store all file content in the context under a single specified key
- Support reading files in text format with UTF-8 encoding
- Where possible, deserialize the content to a Python object (e.g., JSON, YAML) if the file format allows
- Provide flexible content merging options for multi-file reads
- Support optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow a minimal design with clear error handling

## Implementation Considerations

- Render template strings for the `path` parameter before evaluating the input type
- Use template rendering to support dynamic paths for single path, comma-separated paths in one string, and lists of paths
- Render template strings for the `content_key` parameter
- Handle glob pattern in files
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement an `optional` flag to continue execution if files are missing
- For multiple files, provide a way to merge content (default: concatenate with newlines separating each file’s content)
- Provide a clear content structure when reading multiple files (e.g. a dictionary with filenames as keys)
- Keep the implementation simple and focused on a single responsibility
- Support both single-file and multi-file read operations

## Logging

- Debug: Log each file path before attempting to read (useful for diagnosing failures)
- Info: Log the successful reading of each file (including its path) and the final storage key used in the context

## Component Dependencies

### Internal Components

- **Step Interface**: Implements the step interface via StepProtocol
- **Context**: Stores file content using a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils/Templates**: Uses render_template for dynamic path resolution

### External Libraries

- **pyyaml**: For parsing YAML files if the content is in YAML format

### Configuration Dependencies

None

## Error Handling

- Raise a FileNotFoundError with a clear message when required files do not exist
- Support the `optional` flag to continue execution (with empty content) if files are missing
- Handle error cases differently for single-file versus multiple-file scenarios
- Log appropriate warnings and information during execution
- When reading multiple files and some are optional, continue processing those files that exist

## Output Files

- `recipe_executor/steps/read_files.py`
