# mcp-servers/python-code-tools

[collect-files]

**Search:** ['mcp-servers/python-code-tools']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 1:25:39 PM
**Files:** 28

=== File: mcp-servers/python-code-tools/.ruff.toml ===
line-length = 120

[format]
docstring-code-format = true
line-ending = "lf"
preview = true


=== File: mcp-servers/python-code-tools/Makefile ===
repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk


=== File: mcp-servers/python-code-tools/README.md ===
# 🌐 Python Code Tools MCP

MCP server providing Python code quality tools (Ruff linting/fixing) for AI assistants.

## Quick Start

```bash
make install                            # From workspace root
python-code-tools stdio                # stdio transport
python-code-tools sse --port 3001      # SSE transport
```

## Tools

- `lint_code` - Lint and fix Python code snippets
- `lint_project` - Lint and fix entire Python projects

See the [main README](../../README.md) for setup and transport options.


=== File: mcp-servers/python-code-tools/examples/README.md ===
# Python Code Tools Examples

Example code demonstrating MCP server usage with different clients.

## Files

- **stdio_client_example.py** - pydantic-ai agent usage
- **direct_mcp_client_example.py** - Direct MCP client usage  
- **project_linting_example.py** - Project-level linting examples

Run examples directly to see MCP server integration patterns.


=== File: mcp-servers/python-code-tools/examples/direct_mcp_client_example.py ===
"""Example of using the Python Code Tools MCP server with a direct MCP client."""

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Sample Python code with some issues
SAMPLE_CODE = """
import sys
import os
import time  # unused import

def calculate_sum(a, b):
    result = a + b
    unused_variable = 42  # unused variable
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides"
"""  # noqa: E501


async def main():
    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ),  # Convert _Environ to regular dict
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("Connected to Python Code Tools MCP server")

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Available tools: {tool_names}")

            # Call the lint_code tool
            result = await session.call_tool("lint_code", {"code": SAMPLE_CODE, "fix": True})

            # Display the results
            print("\nLint Results:")

            # Get the content text from the result
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                # Check if the content is TextContent (which has a text attribute)
                if hasattr(first_content, "type") and first_content.type == "text":
                    lint_result_text = first_content.text

                    # Print the raw response for debugging
                    print(f"Response debug: {lint_result_text}")

                    lint_result = json.loads(lint_result_text)

                    # Calculate total issues
                    fixed_count = lint_result.get("fixed_count", 0)
                    remaining_count = lint_result.get("remaining_count", 0)
                    total_issues = fixed_count + remaining_count

                    print(f"Total issues found: {total_issues}")
                    print(f"Fixed issues: {fixed_count}")
                    print(f"Remaining issues: {remaining_count}")

                    print("\nFixed code:")
                    print("------------")
                    print(lint_result["fixed_code"])
                    print("------------")

                    # Show remaining issues if any
                    if remaining_count > 0:
                        print("\nRemaining issues:")
                        for issue in lint_result["issues"]:
                            print(
                                f"- Line {issue['line']}, Col {issue['column']}: {issue['code']} - {issue['message']}"
                            )
                    else:
                        print("\nAll issues were fixed!")

                    # Compare with original code
                    if fixed_count > 0:
                        print("\nChanges made:")
                        # A simple diff would be ideal here, but for simplicity we'll just highlight
                        # that changes were made
                        print(f"- Fixed {fixed_count} issues with the code")

                        if lint_result["fixed_code"] != SAMPLE_CODE:
                            print("- Code was modified during fixing")
                        else:
                            print("- NOTE: Code appears unchanged despite fixes")
                else:
                    print(
                        "Unexpected content type: "
                        f"{first_content.type if hasattr(first_content, 'type') else 'unknown'}"
                    )
            else:
                print("No content in the response")


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/direct_project_linting_example.py ===
"""Example of using project linting with a direct MCP client."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Use the current working directory (where you run the script from)
PROJECT_PATH = os.getcwd()


async def main():
    print(f"Using project path: {PROJECT_PATH}")

    # Create parameters for the stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "python_code_tools", "stdio"],
        env=dict(os.environ),  # Convert _Environ to regular dict
    )

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("Connected to Python Code Tools MCP server")

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Available tools: {tool_names}")

            try:
                # Call the lint_project tool with improved error handling
                print(f"Calling lint_project tool for path: {PROJECT_PATH}")
                result = await session.call_tool(
                    "lint_project",
                    {
                        "project_path": PROJECT_PATH,
                        "file_patterns": ["**/*.py", "*.py"],  # Both top-level and nested Python files
                        "fix": True,
                    },
                )

                # Display the results
                print("\nProject Lint Results:")

                # First, check if we got any response at all
                if not result or not result.content:
                    print("Error: No response content received from the MCP server")
                    sys.exit(1)

                # Get the content text from the result with better error handling
                first_content = result.content[0] if result.content else None
                if not first_content:
                    print("Error: Empty response content")
                    sys.exit(1)

                # Check if the content is TextContent (which has a text attribute)
                if not hasattr(first_content, "type") or first_content.type != "text":
                    print(f"Error: Unexpected content type: {getattr(first_content, 'type', 'unknown')}")
                    sys.exit(1)

                lint_result_text = first_content.text
                if not lint_result_text:
                    print("Error: Empty text content in response")
                    sys.exit(1)

                # Print the raw response for debugging
                print(f"Response debug: {lint_result_text}")

                try:
                    lint_result = json.loads(lint_result_text)

                    # Check if we got an error from the server
                    if "error" in lint_result:
                        print(f"Server reported an error: {lint_result['error']}")
                        sys.exit(1)

                    project_path = lint_result.get("project_path", PROJECT_PATH)
                    print(f"Project path: {project_path}")

                    # Display configuration information
                    config_source = lint_result.get("config_source", "unknown")
                    print(f"Configuration source: {config_source}")

                    if "config_summary" in lint_result and "ruff" in lint_result["config_summary"]:
                        ruff_config = lint_result["config_summary"]["ruff"]
                        print("Ruff configuration:")
                        for key, value in ruff_config.items():
                            print(f"  {key}: {value}")

                    # Calculate total issues (sum of fixed and remaining)
                    fixed_count = lint_result.get("fixed_count", 0)
                    remaining_count = lint_result.get("remaining_count", 0)
                    total_issues_count = fixed_count + remaining_count

                    # Print issue counts
                    print(f"\nTotal issues found: {total_issues_count}")
                    print(f"Fixed issues: {fixed_count}")
                    print(f"Remaining issues: {remaining_count}")

                    # Display fixed issues
                    if lint_result.get("fixed_issues") and fixed_count > 0:
                        print("\nIssues that were fixed:")
                        fixed_issues_by_file = {}
                        for issue in lint_result.get("fixed_issues", []):
                            file_path = issue.get("file", "unknown")
                            if file_path not in fixed_issues_by_file:
                                fixed_issues_by_file[file_path] = []
                            fixed_issues_by_file[file_path].append(issue)

                        # Print fixed issues grouped by file
                        for file_path, issues in fixed_issues_by_file.items():
                            print(f"\nFile: {file_path}")
                            for issue in issues:
                                print(
                                    f"  Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                                    f"{issue.get('code', '?')} - {issue.get('message', 'Unknown issue')}"
                                )

                    # Display remaining issues
                    if remaining_count > 0:
                        print("\nRemaining issues:")
                        issues_by_file = {}
                        for issue in lint_result.get("issues", []):
                            file_path = issue.get("file", "unknown")
                            if file_path not in issues_by_file:
                                issues_by_file[file_path] = []
                            issues_by_file[file_path].append(issue)

                        # Print issues grouped by file
                        for file_path, issues in issues_by_file.items():
                            print(f"\nFile: {file_path}")
                            for issue in issues:
                                print(
                                    f"  Line {issue.get('line', '?')}, Col {issue.get('column', '?')}: "
                                    f"{issue.get('code', '?')} - {issue.get('message', 'Unknown issue')}"
                                )

                    # Print file summary
                    if "files_summary" in lint_result and lint_result["files_summary"]:
                        print("\nFiles Summary:")
                        for file_path, summary in lint_result["files_summary"].items():
                            print(f"- {file_path}: {summary.get('total_issues', 0)} remaining issues")
                            if "issue_types" in summary:
                                print("  Issue types:")
                                for code, count in summary["issue_types"].items():
                                    print(f"    {code}: {count}")

                    # Print modified files
                    if "modified_files" in lint_result and lint_result["modified_files"]:
                        print("\nModified files:")
                        for file in lint_result["modified_files"]:
                            print(f"- {file}")
                    else:
                        print("\nNo files were modified.")

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response text: {lint_result_text}")
            except Exception as e:
                print(f"Error during linting: {e}", file=sys.stderr)
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/project_linting_example.py ===
"""Example of project-based linting with Python Code Tools MCP server."""

import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


async def main():
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Using project path: {current_dir}")

    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-7-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        print("Connected to Python Code Tools MCP server via stdio")

        # Example conversation with actual project path
        result = await agent.run(
            f"""
            Please analyze the Python code in this project directory using the lint_project tool.

            Run this command:
            ```
            lint_project(
                project_path="{current_dir}",
                file_patterns=["**/*.py"],
                fix=True
            )
            ```

            After running the lint_project tool, provide a detailed analysis that includes:
            1. How many total issues were found (fixed + remaining)
            2. What types of issues were fixed automatically
            3. What issues remain and need manual attention
            4. Which files were modified

            Please be specific about the exact issues found and fixed.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/examples/stdio_client_example.py ===
"""Example client using stdio transport with the Python Code Tools MCP server."""

import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Sample Python code with some issues
SAMPLE_CODE = """
import sys
import os
import time  # unused import

def calculate_sum(a, b):
    result = a + b
    unused_variable = 42  # unused variable
    return result

# Line too long - will be flagged by ruff
long_text = "This is a very long line of text that exceeds the default line length limit in most Python style guides like PEP 8 which recommends 79 characters, but if the configuration is set to 120, it will be ignored unless the line continues for more than 120 characters like this one now does at over 300 characters."
"""


async def main():
    # Set up the MCP server as a subprocess
    server = MCPServerStdio("python", args=["-m", "python_code_tools", "stdio"])

    # Create an agent with the MCP server
    agent = Agent("claude-3-7-sonnet-latest", mcp_servers=[server])

    # Use the MCP server in a conversation
    async with agent.run_mcp_servers():
        print("Connected to Python Code Tools MCP server via stdio")

        # Example conversation
        result = await agent.run(
            f"""
            Please analyze this Python code using the lint_code tool:

            ```python
            {SAMPLE_CODE}
            ```

            After running the lint_code tool, provide a detailed analysis that includes:
            1. How many total issues were found (fixed + remaining)
            2. What types of issues were fixed automatically
            3. What issues remain and need manual attention
            4. Show the fixed code and explain what was changed

            Please be specific about the exact issues found and fixed.

            Show the updated code with comments explaining the changes made.
            """
        )

        print("\nAgent's response:")
        print(result.output)


if __name__ == "__main__":
    asyncio.run(main())


=== File: mcp-servers/python-code-tools/pyproject.toml ===
[project]
name = "python-code-tools"
version = "0.1.0"
description = "MCP server providing Python code quality tools"
authors = [{ name = "MADE:Explorations Team" }]
license = "MIT"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.9.1",
    "pydantic>=2.7.2,<3.0.0",
    "ruff>=0.1.0",
    "tomli>=2.2.1",
]

[project.scripts]
# Main entry point
python-code-tools = "python_code_tools.cli:main"

# Convenience scripts for specific transports
python-code-tools-stdio = "python_code_tools.cli:stdio_main"
python-code-tools-sse = "python_code_tools.cli:sse_main"

[tool.uv]
package = true

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.hatch.build.targets.wheel]
packages = ["python_code_tools"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"


=== File: mcp-servers/python-code-tools/pyrightconfig.json ===
{
  "extraPaths": ["./"],
  "typeCheckingMode": "basic"
}


=== File: mcp-servers/python-code-tools/pytest.log ===


=== File: mcp-servers/python-code-tools/python_code_tools/__init__.py ===
"""Python Code Tools MCP server package."""

__version__ = "0.1.0"


=== File: mcp-servers/python-code-tools/python_code_tools/__main__.py ===
"""Entry point for running the package as a module."""

from python_code_tools.cli import main

if __name__ == "__main__":
    main()


=== File: mcp-servers/python-code-tools/python_code_tools/cli.py ===
"""Command-line interface for the Python Code Tools MCP server."""

import argparse
import sys
from typing import List, Optional

from python_code_tools.server import create_mcp_server


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Python Code Tools MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port for SSE server (default: 3001)",
    )

    args = parser.parse_args(argv)

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Python Code Tools MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def stdio_main() -> int:
    """Convenience entry point for stdio transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    return main(["stdio"])


def sse_main() -> int:
    """Convenience entry point for SSE transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Get any command-line arguments after the script name
    argv = sys.argv[1:]

    # Pre-populate the 'transport' argument
    all_args = ["sse"] + argv

    return main(all_args)


if __name__ == "__main__":
    sys.exit(main())


=== File: mcp-servers/python-code-tools/python_code_tools/linters/__init__.py ===
"""Module imports for the linters package."""

from python_code_tools.linters.base import (
    BaseLinter,
    CodeLinter,
    CodeLintResult,
    LintResult,
    ProjectLinter,
    ProjectLintResult,
)
from python_code_tools.linters.ruff import RuffLinter, RuffProjectLinter

__all__ = [
    # Base classes
    "BaseLinter",
    "CodeLinter",
    "ProjectLinter",
    "LintResult",
    "CodeLintResult",
    "ProjectLintResult",
    # Implementations
    "RuffLinter",
    "RuffProjectLinter",
]


=== File: mcp-servers/python-code-tools/python_code_tools/linters/base.py ===
"""Base interfaces for code linters."""

import abc
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

"""Result models for linting operations."""


class LintResult(BaseModel):
    """Base result model for linting."""

    issues: List[Dict[str, Any]] = Field(default_factory=list, description="List of issues found in the code")
    fixed_count: int = Field(0, description="Number of issues that were automatically fixed")
    remaining_count: int = Field(0, description="Number of issues that could not be fixed")


class CodeLintResult(LintResult):
    """Result model for code snippet linting."""

    fixed_code: str = Field(..., description="The code after linting and fixing (if enabled)")


class ProjectLintResult(LintResult):
    """Result model for project linting."""

    modified_files: List[str] = Field(
        default_factory=list, description="List of files that were modified by auto-fixes"
    )
    project_path: str = Field(..., description="Path to the project directory that was linted")
    has_ruff_config: bool = Field(False, description="Whether the project has a ruff configuration file")
    # Configuration information
    config_source: Optional[str] = Field(
        "default", description="Source of the configuration (none, pyproject.toml, ruff.toml, etc.)"
    )
    config_summary: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Summary of configuration from different sources"
    )
    files_summary: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Summary of issues by file")
    # New fields for tracking fixed issues
    fixed_issues: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of issues that were fixed during linting"
    )
    fixed_issues_summary: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Summary of fixed issues grouped by file"
    )


class BaseLinter(abc.ABC):
    """Abstract base class for all linters."""

    def __init__(self, name: str, **kwargs):
        """Initialize the linter.

        Args:
            name: The name of the linter
            **kwargs: Additional configuration options
        """
        self.name = name
        self.config = kwargs


class CodeLinter(BaseLinter):
    """Abstract base class for code snippet linters."""

    @abc.abstractmethod
    async def lint_code(self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> CodeLintResult:
        """Lint the provided code snippet and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        pass


class ProjectLinter(BaseLinter):
    """Abstract base class for project directory linters."""

    @abc.abstractmethod
    async def lint_project(
        self,
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> ProjectLintResult:
        """Lint a project directory and return the results.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A ProjectLintResult object containing issues found and fix details
        """
        pass


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/__init__.py ===
from python_code_tools.linters.ruff.project import RuffProjectLinter
from python_code_tools.linters.ruff.snippet import RuffLinter

__all__ = [
    # Base classes
    "RuffLinter",
    "RuffProjectLinter",
]


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/config.py ===
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import tomli

default_config = {
    "select": "E,F,W,I",
    "ignore": [],
    "line-length": 100,
}


async def get_config(user_config: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    """Get the preferred configuration for Ruff.

    Args:
        user_config: Optional user-provided configuration

    Returns:
        Tuple of (configuration settings, source description)
    """
    print(f"Getting Ruff configuration. User config provided: {user_config is not None}")

    # Priority order:
    # 1. User-provided configuration
    # 2. Project configuration from .ruff.toml
    # 3. Project configuration from pyproject.toml
    # 4. Default configuration

    if user_config:
        # User config has highest priority - use ONLY this
        print("Using user-provided configuration")
        return user_config, "user"
    else:
        # Project config has second priority - use ONLY this
        project_config, source = await read_project_config(Path.cwd())
        if project_config:
            print(f"Using project configuration from {source}")
            return project_config, source
        else:
            # Default config has lowest priority - use ONLY this
            print("No project configuration found, using default configuration")
            return default_config, "default"


async def read_project_config(path: Path) -> Tuple[Dict[str, Any], str]:
    """Read Ruff configuration from files within the project directory.

    Args:
        path: Project directory path

    Returns:
        Tuple of (configuration settings, source description)
    """
    config = {}
    source = "none"

    print(f"Looking for Ruff configuration files in {path}")

    # Check for .ruff.toml (highest priority)
    ruff_toml_path = path / ".ruff.toml"
    if ruff_toml_path.exists():
        print(f"Found .ruff.toml at {ruff_toml_path}")
        try:
            with open(ruff_toml_path, "rb") as f:
                ruff_config = tomli.load(f)
                if "lint" in ruff_config:
                    config.update(ruff_config["lint"])
                else:
                    config.update(ruff_config)
                # Return immediately since this is highest priority
                return config, ".ruff.toml"
        except Exception as e:
            print(f"Error reading .ruff.toml: {e}")

    # Check for pyproject.toml (lower priority)
    pyproject_path = path / "pyproject.toml"
    if pyproject_path.exists():
        print(f"Found pyproject.toml at {pyproject_path}")
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
                # Extract Ruff configuration
                if "tool" in pyproject_data and "ruff" in pyproject_data["tool"]:
                    ruff_config = pyproject_data["tool"]["ruff"]
                    if "lint" in ruff_config:
                        config.update(ruff_config["lint"])
                    else:
                        config.update(ruff_config)
                    return config, "pyproject.toml"
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

    return config, source


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/project.py ===
from pathlib import Path

from python_code_tools.linters.base import ProjectLinter, ProjectLintResult
from python_code_tools.linters.ruff.config import get_config
from python_code_tools.linters.ruff.reporter import create_issues_summary, identify_fixed_issues, print_final_report
from python_code_tools.linters.ruff.runner import get_python_files, run_ruff_check, run_ruff_fix
from python_code_tools.linters.ruff.utils import (
    convert_issue_paths_to_relative,
    convert_summary_paths_to_relative,
    get_file_hashes,
    get_modified_files,
)


class RuffProjectLinter(ProjectLinter):
    def __init__(self, **kwargs) -> None:
        super().__init__(name="ruff-project", **kwargs)

    async def lint_project(self, project_path: str, file_patterns=None, fix=True, config=None) -> ProjectLintResult:
        path = Path(project_path)
        effective_config, config_source = await get_config(config)
        has_ruff_config = config_source != "default"

        # Properly structure the config summary as a dictionary of dictionaries
        config_summary = {"ruff": {}}
        for key, value in effective_config.items():
            config_summary["ruff"][key] = value

        py_files = await get_python_files(path, file_patterns)
        if not py_files:
            return ProjectLintResult(
                issues=[],
                fixed_count=0,
                remaining_count=0,
                modified_files=[],
                project_path=str(path),
                has_ruff_config=has_ruff_config,
                config_source=config_source,
                config_summary=config_summary,
                files_summary={},
                fixed_issues=[],
                fixed_issues_summary={},
            )

        # Initial scan - find all issues before fixing
        initial_issues = await run_ruff_check(path, py_files, effective_config)
        total_issues_count = len(initial_issues)

        # Create a copy of initial issues for tracking
        remaining_issues_list = initial_issues.copy()
        fixed_issues_list = []
        modified_files = []

        # Only run the fixer if requested and there are issues to fix
        if fix and initial_issues:
            before_hashes = await get_file_hashes(path, py_files)

            # Run the auto-fix
            await run_ruff_fix(path, py_files, effective_config)

            # Check what's changed
            after_hashes = await get_file_hashes(path, py_files)
            modified_files = get_modified_files(before_hashes, after_hashes)

            # Get remaining issues after fixing
            remaining_issues_list = await run_ruff_check(path, py_files, effective_config)

            # Identify which issues were actually fixed
            fixed_issues_list = identify_fixed_issues(initial_issues, remaining_issues_list)

        # Calculate counts
        fixed_issues_count = len(fixed_issues_list)
        remaining_issues_count = len(remaining_issues_list)

        # Debug info
        print(f"DEBUG: Initial issues found: {total_issues_count}")
        print(f"DEBUG: Issues fixed: {fixed_issues_count}")
        print(f"DEBUG: Issues remaining: {remaining_issues_count}")

        # Sanity check
        expected_total = fixed_issues_count + remaining_issues_count
        if total_issues_count != expected_total:
            print(
                f"WARNING: Issue count mismatch - initial: {total_issues_count}, "
                f"calculated total: {expected_total} (fixed: {fixed_issues_count} + remaining: {remaining_issues_count})"
            )

            # Adjust total to match reality if needed
            if expected_total > total_issues_count:
                total_issues_count = expected_total
                print(f"Adjusted total issues count to {total_issues_count}")

        # Convert all paths to relative
        str_project_path = str(path)
        relative_remaining_issues = convert_issue_paths_to_relative(remaining_issues_list, str_project_path)
        relative_fixed_issues = convert_issue_paths_to_relative(fixed_issues_list, str_project_path)

        # Create summaries with relative paths
        fixed_summary = create_issues_summary(relative_fixed_issues, "fixed_types", "total_fixed")
        files_summary = create_issues_summary(relative_remaining_issues, "issue_types", "total_issues")

        # Convert all paths in summaries to relative
        relative_fixed_summary = convert_summary_paths_to_relative(fixed_summary, str_project_path)
        relative_files_summary = convert_summary_paths_to_relative(files_summary, str_project_path)

        print_final_report(
            total_issues_count,
            fixed_issues_count,
            remaining_issues_count,
            modified_files,
            relative_fixed_issues,
            relative_remaining_issues,
            relative_files_summary,
            relative_fixed_summary,
        )

        # Return the results with the correct counts and relative paths
        return ProjectLintResult(
            issues=relative_remaining_issues,
            fixed_count=fixed_issues_count,
            remaining_count=remaining_issues_count,
            modified_files=modified_files,
            project_path=str(path),
            has_ruff_config=has_ruff_config,
            config_source=config_source,
            config_summary=config_summary,
            files_summary=relative_files_summary,
            fixed_issues=relative_fixed_issues,
            fixed_issues_summary=relative_fixed_summary,
        )


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/reporter.py ===
from typing import Any, Dict, List


def create_issues_summary(issues: List[Dict[str, Any]], types_key: str, total_key: str) -> Dict[str, Dict[str, Any]]:
    """Create a summary of issues by file.

    Args:
        issues: List of issues to summarize
        types_key: Key to use for the types dictionary
        total_key: Key to use for the total count

    Returns:
        Dictionary mapping file paths to issue summaries
    """
    summary = {}
    for issue in issues:
        file_path = issue.get("file", "unknown")
        if file_path not in summary:
            summary[file_path] = {total_key: 0, types_key: {}}

        summary[file_path][total_key] += 1

        code = issue.get("code", "unknown")
        if code not in summary[file_path][types_key]:
            summary[file_path][types_key][code] = 0
        summary[file_path][types_key][code] += 1

    return summary


def identify_fixed_issues(
    initial_issues: List[Dict[str, Any]], remaining_issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Identify which issues were fixed by comparing initial and remaining issues.

    Args:
        initial_issues: List of issues found before fixing
        remaining_issues: List of issues found after fixing

    Returns:
        List of issues that were fixed
    """
    # Create a map of remaining issues for quick lookup
    # Use a more robust signature that takes into account file path and issue code
    # This fixes the problem where line numbers change due to code deletion
    remaining_map = {}
    for issue in remaining_issues:
        file_path = issue.get("file", "")
        code = issue.get("code", "")
        message = issue.get("message", "")

        # Create a composite key that identifies the issue type and content
        # but not its location (since that can change)
        key = f"{file_path}:{code}:{message}"

        if key not in remaining_map:
            remaining_map[key] = 0
        remaining_map[key] += 1

    # Find issues that were truly fixed (not just moved)
    fixed_issues = []
    for issue in initial_issues:
        file_path = issue.get("file", "")
        code = issue.get("code", "")
        message = issue.get("message", "")

        key = f"{file_path}:{code}:{message}"

        if key not in remaining_map or remaining_map[key] == 0:
            # This issue was completely fixed
            fixed_issues.append(issue)
        else:
            # This issue still exists, decrement the count
            remaining_map[key] -= 1

    return fixed_issues


def print_final_report(
    total_issue_count: int,
    fixed_count: int,
    remaining_count: int,
    modified_files: List[str],
    fixed_issues: List[Dict[str, Any]],
    remaining_issues: List[Dict[str, Any]],
    files_summary: Dict[str, Any],
    fixed_issues_summary: Dict[str, Any],
) -> None:
    """Print a comprehensive final report.

    Args:
        total_issue_count: Total number of issues found
        fixed_count: Number of issues fixed
        remaining_count: Number of issues remaining
        modified_files: List of files that were modified
        fixed_issues: List of issues that were fixed
        remaining_issues: List of issues remaining
        files_summary: Summary of remaining issues by file
        fixed_issues_summary: Summary of fixed issues by file
    """
    # Report on issues found, fixed, and remaining
    print(f"\nTotal issues found: {total_issue_count}")
    print(f"Fixed issues: {fixed_count}")
    print(f"Remaining issues: {remaining_count}")

    # Report on fixed issues
    if fixed_count > 0:
        print("\nFixed issues:")
        for issue in fixed_issues:
            file_path = issue.get("file", "unknown")
            code = issue.get("code", "unknown")
            message = issue.get("message", "unknown")
            line = issue.get("line", 0)
            column = issue.get("column", 0)
            print(f"- {file_path} (Line {line}, Col {column}): {code} - {message}")

        # Print summary by file
        if fixed_issues_summary:
            print("\nFixed issues by file:")
            for file_path, summary in fixed_issues_summary.items():
                print(f"- {file_path}: {summary.get('total_fixed', 0)} issues")
                if "fixed_types" in summary:
                    for code, count in summary["fixed_types"].items():
                        print(f"    {code}: {count}")

    # Report on remaining issues
    if remaining_count > 0:
        print("\nRemaining issues:")
        for issue in remaining_issues:
            file_path = issue.get("file", "unknown")
            code = issue.get("code", "unknown")
            message = issue.get("message", "unknown")
            line = issue.get("line", 0)
            column = issue.get("column", 0)
            print(f"- {file_path} (Line {line}, Col {column}): {code} - {message}")

        # Print summary by file
        if files_summary:
            print("\nRemaining issues by file:")
            for file_path, summary in files_summary.items():
                print(f"- {file_path}: {summary.get('total_issues', 0)} issues")
                if "issue_types" in summary:
                    for code, count in summary["issue_types"].items():
                        print(f"    {code}: {count}")

    # Report on modified files
    if modified_files:
        print("\nModified files:")
        for file in modified_files:
            print(f"- {file}")
    else:
        print("\nNo files were modified.")
        if fixed_count > 0:
            print("Note: Some issues were fixed in memory but changes were not written to disk.")
            print("This can happen with certain types of issues that the linter can detect but not automatically fix.")


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/runner.py ===
import asyncio
import glob
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


async def get_python_files(path: Path, patterns: Optional[List[str]] = None) -> List[str]:
    """Get a list of Python files to lint.

    Args:
        path: Project directory path
        file_patterns: Optional list of file patterns to include

    Returns:
        List of Python file paths
    """
    print(f"Looking for Python files in {path}")
    py_files = []

    if not patterns:
        patterns = ["**/*.py"]  # Default to all Python files
        print(f"No patterns provided, using default: {patterns}")
    else:
        print(f"Using provided patterns: {patterns}")

    # Use Python's glob to find files matching patterns
    for pattern in patterns:
        # Handle both absolute and relative paths in patterns
        if os.path.isabs(pattern):
            glob_pattern = pattern
        else:
            glob_pattern = os.path.join(str(path), pattern)

        print(f"Searching with glob pattern: {glob_pattern}")

        # Use glob.glob with recursive=True for ** patterns
        if "**" in pattern:
            matched_files = glob.glob(glob_pattern, recursive=True)
        else:
            matched_files = glob.glob(glob_pattern)

        # Convert to relative paths
        for file in matched_files:
            if file.endswith(".py"):
                try:
                    rel_path = os.path.relpath(file, str(path))
                    # Skip .venv directory and __pycache__
                    if not rel_path.startswith((".venv", "__pycache__")):
                        py_files.append(rel_path)
                except ValueError:
                    # This can happen if the file is on a different drive (Windows)
                    print(f"Skipping file not relative to project path: {file}")

    # Remove duplicates while preserving order
    unique_files = []
    seen = set()
    for file in py_files:
        if file not in seen:
            unique_files.append(file)
            seen.add(file)

    print(f"Found {len(unique_files)} Python files to lint")
    if len(unique_files) < 10:  # Only print all files if there are few
        print(f"Files to lint: {unique_files}")
    else:
        print(f"First 5 files: {unique_files[:5]}")

    return unique_files


async def run_ruff_check(path: Path, py_files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run Ruff in check mode (no fixing).

    Args:
        path: Project directory path
        py_files: List of Python files to check
        config: Configuration to use

    Returns:
        List of issues found
    """
    # Make sure we have files to check
    if not py_files:
        print("No Python files found to check")
        return []

    # Verify the files exist
    existing_files = []
    for file_path in py_files:
        full_path = path / file_path
        if full_path.exists():
            existing_files.append(file_path)

    if not existing_files:
        print(f"None of the specified Python files exist in {path}")
        return []

    py_files = existing_files
    print(f"Found {len(py_files)} Python files to check")

    # Build the command
    cmd = ["ruff", "check", "--output-format=json"]

    # Add configuration options
    if "select" in config:
        select_value = config["select"]
        if isinstance(select_value, list):
            select_str = ",".join(select_value)
        else:
            select_str = str(select_value)
        cmd.extend(["--select", select_str])

    if "ignore" in config and config["ignore"]:
        if isinstance(config["ignore"], list):
            ignore_str = ",".join(config["ignore"])
        else:
            ignore_str = str(config["ignore"])
        cmd.extend(["--ignore", ignore_str])

    if "line-length" in config:
        cmd.extend(["--line-length", str(config["line-length"])])

    # Add files to check
    cmd.extend(py_files)

    try:
        # Now run the actual check command
        print(f"Running ruff command: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_bytes, stderr_bytes = await proc.communicate()

        stdout_text = stdout_bytes.decode().strip() if stdout_bytes else ""
        stderr_text = stderr_bytes.decode().strip() if stderr_bytes else ""

        if proc.returncode != 0 and stderr_text:
            print(f"Ruff command failed with exit code {proc.returncode}: {stderr_text}")
            # Continue processing anyway - non-zero could just mean issues were found

        issues = []

        # Only try to parse JSON if we actually have output
        if stdout_text:
            try:
                json_data = json.loads(stdout_text)
                print(f"Ruff found {len(json_data)} issues")

                for item in json_data:
                    try:
                        # Get location data with proper null handling
                        location = item.get("location") or {}
                        row = location.get("row", 0) if isinstance(location, dict) else 0
                        column = location.get("column", 0) if isinstance(location, dict) else 0

                        # Get fix data with proper null handling
                        fix_data = item.get("fix") or {}
                        fix_applicable = (
                            fix_data.get("applicability", "") == "applicable" if isinstance(fix_data, dict) else False
                        )

                        # Create issue object
                        issues.append({
                            "file": item.get("filename", ""),
                            "line": row,
                            "column": column,
                            "code": item.get("code", ""),
                            "message": item.get("message", ""),
                            "fix_available": fix_applicable,
                        })
                    except Exception as e:
                        print(f"Error processing ruff issue: {e}")
                        # Skip issues we can't parse properly
                        continue
            except json.JSONDecodeError as e:
                print(f"Failed to parse Ruff JSON output: {e}")
                print(f"Raw output: {stdout_text[:200]}...")  # Print first 200 chars
                return []

        return issues

    except Exception as e:
        print(f"Error running Ruff check: {e}")
        return []


async def run_ruff_fix(path: Path, py_files: List[str], config: Dict[str, Any]) -> bool:
    """Run Ruff in fix mode.

    Args:
        path: Project directory path
        py_files: List of Python files to fix
        config: Configuration to use

    Returns:
        True if fixing succeeded, False otherwise
    """
    # Make sure we have files to check
    if not py_files:
        return False

    # Verify the files exist
    existing_files = []
    for file_path in py_files:
        full_path = path / file_path
        if full_path.exists():
            existing_files.append(file_path)

    if not existing_files:
        return False

    py_files = existing_files

    # Build the command
    cmd = ["ruff", "check", "--fix"]

    # Add configuration options
    if "select" in config:
        select_value = config["select"]
        if isinstance(select_value, list):
            select_str = ",".join(select_value)
        else:
            select_str = str(select_value)
        cmd.extend(["--select", select_str])

    if "ignore" in config and config["ignore"]:
        if isinstance(config["ignore"], list):
            ignore_str = ",".join(config["ignore"])
        else:
            ignore_str = str(config["ignore"])
        cmd.extend(["--ignore", ignore_str])

    if "line-length" in config:
        cmd.extend(["--line-length", str(config["line-length"])])

    # Add files to fix
    cmd.extend(py_files)

    try:
        proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await proc.communicate()

        return proc.returncode == 0

    except Exception:
        return False


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/snippet.py ===
"""Ruff linter implementation for single code snippets."""

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional

from python_code_tools.linters.base import CodeLinter, CodeLintResult
from python_code_tools.utils.temp_file import cleanup_temp_file, create_temp_file


class RuffLinter(CodeLinter):
    """Code linter implementation using Ruff."""

    def __init__(self, **kwargs) -> None:
        """Initialize the Ruff linter.

        Args:
            **kwargs: Additional configuration options for Ruff
        """
        super().__init__(name="ruff", **kwargs)

    async def lint_code(self, code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> CodeLintResult:
        """Lint code using Ruff and return the results.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for Ruff

        Returns:
            A CodeLintResult object containing the fixed code and issue details
        """
        temp_file, file_path = create_temp_file(code, suffix=".py")

        try:
            # First, get original issues (before fixing)
            # Convert Path to string for _get_issues
            initial_issues = await self._get_issues(str(file_path), config)
            initial_count = len(initial_issues)

            print(f"Initial scan found {initial_count} issues")

            # Keep a copy of the original code
            with open(file_path, "r") as f:
                original_code = f.read()

            # Only try to fix if requested and there are issues
            fixed_code = original_code
            remaining_issues = initial_issues
            if fix and initial_count > 0:
                # Run ruff with --fix flag - convert Path to string
                fix_success = await self._run_fix(str(file_path), config)

                if fix_success:
                    # Read the fixed code
                    with open(file_path, "r") as f:
                        fixed_code = f.read()

                    # Get remaining issues after fixing - convert Path to string
                    remaining_issues = await self._get_issues(str(file_path), config)

                print(f"After fixing, {len(remaining_issues)} issues remain")

            # Calculate fixed count
            fixed_count = initial_count - len(remaining_issues)
            remaining_count = len(remaining_issues)

            # Debug info
            print(f"DEBUG: Initial issues: {initial_count}")
            print(f"DEBUG: Fixed issues: {fixed_count}")
            print(f"DEBUG: Remaining issues: {remaining_count}")

            return CodeLintResult(
                fixed_code=fixed_code,
                issues=remaining_issues,
                fixed_count=fixed_count,
                remaining_count=remaining_count,
            )

        finally:
            # Clean up temporary file
            cleanup_temp_file(temp_file, file_path)

    async def _get_issues(self, file_path: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get issues from a file using ruff check with JSON output.

        Args:
            file_path: Path to the Python file
            config: Optional configuration settings for Ruff

        Returns:
            List of issues found
        """
        # Build the ruff command for check only (no fixing)
        cmd = ["ruff", "check", file_path, "--output-format=json"]

        # Add config options if provided
        if config:
            for key, value in config.items():
                if key == "select":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--select", value_str])
                elif key == "ignore":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--ignore", value_str])
                elif key == "line-length":
                    cmd.extend(["--line-length", str(value)])

        try:
            # Run the command
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await proc.communicate()

            stdout_text = stdout.decode().strip() if stdout else ""
            stderr_text = stderr.decode().strip() if stderr else ""

            if stderr_text:
                print(f"WARNING: Ruff stderr: {stderr_text}")

            issues = []

            # Parse JSON output if available
            if stdout_text:
                try:
                    data = json.loads(stdout_text)

                    for item in data:
                        # Extract location data
                        location = item.get("location") or {}
                        row = location.get("row", 0) if isinstance(location, dict) else 0
                        column = location.get("column", 0) if isinstance(location, dict) else 0

                        # Extract fix data
                        fix_data = item.get("fix") or {}
                        fix_applicable = (
                            fix_data.get("applicability", "") == "applicable" if isinstance(fix_data, dict) else False
                        )

                        # Create issue object
                        issues.append({
                            "line": row,
                            "column": column,
                            "code": item.get("code", ""),
                            "message": item.get("message", ""),
                            "fix_available": fix_applicable,
                        })
                except json.JSONDecodeError as e:
                    print(f"ERROR: Failed to parse JSON output: {e}")
                    print(f"Raw output: {stdout_text[:200]}...")

            return issues

        except Exception as e:
            print(f"ERROR: Failed to run ruff check: {e}")
            return []

    async def _run_fix(self, file_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Run ruff with --fix flag to automatically fix issues.

        Args:
            file_path: Path to the Python file
            config: Optional configuration settings for Ruff

        Returns:
            True if fixing succeeded, False otherwise
        """
        # Build the ruff command for fixing
        cmd = ["ruff", "check", file_path, "--fix"]

        # Add config options if provided
        if config:
            for key, value in config.items():
                if key == "select":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--select", value_str])
                elif key == "ignore":
                    value_str = ",".join(value) if isinstance(value, list) else value
                    cmd.extend(["--ignore", value_str])
                elif key == "line-length":
                    cmd.extend(["--line-length", str(value)])

        try:
            # Run the command
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await proc.communicate()

            stderr_text = stderr.decode().strip() if stderr else ""
            if stderr_text:
                print(f"WARNING: Ruff fix stderr: {stderr_text}")

            return proc.returncode == 0

        except Exception as e:
            print(f"ERROR: Failed to run ruff fix: {e}")
            return False


=== File: mcp-servers/python-code-tools/python_code_tools/linters/ruff/utils.py ===
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List


async def get_file_hashes(path: Path, file_paths: List[str]) -> Dict[str, str]:
    """Get MD5 hashes of files for change detection.

    Args:
        path: Project directory path
        file_paths: List of file paths

    Returns:
        Dictionary mapping file paths to MD5 hashes
    """

    hashes = {}

    for file_path in file_paths:
        abs_path = path / file_path
        try:
            with open(abs_path, "rb") as f:
                content = f.read()
                hashes[file_path] = hashlib.md5(content).hexdigest()
        except Exception:
            # Skip files we can't read
            pass

    return hashes


def get_modified_files(before_hashes: Dict[str, str], after_hashes: Dict[str, str]) -> List[str]:
    """Determine which files were modified by comparing hashes.

    Args:
        before_hashes: File hashes before modification
        after_hashes: File hashes after modification

    Returns:
        List of modified file paths
    """
    modified_files = []

    for file_path, before_hash in before_hashes.items():
        if file_path in after_hashes:
            after_hash = after_hashes[file_path]
            if before_hash != after_hash:
                modified_files.append(file_path)

    return modified_files


def make_path_relative(file_path: str, project_path: str) -> str:
    """Convert absolute paths to project-relative paths.

    Args:
        file_path: Absolute or relative file path
        project_path: Base project path

    Returns:
        Path relative to the project directory
    """
    try:
        # If it's already a relative path, return it
        if not os.path.isabs(file_path):
            return file_path

        # Convert absolute path to relative path
        rel_path = os.path.relpath(file_path, project_path)

        # Remove leading ./ if present
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]

        return rel_path
    except Exception:
        # If any error occurs, return the original path
        return file_path


def convert_issue_paths_to_relative(issues: List[Dict[str, Any]], project_path: str) -> List[Dict[str, Any]]:
    """Convert all file paths in issues to be relative to the project path.

    Args:
        issues: List of issue dictionaries
        project_path: Base project path

    Returns:
        List of issues with relative paths
    """
    relative_issues = []
    for issue in issues:
        # Create a copy of the issue
        relative_issue = issue.copy()

        # Convert the file path if present
        if "file" in relative_issue:
            relative_issue["file"] = make_path_relative(relative_issue["file"], project_path)

        relative_issues.append(relative_issue)

    return relative_issues


def convert_summary_paths_to_relative(
    summary: Dict[str, Dict[str, Any]], project_path: str
) -> Dict[str, Dict[str, Any]]:
    """Convert all file paths in a summary dictionary to be relative to the project path.

    Args:
        summary: Dictionary of file paths to summaries
        project_path: Base project path

    Returns:
        Summary dictionary with relative paths
    """
    relative_summary = {}
    for file_path, data in summary.items():
        relative_path = make_path_relative(file_path, project_path)
        relative_summary[relative_path] = data

    return relative_summary


=== File: mcp-servers/python-code-tools/python_code_tools/server.py ===
"""MCP server implementation for Python code tools."""

import argparse
import sys
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from python_code_tools.linters import RuffLinter, RuffProjectLinter


def create_mcp_server(host: str = "localhost", port: int = 3001) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        host: The hostname for the SSE server
        port: The port for the SSE server

    Returns:
        A configured FastMCP server instance
    """
    # Initialize FastMCP server with settings for SSE transport
    mcp = FastMCP("Python Code Tools", host=host, port=port, debug=False, log_level="INFO")

    # Initialize the linters
    ruff_linter = RuffLinter()
    project_linter = RuffProjectLinter()

    @mcp.tool()
    async def lint_code(code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Lint Python code and optionally fix issues.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing the fixed code, issues found, and fix counts
        """
        result = await ruff_linter.lint_code(code, fix, config)
        return result.model_dump()

    @mcp.tool()
    async def lint_project(
        project_path: str,
        file_patterns: Optional[List[str]] = None,
        fix: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Lint a Python project directory and optionally fix issues.

        Args:
            project_path: Path to the project directory
            file_patterns: Optional list of file patterns to include (e.g., ["*.py", "src/**/*.py"])
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing issues found, fix counts, and modified files
        """
        try:
            result = await project_linter.lint_project(project_path, file_patterns, fix, config)
            # Explicitly convert to dict to ensure proper serialization
            return result.model_dump()
        except Exception as e:
            # Return a structured error response instead of letting the exception bubble up
            return {
                "error": str(e),
                "project_path": project_path,
                "issues": [],
                "fixed_count": 0,
                "remaining_count": 0,
                "modified_files": [],
            }

    return mcp


def main() -> int:
    """Main entry point for the server CLI.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Python Code Tools MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port for SSE server (default: 3001)",
    )

    args = parser.parse_args()

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Python Code Tools MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# For importing in other modules
mcp = create_mcp_server()

if __name__ == "__main__":
    sys.exit(main())


=== File: mcp-servers/python-code-tools/python_code_tools/utils/__init__.py ===
"""Utility functions for Python Code Tools."""

from python_code_tools.utils.temp_file import cleanup_temp_file, create_temp_file

__all__ = ["create_temp_file", "cleanup_temp_file"]


=== File: mcp-servers/python-code-tools/python_code_tools/utils/temp_file.py ===
"""Temporary file handling utilities."""

import os
import tempfile
from pathlib import Path
from typing import IO, Any, Tuple


def create_temp_file(content: str, suffix: str = ".txt") -> Tuple[IO[Any], Path]:
    """Create a temporary file with the given content.

    Args:
        content: The content to write to the file
        suffix: The file suffix/extension

    Returns:
        A tuple containing the temporary file object and the path to the file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file_path = Path(temp_file.name)

    with open(file_path, "w") as f:
        f.write(content)

    return temp_file, file_path


def cleanup_temp_file(temp_file: IO[Any], file_path: Path) -> None:
    """Clean up a temporary file.

    Args:
        temp_file: The temporary file object
        file_path: The path to the file
    """
    temp_file.close()
    if os.path.exists(file_path):
        os.unlink(file_path)


=== File: mcp-servers/python-code-tools/tests/__init__.py ===
# Test package for python-code-tools MCP server


=== File: mcp-servers/python-code-tools/tests/test_placeholder.py ===
"""Placeholder test to prevent 'no tests ran' error."""


def test_placeholder():
    """Placeholder test - replace with actual tests."""
    assert True


