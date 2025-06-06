# Azure OpenAI Component Usage

## Importing

```python
from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
```

## Basic Usage

```python
def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str],
    context: ContextProtocol,
) -> pydantic_ai.models.openai.OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from context configuration for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o4-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.
        context (ContextProtocol): Context containing configuration values.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
# Get an OpenAI model using Azure OpenAI
openai_model = get_azure_openai_model(
    logger=logger,
    model_name="gpt-4o",
    deployment_name=None,
    context=context
)
```

# Get an OpenAI model using Azure OpenAI with a specific deployment name

```python
openai_model = get_azure_openai_model(
    logger=logger,
    model_name="o4-mini",
    deployment_name="my_deployment_name",
    context=context
)
```

## Configuration

The component accesses configuration through context.get_config(). The configuration values are typically loaded from environment variables by the Config component.

### Required Environment Variables

Depending on your authentication method:

#### Option 1: API Key Authentication
- `AZURE_OPENAI_API_KEY` - API key for Azure OpenAI
- `AZURE_OPENAI_BASE_URL` - Base URL for Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION` - (Optional) API version, defaults to "2025-03-01-preview"
- `AZURE_OPENAI_DEPLOYMENT_NAME` - (Optional) Deployment name, defaults to model_name

#### Option 2: Managed Identity
- `AZURE_USE_MANAGED_IDENTITY=true` - Enable managed identity authentication
- `AZURE_OPENAI_BASE_URL` - Base URL for Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION` - (Optional) API version, defaults to "2025-03-01-preview"
- `AZURE_OPENAI_DEPLOYMENT_NAME` - (Optional) Deployment name, defaults to model_name
- `AZURE_CLIENT_ID` - (Optional) Specific managed identity client ID
