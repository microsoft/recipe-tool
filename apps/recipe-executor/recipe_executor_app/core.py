"""Core functionality for the Recipe Executor app."""

import json
import logging
import os
from typing import Dict, Optional, Any

from recipe_executor.context import Context
from recipe_executor.executor import Executor

from recipe_executor_app.utils import (
    create_temp_file,
    format_results,
    get_main_repo_root,
    get_repo_root,
    parse_context_vars,
    read_file,
    safe_json_dumps,
)

logger = logging.getLogger(__name__)


class RecipeExecutorCore:
    """Core functionality for Recipe Executor operations."""

    def __init__(self, executor: Optional[Executor] = None, default_model: Optional[str] = None):
        """Initialize with the executor."""
        self.executor = executor if executor is not None else Executor(logger)
        self.default_model = default_model

    async def execute_recipe(
        self, recipe_file: Optional[str], recipe_text: Optional[str], context_vars: Optional[str]
    ) -> Dict[str, Any]:
        """Execute a recipe from file or text input."""
        cleanup = None
        try:
            # Parse context
            context_dict = parse_context_vars(context_vars)

            # Add default paths if not provided by user
            repo_root = get_repo_root()
            main_repo_root = get_main_repo_root()

            # Only set defaults if they weren't provided
            if "recipe_root" not in context_dict and main_repo_root:
                context_dict["recipe_root"] = os.path.join(main_repo_root, "recipes")

            if "output_root" not in context_dict:
                context_dict["output_root"] = os.path.join(repo_root, "output")

            # Ensure output directory exists
            if "output_root" in context_dict:
                os.makedirs(context_dict["output_root"], exist_ok=True)

            context = Context(artifacts=context_dict)

            # Determine recipe source
            if recipe_file:
                recipe_source = recipe_file
            elif recipe_text:
                # Save to temp file
                recipe_source, cleanup = create_temp_file(recipe_text, suffix=".json")
            else:
                return {
                    "formatted_results": "### Error\nNo recipe provided.",
                    "raw_json": "{}",
                    "debug_context": {},
                }

            # Execute recipe
            start_time = os.times().elapsed
            if self.default_model:
                logger.info(f"Using default model: {self.default_model}")
                context["model"] = self.default_model

            await self.executor.execute(recipe_source, context)
            execution_time = os.times().elapsed - start_time

            # Get results
            all_artifacts = context.dict()

            # Extract string results
            results = {}
            for key, value in all_artifacts.items():
                if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
                    results[key] = value

            return {
                "formatted_results": format_results(results, execution_time),
                "raw_json": safe_json_dumps(all_artifacts),
                "debug_context": all_artifacts,
            }

        except Exception as e:
            logger.error(f"Error executing recipe: {e}", exc_info=True)
            return {
                "formatted_results": f"### Error\n\n```\n{str(e)}\n```",
                "raw_json": "{}",
                "debug_context": {"error": str(e)},
            }
        finally:
            # Clean up temp file if created
            if cleanup:
                cleanup()

    async def load_recipe(self, recipe_path: str) -> Dict[str, str]:
        """Load a recipe file and return content with preview."""
        try:
            # Try different path resolutions
            repo_root = get_repo_root()
            main_repo_root = get_main_repo_root()

            paths_to_try = [
                recipe_path,
                os.path.join(repo_root, recipe_path),
                os.path.join(repo_root, "recipes", recipe_path),
            ]

            # Add main repo paths if available
            if main_repo_root:
                paths_to_try.extend([
                    os.path.join(main_repo_root, "recipes", recipe_path),
                    os.path.join(main_repo_root, recipe_path),
                ])

            for path in paths_to_try:
                if os.path.exists(path):
                    content = read_file(path)

                    # Parse to validate and extract info
                    recipe = json.loads(content)
                    name = recipe.get("name", os.path.basename(path))
                    desc = recipe.get("description", "No description")
                    steps = len(recipe.get("steps", []))

                    preview = f"""### Recipe: {name}

**Description**: {desc}
**Steps**: {steps}
**Path**: {path}"""

                    return {
                        "recipe_content": content,
                        "structure_preview": preview,
                    }

            return {
                "recipe_content": "",
                "structure_preview": f"### Error\nCould not find recipe at: {recipe_path}",
            }

        except Exception as e:
            logger.error(f"Error loading recipe: {e}")
            return {
                "recipe_content": "",
                "structure_preview": f"### Error\n{str(e)}",
            }
