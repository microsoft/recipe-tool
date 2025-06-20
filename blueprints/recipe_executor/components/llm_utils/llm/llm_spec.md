# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers and optional MCP servers. It handles model initialization, request formatting, and result processing, enabling the Recipe Executor to generate content and orchestrate external tools through a single API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Ollama, OpenAI Responses, Azure Responses)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI's async interface for non-blocking LLM calls
- Use PydanticAI for consistent handling and validation of LLM output
- Implement basic error handling
- Support optional structured output format
- Accept an optional `mcp_servers: Optional[List[MCPServer]]` to enable remote MCP tool integration

## Implementation Hints

- Use a clear `provider/model_name` identifier format
- Configuration values are accessed through context.get_config() instead of directly from environment
- For API key handling:
  - OpenAI: Create OpenAIProvider with api_key from context, pass to OpenAIModel
  - Anthropic: Create AnthropicProvider with api_key from context, pass to AnthropicModel
  - Azure: Handled by get_azure_openai_model function
  - Ollama: Create OpenAIProvider with base_url from context
- Use PydanticAI's provider-specific model classes:
  - pydantic_ai.models.openai.OpenAIModel (used also for Azure OpenAI and Ollama)
  - pydantic_ai.models.anthropic.AnthropicModel
- For `openai_responses` provider: call `get_openai_responses_model(model_name)` which returns the model directly
- For `azure_responses` provider: call `get_azure_responses_model(model_name, deployment_name)` which returns the model directly
- Create a PydanticAI Agent with the model, structured output type, and optional MCP servers
- Support: `output_type: Type[Union[str, BaseModel]] = str`
- Support: `openai_builtin_tools: Optional[List[Dict[str, Any]]] = None` parameter for built-in tools with Responses API models
  - We only want to support `WebSearchToolParam` and `FileSearchToolParam` at this
- Pass provided `mcp_servers` (or empty list) to the Agent constructor (e.g. `Agent(model, mcp_servers=mcp_servers, output_type=output_type)`)
- For Responses API models with built-in tools, configure the model with `OpenAIResponsesModelSettings` that includes properly typed tools
- Convert raw dict tools to PydanticAI tool parameter types (e.g., `WebSearchToolParam`, which are TypedDict) before passing to `OpenAIResponsesModelSettings`
- Import required tool parameter types from `pydantic_ai.models.openai` for type conversion
- Implement fully asynchronous execution with the following signature:
  ```python
  async def generate(
      self,
      prompt: str,
      model: Optional[str] = None,
      max_tokens: Optional[int] = None,
      output_type: Type[Union[str, BaseModel]] = str,
      mcp_servers: Optional[List[MCPServer]] = None,
      openai_builtin_tools: Optional[List[Dict[str, Any]]] = None,
  ) -> Union[str, BaseModel]:
  ```
  - Use `await agent.run(prompt)` method of the Agent to make requests
- CRITICAL: make sure to return the `result.output` in the `generate` method to return only the structured output

### PydanticAI Model Creation

Create a PydanticAI model for the LLM provider and model name:

```python
def get_model(model_id: str, context: ContextProtocol) -> OpenAIModel | AnthropicModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.

    Supported providers:
    - openai
    - azure (for Azure OpenAI, use 'azure/model_name/deployment_name' or 'azure/model_name')
    - anthropic
    - ollama
    - openai_responses (for OpenAI Responses API with built-in tools)
    - azure_responses (for Azure Responses API with built-in tools)

    Args:
        model_id (str): Model identifier in format 'provider/model_name'
            or 'provider/model_name/deployment_name'.
            If None, defaults to 'openai/gpt-4o'.
        context (ContextProtocol): Context containing configuration values.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """

    # If 'azure' is the model provider, use the `get_azure_openai_model` function
    # Access configuration dictionary through context.get_config() and then retrieve the necessary values
    # If 'openai_responses' is the model provider, use the `get_openai_responses_model` function from responses component
    # If 'azure_responses' is the model provider, use the `get_azure_responses_model` function from azure_responses component
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai/gpt-4o", context)
# Uses OpenAIModel('gpt-4o') with API key from context.get_config().get('openai_api_key')

# Get an Anthropic model
anthropic_model = get_model("anthropic/claude-3-5-sonnet-latest", context)
# Uses AnthropicModel('claude-3-5-sonnet-latest') with API key from context.get_config().get('anthropic_api_key')

# Get an Ollama model
ollama_model = get_model("ollama/phi4", context)
# Uses OllamaModel('phi4') with base URL from context.get_config().get('ollama_base_url')

# Get an OpenAI Responses model
responses_model = get_model("openai_responses/gpt-4o", context)
# Uses get_openai_responses_model('gpt-4o') from responses component

# Get an Azure Responses model
azure_responses_model = get_model("azure_responses/gpt-4o", context)
# Uses get_azure_responses_model('gpt-4o', None) from azure_responses component

# Get an Azure Responses model with deployment
azure_responses_model = get_model("azure_responses/gpt-4o/my-deployment", context)
# Uses get_azure_responses_model('gpt-4o', 'my-deployment') from azure_responses component
```

Getting an agent:

```python
from pydantic_ai import Agent

# Create an agent with the model
agent: Agent[None, Union[str, BaseModel]] = Agent(model=ollama_model, output_type=str, mcp_servers=mcp_servers)

# Call the agent with a prompt
async with agent.run_mcp_servers():
  result = await agent.run("What is the capital of France?")

# Process the result
print(result.data)  # This will print the structured output
```

### Ollama Integration

The Ollama model requires an endpoint to be specified:

```python
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers import OpenAIProvider

# inside the get_model function, context is passed as parameter
ollama_base_url = context.get_config().get('ollama_base_url', 'http://localhost:11434')

return OpenAIModel(
    model_name='qwen2.5-coder:7b',
    provider=OpenAIProvider(base_url=f'{ollama_base_url}/v1'),
)
```

## Logging

- Debug: Log full request payload before making call and then full result payload after receiving it, making sure to mask any sensitive information (e.g. API keys, secrets, etc.)
- Info: Log model name and provider before making call (do not include the request payload details) and then include processing times and tokens used upon completion (do not include the result payload details)

## Component Dependencies

### Internal Components

- **Azure OpenAI**: Uses `get_azure_openai_model` for Azure OpenAI model initialization
- **Responses**: Uses `get_openai_responses_model` for OpenAI Responses API model initialization
- **Azure Responses**: Uses `get_azure_responses_model` for Azure Responses API model initialization
- **Logger**: Uses the logger for logging LLM calls
- **MCP**: Integrates remote MCP tools when `mcp_servers` are provided (uses `pydantic_ai.mcp`)

### External Libraries

- **pydantic-ai**: Uses PydanticAI for model initialization, Agent-based request handling, and structured-output processing
- **pydantic-ai.mcp**: Provides `MCPServer`, `MCPServerHTTP` and `MCPServerStdio` classes for MCP server transports
- **openai.types.responses**: Provides types for the responses API `WebSearchToolParam`, `FileSearchToolParam`

### Configuration Dependencies

- **context.config** - All configuration is accessed through the context:
  - `openai_api_key`: (Required for OpenAI) API key for OpenAI access
  - `anthropic_api_key`: (Required for Anthropic) API key for Anthropic access
  - `ollama_base_url`: (Required for Ollama) Endpoint for Ollama models
  - `azure_*`: Azure OpenAI configuration values (handled by azure_openai component)

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `recipe_executor/llm_utils/llm.py`

## Dependency Integration Considerations

Implement a standardized `get_model` function that routes to appropriate provider-specific model creation functions based on the provider prefix in the model identifier. Use existing component functions for Azure OpenAI, Responses API, and Azure Responses API integration.
