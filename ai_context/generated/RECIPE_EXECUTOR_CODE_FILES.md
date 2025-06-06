# recipe-executor/recipe_executor

[collect-files]

**Search:** ['recipe-executor/recipe_executor']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** ['README.md', 'pyproject.toml', '.env.example']
**Date:** 6/6/2025, 3:45:22 PM
**Files:** 29

=== File: .env.example ===
# Optional for the project
#LOG_LEVEL=DEBUG

# Required for the project
OPENAI_API_KEY=

# Additional APIs
#ANTHROPIC_API_KEY=
#GEMINI_API_KEY=

# Azure OpenAI
#AZURE_OPENAI_BASE_URL=
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_USE_MANAGED_IDENTITY=false
#AZURE_OPENAI_API_KEY=

#(Optional) The client ID of the specific managed identity to use.
#  If not provided, DefaultAzureCredential will be used.
#AZURE_MANAGED_IDENTITY_CLIENT_ID=


=== File: README.md ===
# Recipe Tool

**Turn natural language ideas into reliable, automated workflows** - Recipe Tool transforms your ideas written in plain English into executable "recipes" that orchestrate complex multi-step workflows. Write what you want to accomplish, and Recipe Tool generates the JSON recipe that makes it happen - reproducibly and reliably.

**NOTE** This project is a very early, experimental project that is being explored in the open. There is no support offered and it will include frequent breaking changes. This project may be abandoned at any time. If you find it useful, it is strongly encouraged to create a fork and remain on a commit that works for your needs unless you are willing to make the necessary changes to use the latest version. This project is currently **NOT** accepting contributions and suggestions; please see the [docs/dev_guidance.md](docs/dev_guidance.md) for more details.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## From Ideas to Automated Workflows

Recipe Tool bridges the gap between natural language and automation:

1. **Start with an idea** - Write what you want in plain English/markdown
2. **Generate a recipe** - Recipe Tool creates a JSON workflow from your description
3. **Execute reliably** - The JSON recipe runs deterministically, combining LLM calls with structured logic

Think of recipes as the "compiled" version of your ideas - they capture your intent in a format that executes reliably every time, using "more code than model" for reproducible results.

## What are Recipes?

Under the hood, recipes are JSON files that define automated workflows. Each recipe contains:

- **Steps** that execute in sequence (or in parallel)
- **Context** that flows between steps, accumulating results
- **Templates** using Liquid syntax for dynamic content
- **Rich step types**: LLM generation, file I/O, tool calls, conditionals, loops, sub-recipes

Here's what gets generated when you ask to "read a file and create a summary":

```json
{
  "name": "summarize_file",
  "steps": [
    {
      "step_type": "read_files",
      "paths": ["{{ input }}"]
    },
    {
      "step_type": "llm_generate",
      "prompt": "Summarize this content:\n\n{{ file_contents[0] }}"
    },
    {
      "step_type": "write_files",
      "files": [
        {
          "path": "summary.md",
          "content": "{{ llm_output }}"
        }
      ]
    }
  ]
}
```

Example use cases:

- 📝 Generate complete documents from outlines
- 🔧 Transform natural language ideas into executable recipes
- 💻 Generate code from specifications (this project generates its own code!)
- 🔄 Automate complex multi-step workflows
- 🤖 Create AI-powered automation pipelines

## Quick Start

```bash
# Clone and install
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool
make install

# Try an example recipe
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/hello-world-spec.txt
```

See more examples in [recipes](recipes/) directory.

## Architecture

The system is built as a layered architecture where each layer adds capabilities:

```mermaid
graph TD
    subgraph "User Interfaces"
        UI1[Document Generator App]
        UI2[Recipe Executor App]
        UI3[Recipe Tool App]
    end

    subgraph "CLI Layer"
        CLI[Recipe Tool<br/>creation + execution]
    end

    subgraph "Core Engine"
        RE[Recipe Executor<br/>pure execution engine]
    end

    subgraph "Recipe Step Types"
        ST1[LLM Generate]
        ST2[Read/Write Files]
        ST3[MCP Tool Calls]
        ST4[Execute Sub-Recipe]
        ST5[Set Context]
    end

    subgraph "External Services"
        MCP1[Any MCP Server]
        LLM[LLM APIs]
    end

    UI1 --> CLI
    UI2 --> RE
    UI3 --> CLI
    CLI --> RE

    RE --> ST1
    RE --> ST2
    RE --> ST3
    RE --> ST4
    RE --> ST5

    ST3 -.->|calls| MCP1
    ST1 -.->|calls| LLM

    style RE stroke:#f0f,stroke-width:4px
    style CLI stroke:#00f,stroke-width:3px
```

### Self-Generating Architecture

The Recipe Executor's code is entirely generated from markdown blueprints using the codebase generator recipe. This "self-hosting" demonstrates the framework's power - it can build itself!

```mermaid
graph LR
    B[Blueprints<br/>markdown specs] -->|codebase generator<br/>recipe| C[Recipe Executor<br/>source code]
    C -->|executes| B

    style C stroke:#f0f,stroke-width:4px
```

## Core Components

### Execution Layer

- **Recipe Executor** (`recipe-executor/`) - Pure execution engine for JSON recipes. This is the foundation that executes recipe steps including LLM calls, file operations, and flow control.
- **Recipe Tool** (`recipe-tool/`) - Adds recipe creation capabilities on top of Recipe Executor. Can generate new recipes from natural language descriptions.

### User Interfaces

- **Document Generator App** (`apps/document-generator/`) - Specialized UI for document creation workflows with live preview
- **Recipe Executor App** (`apps/recipe-executor/`) - Debug-focused interface for recipe execution with step-by-step visibility
- **Recipe Tool App** (`apps/recipe-tool/`) - Full-featured UI combining recipe creation and execution with MCP server integration

### MCP Servers

These servers expose functionality via the Model Context Protocol:

- **Recipe Tool MCP Server** (`mcp-servers/recipe-tool/`) - Exposes the recipe-tool CLI functionality (execute/create) as MCP tools for AI assistants
- **Python Code Tools MCP** (`mcp-servers/python-code-tools/`) - Provides Python linting capabilities using Ruff for AI assistants to lint code snippets or entire projects

## Installation

### Prerequisites

- **`make`** - Build automation tool ([install guide](https://www.gnu.org/software/make/))
- **`uv`** - Python dependency management ([install guide](https://github.com/astral-sh/uv))
- **`GitHub CLI`** - For ai-context-files tool ([install guide](https://cli.github.com/))
- **Azure CLI** (optional) - For Azure OpenAI with Managed Identity ([install guide](https://docs.microsoft.com/cli/azure/install-azure-cli))

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool

# 2. Configure environment (optional)
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY and other API keys

# 3. Install all dependencies
make install

# 4. Activate virtual environment
source .venv/bin/activate    # Linux/Mac
# OR: .venv\Scripts\activate  # Windows

# 5. Verify installation
recipe-tool --help
```

## Usage Guide

### Basic Workflow

1. **Write your idea** in natural language (markdown file):

```markdown
# Analyze Code Quality

Read all Python files in the project and:

1. Count lines of code per file
2. Identify files with no docstrings
3. Create a report with recommendations
```

2. **Generate a recipe** from your idea:

```bash
recipe-tool --create code_quality_idea.md
# Creates: output/analyze_code_quality.json
```

3. **Execute the recipe** (now it's reproducible!):

```bash
recipe-tool --execute output/analyze_code_quality.json project_path=./myproject
```

### Direct Execution

If you already have JSON recipes:

```bash
# Execute with context variables
recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/gpt-4o
```

### Web Interfaces

For a more visual experience:

```bash
recipe-tool-app          # Full UI for creation and execution
recipe-executor-app      # Debug-focused execution UI
document-generator-app   # Document workflow UI
```

### Advanced Workflows

#### Code Generation from Blueprints

The Recipe Executor generates its own code:

```bash
# Generate all Recipe Executor code
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json

# Generate specific component
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   component_id=steps.llm_generate
```

#### Document Generation

Create structured documents from outlines:

```bash
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline=path/to/outline.json
```

#### MCP Server Integration

For AI assistants (Claude Desktop, etc.):

```bash
# Recipe capabilities via MCP
recipe-tool-mcp-server stdio              # For Claude Desktop
recipe-tool-mcp-server sse --port 3002    # For HTTP clients

# Python linting via MCP
python-code-tools stdio
```

## Recipe Catalog

### 🔨 Code Generation Recipes

- **Codebase Generator** (`recipes/codebase_generator/`) - Transforms markdown blueprints into working code

  - Used to generate the Recipe Executor itself!
  - Sub-recipes for component processing and code generation

- **Blueprint Generators** (`recipes/experimental/blueprint_generator_v*/`) - Creates blueprints from ideas
  - Multiple versions exploring different approaches
  - Generates component specifications and documentation

### 📄 Document Creation Recipes

- **Document Generator** (`recipes/document_generator/`) - Creates documents from structured outlines
  - Handles multi-section documents with resource loading
  - Supports markdown output with live preview in UI

### 🛠️ Utility Recipes

- **Recipe Creator** (`recipes/recipe_creator/`) - Generates recipes from natural language descriptions

  - Core functionality of the recipe-tool CLI
  - Analyzes ideas and creates executable JSON recipes

- **File Generation** (`recipes/utilities/`) - Various file processing utilities
  - Generate content from file collections
  - Template-based file creation

### 📚 Example Recipes

- **Simple Examples** (`recipes/example_simple/`) - Basic recipe patterns
- **Complex Examples** (`recipes/example_complex/`) - Advanced workflows with sub-recipes
- **Template Examples** (`recipes/example_templates/`) - Using Liquid templates
- **MCP Examples** (`recipes/example_mcp_step/`) - MCP server integration
- **Content Writer** (`recipes/example_content_writer/`) - LLM content generation

## Development

### Getting Started

```bash
# Workspace commands
make help              # Show all available commands
make workspace-info    # Show project structure
make doctor           # Check workspace health

# Code quality
make lint             # Run linting
make format           # Format code
make test             # Run tests

# AI development
make ai-context-files # Generate context for AI assistants
```

### VSCode Integration

The project includes a comprehensive VSCode workspace configuration:

- Multi-root workspace organized by project type
- Pre-configured Python paths and testing
- Ruff integration for code quality
- Recommended extensions

```bash
code recipe-tool-workspace.code-workspace
```

### Self-Generating Code

The Recipe Executor generates its own code from blueprints:

1. **Write blueprints** in `blueprints/recipe_executor/components/`
2. **Run generator** `recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json`
3. **Code is generated** in `recipe-executor/`

This demonstrates the power of the modular approach - the tool builds itself!

## Philosophy & Design

This project embodies a modular, AI-driven approach to software development:

- **Modular Design**: Small, self-contained components with clear interfaces
- **AI-First Development**: Components are generated from specifications
- **Regeneration over Editing**: Prefer regenerating components to manual edits
- **Human as Architect**: Humans design specifications, AI builds the code

See [ai_context/MODULAR_DESIGN_PHILOSOPHY.md](ai_context/MODULAR_DESIGN_PHILOSOPHY.md) and [ai_context/IMPLEMENTATION_PHILOSOPHY.md](ai_context/IMPLEMENTATION_PHILOSOPHY.md) for detailed philosophy.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

This project is currently **NOT** accepting contributions and suggestions; please see the [dev_guidance.md](docs/dev_guidance.md) for more details.

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.


=== File: pyproject.toml ===
[tool.uv.workspace]
members = [
    "recipe-tool",
    "recipe-executor",
    "apps/document-generator",
    "apps/recipe-executor",
    "apps/recipe-tool",
    "mcp-servers/docs-server",
    "mcp-servers/python-code-tools",
    "mcp-servers/recipe-tool",
]

[tool.uv.sources]
# Core libraries
recipe-executor = { workspace = true }
recipe-tool = { workspace = true }
# Apps
document-generator-app = { workspace = true }
recipe-executor-app = { workspace = true }
recipe-tool-app = { workspace = true }
# MCP servers
docs-server = { workspace = true }
python-code-tools = { workspace = true }
recipe-tool-mcp-server = { workspace = true }

[dependency-groups]
dev = [
    "build>=1.2.2.post1",
    "debugpy>=1.8.14",
    "pyright>=1.1.400",
    "pytest>=8.3.5",
    "pytest-cov>=6.1.1",
    "pytest-mock>=3.14.0",
    "ruff>=0.11.10",
    "twine>=6.1.0",
]


=== File: recipe-executor/recipe_executor/.DS_Store ===
[ERROR reading file: 'utf-8' codec can't decode byte 0x86 in position 23: invalid start byte]


=== File: recipe-executor/recipe_executor/context.py ===
# This file was generated by Codebase-Generator, do not edit directly
from typing import Any, Dict, Iterator, Optional
import copy
import json

from recipe_executor.protocols import ContextProtocol

__all__ = ["Context"]


class Context(ContextProtocol):
    """
    Context is a shared state container for the Recipe Executor system.
    It provides a dictionary-like interface for runtime artifacts and
    holds a separate configuration store.
    """

    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Deep copy initial data to avoid side effects from external modifications
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self._config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        try:
            return self._artifacts[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        # Let KeyError propagate naturally if key is missing
        del self._artifacts[key]

    def __contains__(self, key: object) -> bool:
        # Only string keys are valid artifact keys
        return isinstance(key, str) and key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Iterate over a snapshot of keys to prevent issues during mutation
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.
        """
        return self.__iter__()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value for key if present, otherwise return default.
        """
        return self._artifacts.get(key, default)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of this Context, including artifacts and config.
        """
        # __init__ will deep-copy the provided dicts
        return Context(artifacts=self._artifacts, config=self._config)

    def dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts as a standard dict.
        """
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        """
        Return a JSON string representation of the artifacts.
        """
        return json.dumps(self.dict())

    def get_config(self) -> Dict[str, Any]:
        """
        Return a deep copy of the configuration store.
        """
        return copy.deepcopy(self._config)

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Replace the configuration store with a deep copy of the provided dict.
        """
        self._config = copy.deepcopy(config)


=== File: recipe-executor/recipe_executor/executor.py ===
# This file was generated by Codebase-Generator, do not edit directly

import os
import json
import inspect
import logging
from pathlib import Path
from typing import Union, Dict, Any

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.models import Recipe
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Concrete implementation of ExecutorProtocol. Loads, validates, and executes
    recipes step by step using a shared context. Stateless between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load a recipe (from file path, JSON string, dict, or Recipe model),
        validate it, and execute its steps sequentially using the provided context.
        """
        # Determine how to load the recipe
        if isinstance(recipe, Recipe):
            self.logger.debug("Using provided Recipe model instance.")
            recipe_model = recipe

        elif isinstance(recipe, Path):
            path_str = str(recipe)
            if not recipe.exists():
                raise ValueError(f"Recipe file not found: {path_str}")
            self.logger.debug(f"Loading recipe from file path: {path_str}")
            try:
                raw = recipe.read_text(encoding="utf-8")
                data = json.loads(raw)
            except Exception as e:
                raise ValueError(f"Failed to read or parse recipe file {path_str}: {e}") from e
            try:
                recipe_model = Recipe.model_validate(data)
            except Exception as e:
                raise ValueError(f"Invalid recipe structure from file {path_str}: {e}") from e

        elif isinstance(recipe, str):
            if os.path.isfile(recipe):
                self.logger.debug(f"Loading recipe from file path: {recipe}")
                try:
                    raw = Path(recipe).read_text(encoding="utf-8")
                    data = json.loads(raw)
                except Exception as e:
                    raise ValueError(f"Failed to read or parse recipe file {recipe}: {e}") from e
                try:
                    recipe_model = Recipe.model_validate(data)
                except Exception as e:
                    raise ValueError(f"Invalid recipe structure from file {recipe}: {e}") from e
            else:
                self.logger.debug("Loading recipe from JSON string.")
                try:
                    data = json.loads(recipe)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON string: {e}") from e
                try:
                    recipe_model = Recipe.model_validate(data)
                except Exception as e:
                    raise ValueError(f"Invalid recipe structure from JSON string: {e}") from e

        elif isinstance(recipe, dict):
            self.logger.debug("Loading recipe from dict.")
            try:
                recipe_model = Recipe.model_validate(recipe)
            except Exception as e:
                raise ValueError(f"Invalid recipe structure: {e}") from e

        else:
            raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Log recipe summary and step count
        try:
            summary = recipe_model.model_dump()
        except Exception:
            summary = {}
        step_count = len(getattr(recipe_model, "steps", []))
        self.logger.debug(f"Recipe loaded: {summary}. Steps count: {step_count}")

        # Execute each step in order
        for idx, step in enumerate(recipe_model.steps):  # type: ignore
            step_type = step.type
            config = step.config or {}
            self.logger.debug(f"Executing step {idx} of type '{step_type}' with config: {config}")

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_cls = STEP_REGISTRY[step_type]
            step_instance = step_cls(self.logger, config)

            try:
                result = step_instance.execute(context)
                if inspect.isawaitable(result):  # type: ignore
                    await result
            except Exception as e:
                msg = f"Error executing step {idx} ('{step_type}'): {e}"
                raise ValueError(msg) from e

            self.logger.debug(f"Step {idx} ('{step_type}') completed successfully.")

        self.logger.debug("All recipe steps completed successfully.")


=== File: recipe-executor/recipe_executor/llm_utils/azure_openai.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Provides a PydanticAI-compatible OpenAIModel instance for Azure OpenAI, handling
authentication via API key or Azure Identity.
"""

import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def _mask_secret(secret: Optional[str]) -> str:
    """
    Mask a secret, showing only the first and last character.
    """
    if not secret:
        return "<None>"
    if len(secret) <= 2:
        return "**"
    return f"{secret[0]}***{secret[-1]}"


def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance for Azure OpenAI, configured via environment variables.

    Args:
        logger (logging.Logger): Logger for messages.
        model_name (str): Model name, e.g. "gpt-4o".
        deployment_name (Optional[str]): Azure deployment name; if not provided, uses env var or model_name.

    Returns:
        OpenAIModel: Configured OpenAIModel instance.

    Raises:
        Exception: On missing configuration or client/model creation errors.
    """
    # Load environment configuration
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("1", "true", "yes")
    azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_client_id = os.getenv("AZURE_CLIENT_ID")

    if not azure_endpoint:
        logger.error("Environment variable AZURE_OPENAI_BASE_URL is required")
        raise Exception("Missing AZURE_OPENAI_BASE_URL")

    # Determine deployment name
    deployment = deployment_name or env_deployment or model_name

    # Log configuration (mask sensitive values)
    masked_key = _mask_secret(os.getenv("AZURE_OPENAI_API_KEY"))
    logger.debug(
        f"Azure OpenAI config: endpoint={azure_endpoint}, api_version={azure_api_version},"
        f" deployment={deployment}, use_managed_identity={use_managed_identity},"
        f" client_id={azure_client_id or '<None>'}, api_key={masked_key}"
    )

    # Create the Azure OpenAI client
    try:
        if use_managed_identity:
            logger.info("Using Azure Managed Identity for authentication")
            if azure_client_id:
                credential = ManagedIdentityCredential(client_id=azure_client_id)
            else:
                credential = DefaultAzureCredential()

            token_provider = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default",
            )
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "Azure Managed Identity"
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                logger.error("Environment variable AZURE_OPENAI_API_KEY is required for API key authentication")
                raise Exception("Missing AZURE_OPENAI_API_KEY")
            logger.info("Using API key authentication for Azure OpenAI")
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "API Key"
    except Exception as err:
        logger.error(f"Failed to create AsyncAzureOpenAI client: {err}")
        raise

    # Wrap in PydanticAI provider and model
    logger.info(f"Creating Azure OpenAI model '{model_name}' with {auth_method}")
    provider = OpenAIProvider(openai_client=azure_client)
    try:
        model = OpenAIModel(model_name=model_name, provider=provider)
    except Exception as err:
        logger.error(f"Failed to create OpenAIModel: {err}")
        raise

    return model


=== File: recipe-executor/recipe_executor/llm_utils/azure_responses.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Azure Responses component for Recipe Executor
Provides PydanticAI wrapper for Azure OpenAI Responses API models.
Handles authentication (API key or Managed Identity) and model initialization.
"""

import os
import logging
from typing import Optional

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)


def _mask_key(key: str) -> str:
    """Mask all but first and last character of a secret key."""
    if not key:
        return ""
    if len(key) <= 2:
        return "*" * len(key)
    return f"{key[0]}{'*' * (len(key) - 2)}{key[-1]}"


def create_azure_responses_model(
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIResponsesModel:
    """
    Create a configured OpenAIResponsesModel for Azure OpenAI.

    Args:
        model_name: Name of the underlying model or alias.
        deployment_name: Optional override for the Azure deployment name.

    Returns:
        Configured OpenAIResponsesModel using Azure authentication.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    # Determine authentication method
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").strip().lower() in ("true", "1", "yes")

    # Required endpoint configuration
    base_url = os.getenv("AZURE_OPENAI_BASE_URL")
    if not base_url:
        raise ValueError("AZURE_OPENAI_BASE_URL environment variable is required for Azure OpenAI endpoint")

    # API version
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview").strip()

    # Optional API key
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    # Determine deployment name
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    final_deployment = deployment_name or env_deployment or model_name

    # Debug log loaded configuration (mask secrets)
    masked_key = _mask_key(api_key) if api_key else None
    logger.debug(
        "Azure Responses config: use_managed_identity=%s, base_url=%s, api_version=%s, deployment_name=%s, api_key=%s",
        use_managed_identity,
        base_url,
        api_version,
        final_deployment,
        masked_key,
    )

    try:
        # Initialize Azure OpenAI client
        if use_managed_identity:
            # Use Azure AD Managed Identity
            client_id = os.getenv("AZURE_CLIENT_ID")
            # DefaultAzureCredential picks up client ID from env if provided,
            # but we pass explicitly if present
            if client_id:
                credential = DefaultAzureCredential(managed_identity_client_id=client_id)
            else:
                credential = DefaultAzureCredential()
            # Scope for Azure Cognitive Services
            scope = "https://cognitiveservices.azure.com/.default"
            token_provider = get_bearer_token_provider(credential, scope)
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=base_url,
                api_version=api_version,
                azure_ad_token_provider=token_provider,
            )
            auth_method = "managed_identity"
        else:
            # API key authentication
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY environment variable is required for API key authentication")
            azure_client = AsyncAzureOpenAI(
                azure_endpoint=base_url,
                api_version=api_version,
                api_key=api_key,
            )
            auth_method = "api_key"

        logger.info(
            "Authenticated Azure OpenAI client using %s for deployment %s",
            auth_method,
            final_deployment,
        )

        # Create PydanticAI Responses model
        provider = OpenAIProvider(openai_client=azure_client)
        model = OpenAIResponsesModel(final_deployment, provider=provider)
        logger.info("Created Azure Responses model '%s'", final_deployment)
        return model

    except Exception as err:
        logger.debug("Failed to create Azure Responses model '%s': %s", final_deployment, err, exc_info=True)
        raise


=== File: recipe-executor/recipe_executor/llm_utils/llm.py ===
# This file was generated by Codebase-Generator, do not edit directly
import os
import time
import logging
from typing import Optional, List, Type, Union, Dict, Any

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.openai import OpenAIModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.mcp import MCPServer

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
from recipe_executor.llm_utils.responses import create_openai_responses_model
from recipe_executor.llm_utils.azure_responses import create_azure_responses_model

# Built-in tool parameter types for Responses API
from openai.types.responses import WebSearchToolParam, FileSearchToolParam


def get_model(model_id: str, logger: logging.Logger) -> Any:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    Supported providers:
      - openai
      - azure
      - anthropic
      - ollama
      - openai_responses
      - azure_responses
    """
    parts = model_id.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid model_id format: '{model_id}'")
    provider = parts[0].lower()

    # OpenAI provider
    if provider == "openai":
        if len(parts) != 2:
            raise ValueError(f"Invalid OpenAI model_id: '{model_id}'")
        model_name = parts[1]
        return OpenAIModel(model_name)

    # Azure OpenAI provider
    if provider == "azure":
        if len(parts) == 2:
            model_name = parts[1]
            deployment = None
        elif len(parts) == 3:
            model_name, deployment = parts[1], parts[2]
        else:
            raise ValueError(f"Invalid Azure model_id: '{model_id}'")
        return get_azure_openai_model(
            logger=logger,
            model_name=model_name,
            deployment_name=deployment,
        )

    # Anthropic provider
    if provider == "anthropic":
        if len(parts) != 2:
            raise ValueError(f"Invalid Anthropic model_id: '{model_id}'")
        return AnthropicModel(parts[1])

    # Ollama provider
    if provider == "ollama":
        if len(parts) != 2:
            raise ValueError(f"Invalid Ollama model_id: '{model_id}'")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        provider_obj = OpenAIProvider(base_url=f"{base_url}/v1")
        return OpenAIModel(model_name=parts[1], provider=provider_obj)

    # OpenAI Responses API
    if provider == "openai_responses":
        if len(parts) != 2:
            raise ValueError(f"Invalid OpenAI Responses model_id: '{model_id}'")
        return create_openai_responses_model(parts[1])

    # Azure Responses API
    if provider == "azure_responses":
        if len(parts) == 2:
            model_name = parts[1]
            deployment = None
        elif len(parts) == 3:
            model_name, deployment = parts[1], parts[2]
        else:
            raise ValueError(f"Invalid Azure Responses model_id: '{model_id}'")
        return create_azure_responses_model(model_name, deployment)

    raise ValueError(f"Unsupported LLM provider: '{provider}' in model_id '{model_id}'")


class LLM:
    """
    Unified interface for interacting with various LLM providers
    and optional MCP servers.
    """

    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        max_tokens: Optional[int] = None,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.default_model_id: str = model
        self.default_max_tokens: Optional[int] = max_tokens
        self.default_mcp_servers: List[MCPServer] = mcp_servers or []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
        openai_builtin_tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        model_id = model or self.default_model_id
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        servers = mcp_servers if mcp_servers is not None else self.default_mcp_servers

        # Info: selected provider and model
        try:
            provider = model_id.split("/", 1)[0]
        except Exception:
            provider = "unknown"
        self.logger.info(
            "LLM generate using provider=%s model_id=%s",
            provider,
            model_id,
        )

        # Debug: request payload (masking sensitive info)
        output_name = getattr(output_type, "__name__", str(output_type))
        self.logger.debug(
            "LLM request payload prompt=%r model_id=%s max_tokens=%s output_type=%s openai_builtin_tools=%s",
            prompt,
            model_id,
            tokens,
            output_name,
            openai_builtin_tools,
        )

        # Initialize model instance
        try:
            model_instance = get_model(model_id, self.logger)
        except ValueError as e:
            self.logger.error("Invalid model_id '%s': %s", model_id, str(e))
            raise

        # Prepare model settings
        model_settings: Optional[Any] = None
        if provider == "openai_responses":
            settings_kwargs: Dict[str, Any] = {}
            if tokens is not None:
                settings_kwargs["max_tokens"] = tokens
            if openai_builtin_tools:
                converted: List[Union[WebSearchToolParam, FileSearchToolParam]] = []
                for t in openai_builtin_tools:
                    try:
                        converted.append(WebSearchToolParam(**t))
                    except Exception:
                        try:
                            converted.append(FileSearchToolParam(**t))
                        except Exception:
                            raise ValueError(f"Unsupported tool param: {t}")
                settings_kwargs["openai_builtin_tools"] = converted
            if settings_kwargs:
                model_settings = OpenAIResponsesModelSettings(**settings_kwargs)
        else:
            if tokens is not None:
                model_settings = ModelSettings(max_tokens=tokens)

        # Build Agent
        agent_kwargs: Dict[str, Any] = {
            "model": model_instance,
            "output_type": output_type,
            "mcp_servers": servers,
        }
        if model_settings is not None:
            agent_kwargs["model_settings"] = model_settings
        agent: Agent = Agent(**agent_kwargs)  # type: ignore

        # Execute the request
        start = time.time()
        try:
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
        except Exception as e:
            self.logger.error("LLM call failed for model_id=%s error=%s", model_id, str(e))
            raise
        end = time.time()

        # Log usage and timing
        duration = end - start
        usage = None
        try:
            usage = result.usage()
        except Exception:
            usage = None
        if usage:
            self.logger.info(
                "LLM result time=%.3f sec requests=%d tokens_total=%d (req=%d res=%d)",
                duration,
                usage.requests,
                usage.total_tokens,
                usage.request_tokens,
                usage.response_tokens,
            )
        else:
            self.logger.info("LLM result time=%.3f sec (usage unavailable)", duration)

        # Debug: raw result payload
        self.logger.debug("LLM raw result: %r", result)

        return result.output


=== File: recipe-executor/recipe_executor/llm_utils/mcp.py ===
# This file was generated by Codebase-Generator, do not edit directly
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
        tool_prefix = config.get("tool_prefix")
        if tool_prefix is not None and not isinstance(tool_prefix, str):
            raise ValueError("HTTP MCP server 'tool_prefix' must be a string if provided")

        logger.info("Creating HTTP MCP server for URL: %s", url)
        try:
            http_kwargs: Dict[str, Any] = {"url": url}
            if headers is not None:
                http_kwargs["headers"] = headers
            if tool_prefix is not None:
                http_kwargs["tool_prefix"] = tool_prefix
            server = MCPServerHTTP(**http_kwargs)
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

        # Environment for subprocess
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
                    sys_val = os.getenv(k)
                    if sys_val is not None:
                        env[k] = sys_val
                else:
                    env[k] = v

        working_dir = config.get("working_dir")
        if working_dir is not None and not isinstance(working_dir, str):
            raise ValueError("Stdio MCP server 'working_dir' must be a string if provided")

        tool_prefix = config.get("tool_prefix")
        if tool_prefix is not None and not isinstance(tool_prefix, str):
            raise ValueError("Stdio MCP server 'tool_prefix' must be a string if provided")

        logger.info("Creating stdio MCP server with command: %s %s", command, args)
        try:
            stdio_kwargs: Dict[str, Any] = {"command": command, "args": args}
            if working_dir is not None:
                stdio_kwargs["cwd"] = working_dir
            if env is not None:
                stdio_kwargs["env"] = env
            if tool_prefix is not None:
                stdio_kwargs["tool_prefix"] = tool_prefix
            server = MCPServerStdio(**stdio_kwargs)
        except Exception as exc:
            raise RuntimeError(f"Failed to create stdio MCP server: {exc}") from exc
        return server

    # Neither HTTP nor Stdio specified
    raise ValueError("Invalid MCP server configuration: must contain 'url' for HTTP or 'command' for stdio transport")


=== File: recipe-executor/recipe_executor/llm_utils/responses.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Responses component for Recipe Executor integrating OpenAI Responses API.
Provides factory function for creating configured OpenAIResponsesModel instances.
"""

from pydantic_ai.models.openai import OpenAIResponsesModel

__all__ = ["create_openai_responses_model"]


def create_openai_responses_model(model_name: str) -> OpenAIResponsesModel:
    """
    Instantiate and return an OpenAIResponsesModel for the given model name.

    Args:
        model_name: The identifier of the OpenAI model (e.g., "gpt-4o").

    Returns:
        An OpenAIResponsesModel instance configured to use the Responses API.

    Raises:
        ValueError: If model_name is invalid or model initialization fails.
    """
    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError("model_name must be a non-empty string")

    try:
        model = OpenAIResponsesModel(model_name)
    except Exception as e:
        # Provide clear context in error message
        raise ValueError(f"Failed to initialize OpenAIResponsesModel for '{model_name}': {e}") from e

    return model


=== File: recipe-executor/recipe_executor/logger.py ===
# This file was generated by Codebase-Generator, do not edit directly
import logging
import os
import sys


def init_logger(log_dir: str = "logs", stdio_log_level: str = "INFO") -> logging.Logger:
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
    # Acquire the root logger and set to the lowest level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to reset configuration
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Ensure log directory exists
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as exc:
        raise Exception(f"Failed to create log directory '{log_dir}': {exc}") from exc

    # Common log formatting
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handlers for each level
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "error": logging.ERROR,
    }
    for name, level in level_map.items():
        file_path = os.path.join(log_dir, f"{name}.log")
        try:
            file_handler = logging.FileHandler(file_path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as exc:
            raise Exception(f"Failed to set up {name} log file '{file_path}': {exc}") from exc

    # Configure console (stdout) handler
    level_name = stdio_log_level.upper()
    if level_name == "WARN":
        level_name = "WARNING"
    if level_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level_name = "INFO"
    console_level = getattr(logging, level_name, logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Log initialization messages
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, level_name)
    logger.info("Logger initialized successfully")

    return logger


=== File: recipe-executor/recipe_executor/main.py ===
# This file was generated by Codebase-Generator, do not edit directly
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

    # High-level start info
    logger.info("Starting Recipe Executor Tool")
    logger.debug("Parsed arguments: %s", args)

    # Parse context and config key=value pairs
    try:
        artifacts = parse_key_value_pairs(args.context)
        config = parse_key_value_pairs(args.config)
    except ValueError as ve:
        # Malformed context/config format
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
        # Reraise to be caught by outer main
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


=== File: recipe-executor/recipe_executor/models.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Models for Recipe Executor system.

Defines Pydantic models for file specifications and recipe structures.
"""

from typing import Any, Dict, List, Union

from pydantic import BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file, which can be a string,
                 a mapping, or a list of mappings for structured outputs.
    """

    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps: A list of steps defining the recipe.
    """

    steps: List[RecipeStep]


=== File: recipe-executor/recipe_executor/protocols.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Protocols definitions for the Recipe Executor system.

This module provides structural interfaces (Protocols) for core components:
- ContextProtocol
- StepProtocol
- ExecutorProtocol

These serve as the single source of truth for component contracts, enabling loose coupling
and clear type annotations without introducing direct dependencies on concrete implementations.
"""

from typing import Protocol, runtime_checkable, Any, Dict, Iterator, Union
from pathlib import Path
from logging import Logger

from recipe_executor.models import Recipe


@runtime_checkable
class ContextProtocol(Protocol):
    """
    Defines a dict-like context for sharing data across steps and executors.

    Methods mirror built-in dict behaviors plus cloning and serialization.
    """

    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __contains__(self, key: str) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __len__(self) -> int: ...

    def get(self, key: str, default: Any = None) -> Any: ...

    def clone(self) -> "ContextProtocol": ...

    def dict(self) -> Dict[str, Any]: ...

    def json(self) -> str: ...

    def keys(self) -> Iterator[str]: ...

    def get_config(self) -> Dict[str, Any]: ...

    def set_config(self, config: Dict[str, Any]) -> None: ...


@runtime_checkable
class StepProtocol(Protocol):
    """
    Defines the interface for a recipe step implementation.

    Each step is initialized with a logger and configuration, and
    exposes an asynchronous execute method.
    """

    def __init__(self, logger: Logger, config: Dict[str, Any]) -> None: ...

    async def execute(self, context: ContextProtocol) -> None: ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """
    Defines the interface for an executor implementation.

    The executor runs a recipe given its definition and a context.
    """

    def __init__(self, logger: Logger) -> None: ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None: ...


=== File: recipe-executor/recipe_executor/steps/__init__.py ===
# This file was generated by Codebase-Generator, do not edit directly

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

# Register standard steps in the global registry
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

__all__ = [
    "STEP_REGISTRY",
    "ConditionalStep",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "MCPStep",
    "ParallelStep",
    "ReadFilesStep",
    "SetContextStep",
    "WriteFilesStep",
]


=== File: recipe-executor/recipe_executor/steps/base.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Base step component for the Recipe Executor.
Defines a generic BaseStep class and the base Pydantic StepConfig.
"""

from __future__ import annotations

import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    Extend this class to add step-specific fields.
    """

    # No common fields; each step should subclass and define its own
    pass


StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Base class for all steps in the recipe executor.

    Each step must implement the async execute method.
    Subclasses should call super().__init__ in their constructor,
    passing a logger and an instance of a StepConfig subclass.
    """

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        """
        Initialize a step with a logger and validated configuration.

        Args:
            logger: Logger instance for the step.
            config: Pydantic-validated configuration for the step.
        """
        self.logger: logging.Logger = logger
        self.config: StepConfigType = config
        # Log initialization with debug-level detail
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config!r}")

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step logic. Must be overridden by subclasses.

        Args:
            context: Execution context adhering to ContextProtocol.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement the execute method")


=== File: recipe-executor/recipe_executor/steps/conditional.py ===
# This file was generated by Codebase-Generator, do not edit directly
import logging
import os
import re
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils.templates import render_template


class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression or boolean to evaluate against the context.
        if_true: Optional branch configuration when condition is true.
        if_false: Optional branch configuration when condition is false.
    """

    condition: Any
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None


# Utility functions for condition evaluation


def file_exists(path: Any) -> bool:
    """Check if a given path exists on the filesystem."""
    try:
        return isinstance(path, str) and os.path.exists(path)
    except Exception:
        return False


def all_files_exist(paths: Any) -> bool:
    """Check if all paths in a list or tuple exist."""
    try:
        if not isinstance(paths, (list, tuple)):
            return False
        return all(isinstance(p, str) and os.path.exists(p) for p in paths)
    except Exception:
        return False


def file_is_newer(src: Any, dst: Any) -> bool:
    """Check if src file is newer than dst file."""
    try:
        if not (isinstance(src, str) and isinstance(dst, str)):
            return False
        if not (os.path.exists(src) and os.path.exists(dst)):
            return False
        return os.path.getmtime(src) > os.path.getmtime(dst)
    except Exception:
        return False


def and_(*args: Any) -> bool:
    """Logical AND over all arguments."""
    return all(bool(a) for a in args)


def or_(*args: Any) -> bool:
    """Logical OR over all arguments."""
    return any(bool(a) for a in args)


def not_(val: Any) -> bool:
    """Logical NOT of the value."""
    return not bool(val)


def evaluate_condition(expr: Any, context: ContextProtocol, logger: logging.Logger) -> bool:
    """
    Render and evaluate a condition expression against the context.
    Supports boolean literals, file checks, comparisons, and logical operations.
    Raises ValueError on render or evaluation errors.
    """
    # Direct boolean
    if isinstance(expr, bool):
        logger.debug("Using boolean condition: %s", expr)
        return expr

    # Coerce to string for template rendering
    expr_str = expr if isinstance(expr, str) else str(expr)
    try:
        rendered = render_template(expr_str, context)
    except Exception as err:
        raise ValueError(f"Error rendering condition '{expr_str}': {err}")

    logger.debug("Rendered condition '%s': '%s'", expr_str, rendered)
    text = rendered.strip()
    lowered = text.lower()

    # Boolean literal handling
    if lowered in ("true", "false"):
        result = lowered == "true"
        logger.debug("Interpreted boolean literal '%s' as %s", text, result)
        return result

    # Avoid Python keyword conflicts for functional logic
    transformed = re.sub(r"\band\(", "and_(", text)
    transformed = re.sub(r"\bor\(", "or_(", transformed)
    transformed = re.sub(r"\bnot\(", "not_(", transformed)
    logger.debug("Transformed expression for eval: '%s'", transformed)

    # Safe globals for eval
    safe_globals: Dict[str, Any] = {
        "__builtins__": {},
        # File utilities
        "file_exists": file_exists,
        "all_files_exist": all_files_exist,
        "file_is_newer": file_is_newer,
        # Logical helpers
        "and_": and_,
        "or_": or_,
        "not_": not_,
        # Boolean literals
        "true": True,
        "false": False,
    }

    try:
        result = eval(transformed, safe_globals, {})  # nosec
    except Exception as err:
        raise ValueError(f"Invalid condition expression '{transformed}': {err}")

    outcome = bool(result)
    logger.debug("Condition '%s' evaluated to %s", transformed, outcome)
    return outcome


class ConditionalStep(BaseStep[ConditionalConfig]):
    """
    Step that branches execution based on a boolean condition.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        config_model = ConditionalConfig.model_validate(config)
        super().__init__(logger, config_model)

    async def execute(self, context: ContextProtocol) -> None:
        expr = self.config.condition
        self.logger.debug("Evaluating conditional expression: '%s'", expr)
        try:
            result = evaluate_condition(expr, context, self.logger)
        except ValueError as err:
            raise RuntimeError(f"Condition evaluation error: {err}")

        branch = self.config.if_true if result else self.config.if_false
        branch_name = "if_true" if result else "if_false"
        self.logger.debug(
            "Condition '%s' is %s, executing '%s' branch",
            expr,
            result,
            branch_name,
        )

        if isinstance(branch, dict) and branch.get("steps"):
            await self._execute_branch(branch, context)
        else:
            self.logger.debug("No branch to execute for this condition result")

    async def _execute_branch(self, branch: Dict[str, Any], context: ContextProtocol) -> None:
        steps: List[Any] = branch.get("steps") or []
        if not isinstance(steps, list):
            self.logger.debug("Branch 'steps' is not a list, skipping execution")
            return

        for step_def in steps:
            if not isinstance(step_def, dict):
                continue

            step_type = step_def.get("type")
            step_conf = step_def.get("config") or {}
            if not step_type:
                self.logger.debug("Step definition missing 'type', skipping")
                continue

            step_cls = STEP_REGISTRY.get(step_type)
            if step_cls is None:
                raise RuntimeError(f"Unknown step type in conditional branch: {step_type}")

            self.logger.debug("Executing step '%s' in conditional branch", step_type)
            step_instance = step_cls(self.logger, step_conf)
            await step_instance.execute(context)


=== File: recipe-executor/recipe_executor/steps/execute_recipe.py ===
# This file was generated by Codebase-Generator, do not edit directly
import os
import ast
import json
from typing import Any, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template

__all__ = ["ExecuteRecipeConfig", "ExecuteRecipeStep"]


def _render_override(value: Any, context: ContextProtocol) -> Any:
    """
    Recursively render and parse override values.

    - Strings are template-rendered, then if the result is a valid Python literal
      list or dict (via ast.literal_eval) or valid JSON list/dict, parsed into Python objects.
    - Lists and dicts are processed recursively.
    - Other types are returned as-is.
    """
    if isinstance(value, str):
        rendered = render_template(value, context)
        # Attempt to parse with Python literal evaluation
        try:
            parsed = ast.literal_eval(rendered)
            if isinstance(parsed, (dict, list)):
                return parsed
        except (ValueError, SyntaxError):  # Not a Python literal list/dict
            pass
        # Attempt to parse as JSON object or array
        try:
            parsed = json.loads(rendered)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass
        return rendered

    if isinstance(value, list):  # type: ignore[type-arg]
        return [_render_override(item, context) for item in value]

    if isinstance(value, dict):  # type: ignore[type-arg]
        return {key: _render_override(val, context) for key, val in value.items()}

    return value


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the sub-recipe to execute (templateable).
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, Any] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step to execute a sub-recipe with shared context and optional overrides."""

    def __init__(
        self,
        logger: Any,
        config: Dict[str, Any],
    ) -> None:
        validated: ExecuteRecipeConfig = ExecuteRecipeConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute a sub-recipe located at the rendered recipe_path.

        Applies context_overrides before execution, shares the same context,
        and logs progress.
        """
        # Render and validate recipe path
        rendered_path = render_template(self.config.recipe_path, context)
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides with templating and literal/JSON parsing
        for key, override_value in self.config.context_overrides.items():
            rendered_value = _render_override(override_value, context)
            context[key] = rendered_value  # type: ignore[index]

        try:
            # Import here to avoid circular dependencies
            from recipe_executor.executor import Executor

            self.logger.info(f"Starting sub-recipe execution: {rendered_path}")
            executor = Executor(self.logger)
            await executor.execute(rendered_path, context)
            self.logger.info(f"Completed sub-recipe execution: {rendered_path}")
        except Exception as exc:
            self.logger.error(f"Error executing sub-recipe '{rendered_path}': {exc}")
            raise RuntimeError(f"Failed to execute sub-recipe '{rendered_path}': {exc}") from exc


=== File: recipe-executor/recipe_executor/steps/llm_generate.py ===
# This file was generated by Codebase-Generator, do not edit directly
import logging
from typing import Any, Dict, List, Optional, Union, Type

from pydantic import BaseModel

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.models import json_object_to_pydantic_model
from recipe_executor.utils.templates import render_template


class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        max_tokens: The maximum number of tokens for the LLM response.
        mcp_servers: List of MCP server configurations for access to tools.
        openai_builtin_tools: List of built-in tools for Responses API models.
        output_format: The format of the LLM output (text, files, or JSON/list schemas).
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    max_tokens: Optional[Union[str, int]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    openai_builtin_tools: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):  # type: ignore
    files: List[FileSpec]


def _render_config(config: Dict[str, Any], context: ContextProtocol) -> Dict[str, Any]:
    """
    Recursively render templated strings in a dict.
    """
    result: Dict[str, Any] = {}
    for key, value in config.items():
        if isinstance(value, str):
            result[key] = render_template(value, context)
        elif isinstance(value, dict):
            result[key] = _render_config(value, context)
        elif isinstance(value, list):
            items: List[Any] = []
            for item in value:
                if isinstance(item, dict):
                    items.append(_render_config(item, context))
                else:
                    items.append(item)
            result[key] = items
        else:
            result[key] = value
    return result


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    """
    Step to generate content via a large language model (LLM).
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render core templated values
        prompt: str = render_template(self.config.prompt, context)
        model_id: str = render_template(self.config.model, context)
        output_key: str = render_template(self.config.output_key, context)

        # Prepare max_tokens
        raw_max = self.config.max_tokens
        max_tokens: Optional[int] = None
        if raw_max is not None:
            max_str = render_template(str(raw_max), context)
            try:
                max_tokens = int(max_str)
            except ValueError:
                raise ValueError(f"Invalid max_tokens value: {raw_max!r}")

        # Collect and render MCP server configurations
        mcp_cfgs: List[Dict[str, Any]] = []
        if self.config.mcp_servers:
            mcp_cfgs.extend(self.config.mcp_servers)
        ctx_mcp = context.get_config().get("mcp_servers") or []
        if isinstance(ctx_mcp, list):
            mcp_cfgs.extend(ctx_mcp)

        mcp_servers: List[Any] = []
        for cfg in mcp_cfgs:
            rendered = _render_config(cfg, context)
            server = get_mcp_server(logger=self.logger, config=rendered)
            mcp_servers.append(server)

        # Instantiate LLM client
        llm = LLM(
            logger=self.logger,
            model=model_id,
            mcp_servers=mcp_servers or None,
        )

        # Validate and render built-in tools for Responses API models
        validated_tools: Optional[List[Dict[str, Any]]] = None
        if self.config.openai_builtin_tools:
            tools_rendered: List[Dict[str, Any]] = []
            for tool_cfg in self.config.openai_builtin_tools:
                tools_rendered.append(_render_config(tool_cfg, context))
            provider = model_id.split("/")[0]
            if provider not in ("openai_responses", "azure_responses"):
                raise ValueError(
                    "Built-in tools only supported with Responses API models (openai_responses/* or azure_responses/*)"
                )
            for tool in tools_rendered:
                ttype = tool.get("type")
                if ttype != "web_search_preview":
                    raise ValueError(f"Unsupported tool type: {ttype}. Supported: web_search_preview")
            validated_tools = tools_rendered

        output_format = self.config.output_format
        result: Any = None

        try:
            self.logger.debug(
                "Calling LLM: model=%s, format=%r, max_tokens=%s, mcp_servers=%r, tools=%r",
                model_id,
                output_format,
                max_tokens,
                mcp_servers,
                validated_tools,
            )

            # Text output
            if output_format == "text":  # type: ignore
                kwargs: Dict[str, Any] = {"output_type": str, "openai_builtin_tools": validated_tools}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                context[output_key] = result

            # Files output
            elif output_format == "files":  # type: ignore
                kwargs = {"output_type": FileSpecCollection, "openai_builtin_tools": validated_tools}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                context[output_key] = result.files

            # JSON object schema
            elif isinstance(output_format, dict):
                schema_model: Type[BaseModel] = json_object_to_pydantic_model(output_format, model_name="LLMObject")
                kwargs = {"output_type": schema_model, "openai_builtin_tools": validated_tools}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                context[output_key] = result.model_dump()

            # List schema
            elif isinstance(output_format, list):  # type: ignore
                if len(output_format) != 1 or not isinstance(output_format[0], dict):
                    raise ValueError(
                        "When output_format is a list, it must be a single-item list containing a schema object."
                    )
                item_schema = output_format[0]
                wrapper_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": item_schema}},
                    "required": ["items"],
                }
                schema_model = json_object_to_pydantic_model(wrapper_schema, model_name="LLMListWrapper")
                kwargs = {"output_type": schema_model, "openai_builtin_tools": validated_tools}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                wrapper = result.model_dump()
                context[output_key] = wrapper.get("items", [])

            else:
                raise ValueError(f"Unsupported output_format: {output_format!r}")

        except Exception as exc:
            self.logger.error("LLM generate failed: %r", exc, exc_info=True)
            raise


=== File: recipe-executor/recipe_executor/steps/loop.py ===
# This file was generated by Codebase-Generator, do not edit directly
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Either a string path to a collection in the context or a direct list/dict.
        item_key: Key under which the current item is placed in each iteration's context.
        max_concurrency: Maximum number of items to process concurrently (0 = unlimited).
        delay: Delay in seconds between starting parallel tasks.
        substeps: List of step configurations to execute for each item.
        result_key: Context key where the list/dict of results will be stored.
        fail_fast: Whether to stop processing on first error.
    """

    items: Union[str, List[Any], Dict[Any, Any]]
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, executing configured substeps for each item.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        validated = LoopStepConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        # Delay import to avoid circular dependency
        from recipe_executor.executor import Executor  # type: ignore

        # Resolve items definition (template or direct)
        items_def = self.config.items
        if isinstance(items_def, str):
            rendered = render_template(items_def, context)
            items_obj: Any = _resolve_path(rendered, context)
        else:
            items_obj = items_def

        # Validate items
        if items_obj is None:
            raise ValueError(f"LoopStep: Items '{items_def}' not found in context.")
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(f"LoopStep: Items must be a list or dict, got {type(items_obj).__name__}.")

        # Flatten to list of (key, value)
        if isinstance(items_obj, list):
            items_list: List[Tuple[Any, Any]] = [(_i, _v) for _i, _v in enumerate(items_obj)]
        else:
            items_list = list(items_obj.items())

        total = len(items_list)
        max_c = self.config.max_concurrency
        self.logger.info(f"LoopStep: Processing {total} items with max_concurrency={max_c}.")

        # Handle empty
        if total == 0:
            result_empty = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = result_empty
            self.logger.info("LoopStep: No items to process.")
            return

        # Prepare result containers
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = [] if isinstance(items_obj, list) else {}

        # Concurrency control
        semaphore: Optional[asyncio.Semaphore]
        if max_c == 0:
            semaphore = None
        else:
            semaphore = asyncio.Semaphore(max_c) if max_c > 0 else None

        # Executor for substeps
        executor: ExecutorProtocol = Executor(self.logger)
        recipe_body: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered = False
        completed = 0
        tasks: List[asyncio.Task] = []

        async def process_one(key: Any, val: Any) -> Tuple[Any, Any, Optional[str]]:
            # Clone for isolation
            item_ctx = context.clone()
            # Set current item
            item_ctx[self.config.item_key] = val
            if isinstance(items_obj, list):
                item_ctx["__index"] = key
            else:
                item_ctx["__key"] = key
            try:
                self.logger.debug(f"LoopStep: Starting item {key}.")
                await executor.execute(recipe_body, item_ctx)
                out = item_ctx.get(self.config.item_key, val)
                self.logger.debug(f"LoopStep: Finished item {key}.")
                return key, out, None
            except Exception as e:
                err_msg = str(e)
                self.logger.error(f"LoopStep: Error on item {key}: {err_msg}")
                return key, None, err_msg

        async def sequential() -> None:
            nonlocal fail_fast_triggered, completed
            for k, v in items_list:
                if fail_fast_triggered:
                    break
                idx, out, err = await process_one(k, v)
                if err:
                    # record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # record success
                    if isinstance(results, list):
                        results.append(out)
                    else:
                        results[idx] = out
                    completed += 1

        async def parallel() -> None:
            nonlocal fail_fast_triggered, completed

            async def worker(k: Any, v: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore:
                    async with semaphore:
                        return await process_one(k, v)
                return await process_one(k, v)

            # schedule tasks with optional delay
            for idx, (k, v) in enumerate(items_list):
                if fail_fast_triggered:
                    break
                tasks.append(asyncio.create_task(worker(k, v)))
                if self.config.delay and idx < total - 1:
                    await asyncio.sleep(self.config.delay)

            # gather results as they complete
            for task in asyncio.as_completed(tasks):  # type: ignore
                if fail_fast_triggered:
                    break
                try:
                    k, out, err = await task  # type: ignore
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": k, "error": err})
                        else:
                            errors[k] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(out)
                        else:
                            results[k] = out
                        completed += 1
                except Exception as e:
                    self.logger.error(f"LoopStep: Unexpected error: {e}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break

        # Execute loops
        if max_c <= 1:
            await sequential()
        else:
            await parallel()

        # Store outputs
        context[self.config.result_key] = results
        if errors:
            context[f"{self.config.result_key}__errors"] = errors

        err_count = len(errors) if isinstance(errors, (list, dict)) else 0
        self.logger.info(f"LoopStep: Completed {completed}/{total} items. Errors: {err_count}.")


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dictionaries.
    """
    current: Any = context
    for part in path.split("."):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current


=== File: recipe-executor/recipe_executor/steps/mcp.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
MCPStep component for invoking tools on remote MCP servers and storing results in context.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult

from recipe_executor.steps.base import BaseStep, ContextProtocol, StepConfig
from recipe_executor.utils.templates import render_template


class MCPConfig(StepConfig):  # type: ignore
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result.
    """

    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"


class MCPStep(BaseStep[MCPConfig]):  # type: ignore
    """
    Step that connects to an MCP server, invokes a tool, and stores the result in the context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        # Validate and store configuration
        cfg: MCPConfig = MCPConfig.model_validate(config)  # type: ignore
        super().__init__(logger, cfg)

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve tool name
        tool_name: str = render_template(self.config.tool_name, context)

        # Resolve arguments (template strings or raw values)
        raw_args: Dict[str, Any] = self.config.arguments or {}
        arguments: Dict[str, Any] = {}
        for key, value in raw_args.items():
            if isinstance(value, str):
                arguments[key] = render_template(value, context)
            else:
                arguments[key] = value

        # Determine server configuration and client
        server_conf: Dict[str, Any] = self.config.server
        service_desc: str
        client_cm: Any

        if "command" in server_conf:
            # stdio transport
            cmd: str = render_template(server_conf.get("command", ""), context)
            raw_args_list: List[Any] = server_conf.get("args", []) or []
            args_list: List[str] = []
            for item in raw_args_list:
                if isinstance(item, str):
                    args_list.append(render_template(item, context))
                else:
                    args_list.append(str(item))

            # Environment variables
            config_env: Optional[Dict[str, str]] = None
            if server_conf.get("env") is not None:
                config_env = {}
                for env_k, env_v in server_conf.get("env", {}).items():
                    if isinstance(env_v, str):
                        rendered: str = render_template(env_v, context)
                        if rendered == "":
                            # Try loading from .env then system environment
                            env_file = os.path.join(os.getcwd(), ".env")
                            if os.path.exists(env_file):
                                load_dotenv(env_file)
                                sys_val = os.getenv(env_k)
                                if sys_val is not None:
                                    rendered = sys_val
                        config_env[env_k] = rendered
                    else:
                        config_env[env_k] = str(env_v)

            # Working directory
            cwd: Optional[str] = None
            if server_conf.get("working_dir") is not None:
                cwd = render_template(server_conf.get("working_dir", ""), context)

            server_params = StdioServerParameters(
                command=cmd,
                args=args_list,
                env=config_env,
                cwd=cwd,
            )
            client_cm = stdio_client(server_params)
            service_desc = f"stdio command '{cmd}'"
        else:
            # SSE transport
            url: str = render_template(server_conf.get("url", ""), context)
            headers_conf: Optional[Dict[str, Any]] = None
            if server_conf.get("headers") is not None:
                headers_conf = {}
                for hk, hv in server_conf.get("headers", {}).items():
                    if isinstance(hv, str):
                        headers_conf[hk] = render_template(hv, context)
                    else:
                        headers_conf[hk] = hv

            client_cm = sse_client(url, headers=headers_conf)
            service_desc = f"SSE server '{url}'"

        # Connect and call the tool
        self.logger.debug(f"Connecting to MCP server: {service_desc}")
        try:
            async with client_cm as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    self.logger.debug(f"Invoking tool '{tool_name}' with arguments {arguments}")
                    try:
                        result: CallToolResult = await session.call_tool(
                            name=tool_name,
                            arguments=arguments,
                        )
                    except Exception as e:
                        raise ValueError(f"Tool invocation failed for '{tool_name}' on {service_desc}: {e}") from e
        except ValueError:
            # Propagate known invocation errors
            raise
        except Exception as e:
            raise ValueError(f"Failed to call tool '{tool_name}' on {service_desc}: {e}") from e

        # Convert CallToolResult to plain dictionary
        try:
            result_dict: Dict[str, Any] = result.__dict__  # type: ignore
        except Exception:
            result_dict = {attr: getattr(result, attr) for attr in dir(result) if not attr.startswith("_")}

        # Store or overwrite result in context
        context[self.config.result_key] = result_dict


=== File: recipe-executor/recipe_executor/steps/parallel.py ===
# This file was generated by Codebase-Generator, do not edit directly
import asyncio
import logging
from typing import Any, Dict, List, Optional, Set

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.protocols import ContextProtocol, StepProtocol


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each a dict with 'type' and 'config'.
        max_concurrency: Maximum number of substeps to run concurrently. 0 means unlimited.
        delay: Optional delay (in seconds) between launching each substep.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """Step to execute multiple sub-steps in parallel."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        # Validate config with Pydantic
        parsed = ParallelConfig.model_validate(config)
        super().__init__(logger, parsed)

    async def execute(self, context: ContextProtocol) -> None:
        substeps: List[Dict[str, Any]] = self.config.substeps or []
        total_steps: int = len(substeps)
        max_conc: int = self.config.max_concurrency
        delay: float = self.config.delay

        self.logger.info(f"Starting ParallelStep: {total_steps} substeps, max_concurrency={max_conc}, delay={delay}")

        if total_steps == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit (0 means unlimited => all at once)
        concurrency: int = max_conc if max_conc > 0 else total_steps
        semaphore = asyncio.Semaphore(concurrency)

        # Track first failure
        failure: Dict[str, Optional[Any]] = {"exc": None, "idx": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            sub_logger = self.logger.getChild(f"substep_{idx}")
            try:
                sub_logger.debug(f"Cloning context and preparing substep {idx} ({spec.get('type')})")
                sub_context = context.clone()

                step_type = spec.get("type")
                step_cfg: Dict[str, Any] = spec.get("config", {})
                if not step_type or step_type not in STEP_REGISTRY:
                    raise RuntimeError(f"Unknown or missing step type '{step_type}' for substep {idx}")
                StepClass = STEP_REGISTRY[step_type]
                step_instance: StepProtocol = StepClass(sub_logger, step_cfg)

                sub_logger.info(f"Launching substep {idx} of type '{step_type}'")
                # Execute the sub-step
                result = step_instance.execute(sub_context)
                if asyncio.iscoroutine(result):
                    await result
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as exc:
                # Record the first exception for fail-fast behavior
                if failure["exc"] is None:
                    failure["exc"] = exc
                    failure["idx"] = idx
                sub_logger.error(f"Substep {idx} failed: {exc}", exc_info=True)
                # Re-raise to let wait() detect exception
                raise

            finally:
                # Release semaphore slot regardless of success or failure
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(substeps):
            # Fail-fast: do not start new substeps after a failure
            if failure["exc"]:
                self.logger.debug(f"Fail-fast: aborting launch of remaining substeps at index {idx}")
                break

            await semaphore.acquire()
            if delay > 0:
                await asyncio.sleep(delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for first exception or all tasks to complete
        done: Set[asyncio.Task]
        pending: Set[asyncio.Task]
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        except Exception:
            # Unexpected errors in wait; proceed to error handling
            done = set()
            pending = set(tasks)

        # If any substep failed, cancel pending and raise
        if failure["exc"]:
            failed_idx = failure.get("idx")
            self.logger.error(f"A substep failed at index {failed_idx}; cancelling remaining tasks")
            for p in pending:
                p.cancel()
            # Ensure all pending tasks are done
            await asyncio.gather(*pending, return_exceptions=True)
            raise RuntimeError(f"ParallelStep aborted due to failure in substep {failed_idx}") from failure["exc"]

        # All substeps succeeded
        # Gather any remaining tasks (done should include all)
        await asyncio.gather(*done)
        success_count = len(done)
        self.logger.info(f"Completed ParallelStep: {success_count}/{total_steps} substeps succeeded")


=== File: recipe-executor/recipe_executor/steps/read_files.py ===
# This file was generated by Codebase-Generator, do not edit directly
import json
import os
import logging
from typing import Any, Dict, List, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to read (may be templated).
        content_key (str): Key under which to store content in context (may be templated).
        optional (bool): If True, missing files are ignored (default: False).
        merge_mode (str): How to merge multiple files: "concat" or "dict" (default: "concat").
    """

    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from disk and stores their content in the context.
    Supports templated paths, optional files, and merge modes for multi-file reads.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        validated = ReadFilesConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        cfg = self.config
        # Render the storage key
        rendered_key = render_template(cfg.content_key, context)

        # Resolve and normalize paths
        raw_path = cfg.path
        paths: List[str] = []

        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            parts = [p.strip() for p in rendered.split(",") if p.strip()]
            paths.extend(parts)
        elif isinstance(raw_path, list):
            for entry in raw_path:
                if not isinstance(entry, str):
                    raise ValueError(f"Invalid path entry type: {entry!r}")
                rendered = render_template(entry, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_map: Dict[str, Any] = {}

        for p in paths:
            self.logger.debug(f"Reading file at path: {p}")
            if not os.path.exists(p):
                msg = f"File not found: {p}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {p}")
                    continue
                raise FileNotFoundError(msg)

            try:
                with open(p, mode="r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as exc:
                raise IOError(f"Error reading file {p}: {exc}")

            # Attempt structured parsing
            ext = os.path.splitext(p)[1].lower()
            content: Any = text
            if ext == ".json":
                try:
                    content = json.loads(text)
                except Exception as exc:
                    self.logger.warning(f"Failed to parse JSON from {p}: {exc}")
            elif ext in (".yaml", ".yml"):
                try:
                    content = yaml.safe_load(text)
                except Exception as exc:
                    self.logger.warning(f"Failed to parse YAML from {p}: {exc}")

            self.logger.info(f"Successfully read file: {p}")
            results.append(content)
            result_map[p] = content

        # Merge results
        if not results:
            if len(paths) <= 1:
                final_content: Any = ""
            elif cfg.merge_mode == "dict":
                final_content = {}
            else:
                final_content = ""
        elif len(results) == 1:
            final_content = results[0]
        else:
            if cfg.merge_mode == "dict":
                final_content = result_map
            else:
                segments: List[str] = []
                for p in paths:
                    if p in result_map:
                        raw = result_map[p]
                        segment = raw if isinstance(raw, str) else json.dumps(raw)
                        segments.append(f"{p}\n{segment}")
                final_content = "\n".join(segments)

        # Store in context
        context[rendered_key] = final_content
        self.logger.info(f"Stored file content under key '{rendered_key}'")


=== File: recipe-executor/recipe_executor/steps/registry.py ===
# This file was generated by Codebase-Generator, do not edit directly

"""
Registry for mapping step type names to their implementation classes.

This registry is a simple global dictionary. Steps register themselves by
updating this mapping, allowing dynamic lookup based on the step type name.
"""

from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry mapping step type names to their implementation classes.
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}

__all__ = ["STEP_REGISTRY"]


=== File: recipe-executor/recipe_executor/steps/set_context.py ===
# This file was generated by Codebase-Generator, do not edit directly
from typing import Any, Dict, List, Literal, Union
import logging

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template


def _has_unrendered_tags(s: str) -> bool:
    """
    Detect if the string still contains Liquid tags that need rendering.
    """
    return "{{" in s or "{%" in s


class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: JSON-serialisable literal, list, dict or Liquid template string rendered against
               the current context.
        nested_render: Whether to render templates recursively until no tags remain.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """

    key: str
    value: Union[str, List[Any], Dict[str, Any]]
    nested_render: bool = False
    if_exists: Literal["overwrite", "merge"] = "overwrite"


class SetContextStep(BaseStep[SetContextConfig]):
    """
    Step to set or update an artifact in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, SetContextConfig.model_validate(config))

    async def execute(self, context: ContextProtocol) -> None:
        key: str = self.config.key
        raw_value: Any = self.config.value
        nested: bool = self.config.nested_render
        existed: bool = key in context

        # Render the provided value (single or nested passes)
        value: Any = self._render_value(raw_value, context, nested)

        strategy: str = self.config.if_exists
        if strategy == "overwrite":
            context[key] = value
        elif strategy == "merge":
            if existed:
                old: Any = context[key]
                merged: Any = self._merge(old, value)
                context[key] = merged
            else:
                context[key] = value
        else:
            raise ValueError(f"Unknown if_exists strategy: '{strategy}'")

        self.logger.info(f"SetContextStep: key='{key}', strategy='{strategy}', existed={existed}")

    def _render_value(self, raw: Any, context: ContextProtocol, nested: bool) -> Any:
        """
        Recursively render Liquid templates in strings, lists, and dicts.

        If nested is True, re-render strings until no tags remain or no change.
        """
        if isinstance(raw, str):
            rendered: str = render_template(raw, context)
            if not nested:
                return rendered
            # nested rendering loop
            result: str = rendered
            while _has_unrendered_tags(result):
                prev: str = result
                result = render_template(result, context)
                if result == prev:
                    break
            return result

        if isinstance(raw, list):
            return [self._render_value(item, context, nested) for item in raw]

        if isinstance(raw, dict):
            return {k: self._render_value(v, context, nested) for k, v in raw.items()}

        # Other JSON-serialisable types pass through unchanged
        return raw

    def _merge(self, old: Any, new: Any) -> Any:
        """
        Shallow merge helper for merging existing and new values.

        Merge semantics:
        - str + str => concatenate
        - list + list or item => append
        - dict + dict => shallow dict merge
        - mismatched types => [old, new]
        """
        # String concatenation
        if isinstance(old, str) and isinstance(new, str):
            return old + new

        # List append
        if isinstance(old, list):  # type: ignore
            if isinstance(new, list):  # type: ignore
                return old + new  # type: ignore
            return old + [new]  # type: ignore

        # Dict shallow merge
        if isinstance(old, dict) and isinstance(new, dict):  # type: ignore
            merged: Dict[Any, Any] = old.copy()  # type: ignore
            merged.update(new)  # type: ignore
            return merged

        # Fallback for mismatched types
        return [old, new]


=== File: recipe-executor/recipe_executor/steps/write_files.py ===
# This file was generated by Codebase-Generator, do not edit directly
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Configuration for WriteFilesStep.

    Attributes:
        files_key: Optional context key containing FileSpec or list/dict specs.
        files: Optional direct list of dicts with 'path'/'content' or their key references.
        root: Base directory for output files.
    """

    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files to disk based on FileSpec or dict inputs.

    Either 'files' or 'files_key' must be provided.  Direct 'files' config takes precedence.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render the base output directory
        raw_root: str = self.config.root or "."
        root: str = render_template(raw_root, context)

        files_to_write: List[Dict[str, Any]] = []

        # 1. Direct 'files' entries take precedence
        if self.config.files is not None:
            for entry in self.config.files:
                # Resolve path
                if "path" in entry:
                    raw_path = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have 'path' or 'path_key'.")

                path_str = str(raw_path)
                path = render_template(path_str, context)

                # Resolve content
                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    raw_content = context[key]
                else:
                    raise ValueError("Each file entry must have 'content' or 'content_key'.")

                files_to_write.append({"path": path, "content": raw_content})

        # 2. Otherwise use files from context via 'files_key'
        elif self.config.files_key:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Files key '{key}' not found in context.")
            raw = context[key]

            # Normalize to list of specs or dicts
            if isinstance(raw, FileSpec):
                items: List[Union[FileSpec, Dict[str, Any]]] = [raw]
            elif isinstance(raw, dict):
                # Accept raw dict with 'path' and 'content'
                if "path" in raw and "content" in raw:
                    items = [raw]
                else:
                    raise ValueError(f"Malformed file dict under key '{key}': {raw}")
            elif isinstance(raw, list):
                items = raw  # type: ignore
            else:
                raise ValueError(f"Unsupported type for files_key '{key}': {type(raw)}")

            for item in items:
                if isinstance(item, FileSpec):
                    raw_path = item.path
                    raw_content = item.content
                elif isinstance(item, dict):
                    if "path" not in item or "content" not in item:
                        raise ValueError(f"Invalid file entry under '{key}': {item}")
                    raw_path = item["path"]
                    raw_content = item["content"]
                else:
                    raise ValueError(
                        f"Each file entry must be FileSpec or dict with 'path' and 'content', got {type(item)}"
                    )

                path_str = str(raw_path)
                path = render_template(path_str, context)
                files_to_write.append({"path": path, "content": raw_content})

        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write each file to disk
        for entry in files_to_write:
            rel_path: str = entry.get("path", "")
            content = entry.get("content")

            # Compute final filesystem path
            if root:
                combined = os.path.join(root, rel_path)
            else:
                combined = rel_path
            final_path = os.path.normpath(combined)

            try:
                # Ensure parent directories exist
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                # Serialize content if dict or list
                if isinstance(content, (dict, list)):
                    try:
                        text = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(f"Failed to serialize content for '{final_path}': {err}")
                else:
                    # Convert None to empty, others to string
                    if content is None:
                        text = ""
                    elif not isinstance(content, str):
                        text = str(content)
                    else:
                        text = content

                # Debug log before writing
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{text}")

                # Write file using UTF-8
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(text)

                # Info log after success
                size = len(text.encode("utf-8"))
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({size} bytes)")

            except Exception as exc:
                self.logger.error(f"[WriteFilesStep] Error writing file '{rel_path}': {exc}")
                raise


=== File: recipe-executor/recipe_executor/utils/models.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Utility functions for generating Pydantic models from JSON-Schema object definitions.
"""

from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, create_model

__all__ = ["json_object_to_pydantic_model"]


def json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]:
    """
    Convert a JSON-Schema object fragment into a Pydantic BaseModel subclass.

    Args:
        schema: A JSON-Schema fragment describing a root-level object (type must be "object").
        model_name: Name for the generated Pydantic model class.

    Returns:
        A subclass of pydantic.BaseModel corresponding to the schema.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    # Validate top-level schema
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary.")
    schema_type = schema.get("type")
    if schema_type is None:
        raise ValueError('Schema missing required "type" property.')
    if schema_type != "object":
        raise ValueError('Root schema type must be "object".')

    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    if not isinstance(properties, dict):
        raise ValueError('Schema "properties" must be a dictionary if present.')
    if not isinstance(required_fields, list):
        raise ValueError('Schema "required" must be a list if present.')

    class _Counter:
        def __init__(self) -> None:
            self._count: int = 0

        def next(self) -> int:
            self._count += 1
            return self._count

    counter = _Counter()

    def _parse_field(field_schema: Any, field_name: str, parent_name: str) -> Tuple[Any, Any]:
        """
        Parse a schema fragment for a single field and return a (type_hint, default) pair.
        """
        if not isinstance(field_schema, dict):
            raise ValueError(f"Schema for field '{field_name}' must be a dictionary.")
        ftype = field_schema.get("type")
        if ftype is None:
            raise ValueError(f"Schema for field '{field_name}' missing required 'type'.")

        # Primitive types
        if ftype == "string":
            return str, ...
        if ftype == "integer":
            return int, ...
        if ftype == "number":
            return float, ...
        if ftype == "boolean":
            return bool, ...

        # Nested object
        if ftype == "object":
            nested_name = f"{parent_name}_{field_name.capitalize()}Obj{counter.next()}"
            nested_model = _build_model(field_schema, nested_name)
            return nested_model, ...

        # Array / list
        if ftype in ("array", "list"):
            items = field_schema.get("items")
            if not isinstance(items, dict):
                raise ValueError(f"Array field '{field_name}' missing valid 'items' schema.")
            item_type, _ = _parse_field(items, f"{field_name}_item", parent_name)
            return List[item_type], ...  # type: ignore

        # Fallback for unknown types
        return Any, ...

    def _wrap_optional(
        field_schema: Any,
        is_required: bool,
        field_name: str,
        parent_name: str,
    ) -> Tuple[Any, Any]:
        """
        Wrap a field's type hint in Optional if it's not required, adjusting default.
        """
        type_hint, default = _parse_field(field_schema, field_name, parent_name)
        if not is_required:
            type_hint = Optional[type_hint]  # type: ignore
            default = None
        return type_hint, default

    def _build_model(obj_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        """
        Build a Pydantic model for an object schema.
        """
        if not isinstance(obj_schema, dict):
            raise ValueError(f"Nested schema '{name}' must be a dictionary.")
        if obj_schema.get("type") != "object":
            raise ValueError(f"Nested schema '{name}' type must be 'object'.")

        props = obj_schema.get("properties", {})
        req = obj_schema.get("required", [])
        if not isinstance(props, dict):
            raise ValueError(f"Nested schema '{name}' properties must be a dictionary.")
        if not isinstance(req, list):
            raise ValueError(f"Nested schema '{name}' required must be a list.")

        fields: Dict[str, Tuple[Any, Any]] = {}
        for prop_name, prop_schema in props.items():
            is_req = prop_name in req
            hint, default = _wrap_optional(prop_schema, is_req, prop_name, name)
            fields[prop_name] = (hint, default)

        return create_model(name, **fields)  # type: ignore

    # Build and return the top-level model
    return _build_model(schema, model_name)


=== File: recipe-executor/recipe_executor/utils/templates.py ===
# This file was generated by Codebase-Generator, do not edit directly
"""
Utility functions for rendering Liquid templates using context data.

This module provides a `render_template` function that uses the Python Liquid templating engine
to render strings with variables sourced from a context object implementing ContextProtocol.
It also registers a custom `snakecase` filter.
"""

import re
from typing import Any

from liquid import Environment
from liquid.exceptions import LiquidError

# Import ContextProtocol inside the module to avoid circular dependencies
from recipe_executor.protocols import ContextProtocol

__all__ = ["render_template"]

# Create a module-level Liquid environment with extra filters enabled
_env = Environment(autoescape=False, extra=True)


def _snakecase(value: Any) -> str:
    """
    Convert a string to snake_case.

    Non-alphanumeric characters are replaced with underscores, camelCase
    boundaries are separated, and result is lowercased.
    """
    s = str(value)
    # Replace spaces and dashes with underscores
    s = re.sub(r"[\s\-]+", "_", s)
    # Insert underscore before capital letters preceded by lowercase/digits
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)
    # Lowercase the string
    s = s.lower()
    # Remove any remaining invalid characters
    s = re.sub(r"[^a-z0-9_]", "", s)
    # Collapse multiple underscores
    s = re.sub(r"__+", "_", s)
    # Strip leading/trailing underscores
    return s.strip("_")


# Register the custom filter
_env.filters["snakecase"] = _snakecase


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Python Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering,
                    includes details about the template and context.
    """
    try:
        template = _env.from_string(text)
        rendered = template.render(**context.dict())
        return rendered
    except LiquidError as e:
        # Liquid-specific errors
        raise ValueError(f"Liquid template rendering error: {e}. Template: {text!r}. Context: {context.dict()!r}")
    except Exception as e:
        # Generic errors
        raise ValueError(f"Error rendering template: {e}. Template: {text!r}. Context: {context.dict()!r}")


