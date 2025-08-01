"""
Main entrypoint for the Document Generator App UI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from document_generator_v1_app.ui import build_editor


def check_deployment_status():
    """Quick deployment status check."""
    # Verify essential configuration
    app_root = Path(__file__).resolve().parents[1]
    bundled_recipe_path = app_root / "document_generator_v1_app" / "recipes" / "document_generator_recipe.json"

    print("Document Generator starting...")
    print(f"Recipe source: {'bundled' if bundled_recipe_path.exists() else 'development'}")

    # Show LLM provider configuration
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    print(f"LLM: {provider}/{model}")


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""

    # Load environment variables from .env file
    load_dotenv()

    # Run diagnostic check
    check_deployment_status()

    # Configuration for hosting - Azure App Service uses PORT environment variable
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "8000")))

    print(f"Server: {server_name}:{server_port}")
    build_editor().launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()
