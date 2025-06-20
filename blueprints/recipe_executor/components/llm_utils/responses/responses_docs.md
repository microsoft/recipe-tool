# Responses Component Documentation

The Responses component provides OpenAI built-in tool integration for Recipe Executor.

## Overview

This component handles OpenAI's Responses API built-in tools (web search, code execution)
by creating configured `OpenAIResponsesModel` instances with appropriate tool settings.

## Importing

```python
from recipe_executor.llm_utils.responses import get_openai_responses_model
```

## Basic Usage

```python
def get_openai_responses_model(
    logger: logging.Logger,
    model_name: str,
) -> pydantic_ia.models.openai.OpenAIResponsesModel:
    """
    Create an OpenAIResponsesModel for the given model name.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name: Name of the model (e.g., "gpt-4o").

    Returns:
        OpenAIResponsesModel: A PydanticAI OpenAIResponsesModel instance .

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
model = get_openai_responses_model("gpt-4o")
# Use with PydanticAI Agent

from pydantic_ai import Agent
agent = Agent(model=model)
result = await agent.run("Hello, what can you do with the Responses API?")
```
