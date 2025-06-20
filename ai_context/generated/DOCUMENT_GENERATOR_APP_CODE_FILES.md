# apps/document-generator/document_generator_app

[collect-files]

**Search:** ['apps/document-generator/document_generator_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 6/18/2025, 3:22:46 PM
**Files:** 9

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
import tempfile
from pathlib import Path

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..models.outline import Outline
from typing import Optional


async def generate_document(outline: Optional[Outline]) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    # Allow stub invocation without an outline for initial tests
    if outline is None:
        return ""
    from urllib.parse import urlparse
    import urllib.request

    REPO_ROOT = Path(__file__).resolve().parents[4]
    RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
    RECIPE_ROOT = RECIPE_PATH.parent

    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve resource paths: download URLs or locate local files
        for res in outline.resources:
            if res.path:
                parsed = urlparse(res.path)
                if parsed.scheme in ("http", "https"):
                    dest = Path(tmpdir) / Path(parsed.path).name
                    urllib.request.urlretrieve(res.path, dest)
                    res.path = str(dest)
                else:
                    p = Path(res.path)
                    if not p.exists():
                        p2 = RECIPE_ROOT / res.path
                        if p2.exists():
                            res.path = str(p2)
                    else:
                        res.path = str(p)

        data = outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)

        logger = init_logger(log_dir=tmpdir)
        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
            }
        )
        executor = Executor(logger)
        await executor.execute(str(RECIPE_PATH), context)

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        if not filename:
            return context.get("document", "")

        document_path = output_root / f"{filename}.md"
        try:
            return document_path.read_text()
        except FileNotFoundError:
            return f"Generated file not found: {document_path}"


=== File: apps/document-generator/document_generator_app/main.py ===
"""
Main entrypoint for the Document Generator App UI.
"""

from document_generator_app.ui import build_editor


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""
    build_editor().launch(mcp_server=True, pwa=True)


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

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from jsonschema import validate


@dataclass
class Resource:
    key: str
    path: str
    description: str
    merge_mode: str


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)
    _mode: Optional[str] = field(default=None, init=False, repr=False)  # Internal mode tracking

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None values and empty refs to match schema."""
        result = {"title": self.title}

        # Use mode to determine which fields to include
        if self._mode == "Static" and self.resource_key is not None:
            result["resource_key"] = self.resource_key
        else:
            # Default to prompt mode
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
            "resources": [asdict(r) for r in self.resources],
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
                    merge_mode=r.get("merge_mode", "concat"),
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
                    "merge_mode": {"type": "string", "enum": ["concat", "dict"]},
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


=== File: apps/document-generator/document_generator_app/ui.py ===
"""
Simplified UI for Document Generator - all UI code in one module.
Following "ruthless simplicity" principle.
"""

import gradio as gr
import json
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple

from .models.outline import Outline, Resource, Section, validate_outline
from .executor.runner import generate_document


# ============================================================================
# State Management
# ============================================================================


def create_initial_state() -> Dict[str, Any]:
    """Create initial app state."""
    return {
        "outline": Outline(title="", general_instruction=""),
        "selected_type": None,  # "resource" or "section"
        "selected_id": None,  # e.g., "resource_0" or "section_1_2"
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


def create_resource_editor() -> Dict[str, gr.components.Component]:
    """Create the resource editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Resource")

        key = gr.Textbox(label="Key *", placeholder="unique_key")
        description = gr.TextArea(label="Description", placeholder="Describe what this resource contains...", lines=3)

        gr.Markdown("#### File Source")
        file = gr.File(label="Upload File", file_types=None)
        gr.Markdown("*OR*")
        path = gr.Textbox(label="File Path / URL", placeholder="/path/to/file.txt or https://example.com/data")

        merge_mode = gr.Radio(label="Merge Mode", choices=["concat", "dict"], value="concat")

    return {
        "container": container,
        "key": key,
        "description": description,
        "file": file,
        "path": path,
        "merge_mode": merge_mode,
    }


def create_section_editor() -> Dict[str, gr.components.Component]:
    """Create the section editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Section")

        title = gr.Textbox(label="Title *", placeholder="Section Title")

        mode = gr.Radio(label="Content Mode", choices=["Prompt", "Static"], value="Prompt")

        # Prompt mode inputs
        with gr.Column(visible=True) as prompt_container:
            prompt = gr.TextArea(label="Prompt", placeholder="Instructions for generating this section...", lines=4)

            # Note: We'll populate choices dynamically
            refs = gr.Dropdown(label="Resource References", choices=[], multiselect=True, interactive=True)

        # Static mode inputs
        with gr.Column(visible=False) as static_container:
            resource_key = gr.Dropdown(label="Resource Key", choices=[], interactive=True)

    return {
        "container": container,
        "title": title,
        "mode": mode,
        "prompt": prompt,
        "refs": refs,
        "resource_key": resource_key,
        "prompt_container": prompt_container,
        "static_container": static_container,
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


def validate_and_preview(state_data: Dict[str, Any]) -> Tuple[str, Any, Any]:
    """Validate outline and update JSON preview."""
    if not state_data:
        return "", gr.update(visible=False), gr.update(interactive=False)

    try:
        outline_dict = state_data["outline"].to_dict()
        json_str = json.dumps(outline_dict, indent=2)

        is_valid, message = validate_outline_data(state_data["outline"])

        if is_valid:
            return json_str, gr.update(visible=False), gr.update(interactive=True)
        else:
            return json_str, gr.update(value=f"⚠️ {message}", visible=True), gr.update(interactive=False)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", gr.update(value=error_msg, visible=True), gr.update(interactive=False)


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
    state["outline"].resources.append(Resource(key="", path="", description="", merge_mode="concat"))
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
    try:
        content = await generate_document(current_state["outline"])

        # Save content to a temporary file for download
        filename = f"{current_state['outline'].title}.md" if current_state["outline"].title else "document.md"
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
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
        return [
            gr.update(value="Generate Document", interactive=True),  # generate_btn
            gr.update(value=f"❌ Error: {str(e)}", visible=True),  # generation_status
            gr.update(visible=True),  # output_container
            f"Error generating document: {str(e)}",  # output_markdown
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
                # Upload button
                upload_btn = gr.UploadButton("Upload Outline", file_types=[".json"], variant="secondary", size="sm")

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
                    gr.Markdown("### Sections")
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

                # Live JSON preview
                with gr.Accordion("JSON Preview", open=False):
                    json_preview = gr.Code(label=None, language="json", interactive=False, wrap_lines=True, lines=20)

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
                    "",
                    "concat",
                    "",
                    "Prompt",
                    "",
                    [],
                    "",
                ]

            # Update state
            new_state = select_item(selected_id, selected_type, current_state)

            # Update UI visibility
            show_resource = selected_type == "resource"
            show_section = selected_type == "section"

            # Default values
            res_key = ""
            res_desc = ""
            res_path = ""
            res_merge = "concat"
            sec_title = ""
            sec_mode = "Prompt"
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
                    res_path = res.path or ""
                    res_merge = res.merge_mode or "concat"

            # Update section editor values
            if show_section:
                path = [int(p) for p in selected_id.split("_")[1:]]
                sec = get_section_at_path(new_state["outline"].sections, path)
                if sec:
                    sec_title = sec.title or ""
                    # Determine mode based on current data
                    sec_mode = "Static" if sec.resource_key else "Prompt"
                    # Update the section's mode for proper serialization
                    sec._mode = sec_mode
                    sec_prompt = sec.prompt or ""
                    # Filter out refs that no longer exist
                    valid_keys = [r.key for r in new_state["outline"].resources if r.key]
                    sec_refs = [ref for ref in (sec.refs or []) if ref in valid_keys]
                    sec_resource_key = sec.resource_key or ""

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
                res_path,
                res_merge,
                sec_title,
                sec_mode,
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
            ]

        def handle_resource_click(val, current_state):
            """Handle resource radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 14
            result = handle_selection(val, "resource", current_state)
            result[1] = gr.update()  # Don't update the resource radio itself
            return result

        def handle_section_click(val, current_state):
            """Handle section radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 14
            result = handle_selection(val, "section", current_state)
            result[2] = gr.update()  # Don't update the section radio itself
            return result

        def update_metadata(state_data, doc_title, doc_instructions):
            """Update document metadata in state."""
            if state_data:
                state_data["outline"].title = doc_title or ""
                state_data["outline"].general_instruction = doc_instructions or ""
            resource_choices, section_choices = update_lists(state_data)
            json_str, validation_msg, generate_btn_update = validate_and_preview(state_data)
            return state_data, resource_choices, section_choices, json_str, validation_msg, generate_btn_update

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
                json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current resource data
            idx = int(current_state["selected_id"].split("_")[1])
            if idx >= len(current_state["outline"].resources):
                json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Update the specific field
            resource = current_state["outline"].resources[idx]
            setattr(resource, field_name, value)

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)

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
                json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Special handling for mode changes
            if field_name == "mode":
                section._mode = value  # Track the mode for serialization
                if value == "Prompt":
                    # Ensure we have a prompt when switching to Prompt mode
                    if not section.prompt:
                        section.prompt = ""
                else:  # Static
                    # Ensure we have a resource_key when switching to Static mode
                    if not section.resource_key:
                        # Try to use the first available resource
                        if current_state["outline"].resources and current_state["outline"].resources[0].key:
                            section.resource_key = current_state["outline"].resources[0].key
            else:
                setattr(section, field_name, value)

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)

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
            json_str, validation_msg, generate_btn_update = validate_and_preview(new_state)
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
            """Upload outline from JSON."""
            if file:
                # Gradio returns the file path as a string
                with open(file, "r") as f:
                    content = f.read()
                data = json.loads(content)
                current_state["outline"] = Outline.from_dict(data)
                current_state["selected_id"] = None
                current_state["selected_type"] = None

                # Update UI
                resource_choices, section_choices = update_lists(current_state)
                json_str, validation_msg, generate_btn_update = validate_and_preview(current_state)

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
            return [current_state] + [gr.update()] * 10

        def toggle_section_mode(mode):
            """Toggle between prompt and static mode."""
            is_prompt = mode == "Prompt"
            return {
                section_editor["prompt_container"]: gr.update(visible=is_prompt),
                section_editor["static_container"]: gr.update(visible=not is_prompt),
            }

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
                resource_editor["path"],
                resource_editor["merge_mode"],
                section_editor["title"],
                section_editor["mode"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
            ],
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
                resource_editor["path"],
                resource_editor["merge_mode"],
                section_editor["title"],
                section_editor["mode"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
            ],
        )

        # Metadata updates
        title.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        instructions.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
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
                resource_editor["path"],
                resource_editor["merge_mode"],
                section_editor["title"],
                section_editor["mode"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
            ],
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
                resource_editor["path"],
                resource_editor["merge_mode"],
                section_editor["title"],
                section_editor["mode"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
            ],
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
                resource_editor["path"],
                resource_editor["merge_mode"],
                section_editor["title"],
                section_editor["mode"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
            ],
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
        )

        # Auto-save resource fields
        resource_editor["key"].change(
            lambda v, s: auto_save_resource_field("key", v, s),
            inputs=[resource_editor["key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["description"].change(
            lambda v, s: auto_save_resource_field("description", v, s),
            inputs=[resource_editor["description"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["path"].change(
            lambda v, s: auto_save_resource_field("path", v, s),
            inputs=[resource_editor["path"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["file"].change(
            lambda v, s: auto_save_resource_field("path", v, s)
            if v
            else (s, gr.update(), gr.update(), gr.update(), gr.update(), gr.update()),
            inputs=[resource_editor["file"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["merge_mode"].change(
            lambda v, s: auto_save_resource_field("merge_mode", v, s),
            inputs=[resource_editor["merge_mode"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        # Auto-save section fields
        section_editor["title"].change(
            lambda v, s: auto_save_section_field("title", v, s),
            inputs=[section_editor["title"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["mode"].change(
            lambda v, s: auto_save_section_field("mode", v, s),
            inputs=[section_editor["mode"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        ).then(
            toggle_section_mode,
            inputs=[section_editor["mode"]],
            outputs=[section_editor["prompt_container"], section_editor["static_container"]],
        )

        section_editor["prompt"].change(
            lambda v, s: auto_save_section_field("prompt", v, s),
            inputs=[section_editor["prompt"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["refs"].change(
            lambda v, s: auto_save_section_field("refs", v, s),
            inputs=[section_editor["refs"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["resource_key"].change(
            lambda v, s: auto_save_section_field("resource_key", v, s),
            inputs=[section_editor["resource_key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
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
        )

        # Generate handler
        generate_btn.click(
            start_generation, outputs=[generate_btn, generation_status, output_container, download_doc_btn]
        ).then(
            handle_generate,
            inputs=[state],
            outputs=[generate_btn, generation_status, output_container, output_markdown, download_doc_btn],
        )

        # Initial validation on load
        app.load(
            lambda s: validate_and_preview(s), inputs=[state], outputs=[json_preview, validation_message, generate_btn]
        )

    return app


