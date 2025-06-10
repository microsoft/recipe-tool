"""Recipe Tool Gradio app."""

import argparse

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


def create_app() -> gr.Blocks:
    """Create the Recipe Tool app."""
    recipe_core = RecipeToolCore()
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
