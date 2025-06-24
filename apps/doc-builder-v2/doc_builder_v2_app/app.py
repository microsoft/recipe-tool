import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

import gradio as gr
from dotenv import load_dotenv

from .executor.runner import generate_document
from .models.outline import Outline, Resource, Section

# Load environment variables from .env file
load_dotenv()


def json_to_outline(json_data: Dict[str, Any]) -> Outline:
    """Convert JSON structure to Outline dataclasses."""
    # Create outline with basic metadata
    outline = Outline(title=json_data.get("title", ""), general_instruction=json_data.get("general_instruction", ""))

    # Convert resources
    for res_data in json_data.get("resources", []):
        resource = Resource(
            key=res_data["key"],
            path=res_data["path"],
            description=res_data["description"],
            merge_mode="concat",  # Default merge mode
        )
        outline.resources.append(resource)

    # Helper function to convert sections recursively
    def convert_sections(sections_data: List[Dict[str, Any]]) -> List[Section]:
        sections = []
        for sec_data in sections_data:
            section = Section(title=sec_data.get("title", ""))

            # Check if it has prompt (AI block) or resource_key (text block)
            if "prompt" in sec_data:
                # AI block
                section.prompt = sec_data["prompt"]
                section.refs = sec_data.get("refs", [])
                section._mode = None  # Default mode
            elif "resource_key" in sec_data:
                # Text block
                section.resource_key = sec_data["resource_key"]
                section._mode = "Static"

            # Convert nested sections
            if "sections" in sec_data:
                section.sections = convert_sections(sec_data["sections"])

            sections.append(section)

        return sections

    # Convert top-level sections
    outline.sections = convert_sections(json_data.get("sections", []))

    return outline


def add_ai_block(blocks, focused_block_id=None):
    """Add an AI content block."""
    new_block = {
        "id": str(uuid.uuid4()),
        "type": "ai",
        "heading": "",
        "content": "",
        "resources": [],
        "collapsed": True,  # Start collapsed
        "indent_level": 0,
    }

    # If no focused block or focused block not found, add at the end
    if not focused_block_id:
        return blocks + [new_block]

    # Find the focused block and insert after it
    for i, block in enumerate(blocks):
        if block["id"] == focused_block_id:
            # Inherit the indent level from the focused block
            new_block["indent_level"] = block.get("indent_level", 0)
            # Insert after the focused block
            return blocks[: i + 1] + [new_block] + blocks[i + 1 :]

    # If focused block not found, add at the end
    return blocks + [new_block]


def add_heading_block(blocks):
    """Add a heading block."""
    new_block = {"id": str(uuid.uuid4()), "type": "heading", "content": "Heading"}
    return blocks + [new_block]


def add_text_block(blocks, focused_block_id=None):
    """Add a text block."""
    new_block = {
        "id": str(uuid.uuid4()),
        "type": "text",
        "heading": "",
        "content": "",
        "resources": [],
        "collapsed": True,  # Start collapsed
        "indent_level": 0,
    }

    # If no focused block or focused block not found, add at the end
    if not focused_block_id:
        return blocks + [new_block]

    # Find the focused block and insert after it
    for i, block in enumerate(blocks):
        if block["id"] == focused_block_id:
            # Inherit the indent level from the focused block
            new_block["indent_level"] = block.get("indent_level", 0)
            # Insert after the focused block
            return blocks[: i + 1] + [new_block] + blocks[i + 1 :]

    # If focused block not found, add at the end
    return blocks + [new_block]


def delete_block(blocks, block_id, title, description, resources):
    """Delete a block by its ID and regenerate outline."""
    blocks = [block for block in blocks if block["id"] != block_id]

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_block_content(blocks, block_id, content, title, description, resources):
    """Update the content of a specific block and regenerate outline."""
    for block in blocks:
        if block["id"] == block_id:
            block["content"] = content
            # Also save to type-specific field
            if block["type"] == "ai":
                block["ai_content"] = content
            elif block["type"] == "text":
                block["text_content"] = content
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_block_heading(blocks, block_id, heading, title, description, resources):
    """Update the heading of a specific block and regenerate outline."""
    for block in blocks:
        if block["id"] == block_id:
            block["heading"] = heading
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def set_focused_block(block_id):
    """Set the currently focused block."""
    return block_id


def convert_block_type(blocks, block_id, to_type, title, description, resources):
    """Convert a block from one type to another while preserving separate content for each type."""
    for block in blocks:
        if block["id"] == block_id:
            current_type = block["type"]

            # Save current content to type-specific field
            if current_type == "ai":
                block["ai_content"] = block.get("content", "")
                block["ai_resources"] = block.get("resources", [])
            elif current_type == "text":
                block["text_content"] = block.get("content", "")
                block["text_resources"] = block.get("resources", [])

            # Switch to new type
            block["type"] = to_type

            # Load content for the new type
            if to_type == "ai":
                block["content"] = block.get("ai_content", "")
                block["resources"] = block.get("ai_resources", [])
            elif to_type == "text":
                block["content"] = block.get("text_content", "")
                block["resources"] = block.get("text_resources", [])

            # Ensure all required fields exist
            if "heading" not in block:
                block["heading"] = ""
            if "collapsed" not in block:
                block["collapsed"] = False
            if "indent_level" not in block:
                block["indent_level"] = 0
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def toggle_block_collapse(blocks, block_id):
    """Toggle the collapsed state of a specific block."""
    for block in blocks:
        if block["id"] == block_id:
            # Simply toggle the collapsed state
            block["collapsed"] = not block.get("collapsed", False)
            break
    return blocks


def update_block_indent(blocks, block_id, direction, title, description, resources):
    """Update the indent level of a specific block and regenerate outline."""
    # Find the index of the block being modified
    block_index = None
    for i, block in enumerate(blocks):
        if block["id"] == block_id:
            block_index = i
            break

    if block_index is None:
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
        return blocks, outline, json_str

    block = blocks[block_index]
    current_level = block.get("indent_level", 0)

    if direction == "in":
        # Check if this is the first block - if so, can't indent at all
        if block_index == 0:
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Get the previous block's indent level
        prev_block = blocks[block_index - 1]
        prev_level = prev_block.get("indent_level", 0)
        max_allowed_level = prev_level + 1

        # Can only indent if current level is less than max allowed and less than 5
        if current_level < max_allowed_level and current_level < 5:
            block["indent_level"] = current_level + 1
    elif direction == "out" and current_level > 0:
        block["indent_level"] = current_level - 1

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


async def handle_document_generation(title, description, resources, blocks):
    """Generate document using the recipe executor."""
    try:
        # First generate the JSON
        json_str = generate_document_json(title, description, resources, blocks)
        json_data = json.loads(json_str)

        # Convert to Outline
        outline = json_to_outline(json_data)

        # Generate the document
        generated_content = await generate_document(outline)

        # Save to temporary file for download
        filename = f"{title}.md" if title else "document.md"
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w") as f:
            f.write(generated_content)

        return json_str, generated_content, gr.update(visible=True, value=file_path, label=f"Download {filename}")

    except Exception as e:
        error_msg = f"Error generating document: {str(e)}"
        return json_str, error_msg, gr.update(visible=False)


def generate_document_json(title, description, resources, blocks):
    """Generate JSON structure from document data following the example format."""
    import json

    # Create the base structure
    doc_json = {"title": title, "general_instruction": description, "resources": [], "sections": []}

    # Process resources
    for idx, resource in enumerate(resources):
        doc_json["resources"].append({
            "key": f"resource_{idx + 1}",
            "path": resource["path"],
            "description": f"Uploaded {resource['type']}: {resource['name']}",
        })

    # Helper function to build nested sections based on indentation
    def build_nested_sections(blocks, start_idx=0, parent_level=-1):
        sections = []
        i = start_idx

        while i < len(blocks):
            block = blocks[i]
            current_level = block.get("indent_level", 0)

            # If this block is at a lower level than parent, return
            if current_level <= parent_level:
                break

            # If this block is at the expected level
            if current_level == parent_level + 1:
                if block["type"] in ["ai", "text"] and (block.get("heading") or block.get("content")):
                    section = {"title": block.get("heading", "Untitled Section")}

                    # Handle AI blocks vs Text blocks differently
                    if block["type"] == "ai":
                        # AI blocks have prompt and refs
                        section["prompt"] = block.get("content", "")

                        # Only add refs if this specific block has resources attached
                        block_resources = block.get("resources", [])
                        if block_resources:
                            # Find the resource keys for this block's resources
                            refs = []
                            for block_resource in block_resources:
                                # Find matching resource in the global resources list
                                for idx, resource in enumerate(resources):
                                    if resource["path"] == block_resource.get("path"):
                                        refs.append(f"resource_{idx + 1}")
                                        break
                            if refs:
                                section["refs"] = refs

                    else:  # block['type'] == 'text'
                        # Text blocks don't have prompt, and use resource_key instead of refs
                        block_resources = block.get("resources", [])
                        if block_resources:
                            # For text blocks, just use the first resource as resource_key
                            for block_resource in block_resources:
                                # Find matching resource in the global resources list
                                for idx, resource in enumerate(resources):
                                    if resource["path"] == block_resource.get("path"):
                                        section["resource_key"] = f"resource_{idx + 1}"
                                        break
                                break  # Only use first resource for resource_key

                    # Check if next blocks are indented under this one
                    next_idx = i + 1
                    if next_idx < len(blocks) and blocks[next_idx].get("indent_level", 0) > current_level:
                        # Build subsections
                        subsections, next_idx = build_nested_sections(blocks, next_idx, current_level)
                        if subsections:
                            section["sections"] = subsections
                        i = next_idx - 1  # Adjust because we'll increment at the end

                    sections.append(section)

            i += 1

        return sections, i

    # Build the sections hierarchy
    doc_json["sections"], _ = build_nested_sections(blocks, 0, -1)

    return json.dumps(doc_json, indent=2)


def regenerate_outline_from_state(title, description, resources, blocks):
    """Regenerate the outline whenever any component changes."""
    try:
        json_str = generate_document_json(title, description, resources, blocks)
        json_data = json.loads(json_str)
        outline = json_to_outline(json_data)
        return outline, json_str
    except Exception as e:
        # Return None outline and error message in JSON
        error_json = json.dumps({"error": str(e)}, indent=2)
        return None, error_json


def update_document_metadata(title, description, resources, blocks):
    """Update document title/description and regenerate outline."""
    # Just regenerate the outline with new metadata
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return outline, json_str


def render_blocks(blocks, focused_block_id=None):
    """Render blocks as HTML."""
    if not blocks:
        return "<div class='empty-blocks-message'>Click AI or T to add content blocks</div>"

    html = ""
    for i, block in enumerate(blocks):
        block_id = block["id"]
        is_collapsed = block.get("collapsed", False)
        collapsed_class = "collapsed" if is_collapsed else ""
        preview_class = "show" if is_collapsed else ""
        content_class = "" if is_collapsed else "show"

        if block["type"] == "ai":
            heading_value = block.get("heading", "")
            indent_level = block.get("indent_level", 0)

            # Determine max allowed indent level based on previous block
            max_allowed_indent = 0
            if i > 0:
                prev_block = blocks[i - 1]
                prev_indent = prev_block.get("indent_level", 0)
                max_allowed_indent = prev_indent + 1

            # Build indent controls - always include both buttons, just hide if not applicable
            indent_controls = '<div class="indent-controls">'
            # Show indent button only if we can indent further
            if indent_level < 5 and indent_level < max_allowed_indent:
                indent_controls += (
                    f"<button class=\"indent-btn indent\" onclick=\"updateBlockIndent('{block_id}', 'in')\">⇥</button>"
                )
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'

            if indent_level > 0:
                indent_controls += f"<button class=\"indent-btn outdent\" onclick=\"updateBlockIndent('{block_id}', 'out')\">⇤</button>"
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'
            indent_controls += "</div>"

            html += f"""
            <div class='content-block ai-block {collapsed_class}' data-id='{block_id}' data-indent='{indent_level}'>
                {indent_controls}
                <div class='block-header'>
                    <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                        <span class='collapse-icon'>{"›" if is_collapsed else "›"}</span>
                    </button>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                    <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                    <button class='convert-btn convert-to-text {"" if is_collapsed else "show"}' onclick='convertBlock("{block_id}", "text")'>T</button>
                </div>
                <div class='block-content {content_class}'>
                    <textarea placeholder='Enter your AI instruction here...'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        Drop AI resources here
                    </div>
                </div>
            </div>
            """
        elif block["type"] == "heading":
            html += f"""
            <div class='content-block heading-block' data-id='{block_id}'>
                <div class='block-header heading-header'>
                    <input type='text' value='{block["content"]}'
                           oninput='updateBlockContent("{block_id}", this.value)'/>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                    <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                </div>
            </div>
            """
        elif block["type"] == "text":
            heading_value = block.get("heading", "")
            indent_level = block.get("indent_level", 0)

            # Determine max allowed indent level based on previous block
            max_allowed_indent = 0
            if i > 0:
                prev_block = blocks[i - 1]
                prev_indent = prev_block.get("indent_level", 0)
                max_allowed_indent = prev_indent + 1

            # Build indent controls - always include both buttons, just hide if not applicable
            indent_controls = '<div class="indent-controls">'
            # Show indent button only if we can indent further
            if indent_level < 5 and indent_level < max_allowed_indent:
                indent_controls += (
                    f"<button class=\"indent-btn indent\" onclick=\"updateBlockIndent('{block_id}', 'in')\">⇥</button>"
                )
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'

            if indent_level > 0:
                indent_controls += f"<button class=\"indent-btn outdent\" onclick=\"updateBlockIndent('{block_id}', 'out')\">⇤</button>"
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'
            indent_controls += "</div>"

            html += f"""
            <div class='content-block text-block {collapsed_class}' data-id='{block_id}' data-indent='{indent_level}'>
                {indent_controls}
                <div class='block-header'>
                    <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                        <span class='collapse-icon'>{"›" if is_collapsed else "›"}</span>
                    </button>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                    <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                    <button class='convert-btn convert-to-ai {"" if is_collapsed else "show"}' onclick='convertBlock("{block_id}", "ai")'>AI</button>
                </div>
                <div class='block-content {content_class}'>
                    <textarea placeholder='Enter your text here...'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        Drop text resources here
                    </div>
                </div>
            </div>
            """

    return html


def handle_file_upload(files, current_resources, title, description, blocks):
    """Handle uploaded files and return HTML display of file names."""
    if not files:
        return current_resources, gr.update(), None, gr.update(), gr.update()

    # Add new files to resources
    new_resources = current_resources.copy() if current_resources else []

    for file_path in files:
        if file_path and file_path not in [r["path"] for r in new_resources]:
            import os

            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()

            # Determine if it's an image
            is_image = file_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]

            new_resources.append({"path": file_path, "name": file_name, "type": "image" if is_image else "file"})

    # Generate HTML for resources display
    if new_resources:
        html_items = []
        for resource in new_resources:
            icon = "🖼️" if resource["type"] == "image" else "📄"
            css_class = f"resource-item {resource['type']}"
            html_items.append(
                f'<div class="{css_class}" draggable="true" data-resource-name="{resource["name"]}" data-resource-type="{resource["type"]}" data-resource-path="{resource["path"]}">{icon} {resource["name"]}</div>'
            )
        resources_html = "\n".join(html_items)
    else:
        resources_html = "<p style='color: #666; font-size: 12px;'>No resources uploaded yet</p>"

    # Regenerate outline with new resources
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, blocks)

    return new_resources, gr.update(value=resources_html), None, outline, json_str  # Return None to clear file upload


def create_app():
    """Create and return the Document Builder Gradio app."""

    # Load custom CSS
    css_path = Path(__file__).parent / "static" / "css" / "styles.css"
    with open(css_path, "r") as f:
        custom_css = f.read()

    # Load custom JavaScript
    js_path = Path(__file__).parent / "static" / "js" / "script.js"
    with open(js_path, "r") as f:
        js_content = f.read()

    # Wrap JS in script tags for head injection
    custom_js = f"<script>{js_content}</script>"

    with gr.Blocks(css=custom_css, head=custom_js) as app:
        # State to track resources and blocks
        resources_state = gr.State([])
        focused_block_state = gr.State(None)

        # Initialize with default blocks
        initial_blocks = [
            {
                "id": str(uuid.uuid4()),
                "type": "ai",
                "heading": "",
                "content": "",
                "resources": [],
                "collapsed": False,  # AI block starts expanded
                "indent_level": 0,
            },
            {
                "id": str(uuid.uuid4()),
                "type": "text",
                "heading": "",
                "content": "",
                "resources": [],
                "collapsed": True,  # Text block starts collapsed
                "indent_level": 0,
            },
        ]
        blocks_state = gr.State(initial_blocks)

        # Initialize outline state with empty values
        initial_outline, initial_json = regenerate_outline_from_state("Document Title", "", [], initial_blocks)
        outline_state = gr.State(initial_outline)

        with gr.Row():
            # App name and explanation
            with gr.Column():
                gr.Markdown("# Document Builder")
                gr.Markdown(
                    "A tool for creating structured documents with customizable sections, "
                    "templates, and formatting options. Build professional documents "
                    "efficiently with an intuitive interface."
                )

            # Import and Save buttons
            with gr.Column():
                with gr.Row():
                    # Add empty space to push buttons to the right
                    gr.HTML("<div style='flex: 1;'></div>")
                    import_builder_btn = gr.Button(
                        "Import",
                        elem_id="import-builder-btn-id",
                        variant="secondary",
                        size="sm",
                        elem_classes="import-builder-btn",
                    )
                    save_builder_btn = gr.Button(
                        "Save",
                        elem_id="save-builder-btn-id",
                        variant="primary",
                        size="sm",
                        elem_classes="save-builder-btn",
                    )

        # Document title and description
        with gr.Row(elem_classes="header-section"):
            # Document title (25% width)
            doc_title = gr.Textbox(
                value="Document Title",
                placeholder="Enter document title",
                label=None,
                show_label=False,
                elem_id="doc-title-id",
                elem_classes="doc-title-box",
                scale=1,
                interactive=True,
            )

            # Document description (75% width)
            doc_description = gr.Textbox(
                value="",
                placeholder="Explain what this document is about. Include specifics such as purpose, audience, style, format, etc.",
                label=None,
                show_label=False,
                elem_id="doc-description-id",
                scale=3,
                interactive=True,
            )

        # Main content area with three columns
        with gr.Row():
            # Resources column: Upload Resources button
            with gr.Column(scale=1, elem_classes="resources-col"):
                # File upload component styled as button
                upload_resources_btn = gr.Button(
                    "Upload Resources",
                    variant="secondary",
                    size="sm",
                    elem_id="upload-resources-btn-id",
                    elem_classes="upload-resources-btn",
                )

                file_upload = gr.File(
                    label="Upload Resources",
                    file_count="multiple",
                    file_types=["image", ".pdf", ".txt", ".md", ".doc", ".docx"],
                    elem_classes="upload-file-invisible-btn",
                    visible=False,
                )

                resources_display = gr.HTML(
                    value="<p style='color: #666; font-size: 12px'>No resources uploaded yet</p>",
                    elem_classes="resources-display-area",
                )

            # Workspace column: AI, H, T buttons (aligned left)
            with gr.Column(scale=1, elem_classes="workspace-col"):
                with gr.Row(elem_classes="square-btn-row"):
                    ai_btn = gr.Button("+ Add Section", elem_classes="add-section-btn", size="sm")

                # Workspace panel for stacking content blocks
                with gr.Column(elem_classes="workspace-display"):
                    blocks_display = gr.HTML(value=render_blocks(initial_blocks, None), elem_classes="blocks-container")

                    # Hidden components for JS communication
                    delete_block_id = gr.Textbox(visible=False, elem_id="delete-block-id")
                    delete_trigger = gr.Button("Delete", visible=False, elem_id="delete-trigger")

                    # Hidden components for content updates
                    update_block_id = gr.Textbox(visible=False, elem_id="update-block-id")
                    update_content_input = gr.Textbox(visible=False, elem_id="update-content-input")
                    update_trigger = gr.Button("Update", visible=False, elem_id="update-trigger")

                    # Hidden components for toggle collapse
                    toggle_block_id = gr.Textbox(visible=False, elem_id="toggle-block-id")
                    toggle_trigger = gr.Button("Toggle", visible=False, elem_id="toggle-trigger")

                    # Hidden components for heading updates
                    update_heading_block_id = gr.Textbox(visible=False, elem_id="update-heading-block-id")
                    update_heading_input = gr.Textbox(visible=False, elem_id="update-heading-input")
                    update_heading_trigger = gr.Button(
                        "Update Heading", visible=False, elem_id="update-heading-trigger"
                    )

                    # Hidden components for indent updates
                    indent_block_id = gr.Textbox(visible=False, elem_id="indent-block-id")
                    indent_direction = gr.Textbox(visible=False, elem_id="indent-direction")
                    indent_trigger = gr.Button("Update Indent", visible=False, elem_id="indent-trigger")

                    # Hidden components for focus tracking
                    focus_block_id = gr.Textbox(visible=False, elem_id="focus-block-id")
                    focus_trigger = gr.Button("Set Focus", visible=False, elem_id="focus-trigger")

                    # Hidden components for adding block after
                    add_after_block_id = gr.Textbox(visible=False, elem_id="add-after-block-id")
                    add_after_type = gr.Textbox(visible=False, elem_id="add-after-type")
                    add_after_trigger = gr.Button("Add After", visible=False, elem_id="add-after-trigger")

                    # Hidden components for converting block type
                    convert_block_id = gr.Textbox(visible=False, elem_id="convert-block-id")
                    convert_type = gr.Textbox(visible=False, elem_id="convert-type")
                    convert_trigger = gr.Button("Convert", visible=False, elem_id="convert-trigger")

            # Generated document column: Generate and Save Document buttons (aligned right)
            with gr.Column(scale=1, elem_classes="generate-col"):
                with gr.Row(elem_classes="generate-btn-row"):
                    # Add empty space to push buttons to the right
                    gr.HTML("<div style='flex: 1;'></div>")
                    generate_doc_btn = gr.Button(
                        "▷ Generate", elem_classes="generate-btn", variant="primary", size="sm"
                    )
                    save_doc_btn = gr.Button("Download", elem_classes="download-btn", variant="secondary", size="sm")

                # Generated document display panel
                with gr.Column(elem_classes="generate-display"):
                    generated_content = gr.Markdown(
                        value="*Click 'Generate Document' to see the generated content here*",
                        elem_classes="generated-content",
                    )

                    # Download button for generated document
                    download_btn = gr.DownloadButton(
                        "Download Document", visible=False, elem_classes="download-generated-doc"
                    )

                # Debug panel for JSON display
                with gr.Column(elem_classes="debug-panel"):
                    gr.Markdown("### Debug Panel (JSON Output)")
                    json_output = gr.Code(value=initial_json, language="json", elem_classes="json-debug-output")

        # Handle file uploads (defined after json_output is created)
        file_upload.change(
            handle_file_upload,
            inputs=[file_upload, resources_state, doc_title, doc_description, blocks_state],
            outputs=[resources_state, resources_display, file_upload, outline_state, json_output],
        )

        # Helper function to add AI block and regenerate outline
        def handle_add_ai_block_top(blocks, _, title, description, resources):
            blocks = add_ai_block(blocks, None)
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Connect button click to add block
        ai_btn.click(
            fn=handle_add_ai_block_top,
            inputs=[
                blocks_state,
                gr.State(None),
                doc_title,
                doc_description,
                resources_state,
            ],  # Always pass None for focused_block_id
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Delete block handler
        delete_trigger.click(
            fn=delete_block,
            inputs=[blocks_state, delete_block_id, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update block content handler
        update_trigger.click(
            fn=update_block_content,
            inputs=[blocks_state, update_block_id, update_content_input, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=set_focused_block, inputs=update_block_id, outputs=focused_block_state)

        # Toggle collapse handler
        toggle_trigger.click(
            fn=toggle_block_collapse, inputs=[blocks_state, toggle_block_id], outputs=blocks_state
        ).then(fn=set_focused_block, inputs=toggle_block_id, outputs=focused_block_state).then(
            fn=render_blocks, inputs=[blocks_state, toggle_block_id], outputs=blocks_display
        )

        # Update heading handler
        update_heading_trigger.click(
            fn=update_block_heading,
            inputs=[
                blocks_state,
                update_heading_block_id,
                update_heading_input,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=set_focused_block, inputs=update_heading_block_id, outputs=focused_block_state)

        # Update indent handler
        indent_trigger.click(
            fn=update_block_indent, 
            inputs=[blocks_state, indent_block_id, indent_direction, doc_title, doc_description, resources_state], 
            outputs=[blocks_state, outline_state, json_output]
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            fn=set_focused_block, inputs=indent_block_id, outputs=focused_block_state
        )

        # Focus handler
        focus_trigger.click(fn=set_focused_block, inputs=focus_block_id, outputs=focused_block_state).then(
            fn=render_blocks, inputs=[blocks_state, focus_block_id], outputs=blocks_display
        )

        # Add after handler - for + button on content blocks
        def handle_add_after(blocks, block_id, block_type, title, description, resources):
            if block_type == "ai":
                blocks = add_ai_block(blocks, block_id)
            else:
                blocks = add_text_block(blocks, block_id)

            # Regenerate outline and JSON
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        add_after_trigger.click(
            fn=handle_add_after,
            inputs=[blocks_state, add_after_block_id, add_after_type, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Convert block type handler
        convert_trigger.click(
            fn=convert_block_type,
            inputs=[blocks_state, convert_block_id, convert_type, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Title and description change handlers
        doc_title.change(
            fn=update_document_metadata,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[outline_state, json_output],
        )

        doc_description.change(
            fn=update_document_metadata,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[outline_state, json_output],
        )

        # Generate document handler
        generate_doc_btn.click(
            fn=handle_document_generation,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[json_output, generated_content, download_btn],
        )

    return app


def main():
    """Main entry point for the Document Builder app."""
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
