# apps/recipe-executor/recipe_executor_app

[collect-files]

**Search:** ['apps/recipe-executor/recipe_executor_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 3:22:46 PM
**Files:** 7

=== File: apps/recipe-executor/recipe_executor_app/__init__.py ===
"""Recipe Executor Gradio App package."""

__version__ = "0.1.0"


=== File: apps/recipe-executor/recipe_executor_app/app.py ===
"""Recipe Executor Gradio app."""

import argparse
from typing import Any, Dict, Optional

import gradio as gr
import gradio.themes
from recipe_executor.logger import init_logger

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.ui import create_ui
from recipe_executor_app.settings_sidebar import create_settings_sidebar

# Set up logging
logger = init_logger(settings.log_dir)
logger.setLevel(settings.log_level.upper())


def create_executor_block(
    core: Optional[RecipeExecutorCore] = None, include_header: bool = True, include_settings: bool = True
) -> gr.Blocks:
    """Create a reusable Recipe Executor block."""
    if core is None:
        core = RecipeExecutorCore()

    theme = gradio.themes.Soft() if settings.theme == "soft" else None

    with gr.Blocks(theme=theme) as block:
        if include_header:
            gr.Markdown("# Recipe Executor")
            gr.Markdown("A web interface for executing recipes.")

        # Settings sidebar
        if include_settings:
            with gr.Sidebar(position="right"):
                gr.Markdown("### ⚙️ Settings")

                def on_settings_save(settings: Dict[str, Any]) -> None:
                    """Callback when settings are saved."""
                    core.current_settings = settings
                    logger.info(
                        f"Settings updated: model={settings.get('model')}, max_tokens={settings.get('max_tokens')}"
                    )

                create_settings_sidebar(on_save=on_settings_save)

        # Main UI
        create_ui(core, include_header)

    return block


def create_app() -> gr.Blocks:
    """Create the full Gradio app."""
    core = RecipeExecutorCore()

    with gr.Blocks(title=settings.app_title) as app:
        create_executor_block(core)

    return app


def get_components(core: Optional[RecipeExecutorCore] = None) -> Dict[str, Any]:
    """Get reusable components for embedding."""
    if core is None:
        core = RecipeExecutorCore()

    return {
        "create_executor_block": create_executor_block,
        "core": core,
        "execute_recipe": core.execute_recipe,
        "load_recipe": core.load_recipe,
    }


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


=== File: apps/recipe-executor/recipe_executor_app/config.py ===
"""Configuration settings for the Recipe Executor app."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExampleRecipe(BaseModel):
    """Configuration for an example recipe."""

    name: str
    path: str
    context_vars: Dict[str, str] = {}


class Settings(BaseSettings):
    """Configuration settings for the Recipe Executor app."""

    # App settings
    app_title: str = "Recipe Executor"
    app_description: str = "A web interface for executing recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port

    # MCP settings
    mcp_server: bool = True

    # Recipe executor settings
    log_dir: str = "logs"
    log_level: str = "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL

    # Example recipes with context
    example_recipes: List[ExampleRecipe] = [
        ExampleRecipe(
            name="Generate Code from Spec File (Hello World Demo)",
            path="../../recipes/example_simple/code_from_spec_recipe.json",
            context_vars={
                "spec_file": "recipes/example_simple/specs/hello-world-spec.txt",
            },
        ),
        ExampleRecipe(
            name="Demo Quarterly Report",
            path="../../recipes/example_quarterly_report/demo_quarterly_report_recipe.json",
            context_vars={"new_data_file": "recipes/example_quarterly_report/demo-data/q2-2025-sales.csv"},
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


=== File: apps/recipe-executor/recipe_executor_app/core.py ===
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
from recipe_executor_app.settings_sidebar import get_model_string, get_setting

logger = logging.getLogger(__name__)


class RecipeExecutorCore:
    """Core functionality for Recipe Executor operations."""

    def __init__(self, executor: Optional[Executor] = None):
        """Initialize with the executor."""
        self.executor = executor if executor is not None else Executor(logger)
        self.current_settings = {}

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

            # Add model configuration from config/environment
            model_str = get_model_string()
            context_dict["model"] = model_str

            # Add max_tokens if set in config/environment
            max_tokens = get_setting("MAX_TOKENS")
            if max_tokens:
                try:
                    context_dict["max_tokens"] = int(max_tokens)
                except ValueError:
                    pass

            # Load configuration from environment
            from recipe_executor.config import load_configuration

            config = load_configuration()

            # Create context with both artifacts and config
            context = Context(artifacts=context_dict, config=config)

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


=== File: apps/recipe-executor/recipe_executor_app/settings_sidebar.py ===
"""Import settings sidebar from shared components."""

from gradio_components.settings_sidebar import SettingsConfig, create_settings_sidebar, get_model_string_from_env
from gradio_components.config_manager import (
    get_model_string,
    get_setting,
    load_settings,
    save_settings,
    get_env_or_default,
    is_override,
)

__all__ = [
    "SettingsConfig",
    "create_settings_sidebar",
    "get_model_string_from_env",
    "get_model_string",
    "get_setting",
    "load_settings",
    "save_settings",
    "get_env_or_default",
    "is_override",
]


=== File: apps/recipe-executor/recipe_executor_app/ui.py ===
"""UI components for the Recipe Executor app."""

import io
import json
import logging

import gradio as gr

from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.utils import safe_json_dumps

logger = logging.getLogger(__name__)


def create_ui(core: RecipeExecutorCore, include_header: bool = True):
    """Create the Recipe Executor UI."""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            # Tabbed interface for recipe input options
            with gr.Tabs():
                with gr.TabItem("Upload Recipe"):
                    recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])

                with gr.TabItem("Examples"):
                    from recipe_executor_app.config import settings

                    # Create dropdown choices from example recipes
                    example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_recipes)]
                    example_dropdown = gr.Dropdown(choices=example_choices, label="Example Recipes", type="index")
                    load_example_btn = gr.Button("Load Example", variant="secondary")

            recipe_text = gr.Code(
                label="Recipe JSON", language="json", interactive=True, lines=10, max_lines=20, wrap_lines=True
            )

            with gr.Accordion("Additional Options", open=False):
                context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs",
                )

            execute_btn = gr.Button("Execute Recipe", variant="primary", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Results"):
                    result_output = gr.Markdown()
                    context_json = gr.JSON(label="Context")

                with gr.TabItem("Logs"):
                    logs_output = gr.Textbox(label="Logs", lines=20, max_lines=30, interactive=False)

    # Set up event handlers
    async def execute_with_logs(file, text, ctx, progress=gr.Progress()):
        """Execute recipe with log capture."""
        # Capture logs
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(logging.INFO)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            progress(0, desc="Executing recipe...")

            # Execute recipe with file path or text
            result = await core.execute_recipe(file, text, ctx)

            progress(1, desc="Complete!")

            # Get logs
            handler.flush()
            logs = log_capture.getvalue()

            # Format context
            context = safe_json_dumps(result.get("debug_context", {}))

            return (result.get("formatted_results", ""), logs, json.loads(context))
        finally:
            root_logger.removeHandler(handler)
            log_capture.close()

    execute_btn.click(
        fn=execute_with_logs,
        inputs=[recipe_file, recipe_text, context_vars],
        outputs=[result_output, logs_output, context_json],
        api_name="execute_recipe",
        show_progress="full",
    )

    # Enable button when recipe is loaded
    recipe_text.change(fn=lambda x: gr.update(interactive=bool(x)), inputs=[recipe_text], outputs=[execute_btn])

    # Load file content
    def load_file(file_path):
        if not file_path:
            return "", gr.update(interactive=False)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            json.loads(content)  # Validate
            return content, gr.update(interactive=True)
        except Exception:
            return "", gr.update(interactive=False)

    recipe_file.change(fn=load_file, inputs=[recipe_file], outputs=[recipe_text, execute_btn])

    # Set up example loading
    async def load_example(example_idx):
        if example_idx is None:
            return "", ""

        example = settings.example_recipes[example_idx]

        # Load the recipe content
        result = await core.load_recipe(example.path)
        content = result.get("recipe_content", "")

        # Convert context vars to string format
        ctx_parts = [f"{k}={v}" for k, v in example.context_vars.items()]
        ctx = ",".join(ctx_parts) if ctx_parts else ""

        return content, ctx

    load_example_btn.click(
        fn=load_example,
        inputs=[example_dropdown],
        outputs=[recipe_text, context_vars],
    )

    return recipe_file, recipe_text, context_vars, execute_btn, result_output, logs_output, context_json


=== File: apps/recipe-executor/recipe_executor_app/utils.py ===
"""Essential utilities for the Recipe Executor app."""

import json
import os
import tempfile
from typing import Any, Callable, Dict, Optional, Tuple


def get_repo_root() -> str:
    """Get the repository root directory."""
    current = os.path.dirname(os.path.abspath(__file__))
    # Check if we've reached the root (works on all platforms)
    while True:
        if os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Reached filesystem root
            break
        current = parent
    return os.path.dirname(os.path.abspath(__file__))


def get_main_repo_root() -> Optional[str]:
    """Get the main repository root that contains recipes directory."""
    current = get_repo_root()
    while True:
        if os.path.exists(os.path.join(current, "recipes")) and os.path.exists(os.path.join(current, "ai_context")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Reached filesystem root
            break
        current = parent
    return None


def read_file(path: str) -> str:
    """Read content from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_temp_file(content: str, suffix: str = ".txt") -> Tuple[str, Callable[[], None]]:
    """Create a temporary file with cleanup function."""
    temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=suffix, delete=False, encoding="utf-8")
    temp_file.write(content)
    temp_file.close()

    def cleanup():
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass

    return temp_file.name, cleanup


def parse_context_vars(context_str: Optional[str]) -> Dict[str, Any]:
    """Parse context variables from comma-separated key=value pairs."""
    if not context_str:
        return {}

    context = {}
    for pair in context_str.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            context[key.strip()] = value.strip()
    return context


def format_results(results: Dict[str, str], execution_time: float = 0.0) -> str:
    """Format recipe execution results as markdown."""
    md = [f"### Recipe Execution Results\n\n**Execution Time**: {execution_time:.2f}s\n"]

    for key, value in results.items():
        md.append(f"\n**{key}**:\n")
        if value.startswith("{") or value.startswith("["):
            md.append(f"```json\n{value}\n```")
        else:
            md.append(f"```\n{value}\n```")

    return "\n".join(md)


def safe_json_dumps(obj: Any) -> str:
    """Safely convert object to JSON string."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return json.dumps({"error": "Could not serialize object"})


