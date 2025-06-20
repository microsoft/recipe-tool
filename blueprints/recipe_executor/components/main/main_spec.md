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
