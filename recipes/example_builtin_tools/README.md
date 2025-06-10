# Built-in Tools Examples

This directory contains example recipes demonstrating the use of OpenAI's built-in tools with the Recipe Tool.

## What are Built-in Tools?

Built-in tools are OpenAI's Responses API features that provide models with access to:
- **Web Search** (`web_search_preview`) - Search the web for current information

## Model Support

Built-in tools are only supported with Responses API models:
- `openai_responses/*` - OpenAI Responses API models
- `azure_responses/*` - Azure OpenAI Responses API models

## Examples

### Web Search Demo (`web_search_demo.json`)
Demonstrates using the web search tool to find current information about Python 3.13 features.

**Usage:**
```bash
# With OpenAI
recipe-tool --execute recipes/example_builtin_tools/web_search_demo.json model=openai_responses/gpt-4o

# With Azure OpenAI  
recipe-tool --execute recipes/example_builtin_tools/web_search_demo.json model=azure_responses/gpt-4o
```


## Recipe Structure

Built-in tools are specified using the `openai_builtin_tools` parameter in `llm_generate` steps:

```json
{
  "step_type": "llm_generate",
  "model": "openai_responses/gpt-4o",
  "openai_builtin_tools": [
    {"type": "web_search_preview"}
  ]
}
```

## Error Handling

- Built-in tools only work with `*_responses` models
- Only `web_search_preview` tool type is currently supported
- Clear error messages will be shown for invalid configurations