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