# apps/document-generator/document_generator_app

[collect-files]

**Search:** ['apps/document-generator/document_generator_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 7/2/2025, 3:22:05 PM
**Files:** 21

=== File: apps/document-generator/document_generator_app/__init__.py ===


=== File: apps/document-generator/document_generator_app/cli/__init__.py ===
"""
CLI package for Document Generator.
"""

__all__ = ["app"]
from .main import app


=== File: apps/document-generator/document_generator_app/cli/main.py ===
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


=== File: apps/document-generator/document_generator_app/config.py ===
"""Configuration settings for the Document Generator app."""

import os
from typing import NamedTuple, List


class ExampleOutline(NamedTuple):
    """Configuration for an example document outline."""

    name: str
    path: str


class Settings:
    """Configuration settings for the Document Generator app."""

    # App settings
    app_title: str = "Document Generator"
    app_description: str = "Create structured documents with AI assistance"

    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "azure"
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o")

    @property
    def model_id(self) -> str:
        """Get the full model ID for recipe-executor."""
        return f"{self.llm_provider}/{self.default_model}"

    # Example outlines
    example_outlines: List[ExampleOutline] = [
        ExampleOutline(
            name="README Generator",
            path="examples/readme.docpack",
        ),
        ExampleOutline(
            name="Product Launch Documentation",
            path="examples/launch-documentation.docpack",
        ),
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.


# Create global settings instance
settings = Settings()


=== File: apps/document-generator/document_generator_app/executor/__init__.py ===
"""
Executor package for Document Generator.
"""

__all__ = ["generate_document"]
from .runner import generate_document


=== File: apps/document-generator/document_generator_app/executor/runner.py ===
"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
import logging
import traceback
from pathlib import Path

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger
from recipe_executor.config import load_configuration

from ..models.outline import Outline
from ..session import session_manager
from ..resource_resolver import resolve_all_resources
from ..config import settings
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_document(outline: Optional[Outline], session_id: Optional[str] = None) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    logger.info(f"Starting document generation for session: {session_id}")

    # Allow stub invocation without an outline for initial tests
    if outline is None:
        logger.warning("No outline provided, returning empty document")
        return ""

    # First try bundled recipes (for deployment), then fall back to repo structure (for development)
    APP_ROOT = Path(__file__).resolve().parents[2]  # document_generator_app parent
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "document_generator_recipe.json"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        # Use bundled recipes (deployment mode)
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
    else:
        # Fall back to repo structure (development mode)
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using development recipes: {RECIPE_PATH}")
        logger.info(f"Recipe exists: {RECIPE_PATH.exists()}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "execution")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Resolve all resources using the new resolver
        logger.info("Resolving resources...")
        outline_data = outline.to_dict()
        logger.info(f"Outline data: {json.dumps(outline_data, indent=2)}")

        resolved_resources = resolve_all_resources(outline_data, session_id)
        logger.info(f"Resolved resources: {resolved_resources}")

        # Update resource paths in outline with resolved paths
        for resource in outline.resources:
            if resource.key in resolved_resources:
                old_path = resource.path
                resource.path = str(resolved_resources[resource.key])
                logger.info(f"Updated resource {resource.key}: {old_path} -> {resource.path}")

        # Create updated outline with resolved paths
        data = outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)
        logger.info(f"Created outline file: {outline_path}")

        recipe_logger = init_logger(log_dir=tmpdir)

        # Load configuration from environment variables
        config = load_configuration()

        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
                "output_root": str(session_dir),  # Use session directory for output
                "model": settings.model_id,  # Use configured model
            },
            config=config,  # Pass configuration to context
        )
        logger.info(f"Context artifacts: {context.dict()}")

        executor = Executor(recipe_logger)
        logger.info(f"Executing recipe: {RECIPE_PATH}")
        await executor.execute(str(RECIPE_PATH), context)
        logger.info("Recipe execution completed")

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        logger.info(f"Output root: {output_root}")
        logger.info(f"Document filename: {filename}")
        logger.info(f"All context keys: {list(context.keys())}")

        if not filename:
            document_content = context.get("document", "")
            logger.info(f"No filename, returning document from context (length: {len(document_content)})")
            return document_content

        document_path = output_root / f"{filename}.md"
        logger.info(f"Looking for document at: {document_path}")

        try:
            content = document_path.read_text()
            logger.info(f"Successfully read document (length: {len(content)})")
            return content
        except FileNotFoundError:
            logger.error(f"Generated file not found: {document_path}")
            # List files in output directory for debugging
            if output_root.exists():
                files = list(output_root.glob("*"))
                logger.info(f"Files in output directory: {files}")
            return f"Generated file not found: {document_path}"
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error generating document: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"


=== File: apps/document-generator/document_generator_app/main.py ===
"""
Main entrypoint for the Document Generator App UI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from document_generator_app.ui import build_editor


def check_deployment_status():
    """Quick deployment status check."""
    # Verify essential configuration
    app_root = Path(__file__).resolve().parents[1]
    bundled_recipe_path = app_root / "document_generator_app" / "recipes" / "document_generator_recipe.json"

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


=== File: apps/document-generator/document_generator_app/models/__init__.py ===
"""
Models package for Document Generator.
"""

__all__ = ["Resource", "Section", "Outline"]
from .outline import Resource, Section, Outline


=== File: apps/document-generator/document_generator_app/models/outline.py ===
"""
Data models for the Document Generator app.
Defines Resource, Section, and Outline dataclasses with serialization utilities.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from jsonschema import validate


@dataclass
class Resource:
    key: str
    path: str
    description: str
    merge_mode: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None merge_mode."""
        result = {
            "key": self.key,
            "path": self.path,
            "description": self.description,
        }
        if self.merge_mode is not None:
            result["merge_mode"] = self.merge_mode
        return result


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)
    _mode: Optional[str] = field(default=None, init=False, repr=False)  # Internal mode tracking

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, using mode to determine which fields to include."""
        result: Dict[str, Any] = {"title": self.title}

        # Use explicit mode if set, otherwise infer from data
        mode = getattr(self, "_mode", None)
        if mode == "Static" or (mode is None and self.resource_key is not None and self.prompt is None):
            # Static mode - include resource_key
            if self.resource_key is not None:
                result["resource_key"] = self.resource_key
        else:
            # Prompt mode (default) - include prompt and refs
            if self.prompt is not None:
                result["prompt"] = self.prompt
            if self.refs:  # Only include refs if not empty
                result["refs"] = self.refs

        # Always include sections array (even if empty)
        result["sections"] = [s.to_dict() for s in self.sections]

        return result


def section_from_dict(data: Dict[str, Any]) -> Section:
    section = Section(
        title=data.get("title", ""),
        prompt=data.get("prompt"),
        refs=list(data.get("refs", [])),
        resource_key=data.get("resource_key"),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )
    # Set mode based on loaded data
    if section.resource_key is not None:
        section._mode = "Static"
    else:
        section._mode = "Prompt"
    return section


@dataclass
class Outline:
    title: str
    general_instruction: str
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert outline to dict with proper section serialization."""
        return {
            "title": self.title,
            "general_instruction": self.general_instruction,
            "resources": [r.to_dict() for r in self.resources],
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        res_list: List[Resource] = []
        for r in data.get("resources", []):
            res_list.append(
                Resource(
                    key=r.get("key", ""),
                    path=r.get("path", ""),
                    description=r.get("description", ""),
                    merge_mode=r.get("merge_mode"),
                )
            )
        sec_list: List[Section] = [section_from_dict(s) for s in data.get("sections", [])]
        return cls(
            title=data.get("title", ""),
            general_instruction=data.get("general_instruction", ""),
            resources=res_list,
            sections=sec_list,
        )


# JSON Schema for outline validation
OUTLINE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Outline",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "general_instruction": {"type": "string"},
        "resources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "path": {"type": "string"},
                    "description": {"type": "string"},
                    "merge_mode": {"oneOf": [{"type": "string", "enum": ["concat", "dict"]}, {"type": "null"}]},
                },
                "required": ["key", "path", "description"],
                "additionalProperties": False,
            },
        },
        "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
    },
    "definitions": {
        "section": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "prompt": {"type": "string"},
                "refs": {"type": "array", "items": {"type": "string"}},
                "resource_key": {"type": "string"},
                "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
            },
            "required": ["title"],
            "oneOf": [{"required": ["prompt"]}, {"required": ["resource_key"]}],
            "additionalProperties": False,
        }
    },
    "required": ["title", "general_instruction", "resources", "sections"],
    "additionalProperties": False,
}


def validate_outline(data: dict) -> None:
    """
    Validate outline data against the JSON schema.
    Raises jsonschema.ValidationError on failure.
    """
    validate(instance=data, schema=OUTLINE_SCHEMA)


=== File: apps/document-generator/document_generator_app/package_handler.py ===
"""Package handler for .docpack files.

Handles creation and extraction of .docpack files which are zip archives
containing an outline.json file and associated resource files.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DocpackHandler:
    """Handles .docpack file creation and extraction."""

    @staticmethod
    def create_package(outline_data: Dict[str, Any], resource_files: List[Path], output_path: Path) -> None:
        """Create a .docpack file from outline data and resource files.

        Args:
            outline_data: The outline JSON data
            resource_files: List of resource file paths to include
            output_path: Where to save the .docpack file
        """
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Always include outline.json
            zf.writestr("outline.json", json.dumps(outline_data, indent=2))

            # Add resource files with their original names
            for resource_file in resource_files:
                if resource_file.exists():
                    zf.write(resource_file, resource_file.name)

    @staticmethod
    def extract_package(package_path: Path, extract_dir: Path) -> Tuple[Dict[str, Any], List[Path]]:
        """Extract a .docpack file to a directory with organized structure.

        Args:
            package_path: Path to the .docpack file
            extract_dir: Session directory to extract to

        Returns:
            Tuple of (outline_data, list_of_resource_file_paths)
        """
        extract_dir.mkdir(parents=True, exist_ok=True)

        # Create files subdirectory for uploaded files
        files_dir = extract_dir / "files"
        files_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(package_path, "r") as zf:
            # Extract outline.json to extract_dir
            if "outline.json" in zf.namelist():
                zf.extract("outline.json", extract_dir)

            # Extract all other files to files/ subdirectory
            for file_info in zf.filelist:
                if file_info.filename != "outline.json":
                    # Extract to files directory
                    file_info.filename = Path(file_info.filename).name  # Remove any path components
                    zf.extract(file_info, files_dir)

        # Read outline.json
        outline_path = extract_dir / "outline.json"
        if not outline_path.exists():
            raise ValueError("Package does not contain outline.json")

        with open(outline_path, "r") as f:
            outline_data = json.load(f)

        # Find all resource files in files directory
        resource_files = [f for f in files_dir.iterdir() if f.is_file()]

        return outline_data, resource_files

    @staticmethod
    def validate_package(package_path: Path) -> bool:
        """Validate that a file is a valid .docpack.

        Args:
            package_path: Path to check

        Returns:
            True if valid .docpack, False otherwise
        """
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                files = zf.namelist()
                return "outline.json" in files
        except zipfile.BadZipFile:
            return False


=== File: apps/document-generator/document_generator_app/recipes/document_generator_recipe.json ===
{
  "name": "Document Generator",
  "description": "Generates a document from an outline, using LLMs to fill in sections and assemble the final document.",
  "inputs": {
    "outline_file": {
      "description": "Path to outline json file.",
      "type": "string"
    },
    "model": {
      "description": "LLM model to use for generation.",
      "type": "string",
      "default": "openai/gpt-4o"
    },
    "output_root": {
      "description": "Directory to save the generated document.",
      "type": "string",
      "default": "output"
    }
  },
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "model",
        "value": "{{ model | default: 'openai/gpt-4o' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "recipe_root",
        "value": "{{ recipe_root | default: 'recipes/document_generator' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document_filename",
        "value": "{{ outline_file | default: 'document' | replace: '\\', '/' | split: '/' | last | split: '.' | first | snakecase | upcase }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/load_outline.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/load_resources.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "# {{ outline.title }}\n\n[document-generator]\n\n**Date:** {{ 'now' | date: '%-m/%-d/%Y %I:%M:%S %p' }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_sections.json",
        "context_overrides": {
          "sections": "{{ outline.sections | json: indent: 2 }}"
        }
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/load_outline.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ outline_file }}",
        "content_key": "outline"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "toc",
        "value": "{% capture toc %}\n## Table of Contents\n\n{% for sec in outline.sections %}\n- {{ sec.title | escape }}\n{% if sec.sections %}\n  {% for child in sec.sections %}\n  - {{ child.title | escape }}\n  {% endfor %}\n{% endif %}\n{% endfor %}\n{% endcapture %}\n{{ toc }}"
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/load_resources.json ===
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "outline.resources",
        "item_key": "resource",
        "result_key": "resources",
        "substeps": [
          {
            "type": "read_files",
            "config": {
              "path": "{{ resource.path }}",
              "content_key": "content",
              "merge_mode": "{{ resource.merge_mode }}"
            }
          },
          {
            "type": "set_context",
            "config": {
              "key": "resource",
              "value": {
                "content": "{{ content }}"
              },
              "if_exists": "merge"
            }
          }
        ]
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/read_document.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ output_root }}/{{ document_filename }}.md",
        "content_key": "document"
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/write_content.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_document.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "\n\n{{ section.title }}\n\n{% for resource in resources %}{% if resource.key == section.resource_key %}{{ resource.content }}{% endif %}{% endfor %}",
        "if_exists": "merge"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/write_document.json ===
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "{{ document_filename }}.md",
            "content_key": "document"
          }
        ],
        "root": "{{ output_root }}"
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/write_section.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_document.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "rendered_prompt",
        "value": "{{ section.prompt }}",
        "nested_render": true
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model }}",
        "prompt": "Generate a section for the <DOCUMENT> based upon the following prompt:\n<PROMPT>\n{{ rendered_prompt }}\n</PROMPT>\n\nGeneral instruction:\n{{ outline.general_instruction }}\n\nAvailable references:\n<REFERENCE_DOCS>\n{% for ref in section.refs %}{% for resource in resources %}{% if resource.key == ref %}<{{ resource.key | upcase }}><DESCRIPTION>{{ resource.description }}</DESCRIPTION><CONTENT>{{ resource.content }}</CONTENT></{{ resource.key | upcase }}>{% endif %}{% endfor %}{% endfor %}\n</REFERENCE_DOCS>\n\nHere is the content of the <DOCUMENT> so far:\n<DOCUMENT>\n{{ document }}\n</DOCUMENT>\n\nPlease write ONLY THE NEW `{{ section.title }}` SECTION requested in your PROMPT, in the same style as the rest of the document.",
        "output_format": {
          "type": "object",
          "properties": {
            "content": {
              "type": "string",
              "description": "The generated content for the section."
            }
          }
        },
        "output_key": "generated"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "\n\n{{ generated.content }}",
        "if_exists": "merge"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/recipes/recipes/write_sections.json ===
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "sections",
        "item_key": "section",
        "result_key": "section.content",
        "substeps": [
          {
            "type": "conditional",
            "config": {
              "condition": "{% if section.resource_key %}true{% else %}false{% endif %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_content.json"
                    }
                  }
                ]
              },
              "if_false": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_section.json"
                    }
                  }
                ]
              }
            }
          },
          {
            "type": "conditional",
            "config": {
              "condition": "{% assign has_children = section | has: 'sections' %}{% if has_children %}true{% else %}false{% endif %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_sections.json",
                      "context_overrides": {
                        "sections": "{{ section.sections | json: indent: 2 }}"
                      }
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  ]
}


=== File: apps/document-generator/document_generator_app/resource_resolver.py ===
"""Resource resolution for document generation.

Handles resolving resources at generation time:
- Uploaded files: resolved to session files directory
- URLs: downloaded to session temp directory
"""

import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .models.outline import Resource
from .session import session_manager


def resolve_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve a resource to a local file path for generation.

    Args:
        resource: Resource object with path (file or URL)
        session_id: Session ID for directory resolution

    Returns:
        Path to local file for use in generation

    Raises:
        FileNotFoundError: If uploaded file doesn't exist
        urllib.error.URLError: If URL download fails
    """
    if resource.path.startswith(("http://", "https://")):
        # URL: download to temp directory
        return _download_url_resource(resource, session_id)
    else:
        # Uploaded file: resolve to files directory
        return _resolve_file_resource(resource, session_id)


def _resolve_file_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve uploaded file resource to local path."""
    files_dir = session_manager.get_files_dir(session_id)
    file_path = files_dir / resource.path

    if not file_path.exists():
        raise FileNotFoundError(f"Resource file not found: {resource.path}")

    return file_path


def _download_url_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Download URL resource to temp directory."""
    temp_dir = session_manager.get_temp_dir(session_id)

    # Generate filename from URL
    parsed_url = urlparse(resource.path)
    filename = Path(parsed_url.path).name

    # If no filename in URL, use resource key
    if not filename or filename == "/":
        filename = f"{resource.key}.downloaded"

    target_path = temp_dir / filename

    # Download the file
    try:
        urllib.request.urlretrieve(resource.path, target_path)
        return target_path
    except Exception as e:
        raise urllib.error.URLError(f"Failed to download {resource.path}: {str(e)}")


def resolve_all_resources(outline_data: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Path]:
    """Resolve all resources in an outline to local paths.

    Args:
        outline_data: Outline dictionary with resources
        session_id: Session ID for directory resolution

    Returns:
        Dictionary mapping resource keys to resolved file paths
    """
    from .models.outline import Outline

    outline = Outline.from_dict(outline_data)
    resolved_resources = {}

    for resource in outline.resources:
        if resource.key:
            resolved_resources[resource.key] = resolve_resource(resource, session_id)

    return resolved_resources


=== File: apps/document-generator/document_generator_app/session.py ===
"""
Session management for multi-user hosting.

Provides session-scoped temporary directories to isolate user data.
"""

import uuid
import tempfile
from pathlib import Path
import shutil
import atexit
from typing import Optional


class SessionManager:
    """Dead simple session directory management"""

    def __init__(self):
        self.session_dirs = {}
        atexit.register(self.cleanup_all)

    def get_session_dir(self, session_id: Optional[str] = None) -> Path:
        """Get unique temp directory for session"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.session_dirs:
            session_dir = Path(tempfile.gettempdir()) / f"doc-gen-{session_id}"
            session_dir.mkdir(exist_ok=True)

            # Create subdirectories for organized file management
            (session_dir / "files").mkdir(exist_ok=True)  # Uploaded files (stored in docpack)
            (session_dir / "temp").mkdir(exist_ok=True)  # Generated files, downloaded URLs

            self.session_dirs[session_id] = session_dir

        return self.session_dirs[session_id]

    def get_files_dir(self, session_id: Optional[str] = None) -> Path:
        """Get files directory for session (for uploaded files)"""
        return self.get_session_dir(session_id) / "files"

    def get_temp_dir(self, session_id: Optional[str] = None) -> Path:
        """Get temp directory for session (for generated files and downloaded URLs)"""
        return self.get_session_dir(session_id) / "temp"

    def cleanup_all(self):
        """Clean up all session directories on shutdown"""
        for session_dir in self.session_dirs.values():
            shutil.rmtree(session_dir, ignore_errors=True)


# Global instance
session_manager = SessionManager()


=== File: apps/document-generator/document_generator_app/ui.py ===
"""
Simplified UI for Document Generator - all UI code in one module.
Following "ruthless simplicity" principle.
"""

import gradio as gr
import json
import os
import uuid
from typing import Dict, Any, List, Optional, Tuple

from .models.outline import Outline, Resource, Section, validate_outline
from .executor.runner import generate_document
from .package_handler import DocpackHandler


# ============================================================================
# State Management
# ============================================================================


def create_initial_state() -> Dict[str, Any]:
    """Create initial app state."""
    return {
        "outline": Outline(title="", general_instruction=""),
        "selected_type": None,  # "resource" or "section"
        "selected_id": None,  # e.g., "resource_0" or "section_1_2"
        "session_id": str(uuid.uuid4()),  # Unique session ID for this UI instance
    }


# ============================================================================
# Utility Functions
# ============================================================================


def validate_outline_data(outline: Outline) -> Tuple[bool, str]:
    """Validate an outline and return (is_valid, message)."""
    try:
        validate_outline(outline.to_dict())
        return True, "Outline is valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_section_at_path(sections: List[Section], path: List[int]) -> Optional[Section]:
    """Navigate to a section using a path of indices."""
    current = sections
    for i, idx in enumerate(path):
        if idx >= len(current):
            return None
        if i == len(path) - 1:
            return current[idx]
        current = current[idx].sections
    return None


def add_section_at_path(sections: List[Section], path: List[int], new_section: Section) -> None:
    """Add a section as a subsection at the given path."""
    if not path:
        sections.append(new_section)
        return

    parent = get_section_at_path(sections, path)
    if parent:
        if not hasattr(parent, "sections") or parent.sections is None:
            parent.sections = []
        parent.sections.append(new_section)


def remove_section_at_path(sections: List[Section], path: List[int]) -> None:
    """Remove a section at the given path."""
    if not path:
        return

    if len(path) == 1:
        if path[0] < len(sections):
            sections.pop(path[0])
    else:
        parent_path = path[:-1]
        parent = get_section_at_path(sections, parent_path)
        if parent and hasattr(parent, "sections") and parent.sections:
            if path[-1] < len(parent.sections):
                parent.sections.pop(path[-1])


# ============================================================================
# UI Component Creation
# ============================================================================


def create_resource_editor() -> Dict[str, Any]:
    """Create the resource editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Resource")

        key = gr.Textbox(label="Key *", placeholder="unique_key")
        description = gr.TextArea(label="Description", placeholder="Describe what this resource contains...", lines=3)

        gr.Markdown("#### Resource Source")
        gr.Markdown(
            "*Only text-based files are supported: Markdown (.md), text (.txt), JSON (.json), "
            "source code (.py, .js, .ts, etc.), CSV (.csv), and similar. "
            "Word docs, PDFs, PowerPoint, images, and binary files are not supported.*"
        )
        with gr.Tabs() as resource_source_tabs:
            with gr.TabItem("Upload File", id="upload_file"):
                bundled_file_info = gr.Markdown(visible=False)
                file = gr.File(label="Upload File", file_types=None)

            with gr.TabItem("URL", id="url_tab"):
                url = gr.Textbox(label="URL", placeholder="https://example.com/data.md")

    return {
        "container": container,
        "key": key,
        "description": description,
        "bundled_file_info": bundled_file_info,
        "file": file,
        "url": url,
        "resource_source_tabs": resource_source_tabs,
    }


def create_section_editor() -> Dict[str, Any]:
    """Create the section editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Section")

        title = gr.Textbox(label="Title *", placeholder="Section Title")

        with gr.Tabs() as content_mode_tabs:
            with gr.TabItem("Prompt", id="prompt_mode") as prompt_tab:
                prompt = gr.TextArea(label="Prompt", placeholder="Instructions for generating this section...", lines=4)
                # Note: We'll populate choices dynamically
                refs = gr.Dropdown(label="Referenced Resources", choices=[], multiselect=True, interactive=True)

            with gr.TabItem("Static", id="static_mode") as static_tab:
                resource_key = gr.Dropdown(label="Resource Key", choices=[], interactive=True)

    return {
        "container": container,
        "title": title,
        "prompt": prompt,
        "refs": refs,
        "resource_key": resource_key,
        "content_mode_tabs": content_mode_tabs,
        "prompt_tab": prompt_tab,
        "static_tab": static_tab,
    }


# ============================================================================
# Choice Generation
# ============================================================================


def generate_resource_choices(state_data: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Generate choices for resource radio."""
    if not state_data or not state_data["outline"].resources:
        return []

    choices = []
    for i, res in enumerate(state_data["outline"].resources):
        label = res.key or f"Resource {i + 1}"
        value = f"resource_{i}"
        choices.append((label, value))
    return choices


def generate_section_choices(state_data: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Generate choices for section radio with indentation."""
    if not state_data or not state_data["outline"].sections:
        return []

    choices = []

    def add_sections(sections, path=None, level=0):
        if path is None:
            path = []

        for i, sec in enumerate(sections):
            if level >= 4:  # Max 4 levels
                continue

            current_path = path + [i]
            # Use non-breaking spaces for indentation
            if level == 0:
                indent = ""
            elif level == 1:
                indent = "└─ "
            else:
                indent = "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0" * (level - 1) + "└─ "

            section_label = sec.title or f"Section {'.'.join(map(str, current_path))}"
            label = f"{indent}{section_label}"
            value = f"section_{'_'.join(map(str, current_path))}"
            choices.append((label, value))

            # Add subsections
            if sec.sections and level < 3:
                add_sections(sec.sections, current_path, level + 1)

    add_sections(state_data["outline"].sections)
    return choices


# ============================================================================
# Validation and Preview
# ============================================================================


def validate_and_preview(state_data: Dict[str, Any]) -> Tuple[str, Any, Any, Any]:
    """Validate outline and update JSON preview."""
    if not state_data:
        return "", gr.update(visible=False), gr.update(interactive=False), gr.update(visible=False)

    try:
        outline_dict = state_data["outline"].to_dict()
        json_str = json.dumps(outline_dict, indent=2)

        is_valid, message = validate_outline_data(state_data["outline"])

        # Update download visibility
        has_content = state_data["outline"].title or state_data["outline"].resources or state_data["outline"].sections
        download_visible = gr.update(visible=has_content)

        if is_valid:
            return json_str, gr.update(visible=False), gr.update(interactive=True), download_visible
        else:
            return (
                json_str,
                gr.update(value=f"⚠️ {message}", visible=True),
                gr.update(interactive=False),
                download_visible,
            )
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", gr.update(value=error_msg, visible=True), gr.update(interactive=False), gr.update(visible=False)


# ============================================================================
# State Update Functions
# ============================================================================


def select_item(item_id: str, item_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle clicking on a list item."""
    state["selected_id"] = item_id
    state["selected_type"] = item_type
    return state


def add_resource(state: Dict[str, Any]) -> Dict[str, Any]:
    """Add new resource and select it."""
    state["outline"].resources.append(Resource(key="", path="", description=""))
    state["selected_id"] = f"resource_{len(state['outline'].resources) - 1}"
    state["selected_type"] = "resource"
    return state


def add_section(state: Dict[str, Any], as_subsection: bool = False) -> Dict[str, Any]:
    """Add new section (top-level or as subsection of selected)."""
    new_section = Section(title="New Section", prompt="")
    new_section._mode = "Prompt"  # Default to prompt mode

    if as_subsection and state["selected_type"] == "section":
        # Add as subsection of selected section
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]

        # Check if we're within depth limit (max 4 levels)
        if len(path) < 4:
            add_section_at_path(state["outline"].sections, path, new_section)
            # Update selection to the new subsection
            parent = get_section_at_path(state["outline"].sections, path)
            if parent and hasattr(parent, "sections") and parent.sections:
                new_idx = len(parent.sections) - 1
                state["selected_id"] = f"section_{'_'.join(path_str + [str(new_idx)])}"
    else:
        # Add at same level as selected section (or top-level if nothing selected)
        if state["selected_type"] == "section":
            path_str = state["selected_id"].split("_")[1:]
            path = [int(p) for p in path_str]

            if len(path) == 1:
                # Top-level section - insert after it
                insert_idx = path[0] + 1
                state["outline"].sections.insert(insert_idx, new_section)
                state["selected_id"] = f"section_{insert_idx}"
            else:
                # Nested section - insert after it at same level
                parent_path = path[:-1]
                parent = get_section_at_path(state["outline"].sections, parent_path)
                if parent and hasattr(parent, "sections"):
                    insert_idx = path[-1] + 1
                    parent.sections.insert(insert_idx, new_section)
                    state["selected_id"] = f"section_{'_'.join([str(p) for p in parent_path] + [str(insert_idx)])}"
        else:
            # No section selected - add to end of top-level
            state["outline"].sections.append(new_section)
            state["selected_id"] = f"section_{len(state['outline'].sections) - 1}"

    state["selected_type"] = "section"
    return state


def remove_selected(state: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the selected item."""
    if not state["selected_id"]:
        return state

    if state["selected_type"] == "resource":
        idx = int(state["selected_id"].split("_")[1])
        if idx < len(state["outline"].resources):
            state["outline"].resources.pop(idx)

    elif state["selected_type"] == "section":
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]
        remove_section_at_path(state["outline"].sections, path)

    # Clear selection
    state["selected_id"] = None
    state["selected_type"] = None
    return state


# ============================================================================
# Document Generation
# ============================================================================


def start_generation() -> List[Any]:
    """Show generation start state."""
    return [
        gr.update(value="🔄 Generating document...", interactive=False),  # generate_btn
        gr.update(value="⏳ Generating your document, please wait...", visible=True),  # generation_status
        gr.update(visible=False),  # output_container
        gr.update(visible=False),  # download_doc_btn
    ]


async def handle_generate(current_state: Dict[str, Any]) -> List[Any]:
    """Generate document from outline."""
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting document generation for outline: {current_state['outline'].title}")
        content = await generate_document(current_state["outline"], current_state.get("session_id"))
        logger.info(f"Generated content length: {len(content)}")

        # Check if content is suspiciously short (just header)
        lines = content.strip().split("\n")
        if len(lines) <= 3 and not any(len(line.strip()) > 50 for line in lines):
            error_msg = (
                f"⚠️ Document generation appears incomplete. Generated only {len(lines)} lines. Check logs for details."
            )
            logger.warning(error_msg)
            return [
                gr.update(value="Generate Document", interactive=True),  # generate_btn
                gr.update(value=error_msg, visible=True),  # generation_status
                gr.update(visible=True),  # output_container
                content
                + "\n\n---\n\n**Debug Info:**\n"
                + f"Content length: {len(content)} characters\nLines: {len(lines)}",  # output_markdown
                gr.update(visible=False),  # download_doc_btn
            ]

        # Save content to a temporary file for download
        filename = f"{current_state['outline'].title}.md" if current_state["outline"].title else "document.md"
        from .session import session_manager

        session_dir = session_manager.get_session_dir(current_state.get("session_id"))
        file_path = os.path.join(session_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)

        return [
            gr.update(value="Generate Document", interactive=True),  # generate_btn
            gr.update(value="✅ Document generated successfully!", visible=True),  # generation_status
            gr.update(visible=True),  # output_container
            content,  # output_markdown
            gr.update(  # download_doc_btn
                visible=True, value=file_path, label=f"Download {filename}"
            ),
        ]
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        logger.error(f"Document generation failed: {str(e)}")
        logger.error(f"Full traceback: {error_details}")

        return [
            gr.update(value="Generate Document", interactive=True),  # generate_btn
            gr.update(value=f"❌ Error: {str(e)}", visible=True),  # generation_status
            gr.update(visible=True),  # output_container
            f"Error generating document: {str(e)}\n\n---\n\n**Full Error Details:**\n```\n{error_details}\n```",  # output_markdown
            gr.update(visible=False),  # download_doc_btn
        ]


# ============================================================================
# Main UI Builder
# ============================================================================


def build_editor() -> gr.Blocks:
    """Create the main Gradio Blocks application."""

    # CSS for vertical radio buttons and section backgrounds
    custom_css = """
    .radio-vertical .wrap {
        flex-direction: column;
    }
    .section-block {
        background-color: var(--block-background-fill) !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        border-radius: var(--block-radius) !important;
        border: 1px solid var(--block-border-color) !important;
    }
    .preview-block {
        padding: 16px !important;
        margin: 8px 0 !important;
        border-radius: var(--block-radius) !important;
        border: 1px solid var(--block-border-color) !important;
    }
    """

    with gr.Blocks(title="Document Generator", theme="soft", css=custom_css) as app:
        state = gr.State(create_initial_state())

        gr.Markdown("# Document Generator")
        gr.Markdown("Create structured documents with AI assistance")

        with gr.Row():
            # Left Column - Lists
            with gr.Column(scale=3, min_width=300):
                # Input options
                with gr.Tabs():
                    with gr.TabItem("Upload Docpack"):
                        upload_btn = gr.UploadButton("Upload Docpack", file_types=[".docpack"], variant="secondary")

                    with gr.TabItem("Examples"):
                        # Create dropdown choices from example outlines
                        from .config import settings

                        example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_outlines)]
                        example_dropdown = gr.Dropdown(choices=example_choices, label="Example Outlines", type="index")
                        load_example_btn = gr.Button("Load Example", variant="secondary")

                # Document metadata
                title = gr.Textbox(label="Document Title", placeholder="Enter your document title...")
                instructions = gr.TextArea(
                    label="General Instructions", placeholder="Overall guidance for document generation...", lines=3
                )

                # Resources section
                with gr.Column(elem_classes="section-block"):
                    gr.Markdown("### Resources")
                    resource_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="resource_radio",
                        elem_classes=["radio-vertical"],
                    )
                    with gr.Row():
                        resource_add_btn = gr.Button("+ Add", size="sm")
                        resource_remove_btn = gr.Button("- Remove", size="sm")

                # Sections section
                with gr.Column(elem_classes="section-block"):
                    gr.Markdown("### Document Structure")
                    gr.Markdown(
                        "*Note: Changing resource keys may require re-selecting sections that reference them*",
                        elem_classes=["markdown-small"],
                    )
                    section_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="section_radio",
                        elem_classes=["radio-vertical"],
                    )

                    with gr.Row():
                        section_add_btn = gr.Button("+ Add", size="sm")
                        section_sub_btn = gr.Button("+ Sub", size="sm")
                        section_remove_btn = gr.Button("- Remove", size="sm")

            # Right Column - Editor
            with gr.Column(scale=2, min_width=300):
                # Empty state
                empty_state = gr.Markdown("### Select an item to edit", visible=True)

                # Editors
                resource_editor = create_resource_editor()
                section_editor = create_section_editor()

                # Validation message
                validation_message = gr.Markdown(visible=False)

                # Generation section
                gr.Markdown("---")
                generate_btn = gr.Button("Generate Document", variant="primary", interactive=False)
                generation_status = gr.Markdown(visible=False)

                download_doc_btn = gr.DownloadButton("Download Document", visible=False)

                # Download docpack section
                gr.Markdown("---")
                download_docpack_btn = gr.DownloadButton(
                    "Generated docpack archive for download", variant="secondary", visible=False
                )

                # Reset button
                with gr.Row():
                    reset_btn = gr.Button("Reset Outline", variant="secondary", size="sm")

                # Live JSON preview
                with gr.Accordion("Outline Preview (JSON)", open=False):
                    json_preview = gr.Code(
                        label="Current Outline Structure",
                        language="json",
                        interactive=False,
                        wrap_lines=True,
                        lines=20,
                    )

        # Output area
        output_container = gr.Column(visible=False, elem_classes="preview-block")
        with output_container:
            output_markdown = gr.Markdown()

        # ====================================================================
        # Event Handlers
        # ====================================================================

        def update_lists(state_data):
            """Update both radio lists based on state."""
            resource_choices = generate_resource_choices(state_data)
            section_choices = generate_section_choices(state_data)

            # Get current selection
            selected_value = None
            if state_data["selected_type"] == "resource":
                selected_value = state_data["selected_id"]

            return (
                gr.update(
                    choices=resource_choices,
                    value=selected_value if state_data["selected_type"] == "resource" else None,
                ),
                gr.update(
                    choices=section_choices,
                    value=state_data["selected_id"] if state_data["selected_type"] == "section" else None,
                ),
            )

        def handle_selection(selected_id, selected_type, current_state):
            """Handle radio selection and update editors."""
            if not selected_id:
                # Clear selection
                current_state["selected_id"] = None
                current_state["selected_type"] = None
                return [
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    "",
                    "",
                    gr.update(visible=False),
                    "",
                    "",
                    "",
                    [],
                    "",
                    gr.update(selected="upload_file"),
                    gr.update(selected="prompt_mode"),
                ]

            # Update state
            new_state = select_item(selected_id, selected_type, current_state)

            # Update UI visibility
            show_resource = selected_type == "resource"
            show_section = selected_type == "section"

            # Default values
            res_key = ""
            res_desc = ""
            res_url = ""
            bundled_file_info = gr.update(visible=False)
            sec_title = ""
            sec_prompt = ""
            sec_refs = []
            sec_resource_key = ""

            # Update resource editor values
            if show_resource:
                idx = int(selected_id.split("_")[1])
                if idx < len(new_state["outline"].resources):
                    res = new_state["outline"].resources[idx]
                    res_key = res.key or ""
                    res_desc = res.description or ""
                    # Handle URL vs bundled file display
                    if res.path and res.path.startswith(("http://", "https://")):
                        res_url = res.path
                        bundled_file_info = gr.update(visible=False)
                    else:
                        res_url = ""  # Leave URL field empty for bundled files
                        if res.path:
                            # Check if file actually exists in session
                            from .session import session_manager

                            files_dir = session_manager.get_files_dir(new_state.get("session_id"))
                            file_path = files_dir / res.path

                            if file_path.exists():
                                bundled_file_info = gr.update(value=f"**Bundled File:** `{res.path}` ✓", visible=True)
                            else:
                                bundled_file_info = gr.update(
                                    value=f"**Referenced File:** `{res.path}` ⚠️ *File not uploaded*", visible=True
                                )
                        else:
                            bundled_file_info = gr.update(visible=False)

            # Determine which resource source tab should be selected
            # Check if path is a URL
            is_url = res_url.startswith(("http://", "https://")) if res_url else False
            resource_source_tab_selected = "url_tab" if show_resource and is_url else "upload_file"

            # Update section editor values and determine content mode tab
            sec = None
            content_mode_tab_selected = "prompt_mode"  # default
            if show_section:
                path = [int(p) for p in selected_id.split("_")[1:]]
                sec = get_section_at_path(new_state["outline"].sections, path)
                if sec:
                    sec_title = sec.title or ""
                    sec_prompt = sec.prompt or ""
                    # Filter out refs that no longer exist
                    valid_keys = [r.key for r in new_state["outline"].resources if r.key]
                    sec_refs = [ref for ref in (sec.refs or []) if ref in valid_keys]
                    sec_resource_key = sec.resource_key or ""

                    # Set mode based on current data if not already set
                    if not hasattr(sec, "_mode") or sec._mode is None:
                        sec._mode = "Static" if sec_resource_key and not sec_prompt else "Prompt"

                    # Determine which content mode tab should be selected based on section mode
                    content_mode_tab_selected = (
                        "static_mode" if getattr(sec, "_mode", None) == "Static" else "prompt_mode"
                    )

            # Update radio choices
            resource_choices = generate_resource_choices(new_state)
            section_choices = generate_section_choices(new_state)

            # Only the radio for the selected type should have a value
            resource_value = new_state["selected_id"] if selected_type == "resource" else None
            section_value = new_state["selected_id"] if selected_type == "section" else None

            return [
                new_state,
                gr.update(choices=resource_choices, value=resource_value),
                gr.update(choices=section_choices, value=section_value),
                gr.update(visible=not (show_resource or show_section)),
                gr.update(visible=show_resource),
                gr.update(visible=show_section),
                res_key,
                res_desc,
                bundled_file_info,
                res_url,
                sec_title,
                sec_prompt,
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key], value=sec_refs if sec_refs else []
                ),
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key],
                    value=sec_resource_key
                    if sec_resource_key and sec_resource_key in [r.key for r in new_state["outline"].resources if r.key]
                    else None,
                ),
                gr.update(selected=resource_source_tab_selected),
                gr.update(selected=content_mode_tab_selected),
            ]

        def handle_resource_click(val, current_state):
            """Handle resource radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 15
            result = handle_selection(val, "resource", current_state)
            result[1] = gr.update()  # Don't update the resource radio itself
            return result

        def handle_section_click(val, current_state):
            """Handle section radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 15
            result = handle_selection(val, "section", current_state)
            result[2] = gr.update()  # Don't update the section radio itself
            return result

        def update_metadata(state_data, doc_title, doc_instructions):
            """Update document metadata in state."""
            if state_data:
                state_data["outline"].title = doc_title or ""
                state_data["outline"].general_instruction = doc_instructions or ""
            resource_choices, section_choices = update_lists(state_data)
            json_str, validation_msg, generate_btn_update, download_btn_update = validate_and_preview(state_data)
            return (
                state_data,
                resource_choices,
                section_choices,
                json_str,
                validation_msg,
                generate_btn_update,
                download_btn_update,
            )

        def handle_add_resource(current_state):
            """Add a new resource."""
            new_state = add_resource(current_state)
            return handle_selection(new_state["selected_id"], new_state["selected_type"], new_state)

        def handle_add_section(current_state, as_subsection=False):
            """Add a new section."""
            new_state = add_section(current_state, as_subsection)
            return handle_selection(new_state["selected_id"], new_state["selected_type"], new_state)

        def auto_save_resource_field(field_name, value, current_state):
            """Auto-save a resource field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "resource":
                json_str, validation_msg, generate_btn_update, download_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current resource data
            idx = int(current_state["selected_id"].split("_")[1])
            if idx >= len(current_state["outline"].resources):
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Update the specific field
            resource = current_state["outline"].resources[idx]
            setattr(resource, field_name, value)

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            # If changing a resource key, clear any section selection to avoid ref conflicts
            if field_name == "key":
                return (
                    current_state,
                    gr.update(choices=resource_choices, value=current_state["selected_id"]),
                    gr.update(choices=section_choices, value=None),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            return (
                current_state,
                gr.update(choices=resource_choices, value=current_state["selected_id"]),
                gr.update(choices=section_choices),
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def auto_save_section_field(field_name, value, current_state):
            """Auto-save a section field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Set the field value
            setattr(section, field_name, value)

            # Only update mode if not explicitly set or if there's a clear indication
            if not hasattr(section, "_mode") or section._mode is None:
                # Auto-detect mode based on field values for new sections
                if hasattr(section, "resource_key") and hasattr(section, "prompt"):
                    if section.resource_key and not section.prompt:
                        section._mode = "Static"
                    else:
                        section._mode = "Prompt"

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def handle_remove(current_state):
            """Remove selected item."""
            new_state = remove_selected(current_state)
            resource_choices, section_choices = update_lists(new_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(new_state)
            return [
                new_state,
                resource_choices,
                section_choices,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                json_str,
                validation_msg,
                generate_btn_update,
            ]

        def handle_upload(file, current_state):
            """Upload and extract a .docpack file to load outline and resources into the editor."""
            if file:
                from pathlib import Path
                from .session import session_manager

                # Extract package to session directory
                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                package_path = Path(file)

                try:
                    outline_data, resource_files = DocpackHandler.extract_package(package_path, session_dir)
                    current_state["outline"] = Outline.from_dict(outline_data)
                    current_state["selected_id"] = None
                    current_state["selected_type"] = None

                    # Update UI
                    resource_choices, section_choices = update_lists(current_state)
                    json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                    return [
                        current_state,
                        current_state["outline"].title,
                        current_state["outline"].general_instruction,
                        resource_choices,
                        section_choices,
                        gr.update(visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        json_str,
                        validation_msg,
                        generate_btn_update,
                    ]
                except Exception as e:
                    print(f"Error extracting docpack: {str(e)}")
                    return [current_state] + [gr.update()] * 10
            return [current_state] + [gr.update()] * 10

        def handle_load_example(example_idx, current_state):
            """Load a pre-built example outline (README or Product Launch Documentation) into the editor."""
            if example_idx is None:
                return [current_state] + [gr.update()] * 10

            try:
                from .config import settings
                from pathlib import Path
                from .session import session_manager

                # Get the example configuration
                example = settings.example_outlines[example_idx]

                # Get the directory where this module is located
                module_dir = Path(__file__).parent.parent
                example_path = module_dir / example.path

                # Extract docpack to session directory
                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                outline_data, resource_files = DocpackHandler.extract_package(example_path, session_dir)

                # Update state with loaded outline
                current_state["outline"] = Outline.from_dict(outline_data)
                current_state["selected_id"] = None
                current_state["selected_type"] = None

                # Update UI
                resource_choices, section_choices = update_lists(current_state)
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                return [
                    current_state,
                    current_state["outline"].title,
                    current_state["outline"].general_instruction,
                    resource_choices,
                    section_choices,
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                ]
            except Exception as e:
                # If loading fails, return current state with error
                print(f"Error loading example: {str(e)}")
                return [current_state] + [gr.update()] * 10

        def handle_file_change(file_path, current_state):
            """Handle file upload or deletion and manage session files directory."""
            if not current_state["selected_id"] or current_state["selected_type"] != "resource":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            try:
                from pathlib import Path
                import shutil
                from .session import session_manager

                # Get current resource index
                idx = int(current_state["selected_id"].split("_")[1])
                if idx >= len(current_state["outline"].resources):
                    json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                    return (
                        current_state,
                        gr.update(),
                        gr.update(),
                        gr.update(),
                        json_str,
                        validation_msg,
                        generate_btn_update,
                    )

                resource = current_state["outline"].resources[idx]
                files_dir = session_manager.get_files_dir(current_state.get("session_id"))

                if file_path is None:
                    # File was cleared - delete the existing file and clear resource path
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        # Only delete if it's a file (not a URL)
                        old_file_path = files_dir / resource.path
                        if old_file_path.exists():
                            old_file_path.unlink()
                            print(f"Deleted file: {old_file_path}")

                    # Clear the resource path
                    resource.path = ""

                    # Update bundled file info to show nothing
                    bundled_file_info_update = gr.update(visible=False)

                else:
                    # File was uploaded - copy it and update resource
                    # First, clean up any existing file
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        old_file_path = files_dir / resource.path
                        if old_file_path.exists():
                            old_file_path.unlink()
                            print(f"Replaced file: {old_file_path}")

                    # Copy uploaded file to files directory
                    source_path = Path(file_path)
                    target_path = files_dir / source_path.name
                    shutil.copy2(source_path, target_path)

                    # Update resource with relative path (just filename)
                    resource.path = source_path.name

                    # Update bundled file info to show uploaded file
                    bundled_file_info_update = gr.update(
                        value=f"**Uploaded File:** `{source_path.name}` ✓", visible=True
                    )

                # Update radio choices to reflect changes
                resource_choices = generate_resource_choices(current_state)
                section_choices = generate_section_choices(current_state)

                # Validate and preview
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                return (
                    current_state,
                    gr.update(choices=resource_choices, value=current_state["selected_id"]),
                    gr.update(choices=section_choices),
                    bundled_file_info_update,
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            except Exception as e:
                print(f"Error handling file change: {str(e)}")
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

        def handle_download_docpack(current_state):
            """Create a portable .docpack archive containing the current outline and resources for download."""
            try:
                from .session import session_manager

                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                files_dir = session_manager.get_files_dir(current_state.get("session_id"))

                # Get current outline data
                outline_data = current_state["outline"].to_dict()

                # Find resource files in session files directory
                resource_files = []
                for resource in current_state["outline"].resources:
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        # Only include uploaded files (not URLs)
                        resource_path = files_dir / resource.path
                        if resource_path.exists():
                            resource_files.append(resource_path)

                # Create docpack filename
                title = current_state["outline"].title or "outline"
                # Sanitize filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
                filename = f"{safe_title}.docpack"

                # Create docpack in session directory
                docpack_path = session_dir / filename
                DocpackHandler.create_package(outline_data, resource_files, docpack_path)

                return gr.update(value=str(docpack_path), label=f"Download {filename}")

            except Exception as e:
                print(f"Error creating docpack: {str(e)}")
                return gr.update()

        def handle_reset_outline(current_state):
            """Reset the outline to initial state."""
            # Create fresh initial state but keep the same session_id
            session_id = current_state.get("session_id")
            new_state = create_initial_state()
            new_state["session_id"] = session_id

            # Clear any uploaded files from the session
            try:
                from .session import session_manager

                files_dir = session_manager.get_files_dir(session_id)
                if files_dir.exists():
                    import shutil

                    shutil.rmtree(files_dir)
                    files_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not clear session files: {str(e)}")

            # Update all UI components to initial state
            json_str, validation_msg, generate_btn_update, download_btn_update = validate_and_preview(new_state)

            return [
                new_state,  # state
                "",  # title
                "",  # instructions
                gr.update(choices=[], value=None),  # resource_radio
                gr.update(choices=[], value=None),  # section_radio
                gr.update(visible=True),  # empty_state
                gr.update(visible=False),  # resource_editor container
                gr.update(visible=False),  # section_editor container
                json_str,  # json_preview
                validation_msg,  # validation_message
                generate_btn_update,  # generate_btn
                download_btn_update,  # download_docpack_btn
                gr.update(visible=False),  # generation_status
                gr.update(visible=False),  # output_container
                gr.update(visible=False),  # download_doc_btn
            ]

        # ====================================================================
        # Connect Event Handlers
        # ====================================================================

        # Radio selections
        resource_radio.change(
            handle_resource_click,
            inputs=[resource_radio, state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
            api_name=False,
        )

        section_radio.change(
            handle_section_click,
            inputs=[section_radio, state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
            api_name=False,
        )

        # Metadata updates
        title.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[
                state,
                resource_radio,
                section_radio,
                json_preview,
                validation_message,
                generate_btn,
                download_docpack_btn,
            ],
            api_name=False,
        )

        instructions.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[
                state,
                resource_radio,
                section_radio,
                json_preview,
                validation_message,
                generate_btn,
                download_docpack_btn,
            ],
            api_name=False,
        )

        # Add/Remove buttons
        resource_add_btn.click(
            handle_add_resource,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
            api_name=False,
        )

        section_add_btn.click(
            lambda s: handle_add_section(s, False),
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
            api_name=False,
        )

        section_sub_btn.click(
            lambda s: handle_add_section(s, True),
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
            api_name=False,
        )

        resource_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        section_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        # Auto-save resource fields
        resource_editor["key"].change(
            lambda v, s: auto_save_resource_field("key", v, s),
            inputs=[resource_editor["key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        resource_editor["description"].change(
            lambda v, s: auto_save_resource_field("description", v, s),
            inputs=[resource_editor["description"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        resource_editor["url"].change(
            lambda v, s: auto_save_resource_field("path", v, s),
            inputs=[resource_editor["url"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        resource_editor["file"].change(
            handle_file_change,
            inputs=[resource_editor["file"], state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                resource_editor["bundled_file_info"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        # Auto-save section fields
        section_editor["title"].change(
            lambda v, s: auto_save_section_field("title", v, s),
            inputs=[section_editor["title"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        section_editor["prompt"].change(
            lambda v, s: auto_save_section_field("prompt", v, s),
            inputs=[section_editor["prompt"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        section_editor["refs"].change(
            lambda v, s: auto_save_section_field("refs", v, s),
            inputs=[section_editor["refs"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        section_editor["resource_key"].change(
            lambda v, s: auto_save_section_field("resource_key", v, s),
            inputs=[section_editor["resource_key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
            api_name=False,
        )

        # Handle content mode tab changes via individual tab events
        def handle_prompt_tab_select(current_state):
            """Handle switching to prompt mode tab."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Set prompt mode (but keep all field values)
            section._mode = "Prompt"
            # Ensure prompt fields exist
            if not section.prompt:
                section.prompt = ""

            # Update UI (don't clear fields, just update choices and JSON)
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                gr.update(),  # Keep current resource_key value (don't change UI)
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def handle_static_tab_select(current_state):
            """Handle switching to static mode tab."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Set static mode (but keep all field values)
            section._mode = "Static"
            # Set to first available resource if no resource is selected
            if not section.resource_key and current_state["outline"].resources:
                available_resources = [r.key for r in current_state["outline"].resources if r.key]
                if available_resources:
                    section.resource_key = available_resources[0]

            # Update UI (don't clear fields, just update choices and JSON)
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                gr.update(),  # Keep current prompt value (don't change UI)
                gr.update(),  # Keep current refs value (don't change UI)
                json_str,
                validation_msg,
                generate_btn_update,
            )

        # Upload handler
        upload_btn.upload(
            handle_upload,
            inputs=[upload_btn, state],
            outputs=[
                state,
                title,
                instructions,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        # Example load handler
        load_example_btn.click(
            handle_load_example,
            inputs=[example_dropdown, state],
            outputs=[
                state,
                title,
                instructions,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,  # Disable UI handler API, use dedicated api_load_example instead
        )

        # Generate handler
        generate_btn.click(
            start_generation,
            outputs=[generate_btn, generation_status, output_container, download_doc_btn],
            api_name=False,
        ).then(
            handle_generate,
            inputs=[state],
            outputs=[generate_btn, generation_status, output_container, output_markdown, download_doc_btn],
            api_name=False,
        )

        # Tab change handlers for content mode
        section_editor["prompt_tab"].select(
            handle_prompt_tab_select,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                section_editor["resource_key"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        section_editor["static_tab"].select(
            handle_static_tab_select,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                section_editor["prompt"],
                section_editor["refs"],
                json_preview,
                validation_message,
                generate_btn,
            ],
            api_name=False,
        )

        # Set up download docpack handler to update with file path when clicked
        download_docpack_btn.click(
            handle_download_docpack,
            inputs=[state],
            outputs=[download_docpack_btn],
            api_name=False,  # Disable UI handler API - this is session-specific
        )

        # Reset button handler
        reset_btn.click(
            handle_reset_outline,
            inputs=[state],
            outputs=[
                state,
                title,
                instructions,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
                download_docpack_btn,
                generation_status,
                output_container,
                download_doc_btn,
            ],
            api_name=False,
        )

        # Initial validation on load
        app.load(
            lambda s: validate_and_preview(s),
            inputs=[state],
            outputs=[json_preview, validation_message, generate_btn, download_docpack_btn],
            api_name=False,
        )

        # ====================================================================
        # Dedicated API Functions with Clear Documentation
        # ====================================================================

        def api_list_examples() -> str:
            """List available example document templates with names, indices, and descriptions. Returns JSON array that can be used with load_example()."""
            from .config import settings
            import json

            examples = []
            for idx, example in enumerate(settings.example_outlines):
                examples.append({
                    "name": example.name,
                    "index": idx,
                    "description": f"Pre-built template for {example.name.lower()}",
                })

            return json.dumps(examples, indent=2)

        def api_generate_document(outline_json: str) -> str:
            """Generate complete Markdown document from JSON outline specification containing title, instructions, resources, and sections using AI assistance.

            Args:
                outline_json (str): JSON outline with title, general_instruction, resources array, and sections array

            Returns:
                str: Generated Markdown document
            """
            import json
            import asyncio
            from .models.outline import Outline
            from .executor.runner import generate_document

            try:
                outline_data = json.loads(outline_json)
                outline = Outline.from_dict(outline_data)

                # Run async generation in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    content = loop.run_until_complete(generate_document(outline, None))
                    return content
                finally:
                    loop.close()

            except Exception as e:
                return f"Error generating document: {str(e)}"

        def api_validate_outline(outline_json: str) -> str:
            """Validate outline JSON structure and return detailed validation results with errors and success status.

            Args:
                outline_json (str): JSON outline specification to validate

            Returns:
                str: Validation results as JSON with valid boolean, message, and errors array
            """
            import json
            from .models.outline import validate_outline

            try:
                outline_data = json.loads(outline_json)
                validate_outline(outline_data)
                return json.dumps({"valid": True, "message": "Outline is valid and ready for generation", "errors": []})
            except json.JSONDecodeError as e:
                return json.dumps({"valid": False, "message": "Invalid JSON format", "errors": [str(e)]})
            except Exception as e:
                return json.dumps({"valid": False, "message": "Validation failed", "errors": [str(e)]})

        def api_create_template(document_type: str) -> str:
            """Create template outline JSON for common document types including readme, api, research, manual, or basic structures.

            Args:
                document_type (str): Template type - readme, api, research, manual, or basic

            Returns:
                str: JSON outline template ready for customization
            """
            import json

            templates = {
                "readme": {
                    "title": "Project README",
                    "general_instruction": "Create comprehensive README documentation that helps users understand and use the project",
                    "resources": [],
                    "sections": [
                        {
                            "title": "Description",
                            "prompt": "Provide a clear description of what this project does and its main purpose",
                        },
                        {"title": "Installation", "prompt": "Explain how to install and set up the project"},
                        {"title": "Usage", "prompt": "Show examples of how to use the project with code samples"},
                        {"title": "Contributing", "prompt": "Describe how others can contribute to the project"},
                    ],
                },
                "api": {
                    "title": "API Documentation",
                    "general_instruction": "Create comprehensive API documentation for developers",
                    "resources": [],
                    "sections": [
                        {"title": "Authentication", "prompt": "Explain how to authenticate with the API"},
                        {
                            "title": "Endpoints",
                            "prompt": "Document all available endpoints with parameters and responses",
                        },
                        {"title": "Examples", "prompt": "Provide code examples in multiple languages"},
                        {"title": "Error Handling", "prompt": "Document error codes and how to handle them"},
                    ],
                },
                "research": {
                    "title": "Research Document",
                    "general_instruction": "Create a structured research document with clear methodology and findings",
                    "resources": [],
                    "sections": [
                        {
                            "title": "Abstract",
                            "prompt": "Summarize the research question, methodology, and key findings",
                        },
                        {"title": "Methodology", "prompt": "Describe the research methods and approach used"},
                        {"title": "Results", "prompt": "Present the findings and analysis"},
                        {"title": "Conclusions", "prompt": "Discuss implications and future research directions"},
                    ],
                },
                "manual": {
                    "title": "User Manual",
                    "general_instruction": "Create a comprehensive user manual that guides users through all features",
                    "resources": [],
                    "sections": [
                        {"title": "Getting Started", "prompt": "Help users set up and take their first steps"},
                        {"title": "Features", "prompt": "Explain all major features and how to use them"},
                        {"title": "Troubleshooting", "prompt": "Address common issues and their solutions"},
                        {"title": "FAQ", "prompt": "Answer frequently asked questions"},
                    ],
                },
                "basic": {
                    "title": "New Document",
                    "general_instruction": "Create a well-structured document",
                    "resources": [],
                    "sections": [
                        {"title": "Introduction", "prompt": "Introduce the topic and main points"},
                        {"title": "Main Content", "prompt": "Develop the main content and ideas"},
                        {"title": "Conclusion", "prompt": "Summarize key points and takeaways"},
                    ],
                },
            }

            template = templates.get(document_type.lower(), templates["basic"])
            return json.dumps(template, indent=2)

        def api_load_example(example_index: int) -> str:
            """Load pre-built example outline by index returning complete JSON outline for document generation.

            Args:
                example_index (int): Zero-based index of example to load (use list_examples to see available options)

            Returns:
                str: Complete JSON outline ready for generation or customization
            """
            try:
                from .config import settings
                from pathlib import Path
                from .package_handler import DocpackHandler
                import tempfile
                import json

                if example_index < 0 or example_index >= len(settings.example_outlines):
                    return json.dumps({"error": f"Invalid example index. Use 0-{len(settings.example_outlines) - 1}"})

                example = settings.example_outlines[example_index]
                module_dir = Path(__file__).parent.parent
                example_path = module_dir / example.path

                # Extract to temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    outline_data, _ = DocpackHandler.extract_package(example_path, Path(temp_dir))
                    return json.dumps(outline_data, indent=2)

            except Exception as e:
                import json

                return json.dumps({"error": f"Failed to load example: {str(e)}"})

        def api_get_outline_schema() -> str:
            """Get JSON schema specification for valid outline structure showing required fields and data types.

            Returns:
                str: JSON schema defining outline structure requirements
            """
            import json

            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "general_instruction": {
                        "type": "string",
                        "description": "Overall guidance for document generation",
                    },
                    "resources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Unique identifier for referencing"},
                                "path": {"type": "string", "description": "File path or URL to resource"},
                                "description": {"type": "string", "description": "Description of resource content"},
                            },
                            "required": ["key", "path"],
                        },
                    },
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Section title"},
                                "prompt": {"type": "string", "description": "Instructions for AI generation"},
                                "refs": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Resource keys to reference",
                                },
                                "resource_key": {
                                    "type": "string",
                                    "description": "Single resource key for static content",
                                },
                                "sections": {"type": "array", "description": "Nested subsections (recursive)"},
                            },
                            "required": ["title"],
                        },
                    },
                },
                "required": ["title"],
            }

            return json.dumps(schema, indent=2)

        # Register API functions with clear names and documentation using dummy components
        # This approach ensures compatibility across Gradio versions

        # Create hidden textboxes for API endpoints
        api_input = gr.Textbox(visible=False)
        api_output = gr.Textbox(visible=False)
        api_input_int = gr.Number(visible=False)

        # Register API endpoints with proper documentation
        api_input.submit(fn=api_list_examples, inputs=[], outputs=[api_output], api_name="list_examples")

        api_input.submit(fn=api_get_outline_schema, inputs=[], outputs=[api_output], api_name="get_outline_schema")

        api_input.submit(fn=api_create_template, inputs=[api_input], outputs=[api_output], api_name="create_template")

        api_input_int.submit(fn=api_load_example, inputs=[api_input_int], outputs=[api_output], api_name="load_example")

        api_input.submit(fn=api_validate_outline, inputs=[api_input], outputs=[api_output], api_name="validate_outline")

        api_input.submit(
            fn=api_generate_document, inputs=[api_input], outputs=[api_output], api_name="generate_document"
        )

    return app


