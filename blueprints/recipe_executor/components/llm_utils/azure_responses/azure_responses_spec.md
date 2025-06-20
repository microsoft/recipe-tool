# Azure Responses Component Specification

## Purpose

The Azure Responses component provides a PydanticAI wrapper for Azure OpenAI Responses API models for use with PydanticAI Agents. It handles model initialization, authentication, and built-in tools configuration.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIResponsesModel instance for Azure OpenAI
- Use proper Azure OpenAI authentication (API key or Azure Identity)
- Support Azure OpenAI endpoints and deployments
- Implement basic error handling and parameter validation
- Export `get_azure_responses_model` function
- Follow same patterns as existing `azure_openai` component

## Implementation Considerations

- Use `OpenAIResponsesModel` with `provider='azure'` parameter
- Create `AsyncAzureOpenAI` client following same patterns as `azure_openai` component
- Pass Azure client via `OpenAIProvider(openai_client=azure_client)`
- Support both API key and Azure Identity authentication
- Return a `pydantic_ai.models.openai.OpenAIResponsesModel` configured for Azure

## Implementation Hints

```python
# Use sync credentials for token provider (important for Azure AD)
if use_managed_identity:
    credential = DefaultAzureCredential()  # sync, not async
    token_provider = get_bearer_token_provider(credential, scope)
    azure_client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_OPENAI_BASE_URL,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_ad_token_provider=token_provider,
    )
else:
    azure_client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_OPENAI_BASE_URL,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,
    )

# Create Azure Responses model
model = OpenAIResponsesModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIResponsesModel` for model management
- **openai**: Uses `AsyncAzureOpenAI` client for API communication
- **azure-identity**: Uses `DefaultAzureCredential`, `ManagedIdentityCredential`, and `get_bearer_token_provider` for token provision

### Configuration Dependencies

- **AZURE_USE_MANAGED_IDENTITY**: (Optional) Boolean flag to use Azure Identity for authentication
- **AZURE_OPENAI_API_KEY**: (Required for API key auth) API key for Azure OpenAI authentication
- **AZURE_OPENAI_BASE_URL**: (Required) Endpoint URL for Azure OpenAI service
- **AZURE_OPENAI_DEPLOYMENT_NAME**: (Required) Deployment name in Azure OpenAI
- **AZURE_OPENAI_API_VERSION**: (Required) API version to use with Azure OpenAI, defaults to "2025-03-01-preview"
- **AZURE_CLIENT_ID**: (Optional) Client ID for managed identity authentication

## Error Handling

- Debug: Log detailed error messages for failed authentication or model creation
- Info: Log successful authentication and model creation

## Output Files

- `recipe_executor/llm_utils/azure_responses.py`

## Dependency Integration Considerations

None
