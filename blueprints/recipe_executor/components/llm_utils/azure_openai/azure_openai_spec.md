# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from context configuration instead of environment variables
- The function `get_azure_openai_model` should accept a `context: ContextProtocol` parameter
- Access configuration dictionary through `context.get_config()` method, returning a dictionary with all configuration values
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Create the async client using `openai.AsyncAzureOpenAI` with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
def get_azure_openai_model(model_name: str, deployment_name: Optional[str], context: ContextProtocol) -> OpenAIModel:
    # Get configuration from context
    api_key = context.get_config().get('azure_openai_api_key')
    base_url = context.get_config().get('azure_openai_base_url')
    api_version = context.get_config().get('azure_openai_api_version', '2025-03-01-preview')
    use_managed_identity = context.get_config().get('azure_use_managed_identity', False)

    # Use deployment name from config or parameter or default to model name
    deployment = deployment_name or context.get_config().get('azure_openai_deployment_name', model_name)

    # Option 1: Create AsyncAzureOpenAI client with API key
    if not use_managed_identity and api_key:
        azure_client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=api_version,
            azure_deployment=deployment,
        )

    # Option 2: Create AsyncAzureOpenAI client with Azure Identity
    else:
        client_id = context.get_config().get('azure_client_id')
        # Create token provider using Azure Identity
        azure_client = AsyncAzureOpenAI(
            azure_ad_token_provider=token_provider,
            azure_endpoint=base_url,
            api_version=api_version,
            azure_deployment=deployment,
        )

    # Use the client to create the OpenAIProvider
    openai_model = OpenAIModel(
        model_name,
        provider=OpenAIProvider(openai_client=azure_client),
    )
    return openai_model
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIModel` and `OpenAIProvider` for model management
- **openai**: Uses `AsyncAzureOpenAI` client for API communication
- **azure-identity**: Uses `DefaultAzureCredential`, `ManagedIdentityCredential`, and `get_bearer_token_provider` for token provision

### Configuration Dependencies

All configuration is accessed through context.get_config():

- **azure_use_managed_identity**: (Optional) Boolean flag to use Azure Identity for authentication
- **azure_openai_api_key**: (Required for API key auth) API key for Azure OpenAI authentication
- **azure_openai_base_url**: (Required) Endpoint URL for Azure OpenAI service
- **azure_openai_deployment_name**: (Optional) Deployment name in Azure OpenAI (defaults to model name)
- **azure_openai_api_version**: (Optional) API version to use with Azure OpenAI, defaults to "2025-03-01-preview"
- **azure_client_id**: (Optional) Client ID for managed identity authentication

## Error Handling

- Debug: Log detailed error messages for failed authentication or model creation
- Info: Log successful authentication and model creation

## Output Files

- `recipe_executor/llm_utils/azure_openai.py`
