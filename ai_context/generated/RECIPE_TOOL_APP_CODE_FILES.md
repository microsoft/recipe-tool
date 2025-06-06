# apps/recipe-tool/recipe_tool_app

[collect-files]

**Search:** ['apps/recipe-tool/recipe_tool_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/4/2025, 2:36:24 PM
**Files:** 8

=== File: apps/recipe-tool/recipe_tool_app/__init__.py ===
"""Gradio web app for the Recipe Tool."""

__version__ = "0.1.0"


=== File: apps/recipe-tool/recipe_tool_app/app.py ===
"""Recipe Tool Gradio app."""

import argparse
from typing import Any, Dict

import gradio as gr
import gradio.themes
from recipe_executor.logger import init_logger
from recipe_executor_app.app import create_executor_block
from recipe_executor_app.core import RecipeExecutorCore

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore
from recipe_tool_app.ui import create_recipe_ui
from recipe_tool_app.settings_sidebar import create_settings_sidebar

# Set up logging
logger = init_logger(settings.log_dir)
logger.setLevel(settings.log_level.upper())


def create_app() -> gr.Blocks:
    """Create the Recipe Tool app."""
    recipe_core = RecipeToolCore()
    theme = gradio.themes.Soft() if settings.theme == "soft" else None  # type: ignore

    with gr.Blocks(title=settings.app_title, theme=theme) as app:
        gr.Markdown("# Recipe Tool")
        gr.Markdown("A web interface for executing and creating recipes.")

        # Settings sidebar
        with gr.Sidebar(position="right"):
            gr.Markdown("### ⚙️ Settings")

            def on_settings_save(saved_settings: Dict[str, Any]) -> None:
                """Handle settings updates."""
                logger.info(
                    f"Settings updated: model={saved_settings.get('model')}, max_tokens={saved_settings.get('max_tokens')}"
                )

            create_settings_sidebar(on_save=on_settings_save)

        with gr.Tabs():
            # Create Recipe Tab
            with gr.TabItem("Create Recipe"):
                create_recipe_ui(recipe_core)

            # Execute Recipe Tab (reuse from recipe-executor)
            with gr.TabItem("Execute Recipe"):
                executor_core = RecipeExecutorCore()
                create_executor_block(executor_core, include_header=False)

    return app


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host (default: {settings.host})")
    parser.add_argument("--port", type=int, help="Port")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    # Override settings
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True

    # Launch app
    app = create_app()
    app.launch(**settings.to_launch_kwargs())


if __name__ == "__main__":
    main()


=== File: apps/recipe-tool/recipe_tool_app/config.py ===
"""Configuration settings for the Recipe Tool app."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExampleIdea(BaseModel):
    """Configuration for an example recipe idea."""

    name: str
    path: str
    context_vars: Dict[str, str] = {}


class Settings(BaseSettings):
    """Configuration settings for the Recipe Tool app."""

    # App settings
    app_title: str = "Recipe Tool"
    app_description: str = "A web interface for executing and creating recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port
    # Queue is enabled by default in Gradio

    # MCP settings
    mcp_server: bool = True

    # Recipe tool settings
    log_dir: str = "logs"
    log_level: str = (
        "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL - Set to DEBUG for detailed path information
    )

    # Example ideas (for recipe creator)
    example_ideas: List[ExampleIdea] = [
        ExampleIdea(
            name="Simple Spec to Python",
            path="../../recipes/recipe_creator/examples/simple-spec-recipe-idea.md",
            context_vars={
                "output_root": "./output",
            },
        ),
        ExampleIdea(
            name="Quarterly Report Generator",
            path="../../recipes/recipe_creator/examples/demo-quarterly-report-idea.md",
            context_vars={},
        ),
        ExampleIdea(
            name="Recipe to Mermaid Diagram",
            path="../../recipes/recipe_creator/examples/recipe-to-mermaid-idea.md",
        ),
        ExampleIdea(
            name="Analyze Code Files",
            path="../../recipes/recipe_creator/examples/analyze-code-files-idea.md",
        ),
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables like PYTHONPATH
    )

    def to_launch_kwargs(self) -> Dict[str, Any]:
        """Convert settings to kwargs for gradio launch() method."""
        return {
            "server_name": self.host,
            "server_port": self.port,
            "share": False,
            "pwa": True,
            "debug": self.debug,
            "mcp_server": self.mcp_server,
        }


# Create global settings instance
settings = Settings()


=== File: apps/recipe-tool/recipe_tool_app/core.py ===
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

    def __init__(self, executor: Optional[Executor] = None):
        """Initialize with the executor."""
        self.executor = executor if executor is not None else Executor(logger)

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


=== File: apps/recipe-tool/recipe_tool_app/path_resolver.py ===
"""Path resolution utilities for Recipe Tool.

This module handles all path-related operations including finding recipe roots,
output directories, and resolving file paths.
"""

import os
from typing import Dict, Optional


def get_recipe_paths() -> Dict[str, str]:
    """Get common recipe-related paths.

    Returns:
        Dictionary with recipe_root, ai_context_root, and output_root paths.
    """
    from recipe_executor_app.utils import get_repo_root, get_main_repo_root

    # Get the current app's repo root
    app_root = get_repo_root()
    main_repo_root = get_main_repo_root()

    # Fallback to app root if not found
    if not main_repo_root:
        main_repo_root = app_root

    return {
        "recipe_root": os.path.join(main_repo_root, "recipes"),
        "ai_context_root": os.path.join(main_repo_root, "ai_context"),
        "output_root": os.path.join(app_root, "output"),
    }


def prepare_context_paths(context_dict: Dict[str, str]) -> Dict[str, str]:
    """Add default paths to context dictionary if not present.

    Args:
        context_dict: Context dictionary to update

    Returns:
        Updated context dictionary with default paths
    """
    paths = get_recipe_paths()

    # Add defaults if not present
    for key, value in paths.items():
        context_dict.setdefault(key, value)

    # Ensure output directory exists
    os.makedirs(context_dict["output_root"], exist_ok=True)

    return context_dict


def find_recipe_creator() -> Optional[str]:
    """Find the recipe creator path.

    Returns:
        Path to recipe creator or None if not found
    """
    paths = get_recipe_paths()
    creator_path = os.path.join(paths["recipe_root"], "recipe_creator/create.json")

    return creator_path if os.path.exists(creator_path) else None


def resolve_output_path(output_root: str, target_file: str) -> str:
    """Resolve the full path for an output file.

    Args:
        output_root: Root output directory
        target_file: Target filename (can be relative or absolute)

    Returns:
        Resolved absolute path
    """
    if os.path.isabs(target_file):
        return target_file
    return os.path.join(output_root, target_file)


=== File: apps/recipe-tool/recipe_tool_app/recipe_processor.py ===
"""Recipe processing utilities for Recipe Tool.

This module handles recipe output finding, parsing, and preview generation.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from recipe_executor_app.utils import read_file


logger = logging.getLogger(__name__)


def find_recipe_output(context_dict: Dict[str, Any]) -> Optional[str]:
    """Find the recipe output from the generated file.

    Args:
        context_dict: Context dictionary from recipe execution

    Returns:
        Recipe JSON content or None if not found
    """
    # Get the generated recipe path from context
    if "generated_recipe" not in context_dict:
        logger.error("No generated_recipe in context")
        return None

    generated_recipe = context_dict["generated_recipe"]
    if not isinstance(generated_recipe, list) or not generated_recipe:
        logger.error(f"generated_recipe is not a list or is empty: {type(generated_recipe)}")
        return None

    # Get the first generated recipe file (FileSpec object)
    first_recipe = generated_recipe[0]

    # Extract path from FileSpec object
    if not hasattr(first_recipe, "path"):
        logger.error(f"Recipe item doesn't have path attribute: {type(first_recipe)}")
        return None

    recipe_filename = first_recipe.path

    # Build the full path
    output_root = context_dict.get("output_root", "output")
    file_path = os.path.join(output_root, recipe_filename)

    # Read the file
    try:
        content = read_file(file_path)
        logger.info(f"Successfully read generated recipe from: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to read generated recipe from {file_path}: {e}")
        return None


def generate_preview(recipe: Dict[str, Any], execution_time: float) -> str:
    """Generate a markdown preview of the recipe.

    Args:
        recipe: Parsed recipe dictionary
        execution_time: Time taken to execute recipe

    Returns:
        Markdown formatted preview string
    """
    preview = "### Recipe Structure\n\n"
    preview += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

    if "name" in recipe:
        preview += f"**Name**: {recipe['name']}\n\n"

    if "description" in recipe:
        preview += f"**Description**: {recipe['description']}\n\n"

    if "steps" in recipe and isinstance(recipe["steps"], list):
        preview += f"**Steps**: {len(recipe['steps'])}\n\n"
        preview += "| # | Type | Description |\n"
        preview += "|---|------|-------------|\n"

        for i, step in enumerate(recipe["steps"]):
            step_type = step.get("type", "unknown")
            desc = step.get("config", {}).get("description", step.get("description", ""))
            preview += f"| {i + 1} | {step_type} | {desc} |\n"

    return preview


def process_recipe_output(output_recipe: str, execution_time: float, context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Process recipe output and generate result dictionary.

    Args:
        output_recipe: Recipe JSON string
        execution_time: Time taken to execute
        context_dict: Final context dictionary

    Returns:
        Result dictionary with recipe_json, structure_preview, and debug_context
    """
    try:
        recipe = json.loads(output_recipe)
        preview = generate_preview(recipe, execution_time)

        return {
            "recipe_json": output_recipe,
            "structure_preview": preview,
            "debug_context": context_dict,
        }
    except json.JSONDecodeError:
        return {
            "recipe_json": output_recipe,
            "structure_preview": f"### Recipe Created\n\n**Time**: {execution_time:.2f}s\n\nWarning: Invalid JSON",
            "debug_context": context_dict,
        }


=== File: apps/recipe-tool/recipe_tool_app/settings_sidebar.py ===
"""Reusable settings sidebar component for Gradio apps."""

import os
from typing import Any, Callable, Dict, List, Optional

import gradio as gr
from pydantic import BaseModel


class SettingsConfig(BaseModel):
    """Configuration for the settings sidebar."""

    # Model settings
    model_providers: List[str] = ["openai", "azure", "anthropic", "ollama"]
    default_model: str = "openai/gpt-4o"

    # Environment variable definitions
    env_vars: Dict[str, Dict[str, Any]] = {
        # OpenAI
        "OPENAI_API_KEY": {
            "label": "OpenAI API Key",
            "type": "password",
            "provider": "openai",
            "required": True,
        },
        # Anthropic
        "ANTHROPIC_API_KEY": {
            "label": "Anthropic API Key",
            "type": "password",
            "provider": "anthropic",
            "required": True,
        },
        # Azure OpenAI
        "AZURE_OPENAI_BASE_URL": {
            "label": "Azure OpenAI Base URL",
            "type": "text",
            "provider": "azure",
            "required": True,
            "placeholder": "https://your-resource.openai.azure.com/",
        },
        "AZURE_OPENAI_API_KEY": {
            "label": "Azure OpenAI API Key",
            "type": "password",
            "provider": "azure",
            "required": False,  # Not required if using managed identity
        },
        "AZURE_OPENAI_API_VERSION": {
            "label": "Azure API Version",
            "type": "text",
            "provider": "azure",
            "default": "2025-03-01-preview",
            "required": False,
        },
        "AZURE_USE_MANAGED_IDENTITY": {
            "label": "Use Azure Managed Identity",
            "type": "checkbox",
            "provider": "azure",
            "default": False,
            "required": False,
        },
        "AZURE_MANAGED_IDENTITY_CLIENT_ID": {
            "label": "Azure Managed Identity Client ID",
            "type": "text",
            "provider": "azure",
            "required": False,
            "placeholder": "Optional - specific managed identity to use",
        },
        # Ollama
        "OLLAMA_BASE_URL": {
            "label": "Ollama Base URL",
            "type": "text",
            "provider": "ollama",
            "default": "http://localhost:11434",
            "required": False,
        },
        # General
        "LOG_LEVEL": {
            "label": "Log Level",
            "type": "dropdown",
            "provider": None,
            "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "default": "INFO",
            "required": False,
        },
    }

    # Model configurations
    model_configs: Dict[str, List[str]] = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "azure": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
        "ollama": ["llama3.2", "mistral", "gemma2", "phi3"],
    }


def create_settings_sidebar(
    config: Optional[SettingsConfig] = None,
    on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Create settings components for the Gradio sidebar.

    Args:
        config: Settings configuration (uses defaults if not provided)
        on_save: Optional callback when settings are saved

    Returns:
        Dict of component references
    """
    if config is None:
        config = SettingsConfig()

    components = {}

    with gr.Accordion("Model Configuration", open=True):
        # Model provider dropdown
        provider = gr.Dropdown(
            label="Model Provider",
            choices=config.model_providers,
            value=config.default_model.split("/")[0],
            interactive=True,
        )
        components["provider"] = provider

        # Model selection (dynamic based on provider)
        model_name = gr.Dropdown(
            label="Model",
            choices=config.model_configs.get(config.default_model.split("/")[0], []),
            value=config.default_model.split("/")[1] if "/" in config.default_model else "",
            interactive=True,
        )
        components["model_name"] = model_name

        # Azure deployment name (only shown for Azure)
        azure_deployment = gr.Textbox(
            label="Azure Deployment Name",
            placeholder="Optional - defaults to model name",
            visible=False,
            interactive=True,
        )
        components["azure_deployment"] = azure_deployment

        # Max tokens
        max_tokens = gr.Number(
            label="Max Tokens",
            value=None,
            minimum=1,
            maximum=128000,
            step=1,
            interactive=True,
            info="Leave empty for model default",
        )
        components["max_tokens"] = max_tokens

    with gr.Accordion("API Configuration", open=False):
        # Create inputs for each environment variable
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")

            # Determine visibility based on provider
            visible = provider_match is None or provider_match == config.default_model.split("/")[0]

            if var_config["type"] == "password":
                component = gr.Textbox(
                    label=var_config["label"],
                    type="password",
                    value=os.getenv(var_name, ""),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "checkbox":
                default_val = var_config.get("default", False)
                env_val = os.getenv(var_name, "").lower() in ("1", "true", "yes")
                component = gr.Checkbox(
                    label=var_config["label"],
                    value=env_val if os.getenv(var_name) else default_val,
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "dropdown":
                component = gr.Dropdown(
                    label=var_config["label"],
                    choices=var_config.get("choices", []),
                    value=os.getenv(var_name, var_config.get("default", "")),
                    visible=visible,
                    interactive=True,
                )
            else:  # text
                component = gr.Textbox(
                    label=var_config["label"],
                    value=os.getenv(var_name, var_config.get("default", "")),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )

            components[var_name] = component

    # Save and status
    with gr.Row():
        save_btn = gr.Button("💾 Save Settings", variant="primary", scale=2)
        components["save_btn"] = save_btn

    status = gr.Markdown("", visible=False)
    components["status"] = status

    # Set up event handlers
    def update_model_choices(provider: str) -> Dict[str, Any]:
        """Update model choices based on provider selection."""
        models = config.model_configs.get(provider, [])
        updates = {
            "model_name": gr.update(choices=models, value=models[0] if models else ""),
            "azure_deployment": gr.update(visible=(provider == "azure")),
        }

        # Update visibility of provider-specific settings
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")
            if provider_match is not None:
                visible = provider_match == provider
                updates[var_name] = gr.update(visible=visible)

        return updates

    # Connect provider change to update function
    outputs = [components["model_name"], components["azure_deployment"]]
    outputs.extend([components[var_name] for var_name in config.env_vars.keys()])

    provider.change(
        fn=update_model_choices,
        inputs=[provider],
        outputs=outputs,
    )

    def save_settings(**kwargs) -> str:
        """Save settings to environment and optionally call callback."""
        try:
            # Build model string
            provider = kwargs.get("provider", "openai")
            model_name = kwargs.get("model_name", "gpt-4o")
            azure_deployment = kwargs.get("azure_deployment", "")

            if provider == "azure" and azure_deployment:
                model_str = f"{provider}/{model_name}/{azure_deployment}"
            else:
                model_str = f"{provider}/{model_name}"

            # Prepare settings dict
            settings = {
                "model": model_str,
                "max_tokens": kwargs.get("max_tokens"),
            }

            # Set environment variables
            for var_name in config.env_vars.keys():
                value = kwargs.get(var_name)
                if value is not None and value != "":
                    if isinstance(value, bool):
                        os.environ[var_name] = "true" if value else "false"
                    else:
                        os.environ[var_name] = str(value)

            # Add env vars to settings
            settings.update({k: v for k, v in kwargs.items() if k in config.env_vars})

            # Call callback if provided
            if on_save:
                on_save(settings)

            return "✅ Settings saved successfully!"

        except Exception as e:
            return f"❌ Error saving settings: {str(e)}"

    # Connect save button
    save_inputs = list(components.values())[:-2]  # Exclude save_btn and status
    save_btn.click(
        fn=save_settings,
        inputs=save_inputs,
        outputs=[status],
    ).then(
        lambda: gr.update(visible=True),
        outputs=[status],
    ).then(
        lambda: gr.update(visible=False),
        outputs=[status],
        js="() => new Promise(resolve => setTimeout(() => resolve(), 3000))",
    )

    return components


def get_model_string_from_env() -> str:
    """Get the current model string from environment or use default."""
    # Check for explicit model env var first
    if os.getenv("MODEL"):
        return os.getenv("MODEL", "openai/gpt-4o")

    # Otherwise, try to construct from available info
    if os.getenv("AZURE_OPENAI_BASE_URL"):
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        return f"azure/gpt-4o/{deployment}"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic/claude-3-5-sonnet"
    elif os.getenv("OLLAMA_BASE_URL"):
        return "ollama/llama3.2"
    else:
        return "openai/gpt-4o"


=== File: apps/recipe-tool/recipe_tool_app/ui.py ===
"""UI components for the Recipe Tool app."""

from typing import Optional, Tuple

import gradio as gr

from .core import RecipeToolCore


def create_recipe_ui(core: RecipeToolCore) -> Tuple:
    """Create the Create Recipe UI components."""
    from .config import settings

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            with gr.Tabs():
                with gr.TabItem("Upload Idea"):
                    idea_file = gr.File(label="Idea Text File", file_types=[".md", ".txt"])

                with gr.TabItem("Examples"):
                    # Create dropdown choices from example ideas
                    example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_ideas)]
                    example_dropdown = gr.Dropdown(choices=example_choices, label="Example Ideas", type="index")
                    load_example_btn = gr.Button("Load Example", variant="secondary")

            idea_text = gr.Code(
                label="Idea Text",
                language="markdown",
                lines=10,
                max_lines=20,
                show_line_numbers=False,
                interactive=True,
                wrap_lines=True,
            )

            with gr.Accordion("Additional Options", open=False):
                reference_files = gr.File(
                    label="Reference Files",
                    file_types=[".md", ".txt", ".py", ".json"],
                    file_count="multiple",
                )
                context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs",
                )

            create_btn = gr.Button("Create Recipe", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Generated Recipe"):
                    recipe_output = gr.Code(language="json", label="Recipe JSON", lines=20, wrap_lines=True)
                with gr.TabItem("Preview"):
                    preview_md = gr.Markdown(label="Recipe Structure")
                with gr.TabItem("Context"):
                    debug_context = gr.JSON(label="Context Variables")

    # Set up event handler
    import asyncio

    def create_recipe_handler(text: str, file, refs, ctx: Optional[str]):
        """Wrapper to handle async function in Gradio."""
        try:
            # Handle Gradio file input
            file_path = file.name if file else None
            ref_paths = [f.name for f in refs] if refs else None

            # Use asyncio.run() which properly manages the event loop
            result = asyncio.run(core.create_recipe(text, file_path, ref_paths, ctx))
            return (
                result.get("recipe_json", ""),
                result.get("structure_preview", ""),
                result.get("debug_context", {}),
            )
        except Exception as e:
            import traceback

            error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return ("", f"### Error\n```\n{error_msg}\n```", {"error": str(e)})

    create_btn.click(
        fn=create_recipe_handler,
        inputs=[idea_text, idea_file, reference_files, context_vars],
        outputs=[recipe_output, preview_md, debug_context],
        api_name="create_recipe",
    )

    # Set up example loading
    def load_example(example_idx):
        if example_idx is None:
            return "", ""

        example = settings.example_ideas[example_idx]

        # Read the example file content
        try:
            from pathlib import Path

            # Get the directory where this module is located
            module_dir = Path(__file__).parent.parent
            example_path = module_dir / example.path

            with open(example_path, "r") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading example: {str(e)}"

        # Convert context vars to string format
        ctx_parts = [f"{k}={v}" for k, v in example.context_vars.items()]
        ctx = ",".join(ctx_parts) if ctx_parts else ""

        return content, ctx

    load_example_btn.click(
        fn=load_example,
        inputs=[example_dropdown],
        outputs=[idea_text, context_vars],
    )

    # Load file content when a file is selected
    def load_file_content(file):
        if not file:
            return ""
        try:
            with open(file.name, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error loading file: {str(e)}"

    idea_file.change(
        fn=load_file_content,
        inputs=[idea_file],
        outputs=[idea_text],
    )

    return (idea_text, idea_file, reference_files, context_vars, create_btn, recipe_output, preview_md, debug_context)


