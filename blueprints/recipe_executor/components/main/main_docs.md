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
