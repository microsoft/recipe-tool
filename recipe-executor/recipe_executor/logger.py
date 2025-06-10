import os
import sys
import logging
from typing import Any


def init_logger(log_dir: str = "logs", stdio_log_level: str = "INFO") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR" (case-insensitive).

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Get root logger and set lowest level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create log directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as exc:
        raise Exception(f"Failed to create log directory '{log_dir}': {exc}")

    # Define formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set up file handlers: debug.log, info.log, error.log
    level_map = [
        ("debug", logging.DEBUG),
        ("info", logging.INFO),
        ("error", logging.ERROR),
    ]
    for name, level in level_map:
        path = os.path.join(log_dir, f"{name}.log")
        try:
            file_handler = logging.FileHandler(path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as exc:
            raise Exception(f"Failed to set up {name} log file '{path}': {exc}")

    # Configure console (stdout) handler
    level_name = stdio_log_level.upper()
    if level_name == "WARN":
        level_name = "WARNING"
    if level_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level_name = "INFO"
    console_level: Any = getattr(logging, level_name, logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Initialization logs
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, level_name)
    logger.info("Logger initialized successfully")

    return logger
