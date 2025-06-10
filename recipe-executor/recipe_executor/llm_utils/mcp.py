import os
import logging
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Attempt to import load_dotenv for .env support; optional
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

__all__ = ["get_mcp_server"]


def get_mcp_server(logger: logging.Logger, config: Dict[str, Any]) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.

    Raises:
        ValueError: If the configuration is invalid.
        RuntimeError: On underlying errors when creating the server instance.
    """
    # Validate config type
    if not isinstance(config, dict):
        raise ValueError("MCP server configuration must be a dict")

    # Mask sensitive values for debug logging
    masked: Dict[str, Any] = {}
    for key, value in config.items():
        if key in ("headers", "env") and isinstance(value, dict):
            masked[key] = {k: "***" for k in value.keys()}
        else:
            masked[key] = value
    logger.debug("MCP server configuration: %s", masked)

    # HTTP transport
    if "url" in config:
        url = config.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("HTTP MCP server requires a non-empty 'url' string")
        headers = config.get("headers")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("HTTP MCP server 'headers' must be a dict if provided")

        logger.info("Creating HTTP MCP server for URL: %s", url)
        try:
            # Only pass headers if provided
            server = MCPServerHTTP(url=url, headers=headers) if headers is not None else MCPServerHTTP(url=url)
        except Exception as exc:
            raise RuntimeError(f"Failed to create HTTP MCP server: {exc}") from exc
        return server

    # Stdio transport
    if "command" in config:
        command = config.get("command")
        if not isinstance(command, str) or not command:
            raise ValueError("Stdio MCP server requires a non-empty 'command' string")

        args = config.get("args")
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            raise ValueError("Stdio MCP server 'args' must be a list of strings")

        env_cfg = config.get("env")
        env: Optional[Dict[str, str]] = None
        if env_cfg is not None:
            if not isinstance(env_cfg, dict):
                raise ValueError("Stdio MCP server 'env' must be a dict if provided")
            # Load .env if any value is empty and dotenv is available
            if load_dotenv and any(v == "" for v in env_cfg.values()):  # type: ignore
                load_dotenv()  # type: ignore
            env = {}
            for k, v in env_cfg.items():
                if not isinstance(v, str):
                    raise ValueError(f"Environment variable '{k}' must be a string")
                if v == "":
                    # attempt to get from system environment
                    sys_val = os.getenv(k)
                    if sys_val is not None:
                        env[k] = sys_val
                else:
                    env[k] = v

        working_dir = config.get("working_dir")
        if working_dir is not None and not isinstance(working_dir, str):
            raise ValueError("Stdio MCP server 'working_dir' must be a string if provided")

        logger.info("Creating stdio MCP server with command: %s %s", command, args)
        try:
            server = MCPServerStdio(command=command, args=args, cwd=working_dir, env=env)
        except Exception as exc:
            raise RuntimeError(f"Failed to create stdio MCP server: {exc}") from exc
        return server

    # Neither HTTP nor Stdio specified
    raise ValueError("Invalid MCP server configuration: must contain 'url' for HTTP or 'command' for stdio transport")
