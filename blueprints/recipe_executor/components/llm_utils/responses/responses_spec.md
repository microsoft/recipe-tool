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

None

## Output Files

- `recipe_executor/llm_utils/responses.py`

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name

## Error Handling

- Handle model initialization errors gracefully with clear error messages

## Dependency Integration Considerations

None
