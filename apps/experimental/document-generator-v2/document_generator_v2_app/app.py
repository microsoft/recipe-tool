import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

import gradio as gr
from dotenv import load_dotenv

from docpack import DocpackHandler

from .executor.runner import generate_document
from .models.outline import Outline, Resource, Section
from .session import session_manager

# Load environment variables from .env file
load_dotenv()


def json_to_outline(json_data: Dict[str, Any]) -> Outline:
    """Convert JSON structure to Outline dataclasses."""
    # Create outline with basic metadata
    outline = Outline(title=json_data.get("title", ""), general_instruction=json_data.get("general_instruction", ""))

    # Convert resources
    for res_data in json_data.get("resources", []):
        # Handle backward compatibility - use filename as title if title not present
        title = res_data.get("title", "")
        if not title:
            # Extract filename from path as default title
            title = os.path.basename(res_data["path"])

        resource = Resource(
            key=res_data["key"],
            path=res_data["path"],
            title=title,
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
                # Mark text block as edited when content changes
                if content:
                    block["edited"] = True
                    # Store original resource reference if exists
                    if "resources" in block and block["resources"]:
                        block["original_resource"] = block["resources"][0]
                        block["resources"] = []  # Clear resources since content is now edited
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


def reset_document(session_id=None):
    """Reset the document to initial empty state."""
    # Create new session ID
    new_session_id = str(uuid.uuid4())

    # Reset to initial blocks
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

    # Generate initial outline
    outline, json_str = regenerate_outline_from_state("", "", [], initial_blocks)

    # Return empty title, description, empty resources, initial blocks
    return (
        gr.update(value=""),  # title - use gr.update to ensure proper clearing
        gr.update(value=""),  # description - use gr.update to ensure proper clearing
        [],  # resources
        initial_blocks,  # blocks
        outline,  # outline
        json_str,  # json_output
        None,  # import_file
        new_session_id,  # session_id
        gr.update(
            value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>", visible=True
        ),  # generated_content_html
        gr.update(visible=False),  # generated_content
        gr.update(interactive=False),  # save_doc_btn
    )


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


def save_inline_resources(blocks, output_dir):
    """Save inline resources from edited text blocks to disk."""
    saved_resources = []
    for block in blocks:
        if block.get("type") == "text" and block.get("edited") and block.get("text_content"):
            # Save the inline resource
            filename = f"inline_{block['id']}.txt"
            filepath = Path(output_dir) / filename
            filepath.write_text(block["text_content"], encoding="utf-8")
            saved_resources.append({"block_id": block["id"], "path": str(filepath)})
    return saved_resources


async def handle_document_generation(title, description, resources, blocks, session_id=None):
    """Generate document using the recipe executor."""
    json_str = ""  # Initialize json_str before the try block
    try:
        # Get or create session ID
        if not session_id:
            session_id = str(uuid.uuid4())

        # Use session temp directory for inline resources and output
        temp_dir = session_manager.get_temp_dir(session_id)

        # Generate the JSON with inline resources saved to temp directory
        json_str = generate_document_json(title, description, resources, blocks, save_inline=True, inline_dir=temp_dir)
        json_data = json.loads(json_str)

        # Remove is_inline flags for compatibility with json_to_outline
        for res in json_data.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Convert to Outline
        outline = json_to_outline(json_data)

        # Generate the document
        generated_content = await generate_document(outline, session_id)

        # Save to temporary file for download
        filename = f"{title}.md" if title else "document.md"
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w") as f:
            f.write(generated_content)

        return json_str, generated_content, file_path, filename

    except Exception as e:
        error_msg = f"Error generating document: {str(e)}"
        return json_str, error_msg, None, None


def generate_document_json(title, description, resources, blocks, save_inline=False, inline_dir=None):
    """Generate JSON structure from document data following the example format.

    Args:
        save_inline: If True, save inline resources to inline_dir and use real paths
        inline_dir: Directory to save inline resources to (required if save_inline=True)
    """
    import json

    # Create the base structure
    doc_json = {"title": title, "general_instruction": description, "resources": [], "sections": []}

    # Track inline resources that need to be added
    inline_resources = []

    # Process resources with their descriptions from the resources list
    for idx, resource in enumerate(resources):
        # Get description directly from the resource
        description = resource.get("description", "")
        # Get title from resource or default to filename
        title = resource.get("title", resource.get("name", os.path.basename(resource["path"])))
        doc_json["resources"].append({
            "key": f"resource_{idx + 1}",
            "path": resource["path"],
            "title": title,
            "description": description,
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
                if block["type"] in ["ai", "text"] and (
                    block.get("heading") or block.get("content") or block.get("resources")
                ):
                    section = {"title": block.get("heading", "Untitled Section")}

                    # Handle AI blocks vs Text blocks differently
                    if block["type"] == "ai":
                        # AI blocks always have these keys
                        section["prompt"] = block.get("content", "")
                        section["sections"] = []  # Will be populated if there are nested sections

                        # Handle refs - always include the key
                        refs = []
                        block_resources = block.get("resources", [])
                        if block_resources:
                            # Find the resource keys for this block's resources
                            for block_resource in block_resources:
                                # Find matching resource in the global resources list
                                for idx, resource in enumerate(resources):
                                    if resource["path"] == block_resource.get("path"):
                                        refs.append(f"resource_{idx + 1}")
                                        break
                        section["refs"] = refs

                    else:  # block['type'] == 'text'
                        # Text blocks always have these keys
                        section["resource_key"] = ""  # Default to empty string
                        section["sections"] = []  # Will be populated if there are nested sections

                        # Check if this text block has been edited
                        if block.get("edited") and block.get("text_content"):
                            # Create an inline resource for the edited content
                            inline_resource_key = f"inline_resource_{len(inline_resources) + 1}"
                            inline_resources.append({
                                "key": inline_resource_key,
                                "content": block["text_content"],
                                "block_id": block["id"],
                            })
                            section["resource_key"] = inline_resource_key
                        else:
                            # Handle regular file resource
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

    # Add inline resources to the resources list
    if save_inline and inline_dir:
        # Actually save the inline resources and use real paths
        for inline_res in inline_resources:
            filename = f"inline_{inline_res['block_id']}.txt"
            filepath = Path(inline_dir) / filename
            filepath.write_text(inline_res["content"], encoding="utf-8")

            doc_json["resources"].append({
                "key": inline_res["key"],
                "path": str(filepath),
                "title": filename,  # Use filename as title for inline resources
                "description": "",  # No description for inline resources
                "is_inline": True,  # Mark as inline resource
            })
    else:
        # For preview, save to temp gradio directory immediately
        import tempfile

        gradio_temp_dir = Path(tempfile.gettempdir()) / "gradio"
        gradio_temp_dir.mkdir(exist_ok=True)

        for inline_res in inline_resources:
            # Generate unique filename with timestamp
            import time

            timestamp = str(int(time.time() * 1000000))
            filename = f"inline_{inline_res['block_id']}_{timestamp}.txt"
            filepath = gradio_temp_dir / filename
            filepath.write_text(inline_res["content"], encoding="utf-8")

            doc_json["resources"].append({
                "key": inline_res["key"],
                "path": str(filepath),
                "title": filename,  # Use filename as title for inline resources
                "description": "",  # No description for inline resources
                "is_inline": True,  # Mark as inline resource
            })

    return json.dumps(doc_json, indent=2)


def regenerate_outline_from_state(title, description, resources, blocks):
    """Regenerate the outline whenever any component changes."""
    try:
        json_str = generate_document_json(title, description, resources, blocks)
        json_data = json.loads(json_str)
        outline = json_to_outline(json_data)

        # Update global state whenever outline is regenerated
        global current_document_state
        current_document_state = {"title": title, "outline_json": json_str, "blocks": blocks}
        print(f"Regenerated outline from state: {current_document_state}")

        return outline, json_str
    except Exception as e:
        # Return None outline and error message in JSON
        import traceback

        print(f"ERROR in regenerate_outline_from_state: {str(e)}")
        print(traceback.format_exc())
        error_json = json.dumps({"error": str(e), "traceback": traceback.format_exc()}, indent=2)
        return None, error_json


def update_document_metadata(title, description, resources, blocks):
    """Update document title/description and regenerate outline."""
    # Just regenerate the outline with new metadata
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return outline, json_str


def update_block_resources(blocks, block_id, resource_json, title, description, resources):
    """Update a block's resources when a resource is dropped on it."""
    import json

    # Parse the resource data
    resource_data = json.loads(resource_json)

    # Find the block and update its resources
    for block in blocks:
        if block["id"] == block_id:
            if "resources" not in block:
                block["resources"] = []

            # For text blocks, only allow one resource AND auto-load content
            if block["type"] == "text":
                # Replace any existing resource
                block["resources"] = [resource_data]

                # Auto-load the file content into the text block
                try:
                    with open(resource_data["path"], "r", encoding="utf-8") as f:
                        block["content"] = f.read()
                except Exception as e:
                    print(f"Error loading file content: {e}")
                    # Keep existing content if file can't be read
            else:
                # For AI blocks, allow multiple resources
                # Check if resource already exists in the block
                exists = False
                for res in block["resources"]:
                    if res.get("path") == resource_data.get("path"):
                        exists = True
                        break

                # Add resource if it doesn't exist
                if not exists:
                    # Check if this resource already has a description in another block
                    existing_description = ""
                    for other_block in blocks:
                        if other_block.get("type") == "ai" and "resources" in other_block:
                            for res in other_block["resources"]:
                                if res.get("path") == resource_data.get("path") and res.get("description"):
                                    existing_description = res.get("description", "")
                                    break
                            if existing_description:
                                break

                    # Add the resource with existing description if found
                    resource_to_add = resource_data.copy()
                    if existing_description:
                        resource_to_add["description"] = existing_description

                    block["resources"].append(resource_to_add)
            break

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def remove_block_resource(blocks, block_id, resource_path, title, description, resources):
    """Remove a resource from a block."""
    # Find the block and remove the resource
    for block in blocks:
        if block["id"] == block_id:
            if "resources" in block:
                # Remove the resource with matching path
                block["resources"] = [res for res in block["resources"] if res.get("path") != resource_path]

                # If this is a text block and we just removed its resource, clear the content
                if block["type"] == "text" and len(block["resources"]) == 0:
                    block["content"] = ""
            break

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_resource_description(blocks, block_id, resource_path, description_text, title, doc_description, resources):
    """Update the description of a resource globally - affects all blocks using this resource."""
    # Update the description in ALL blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["description"] = description_text

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, doc_description, resources, blocks)
    return blocks, outline, json_str


def generate_resource_html(resources):
    """Generate HTML for resource panel display."""
    if not resources:
        return (
            "<p style='color: #666; font-size: 12px'>(.md, .csv, .py, .json, .txt, etc.)</p>"
            "<p style='color: #666; font-size: 12px'>These reference files will be used for AI context.</p>"
        )

    html_items = []
    for idx, resource in enumerate(resources):
        css_class = "resource-item text"
        path = resource["path"].replace("'", "\\'")  # Escape single quotes
        title = resource.get("title", resource["name"])
        description = resource.get("description", "")
        resource_id = f"resource-{idx}"  # Unique ID for each resource

        html_items.append(
            f'<div class="{css_class}" id="{resource_id}" draggable="true" data-resource-name="{resource["name"]}" '
            f'data-resource-title="{title}" data-resource-type="text" data-resource-path="{resource["path"]}">'
            f'<div class="resource-content">'
            f'<div class="resource-header">'
            f'<input type="text" class="resource-title-input" value="{title}" '
            f'placeholder="Title" '
            f"oninput=\"updateResourceTitle('{path}', this.value)\" "
            f'onclick="event.stopPropagation()" />'
            f'<span class="resource-delete" onclick="deleteResourceFromPanel(\'{path}\')">🗑</span>'
            f"</div>"
            f'<div class="resource-description-container">'
            f'<textarea class="resource-panel-description" '
            f'placeholder="Add a description for this resource..." '
            f"oninput=\"updateResourcePanelDescription('{path}', this.value)\" "
            f'onclick="event.stopPropagation()">{description}</textarea>'
            f'<button class="desc-expand-btn" onclick="toggleResourceDescription(\'{resource_id}\')">⌵</button>'
            f"</div>"
            f'<div class="resource-filename">{resource["name"]}</div>'
            f'<div class="resource-upload-zone" data-resource-path="{path}">'
            f'<span class="upload-text">Drop file here to replace</span>'
            f'<input type="file" class="resource-file-input" accept=".txt,.md,.py,.c,.cpp,.h,.java,.js,.ts,.jsx,.tsx,.json,.xml,.yaml,.yml,.toml,.ini,.cfg,.conf,.sh,.bash,.zsh,.fish,.ps1,.bat,.cmd,.rs,.go,.rb,.php,.pl,.lua,.r,.m,.swift,.kt,.scala,.clj,.ex,.exs,.elm,.fs,.ml,.sql,.html,.htm,.css,.scss,.sass,.less,.vue,.svelte,.astro,.tex,.rst,.adoc,.org,.csv" '
            f"onchange=\"handleResourceFileUpload('{path}', this)\" />"
            f"</div>"
            f"</div>"
            f"</div>"
        )

    return "\n".join(html_items)


def delete_resource_from_panel(resources, resource_path, title, description, blocks):
    """Delete a resource from the resource panel and all blocks that use it."""
    print(f"Deleting resource from panel: {resource_path}")

    # Remove from resources list
    new_resources = [res for res in resources if res.get("path") != resource_path]

    # Create new blocks list to ensure state updates
    updated_blocks = []
    for block in blocks:
        block_copy = block.copy()
        if "resources" in block_copy:
            # Count resources before removal
            original_count = len(block_copy["resources"])

            # Remove the resource
            block_copy["resources"] = [res for res in block_copy["resources"] if res.get("path") != resource_path]

            if original_count != len(block_copy["resources"]):
                print(
                    f"Removed resource from block {block_copy['id']}: {original_count} -> {len(block_copy['resources'])}"
                )

            # If this was a text block and we removed its only resource, clear the content
            if block_copy["type"] == "text" and original_count > 0 and len(block_copy["resources"]) == 0:
                block_copy["content"] = ""

        updated_blocks.append(block_copy)

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, updated_blocks)

    # Return the values expected by the handler (4 outputs)
    return new_resources, updated_blocks, outline, json_str


def update_resource_title(resources, resource_path, new_title, doc_title, doc_description, blocks):
    """Update the title of a resource."""
    # Update the title in the resources list
    for resource in resources:
        if resource.get("path") == resource_path:
            resource["title"] = new_title
            break

    # Regenerate outline with updated resources (for JSON display)
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    return resources, outline, json_str


def update_resource_panel_description(resources, resource_path, new_description, doc_title, doc_description, blocks):
    """Update the description of a resource from the panel."""
    # Update the description in the resources list
    for resource in resources:
        if resource.get("path") == resource_path:
            resource["description"] = new_description
            break

    # Regenerate outline with updated resources (for JSON display)
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    return resources, outline, json_str


def replace_resource_file(
    resources, old_resource_path, new_file_path, doc_title, doc_description, blocks, session_id=None
):
    """Replace a resource file with a new one while keeping the same resource key."""
    import shutil

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Get session files directory
    files_dir = session_manager.get_files_dir(session_id)

    # Copy new file to session directory
    new_file_name = os.path.basename(new_file_path)
    session_file_path = files_dir / new_file_name
    shutil.copy2(new_file_path, session_file_path)

    # Update the resource and all blocks that use it
    for resource in resources:
        if resource.get("path") == old_resource_path:
            # Keep the same key and description, just update the path and name
            resource["path"] = str(session_file_path)
            resource["name"] = new_file_name
            # Keep the existing title - don't update it
            break

    # Update all blocks that reference this resource
    for block in blocks:
        if "resources" in block:
            for block_resource in block["resources"]:
                if block_resource.get("path") == old_resource_path:
                    block_resource["path"] = str(session_file_path)
                    block_resource["name"] = new_file_name
                    # Keep the existing title - don't update it

    # Generate HTML for resources display
    resources_html = generate_resource_html(resources)

    # Regenerate outline with updated resources
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    # Return updated values including a success flag
    return resources, blocks, gr.update(value=resources_html), outline, json_str, "Resource replaced successfully!"


def load_example(example_id, session_id=None):
    """Load a predefined example based on the example ID."""
    if not example_id:
        return (
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            session_id,
            gr.update(),
            gr.update(),
            gr.update(),
        )

    # Map example IDs to file paths - now using .docpack files
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = {
        "1": examples_dir / "readme-generation" / "readme.docpack",
        "2": examples_dir / "launch-documentation" / "launch-documentation.docpack",
        "3": examples_dir
        / "scenario-4-annual-performance-review"
        / "Annual Employee Performance Review_20250709_153352.docpack",
    }

    file_path = example_files.get(example_id)
    if not file_path or not file_path.exists():
        # If docpack doesn't exist, show error message
        error_msg = f"Example file not found: {file_path.name if file_path else 'Unknown'}"
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            json.dumps({"error": error_msg}, indent=2),  # json_output
            session_id,  # session_id
        )

    # Use the import_outline function to load the example
    result = import_outline(str(file_path), session_id)
    # import_outline now returns 11 values matching import_file.change outputs
    # import_outline returns: title, desc, resources, blocks, outline, json, import_file, session_id, gen_html, gen_content, save_btn
    # load_example needs: title, desc, resources, blocks, outline, json, session_id, gen_html, gen_content, save_btn
    # We need to skip import_file (at index 6) from the result
    return (
        result[0],  # title
        result[1],  # description
        result[2],  # resources
        result[3],  # blocks
        result[4],  # outline
        result[5],  # json_str
        result[7],  # session_id (skip import_file at 6)
        result[8],  # generated_content_html
        result[9],  # generated_content
        result[10],  # save_doc_btn
    )


def import_outline(file_path, session_id=None):
    """Import an outline from a .docpack file and convert to blocks format."""
    if not file_path:
        # Return 11 values matching import_file.change outputs
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            gr.update(),  # json_output
            None,  # import_file
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
        )

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Define allowed text file extensions
    ALLOWED_EXTENSIONS = {
        ".txt",
        ".md",
        ".py",
        ".c",
        ".cpp",
        ".h",
        ".java",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".bat",
        ".cmd",
        ".rs",
        ".go",
        ".rb",
        ".php",
        ".pl",
        ".lua",
        ".r",
        ".m",
        ".swift",
        ".kt",
        ".scala",
        ".clj",
        ".ex",
        ".exs",
        ".elm",
        ".fs",
        ".ml",
        ".sql",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".vue",
        ".svelte",
        ".astro",
        ".tex",
        ".rst",
        ".adoc",
        ".org",
        ".csv",
    }

    try:
        file_path = Path(file_path)

        # Only accept .docpack files
        if file_path.suffix.lower() != ".docpack":
            error_msg = "Import failed: Only .docpack files are supported. Please use a .docpack file created by the Save function."
            return (
                gr.update(),  # title
                gr.update(),  # description
                gr.update(),  # resources
                gr.update(),  # blocks
                gr.update(),  # outline
                json.dumps({"error": error_msg}, indent=2),  # json_output
                None,  # import_file
                session_id,  # session_id
                gr.update(),  # generated_content_html
                gr.update(),  # generated_content
                gr.update(),  # save_doc_btn
            )

        # Use session directory for extraction
        session_dir = session_manager.get_session_dir(session_id)

        # Extract the docpack to session directory
        json_data, extracted_files = DocpackHandler.extract_package(file_path, session_dir)

        # Extract title and description
        title = json_data.get("title", "")
        description = json_data.get("general_instruction", "")

        # Extract and validate resources
        resources = []
        invalid_resources = []
        inline_resources = {}  # Store inline resources by key

        for res_data in json_data.get("resources", []):
            resource_path = res_data.get("path", "")
            resource_name = Path(resource_path).name
            file_ext = Path(resource_name).suffix.lower()

            # Check if this is an inline resource
            if res_data.get("is_inline", False) or res_data.get("key", "").startswith("inline_resource_"):
                # Store inline resource content for later use
                inline_resources[res_data["key"]] = resource_path
                continue  # Don't add to regular resources

            # Check if file extension is allowed
            if file_ext not in ALLOWED_EXTENSIONS:
                invalid_resources.append(f"{resource_name} ({file_ext})")
                continue

            resources.append({
                "key": res_data.get("key", ""),  # Preserve original key
                "path": resource_path,
                "name": resource_name,
                "title": res_data.get("title", resource_name),  # Preserve title or default to filename
                "type": "text",  # All are text files now
                "description": res_data.get("description", ""),
            })

        # If there are invalid resources, show error and return
        if invalid_resources:
            error_msg = "Import failed: The following resources have unsupported file types:\n" + "\n".join(
                invalid_resources
            )
            error_msg += f"\n\nOnly text files are allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            # Return error in the JSON output field
            return (
                gr.update(),  # title
                gr.update(),  # description
                gr.update(),  # resources
                gr.update(),  # blocks
                gr.update(),  # outline
                json.dumps({"error": error_msg}, indent=2),  # json_output
                None,  # import_file
                session_id,  # session_id
                gr.update(),  # generated_content_html
                gr.update(),  # generated_content
                gr.update(),  # save_doc_btn
            )

        # Convert sections to blocks
        blocks = []

        def sections_to_blocks(sections, parent_indent=-1):
            """Recursively convert sections to blocks."""
            for section in sections:
                # Create a block from the section
                block = {
                    "id": str(uuid.uuid4()),
                    "heading": section.get("title", ""),
                    "content": "",
                    "resources": [],
                    "collapsed": True,
                    "indent_level": parent_indent + 1,
                }

                # Determine block type and content
                if "prompt" in section:
                    # AI block
                    block["type"] = "ai"
                    block["content"] = section.get("prompt", "")
                    block["ai_content"] = section.get("prompt", "")

                    # Handle refs
                    refs = section.get("refs", [])
                    if refs and resources:
                        # Map refs back to resources by matching keys
                        for ref in refs:
                            # Find resource with matching key
                            for resource in resources:
                                if resource.get("key") == ref:
                                    block["resources"].append(resource)
                                    break

                elif "resource_key" in section:
                    # Text block
                    block["type"] = "text"
                    block["text_content"] = ""

                    # Handle resource_key
                    resource_key = section.get("resource_key", "")

                    # Check if this is an inline resource
                    if resource_key in inline_resources:
                        # Load content from inline resource file
                        try:
                            inline_path = inline_resources[resource_key]
                            # If it's a relative path in a save directory, construct full path
                            if not Path(inline_path).is_absolute():
                                # Look for the file in the same directory as the imported JSON
                                import_dir = Path(file_path).parent
                                inline_path = import_dir / inline_path

                            with open(inline_path, "r", encoding="utf-8") as f:
                                block["content"] = f.read()
                                block["text_content"] = block["content"]
                                block["edited"] = True  # Mark as edited
                        except Exception as e:
                            print(f"Error loading inline resource: {e}")
                    elif resource_key and resources:
                        # Regular resource reference - find by key
                        for resource in resources:
                            if resource.get("key") == resource_key:
                                block["resources"].append(resource)
                                # Auto-load content from the resource file
                                try:
                                    with open(resource["path"], "r", encoding="utf-8") as f:
                                        block["content"] = f.read()
                                        block["text_content"] = block["content"]
                                except Exception as e:
                                    print(f"Error loading resource content: {e}")
                                break
                else:
                    # Default to AI block if no specific type indicators
                    block["type"] = "ai"

                blocks.append(block)

                # Process nested sections
                if "sections" in section:
                    sections_to_blocks(section["sections"], block["indent_level"])

        # Convert top-level sections
        sections_to_blocks(json_data.get("sections", []))

        # If no blocks were created, add default ones
        if not blocks:
            blocks = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "ai",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": False,
                    "indent_level": 0,
                }
            ]
        else:
            # Ensure the first block is expanded
            if blocks and len(blocks) > 0:
                blocks[0]["collapsed"] = False

        # Regenerate outline and JSON
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)

        # Generate resources HTML using the proper function
        generate_resource_html(resources)

        # Return values matching what import_file.change expects
        return (
            title,
            description,
            resources,
            blocks,
            outline,
            json_str,
            None,  # import_file (clear it)
            session_id,
            gr.update(
                value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>", visible=True
            ),  # generated_content_html
            gr.update(visible=False),  # generated_content
            gr.update(interactive=False),  # save_doc_btn
        )

    except Exception as e:
        error_msg = f"Error importing file: {str(e)}"
        print(error_msg)
        # Return current values on error matching expected outputs
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            gr.update(),  # json_output
            None,  # import_file
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
        )


def save_outline(title, outline_json, blocks):
    """Create a .docpack file with all resources bundled and return for download."""
    from datetime import datetime

    try:
        # Create filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
        docpack_name = f"{safe_title}_{timestamp}.docpack"

        # Create a temporary file for the docpack
        temp_dir = Path(tempfile.gettempdir())
        docpack_path = temp_dir / docpack_name

        # Parse the current JSON
        current_json = json.loads(outline_json)

        # Collect all resource files and create key mapping
        resource_files = []
        resource_key_map = {}

        for res in current_json.get("resources", []):
            resource_path = Path(res["path"])
            if resource_path.exists():
                resource_files.append(resource_path)
                resource_key_map[str(resource_path.resolve())] = res["key"]

        # Remove is_inline flags before saving
        for res in current_json.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Create the docpack with conflict-safe naming
        DocpackHandler.create_package(
            outline_data=current_json,
            resource_files=resource_files,
            output_path=docpack_path,
            resource_key_map=resource_key_map,
        )

        # Return the file path for download
        return gr.update(value=str(docpack_path), visible=True, interactive=True)

    except Exception as e:
        error_msg = f"Error creating docpack: {str(e)}"
        print(error_msg)
        return gr.update(value=None, visible=False)


def create_docpack_from_current_state():
    """Create a docpack using the current global document state."""
    import time
    from datetime import datetime

    global current_document_state

    print(f"=== CREATING DOCPACK at {datetime.now().isoformat()} ===")
    print(f"Title: {current_document_state.get('title', 'N/A') if current_document_state else 'No state'}")
    print(f"Has outline_json: {'outline_json' in current_document_state if current_document_state else False}")
    print(f"Number of blocks: {len(current_document_state.get('blocks', [])) if current_document_state else 0}")

    if not current_document_state:
        return None

    try:
        title = current_document_state.get("title", "Document")
        outline_json = current_document_state.get("outline_json", "{}")

        # Create filename from title and timestamp with milliseconds to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        milliseconds = int(time.time() * 1000) % 1000
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
        docpack_name = f"{safe_title}_{timestamp}_{milliseconds}.docpack"

        # Create a temporary file for the docpack
        temp_dir = Path(tempfile.gettempdir())
        docpack_path = temp_dir / docpack_name

        # Parse the current JSON
        current_json = json.loads(outline_json)

        # Collect all resource files and create key mapping
        resource_files = []
        resource_key_map = {}

        for res in current_json.get("resources", []):
            resource_path = Path(res["path"])
            if resource_path.exists():
                resource_files.append(resource_path)
                resource_key_map[str(resource_path.resolve())] = res["key"]

        # Remove is_inline flags before saving
        for res in current_json.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Create the docpack with conflict-safe naming
        DocpackHandler.create_package(
            outline_data=current_json,
            resource_files=resource_files,
            output_path=docpack_path,
            resource_key_map=resource_key_map,
        )

        # Return just the file path
        return str(docpack_path)

    except Exception as e:
        error_msg = f"Error creating docpack: {str(e)}"
        print(error_msg)
        return None


def render_block_resources(block_resources, block_type, block_id):
    """Render the resources inside a block."""
    print(f"render_block_resources for block {block_id}: {len(block_resources) if block_resources else 0} resources")

    if block_type == "text":
        # Text blocks always show the drop zone, never show resources
        return "Drop reference files here to upload text."

    # AI blocks show resources or drop zone
    if not block_resources:
        return "Drop reference files here for AI context."

    html = ""
    for resource in block_resources:
        # Use title if available, otherwise fall back to name
        display_name = resource.get("title", resource.get("name", "Unknown"))
        path = resource.get("path", "").replace("'", "\\'")  # Escape single quotes

        # For AI blocks, show resource without description input and without icon
        html += f"""
        <div class="dropped-resource" data-resource-path="{path}">
            <span class="dropped-resource-title">{display_name}</span>
            <span class="remove-resource" onclick="removeBlockResource('{block_id}', '{path}')">×</span>
        </div>
        """

    return html


def render_blocks(blocks, focused_block_id=None):
    """Render blocks as HTML."""
    import time

    timestamp = int(time.time() * 1000)

    print(f"render_blocks called with {len(blocks) if blocks else 0} blocks at {timestamp}")
    if blocks:
        for i, block in enumerate(blocks):
            res_count = len(block.get("resources", []))
            print(f"  Block {i} ({block['id']}): {res_count} resources")

    if not blocks:
        return "<div class='empty-blocks-message'>Click '+ Add AI' to add an AI generated section.</div><div class='empty-blocks-message'>Click '+ Add Text' to add a traditional text section.</div>"

    html = f"<!-- Rendered at {timestamp} -->\n"
    for i, block in enumerate(blocks):
        block_id = block["id"]
        is_collapsed = block.get("collapsed", False)
        collapsed_class = "collapsed" if is_collapsed else ""
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
                <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                    <span class='collapse-icon'>⌵</span>
                </button>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='expandBlockOnHeadingFocus("{block_id}"); setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <div class='block-tabs'>
                        <button class='block-tab active' onclick='focusBlockTextarea("{block_id}")'>AI</button>
                        <button class='block-tab' onclick='convertBlock("{block_id}", "text")'>Text</button>
                    </div>
                    <textarea placeholder='Type your AI instruction here...\nThis text will be used for AI content generation.'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        {render_block_resources(block.get("resources", []), "AI", block_id)}
                    </div>
                </div>
            </div>
            """
        elif block["type"] == "heading":
            html += f"""
            <div class='content-block heading-block' data-id='{block_id}'>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header heading-header'>
                    <input type='text' value='{block["content"]}'
                           oninput='updateBlockContent("{block_id}", this.value)'/>
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
                <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                    <span class='collapse-icon'>⌵</span>
                </button>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='expandBlockOnHeadingFocus("{block_id}"); setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <div class='block-tabs'>
                        <button class='block-tab' onclick='convertBlock("{block_id}", "ai")'>AI</button>
                        <button class='block-tab active' onclick='focusBlockTextarea("{block_id}")'>Text</button>
                    </div>
                    <textarea placeholder='Type your text here...\nThis text will be copied into your document.'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        {render_block_resources(block.get("resources", []), "text", block_id)}
                    </div>
                </div>
            </div>
            """

    return html


def handle_file_upload(files, current_resources, title, description, blocks, session_id=None):
    """Handle uploaded files and return HTML display of file names."""
    if not files:
        # Don't return None for outline and json_output to avoid clearing them
        return current_resources, None, gr.update(), gr.update(), session_id

    # Debug: Check what we're receiving
    print(f"DEBUG handle_file_upload - title: {title}, description: {description}, blocks: {blocks}")

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Add new files to resources
    new_resources = current_resources.copy() if current_resources else []

    # Get session files directory
    files_dir = session_manager.get_files_dir(session_id)

    for file_path in files:
        if file_path:
            import shutil

            file_name = os.path.basename(file_path)

            # Copy file to session directory
            session_file_path = files_dir / file_name
            shutil.copy2(file_path, session_file_path)

            # Check if already in resources (by name)
            if not any(r["name"] == file_name for r in new_resources):
                # All uploaded files are text files now
                new_resources.append({
                    "path": str(session_file_path),
                    "name": file_name,
                    "title": file_name,  # Default title is the filename
                    "type": "text",
                    "description": "",  # Initialize with empty description
                })

    # Regenerate outline with new resources
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, blocks)

    # Debug: Check what we're returning
    print(f"DEBUG handle_file_upload - returning json_str: {json_str[:100]}...")
    print("DEBUG handle_file_upload - full return values:")
    print(f"  - new_resources length: {len(new_resources)}")
    print("  - file_upload clear: None")
    print(f"  - outline type: {type(outline)}")
    print(f"  - json_str type: {type(json_str)}, length: {len(json_str)}")
    print(f"  - session_id: {session_id}")

    return (
        new_resources,
        None,  # Clear file upload
        outline,
        json_str,
        session_id,
    )


# Global variable to store current document state for download
current_document_state = {"title": "", "outline_json": "{}", "blocks": []}


def update_resource_title_gradio(resources, resource_path, new_title, title, description, blocks):
    """Update resource title from Gradio component."""
    for resource in resources:
        if resource["path"] == resource_path:
            resource["title"] = new_title
            break

    # Update title in all blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["title"] = new_title

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return resources, outline, json_str


def update_resource_description_gradio(resources, resource_path, new_description, title, description, blocks):
    """Update resource description from Gradio component."""
    for resource in resources:
        if resource["path"] == resource_path:
            resource["description"] = new_description
            break

    # Update description in ALL blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["description"] = new_description

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return resources, outline, json_str


def delete_resource_gradio(resources, resource_path, title, description, blocks):
    """Delete a resource from Gradio component."""
    print(f"Deleting resource: {resource_path}")

    # Remove from resources list
    new_resources = [res for res in resources if res.get("path") != resource_path]

    # Also remove from all blocks that have this resource
    updated_blocks = []
    for block in blocks:
        block_copy = block.copy()
        if "resources" in block_copy:
            # Remove the resource with matching path
            original_count = len(block_copy["resources"])
            block_copy["resources"] = [res for res in block_copy["resources"] if res.get("path") != resource_path]
            new_count = len(block_copy["resources"])

            if original_count != new_count:
                print(f"Removed resource from block {block_copy['id']}: {original_count} -> {new_count}")

            # If this is a text block and we just removed its resource, clear the content
            if block_copy["type"] == "text" and len(block_copy["resources"]) == 0:
                block_copy["content"] = ""

        updated_blocks.append(block_copy)

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, updated_blocks)
    # Return blocks too so the UI updates
    return new_resources, updated_blocks, outline, json_str


def replace_resource_file_gradio(resources, old_resource_path, new_file, title, description, blocks, session_id=None):
    """Replace a resource file from Gradio component."""
    if not new_file:
        return resources, None, "{}", None

    try:
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())

        session_dir = session_manager.get_session_dir(session_id)

        # Copy new file to session directory
        new_file_path = Path(new_file.name)
        new_filename = new_file_path.name
        dest_path = session_dir / new_filename

        # If the new file has the same name as an existing file, add a suffix
        counter = 1
        while dest_path.exists() and str(dest_path) != old_resource_path:
            stem = new_file_path.stem
            suffix = new_file_path.suffix
            new_filename = f"{stem}_{counter}{suffix}"
            dest_path = session_dir / new_filename
            counter += 1

        # Copy the file
        import shutil

        shutil.copy2(new_file.name, dest_path)

        # Update resources list
        for i, resource in enumerate(resources):
            if resource["path"] == old_resource_path:
                # Keep the same title and description
                old_title = resource.get("title", "")
                old_description = resource.get("description", "")

                # Update the resource
                resources[i] = {
                    "name": new_filename,
                    "path": str(dest_path),
                    "title": old_title if old_title else new_filename,
                    "description": old_description,
                }

                # Update in all blocks
                for block in blocks:
                    if "resources" in block:
                        for j, res in enumerate(block["resources"]):
                            if res.get("path") == old_resource_path:
                                block["resources"][j] = {
                                    "path": str(dest_path),
                                    "title": old_title if old_title else new_filename,
                                    "description": old_description,
                                }

                                # If it's a text block, reload the content
                                if block["type"] == "text":
                                    try:
                                        with open(dest_path, "r", encoding="utf-8") as f:
                                            block["content"] = f.read()
                                    except Exception as e:
                                        print(f"Error loading new file content: {e}")

                break

        # Regenerate outline
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)

        # Return with cleared file input
        return resources, outline, json_str, None

    except Exception as e:
        print(f"Error replacing resource file: {e}")
        return resources, None, "{}", None


def log_gradio_functions(app):
    """Log all Gradio function mappings with their fn_index."""
    print("\n=== Gradio Function Index Mapping ===")
    total_fns = 0
    if hasattr(app, "fns"):
        total_fns = len(app.fns)
        print(f"Total registered functions: {total_fns}")
        print(f"Highest fn_index: {total_fns - 1}")

        for idx, fn_data in enumerate(app.fns):
            if fn_data and hasattr(fn_data, "fn"):
                fn = fn_data.fn
                fn_name = fn.__name__ if hasattr(fn, "__name__") else str(fn)
                print(f"fn_index {idx}: {fn_name}")
            else:
                print(f"fn_index {idx}: <empty/None>")
    else:
        print("WARNING: app.fns not found!")
    print("=====================================\n")

    # Also create a mapping file for reference
    mapping = {"total_functions": total_fns, "functions": {}}
    if hasattr(app, "fns"):
        for idx, fn_data in enumerate(app.fns):
            if fn_data and hasattr(fn_data, "fn"):
                fn = fn_data.fn
                fn_name = fn.__name__ if hasattr(fn, "__name__") else str(fn)
                mapping["functions"][idx] = fn_name
            else:
                mapping["functions"][idx] = "<empty/None>"

    # Save to a file for easy reference
    import json

    with open("gradio_fn_index_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)
    print("Function mapping saved to gradio_fn_index_mapping.json")


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

    with gr.Blocks(title="Document Generator", css=custom_css, head=custom_js) as app:
        # Create tabs at the highest level
        with gr.Tabs() as tabs:
            # First tab - New tab that will show first
            with gr.Tab("Start", id="start_tab"):
                gr.Markdown("# Welcome to Document Generator")
                gr.Markdown("This is the start tab. Add your content here.")
                # TODO: Add content for the start tab

            # Second tab - Existing Document Builder content
            with gr.Tab("Document Builder", id="document_builder_tab"):
                # State to track resources and blocks
                resources_state = gr.State([])
                focused_block_state = gr.State(None)
                session_state = gr.State(None)  # Track session ID

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
                initial_outline, initial_json = regenerate_outline_from_state("", "", [], initial_blocks)
                outline_state = gr.State(initial_outline)

                with gr.Row():
                    # App name and explanation
                    with gr.Column(elem_classes="app-header-col"):
                        gr.Markdown("# Document Generator")
                        gr.Markdown(" An AI tool for creating structured documents with customizable sections.")

                    # Import and Save buttons
                    with gr.Column(elem_classes="app-buttons-col"):
                        with gr.Row():
                            # Add empty space to push buttons to the right
                            gr.HTML("<div style='flex: 1;'></div>")
                            # Try Examples button with dropdown container
                            with gr.Column(elem_classes="try-examples-container"):
                                gr.Button(
                                    "Try Examples",
                                    elem_id="try-examples-btn-id",
                                    variant="secondary",
                                    size="sm",
                                    elem_classes="try-examples-btn",
                                )
                                # Dropdown menu (hidden by default via CSS)
                                with gr.Column(elem_classes="examples-dropdown", elem_id="examples-dropdown-id"):
                                    gr.HTML("""
                                        <div class="examples-dropdown-item" data-example="1">
                                            <div class="example-title">README</div>
                                            <div class="example-desc">Technical documentation with code</div>
                                        </div>
                                        <div class="examples-dropdown-item" data-example="2">
                                            <div class="example-title">Product Launch Documentation</div>
                                            <div class="example-desc">Product research and strategy</div>
                                        </div>
                                        <div class="examples-dropdown-item" data-example="3">
                                            <div class="example-title">Annual Performance Review</div>
                                            <div class="example-desc">Employee evaluation and feedback</div>
                                        </div>
                                    """)
                            # New button (for resetting document)
                            new_doc_btn = gr.Button(
                                "New",
                                elem_id="new-builder-btn-id",
                                variant="secondary",
                                size="sm",
                                elem_classes="new-builder-btn",
                            )
                            gr.Button(
                                "Import",
                                elem_id="import-builder-btn-id",
                                variant="secondary",
                                size="sm",
                                elem_classes="import-builder-btn",
                            )
                            save_outline_btn = gr.DownloadButton(
                                "Save",
                                elem_id="save-builder-btn-id",
                                variant="secondary",
                                size="sm",
                                elem_classes="save-builder-btn",
                                visible=True,
                                value=create_docpack_from_current_state,
                            )

                        # Hidden file component for import
                        import_file = gr.File(
                            label="Import Docpack",
                            file_types=[".docpack"],
                            visible=True,
                            elem_id="import-file-input",
                            elem_classes="hidden-component",
                        )

                # Document title and description
                with gr.Row(elem_classes="header-section"):
                    # Document title (narrower width)
                    doc_title = gr.Textbox(
                        value="",
                        placeholder="Document Title",
                        label=None,
                        show_label=False,
                        elem_id="doc-title-id",
                        elem_classes="doc-title-box",
                        scale=2,
                        interactive=True,
                        lines=1,
                        max_lines=1,
                    )

                    # Document description (wider width)
                    doc_description = gr.TextArea(
                        value="",
                        placeholder="Provide overall guidance for the document generation.\nSpecifics may include purpose, audience, style, format, etc.",
                        label=None,
                        show_label=False,
                        elem_id="doc-description-id",
                        elem_classes="doc-description-box",
                        scale=5,
                        lines=2,
                        max_lines=10,
                        interactive=True,
                    )

                # Main content area with three columns
                with gr.Row():
                    # Resources column: Upload Resources button
                    with gr.Column(scale=1, elem_classes="resources-col"):
                        # Drag and drop file upload component
                        file_upload = gr.File(
                            label="Drop Text File Here",
                            file_count="multiple",
                            file_types=[
                                ".txt",
                                ".md",
                                ".py",
                                ".c",
                                ".cpp",
                                ".h",
                                ".java",
                                ".js",
                                ".ts",
                                ".jsx",
                                ".tsx",
                                ".json",
                                ".xml",
                                ".yaml",
                                ".yml",
                                ".toml",
                                ".ini",
                                ".cfg",
                                ".conf",
                                ".sh",
                                ".bash",
                                ".zsh",
                                ".fish",
                                ".ps1",
                                ".bat",
                                ".cmd",
                                ".rs",
                                ".go",
                                ".rb",
                                ".php",
                                ".pl",
                                ".lua",
                                ".r",
                                ".m",
                                ".swift",
                                ".kt",
                                ".scala",
                                ".clj",
                                ".ex",
                                ".exs",
                                ".elm",
                                ".fs",
                                ".ml",
                                ".sql",
                                ".html",
                                ".htm",
                                ".css",
                                ".scss",
                                ".sass",
                                ".less",
                                ".vue",
                                ".svelte",
                                ".astro",
                                ".tex",
                                ".rst",
                                ".adoc",
                                ".org",
                                ".csv",
                            ],
                            elem_classes="file-upload-dropzone",
                            visible=True,
                            height=90,
                            show_label=False,
                        )

                        # Container for dynamic resource components
                        with gr.Column(elem_classes="resources-display-area"):

                            @gr.render(inputs=resources_state)
                            def render_resource_components(resources):
                                if not resources:
                                    gr.HTML(
                                        value="<p style='color: #666; font-size: 12px'>(.md, .csv, .py, .json, .txt, etc.)</p>"
                                        "<p style='color: #666; font-size: 12px'>These reference files will be used for AI context.</p>"
                                    )
                                else:
                                    for idx, resource in enumerate(resources):
                                        with gr.Group(elem_classes="resource-item-gradio"):
                                            # Hidden element containing resource path for drag and drop
                                            gr.HTML(
                                                f'<div class="resource-path-hidden" style="display:none;" data-path="{resource["path"]}">{resource["path"]}</div>'
                                            )

                                            with gr.Row(elem_classes="resource-row-gradio"):
                                                with gr.Column(scale=1, elem_classes="resource-info-col"):
                                                    # Resource title
                                                    resource_title = gr.Textbox(
                                                        value=resource.get("title", resource["name"]),
                                                        placeholder="Title",
                                                        label=None,
                                                        show_label=False,
                                                        elem_classes="resource-title-gradio",
                                                        scale=1,
                                                    )

                                                    delete_btn = gr.Button(
                                                        "🗑", elem_classes="resource-delete-btn", size="sm"
                                                    )

                                                    # Resource description
                                                    resource_desc = gr.Textbox(
                                                        value=resource.get("description", ""),
                                                        placeholder="Add a description for this resource...",
                                                        label=None,
                                                        show_label=False,
                                                        elem_classes="resource-desc-gradio",
                                                        lines=2,
                                                        scale=1,
                                                    )

                                                    # Filename display
                                                    gr.HTML(
                                                        elem_classes="resource-filename",
                                                        value=f"<div>  {resource['name']}</div>",
                                                    )

                                            # File replacement upload area
                                            replace_file = gr.File(
                                                label="Drop file here to replace",
                                                file_types=[
                                                    ".txt",
                                                    ".md",
                                                    ".py",
                                                    ".c",
                                                    ".cpp",
                                                    ".h",
                                                    ".java",
                                                    ".js",
                                                    ".ts",
                                                    ".jsx",
                                                    ".tsx",
                                                    ".json",
                                                    ".xml",
                                                    ".yaml",
                                                    ".yml",
                                                    ".toml",
                                                    ".ini",
                                                    ".cfg",
                                                    ".conf",
                                                    ".sh",
                                                    ".bash",
                                                    ".zsh",
                                                    ".fish",
                                                    ".ps1",
                                                    ".bat",
                                                    ".cmd",
                                                    ".rs",
                                                    ".go",
                                                    ".rb",
                                                    ".php",
                                                    ".pl",
                                                    ".lua",
                                                    ".r",
                                                    ".m",
                                                    ".swift",
                                                    ".kt",
                                                    ".scala",
                                                    ".clj",
                                                    ".ex",
                                                    ".exs",
                                                    ".elm",
                                                    ".fs",
                                                    ".ml",
                                                    ".sql",
                                                    ".html",
                                                    ".htm",
                                                    ".css",
                                                    ".scss",
                                                    ".sass",
                                                    ".less",
                                                    ".vue",
                                                    ".svelte",
                                                    ".astro",
                                                    ".tex",
                                                    ".rst",
                                                    ".adoc",
                                                    ".org",
                                                    ".csv",
                                                ],
                                                elem_classes="resource-upload-gradio",
                                                scale=1,
                                                show_label=False,
                                            )

                                            # Connect events for this resource
                                            resource_path = resource["path"]

                                            # Title update - don't update resources_state to avoid re-render
                                            resource_title.change(
                                                fn=update_resource_title_gradio,
                                                inputs=[
                                                    resources_state,
                                                    gr.State(resource_path),
                                                    resource_title,
                                                    doc_title,
                                                    doc_description,
                                                    blocks_state,
                                                ],
                                                outputs=[
                                                    gr.State(),
                                                    outline_state,
                                                    json_output,
                                                ],  # Use dummy State to avoid re-render
                                                trigger_mode="always_last",  # Only trigger after user stops typing
                                            )

                                            # Description update - don't update resources_state to avoid re-render
                                            resource_desc.change(
                                                fn=update_resource_description_gradio,
                                                inputs=[
                                                    resources_state,
                                                    gr.State(resource_path),
                                                    resource_desc,
                                                    doc_title,
                                                    doc_description,
                                                    blocks_state,
                                                ],
                                                outputs=[
                                                    gr.State(),
                                                    outline_state,
                                                    json_output,
                                                ],  # Use dummy State to avoid re-render
                                                trigger_mode="always_last",  # Only trigger after user stops typing
                                            )

                                            # Delete button
                                            def delete_gradio_and_render(resources, path, title, desc, blocks, focused):
                                                """Delete resource via Gradio button and render blocks."""
                                                print("\n=== delete_gradio_and_render called ===")
                                                new_res, new_blocks, outline, json_str = delete_resource_gradio(
                                                    resources, path, title, desc, blocks
                                                )
                                                blocks_html = render_blocks(new_blocks, focused)
                                                print("=== delete_gradio_and_render complete ===\n")
                                                return new_res, new_blocks, outline, json_str, blocks_html

                                            delete_btn.click(
                                                fn=delete_gradio_and_render,
                                                inputs=[
                                                    resources_state,
                                                    gr.State(resource_path),
                                                    doc_title,
                                                    doc_description,
                                                    blocks_state,
                                                    focused_block_state,
                                                ],
                                                outputs=[
                                                    resources_state,
                                                    blocks_state,
                                                    outline_state,
                                                    json_output,
                                                    blocks_display,
                                                ],
                                            )

                                            # File replacement
                                            replace_file.change(
                                                fn=replace_resource_file_gradio,
                                                inputs=[
                                                    resources_state,
                                                    gr.State(resource_path),
                                                    replace_file,
                                                    doc_title,
                                                    doc_description,
                                                    blocks_state,
                                                    session_state,
                                                ],
                                                outputs=[resources_state, outline_state, json_output, replace_file],
                                            ).then(
                                                # Force JSON update after resources render
                                                fn=lambda title, desc, res, blocks: regenerate_outline_from_state(
                                                    title, desc, res, blocks
                                                )[1],
                                                inputs=[doc_title, doc_description, resources_state, blocks_state],
                                                outputs=[json_output],
                                            )

                    # Workspace column: AI, H, T buttons (aligned left)
                    with gr.Column(scale=1, elem_classes="workspace-col"):
                        with gr.Row(elem_classes="square-btn-row"):
                            ai_btn = gr.Button("+ Add Section", elem_classes="add-section-btn", size="sm")

                        # Workspace panel for stacking content blocks
                        with gr.Column(elem_classes="workspace-display"):
                            blocks_display = gr.HTML(
                                value=render_blocks(initial_blocks, None), elem_classes="blocks-container"
                            )

                            # Hidden components for JS communication
                            delete_block_id = gr.Textbox(
                                visible=True, elem_id="delete-block-id", elem_classes="hidden-component"
                            )
                            delete_trigger = gr.Button(
                                "Delete", visible=True, elem_id="delete-trigger", elem_classes="hidden-component"
                            )

                            # Hidden HTML for JavaScript execution
                            js_executor = gr.HTML(visible=False)

                            # Hidden components for content updates
                            update_block_id = gr.Textbox(
                                visible=True, elem_id="update-block-id", elem_classes="hidden-component"
                            )
                            update_content_input = gr.Textbox(
                                visible=True, elem_id="update-content-input", elem_classes="hidden-component"
                            )
                            update_trigger = gr.Button(
                                "Update", visible=True, elem_id="update-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for toggle collapse
                            toggle_block_id = gr.Textbox(
                                visible=True, elem_id="toggle-block-id", elem_classes="hidden-component"
                            )
                            toggle_trigger = gr.Button(
                                "Toggle", visible=True, elem_id="toggle-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for heading updates
                            update_heading_block_id = gr.Textbox(
                                visible=True, elem_id="update-heading-block-id", elem_classes="hidden-component"
                            )
                            update_heading_input = gr.Textbox(
                                visible=True, elem_id="update-heading-input", elem_classes="hidden-component"
                            )
                            update_heading_trigger = gr.Button(
                                "Update Heading",
                                visible=True,
                                elem_id="update-heading-trigger",
                                elem_classes="hidden-component",
                            )

                            # Hidden components for indent updates
                            indent_block_id = gr.Textbox(
                                visible=True, elem_id="indent-block-id", elem_classes="hidden-component"
                            )
                            indent_direction = gr.Textbox(
                                visible=True, elem_id="indent-direction", elem_classes="hidden-component"
                            )
                            indent_trigger = gr.Button(
                                "Update Indent", visible=True, elem_id="indent-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for focus tracking
                            focus_block_id = gr.Textbox(
                                visible=True, elem_id="focus-block-id", elem_classes="hidden-component"
                            )
                            focus_trigger = gr.Button(
                                "Set Focus", visible=True, elem_id="focus-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for adding block after
                            add_after_block_id = gr.Textbox(
                                visible=True, elem_id="add-after-block-id", elem_classes="hidden-component"
                            )
                            add_after_type = gr.Textbox(
                                visible=True, elem_id="add-after-type", elem_classes="hidden-component"
                            )
                            add_after_trigger = gr.Button(
                                "Add After", visible=True, elem_id="add-after-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for converting block type
                            convert_block_id = gr.Textbox(
                                visible=True, elem_id="convert-block-id", elem_classes="hidden-component"
                            )
                            convert_type = gr.Textbox(
                                visible=True, elem_id="convert-type", elem_classes="hidden-component"
                            )
                            convert_trigger = gr.Button(
                                "Convert", visible=True, elem_id="convert-trigger", elem_classes="hidden-component"
                            )

                            # Hidden components for updating block resources
                            update_resources_block_id = gr.Textbox(
                                visible=True, elem_id="update-resources-block-id", elem_classes="hidden-component"
                            )
                            update_resources_input = gr.Textbox(
                                visible=True, elem_id="update-resources-input", elem_classes="hidden-component"
                            )
                            update_resources_trigger = gr.Button(
                                "Update Resources",
                                visible=True,
                                elem_id="update-resources-trigger",
                                elem_classes="hidden-component",
                            )

                            # Hidden components for removing block resources
                            remove_resource_block_id = gr.Textbox(
                                visible=True, elem_id="remove-resource-block-id", elem_classes="hidden-component"
                            )
                            remove_resource_path = gr.Textbox(
                                visible=True, elem_id="remove-resource-path", elem_classes="hidden-component"
                            )
                            remove_resource_trigger = gr.Button(
                                "Remove Resource",
                                visible=True,
                                elem_id="remove-resource-trigger",
                                elem_classes="hidden-component",
                            )

                            # Hidden components for deleting resources from panel
                            delete_panel_resource_path = gr.Textbox(visible=False, elem_id="delete-panel-resource-path")
                            delete_panel_resource_trigger = gr.Button(
                                "Delete Panel Resource", visible=False, elem_id="delete-panel-resource-trigger"
                            )

                            # Hidden components for updating resource descriptions
                            update_desc_block_id = gr.Textbox(visible=False, elem_id="update-desc-block-id")
                            update_desc_resource_path = gr.Textbox(visible=False, elem_id="update-desc-resource-path")
                            update_desc_text = gr.Textbox(visible=False, elem_id="update-desc-text")
                            update_desc_trigger = gr.Button(
                                "Update Description", visible=False, elem_id="update-desc-trigger"
                            )

                            # Hidden components for loading examples
                            example_id_input = gr.Textbox(
                                visible=True, elem_id="example-id-input", elem_classes="hidden-component"
                            )
                            load_example_trigger = gr.Button(
                                "Load Example",
                                visible=True,
                                elem_id="load-example-trigger",
                                elem_classes="hidden-component",
                            )

                            # Hidden components for updating resource titles
                            update_title_resource_path = gr.Textbox(visible=False, elem_id="update-title-resource-path")
                            update_title_text = gr.Textbox(visible=False, elem_id="update-title-text")
                            update_title_trigger = gr.Button(
                                "Update Title", visible=False, elem_id="update-title-trigger"
                            )

                            # Hidden button for updating resource panel descriptions
                            update_panel_desc_trigger = gr.Button(
                                "Update Panel Description", visible=False, elem_id="update-panel-desc-trigger"
                            )

                            # Hidden components for replacing resource files
                            replace_resource_path = gr.Textbox(visible=False, elem_id="replace-resource-path")
                            replace_resource_file_input = gr.File(
                                visible=False,
                                elem_id="replace-resource-file",
                                file_types=[
                                    ".txt",
                                    ".md",
                                    ".py",
                                    ".c",
                                    ".cpp",
                                    ".h",
                                    ".java",
                                    ".js",
                                    ".ts",
                                    ".jsx",
                                    ".tsx",
                                    ".json",
                                    ".xml",
                                    ".yaml",
                                    ".yml",
                                    ".toml",
                                    ".ini",
                                    ".cfg",
                                    ".conf",
                                    ".sh",
                                    ".bash",
                                    ".zsh",
                                    ".fish",
                                    ".ps1",
                                    ".bat",
                                    ".cmd",
                                    ".rs",
                                    ".go",
                                    ".rb",
                                    ".php",
                                    ".pl",
                                    ".lua",
                                    ".r",
                                    ".m",
                                    ".swift",
                                    ".kt",
                                    ".scala",
                                    ".clj",
                                    ".ex",
                                    ".exs",
                                    ".elm",
                                    ".fs",
                                    ".ml",
                                    ".sql",
                                    ".html",
                                    ".htm",
                                    ".css",
                                    ".scss",
                                    ".sass",
                                    ".less",
                                    ".vue",
                                    ".svelte",
                                    ".astro",
                                    ".tex",
                                    ".rst",
                                    ".adoc",
                                    ".org",
                                    ".csv",
                                ],
                            )
                            replace_resource_trigger = gr.Button(
                                "Replace Resource", visible=False, elem_id="replace-resource-trigger"
                            )
                            replace_success_msg = gr.Textbox(visible=False, elem_id="replace-success-msg")

                    # Generated document column: Generate and Save Document buttons (aligned right)
                    with gr.Column(scale=1, elem_classes="generate-col"):
                        with gr.Row(elem_classes="generate-btn-row"):
                            # Add empty space to push buttons to the right
                            gr.HTML("<div style='flex: 1;'></div>")
                            generate_doc_btn = gr.Button(
                                "▷ Generate", elem_classes="generate-btn", variant="primary", size="sm"
                            )
                            save_doc_btn = gr.DownloadButton(
                                "Download",
                                elem_classes="download-btn",
                                variant="secondary",
                                size="sm",
                                visible=True,
                                interactive=False,  # Disabled until document is generated
                            )

                        # Generated document display panel
                        with gr.Column(elem_classes="generate-display"):
                            generated_content_html = gr.HTML(
                                value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>",
                                elem_classes="generated-content",
                                visible=True,
                            )
                            generated_content = gr.Markdown(visible=False)

                        # Debug panel for JSON display (collapsible)
                        with gr.Column(elem_classes="debug-panel", elem_id="debug-panel-container"):
                            with gr.Row(elem_classes="debug-panel-header"):
                                gr.HTML("""
                                    <div class="debug-panel-title" onclick="toggleDebugPanel()">
                                        <span>Debug Panel (JSON Output)</span>
                                        <span class="debug-collapse-icon" id="debug-collapse-icon">⌵</span>
                                    </div>
                                """)

                            with gr.Column(
                                elem_classes="debug-panel-content", elem_id="debug-panel-content", visible=True
                            ):
                                json_output = gr.Code(
                                    value=initial_json, language="json", elem_classes="json-debug-output"
                                )

        # Helper function to add AI block and regenerate outline
        def handle_add_ai_block_top(blocks, _, title, description, resources):
            blocks = add_ai_block(blocks, None)
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Helper function to add Text block and regenerate outline
        def handle_add_text_block_top(blocks, _, title, description, resources):
            blocks = add_text_block(blocks, None)
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Connect button click to add AI block
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

        # Connect button click to add Text block

        # Connect New document button to reset everything
        new_doc_btn.click(
            fn=reset_document,
            inputs=[session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                import_file,
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            fn=lambda: gr.update(value="<script>setTimeout(resetDocumentDescription, 100);</script>"),
            outputs=js_executor,
        )

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
            outputs=[blocks_state, outline_state, json_output],
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

        # Update block resources handler
        update_resources_trigger.click(
            fn=update_block_resources,
            inputs=[
                blocks_state,
                update_resources_block_id,
                update_resources_input,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Remove block resource handler
        remove_resource_trigger.click(
            fn=remove_block_resource,
            inputs=[
                blocks_state,
                remove_resource_block_id,
                remove_resource_path,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Delete resource from panel handler
        def delete_and_render(resources, resource_path, title, description, blocks, focused_id):
            """Delete resource and return both the state updates and rendered HTML."""
            print("\n=== delete_and_render called ===")
            print(f"Resource path: {resource_path}")
            print(f"Blocks before: {len(blocks)} blocks")

            new_resources, updated_blocks, outline, json_str = delete_resource_from_panel(
                resources, resource_path, title, description, blocks
            )

            print(f"Blocks after delete: {len(updated_blocks)} blocks")

            # Render the blocks immediately
            blocks_html = render_blocks(updated_blocks, focused_id)

            print(f"Generated HTML length: {len(blocks_html)}")
            print("=== delete_and_render complete ===\n")

            return new_resources, updated_blocks, outline, json_str, blocks_html

        delete_panel_resource_trigger.click(
            fn=delete_and_render,
            inputs=[
                resources_state,
                delete_panel_resource_path,
                doc_title,
                doc_description,
                blocks_state,
                focused_block_state,
            ],
            outputs=[resources_state, blocks_state, outline_state, json_output, blocks_display],
        )

        # Update resource description handler - don't re-render blocks to avoid interrupting typing
        update_desc_trigger.click(
            fn=update_resource_description,
            inputs=[
                blocks_state,
                update_desc_block_id,
                update_desc_resource_path,
                update_desc_text,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        )

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

        # Handle file uploads (defined after json_output is created)
        file_upload.change(
            fn=handle_file_upload,
            inputs=[file_upload, resources_state, doc_title, doc_description, blocks_state, session_state],
            outputs=[resources_state, file_upload, outline_state, json_output, session_state],
        ).then(
            # Force JSON update after resources render
            fn=lambda title, desc, res, blocks: regenerate_outline_from_state(title, desc, res, blocks)[1],
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[json_output],
        )

        # Generate document handler - update to return the download button state
        async def handle_generate_and_update_download(title, description, resources, blocks, session_id):
            """Generate document and update download button."""
            json_str, content, file_path, filename = await handle_document_generation(
                title, description, resources, blocks, session_id
            )

            # Hide HTML component and show Markdown component
            html_update = gr.update(visible=False)
            markdown_update = gr.update(value=content, visible=True)

            if file_path:
                download_update = gr.update(value=file_path, interactive=True)
            else:
                download_update = gr.update(interactive=False)

            # Re-enable the generate button
            generate_btn_update = gr.update(interactive=True)

            return json_str, markdown_update, html_update, download_update, generate_btn_update

        generate_doc_btn.click(
            fn=lambda: [
                gr.update(interactive=False),  # Disable generate button
                gr.update(visible=False),  # Hide markdown content
                gr.update(
                    value="<em></em><br><br><br>", visible=True
                ),  # Show HTML with empty content but structure intact
                gr.update(interactive=False),  # Disable download button
            ],
            outputs=[generate_doc_btn, generated_content, generated_content_html, save_doc_btn],
        ).then(
            fn=handle_generate_and_update_download,
            inputs=[doc_title, doc_description, resources_state, blocks_state, session_state],
            outputs=[json_output, generated_content, generated_content_html, save_doc_btn, generate_doc_btn],
        )

        # Save button is handled directly by DownloadButton with create_docpack_from_current_state

        # Import file handler
        import_file.change(
            fn=import_outline,
            inputs=[import_file, session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                import_file,  # Add import_file to outputs to clear it
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update save button value whenever outline changes
        outline_state.change(fn=lambda: gr.update(value=create_docpack_from_current_state()), outputs=save_outline_btn)

        # Load example handler
        load_example_trigger.click(
            fn=load_example,
            inputs=[example_id_input, session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update resource title handler - don't re-render resources to avoid interrupting typing
        update_title_trigger.click(
            fn=update_resource_title,
            inputs=[
                resources_state,
                update_title_resource_path,
                update_title_text,
                doc_title,
                doc_description,
                blocks_state,
            ],
            outputs=[resources_state, outline_state, json_output],
        )

        # Update resource panel description handler - reuse the same inputs
        update_panel_desc_trigger.click(
            fn=update_resource_panel_description,
            inputs=[
                resources_state,
                update_title_resource_path,
                update_title_text,
                doc_title,
                doc_description,
                blocks_state,
            ],
            outputs=[resources_state, outline_state, json_output],
        )

        # Replace resource file handler
        def handle_resource_replacement(resources, old_path, new_file, doc_title, doc_description, blocks, session_id):
            """Handle resource file replacement."""
            if not new_file:
                # No file selected, return unchanged - regenerate outline to return current state
                outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)
                return resources, blocks, outline, json_str, ""

            # new_file is the file path from Gradio
            new_file_path = new_file if isinstance(new_file, str) else new_file.name

            # Call the replace function
            updated_resources, updated_blocks, resources_html, outline, json_str, success_msg = replace_resource_file(
                resources, old_path, new_file_path, doc_title, doc_description, blocks, session_id
            )

            # Return only the values that match the outputs list
            return updated_resources, updated_blocks, outline, json_str, success_msg

        replace_resource_trigger.click(
            fn=handle_resource_replacement,
            inputs=[
                resources_state,
                replace_resource_path,
                replace_resource_file_input,
                doc_title,
                doc_description,
                blocks_state,
                session_state,
            ],
            outputs=[
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                replace_success_msg,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            # Clear the file input after processing
            fn=lambda: None,
            outputs=replace_resource_file_input,
        )

    return app


def check_deployment_status():
    """Quick deployment status check."""
    # Verify essential configuration
    app_root = Path(__file__).resolve().parents[1]
    bundled_recipe_path = app_root / "document_generator_v2_app" / "recipes" / "document_generator_recipe.json"

    print("Document Generator starting...")
    print(f"Recipe source: {'bundled' if bundled_recipe_path.exists() else 'development'}")

    # Show LLM provider configuration
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    print(f"LLM: {provider}/{model}")


def main():
    """Main entry point for the Document Builder app."""
    # Load environment variables from .env file
    load_dotenv()

    # Run diagnostic check
    check_deployment_status()

    # Configuration for hosting - Azure App Service uses PORT environment variable
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "8000")))
    print(f"Server: {server_name}:{server_port}")

    app = create_app()

    # Log all function mappings
    log_gradio_functions(app)

    # Add runtime request logging
    import functools

    def log_gradio_request(fn, fn_index):
        """Wrapper to log function calls with their index."""

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            print(
                f"\n>>> Gradio function call: fn_index={fn_index}, function={fn.__name__ if hasattr(fn, '__name__') else str(fn)}"
            )
            try:
                result = fn(*args, **kwargs)
                print("<<< Function completed successfully")
                return result
            except Exception as e:
                print(f"<<< Function failed with error: {type(e).__name__}: {e}")
                raise

        return wrapper

    # Wrap all registered functions with logging
    # if hasattr(app, "fns"):
    #    for idx, fn_data in enumerate(app.fns):
    #        if fn_data and hasattr(fn_data, "fn") and fn_data.fn:
    #            original_fn = fn_data.fn
    #            fn_data.fn = log_gradio_request(original_fn, idx)
    #            print(
    #                f"Added logging to fn_index {idx}: {original_fn.__name__ if hasattr(original_fn, '__name__') else str(original_fn)}"
    #            )

    # Also add error handler for out-of-bounds function indices
    # original_push = None
    # if hasattr(app, "_queue") and hasattr(app._queue, "push"):
    #    original_push = app._queue.push
    #
    #    async def debug_push(body, *args, **kwargs):
    #        print(f"\n>>> Queue push request: fn_index={body.fn_index if hasattr(body, 'fn_index') else 'unknown'}")
    #        if hasattr(app, "fns") and hasattr(body, "fn_index"):
    #            max_index = len(app.fns) - 1
    #            if body.fn_index > max_index:
    #                print(f"!!! ERROR: fn_index {body.fn_index} is out of bounds! Max index is {max_index}")
    #                print(f"!!! Total registered functions: {len(app.fns)}")
    #        try:
    #            return await original_push(body, *args, **kwargs)
    #        except KeyError as e:
    #            print(f"!!! KeyError in queue push: {e}")
    #            print(f"!!! Requested fn_index: {body.fn_index if hasattr(body, 'fn_index') else 'unknown'}")
    #            print(f"!!! Available functions: {len(app.fns) if hasattr(app, 'fns') else 'unknown'}")
    #            raise
    #
    #    app._queue.push = debug_push

    # Enable debug mode to see fn_index mappings
    import logging

    logging.basicConfig(level=logging.DEBUG)
    app.launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True, debug=True)


if __name__ == "__main__":
    main()
