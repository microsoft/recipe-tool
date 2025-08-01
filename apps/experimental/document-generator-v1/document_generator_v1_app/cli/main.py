"""
CLI for headless document generation.
"""

import json
import asyncio
from pathlib import Path

import typer  # type: ignore

from ..models.outline import Outline
from ..executor.runner import generate_document

app = typer.Typer(no_args_is_help=False)


@app.command()
def generate(
    outline_file: str = typer.Option(..., "--outline", "-o", help="Path to outline JSON file"),
    output_file: str = typer.Option(None, "--output", "-O", help="Path to write generated Markdown"),
):
    """
    Generate a document from the given outline JSON.
    """
    # Load and validate outline
    try:
        raw = Path(outline_file).read_text()
        data = json.loads(raw)
        outline = Outline.from_dict(data)
    except Exception as e:
        typer.secho(f"Failed to load outline: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    # Generate document
    try:
        doc_text = asyncio.run(generate_document(outline))
    except Exception as e:
        typer.secho(f"Generation failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    # Output
    if output_file:
        try:
            Path(output_file).write_text(doc_text)
            typer.secho(f"Document written to {output_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Failed to write document: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    else:
        typer.echo(doc_text)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    # Entry point for CLI
    app()
