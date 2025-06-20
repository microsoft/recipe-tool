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
