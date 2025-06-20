# Responses Component Specification

## Purpose

The Responses component provides OpenAI built-in tool integration using the PydanticAI Responses API.
It enables recipes to request OpenAI's built-in capabilities (web search, code execution)
via the `openai_responses` provider.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIResponsesModel instance
- Implement basic error handling

## Implementation Considerations

- For the `get_openai_responses_model` function:
  - Return the `OpenAIResponsesModel` instance directly

## Implementation Hints

None

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIResponsesModel`

### Configuration Dependencies

- **DEFAULT_MODEL**: (Optional) Environment variable specifying the default LLM model in format "provider/model_name"
- **OPENAI_API_KEY**: (Required for OpenAI) API key for OpenAI access

## Output Files

- `recipe_executor/llm_utils/responses.py`

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Dependency Integration Considerations

None
