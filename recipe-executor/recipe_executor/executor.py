import os
import logging
import inspect
from pathlib import Path
from typing import Union, Dict, Any

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.models import Recipe
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Concrete implementation of ExecutorProtocol. Loads, validates, and executes
    recipes step by step using a shared context. Stateless between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load a recipe (from file path, JSON string, dict, or Recipe model),
        validate it, and execute its steps sequentially using the provided context.
        """
        # Load or use provided Recipe model
        if isinstance(recipe, Recipe):
            self.logger.debug("Using provided Recipe model instance.")
            recipe_model = recipe
        else:
            # Path input
            if isinstance(recipe, Path):
                path_str = str(recipe)
                if not recipe.exists():
                    raise ValueError(f"Recipe file not found: {path_str}")
                self.logger.debug(f"Loading recipe from file path: {path_str}")
                try:
                    content = recipe.read_text(encoding="utf-8")
                except Exception as e:
                    raise ValueError(f"Failed to read recipe file {path_str}: {e}") from e
                try:
                    recipe_model = Recipe.model_validate_json(content)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON from file {path_str}: {e}") from e
            # String input: file path or JSON
            elif isinstance(recipe, str):
                if os.path.isfile(recipe):
                    self.logger.debug(f"Loading recipe from file path: {recipe}")
                    try:
                        content = Path(recipe).read_text(encoding="utf-8")
                    except Exception as e:
                        raise ValueError(f"Failed to read recipe file {recipe}: {e}") from e
                    try:
                        recipe_model = Recipe.model_validate_json(content)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON from file {recipe}: {e}") from e
                else:
                    self.logger.debug("Loading recipe from JSON string.")
                    try:
                        recipe_model = Recipe.model_validate_json(recipe)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON string: {e}") from e
            # Dict input
            elif isinstance(recipe, dict):
                self.logger.debug("Loading recipe from dict.")
                try:
                    recipe_model = Recipe.model_validate(recipe)
                except Exception as e:
                    raise ValueError(f"Invalid recipe structure: {e}") from e
            else:
                raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Log recipe summary
        try:
            summary = recipe_model.model_dump()
        except Exception:
            summary = {}
        step_count = len(getattr(recipe_model, "steps", []))
        self.logger.debug(f"Recipe loaded: {summary}. Steps count: {step_count}")

        # Execute each step sequentially
        for idx, step in enumerate(recipe_model.steps):  # type: ignore
            step_type = step.type
            config = step.config or {}
            self.logger.debug(f"Executing step {idx} of type '{step_type}' with config: {config}")

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_cls = STEP_REGISTRY[step_type]
            step_instance = step_cls(self.logger, config)

            try:
                result = step_instance.execute(context)
                if inspect.isawaitable(result):  # type: ignore
                    await result
            except Exception as e:
                msg = f"Error executing step {idx} ('{step_type}'): {e}"
                raise ValueError(msg) from e

            self.logger.debug(f"Step {idx} ('{step_type}') completed successfully.")

        self.logger.debug("All recipe steps completed successfully.")
