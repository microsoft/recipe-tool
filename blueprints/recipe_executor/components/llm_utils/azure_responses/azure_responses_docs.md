# Azure Responses Component Documentation

The Azure Responses component provides Azure OpenAI built-in tool integration for Recipe Executor.

## Overview

This component handles Azure OpenAI's Responses API built-in tools (web search, code execution) 
by creating configured `OpenAIResponsesModel` instances with Azure authentication and appropriate tool settings.

## Usage

### Basic Usage (Phase 2)

```python
from recipe_executor.llm_utils.azure_responses import create_azure_responses_model

# Create basic Azure responses model
model = create_azure_responses_model("gpt-4o")

# Use with PydanticAI Agent
from pydantic_ai import Agent
agent = Agent(model=model)
result = await agent.run("Hello, what can you do with the Azure Responses API?")
```

### Phase 3 Features (Future)

Built-in tools support (web search, code execution) will be added in Phase 3 via the `llm_generate` step, not in this component.

## Integration with LLM Component

The LLM component routes `azure_responses/*` model identifiers to this component:

```python
# In llm.py get_model() function:
if provider == "azure_responses":
    from recipe_executor.llm_utils.azure_responses import create_azure_responses_model
    model_name = parts[1]
    deployment_name = parts[2] if len(parts) > 2 else None
    model = create_azure_responses_model(model_name, deployment_name)
    return model
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

## Phase 2 Scope

Provides full Azure OpenAI Responses API model creation with proper Azure authentication and endpoint configuration. Built-in tools (web search, code execution) will be added in Phase 3.

## Error Handling

- **Model initialization errors**: Clear error messages for Azure OpenAI model creation failures
- **Authentication errors**: Detailed error messages for Azure Identity or API key issues
- **Invalid model names**: Validation errors with helpful context