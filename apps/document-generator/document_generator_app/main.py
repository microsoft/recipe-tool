"""
Main entrypoint for the Document Generator App UI.
"""

from document_generator_app.ui import build_editor


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""
    import os

    # Configuration for hosting
    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    build_editor().launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()
