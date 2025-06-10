"""Recipe Tool Gradio app."""

import argparse
from typing import Optional

import gradio as gr
import gradio.themes
from recipe_executor.logger import init_logger
from recipe_executor_app.app import create_executor_block
from recipe_executor_app.core import RecipeExecutorCore

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore
from recipe_tool_app.ui import create_recipe_ui

# Set up logging
logger = init_logger(settings.log_dir)
logger.setLevel(settings.log_level.upper())


def create_app(model: Optional[str] = None) -> gr.Blocks:
    """Create the Recipe Tool app."""
    recipe_core = RecipeToolCore(default_model=model)
    theme = gradio.themes.Soft() if settings.theme == "soft" else None  # type: ignore

    with gr.Blocks(title=settings.app_title, theme=theme) as app:
        gr.Markdown("# Recipe Tool")
        gr.Markdown("A web interface for executing and creating recipes.")

        with gr.Tabs():
            # Create Recipe Tab
            with gr.TabItem("Create Recipe"):
                create_recipe_ui(recipe_core)

            # Execute Recipe Tab (reuse from recipe-executor)
            with gr.TabItem("Execute Recipe"):
                executor_core = RecipeExecutorCore(default_model=model)
                create_executor_block(
                    executor_core,
                    include_header=False,
                )

    return app


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host (default: {settings.host})")
    parser.add_argument("--port", type=int, help="Port")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--model", type=str, help="Model name for recipe execution")

    args = parser.parse_args()
    model: Optional[str] = None
    # Override settings
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True
    if args.model:
        model = args.model

    # Launch app
    app = create_app(model=model)
    app.launch(**settings.to_launch_kwargs())


if __name__ == "__main__":
    main()
