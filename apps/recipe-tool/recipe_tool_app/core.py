"""Core functionality for the Recipe Tool app."""

import logging
import os
from typing import Any, Dict, List, Optional

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor_app.utils import (
    create_temp_file,
    parse_context_vars,
)

from .path_resolver import find_recipe_creator, prepare_context_paths
from .recipe_processor import find_recipe_output, process_recipe_output


logger = logging.getLogger(__name__)


class RecipeToolCore:
    """Core functionality for Recipe Tool operations."""

    def __init__(self, executor: Optional[Executor] = None, default_model: Optional[str] = None):
        """Initialize with the executor."""
        self.executor = executor if executor is not None else Executor(logger)
        self.default_model = default_model

    async def create_recipe(
        self,
        idea_text: str,
        idea_file: Optional[str],
        reference_files: Optional[List[str]],
        context_vars: Optional[str],
    ) -> Dict:
        """Create a recipe from an idea.

        Args:
            idea_text: Recipe idea as text
            idea_file: Path to file containing recipe idea
            reference_files: List of reference file paths
            context_vars: Context variables as key=value pairs

        Returns:
            Dictionary with recipe_json, structure_preview, and debug_context
        """
        # Determine idea source
        cleanup_fn = None

        if idea_file:
            idea_source = idea_file
        elif idea_text:
            idea_source, cleanup_fn = create_temp_file(idea_text, suffix=".md")
        else:
            return self._error_result("No idea provided")

        try:
            # Prepare context
            context_dict = parse_context_vars(context_vars)
            context_dict = prepare_context_paths(context_dict)

            if self.default_model:
                logger.info(f"Using default model: {self.default_model}")
                context_dict["model"] = self.default_model

            # Add reference files
            if reference_files:
                context_dict["files"] = ",".join(reference_files)

            # Add input
            context_dict["input"] = idea_source

            # Create context
            context = Context(artifacts=context_dict)

            # Find recipe creator
            creator_path = find_recipe_creator()
            if not creator_path:
                return self._error_result("Recipe creator not found")

            # Execute recipe creator
            start_time = os.times().elapsed
            await self.executor.execute(creator_path, context)
            execution_time = os.times().elapsed - start_time

            # Get results
            final_context = context.dict()

            # Find generated recipe
            output_recipe = find_recipe_output(final_context)

            if not output_recipe:
                return {
                    "recipe_json": "",
                    "structure_preview": "### Recipe created\nBut no output found. Check output directory.",
                    "debug_context": final_context,
                }

            # Process and return results
            return process_recipe_output(output_recipe, execution_time, final_context)

        except Exception as e:
            logger.error(f"Error creating recipe: {e}", exc_info=True)
            return self._error_result(str(e))
        finally:
            if cleanup_fn:
                cleanup_fn()

    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Create a standard error result.

        Args:
            error_msg: Error message to display

        Returns:
            Error result dictionary
        """
        return {
            "recipe_json": "",
            "structure_preview": f"### Error\n{error_msg}",
            "debug_context": {"error": error_msg},
        }
