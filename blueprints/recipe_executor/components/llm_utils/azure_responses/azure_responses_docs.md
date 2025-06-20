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
