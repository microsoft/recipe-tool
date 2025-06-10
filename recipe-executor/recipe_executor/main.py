import argparse
import asyncio
import logging
import os
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv

from .context import Context
from .executor import Executor
from .logger import init_logger


def parse_key_value_pairs(pairs: List[str]) -> Dict[str, str]:
    """
    Parse a list of strings in the form key=value into a dictionary.
    Raises ValueError on malformed entries.
    """
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid key=value format '{pair}'")
        key, value = pair.split("=", 1)
        if not key:
            raise ValueError(f"Invalid key in pair '{pair}'")
        result[key] = value
    return result


async def main_async() -> None:
    # Load environment variables from .env
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Recipe Executor CLI")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file to execute")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory for log files")
    parser.add_argument("--context", action="append", default=[], help="Context artifact values as key=value pairs")
    parser.add_argument("--config", action="append", default=[], help="Static configuration values as key=value pairs")
    args = parser.parse_args()

    # Ensure log directory exists
    try:
        os.makedirs(args.log_dir, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: cannot create log directory '{args.log_dir}': {e}\n")
        raise SystemExit(1)

    # Initialize logging
    try:
        logger: logging.Logger = init_logger(args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {e}\n")
        raise SystemExit(1)

    logger.debug("Starting Recipe Executor Tool")
    logger.debug("Parsed arguments: %s", args)

    # Parse context and config key=value pairs
    try:
        artifacts = parse_key_value_pairs(args.context)
        config = parse_key_value_pairs(args.config)
    except ValueError as ve:
        # Invalid context/config formatting
        raise ve

    logger.debug("Initial context artifacts: %s", artifacts)

    # Create execution context
    context = Context(artifacts=artifacts, config=config)

    # Create and run executor
    executor = Executor(logger)
    logger.info("Executing recipe: %s", args.recipe_path)

    start_time = time.time()
    try:
        await executor.execute(args.recipe_path, context)
    except Exception as exec_err:
        logger.error("An error occurred during recipe execution: %s", exec_err, exc_info=True)
        raise
    duration = time.time() - start_time

    logger.info("Recipe execution completed successfully in %.2f seconds", duration)


def main() -> None:
    try:
        asyncio.run(main_async())
    except ValueError as ve:
        sys.stderr.write(f"Context Error: {ve}\n")
        sys.exit(1)
    except SystemExit as se:
        # Preserve explicit exit codes
        sys.exit(se.code)
    except Exception:
        # Unexpected errors: print traceback
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
