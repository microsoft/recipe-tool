# blueprints/recipe_executor

[collect-files]

**Search:** ['blueprints/recipe_executor']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 1:25:39 PM
**Files:** 55

=== File: blueprints/recipe_executor/README.md ===
# Recipe Executor Recipes

This directory contains the recipes used for generating the Recipe Executor components. These recipes demonstrate the self-generating capability of the Recipe Executor system.

## Generate the Recipe Executor Code

The Recipe Executor can generate its own codebase from a component manifest file and individual component documentation/specification files. This is done using the `codebase_generator` recipe.
To generate the codebase, you can run the following command:

```bash
# Generate the Recipe Executor codebase using the defaults
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json
```

This command will generate the codebase for the Recipe Executor, using the existing code as a reference and adjusting for changes to the source documentation/specification files.
Instead of generating the entire codebase, you can generate just the code for a specific module. For example, to generate the code for the `steps.llm_generate` module, run:

```bash
# Generate code for a specific module
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
    edit=true \
    component_id=steps.llm_generate
```

You can also run with `edit` set to `false` to generate code without using the existing code as a reference.

```bash
# Generate code without using existing code as a reference
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
    edit=false
```

See the [codebase_generator](../../recipes/codebase_generator/README.md) recipe documentation for more details on the parameters you can specify.

## Generating Documentation

The Recipe Executor can generate its own documentation using the `document_generator` recipe. This is useful for creating up-to-date documentation based on the current state of the codebase.
To generate documentation, you can run the following command:

```bash
# Generate documentation for the Recipe Executor
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
    outline_file=blueprints/recipe_executor/outlines/recipe-json-authoring-guide.json \
    output_root=output/docs \
    model=openai/o4-mini
```

This command will create documentation from a structured outline configuration file, reading in referenced resources, including sections for each component, their specifications, and any relevant resources. The generated documentation will be saved in the specified output directory.

See the [document_generator](../../recipes/document_generator/README.md) recipe documentation for more details on the parameters you can specify.


=== File: blueprints/recipe_executor/components.json ===
[
  {
    "id": "config",
    "deps": [],
    "refs": []
  },
  {
    "id": "context",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "executor",
    "deps": ["protocols", "logger", "models", "steps.registry"],
    "refs": []
  },
  {
    "id": "logger",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "main",
    "deps": ["config", "context", "executor", "logger", "protocols"],
    "refs": []
  },
  {
    "id": "models",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "protocols",
    "deps": ["models"],
    "refs": []
  },
  {
    "id": "llm_utils.azure_openai",
    "deps": ["context", "logger", "protocols"],
    "refs": [
      "AZURE_IDENTITY_CLIENT_DOCS.md",
      "git_collector/PYDANTIC_AI_DOCS.md"
    ]
  },
  {
    "id": "llm_utils.llm",
    "deps": [
      "context", "logger",
      "llm_utils.azure_openai",
      "llm_utils.mcp", "protocols",
      "llm_utils.responses",
      "llm_utils.azure_responses"
    ],
    "refs": ["git_collector/PYDANTIC_AI_DOCS.md"]
  },
  {
    "id": "llm_utils.mcp",
    "deps": ["logger"],
    "refs": ["git_collector/PYDANTIC_AI_DOCS.md"]
  },
  {
    "id": "llm_utils.responses",
    "deps": ["logger"],
    "refs": ["git_collector/PYDANTIC_AI_DOCS.md"]
  },
  {
    "id": "llm_utils.azure_responses",
    "deps": ["logger"],
    "refs": [
      "AZURE_IDENTITY_CLIENT_DOCS.md",
      "git_collector/PYDANTIC_AI_DOCS.md"
    ]
  },
  {
    "id": "steps.base",
    "deps": ["logger", "protocols"],
    "refs": []
  },
  {
    "id": "steps.conditional",
    "deps": ["context", "protocols", "steps.base", "utils.templates"],
    "refs": []
  },
  {
    "id": "steps.execute_recipe",
    "deps": [
      "context",
      "executor",
      "protocols",
      "steps.base",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.llm_generate",
    "deps": [
      "context",
      "models",
      "llm_utils.llm",
      "llm_utils.mcp",
      "protocols",
      "steps.base",
      "utils.models",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.loop",
    "deps": [
      "context",
      "executor",
      "protocols",
      "steps.base",
      "steps.registry",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.mcp",
    "deps": ["context", "protocols", "steps.base", "utils.templates"],
    "refs": ["git_collector/MCP_PYTHON_SDK_DOCS.md"]
  },
  {
    "id": "steps.parallel",
    "deps": ["protocols", "steps.base", "steps.registry"],
    "refs": []
  },
  {
    "id": "steps.read_files",
    "deps": ["context", "protocols", "steps.base", "utils.templates"],
    "refs": []
  },
  {
    "id": "steps.registry",
    "deps": [],
    "refs": []
  },
  {
    "id": "steps.set_context",
    "deps": ["context", "protocols", "steps.base", "utils.templates"],
    "refs": []
  },
  {
    "id": "steps.write_files",
    "deps": ["context", "models", "protocols", "steps.base", "utils.templates"],
    "refs": []
  },
  {
    "id": "utils.models",
    "deps": [],
    "refs": []
  },
  {
    "id": "utils.templates",
    "deps": ["protocols"],
    "refs": ["git_collector/LIQUID_PYTHON_DOCS.md"]
  }
]


=== File: blueprints/recipe_executor/components/config/config_docs.md ===
# Config Component Usage

## Importing

```python
from recipe_executor.config import load_configuration, RecipeExecutorConfig
```

## Interface (Public API)

```python
from typing import Dict, List, Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class RecipeExecutorConfig(BaseSettings):
    """Configuration for recipe executor API keys and credentials.

    This class automatically loads values from environment variables
    and .env files.
    """

    # Standard AI Provider API Keys (following PydanticAI patterns)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Azure OpenAI Credentials
    azure_openai_api_key: Optional[str] = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_base_url: Optional[str] = Field(default=None, alias="AZURE_OPENAI_BASE_URL")
    azure_openai_api_version: Optional[str] = Field(default="2025-03-01-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: Optional[str] = Field(default=None, alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_use_managed_identity: bool = Field(default=False, alias="AZURE_USE_MANAGED_IDENTITY")
    azure_client_id: Optional[str] = Field(default=None, alias="AZURE_CLIENT_ID")

    # Ollama Settings
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_EXECUTOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def load_configuration(recipe_env_vars: Optional[List[str]] = None) -> Dict[str, Any]:
    """Load configuration from environment variables.

    Args:
        recipe_env_vars: Optional list of additional environment variable names
                        that the recipe requires. These will be loaded and added
                        to the configuration with lowercase keys.

    Returns:
        Dictionary containing all configuration values, with None values excluded.
    """
```

## Basic Usage

```python
# Load standard configuration
config = load_configuration()

# Access configuration values
openai_key = config.get("openai_api_key")
azure_base_url = config.get("azure_openai_base_url")
```

## With Recipe-Specific Variables

```python
# Recipe declares required environment variables
recipe_env_vars = ["BRAVE_API_KEY", "CUSTOM_ENDPOINT"]

# Load configuration including recipe-specific vars
config = load_configuration(recipe_env_vars)

# Access recipe-specific values (note: keys are lowercase)
brave_key = config.get("brave_api_key")
custom_endpoint = config.get("custom_endpoint")
```

## Integration with Context

```python
from recipe_executor.context import Context
from recipe_executor.config import load_configuration

# Load configuration
config = load_configuration(recipe.env_vars if recipe else None)

# Create context with configuration
context = Context(
    artifacts={},
    config=config
)

# Components can access config through context
api_key = context.get_config().get("openai_api_key")
```

## Standard Environment Variables

The Config component automatically loads these environment variables:

| Variable                       | Description                        | Default                  |
| ------------------------------ | ---------------------------------- | ------------------------ |
| `OPENAI_API_KEY`               | API key for OpenAI                 | None                     |
| `ANTHROPIC_API_KEY`            | API key for Anthropic              | None                     |
| `AZURE_OPENAI_API_KEY`         | API key for Azure OpenAI           | None                     |
| `AZURE_OPENAI_BASE_URL`        | Base URL for Azure OpenAI endpoint | None                     |
| `AZURE_OPENAI_API_VERSION`     | API version for Azure OpenAI       | "2025-03-01-preview"     |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name for Azure OpenAI   | None                     |
| `AZURE_USE_MANAGED_IDENTITY`   | Use Azure managed identity         | false                    |
| `AZURE_CLIENT_ID`              | Client ID for managed identity     | None                     |
| `OLLAMA_BASE_URL`              | Base URL for Ollama API            | "http://localhost:11434" |

## Recipe-Specific Variables

Recipes can declare additional required environment variables:

```json
{
  "env_vars": ["BRAVE_API_KEY", "WEATHER_API_KEY"],
  "steps": [...]
}
```

These variables will be automatically loaded and made available with lowercase keys:

- `BRAVE_API_KEY` → `brave_api_key`
- `WEATHER_API_KEY` → `weather_api_key`

## Configuration Access Patterns

## In Step Implementations

```python
def execute(self, context: Context) -> Dict[str, Any]:
    # Get API key from context config
    api_key = context.get_config().get("openai_api_key")

    # Use default if not set
    model = context.get_config().get("llm_model", "gpt-4")
```

## In Templates

Configuration values are accessible in Liquid templates through context:

```liquid
API Key: {{ openai_api_key }}
Endpoint: {{ azure_openai_base_url | default: "https://api.openai.com" }}
```

## Important Notes

- All configuration keys are converted to lowercase for consistency
- Always check if optional configuration exists before using
- Use sensible defaults for optional configuration
- Clearly document which environment variables your recipe needs
- Never hardcode API keys or secrets in recipe files
- API keys and credentials are sensitive data - never log or print them
- Use environment variables or .env files (not committed to version control)
- The config component automatically excludes None values


=== File: blueprints/recipe_executor/components/config/config_spec.md ===
# Config Component Specification

## Purpose

The Config component provides centralized configuration management for the recipe executor, focusing on loading API keys and credentials from environment variables and making them available through the context.

## Core Requirements

- Load standard API keys and credentials from environment variables
- Support loading custom environment variables declared by recipes
- Provide configuration values to other components through context.config
- Handle .env file loading and environment variable parsing
- Use Pydantic BaseSettings for type-safe configuration
- Convert environment variable names to lowercase keys for consistent access
- Exclude None values from the returned configuration dictionary

## Implementation Considerations

- Use Pydantic BaseSettings to define configuration schema
- Define fields for all standard API keys and credentials
- Support .env file loading (though main component handles the actual loading)
- Implement a `load_configuration` function that:
  - Creates a RecipeExecutorConfig instance
  - Converts the config to a dictionary excluding None values
  - Loads any recipe-specific environment variables
  - Returns the merged configuration dictionary
- Convert recipe-specific env var names to lowercase for consistency
- Use descriptive field names and include descriptions for each field

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic-settings** - Uses BaseSettings for automatic environment variable loading and validation
- **typing** - Uses type annotations for function signatures and field definitions

### Configuration Dependencies

The component loads these environment variables:

- **OPENAI_API_KEY** - (Optional) API key for OpenAI
- **ANTHROPIC_API_KEY** - (Optional) API key for Anthropic
- **AZURE_OPENAI_API_KEY** - (Optional) API key for Azure OpenAI
- **AZURE_OPENAI_BASE_URL** - (Optional) Base URL for Azure OpenAI endpoint
- **AZURE_OPENAI_API_VERSION** - (Optional) API version for Azure OpenAI, defaults to "2025-03-01-preview"
- **AZURE_OPENAI_DEPLOYMENT_NAME** - (Optional) Deployment name for Azure OpenAI
- **AZURE_USE_MANAGED_IDENTITY** - (Optional) Use Azure managed identity for authentication, defaults to False
- **AZURE_CLIENT_ID** - (Optional) Client ID for Azure managed identity
- **OLLAMA_BASE_URL** - (Optional) Base URL for Ollama API, defaults to "http://localhost:11434"

## Output Files

- `recipe_executor/config.py`

## Logging

None

## Error Handling

- Missing environment variables should not cause errors (return None)
- Invalid values should be logged but not prevent execution
- Recipe-specific env vars that don't exist are simply not included
- No exceptions should be raised for missing configuration

## Dependency Integration Considerations

None

=== File: blueprints/recipe_executor/components/context/context_docs.md ===
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
from recipe_executor.protocols import ContextProtocol
```

_(The `ContextProtocol` interface is imported for typing or interface reference, while `Context` is the concrete class you instantiate.)_

## Initialization

You can create a Context with or without initial data:

```python
# Create an empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"input": "example data"})

# With configuration values
context = Context(config={"run_mode": "test"})

# With both artifacts and configuration
context = Context(
    artifacts={"input": "example data"},
    config={"run_mode": "test"}
)
```

When providing initial artifacts or config, Context will deep-copy them. Changes to the original dictionaries after creation won’t affect the Context.

## Core API

Once you have a Context, you use it like a dictionary for artifacts:

### Storing Values

```python
context["result"] = 42
```

Stores the value `42` under the key `"result"` in the context’s artifacts.

### Retrieving Values

```python
value = context["result"]          # Retrieves the value for "result" (KeyError if missing)
value_or_default = context.get("missing", default_value)
```

Use `context[key]` for direct access (which will throw an error if the key is not present), or `context.get(key, default)` to safely retrieve a value with a fallback.

### Checking for Keys

```python
if "result" in context:
    # Key exists in context
    print(context["result"])
```

The `in` operator checks if a given artifact key exists in the context.

### Iterating over Keys

```python
for key in context:
    print(key, context[key])

# Or equivalently:
for key in context.keys():
    print(key, context[key])
```

Context supports iteration, yielding each artifact key (internally, it iterates over a snapshot list of keys to avoid issues if you modify the context during iteration). You can also call `keys()` to get an iterator of keys explicitly. The `len(context)` function returns the number of artifacts currently stored.

### Getting All Values

```python
snapshot = context.dict()
```

`dict()` returns a deep copy of all artifacts in the context as a regular Python dictionary. This is useful if you need to inspect or serialize the entire state without risk of modifying the Context itself.

```python
snapshot_json = context.json()
```

`json()` returns a JSON string representation of the context’s artifacts. This is useful for logging or sending the context over a network.

### Cloning the Context

```python
new_context = context.clone()
```

The `clone()` method creates a deep copy of the Context, including all artifacts and configuration. The returned object is a new `Context` instance that can be modified independently of the original. This is often used when running sub-recipes or parallel steps to ensure each execution has an isolated context state.

### Configuration Management

The Context class manages configuration values separately from artifacts. You can retrieve the entire configuration dictionary with `get_config()`, or set it with `set_config()`. This allows you to manage recipe-specific configuration values without cluttering the artifact namespace.

```python
# Get a configuration value
config = context.get_config()
api_key = config.get("api_key")

# Set a configuration value
context.set_config(config)
```

## Important Notes

- **Shared State**: The Context is shared across all steps in a recipe execution. Any step that writes to the context (e.g., `context["x"] = value`) is making that data available to subsequent steps. This is how data flows through a recipe.
- **No Thread Safety**: The Context class does not implement any locking or thread-safety mechanisms. It assumes sequential access. If you need to use it in parallel, each parallel thread or process should work on a cloned copy of the Context to avoid race conditions (as done in the Parallel step implementation).
- **Protocols Interface**: The `Context` class implements the `ContextProtocol` interface defined in the Protocols component. When writing code that interacts with contexts, you can use `ContextProtocol` in type hints to allow any context implementation. In practice, you will typically use the provided `Context` class unless you extend the system.
- **Configuration vs Artifacts**: Remember that context configuration is only available via `context.get_config()` and `context.set_config()`. It is not manipulated via the dictionary interface (`__getitem__`/`__setitem__`). This separation is by convention; Context does not prevent you from modifying the configuration, so it is up to developers to decide how to manage configuration values.


=== File: blueprints/recipe_executor/components/context/context_spec.md ===
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple, dictionary-like interface that steps and other components use to store and retrieve data (artifacts) during recipe execution, along with a separate space for configuration values.

## Core Requirements

- Maintain a store for **artifacts** (dynamic data produced and consumed by steps) and a separate store for **configuration** (static or initial settings).
- Support dictionary-like operations for artifacts:
  - Setting values by key (e.g., `context["x"] = value`).
  - Retrieving values by key (e.g., `value = context["x"]` or `context.get("x")`).
  - Checking for keys (`"x" in context`).
  - Iterating over keys (for example, `for k in context: ...`).
- Ensure that modifying the context in one step affects subsequent steps (shared mutability), while also allowing safe copying when needed.
- Provide a `clone()` method to create a deep copy of the entire context (both artifacts and configuration) for use cases like parallel execution where isolation is required.
- Remain lightweight and straightforward, following minimalist design principles (it should essentially behave like a `dict` with a config attached, without extra complexity).
- Provide a `dict()` and `json()` method to return a deep copy of the artifacts as a standard Python dictionary and a JSON string, respectively. This is useful for serialization or logging purposes.

## Implementation Considerations

- Use a Python dictionary internally to store artifacts. The keys are strings and values can be of any type (no restriction on artifact data types).
- Store configuration in a separate, internal dictionary (`_config` attribute) to distinguish it from runtime artifacts. Configuration might be populated at context creation and typically remains constant, but it's not enforced as immutable by the class.
- On initialization (`__init__`), deep copy any provided artifacts or config dictionaries. This prevents unintentional side effects if the caller modifies the dictionaries after passing them in.
- Implement the magic methods `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, and `__len__` to mimic standard dict behavior for artifacts. Also provide a `keys()` method for convenience.
- The `get` method should allow a default value, similar to `dict.get`, to avoid raising exceptions on missing keys.
- When iterating (`__iter__` or using `keys()`), return a static list or iterator that won’t be affected by concurrent modifications (for example, by copying the key list).
- The `clone()` method should deep copy both artifacts and configuration to produce a completely independent Context. This is important for features like running sub-recipes in parallel or reusing a context as a template.
- Raise a `KeyError` with a clear message in `__getitem__` if a key is not found, to help with debugging missing artifact issues.
- Do not implement any locking or thread-safety measures; the context is intended for sequential use within the executor (concurrent modifications are handled by using `clone` for parallelism instead).
- The Context class should implement the `ContextProtocol` interface defined in the Protocols component. That means any changes to the interface (methods or behavior) should be reflected in both the class and the protocol definition. In practice, the Context class already provides all methods required by `ContextProtocol`.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- **Protocols** - (Required) The Context component conforms to the `ContextProtocol` interface, which is defined in the Protocols component. This ensures other components interact with Context through a well-defined contract.

### External Libraries

- **copy** (Python stdlib) - (Required) Uses `copy.deepcopy` for cloning internal state safely.
- **typing** - (Required) Used for type hints (e.g., `Dict[str, Any]`, `Iterator[str]`) to clarify usage.

### Configuration Dependencies

- **None.** The Context component does not rely on external configuration. It is typically configured via its constructor arguments (artifacts and config dicts) provided at runtime by Main or a calling component.

## Error Handling

- Attempts to access a missing artifact key via `context["missing_key"]` result in a `KeyError`. The error message explicitly names the missing key for clarity (e.g., `"Key 'foo' not found in Context."`).
- The `get` method returns a default (or `None` if not provided) instead of raising an error for missing keys, offering a safe way to query the context.
- Setting a key (`context["x"] = value`) has no special error cases; it will overwrite existing values if the key already exists.
- Cloning always succeeds barring extreme cases (like objects in the context that are not copyable); such cases would raise exceptions from `copy.deepcopy` which propagate up (this is acceptable, as it would be a misusage of context content types).

## Output Files

- `recipe_executor/context.py`

## Future Considerations

- **Namespacing or Hierarchies**: In larger workflows, there might be a need to namespace context data (e.g., per step or per sub-recipe) to avoid key collisions. Future versions might introduce optional namespacing schemes or structured keys.
- **Immutable Context Option**: Possibly provide a mode or subclass for an immutable context (read-only once created) for scenarios where you want to ensure no step modifies the data.


=== File: blueprints/recipe_executor/components/executor/executor_docs.md ===
# Executor Component Usage

## Importing

```python
from recipe_executor.executor import Executor
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
```

_(Import the concrete `Executor` to create an instance, and import `ExecutorProtocol`/`ContextProtocol` if you want to use interfaces in type hints.)_

## Basic Usage

The Executor has a single primary method: `execute()`. This async method loads and runs a recipe with a given context. Typically, you will create a `Context` (for artifacts) and an `Executor`, then call and await `execute` with the recipe you want to run.

```python
from recipe_executor import Context

# Create context and executor (with protocol typing for clarity)
context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor(logger)

# Execute a recipe from a JSON file path
await executor.execute("path/to/recipe.json", context)

# Execute a recipe from a JSON string
json_string = '{"steps": [{"type": "read_files", "path": "example.txt", "content_key": "file_content"}]}'
await executor.execute(json_string, context)

# Execute a recipe from a JSON object (dict)
import json
recipe_dict = json.loads(json_string)
await executor.execute(recipe_dict, context)

# Execute a recipe from a Path object (if using pathlib)
from pathlib import Path
recipe_path = Path("path/to/recipe.json")
await executor.execute(recipe_path, context)

# Execute a recipe from a pre-defined dictionary
recipe_dict = {
    "steps": [
        {
            "type": "llm_generate",
            "prompt": "Write a poem about the sea",
            "model": "openai/gpt-4o",
            "output_format": "files",
            "output_key": "poem"
        }
    ]
}
await executor.execute(recipe_dict, context)
```

In each case, the Executor will parse the input (if needed) and sequentially execute each step in the recipe using the same `context`. After execution, the `context` may contain new artifacts produced by the steps (for example, in the above cases, the `file_content` and `poem` artifacts would be available in the context).

## Behavior Details

- The context passed into `execute` is mutated in-place by the steps. You should create a fresh Context (or clone an existing one) if you plan to reuse it for multiple recipe executions to avoid cross-contamination of data.
- If the recipe path is invalid or the JSON is malformed, `execute` will raise an error (ValueError or TypeError). Ensure you handle exceptions when calling `execute` if there's a possibility of bad input.
- The Executor uses the step registry to find the implementation for each step type. All default steps (like `"read_files"`, `"write_files"`, `"execute_recipe"`, etc.) are registered when you import the `recipe_executor.steps` modules. Custom steps need to be registered in the registry before Executor can use them.

## Important Notes

- **Interface Compliance**: The `Executor` class implements the `ExecutorProtocol` interface. Its `execute` method is designed to accept any object implementing `ContextProtocol`. In practice, you will pass a `Context` instance (which fulfills that protocol). This means the Executor is flexible — if the context were some subclass or alternative implementation, Executor would still work as long as it follows the interface.
- **One Executor, One Execution**: An `Executor` instance can be reused to run multiple recipes (simply call `execute` again with a different recipe and context), but it does not retain any state between runs. You can also create a new `Executor` for each execution. Both approaches are acceptable; there's typically little overhead in creating a new Executor.
- **Step Instantiation**: When the Executor runs a step, it creates a new instance of the step class for each step execution (even if the same step type appears multiple times, each occurrence is a fresh instance). The step class’s `__init__` usually takes the step configuration (from the recipe) and an optional logger.
- **Error Handling**: If any step fails (raises an exception), Executor will halt the execution of the remaining steps. The exception will bubble up as a `ValueError` with context about which step failed. You should be prepared to catch exceptions around `await executor.execute(...)` in contexts where a failure is possible or should not crash the entire program.
- **Context After Execution**: After `execute` completes (successfully), the context contains all the artifacts that steps have placed into it. You can inspect `context` to get results (for example, if a step writes an output, it might be found in `context["output_key"]`). The context is your way to retrieve outcomes from the recipe.


=== File: blueprints/recipe_executor/components/executor/executor_spec.md ===
# Executor Component Specification

## Purpose

The Executor component is responsible for executing recipes defined in JSON format. It loads the recipe, validates its structure, and sequentially executes each step using a shared context object. The Executor is designed to be stateless, meaning it does not maintain any internal state between executions. It also handles logging and error propagation to ensure that any issues encountered during execution are reported clearly.

## Core Requirements

- Accept recipe definitions in multiple formats:
  - File path to a JSON recipe file on disk.
  - Raw JSON string containing the recipe.
  - A Python dictionary already representing the recipe.
- Parse or load the recipe into the `Recipe` type.
- Validate the recipe structure.
- Iterate through the list of steps and execute them sequentially:
  - For each step, retrieve the step class from the Step Registry using the step's `"type"`.
  - Instantiate the step with its configuration.
  - Call and await the step's `execute(context)` method, passing in the shared context object.
- Handle errors gracefully:
  - If a step raises an exception, stop execution and wrap the exception in a clear message indicating which step failed.
  - Propagate errors up to the caller (Main or a supervising component) with context so that it can be logged or handled.
- Remain stateless aside from the execution flow; the Executor should not hold state between runs (each call to `execute` is independent).

## Implementation Considerations

- **Recipe Loading**:
  - If the recipe is a string, check if it is a file path (using `os.path.isfile()`). If so, read the file content and parse it as JSON. If not, treat it as a raw JSON string.
  - If the recipe is a dictionary, use it directly.
  - Use `json.loads()` to parse JSON strings into Python dictionaries.
  - If the recipe is a file path, use `json.load()` to read and parse the file content.
- **Format Validation**: Use `Recipe.model_validate(value)` or `Recipe.model_validate_json(value)` to validate the loaded recipe against the `Recipe` model. This ensures that the recipe adheres to the expected structure and types.
- **Step Execution**: Retrieve step implementations via `STEP_REGISTRY` (a global registry mapping step type names to their classes).
- **Context Interface**: Use the `ContextProtocol` interface for the `context` parameter to prevent coupling to a specific context implementation.
- **Protocols Compliance**: Document that Executor implements the `ExecutorProtocol`. The async `execute` method signature should match exactly what `ExecutorProtocol` defines.
- **Sequential Execution**: Execute each defined step in the order they appear in the recipe. The context object is passed to each step's `execute` method, allowing steps to read from and write to the context.
- **Error Propagation**: Wrap exceptions from steps in a `ValueError` with a message indicating the step index and type that failed, then raise it.

## Component Dependencies

### Internal Components

- **Protocols**: Uses the `ContextProtocol` definition for interacting with the context, and in concept provides the implementation for the `ExecutorProtocol`.
- **Models**: Uses the `Recipe` and `RecipeStep` models to represent the loaded recipe.
- **Step Registry**: Uses `STEP_REGISTRY` to look up and instantiate step classes by their type names.
  - _Note_: The dependency on specific step classes is indirect via the registry, preventing the Executor from needing to import each step module.
- **Logger**: The Executor will use the logger passed in by the caller

### External Libraries

- **json** - (Required) Used to parse JSON strings and files into Python dictionaries.
- **os** - (Required) Used to check file path existence and determine if a string is a file path.
- **logging** - (Required) Uses Python's logging library to report on execution progress and issues.
- **typing** - (Required) Utilizes typing for type hints (e.g., `Union[str, Dict]` for recipe input, and `ContextProtocol` for context type).

### Configuration Dependencies

- None

## Logging

- Debug:
  - Log when a recipe is loaded (including whether it came from a dict, file, or JSON string).
  - Log the entire recipe content (or a summary) and the number of steps at the start of execution.
  - Log before executing each step (index and type, plus step details for traceability).
  - Log after a step executes successfully.
  - Log a message when all steps complete.
- Info:
  - The Executor itself does not log at info level by default. (High-level info logging, like start and end of execution, is usually handled by Main or the logger setup.)
- Warning/Error:
  - If a step type is not found in the registry, log or include a message about the unknown step type (this triggers a ValueError as well).
  - No direct error logging inside Executor (it raises exceptions up, and the caller (Main) will log the error).

## Error Handling

- **Unsupported Recipe Type**: If the `recipe` argument is neither `dict` nor `str`, a `TypeError` is raised immediately.
- **File Read Errors**: If a file path is provided but reading or JSON parsing fails, a `ValueError` is raised with details (e.g., file not found or JSON decode error).
- **Invalid Recipe Structure**: If after loading, the structure isn't a dict or missing a proper steps list, a `ValueError` is raised explaining the expectation.
- **Unknown Step Type**: If a step's `"type"` is not in `STEP_REGISTRY`, raise `ValueError` indicating an unknown step type at that index.
- **Step Execution Error**: If `step_instance.execute(context)` raises an Exception, catch it. Raise a new `ValueError` that wraps the original exception, with a message specifying which step index and type failed.
- Stop execution upon the first error encountered (fail-fast behavior).

## Output Files

- `recipe_executor/executor.py`


=== File: blueprints/recipe_executor/components/llm_utils/azure_openai/azure_openai_docs.md ===
# Azure OpenAI Component Usage

## Importing

```python
from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
```

## Basic Usage

```python
def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str],
    context: ContextProtocol,
) -> pydantic_ai.models.openai.OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from context configuration for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o4-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.
        context (ContextProtocol): Context containing configuration values.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
# Get an OpenAI model using Azure OpenAI
openai_model = get_azure_openai_model(
    logger=logger,
    model_name="gpt-4o",
    deployment_name=None,
    context=context
)
```

# Get an OpenAI model using Azure OpenAI with a specific deployment name

```python
openai_model = get_azure_openai_model(
    logger=logger,
    model_name="o4-mini",
    deployment_name="my_deployment_name",
    context=context
)
```

## Configuration

The component accesses configuration through context.get_config(). The configuration values are typically loaded from environment variables by the Config component.

### Required Environment Variables

Depending on your authentication method:

#### Option 1: API Key Authentication
- `AZURE_OPENAI_API_KEY` - API key for Azure OpenAI
- `AZURE_OPENAI_BASE_URL` - Base URL for Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION` - (Optional) API version, defaults to "2025-03-01-preview"
- `AZURE_OPENAI_DEPLOYMENT_NAME` - (Optional) Deployment name, defaults to model_name

#### Option 2: Managed Identity
- `AZURE_USE_MANAGED_IDENTITY=true` - Enable managed identity authentication
- `AZURE_OPENAI_BASE_URL` - Base URL for Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION` - (Optional) API version, defaults to "2025-03-01-preview"
- `AZURE_OPENAI_DEPLOYMENT_NAME` - (Optional) Deployment name, defaults to model_name
- `AZURE_CLIENT_ID` - (Optional) Specific managed identity client ID


=== File: blueprints/recipe_executor/components/llm_utils/azure_openai/azure_openai_spec.md ===
# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from context configuration instead of environment variables
- The function `get_azure_openai_model` should accept a `context: ContextProtocol` parameter
- Access configuration dictionary through `context.get_config()` method, returning a dictionary with all configuration values
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Create the async client using `openai.AsyncAzureOpenAI` with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
def get_azure_openai_model(model_name: str, deployment_name: Optional[str], context: ContextProtocol) -> OpenAIModel:
    # Get configuration from context
    api_key = context.get_config().get('azure_openai_api_key')
    base_url = context.get_config().get('azure_openai_base_url')
    api_version = context.get_config().get('azure_openai_api_version', '2025-03-01-preview')
    use_managed_identity = context.get_config().get('azure_use_managed_identity', False)

    # Use deployment name from config or parameter or default to model name
    deployment = deployment_name or context.get_config().get('azure_openai_deployment_name', model_name)

    # Option 1: Create AsyncAzureOpenAI client with API key
    if not use_managed_identity and api_key:
        azure_client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=api_version,
            azure_deployment=deployment,
        )

    # Option 2: Create AsyncAzureOpenAI client with Azure Identity
    else:
        client_id = context.get_config().get('azure_client_id')
        # Create token provider using Azure Identity
        azure_client = AsyncAzureOpenAI(
            azure_ad_token_provider=token_provider,
            azure_endpoint=base_url,
            api_version=api_version,
            azure_deployment=deployment,
        )

    # Use the client to create the OpenAIProvider
    openai_model = OpenAIModel(
        model_name,
        provider=OpenAIProvider(openai_client=azure_client),
    )
    return openai_model
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIModel` and `OpenAIProvider` for model management
- **openai**: Uses `AsyncAzureOpenAI` client for API communication
- **azure-identity**: Uses `DefaultAzureCredential`, `ManagedIdentityCredential`, and `get_bearer_token_provider` for token provision

### Configuration Dependencies

All configuration is accessed through context.get_config():

- **azure_use_managed_identity**: (Optional) Boolean flag to use Azure Identity for authentication
- **azure_openai_api_key**: (Required for API key auth) API key for Azure OpenAI authentication
- **azure_openai_base_url**: (Required) Endpoint URL for Azure OpenAI service
- **azure_openai_deployment_name**: (Optional) Deployment name in Azure OpenAI (defaults to model name)
- **azure_openai_api_version**: (Optional) API version to use with Azure OpenAI, defaults to "2025-03-01-preview"
- **azure_client_id**: (Optional) Client ID for managed identity authentication

## Error Handling

- Debug: Log detailed error messages for failed authentication or model creation
- Info: Log successful authentication and model creation

## Output Files

- `recipe_executor/llm_utils/azure_openai.py`


=== File: blueprints/recipe_executor/components/llm_utils/azure_responses/azure_responses_docs.md ===
# Azure Responses Component Documentation

The Azure Responses component provides Azure OpenAI built-in tool integration for Recipe Executor.

## Overview

This component handles Azure OpenAI's Responses API built-in tools (web search, code execution)
by creating configured `OpenAIResponsesModel` instances with Azure authentication and appropriate tool settings.

## Importing

```python
from recipe_executor.llm_utils.azure_responses import get_azure_responses_model
```

### Basic Usage

```python
def get_azure_responses_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None
) -> pydantic_ai.models.openai.OpenAIResponsesModel:
    """
    Create an OpenAIResponsesModel for the given model name.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name: Name of the model (e.g., "gpt-4o").
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.

    Returns:
        OpenAIResponsesModel: A PydanticAI OpenAIResponsesModel instance .

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python

# Create basic Azure responses model
model = get_azure_responses_model("gpt-4o")

# Use with PydanticAI Agent
from pydantic_ai import Agent
agent = Agent(model=model)
result = await agent.run("Hello, what can you do with the Azure Responses API?")
```

## Environment Variables

The component uses environment variables for authentication and configuration. Depending upon the authentication method, set the following environment variables:

### Option 1: Managed Identity with Default Managed Identity

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 2: Managed Identity with Custom Client ID

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_CLIENT_ID= # Required
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 3: API Key Authentication

```bash
AZURE_OPENAI_API_KEY= # Required
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

## Error Handling

- Handle model initialization errors gracefully with clear error messages

## Dependency Integration Considerations

None


=== File: blueprints/recipe_executor/components/llm_utils/azure_responses/azure_responses_spec.md ===
# Azure Responses Component Specification

## Purpose

The Azure Responses component provides a PydanticAI wrapper for Azure OpenAI Responses API models for use with PydanticAI Agents. It handles model initialization, authentication, and built-in tools configuration.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIResponsesModel instance for Azure OpenAI
- Use proper Azure OpenAI authentication (API key or Azure Identity)
- Support Azure OpenAI endpoints and deployments
- Implement basic error handling and parameter validation
- Export `get_azure_responses_model` function
- Follow same patterns as existing `azure_openai` component

## Implementation Considerations

- Use `OpenAIResponsesModel` with `provider='azure'` parameter
- Create `AsyncAzureOpenAI` client following same patterns as `azure_openai` component
- Pass Azure client via `OpenAIProvider(openai_client=azure_client)`
- Support both API key and Azure Identity authentication
- Return a `pydantic_ai.models.openai.OpenAIResponsesModel` configured for Azure

## Implementation Hints

```python
# Use sync credentials for token provider (important for Azure AD)
if use_managed_identity:
    credential = DefaultAzureCredential()  # sync, not async
    token_provider = get_bearer_token_provider(credential, scope)
    azure_client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_OPENAI_BASE_URL,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_ad_token_provider=token_provider,
    )
else:
    azure_client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_OPENAI_BASE_URL,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,
    )

# Create Azure Responses model
model = OpenAIResponsesModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIResponsesModel` for model management
- **openai**: Uses `AsyncAzureOpenAI` client for API communication
- **azure-identity**: Uses `DefaultAzureCredential`, `ManagedIdentityCredential`, and `get_bearer_token_provider` for token provision

### Configuration Dependencies

- **AZURE_USE_MANAGED_IDENTITY**: (Optional) Boolean flag to use Azure Identity for authentication
- **AZURE_OPENAI_API_KEY**: (Required for API key auth) API key for Azure OpenAI authentication
- **AZURE_OPENAI_BASE_URL**: (Required) Endpoint URL for Azure OpenAI service
- **AZURE_OPENAI_DEPLOYMENT_NAME**: (Required) Deployment name in Azure OpenAI
- **AZURE_OPENAI_API_VERSION**: (Required) API version to use with Azure OpenAI, defaults to "2025-03-01-preview"
- **AZURE_CLIENT_ID**: (Optional) Client ID for managed identity authentication

## Error Handling

- Debug: Log detailed error messages for failed authentication or model creation
- Info: Log successful authentication and model creation

## Output Files

- `recipe_executor/llm_utils/azure_responses.py`

## Dependency Integration Considerations

None


=== File: blueprints/recipe_executor/components/llm_utils/llm/llm_docs.md ===
# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import create_mcp_server_config
```

## Basic Usage

The LLM component provides one main function:

```python
class LLM:
    def __init__(
            self,
            logger: logging.Logger,
            context: ContextProtocol,
            model: str = "openai/gpt-4o",
            max_tokens: Optional[int] = None,
            mcp_servers: Optional[List[MCPServer]] = None,
        ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            context (ContextProtocol): Context containing configuration values (API keys, endpoints).
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
            max_tokens (int): Maximum number of tokens for the LLM response.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
        """

    async def generate(
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                If not provided, the default set during initialization will be used.
            max_tokens (Optional[int]): Maximum number of tokens for the LLM response.
                If not provided, the default set during initialization will be used.
            output_type (Type[Union[str, BaseModel]]): The requested type for the LLM output.
                - str: Plain text output (default).
                - BaseModel: Structured output based on the provided JSON schema.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
                If not provided, the default set during initialization will be used.

        Returns:
            Union[str, BaseModel]: The output from the LLM, either as plain text or structured data.

        Raises:
            Exception: If any of the following occurs:
                - Invalid model ID or format.
                - Unsupported provider.
                - MCP server errors.
                - Network or API errors.
                - JSON schema validation errors.
        """
```

Usage example:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server

llm = LLM(logger=logger, context=context)
# With optional MCP integration:
weather_mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        },
    }
)
llm_mcp = LLM(logger=logger, context=context, mcp_servers=[weather_mcp_server])

# Call LLM with default model
result = await llm.generate("What is the weather in Redmond, WA today?")

# Call with specific model
result = await llm.generate(
    prompt="What is the capital of France?",
    model="openai/o4-mini"
)

# Call with JSON schema validation
class UserProfile(BaseModel):
    name: str
    age: int
    email: str

result = await llm.generate(
    prompt="Extract the user profile from the following text: {{text}}",
    model="openai/gpt-4o",
    max_tokens=100,
    output_type=UserProfile
)
```

## Model ID Format

The component uses a standardized model identifier format:

All models: `provider/model_name`
Example: `openai/o4-mini`

Azure OpenAI models with custom deployment name: `azure/model_name/deployment_name`
Example: `azure/gpt-4o/my_deployment_name`
If no deployment name is provided, the model name is used as the deployment name.

### Supported providers:

- **openai**: OpenAI models (e.g., `gpt-4o`, `gpt-4.1`, `o3`, `o4-mini`)
- **azure**: Azure OpenAI models (e.g., `gpt-4o`, `gpt-4.1`, `o3`, `o4-mini`)
- **azure**: Azure OpenAI models with custom deployment name (e.g., `gpt-4o/my_deployment_name`)
- **anthropic**: Anthropic models (e.g., `claude-3-5-sonnet-latest`)
- **ollama**: Ollama models (e.g., `phi4`, `llama3.2`, `qwen2.5-coder:14b`)

## Error Handling

Example of error handling:

```python
try:
    result = async llm.generate(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Important Notes

- The component logs full request details at debug level
- API keys are read from context configuration, not directly from environment


=== File: blueprints/recipe_executor/components/llm_utils/llm/llm_spec.md ===
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers and optional MCP servers. It handles model initialization, request formatting, and result processing, enabling the Recipe Executor to generate content and orchestrate external tools through a single API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Ollama, OpenAI Responses, Azure Responses)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI's async interface for non-blocking LLM calls
- Use PydanticAI for consistent handling and validation of LLM output
- Implement basic error handling
- Support optional structured output format
- Accept an optional `mcp_servers: Optional[List[MCPServer]]` to enable remote MCP tool integration

## Implementation Hints

- Use a clear `provider/model_name` identifier format
- Configuration values are accessed through context.get_config() instead of directly from environment
- For API key handling:
  - OpenAI: Create OpenAIProvider with api_key from context, pass to OpenAIModel
  - Anthropic: Create AnthropicProvider with api_key from context, pass to AnthropicModel
  - Azure: Handled by get_azure_openai_model function
  - Ollama: Create OpenAIProvider with base_url from context
- Use PydanticAI's provider-specific model classes:
  - pydantic_ai.models.openai.OpenAIModel (used also for Azure OpenAI and Ollama)
  - pydantic_ai.models.anthropic.AnthropicModel
- For `openai_responses` provider: call `get_openai_responses_model(model_name)` which returns the model directly
- For `azure_responses` provider: call `get_azure_responses_model(model_name, deployment_name)` which returns the model directly
- Create a PydanticAI Agent with the model, structured output type, and optional MCP servers
- Support: `output_type: Type[Union[str, BaseModel]] = str`
- Support: `openai_builtin_tools: Optional[List[Dict[str, Any]]] = None` parameter for built-in tools with Responses API models
  - We only want to support `WebSearchToolParam` and `FileSearchToolParam` at this
- Pass provided `mcp_servers` (or empty list) to the Agent constructor (e.g. `Agent(model, mcp_servers=mcp_servers, output_type=output_type)`)
- For Responses API models with built-in tools, configure the model with `OpenAIResponsesModelSettings` that includes properly typed tools
- Convert raw dict tools to PydanticAI tool parameter types (e.g., `WebSearchToolParam`, which are TypedDict) before passing to `OpenAIResponsesModelSettings`
- Import required tool parameter types from `pydantic_ai.models.openai` for type conversion
- Implement fully asynchronous execution with the following signature:
  ```python
  async def generate(
      self,
      prompt: str,
      model: Optional[str] = None,
      max_tokens: Optional[int] = None,
      output_type: Type[Union[str, BaseModel]] = str,
      mcp_servers: Optional[List[MCPServer]] = None,
      openai_builtin_tools: Optional[List[Dict[str, Any]]] = None,
  ) -> Union[str, BaseModel]:
  ```
  - Use `await agent.run(prompt)` method of the Agent to make requests
- CRITICAL: make sure to return the `result.output` in the `generate` method to return only the structured output

### PydanticAI Model Creation

Create a PydanticAI model for the LLM provider and model name:

```python
def get_model(model_id: str, context: ContextProtocol) -> OpenAIModel | AnthropicModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.

    Supported providers:
    - openai
    - azure (for Azure OpenAI, use 'azure/model_name/deployment_name' or 'azure/model_name')
    - anthropic
    - ollama
    - openai_responses (for OpenAI Responses API with built-in tools)
    - azure_responses (for Azure Responses API with built-in tools)

    Args:
        model_id (str): Model identifier in format 'provider/model_name'
            or 'provider/model_name/deployment_name'.
            If None, defaults to 'openai/gpt-4o'.
        context (ContextProtocol): Context containing configuration values.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """

    # If 'azure' is the model provider, use the `get_azure_openai_model` function
    # Access configuration dictionary through context.get_config() and then retrieve the necessary values
    # If 'openai_responses' is the model provider, use the `get_openai_responses_model` function from responses component
    # If 'azure_responses' is the model provider, use the `get_azure_responses_model` function from azure_responses component
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai/gpt-4o", context)
# Uses OpenAIModel('gpt-4o') with API key from context.get_config().get('openai_api_key')

# Get an Anthropic model
anthropic_model = get_model("anthropic/claude-3-5-sonnet-latest", context)
# Uses AnthropicModel('claude-3-5-sonnet-latest') with API key from context.get_config().get('anthropic_api_key')

# Get an Ollama model
ollama_model = get_model("ollama/phi4", context)
# Uses OllamaModel('phi4') with base URL from context.get_config().get('ollama_base_url')

# Get an OpenAI Responses model
responses_model = get_model("openai_responses/gpt-4o", context)
# Uses get_openai_responses_model('gpt-4o') from responses component

# Get an Azure Responses model
azure_responses_model = get_model("azure_responses/gpt-4o", context)
# Uses get_azure_responses_model('gpt-4o', None) from azure_responses component

# Get an Azure Responses model with deployment
azure_responses_model = get_model("azure_responses/gpt-4o/my-deployment", context)
# Uses get_azure_responses_model('gpt-4o', 'my-deployment') from azure_responses component
```

Getting an agent:

```python
from pydantic_ai import Agent

# Create an agent with the model
agent: Agent[None, Union[str, BaseModel]] = Agent(model=ollama_model, output_type=str, mcp_servers=mcp_servers)

# Call the agent with a prompt
async with agent.run_mcp_servers():
  result = await agent.run("What is the capital of France?")

# Process the result
print(result.data)  # This will print the structured output
```

### Ollama Integration

The Ollama model requires an endpoint to be specified:

```python
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers import OpenAIProvider

# inside the get_model function, context is passed as parameter
ollama_base_url = context.get_config().get('ollama_base_url', 'http://localhost:11434')

return OpenAIModel(
    model_name='qwen2.5-coder:7b',
    provider=OpenAIProvider(base_url=f'{ollama_base_url}/v1'),
)
```

## Logging

- Debug: Log full request payload before making call and then full result payload after receiving it, making sure to mask any sensitive information (e.g. API keys, secrets, etc.)
- Info: Log model name and provider before making call (do not include the request payload details) and then include processing times and tokens used upon completion (do not include the result payload details)

## Component Dependencies

### Internal Components

- **Azure OpenAI**: Uses `get_azure_openai_model` for Azure OpenAI model initialization
- **Responses**: Uses `get_openai_responses_model` for OpenAI Responses API model initialization
- **Azure Responses**: Uses `get_azure_responses_model` for Azure Responses API model initialization
- **Logger**: Uses the logger for logging LLM calls
- **MCP**: Integrates remote MCP tools when `mcp_servers` are provided (uses `pydantic_ai.mcp`)

### External Libraries

- **pydantic-ai**: Uses PydanticAI for model initialization, Agent-based request handling, and structured-output processing
- **pydantic-ai.mcp**: Provides `MCPServer`, `MCPServerHTTP` and `MCPServerStdio` classes for MCP server transports
- **openai.types.responses**: Provides types for the responses API `WebSearchToolParam`, `FileSearchToolParam`

### Configuration Dependencies

- **context.config** - All configuration is accessed through the context:
  - `openai_api_key`: (Required for OpenAI) API key for OpenAI access
  - `anthropic_api_key`: (Required for Anthropic) API key for Anthropic access
  - `ollama_base_url`: (Required for Ollama) Endpoint for Ollama models
  - `azure_*`: Azure OpenAI configuration values (handled by azure_openai component)

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `recipe_executor/llm_utils/llm.py`

## Dependency Integration Considerations

Implement a standardized `get_model` function that routes to appropriate provider-specific model creation functions based on the provider prefix in the model identifier. Use existing component functions for Azure OpenAI, Responses API, and Azure Responses API integration.


=== File: blueprints/recipe_executor/components/llm_utils/mcp/mcp_docs.md ===
# MCP Utility Usage

## Importing

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
```

## Basic Usage

You can create an MCP server client using the `get_mcp_server` function. This function takes a logger and a configuration object as arguments.

```python
def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any]
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.
    """
```

The configuration object should contain the necessary parameters for the MCP server. The function will create an instance of `MCPServer` based on the provided configuration.

For HTTP servers:

- `url`: str - the URL of the MCP server.
- `headers`: Optional[Dict[str, Any]] -headers to include in the request.

For stdio servers:

- `command`: str - the command to run the MCP server.
- `args`: List[str] - arguments to pass to the command.
- `env`: Optional[Dict[str, str]] - environment variables to set for the command.
  - If an env var is set to "", an attempt will be made to load the variable from the system environment variables and `.env` file.
- `working_dir`: The working directory for the command.

Use the provided `MCPServer` client to connect to an MCP server for external tool calls:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server

mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        }
    }
)

# List available tools
tools = await mcp_server.list_tools()
print([t.name for t in tools.tools])

# Call a specific tool
result = await mcp_server.call_tool("get_stock", {"item_id": 123})
print(result)
```

## Error Handling

Tools list and calls will raise exceptions on failures:

```python
try:
    result = await client.call_tool("bad_tool", {})
except RuntimeError as e:
    print(f"Tool call failed: {e}")
```

## Important Notes

- **MCPServer** does not maintain an active connection to the server. Each tool list/call creates a new connection.


=== File: blueprints/recipe_executor/components/llm_utils/mcp/mcp_spec.md ===
# MCP Utility Component Specification

## Purpose

The MCP utilities provide minimal, low‑level utilities for interacting with MCP servers.

## Core Requirements

- Provide a utilty method to create a PydanticAI `MCPServer` instance from a configuration object.

## Implementation Considerations

- For the `get_mcp_server` function:
  - Accept a logger and a configuration object.
  - Create an `MCPServer` instance based on the provided configuration, inferring the type of server (HTTP or stdio) from the configuration.
  - For Stdio servers:
    - Use `cwd` as the working directory in the server config.
    - If the `env` variable is set to `""`, attempt to load the variable from the system environment variables and `.env` file.
  - Only use the values that are necessary for the MCP server, ignore the rest.
  - Validate the configuration and raise `ValueError` if invalid.
  - Always return a PydanticAI `MCPServer` instance.

## Logging

- Debug: Log the configuration values (masking sensitive information such as keys, secrets, etc.).
- Info: For `get_mcp_server`, log the server type (HTTP or stdio) and relevant identifying information (e.g., URL, command/arg).

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic_ai.mcp**: Provides `MCPServer`, `MCPServerHTTP`, and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

None

## Error Handling

- Wrap low‑level exceptions in `RuntimeError` or `ValueError` with descriptive messages.

## Output Files

- `recipe_executor/llm_utils/mcp.py`


=== File: blueprints/recipe_executor/components/llm_utils/responses/responses_docs.md ===
# Responses Component Documentation

The Responses component provides OpenAI built-in tool integration for Recipe Executor.

## Overview

This component handles OpenAI's Responses API built-in tools (web search, code execution)
by creating configured `OpenAIResponsesModel` instances with appropriate tool settings.

## Importing

```python
from recipe_executor.llm_utils.responses import get_openai_responses_model
```

## Basic Usage

```python
def get_openai_responses_model(
    logger: logging.Logger,
    model_name: str,
) -> pydantic_ia.models.openai.OpenAIResponsesModel:
    """
    Create an OpenAIResponsesModel for the given model name.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name: Name of the model (e.g., "gpt-4o").

    Returns:
        OpenAIResponsesModel: A PydanticAI OpenAIResponsesModel instance .

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
model = get_openai_responses_model("gpt-4o")
# Use with PydanticAI Agent

from pydantic_ai import Agent
agent = Agent(model=model)
result = await agent.run("Hello, what can you do with the Responses API?")
```


=== File: blueprints/recipe_executor/components/llm_utils/responses/responses_spec.md ===
# Responses Component Specification

## Purpose

The Responses component provides OpenAI built-in tool integration using the PydanticAI Responses API.
It enables recipes to request OpenAI's built-in capabilities (web search, code execution)
via the `openai_responses` provider.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIResponsesModel instance
- Implement basic error handling

## Implementation Considerations

- For the `get_openai_responses_model` function:
  - Return the `OpenAIResponsesModel` instance directly

## Implementation Hints

None

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIResponsesModel`

### Configuration Dependencies

- **DEFAULT_MODEL**: (Optional) Environment variable specifying the default LLM model in format "provider/model_name"
- **OPENAI_API_KEY**: (Required for OpenAI) API key for OpenAI access

## Output Files

- `recipe_executor/llm_utils/responses.py`

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Dependency Integration Considerations

None


=== File: blueprints/recipe_executor/components/logger/logger_docs.md ===
# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize the logger. This function sets up the logging configuration, including log levels and file handlers.

```python
def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR".
            Note: This is not case-sensitive.
            If set to "DEBUG", all logs will be printed to stdout.
            If set to "INFO", only INFO and higher level logs will be printed to stdout.

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
```

Examples:

```python
# Default usage
logger = init_logger(log_dir="custom/log/path")

# Enable debug logging to stdout
logger = init_logger(log_dir="custom/log/path", stdio_log_level="DEBUG")

# Example usage
logger.info("This is an info message")
```

## Log Levels

The configured logger supports standard Python logging levels:

```python
# Debug level (to debug.log file and higher level logs)
logger.debug("Detailed information for diagnosing problems")

# Info level (to console, info.log, and error.log)
logger.info("Confirmation that things are working as expected")

# Warning level (to console, info.log, and error.log)
logger.warning("An indication that something unexpected happened")

# Error level (to console, info.log, and error.log)
logger.error("Due to a more serious problem, the software could not perform a function")

# Critical level (to all logs)
logger.critical("A serious error indicating the program itself may be unable to continue running")
```

## Log Files

The logger creates three log files:

1. `debug.log` - All messages (DEBUG and above)
2. `info.log` - INFO messages and above
3. `error.log` - ERROR messages and above

Example:

```
2025-03-30 15:42:38.927 [INFO] (main.py:25) Starting Recipe Executor Tool
2025-03-30 15:42:38.928 [DEBUG](executor.py:42) Initializing executor
2025-03-30 15:42:38.930 [INFO] (executor.py:156) Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38.935 [ERROR] (executor.py:256) Recipe execution failed: Invalid step type
```

## Important Notes

- Logs are cleared (overwritten) on each run
- Debug logs can get large with detailed information
- The log directory is created if it doesn't exist
- The logger is thread-safe and can be used in multi-threaded applications


=== File: blueprints/recipe_executor/components/logger/logger_spec.md ===
# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

- Writes to both stdout and log files
- Allow configuration of the log directory and log levels
- Support different log levels (DEBUG, INFO, ERROR)
- Create separate log files for each level
- For stdout, set the log level to INFO
- Clear existing logs on each run to prevent unbounded growth
- Provide a consistent log format with timestamps, log level, source file, line number, and message
- Create log directories if they don't exist

## Implementation Considerations

- Ensure thread safety for concurrent logging
- Use Python's standard logging module directly
- Reset existing handlers to ensure consistent configuration
- Set up separate handlers for console and different log files
- Create the log directory if it doesn't exist
- Use mode="w" for file handlers to clear previous logs
- Use a custom formatter:
  - Log Format: `%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s`
  - Log Date Format: `%Y-%m-%d %H:%M:%S`

## Logging

- Debug: Log that the logger is being initialized, the log directory being created, and any errors encountered during initialization
- Info: Log that the logger has been initialized successfully

## Component Dependencies

### Internal Components

None

### External Libraries

- **logging**: Uses Python's standard logging module for core functionality

### Configuration Dependencies

None

## Error Handling

- Catch and report directory creation failures
- Handle file access permission issues
- Provide clear error messages for logging setup failures

## Output Files

- `recipe_executor/logger.py`


=== File: blueprints/recipe_executor/components/main/main_docs.md ===
# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line. You invoke the `main` module with a recipe file and optional parameters. For example:

```bash
# Basic usage:
python -m recipe_executor.main recipes/my_recipe.json

# With a custom log directory:
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values:
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2

# With static configuration:
python -m recipe_executor.main recipes/my_recipe.json --config api_key=XYZ --config timeout=30
```

## Command-Line Arguments

The Main component supports these command-line arguments:

1. **`recipe_path`** (positional, required): Path to the recipe file to execute.
2. **`--log-dir`** (optional): Directory for log files (default: `"logs"`). If the directory does not exist, it will be created.
3. **`--context`** (optional, repeatable): Context artifact values as `key=value` pairs. You can specify this option multiple times.
4. **`--config`** (optional, repeatable): Static configuration values as `key=value` pairs, populated into context config. Useful for settings like MCP servers or API credentials.

## Context Parsing

If you provide context values via `--context`, the Main component will parse them into the execution context. For example:

```bash
# Given the arguments:
--context name=John --context age=30 --context active=true

# The resulting context artifacts will be:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

_(All values are parsed as strings. It's up to individual steps to interpret types as needed.)_

## Exit Codes

Main uses exit codes to indicate outcome:

- `0` — Successful execution.
- `1` — An error occurred (e.g., invalid arguments, failure during recipe execution).

These codes can be used in shell scripts to handle success or failure of the recipe execution.

## Error Messages

Error messages and exceptions are written to standard error and also logged:

```python
# Example of an error message for a context format issue:
sys.stderr.write("Context Error: Invalid context format 'foo'\n")

# Example of logging an execution error (in logs and stderr):
logger.error("An error occurred during recipe execution: ...")
```

The stack trace for exceptions is output to stderr (via `traceback.format_exc()`) to aid in debugging issues directly from the console.

## Configuration Loading

The Main component uses a hierarchical approach to configuration:

1. **Environment Variables**: Loaded from system environment and `.env` file
2. **Recipe-Specific Variables**: If the recipe declares `env_vars`, those are loaded
3. **CLI Overrides**: `--config` arguments override any environment-based configuration

Example flow:
```python
# 1. Load .env file
load_dotenv()

# 2. Load recipe
recipe = Recipe.model_validate_json(recipe_json)

# 3. Load configuration from environment
from recipe_executor.config import load_configuration
env_config = load_configuration(recipe.env_vars)

# 4. Parse CLI config arguments
cli_config = parse_config(args.config)

# 5. Merge configurations (CLI overrides environment)
merged_config = {**env_config, **cli_config}

# 6. Create context with merged configuration
context = Context(artifacts=artifacts, config=merged_config)
```

## Important Notes

- The main entry point is designed to be simple and minimal. It delegates the heavy lifting to the `Context` and `Executor` components.
- All steps in the executed recipe share the same context instance, which is created by Main from the provided context arguments and configuration.
- The Main component itself doesn't enforce any type of step ordering beyond what the recipe dictates; it simply invokes the Executor and waits for it to process the steps sequentially.
- Environment variables (for example, API keys for LLM steps) can be set in a `.env` file. Main will load this file at startup via `load_dotenv()`, making those values available through the Config component.
- Configuration values are accessible to steps through `context.get_config()` method, allowing centralized access to all configuration.
- Logging is configured at runtime when Main calls `init_logger`. The logs (including debug information and errors) are saved in the directory specified by `--log-dir`. Each run may append to these logs, so it's advisable to monitor or clean the log directory if running many recipes.


=== File: blueprints/recipe_executor/components/main/main_spec.md ===
# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, invokes the executor to run the specified recipe, and handles top-level error reporting (exit codes and exceptions).

## Core Requirements

- Provide a command-line interface for executing recipes (accept recipe path and optional parameters).
- Load environment variables from a `.env` file at startup (using python-dotenv).
- Parse context values supplied via command-line arguments (`--context key=value`) into initial Context artifacts.
- Parse configuration values supplied via command-line arguments (`--config key=value`) into the Context `config` attribute.
- Initialize a logging system and direct log output to a specified directory.
- Create the Context and Executor instances and orchestrate the recipe execution by running an asyncio event loop to call `await Executor.execute` with the provided context.
- Handle successful completion by reporting execution time, and handle errors by logging and exiting with a non-zero status.

## Implementation Considerations

- Use Python's built-in `argparse` for argument parsing.
- Support multiple `--context` arguments by accumulating them into a list and parsing into a dictionary of artifacts.
- Support multiple `--config` arguments by accumulating them into a list and parsing into a dictionary of configuration values.
- After loading the recipe, use the Config component to load environment-based configuration:
  - Call `load_configuration(recipe.env_vars)` to get environment variables including recipe-specific ones
  - Merge CLI config overrides with the environment configuration (CLI takes precedence)
- Create a `Context` object using the parsed artifacts and merged configuration dictionary (e.g., `Context(artifacts=artifacts, config=merged_config)`).
- Use the `Executor` component to run the recipe, passing the context object to it.
- Implement asynchronous execution:
  - Define an async `main_async` function that performs the core execution logic
  - In the `main` entry point, run this async function using `asyncio.run(main_async())`
  - This enables proper async/await usage throughout the execution pipeline
- Keep the main logic linear and straightforward: parse inputs, setup context and logger, run executor, handle errors. Avoid additional complexity or long-running logic in Main; delegate to Executor and other components.
- Ensure that any exception raised during execution is caught and results in a clean error message to `stderr` and an appropriate exit code (`1` for failure).
- Maintain minimal state in Main (it should primarily act as a procedural script). Do not retain references to context or executor after execution beyond what’s needed for logging.
- Follow the project philosophy of simplicity: avoid global state, singletons, or complex initialization in the Main component.

## Component Dependencies

### Internal Components

- **Config**: Uses the Config component to load environment-based configuration.
- **Context**: Creates the Context object to hold initial artifacts parsed from CLI and configuration from environment.
- **Executor**: Uses the Executor to run the specified recipe
- **Logger**: Uses the Logger component (via `init_logger`) to initialize logging for the execution.

### External Libraries

- **python-dotenv**: Loads environment variables from a file at startup.
- **argparse**: Parses command-line arguments.
- **asyncio**: Manages the event loop for asynchronous execution.

### Configuration Dependencies

- **Environment File** - The presence of a `.env` file is optional; if present, it's loaded for environment configuration (like API keys for steps, etc., though Main itself mainly cares about logging configuration if any).
- **Logging Directory** - Uses the `--log-dir` argument (default "logs") to determine where log files are written.

## Logging

- Debug: Log the start of execution, the parsed arguments, and the initial context artifact dictionary for traceability.
- Info: Log high-level events such as "Starting Recipe Executor Tool", the recipe being executed, and a success message with execution time.

## Error Handling

- Incorrect context argument format (missing `=`) results in a `ValueError` from `parse_context`; Main catches this and outputs a clear error message to `stderr` before exiting with code 1.
- Failures in logger initialization (e.g., invalid log directory permissions) are caught and cause the program to exit with an error message.
- Any exception during Executor execution is caught in Main; it logs the error and ensures the program exits with a non-zero status.
- Main distinguishes between normal execution termination and error termination by exit codes (0 for success, 1 for any failure case).
- After handling an error, Main uses `sys.exit(1)` to terminate the process, as no further steps should be taken.

## Output Files

- `recipe_executor/main.py`


=== File: blueprints/recipe_executor/components/models/models_docs.md ===
# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    RecipeStep,
    Recipe
)
```

## File Models

### FileSpec

Represents a single file:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict[str, Any]
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps: A list containing the steps of the recipe.
        env_vars: Optional list of environment variable names this recipe requires.
    """

    steps: List[RecipeStep]
    env_vars: Optional[List[str]] = None
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_files",
            config={"path": "specs/component_spec.md", "content_key": "spec"}
        ),
        RecipeStep(
            type="llm_generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "{{model|default:'openai/gpt-4o'}}",
                "output_format": "files",
                "output_key": "code_result"
            }
        ),
        RecipeStep(
            type="write_files",
            config={"files_key": "code_result", "root": "./output"}
        )
    ]
)

# Create a recipe that requires specific environment variables
recipe_with_env = Recipe(
    env_vars=["BRAVE_API_KEY", "CUSTOM_API_ENDPOINT"],
    steps=[
        RecipeStep(
            type="llm_generate",
            config={
                "prompt": "Search for: {{query}}",
                "model": "openai/gpt-4",
                "mcp_servers": [{
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                    "env": {
                        "BRAVE_API_KEY": "{{ brave_api_key }}"
                    }
                }]
            }
        )
    ]
)
```

## Instantiation from JSON

Models can be instantiated from JSON strings or dictionaries:

```python
# From JSON string
json_data = '{"path": "src/utils.py", "content": "def hello_world():\\n    print(\'Hello, world!\')"}'
file = FileSpec.model_validate_json(json_data)
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...

# From dictionary
dict_data = {
    "path": "src/utils.py",
    "content": "def hello_world():\n    print('Hello, world!')"
}
file = FileSpec.model_validate(dict_data)
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

- Models can be converted to dictionaries with `.model_dump()` method
- Models can be created from dictionaries with `Model.model_validate(dict_data)`
- Models can be converted to JSON with `.model_dump_json()` method
- Models can be created from JSON with `Model.model_validate_json(json_data)`


=== File: blueprints/recipe_executor/components/models/models_spec.md ===
# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, files, and recipe configuration.

## Core Requirements

- Define consistent data structures for files
- Provide configuration models for various step types
- Support recipe structure validation with optional environment variable declarations
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings

## Implementation Considerations

- Use Pydantic `BaseModel` for all data structures
- Ensure all models are serializable to JSON
- Use type hints for all fields
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering
- Support optional fields for forward compatibility


## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic**: Uses Pydantic for schema validation and model definition

### Configuration Dependencies

None

## Output Files

- `recipe_executor/models.py`


=== File: blueprints/recipe_executor/components/protocols/protocols_docs.md ===
# Protocols Component Usage

The Protocols component provides **interface definitions** for key parts of the Recipe Executor system. By defining formal contracts (`Protocol` classes) for the `Executor`, `Context`, and `Step`, this component decouples implementations from each other and serves as the single source of truth for how components interact. All components that implement or use these interfaces should refer to the `Protocols` component to ensure consistency. Where the concrete implementations are needed, consider importing them inside the method or class that requires them, rather than at the top of the file. This helps to prevent circular imports and keeps the code clean.

## Importing

```python
from recipe_executor.protocols import ContextProtocol, StepProtocol, ExecutorProtocol
```

## Provided Interfaces

### `ContextProtocol`

The `ContextProtocol` defines the interface for the context object used throughout the Recipe Executor system. It specifies methods for accessing, modifying, and managing context data. This includes standard dictionary-like operations (like `__getitem__`, `__setitem__`, etc.) as well as additional methods like `clone`, `dict`, and `json` for deep copying and serialization. In addition, it provides methods for managing configuration data, such as `get_config` and `set_config`.

```python
from typing import Protocol, Dict, Any, Iterator
class ContextProtocol(Protocol):
    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: str) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def clone(self) -> "ContextProtocol":
        ...

    def dict(self) -> Dict[str, Any]:
        ...

    def json(self) -> str:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get_config(self) -> Dict[str, Any]:
        ...

    def set_config(self, config: Dict[str, Any]) -> None:
        ...
```

### `StepProtocol`

The `StepProtocol` defines the interface for steps within a recipe. Each step must implement an `execute` method that takes a context (any `ContextProtocol` implementation) and performs its designated action. This allows for a consistent way to execute steps, regardless of their specific implementations.

```python
from typing import Protocol
class StepProtocol(Protocol):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        ...

    def execute(self, context: ContextProtocol) -> None:
        ...
```

### `ExecutorProtocol`

The `ExecutorProtocol` defines the interface for the executor component, which is responsible for executing recipes. It specifies an `execute` method that takes a recipe (which can be a string, path, or a Recipe object) and a context. This allows the executor to run recipes in a consistent manner, regardless of their specific implementations.

```python
from typing import Protocol
from recipe_executor.models import Recipe

class ExecutorProtocol(Protocol):
    def __init__(self, logger: logging.Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...
```

## How to Use These Protocols

Developers should **import the protocol interfaces** when writing type hints or designing new components. For example, to annotate variables or function parameters:

```python
from recipe_executor import Executor, Context
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol

context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor(logger)
executor.execute("path/to/recipe.json", context)
```

In this example, `Context` is the concrete implementation provided by the system (which implements `ContextProtocol`), and `Executor` is the concrete executor implementing `ExecutorProtocol`. By annotating them as `ContextProtocol` and `ExecutorProtocol`, we emphasize that our code relies only on the defined interface, not a specific implementation. This is optional for running the code (the system will work with or without the annotations), but it is useful for clarity and static type checking.

```python
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol

class MyCustomExecutor(ExecutorProtocol):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(self, recipe: str, context: ContextProtocol) -> None:
        # Custom implementation
        pass
```

In this example, `MyCustomExecutor` implements the `ExecutorProtocol`, ensuring it adheres to the expected interface. This allows it to be used interchangeably with any other executor that also implements `ExecutorProtocol`.

```python
from recipe_executor.protocols import ContextProtocol, StepProtocol
from recipe_executor.models import StepConfig

class MyCustomStep(StepProtocol):
    def __init__(self, logger: logging.Logger, config: StepConfig) -> None:
        self.logger = logger
        self.config = config

    def execute(self, context: ContextProtocol) -> None:
        # Custom implementation
        pass
```

In this example, `MyCustomStep` implements the `StepProtocol`, ensuring it adheres to the expected interface. This allows creation of custom steps that may be used as plugins or replacements for existing steps in the Recipe Executor system.

## Implementation Notes for Developers

- **For Implementers**: When creating a new Context or Executor implementation (or any new Step), ensure it provides all methods defined in the corresponding protocol. It is recommended to inherit from the protocol class to ensure compliance. This way, you can be sure that your implementation will work seamlessly with any code that relies on the protocol.

- **For Consumers**: If you use the protocols as the type hints in your code, you can be sure that your code will work with any implementation of the protocol. This allows for greater flexibility and easier testing, as you can swap out different implementations without changing the code that uses them.

- **Decoupling and Cycle Prevention**: By using these protocols, components like the Executor and steps do not need to import each other's concrete classes. This breaks import cycles (for example, steps can call executor functionality through `ExecutorProtocol` without a direct import of the Executor class). The Protocols component thus centralizes interface knowledge: it owns the definitions of `execute` methods and context operations that others rely on.

All developers and AI recipes should reference **this protocols documentation** when implementing or using components. This ensures that all components are consistent and adhere to the same interface definitions, enables decoupling, and prevents import cycles. It also allows for easier testing and swapping of implementations, as all components can be treated as interchangeable as long as they adhere to the defined protocols.


=== File: blueprints/recipe_executor/components/protocols/protocols_spec.md ===
# Protocols Component Specification

## Purpose

The Protocols component defines the core interfaces for the Recipe Executor system. It provides a set of protocols that standardize the interactions between components, ensuring loose coupling and clear contracts for behavior. This allows for flexible implementations and easy integration of new components without modifying existing code.

## Core Requirements

- Define a `ContextProtocol` that captures the required behaviors of the Context (dictionary-like access, retrieval, iteration, cloning).
- Define a `StepProtocol` that captures the execution interface for any step (the async `execute(context)` method signature).
- Define an `ExecutorProtocol` that captures the interface of the executor (the async `execute(recipe, context)` method signature).
- Support asynchronous execution throughout the system to enable non-blocking I/O operations.
- Ensure these protocols are the single source of truth for their respective contracts, referenced throughout the codebase for type annotations and documentation.
- Eliminate direct references to concrete classes (e.g., `Context` or `Executor`) in other components’ interfaces by using these protocol definitions, thereby avoiding circular dependencies.
- Follow the project's minimalist design philosophy: interfaces should be concise, containing only what is necessary for inter-component communication.

## Implementation Considerations

- Use Python's `typing.Protocol` to define interfaces in a structural subtyping manner. This allows classes to implement the protocols without explicit inheritance, maintaining loose coupling.
- Mark protocol interfaces with `@runtime_checkable` to allow runtime enforcement (e.g., in tests) if needed, without impacting normal execution.
- See the `protocols_docs.md` file for detailed documentation on each protocol, including method signatures, expected behaviors, and examples of usage. This file serves as the authoritative reference for developers implementing or using these protocols.
- No actual business logic or data storage should exist in `protocols.py`; it strictly contains interface definitions with `...` (ellipsis) as method bodies. This keeps it aligned with the "contracts only" role of the component.
- Ensure naming and signatures exactly match those used in concrete classes to avoid confusion. For example, `ContextProtocol.clone()` returns a `ContextProtocol` to allow flexibility in context implementations.
- Keep the protocols in a single file (`protocols.py`) at the root of the package (no sub-package), consistent with single-file component convention. This file becomes a lightweight dependency for any module that needs the interfaces.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- **Models**: The `Recipe` class is used in the `ExecutorProtocol` to define the type of the recipe parameter in the `execute` method.

### External Libraries

- **typing**: Uses Python's built-in `typing` module (particularly `Protocol` and related features) to define structural interfaces.

### Configuration Dependencies

- None

## Error Handling

- None

## Output Files

- `recipe_executor/protocols.py`


=== File: blueprints/recipe_executor/components/steps/base/base_docs.md ===
# Steps Base Component Usage

## Importing

To use the `BaseStep` and `StepConfig` classes in your custom step implementations, you will need to import them from the `recipe_executor.steps.base` module. Here’s how you can do that:

```python
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol, StepProtocol
```

## Defining a New Step (Example)

To illustrate how `BaseStep` is used, let's say you want to create a new step type called `"EchoStep"` that simply logs a message:

1. **Define the Configuration**: Subclass `StepConfig` to define any inputs the step needs. If none are required, you could even use `StepConfig` as is, but we'll define one for example:

   ```python
   class EchoConfig(StepConfig):
       message: str
   ```

   This uses Pydantic to require a `message` field for the step.

2. **Define the Step Class**: Subclass `BaseStep` with the config type and implement `execute`:

   ```python
   class EchoStep(BaseStep[EchoConfig]):
       def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
           super().__init__(logger, EchoConfig(**config))

       async def execute(self, context: ContextProtocol) -> None:
           # Simply log the message
           self.logger.info(f"Echo: {self.config.message}")
   ```

3. **Register the Step**: Finally, to use `EchoStep` in recipes, add it to the step registry:

   ```python
   from recipe_executor.steps.registry import STEP_REGISTRY
   STEP_REGISTRY["echo"] = EchoStep
   ```

Now, any recipe with a step like `{"type": "echo", "config": {"message": "Hello World"}}` will use `EchoStep`.

## Important Notes

- **Inheriting BaseStep**: All step implementations **must** inherit from `BaseStep` and implement the `execute` method.
- **Configuration Validation**: Using Pydantic `StepConfig` for your step’s configuration is highly recommended. It will automatically validate types and required fields. In the example above, if a recipe is missing the `"message"` field or if it's not a string, the creation of `EchoConfig` would raise an error, preventing execution with bad config.
- **Context Usage**: Steps interact with the execution context via the interface methods defined in `ContextProtocol`. For example, a step can do `value = context.get("some_key")` or `context["result"] = data`.
- **Logging**: Each step gets a logger (`self.logger`). Use it to log important events or data within the step.
- **BaseStep Utility**: Aside from providing the structure, `BaseStep` doesn't interfere with your step logic. You control what happens in `execute`. However, because `BaseStep` takes care of storing config and logger, you should always call its `__init__` in your step’s constructor (as shown with `super().__init__`). This ensures the config is properly parsed and the logger is set up.
- **Step Lifecycle**: There is no explicit "tear down" method for steps. If your step allocates resources (files, network connections, etc.), you should handle those within the step itself (and possibly in the `finally` block or context managers inside `execute`). Each step instance is short-lived (used only for one execution and then discarded).
- **Adhering to StepProtocol**: By following the pattern above, your custom step automatically adheres to `StepProtocol` because it implements `execute(context: ContextProtocol)`.


=== File: blueprints/recipe_executor/components/steps/base/base_spec.md ===
# Steps Base Component Specification

## Purpose

The purpose of the Steps Base component is to provide a foundational structure for creating and executing steps in the recipe executor. This component defines the base class for all steps, ensuring that they adhere to a consistent interface and can be easily integrated into the overall execution framework.

## Core Requirements

- Provide a base class (`BaseStep`) that all step classes will inherit from.
- Provide a base configuration model class (`StepConfig`) using Pydantic for validation of step-specific configuration.
- Enforce a consistent interface for step execution (each step must implement an async `execute(context)` method).
- Utilize generics to allow `BaseStep` to be typed with a specific `StepConfig` subclass for that step, enabling type-safe access to configuration attributes within step implementations.
- Integrate logging into steps, so each step has a logger to record its actions.
- Keep the base step minimal—only define structure and common functionality, deferring actual execution logic to subclasses.

## Implementation Considerations

- **StepConfig (Pydantic Model)**: Define a `StepConfig` class as a subclass of `BaseModel`. This serves as a base for all configurations. By default, it has no predefined fields (each step will define its own fields by extending this model). Using Pydantic ensures that step configurations are validated and parsed (e.g., types are enforced, missing fields are caught) when constructing the step.
- **Generic Config Type**: Use a `TypeVar` and generic class definition (`BaseStep[StepConfigType]`) so that each step class can specify what config type it expects. For instance, a `PrintStep` could be `BaseStep[PrintConfig]`. This allows the step implementation to access `self.config` with the correct type.
  - Example: `StepConfigType = TypeVar("StepConfigType", bound=StepConfig)`.
- **BaseStep Class**:
  - Inherit from `Generic[StepConfigType]` to support the generic config typing.
  - Provide an `__init__` that stores the `config` (of type StepConfigType) and a logger. This logger is used by steps to log their internal operations.
  - The `__init__` should log a debug message indicating the class name and config with which the step was initialized. This is useful for tracing execution in logs.
  - Declare a `async execute(context: ContextProtocol) -> None` method. This is the core contract: every step must implement this method as an async method.
  - `BaseStep` should not provide any implementation (aside from possibly a placeholder raise of NotImplementedError, which is a safeguard).
- **Logging in Steps**: Steps can use `self.logger` to log debug or info messages.
- **Step Interface Protocol**: The `BaseStep` (and by extension all steps) fulfill the `StepProtocol` as defined in the Protocols component.

## Logging

- Debug: BaseStep’s `__init__` logs a message when a step is initialized (including the provided configuration).

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for the type of the context parameter in `execute`. Also, by design, `BaseStep` and its subclasses implement `StepProtocol` as defined in the Protocols component.
- **Logger**: Uses the logger for logging messages. The logger is passed to the step during initialization.

### External Libraries

- **typing**: Uses `TypeVar` and `Generic` for typing the BaseStep with its config model.

### Configuration Dependencies

- None

## Error Handling

- BaseStep does not implement run-time error handling. It defines the interface and common setup. Any exceptions that occur within an actual step's `execute` method will propagate up unless handled inside that step.
- In the unlikely case that `BaseStep.execute` is called (e.g., via `super()` call from a subclass that doesn't override it), it will raise `NotImplementedError`, clearly indicating that the subclass should implement it. This is a safeguard and developmental aid.

## Output Files

- `recipe_executor/steps/base.py`


=== File: blueprints/recipe_executor/components/steps/conditional/conditional_docs.md ===
# Conditional Step Documentation

## Importing

```python
from recipe_executor.steps.conditional import ConditionalStep
```

## Configuration

The ConditionalStep is configured with a condition expression and step branches to execute based on the evaluation result:

```python
class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression string to evaluate against the context.
          - Will attempt to coerce to a boolean value.
        if_true: Optional steps to execute when the condition evaluates to true.
        if_false: Optional steps to execute when the condition evaluates to false.
    """
    condition: Any
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None
```

## Step Registration

The ConditionalStep is registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep

STEP_REGISTRY["conditional"] = ConditionalStep
```

## Basic Usage in Recipes

The ConditionalStep allows you to branch execution paths based on evaluating expressions:

```json
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "{{ analysis_result.needs_splitting }}",
        "if_true": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator/recipes/split_project.json"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator/recipes/process_single_component.json"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## Supported Expression Types

### Context Value Checks

```json
"condition": "{{key}} == 'value'"
"condition": "{{nested.key}} != null"
"condition": "{{count}} > 0"
"condition": "{{is_ready}}"
```

### File Operations

```json
"condition": "file_exists('{{output_dir}}/specs/initial_project_spec.md')"
"condition": "all_files_exist(['file1.md', 'file2.md'])"
"condition": "file_is_newer('source.txt', 'output.txt')"
```

### Logical Operations

```json
"condition": "and({{a}}, {{b}})"
"condition": "or(file_exists('file1.md'), file_exists('file2.md'))"
"condition": "not({{skip_processing}})"
```

### Template Variables in Expressions

```json
"condition": "file_exists('{{output_dir}}/components/{{component_id}}_spec.md')"
```

## Common Use Cases

### Conditional Recipe Execution

```json
{
  "type": "conditional",
  "config": {
    "condition": "{{ step_complete }}",
    "if_true": {
      "steps": [
        {
          "type": "execute_recipe",
          "config": {
            "recipe_path": "recipes/next_step.json"
          }
        }
      ]
    }
  }
}
```

### File Existence Checking

```json
{
  "type": "conditional",
  "config": {
    "condition": "file_exists('{{ output_path }}')",
    "if_true": {
      "steps": [
        /* Steps to handle existing file */
      ]
    },
    "if_false": {
      "steps": [
        /* Steps to generate the file */
      ]
    }
  }
}
```

### Complex Condition

```json
{
  "type": "conditional",
  "config": {
    "condition": "and({{ should_process }}, or(file_exists('input1.md'), file_exists('input2.md')))",
    "if_true": {
      "steps": [
        /* Processing steps */
      ]
    }
  }
}
```

## Utility Recipe Example

```json
// check_and_process.json
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "all_files_exist(['{{ input_file }}', '{{ config_file }}'])",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ input_file }}",
                "content_key": "input_content"
              }
            }
            /* More processing steps */
          ]
        },
        "if_false": {
          "steps": [
            /* Steps to handle missing files */
          ]
        }
      }
    }
  ]
}
```

## Important Notes

- Expressions are evaluated in the context of the current recipe execution
- Template variables in the condition string are rendered before evaluation
- Both `if_true` and `if_false` branches are optional and can be omitted for simple checks
- When a branch doesn't exist for the condition result, that path is simply skipped
- Nested conditional steps are supported for complex decision trees
- The conditional step is specifically designed to reduce unnecessary LLM calls in recipes


=== File: blueprints/recipe_executor/components/steps/conditional/conditional_spec.md ===
# Conditional Step Type Specification

## Purpose

The Conditional step enables branching execution paths in recipes based on evaluating expressions. It serves as a key building block for creating utility recipes or non-LLM flow control.

## Core Requirements

- Evaluate conditional expressions against the current context state
  - Attempt to coerce the expression to a boolean value
- Support multiple condition types including:
  - Context value checks
  - File existence checks
  - Comparison operations
- Execute different sets of steps based on the result of the condition evaluation
- Support nested conditions and complex logical operations
- Provide clear error messages when expressions are invalid

## Implementation Considerations

- If expression is already a boolean or a string that can be evaluated to a boolean, use it directly as it may have been rendered by the template engine
- Do not send non-string values to the template engine
- Include conversion of "true" and "false" strings to boolean values in any safe globals list
- Keep expression evaluation lightweight and focused on common needs
- Allow for direct access to context values via expression syntax
- Make error messages helpful for debugging invalid expressions
- Process nested step configurations in a recursive manner
- Ensure consistent logging of condition results and execution paths
- Properly handle function-like logical operations that conflict with Python keywords

## Logging

- Debug: Log the condition being evaluated, its result, and which branch is taken
- Info: None

## Component Dependencies

### Internal Components

- **Context**: Uses context to access values for condition evaluation
- **Utils/Templates**: Uses template rendering for condition strings with variables

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Provide clear error messages for invalid expressions
- Handle missing context values gracefully (typically evaluating to false)
- Properly propagate errors from executed step branches

## Output Files

- `recipe_executor/steps/conditional.py`


=== File: blueprints/recipe_executor/components/steps/execute_recipe/execute_recipe_docs.md ===
# ExecuteRecipeStep Component Usage

## Importing

```python
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep, ExecuteRecipeConfig
```

## Configuration

The ExecuteRecipeStep is configured with an ExecuteRecipeConfig:

```python
class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, Any] = {}
```

## Step Registration

The ExecuteRecipeStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep

STEP_REGISTRY["execute_recipe"] = ExecuteRecipeStep
```

## Basic Usage in Recipes

The ExecuteRecipeStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/sub_recipe.json"
      }
    }
  ]
}
```

## Context Overrides

You can override specific context values for the sub-recipe execution:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/generate_component.json",
        "context_overrides": {
          "component_name": "Utils",
          "is_component": true,
          "revision_count": 1,
          "refs": ["utils"],
          "output_dir": "output/components/utils"
        }
      }
    }
  ]
}
```

## Template-Based Values

Both the `recipe_path` and `context_overrides` can include template variables:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/{{ recipe_type }}/{{ component_id }}.json",
        "context_overrides": {
          "component_name": "{{ component_display_name }}",
          "sub_components": "{{ sub_components | json }}",
          "output_dir": "output/components/{{ component_id }}"
        }
      }
    }
  ]
}
```

**NOTE**: For any **templated** values in the `context_overrides`, you can use the Python Liquid templating engine to resolve them. For example, `{{ sub_components | json }}` will convert the `sub_components` list into a JSON string so that it can be passed to the sub-recipe. This is useful for passing complex data structures or lists. This is especially important for any lists of objects as the Python Liquid engine will only pass the first element of the list if you don't use the `json` filter.

## Recipe Composition

Sub-recipes can be composed to create more complex workflows:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/project_spec.md",
        "content_key": "project_spec"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/parse_project.json",
        "context_overrides": {
          "spec": "{{ project_spec }}"
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/generate_components.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/assemble_project.json"
      }
    }
  ]
}
```

## Common Use Cases

**Component Generation**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/generate_component.json",
    "context_overrides": {
      "component_id": "utils",
      "component_name": "Utils Component"
    }
  }
}
```

**Template-Based Recipes**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/component_template.json",
    "context_overrides": {
      "template_type": "create",
      "component_id": "{{ component_id }}"
    }
  }
}
```

**Multi-Step Workflows**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/workflow/{{ workflow_name }}.json"
  }
}
```

## Important Notes

- The sub-recipe receives the **same context object** as the parent recipe (the shared context implements ContextProtocol)
- Context overrides are applied **before** sub-recipe execution
- Changes made to the context by the sub-recipe persist after it completes
- Template variables in both `recipe_path` and `context_overrides` are resolved before execution
- Sub-recipes can execute their own sub-recipes (nested execution)


=== File: blueprints/recipe_executor/components/steps/execute_recipe/execute_recipe_spec.md ===
# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building-block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current execution context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow a minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- When processing context overrides
  - Process all **string** values (including those within lists or dictionaries) using the template engine
  - All non-string values in context overrides should be passed as-is
  - String value may contain JSON objects or lists of JSON objects with mixed, escaped quotes, use `ast.literal_eval` to parse them
  - If a string value is a valid JSON object, it should be parsed and passed as a dictionary
  - If a string value is a list of valid JSON objects, it should be parsed and passed as a list of dictionaries
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Implementation Hints

- Import the `Executor` within the `execute` method to avoid circular dependencies

## Logging

- Debug: None
- Info: Log the path of the sub-recipe being executed at both the start and end of execution

## Component Dependencies

### Internal Components

- **Protocols**: Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Interface**: Implements the step execution interface (via the StepProtocol)
- **Context**: Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor**: Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates**: Uses render_template for dynamic content resolution in paths and context overrides

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include the sub-recipe path in error messages for debugging

## Output Files

- `recipe_executor/steps/execute_recipe.py`


=== File: blueprints/recipe_executor/components/steps/llm_generate/llm_generate_docs.md ===
# LLMGenerateStep Component Usage

## Importing

```python
from recipe_executor.steps.llm_generate import LLMGenerateStep, LLMGenerateConfig
```

## Configuration

The LLMGenerateStep is configured with a LLMGenerateConfig:

```python
class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        max_tokens: The maximum number of tokens for the LLM response.
        mcp_servers: List of MCP servers for access to tools.
        output_format: The format of the LLM output (text, files, or JSON).
            - text: Plain text output.
            - files: List of files generated by the LLM.
            - object: Object based on the provided JSON schema.
            - list: List of items based on the provided JSON schema.
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    max_tokens: Optional[Union[str, int]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: "text" | "files" | Dict[str, Any]
    output_key: str = "llm_output"
```

## Basic Usage in Recipes

The LLMGenerateStep can be used in recipes via the `llm_generate` step type:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "What is the weather in Redmond, WA today?",
        "model": "openai/o4-mini",
        "mcp_servers": [
          {
            "url": "http://localhost:3001/sse"
          }
        ],
        "output_format": "text",
        "output_key": "capital_result"
      }
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md",
        "content_key": "component_spec_content"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Based on the following specification, generate python code for a component:\n\n{{component_spec_content}}",
        "model": "{{model|default:'openai/o4-mini'}}",
        "output_format": "files",
        "output_key": "component_code_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        # Prefer using "files_key" over "files" when using LLMGenerateStep with "files" output format
        "files_key": "component_code_files",
        "root": "./output"
      }
    }
  ]
}
```

## Dynamic Output Keys

The output key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a JSON object with user details.",
        "model": "{{model|default:'openai/o4-mini'}}",
        "output_format": {
          "type": "object",
          "properties": {
            "user": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                },
                "age": {
                  "type": "integer"
                }
              },
              "required": ["name", "age"]
            }
          }
        },
        "output_key": "user_details_{{name}}"
      }
    }
  ]
}
```

## MCP Integration

The LLMGenerateStep can integrate with MCP servers for tool access. The MCP servers can be specified in the `mcp_servers` field of the configuration. The LLM will use these servers to access tools during the generation process.

### MCP Server Configuration Formats

The MCP server configuration can be specified in two formats:

- **HTTP**: For HTTP-based MCP servers, provide:

  - `url`: The URL of the MCP server.
  - `headers`: Optional dictionary of headers to include in the requests.

Example:

```json
{
  "mcp_servers": [
    {
      "url": "http://localhost:3001/sse",
      "headers": {
        "Authorization": "{{token}}"
      }
    }
  ]
}
```

- **STDIO**: For STDIO-based MCP servers, provide:

  - `command`: The command to run the MCP server.
  - `args`: List of arguments for the command.
  - `env`: Optional dictionary of environment variables for the command.
  - `cwd`: Optional working directory for the command.

Example:

```json
{
  "mcp_servers": [
    {
      "command": "python",
      "args": ["-m", "/path/to/mcp_server.py"],
      "env": {
        "MCP_TOKEN": "{{token}}"
      },
      "cwd": "/path/to/mcp"
    }
  ]
}
```

## LLM Output Formats

The LLM can return different formats based on the `output_format` parameter:

- **"text"**: Returns a plain text output.
- **"files"**: Returns a list of `FileSpec` objects, this is provided as a convenience due to the common use case of generating files from LLMs.
- **object**: Returns a JSON object based on the provided JSON schema. The schema is validated before the LLM call, and if invalid, the step will fail.
- **list**: Returns a list of items based on the provided JSON schema. The schema is validated before the LLM call, and if invalid, the step will fail.

### Text Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "What is the capital of France?",
    "model": "openai/gpt-4o",
    "max_tokens": 100,
    "output_format": "text",
    "output_key": "capital_result"
  }
}
```

Context after execution:

```json
{
  "capital_result": "The capital of France is Paris."
}
```

### Files Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Generate Python files for a simple calculator.",
    "model": "openai/o4-mini",
    "output_format": "files",
    "output_key": "calculator_files"
  }
}
```

Context after execution:

```json
{
  "calculator_files": [
    {
      "path": "calculator.py",
      "content": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b"
    },
    {
      "path": "test_calculator.py",
      "content": "import calculator\n\ndef test_add():\n    assert calculator.add(1, 2) == 3\n\ndef test_subtract():\n    assert calculator.subtract(2, 1) == 1"
    }
  ]
}
```

### Object Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Generate a JSON object with user details.",
    "model": "openai/o4-mini",
    "output_format": {
      "type": "object",
      "properties": {
        "user": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "age": {
              "type": "integer"
            }
          },
          "required": ["name", "age"]
        }
      }
    },
    "output_key": "user_details"
  }
}
```

Context after execution:

```json
{
  "user_details": {
    "user": {
      "name": "Alice",
      "age": 30
    }
  }
}
```

### List Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Extract the list of users from this document: {{document_content}}.",
    "model": "openai/o4-mini",
    "output_format": [
      {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "age": {
            "type": "integer"
          }
        },
        "required": ["name", "age"]
      }
    ],
    "output_key": "user_details"
  }
}
```

Context after execution:

```json
{
  "user_details": [
    {
      "name": "Alice",
      "age": 30
    },
    {
      "name": "Bob",
      "age": 25
    }
  ]
}
```


=== File: blueprints/recipe_executor/components/steps/llm_generate/llm_generate_spec.md ===
# LLMGenerateStep Component Specification

## Purpose

The LLMGenerateStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, MCP server tools, structured output, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Support MCP server configuration for tool access
- Support OpenAI built-in tools (web search) for Responses API models via `openai_builtin_tools` config field
- Support multiple output formats (text, files, object, list)
- Call LLMs to generate content
- Store generated results in the context with dynamic key support
- Include appropriate logging for LLM operations
- Configuration fields: `prompt`, `model`, `max_tokens`, `mcp_servers`, `openai_builtin_tools`, `output_format`, `output_key`

## Implementation Considerations

- Use `render_template` for templating prompts, model identifiers, mcp server configs, and output key
- Convert any MCP Server configurations to `MCPServer` instances (via `get_mcp_server`) to pass as `mcp_servers` to the LLM component
- Accept a string for `max_tokens` and convert it to an integer to pass to the LLM component
- Support `openai_builtin_tools` parameter with validation:
  - Only allow for models with `openai_responses` or `azure_responses` providers
  - Support tool types: `web_search_preview` only
  - Validate tool configuration before making LLM calls
  - Pass built-in tools to the LLM component for Responses API configuration
- In order to support dyanmic output keys, set the result type to `Any` prior to determining the output format and then set the output key immediately after the LLM call
- If `output_format` is an object (JSON schema) or list:
  - Use `json_object_to_pydantic_model` to create a dynamic Pydantic model from the JSON schema
  - Pass the dynamic model to the LLM call as the `output_type` parameter
  - After receiving the results, convert the output to a Dict[str, Any] and store it in the context
- If `output_format` is a list:
  - Wrap the list in an object with a root key `items`:
    ```python
    object_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": // Define the item schema here
            }
        }
    }
    ```
  - Use `json_object_to_pydantic_model` to create a dynamic Pydantic model from the JSON schema
  - Pass the dynamic model to the LLM call as the `output_type` parameter
  - After receiving the results, convert the output to a Dict[str, Any] and store the `items` list in the context
- If `output_format` is "files":
  - Pass the following `FileSpecCollection` model to the LLM call:
    ```python
    class FileSpecCollection(BaseModel):
        files: List[FileSpec]
    ```
  - After receiving the results, store the `files` value (not the entire `FileSpecCollection`) in the context
- Instantiate the `LLM` component with optional MCP servers from context config:
  ```python
  mcp_server_configs = context.get_config().get("mcp_servers", [])
  mcp_servers = [get_mcp_server(logger=self.logger, config=mcp_server_config) for mcp_server_config in mcp_server_configs]
  llm = LLM(logger, model=config.model, mcp_servers=mcp_servers)
  ```
- Use `await llm.generate(prompt, output_type=..., openai_builtin_tools=validated_tools)` to perform the generation call
- Always pass `openai_builtin_tools` parameter to the LLM generate method (pass None if not provided)
- Example LLM call with built-in tools:
  ```python
  # Validate built-in tools if provided
  validated_tools = None
  if self.config.openai_builtin_tools:
      # Validation logic here
      validated_tools = self.config.openai_builtin_tools
  
  # Call LLM with tools parameter
  result = await llm.generate(
      prompt, 
      output_type=output_type,
      openai_builtin_tools=validated_tools
  )
  ```

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface**: Implements the step behavior via `StepProtocol`
- **Context**: Uses a context implementing `ContextProtocol` to retrieve input values and store generation output
- **Models**: Uses the `FileSpec` model for file generation output
- **LLM**: Uses the LLM component class `LLM` from `llm_utils.llm` to interact with language models and optional MCP servers
- **MCP**: Uses the `get_mcp_server` function to convert MCP server configurations to `MCPServer` instances
- **Utils/Models**: Uses `json_object_to_pydantic_model` to create dynamic Pydantic models from JSON objects, after receiving the results from the LLM use `.model_dump()` to convert the Pydantic model to a dictionary
- **Utils/Templates**: Uses `render_template` for dynamic content resolution in prompts and model identifiers

### External Libraries

- **Pydantic**: For BaseModel creation

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls
- Validate `openai_builtin_tools` parameter:
  - Raise error if tools are specified with non-Responses API models
  - Raise error for unsupported tool types (only `web_search_preview` allowed)
  - Example error messages:
    - "Built-in tools only supported with Responses API models (openai_responses/* or azure_responses/*)"
    - "Unsupported tool type: {type}. Supported: web_search_preview"

## Output Files

- `recipe_executor/steps/llm_generate.py`


=== File: blueprints/recipe_executor/components/steps/loop/loop_docs.md ===
# LoopStep Component Usage

The **LoopStep** component allows you to iterate over a collection of items and execute specified sub-steps for each item. It is useful for processing lists or arrays of data in a structured manner.

## Importing

Import the LoopStep and its configuration:

```python
from recipe_executor.steps.loop import LoopStep, LoopStepConfig
```

## Configuration

The LoopStep is configured via a `LoopStepConfig` object. This configuration defines the collection to iterate over, the key for the current item, the sub-steps to execute, and how to handle results.

```python
class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Either string that resolves to a collection in the context (e.g., "data.items") or a list/dict.
               If a string, it is rendered using template rendering to resolve nested paths.
               If a list/dict, it is used directly without rendering.
               If a dict, iterate over its keys.
        item_key: Key to use when storing the current item in each iteration's context.
        max_concurrency: Maximum number of items to process concurrently.
                         Default = 1 means process items sequentially (no parallelism).
                         n > 1 means process up to n items at a time.
                         0 means no explicit limit (all items may run at once, limited only by system resources).
        delay: Time in seconds to wait between starting each parallel task.
               Default = 0 means no delay (all allowed items start immediately).
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error.
    """

    items: Union[str, List, Dict]
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True
```

## Parallel Execution Support

The LoopStep supports parallel processing of items:

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 3,  // Process up to 3 items in parallel
    "delay": 0.2,          // Wait 0.2 seconds between starting each task
    "substeps": [...],
    "result_key": "processed_components"
  }
}
```

### Parallel Execution Parameters

- **max_concurrency**: Maximum number of items to process concurrently.

  - `0` (default): Process all items at once (limited only by system resources)
  - `1`: Process items sequentially (no parallelism)
  - `n > 1`: Process up to n items at a time

- **delay**: Time in seconds to wait between starting each parallel task.
  - `0.0` (default): Start all allowed tasks immediately
  - `n > 0`: Add n seconds delay between starting each task

### When to Use Parallel Execution

Parallel execution is most beneficial for loops where:

- Each item's processing is independent of other items
- Processing each item involves significant wait time (e.g., LLM calls, network requests)
- The number of items is large enough to benefit from parallelism

## Step Registration

To enable the use of LoopStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.loop import LoopStep

STEP_REGISTRY["loop"] = LoopStep
```

## Basic Usage in Recipes

The LoopStep allows you to run multiple steps for each item in a collection. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "components",
        "item_key": "component",
        "substeps": [
          {
            "type": "llm_generate",
            "config": {
              "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
              "model": "{{model}}",
              "output_format": "files",
              "output_key": "component_questions"
            }
          },
          {
            "type": "write_files",
            "config": {
              "root": "{{output_dir}}/components/{{component.id}}",
              "files_key": "component_questions"
            }
          }
        ],
        "result_key": "processed_components"
      }
    }
  ]
}
```

## How It Works

For each iteration:

1. The LoopStep renders the `items` path using template rendering to resolve nested paths (e.g., "data.items" becomes the actual array from context["data"]["items"])
2. The LoopStep clones the parent context to create an isolated execution environment
3. It places the current item in the cloned context using the `item_key`
4. It executes all specified steps using the cloned context
5. After execution, it extracts the result from the context (using the same `item_key`)
6. The result is added to a collection that will be stored in the parent context under `result_key`

## Accessing Nested Data

The `items` parameter can reference nested data in the context using dot notation. This is processed using template rendering, similar to other Recipe Executor components:

```json
{
  "type": "loop",
  "config": {
    "items": "data.users.list",
    "item_key": "user",
    "substeps": [...]
  }
}
```

This example would iterate over the array found at `context["data"]["users"]["list"]`.

## Template Variables

Within each iteration, you can reference:

- The current item using the specified `item_key` (e.g., `{{current_component}}`)
- Properties of the current item (e.g., `{{current_component.id}}`)
- The iteration index using `{{__index}}` (for arrays) or key using `{{__key}}` (for objects)
- Other context values from the parent context

## Common Usage Patterns

### Processing Collection of Objects

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "component_questions"
        }
      },
      {
        "type": "write_files",
        "config": {
          "root": "output/{{component.id}}",
          "files_key": "component_questions"
        }
      }
    ],
    "result_key": "processed_components"
  }
}
```

### Processing Files from a Directory

```json
{
  "type": "loop",
  "config": {
    "items": "code_files",
    "item_key": "file",
    "substeps": [
      {
        "type": "read_files",
        "config": {
          "path": "{{file.path}}",
          "content_key": "file_content"
        }
      },
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Analyze this code file:\n{{file_content}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "file_analysis"
        }
      }
    ],
    "result_key": "analyzed_files"
  }
}
```

### Transforming an Array

```json
{
  "type": "loop",
  "config": {
    "items": "input_data",
    "item_key": "item",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Transform this data item: {{item}}\nIndex: {{__index}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "transformed_item"
        }
      }
    ],
    "result_key": "transformed_data"
  }
}
```

### Parallel Processing Example

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 5,
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate a blueprint for component: {{component.name}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "blueprint"
        }
      },
      {
        "type": "write_files",
        "config": {
          "files_key": "blueprint",
          "root": "{{output_dir}}/components/{{component.id}}"
        }
      }
    ],
    "result_key": "processed_blueprints"
  }
}
```

In this example, up to 5 components will be processed simultaneously, each generating and writing a blueprint. This can significantly reduce execution time for LLM-intensive operations across multiple items.

## Error Handling

By default, the LoopStep will stop processing on the first error (`fail_fast: true`). You can change this behavior:

```json
{
  "type": "loop",
  "items": "components",
  "item_key": "component",
  "substeps": [...],
  "result_key": "processed_components",
  "fail_fast": false
}
```

With `fail_fast: false`, the LoopStep will:

- Continue processing remaining items even if some fail
- Include successful results in the output collection
- Log errors for failed items
- Add information about failed items to the `__errors` key in the result collection

## Important Notes

- Each item is processed in isolation with its own context clone
- Changes to the parent context during iteration are not visible to subsequent iterations
- The final result is always a collection, even if only one item is processed
- If the items collection is empty, an empty collection is stored in the result_key
- If a referenced key doesn't exist in the context, an error is raised
- Collection elements can be of any type (objects, strings, numbers, etc.)
- The LoopStep supports both array and object collections


=== File: blueprints/recipe_executor/components/steps/loop/loop_spec.md ===
# LoopStep Component Specification

## Purpose

The LoopStep component enables recipes to iterate over a collection of items, executing a specified set of steps for each item. It serves as a fundamental building block for batch processing, enabling modular workflows that operate on multiple similar items without requiring separate recipes.

## Core Requirements

- Process each item in a collection using a specified set of steps
- Support template rendering for the `items` path to access nested data structures via dot notation (e.g., "results.data.items")
- Isolate processing of each item to prevent cross-contamination
- Store the results of processing each item in a designated collection
- Support conditional execution based on item properties
- Provide consistent error handling across all iterations
- Maintain processing state to enable resumability
- Support various collection types (arrays, objects)
- Support concurrent processing of items using configurable parallelism settings (max_concurrency > 1, or max_concurrency = 0 for no limit)
- Provide control over the number of items processed simultaneously
- Allow for staggered execution of parallel items via optional delay parameter
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Process `items` strings using template rendering to determine if they are collections or if it remains a string
  - For `items` that remain a string, apply template rendering to the path before accessing data, enabling support for nested paths
- Clone the context for each item to maintain isolation between iterations
- Use a unique context key for each processed item to prevent collisions
- Execute the specified steps for each item using the current executor
- Collect results into a unified collection once all items are processed
- Log progress for each iteration to enable monitoring
- Support proper error propagation while maintaining iteration context
- Handle empty collections gracefully
- Leverage asyncio for efficient processing
- Support structured iteration history for debugging
- Use asyncio for concurrency control and task management
- If parallel item processing is enabled (max_concurrency > 1):
  - Implement an async execution model to allow for non-blocking I/O operations
  - When executing items in parallel, properly await async operations and run sync operations directly
  - Use `Context.clone()` to create independent context copies for each item
  - Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
  - Monitor exceptions and implement fail-fast behavior
  - Provide clear logging for item lifecycle events and execution summary
  - Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols**: Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Base**: Adheres to the step execution interface via StepProtocol
- **Step Registry**: Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Context**: Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor**: Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates**: Uses template rendering for the `items` path and sub-step configurations

### External Libraries

- **asyncio**: Uses asyncio for asynchronous processing and managing parallel processing of loop items
- **time**: Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Logging

- Debug: Log the start/end of each item processing with its index/key, log steps execution within the loop
- Info: Log high-level information about how many items are being processed and the result collection

## Error Handling

- Validate the items collection exists and is iterable before starting
- Validate that steps are properly specified
- Handle both empty collections and single items gracefully
- Provide clear error messages when an item fails processing
- Include the item key/index in error messages for easier debugging
- Allow configuration of whether to fail fast or continue on errors

## Output Files

- `recipe_executor/steps/loop.py` - (LoopStep implementation)


=== File: blueprints/recipe_executor/components/steps/mcp/mcp_docs.md ===
# MCPStep Component Usage

## Importing

```python
from recipe_executor.steps.mcp import MCPStep, MCPConfig
```

## Configuration

The MCPStep is configured with a `MCPConfig`:

```python
class MCPConfig(StepConfig):
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result as a dictionary.
    """
    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"
```

The `server` field is a dictionary containing the server configuration, which can include:

For HTTP servers:

- `url`: str - the URL of the MCP server.
- `headers`: Optional[Dict[str, Any]] -headers to include in the request.

For stdio servers:

- `command`: str - the command to run the MCP server.
- `args`: List[str] - arguments to pass to the command.
- `env`: Optional[Dict[str, str]] - environment variables to set for the command.
  - If an env var is set to "", an attempt will be made to load the variable from the system environment variables and `.env` file.
- `working_dir`: The working directory for the command.

## Basic Usage in Recipes

The `MCPStep` is available via the `mcp` step type in recipes:

```json
{
  "steps": [
    {
      "type": "mcp",
      "config": {
        "server": {
          "url": "http://localhost:5000",
          "headers": {
            "api_key": "your_api_key"
          }
        },
        "tool_name": "get_stock",
        "arguments": { "item_id": "{{item_id}}" },
        "result_key": "stock_info"
      }
    }
  ]
}
```

After execution, the context contains:

```json
{
  "stock_info": {
    "item_id": 123,
    "name": "Widget",
    "price": 19.99,
    "in_stock": true,
    "quantity": 42
  }
}
```

## Template-Based Configuration

All string configuration fields support templating using context variables.


=== File: blueprints/recipe_executor/components/steps/mcp/mcp_spec.md ===
# MCPStep Component Specification

## Purpose

The MCPStep component allows recipes to invoke tools on remote MCP servers and store the result in the execution context.

## Core Requirements

- Accept configuration for the MCP server, tool name, arguments, and result key.
- Use a minimal MCP client implementation:
  - Connect to the MCP server using the provided configuration.
  - Call the specified tool with the provided arguments.
- Handle errors:
  - Raise a `ValueError` with a clear message if the call fails.
- Remain stateless across invocations.

## Implementation Considerations

- Retrieve configuration values via the step config object.
- Use `render_template` to resolve templated configuration values before use.
- Use `mcp.client.sse.sse_client` or `mcp.client.stdio.stdio_client` to create `ClientSession` instance.
  - For `stdio_client`:
    - Use `StdioServerParameters` for `server` config parameter.
    - Use `cwd` as the working directory in the server config.
- Intialize session and execute session.call_tool with the tool name and arguments.
- Wrap exceptions from the client in `ValueError` including the tool name and service.
- Convert the `mcp.types.CallToolResult` to `Dict[str, Any]`.
- Store converted tool result dictionary in context under `result_key`.
- Overwrite existing context values if `result_key` already exists.

## Logging

- Debug: Log connection attempts and tool invocation details (tool name, arguments).
- Info: None by default.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context interactions and `StepProtocol` for the step interface.
- **Utils/Templates**: Uses `render_template` for resolving templated parameters.

### External Libraries

- **mcp**: Provides `client.sse.sse_client`, `stdio_client`, `types.CallToolResult` `StdioServerParameters` and `ClientSession` for MCP server interactions.
- **dotenv**: For loading environment variables from `.env` files.

### Configuration Dependencies

None

## Error Handling

- Raise `ValueError` on connection failures or tool invocation errors with descriptive messages.
- Allow exceptions from the client to propagate if not caught.

## Output Files

- `recipe_executor/steps/mcp.py`


=== File: blueprints/recipe_executor/components/steps/parallel/parallel_docs.md ===
# ParallelStep Component Usage

The **ParallelStep** component enables the concurrent execution of multiple sub-steps within a recipe. It is ideal for improving performance when independent tasks can be executed in parallel.

## Importing

Import the ParallelStep and its configuration:

```python
from recipe_executor.steps.parallel import ParallelStep, ParallelConfig
```

## Configuration

The ParallelStep is configured via a `ParallelConfig` object. This configuration defines the list of sub-steps to run concurrently, along with optional settings for controlling concurrency.

```python
class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0
```

## Step Registration

To enable the use of ParallelStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.parallel import ParallelStep

STEP_REGISTRY["parallel"] = ParallelStep
```

## Basic Usage in Recipes

The ParallelStep allows you to run multiple steps concurrently. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "parallel",
      "config": {
        "substeps": [
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "recipes/subtask_a.json",
              "context_overrides": {
                "input_data": "{{shared_input}}"
              }
            }
          },
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "recipes/subtask_b.json",
              "context_overrides": {
                "input_data": "{{shared_input}}"
              }
            }
          }
        ],
        "max_concurrency": 2, // Process up to 2 sub-steps in parallel
        "delay": 0.5 // Optional delay of 0.5 seconds between starting each sub-step
      }
    }
  ]
}
```

## Integration with Other Steps

The ParallelStep is designed to integrate seamlessly with the rest of your recipe:

- **Copies of Context:** All sub-steps are provided a copy of the same context (the shared context implements ContextProtocol), enabling them to read from common data.
- **Independent Execution:** Use ParallelStep only for tasks that do not depend on each other nor write back to context beyond the parallel block’s lifecycle, as each cloned context is discarded after the parallel block completes.

## Important Notes

- **Error Handling:** If any sub-step fails, the entire parallel execution aborts. Handle errors within each sub-step to ensure graceful degradation.
- **Resource Constraints:** Adjust `max_concurrency` based on system resources to avoid overwhelming the executor.
- **Delay Between Sub-steps:** Use the `delay` parameter to control the timing of sub-step execution, which can help manage resource contention.


=== File: blueprints/recipe_executor/components/steps/parallel/parallel_spec.md ===
# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It improves execution efficiency by parallelizing independent tasks while maintaining isolation between them.

## Core Requirements

- Accept a list of sub-step configurations (each sub-step is an `execute_recipe` step definition)
- Clone the current execution context for each sub-step to ensure isolation
- Execute sub-steps concurrently with a configurable maximum concurrency limit (max_concurrency > 1, or max_concurrency = 0 for no limit)
- Support an optional delay between launching each sub-step
- Wait for all sub-steps to complete before proceeding, with appropriate timeout handling
- Implement fail-fast behavior: if any sub-step fails, stop launching new ones and report the error
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Use asyncio for concurrency control and task management
- Implement an async execution model to allow for non-blocking I/O operations
- When executing substeps, properly await async operations and run sync operations directly
- Add configurable timeouts to prevent indefinite waiting for task completion
- Use `Context.clone()` to create independent context copies for each sub-step
- Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
- Monitor exceptions and implement fail-fast behavior
- Provide clear logging for sub-step lifecycle events and execution summary
- Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context management, ExecutorProtocol for parallel execution, and StepProtocol for the step interface
- **Step Base**: Adheres to the step execution interface via StepProtocol
- **Step Registry**: Uses the step registry to instantiate the `execute_recipe` step for each sub-step

### External Libraries

- **asyncio**: Utilizes asyncio for asynchronous task management and parallel execution
- **time**: Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Logging

- Debug: Log sub-step start/completion events, thread allocation, and configuration details
- Info: Log start and completion with a summary of the parallel execution (number of steps and success/failure counts)

## Error Handling

- Implement fail-fast behavior when any sub-step encounters an error
- Cancel pending sub-steps if an error occurs
- Include clear error context identifying which sub-step failed
- Ensure proper thread pool shutdown to prevent orphaned threads
- Propagate the original exception with contextual information about the failure

## Output Files

- `recipe_executor/steps/parallel.py` (ParallelStep implementation)


=== File: blueprints/recipe_executor/components/steps/read_files/read_files_docs.md ===
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
You can also read multiple files by providing a glob pattern that will be expanded with the matching entities.
A glob is a term used to define patterns for matching file and directory names based on wildcards. Globbing is the act of defining one or more glob patterns, and yielding files from either inclusive or exclusive matches :

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/*_spec.md",
        "content_key": "component_specs",
        "merge_mode": "concat"
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


=== File: blueprints/recipe_executor/components/steps/read_files/read_files_spec.md ===
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


=== File: blueprints/recipe_executor/components/steps/registry/registry_docs.md ===
# Step Registry Component Usage

## Importing

```python
from recipe_executor.steps.registry import STEP_REGISTRY
```

## Registry Structure

The registry is a simple dictionary that maps step type names to their implementation classes:

```python
# Type definition
from typing import Dict, Type
from recipe_executor.steps.base import BaseStep

# Structure of STEP_REGISTRY
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "set_context": SetContextStep,
    "write_files": WriteFilesStep,
}
```

Custom steps can be registered in the same way:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.base import BaseStep
from my_custom_steps import CustomStep

# Register a custom step implementation
STEP_REGISTRY["custom_step"] = CustomStep
```

## Looking Up Steps

The executor uses the registry to look up step classes by type:

```python
# Example of registry usage in executor
from recipe_executor.steps.registry import STEP_REGISTRY

... code ...
    step_type = step["type"]
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}'")

    step_class = STEP_REGISTRY[step_type]
    step_config = step.get("config", {})
    step_instance = step_class(logger, step_config)
    await step_instance.execute(context)
```

## Important Notes

- Step type names must be unique across the entire system
- Steps must be registered before the executor tries to use them
- Standard steps are automatically registered when the package is imported
- Custom steps need to be explicitly registered by the user


=== File: blueprints/recipe_executor/components/steps/registry/registry_spec.md ===
# Step Registry Component Specification

## Purpose

The Step Registry component provides a central mechanism for registering and looking up step implementations by their type names. It enables the dynamic discovery of step classes during recipe execution.

## Core Requirements

- Provide a simple mapping between step type names and their implementation classes
- Support registration of step implementations from anywhere in the codebase
- Enable the executor to look up step classes by their type name
- Follow a minimal, dictionary-based approach with no unnecessary complexity

## Implementation Considerations

- Use a single, global dictionary to store all step registrations
- Allow steps to register themselves upon import
- Keep the registry structure simple and stateless
- Avoid unnecessary abstractions or wrapper functions

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Output Files

- `recipe_executor/steps/registry.py`
- `recipe_executor/steps/__init__.py` (details below)

```python
# recipe_executor/steps/__init__.py
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import MCPStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.set_context import SetContextStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "set_context": SetContextStep,
    "write_files": WriteFilesStep,
})
```


=== File: blueprints/recipe_executor/components/steps/set_context/set_context_docs.md ===
# SetContextStep Component Usage

## Importing

```python
from recipe_executor.steps.set_context import SetContextStep, SetContextConfig
```

## Configuration

`SetContextStep` is configured with a simple `SetContextConfig`:

```python
class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: String, list, dict **or** Liquid template string rendered against
               the current context.
        nested_render: Whether to render the prompt with nested context, recursively
                       until no more templates are found. This is useful for rendering complex prompts with multiple levels of context. Wrap any sections that should not be rendered in {% raw %}...{% endraw %}.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """
    key: str
    value: Union[str, list, dict]
    nested_render: bool = False
    if_exists: Literal["overwrite", "merge"] = "overwrite"
```

### Merge semantics (when `if_exists: "merge"`)

| Existing type      | New type       | Result                                                      |
| ------------------ | -------------- | ----------------------------------------------------------- |
| `str`              | `str`          | `old + new` (simple concatenation)                          |
| `list`             | `list` or item | `old + new` (append)                                        |
| `dict`             | `dict`         | Shallow merge – keys in `new` overwrite duplicates in `old` |
| Other / mismatched | any            | `[old, new]` (both preserved in a list)                     |

## Step Registration

Register once (typically in `recipe_executor/steps/__init__.py`):

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.set_context import SetContextStep

STEP_REGISTRY["set_context"] = SetContextStep
```

The executor will then recognise the `"set_context"` step type during recipe execution.

## Basic Usage in Recipes

**Create or append to a document artifact**

```json
{
  "type": "set_context",
  "config": {
    "key": "document",
    "value": "{{ content }}",
    "if_exists": "merge"
  }
}
```

**Create a dictionary artifact**

```json
{
  "type": "set_context",
  "config": {
    "key": "document",
    "value": {
      "title": "{{ title }}",
      "description": "{{ description }}"
    },
    "if_exists": "merge"
  }
}
```

**Nested content rendering**

Example loaded data file:

```json
{
  "report": {
    "prompt": "Perform sentiment analysis on the following data: {{ context.data }}"
  }
}
```

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "report_instruction.json",
        "content_key": "loaded_prompts"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "rendered_prompt",
        "value": "Generate a markdown formatted document based upon: {{loaded_prompts.report.prompt}}",
        "nested_render": true
      }
    }
  ]
}
```

**NOTE**: Anything wrapped in `{% raw %}...{% endraw %}` will not be rendered. This is useful for including template sample snippets or other content that should not be processed as a template.

**Pull a section from another artifact**

```json
{
  "type": "set_context",
  "config": {
    "key": "section_md",
    "value": "{{ context[section.content_key] }}"
  }
}
```

After execution, the target keys (`document`, `section_md`) are available for any downstream steps in the same recipe run, just like artifacts produced by `read_files`, `llm_generate`, or other core steps.

## Important Notes

- `value` strings are rendered with the same Liquid templating engine used throughout the toolchain, so you can interpolate any current context values before they are stored.
- `if_exists` defaults to `"overwrite"` for consistent behavior.
- Merging is intentionally **shallow** for dictionaries to keep the step lightweight; if you need deep-merge semantics, perform that in a custom step or LLM call.


=== File: blueprints/recipe_executor/components/steps/set_context/set_context_spec.md ===
# SetContextStep Component Specification

## Purpose

The **SetContextStep** component provides a declarative way for recipes to create or update artifacts in the shared execution context.

## Core Requirements

- Accept a **key** (string) that identifies the artifact in `ContextProtocol`.
- Accept a **value** that may be:
  - Any JSON-serializable literal, **or**
  - A Liquid template string rendered against the current context before assignment.
- If `nested_render` is true, recursively render the `value` using context data until all variables are resolved, ignoring any template variables that are wrapped in `{% raw %}` tags
- Support an **if_exists** strategy with the following options:
  - `"overwrite"` (default) – replace the existing value.
  - `"merge"` – combine the existing and new values using type-aware rules.
- Implement shallow merge semantics when `if_exists="merge"`:
  | Existing type | New type | Result |
  | ------------- | -------------- | --------------------------------------------------------------- |
  | `str` | `str` | Concatenate: `old + new` |
  | `list` | `list` or item | Append: `old + new` |
  | `dict` | `dict` | Shallow dict merge; keys in `new` overwrite duplicates in `old` |
  | Mismatched | any | Create a 2-item list `[old, new]` |

## Implementation Considerations

- **Template rendering**:
  - When `value` is a string, call `render_template(value, context)` before assignment.
  - When `value` is a list or dict, call `render_template` on each item, all the way down.
  - If `nested_render` is true, recursively render the `value` using context data until all variables are resolved, ignoring any template variables that are wrapped in `{% raw %}` tags
    - When `true`, after the initial `render_template` pass on `value`, repeat rendering while the string both changes **and** still contains Liquid tags (`{{` or `{%}`), ignoring `{% raw %}`. This ensures nested templates inside your `value` get fully expanded.
- **Merge helper**: Encapsulate merge logic in a small private function to keep `execute()` readable.

## Logging

- _Info_: one-line message indicating `key`, `strategy`, and whether the key previously existed.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context read/write operations.
- **Context**: Uses `Context` for storing artifacts.
- **Step Base**: Inherits from `BaseStep` and uses `StepConfig` for validation.
- **Utilities**: Calls `render_template` for Liquid evaluation.

### External Libraries

None

### Configuration Dependencies

None.

## Error Handling

- Raise `ValueError` for unknown `if_exists` values.
- Allow merge helper to fall back to `[old, new]` to avoid hard failures on type mismatch.
- Propagate template rendering errors unchanged for visibility.

## Output Files

- `recipe_executor/steps/set_context.py` – implementation of **SetContextStep**.


=== File: blueprints/recipe_executor/components/steps/write_files/write_files_docs.md ===
# WriteFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFilesStep, WriteFilesConfig
```

## Configuration

The WriteFilesStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        files_key: Optional name of the context key holding a List[FileSpec].
        files: Optional list of dictionaries with 'path' and 'content' keys.
        root: Optional base path to prepend to all output file paths.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."
```

## Step Registration

The WriteFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

STEP_REGISTRY["write_files"] = WriteFilesStep
```

## Basic Usage in Recipes

Either `files_key` or `files` is required in the configuration. If both are provided, `files` takes precedence.

The `files_key` is the context key where the generated files are stored. The `files` parameter can be used to directly provide a list of dictionaries with `path` and `content` keys. Alternatively, the path and content can be specfied using `path_key` and `content_key` respectively to reference values in the context.

Content (regardless of the input format or which context path the data comes in) is automatically detected and serialized to proper JSON with indentation if it is a Python dictionary or list. This ensures that the content is written in a readable format.

The WriteFilesStep can be used in recipes like this:

Files Key Example:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a Python script that prints 'Hello, world!'",
        "model": "openai/o4-mini",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        # Preferred way to receive "files" from other steps that create FileSpec objects
        "files_key": "generated_files",
        "root": "output/src"
      }
    }
  ]
}
```

Files Example:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files": [
          { "path": "src/main.py", "content": "print('Hello, world!')" },
          {
            "path": "src/{{component_name}}_utils.py",
            "content_key": "generated_code"
          },
          {
            "path_key": "generated_config_path",
            "content_key": "generated_config_data"
          }
        ],
        "root": "output/src"
      }
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### Single FileSpec object

```python
from recipe_executor.models import FileSpec
# Example of generating a FileSpec object
file = FileSpec(path="src/main.py", content="print('Hello, world!')")
# Store in context
context["generated_file"] = file
```

### List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Automatic JSON Serialization

When the content to be written is a Python dictionary or list, WriteFilesStep automatically serializes it to properly formatted JSON:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate configuration data for a project.",
        "model": "openai/o4-mini",
        "output_format": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "version": { "type": "string" },
            "dependencies": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "output_key": "project_config"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "config.json",
            "content_key": "project_config"
          }
        ],
        "root": "output"
      }
    }
  ]
}
```

In this example, `project_config` is a Python dictionary, but when written to `config.json`, it will be automatically serialized as proper JSON with double quotes and indentation.

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "output/{{project_name}}"
      }
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code....\nprint('Hello, world!')"
)
```

## Common Use Cases

**Writing Generated Code**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/src",
    "files_key": "generated_files"
  }
}
```

**Writing Structured Data as JSON**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/data",
    "files": [
      {
        "path": "config.json",
        "content_key": "config_data"
      }
    ]
  }
}
```

When `config_data` is a Python dictionary or list, it will be automatically serialized as formatted JSON.

**Project-Specific Output**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/{{project_name}}",
    "files_key": "project_files"
  }
}
```

**Component Generation**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/components",
    "files_key": "component_result"
  }
}
```

## Important Notes

- Directories are created automatically if they don't exist
- Files are overwritten without confirmation if they already exist
- All paths are rendered using template variables from the context (ContextProtocol)
- File content is not processed for templates
- File content is written using UTF-8 encoding
- Both FileSpec and List[FileSpec] input formats are supported
- Python dictionaries and lists are automatically serialized to properly formatted JSON with indentation
- JSON serialization uses `json.dumps(content, ensure_ascii=False, indent=2)` for consistent formatting


=== File: blueprints/recipe_executor/components/steps/write_files/write_files_spec.md ===
# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both single FileSpec and list of FileSpec formats as input
- Optional use of `files_key` to specify the context key for file content or `files` for direct input
- While `FileSpec` is preferred, the component should also support a list of dictionaries with `path` and `content` keys and then write the files to disk, preserving the original structure of `content`
- Create directories as needed for file paths
- Apply template rendering to all file paths and keys
- Do not apply template rendering to file content
- Automatically serialize Python dictionaries or lists to proper JSON format when writing to files
- Provide appropriate logging for file operations
- Follow a minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (single FileSpec or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically if they do not exist
- Regardless of which context path the data comes in, automatically detect when content is a Python dictionary or list and serialize it to proper JSON with indentation
- When serializing to JSON, use `json.dumps(content, ensure_ascii=False, indent=2)` for consistent, readable formatting
- Handle serialization errors with clear messages
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log each file's path and content before writing (to help debug failures)
- Info: Log the successful writing of each file (including its path) and the size of its content

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for the type of the context parameter in `execute` and `StepProtocol` for the step interface
- **Step Base**: Inherits from `BaseStep` to implement the step interface and uses `StepConfig` for configuration management
- **Models**: Uses FileSpec models for content structure
- **Context**: Reads file content from a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils/Templates**: Uses render_template for dynamic path resolution

### External Libraries

- **json**: For serializing Python dictionaries and lists to JSON

### Configuration Dependencies

None

## Error Handling

- Validate that the specified artifact exists in context
- Ensure the artifact contains a valid single FileSpec or list of FileSpec objects
- Handle serialization errors with clear error messages when content cannot be converted to JSON
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `recipe_executor/steps/write_files.py`


=== File: blueprints/recipe_executor/components/utils/models/models_docs.md ===
# Pydantic-Model Utilities

## Importing

```python
from recipe_executor.utils.models import json_schema_object_to_pydantic_model
```

## Conversion from JSON Object to Pydantic

This utility function converts a JSON object definition into a Pydantic model. It
allows you to define an object as a JSON-Schema fragment and then generate a strongly-typed
Pydantic model that can be used for data validation and serialization.

The generated model will have fields corresponding to the properties defined in the
JSON-Schema. The types of the fields will be inferred from the JSON-Schema types.

```python
def json_object_to_pydantic_model(
    object_schema: Dict[str, Any],
    model_name: str = "SchemaModel"
) -> Type[pydantic.BaseModel]:
    """
    Convert a JSON object dictionary into a dynamic Pydantic model.

    Args:
        object_schema: A valid JSON-Schema fragment describing an object.
        model_name: Name given to the generated model class.

    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
```

Basic usage example:

```python
from recipe_executor.utils.models import json_object_to_pydantic_model

user_schema = {
    "type": "object",
    "properties": {
        "name":  {"type": "string"},
        "age":   {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

User = json_object_to_pydantic_model(user_schema, model_name="User")

instance = User(name="Alice", age=30, email="alice@example.com")
print(instance.model_dump())      # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

NOTE: An **object** is required at the root level of the schema. If the root type is not an object, a `ValueError` will be raised.


=== File: blueprints/recipe_executor/components/utils/models/models_spec.md ===
# Models-Utility Component Specification

## Purpose

Provide reusable helpers for Pydantic models, such as conversion from JSON-Schema object definitions to fully-typed
`pydantic.BaseModel` subclasses.

## Core Requirements

- `json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]`
  Converts any root-level **object** (incl. nested structures & `"required"`) into a `BaseModel` created with `pydantic.create_model`.
- The schema must be a valid JSON-Schema object fragment. Chilren of the root object can be:
  - JSON-Schema primitive types: `"string"`, `"integer"`, `"number"`, `"boolean"`.
  - Compound types: `"object"`, `"array"` (alias `"list"`).
  - Unknown / unsupported `"type"` values fall back to `typing.Any`.
- All schema types must yield a valid BaseModel subclass:
  - Root object schemas become a model with fields matching properties
  - Any other root type (e.g., array, string, number) is rejected as invalid.
- Strictly validate input schemas before processing.
- Stateless, synchronous, no logging, no I/O.
- Raise `ValueError` on malformed schemas (e.g., missing `"type"`).

## Implementation Considerations

- Use **`pydantic.create_model`** for creating all models.
- Generate deterministic nested-model names using a counter for nested objects.
- Provide clear error messages for schema validation issues.

## Component Dependencies

### Internal Components

- **None**

### External Libraries

- **pydantic** – (Required) Provides `BaseModel` and `create_model`.
- **typing** – (Required) `Any`, `List`, `Optional`, `Type`.

### Configuration Dependencies

None

## Logging

None

## Error Handling

- Raise **`ValueError`** with a clear message when the input schema is invalid or unsupported.
- Include details about the specific validation error in the error message.
- Validate schema types before processing to avoid cryptic errors.

## Dependency Integration Considerations

None

## Output Files

- `recipe_executor/utils/models.py`


=== File: blueprints/recipe_executor/components/utils/templates/templates_docs.md ===
# Template Utility Component Usage

## Importing

```python
from recipe_executor.utils.templates import render_template
```

## Template Rendering

The Templates utility component provides a `render_template` function that renders [Python Liquid](https://jg-rp.github.io/liquid/) templates using values from a context object implementing the ContextProtocol:

```python
def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Python Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.utils.templates import render_template

# Create a context with some values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template string using the context
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Python Liquid syntax. Here are some common features:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains nested dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```

## Custom Filters

In addition to the [built-in Python Liquid filters](https://jg-rp.github.io/liquid/filter_reference/), we have provided some additional custom filters for specific use cases:

- `snakecase`: Converts a string to snake_case.
  - Syntax: `<string> | snakecase`
  - Example: `{{ "Hello World" | snakecase }}` results in `hello_world`.

The following "extra filters" are also available:

- `json`: Return the input object serialized to a JSON (JavaScript Object Notation) string.
  - Syntax: `<object> | json[: <indent>]`
  - Example: `{{ {"name": "John", "age": 30} | json: indent: 2 }}` results in:
    ```json
    {
      "name": "John",
      "age": 30
    }
    ```
- `datetime`: Date and time formatting. Return the input datetime formatted according to the current locale. If `dt` is a `datetime.datetime` object `datetime.datetime(2007, 4, 1, 15, 30)`.
  - Syntax: `<object> | datetime[: <format>]`
  - Valid formats:
    - `short`: Short date format.
    - `medium`: Medium date format.
    - `long`: Long date format.
    - `full`: Full date format.
    - Custom formats using [CLDR](https://cldr.unicode.org/translation/date-time/date-time-patterns) format (e.g., `MMM d, y`).
  - Example: `{{ dt | datetime }}` results in `Apr 1, 2007, 3:30:00 PM` (default format).
  - Example: `{{ dt | datetime: format: 'MMM d, y' }}` results in `2007-04-01`.
  - Example: `{{ dt | datetime: format: 'short' }}` results in `01/04/2007, 03:30`.


=== File: blueprints/recipe_executor/components/utils/templates/templates_spec.md ===
# Utils Component Specification

## Purpose

The Utils component provides general utility functions for recipes, primarily focused on template rendering. It offers a way to render strings with template variables against the execution context, enabling dynamic content generation in recipes.

## Core Requirements

- Render strings as templates using context data
- Utilize a standard templating engine (Liquid) for consistency
- Ensure that all context values are accessible to the templates
- Handle errors in template rendering gracefully
- Keep the utility functions stateless and reusable

## Implementation Considerations

- Use the Liquid templating library directly without unnecessary abstraction
- Pass the `context.dict()` to the Liquid template for rendering
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused on its single responsibility

## Logging

- None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol definition for context data access

### External Libraries

- **python-liquid**: Uses the Liquid templating engine for rendering

### Configuration Dependencies

None

## Error Handling

- Wrap template rendering in try/except blocks
- Raise ValueError with a clear message if rendering fails
- Use `liquid.exceptions.LiquidError` for Liquid-specific errors, otherwise just raise a generic ValueError
- Ensure that the error message includes the template and context for easier debugging

## Output Files

- `recipe_executor/utils/templates.py`


=== File: blueprints/recipe_executor/generate_authoring_guide.json ===
{
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "outline_file",
        "value": "{{ outline_file | default: 'blueprints/recipe_executor/outlines/recipe-json-authoring-guide.json' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output/docs' }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root | default: 'recipes/document_generator' }}/document_generator_recipe.json"
      }
    }
  ]
}


=== File: blueprints/recipe_executor/generate_codebase.json ===
{
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "project_blueprints_root",
        "value": "{{ project_blueprints_root | default: 'blueprints/recipe_executor' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "edit",
        "value": "{{ edit | default: false }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "component_id",
        "value": "{{ component_id | default: 'all' }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root | default: 'recipes/codebase_generator' }}/codebase_generator_recipe.json"
      }
    }
  ]
}


=== File: blueprints/recipe_executor/outlines/recipe-json-authoring-guide.json ===
{
  "title": "Recipe JSON Authoring Guide",
  "general_instruction": "This document serves as a guide for effectively writing recipe JSON files for simple to complex levels of automation. Recipients of this file will not have access to the resource files that are available during the drafting of this document, so please be sure to include all relevant information in the document itself. The document should be structured in a way that is easy to read and understand, with clear headings and sections. Use the provided outline as a guide for the structure of the document. The document should be written in a way that is accessible to users who may not have a technical background.",
  "resources": [
    {
      "key": "recipe_executor_code",
      "path": "ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md",
      "description": "Roll-up of the recipe executor code files. These files were generated by the recipe executor itself, using the recipe executor recipe files."
    },
    {
      "key": "recipe_executor_blueprints",
      "path": "ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md",
      "description": "Blueprint files used with the codebase generator recipes for generating the recipe executor code files. This roll-up includes the individual component 'docs' and 'spec' files that define each component. The component `docs` files can serve as documentation for the component."
    },
    {
      "key": "codebase_generator_recipes",
      "path": "ai_context/generated/CODEBASE_GENERATOR_RECIPE_FILES.md",
      "description": "Recipe files used to generate code from blueprint files (component manifest and then per-component 'docs' and 'spec' files)."
    },
    {
      "key": "sample_recipes",
      "path": "ai_context/generated/BLUEPRINT_GENERATOR_V4_RECIPE_FILES.md, ai_context/generated/DOCUMENT_GENERATOR_RECIPE_FILES.md",
      "description": "Additional sample recipes that show other ways to use the recipe tools for different use cases and ways to use Python Liquid templating, the various step types, etc."
    },
    {
      "key": "modular_design_philosophy",
      "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
      "description": "The modular design philosophy document. This document describes the modular design philosophy of our work, with can be applied to how we construct recipes as well."
    },
    {
      "key": "implementation_philosophy",
      "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
      "description": "The implementation philosophy document. This document describes the implementation philosophy of our work, with can be applied to how we construct recipes as well."
    },
    {
      "key": "liquid_docs",
      "path": "ai_context/git_collector/LIQUID_PYTHON_DOCS.md",
      "description": "Documentation for the Python Liquid templating engine. This includes the Liquid syntax, filters, and tags that can be used in recipe JSON files. Consider the contents of actual recipe files and the generated code as the primary source of truth for how to use Liquid templating in recipes, as we have discovered some issues with the Liquid documentation."
    }
  ],
  "sections": [
    {
      "title": "Introduction",
      "prompt": "Write an opening that:\n- Defines what the overall recipe framework is, what a recipe JSON file is and how the Recipe Executor runs it.\n- States that this guide targets both *human* developers and *LLM* assistants that must generate valid recipes from natural-language requests.\n- Lists the main topics that will follow (basic structure → context → step types → templating → best practices → snippets).",
      "refs": [
        "recipe_executor_code",
        "recipe_executor_blueprints",
        "codebase_generator_recipes"
      ]
    },
    {
      "title": "Basic Recipe Structure",
      "prompt": "Using the executor's code & example recipes as ground truth, explain:\n1. The required top-level `\"steps\"` array (must be valid/strict JSON without comments, etc.; unknown step `type` raises an error).\n2. Optional blocks (`inputs`, `outputs`, `description`) and how the executor ignores unknown keys.\n3. A **minimal runnable example** (just one step) plus a **slightly larger skeleton** showing `set_context`, `read_files`, `execute_recipe`, `loop`, `write_files`.\nKeep prose to a useful, but not overly verbose length; rely on code snippets, mermaid diagrams, and bullet lists where appropriate.",
      "refs": [
        "recipe_executor_code",
        "sample_recipes",
        "recipe_executor_blueprints",
        "codebase_generator_recipes"
      ]
    },
    {
      "title": "Working with Objects Between Recipe Steps",
      "prompt": "Describe the shared *context* object:\n- How each step reads/writes keys (pass by reference, no manual serialization needed).\n- Common patterns (`set_context`, `context_overrides` in `execute_recipe`).\n- Call out **common mistakes** (e.g., unnecessary JSON filters, forgetting to set a `result_key` in loops).\nProvide at least *three* code snippets: simple value pass, complex object pass, loop iteration collecting results.",
      "refs": ["recipe_executor_code", "sample_recipes"]
    },
    {
      "title": "Built-in Step Types and Configuration",
      "prompt": "Give a concise overview (≤ 2 short paragraphs) of the Recipe Executor's built-in step types: why they matter, how the reference entries below are structured, and when to consult them. Finish with a simple table list of all current step type pulled from the resource code, so readers know what is going to be covered in the subsections.",
      "refs": [
        "recipe_executor_code",
        "recipe_executor_blueprints",
        "sample_recipes",
        "codebase_generator_recipes"
      ],
      "sections": [
        {
          "title": "`read_files`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`write_files`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`set_context`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`conditional`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`loop`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`parallel`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`execute_recipe`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`llm_generate`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        },

        {
          "title": "`mcp`",
          "prompt": "From the resource docs, write a full reference entry for this step: purpose, when to use, key configuration (with defaults), notable pitfalls, and at least one runnable example (more if important to show variants of use cases).",
          "refs": [
            "recipe_executor_blueprints",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        }
      ]
    },
    {
      "title": "Using Liquid Templating for Dynamic Content",
      "prompt": "Explain Liquid features supported by the executor (template substitutions, filters like `default`, loops, conditionals, `json`, `snakecase`, etc.).\nShow *four* diverse examples (dynamic path, default fallback, building a list with `for`, inline conditional).\nThen introduce a **sub-section** on embedding large content blocks:",
      "refs": [
        "liquid_docs",
        "recipe_executor_code",
        "sample_recipes",
        "codebase_generator_recipes"
      ],
      "sections": [
        {
          "title": "Embedding Large Content in Prompts",
          "prompt": "Using code and earlier docs as reference, teach the technique of wrapping big pasted docs in distinctive ALL-CAPS XML-like tags (e.g., `<SPEC>` … `</SPEC>`):\n- Why this helps LLMs focus or ignore sections.\n- Dos & Don'ts table (one tag per line, close every tag, treat as opaque, etc.).\n- Show a prompt snippet that injects a large markdown blob using this wrapper.",
          "refs": [
            "recipe_executor_code",
            "sample_recipes",
            "codebase_generator_recipes"
          ]
        }
      ]
    },
    {
      "title": "Best Practices and Patterns",
      "prompt": "Summarize *at least eight* actionable guidelines (concise bullets) covering:\n- Designing small, focused recipes; reusing sub-recipes.\n- Clear context keys & avoiding magic strings.\n- Guarding with `conditional` & optional file reads.\n- Loop/parallel concurrency & `fail_fast` considerations.\n- **Always supply `result_key` in loops** even if ignored.\n- **Token-budget / prompt-length advice** - suggest summarizing or wrapping large content.\n- Merge semantics with `set_context` (strings concatenate, lists append, dicts shallow-merge).",
      "refs": [
        "modular_design_philosophy",
        "implementation_philosophy",
        "recipe_executor_code",
        "sample_recipes"
      ]
    },
    {
      "title": "Recipe Cookbook",
      "prompt": "Provide **four** ready-to-paste snippets covering common automation patterns:\n1. Conditional file check & fallback.\n2. Batch loop over items (with concurrency).\n3. Parallel independent tasks.\n4. Reusing logic via `execute_recipe` (sub-recipe composition).\nFor each snippet include: purpose, typical use cases, natural-language flow summary, a Mermaid diagram (if helpful), and the JSON snippet.\nEnsure snippets compile against current executor code.",
      "refs": [
        "recipe_executor_code",
        "sample_recipes",
        "recipe_executor_blueprints",
        "codebase_generator_recipes"
      ]
    },
    {
      "title": "Conclusion",
      "prompt": "Write a wrap-up that recaps the major points (structure, context, templating, best practices) and encourages readers/LLMs to apply these principles when generating new recipes. End with an invitation to iterate and refine recipes as requirements evolve.",
      "refs": []
    }
  ]
}


