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
from .session import session_manager
from .package_handler import DocpackHandler

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
        generated_content = await generate_document(outline)

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

    # First, collect all resource descriptions from blocks
    resource_descriptions = {}
    for block in blocks:
        if block.get("type") == "ai" and "resources" in block:
            for res in block["resources"]:
                if res.get("path") and res.get("description"):
                    # Store the description keyed by path
                    resource_descriptions[res["path"]] = res["description"]

    # Process resources with descriptions from blocks
    for idx, resource in enumerate(resources):
        # Get description from blocks if available, otherwise empty
        description = resource_descriptions.get(resource["path"], "")
        doc_json["resources"].append({
            "key": f"resource_{idx + 1}",
            "path": resource["path"],
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


def delete_resource_from_panel(resources, resource_path, title, description, blocks):
    """Delete a resource from the resource panel and all blocks that use it."""
    # Remove from resources list
    new_resources = [res for res in resources if res.get("path") != resource_path]

    # Also remove from all blocks that have this resource
    for block in blocks:
        if "resources" in block:
            # Count resources before removal
            original_count = len(block["resources"])

            # Remove the resource
            block["resources"] = [res for res in block["resources"] if res.get("path") != resource_path]

            # If this was a text block and we removed its only resource, clear the content
            if block["type"] == "text" and original_count > 0 and len(block["resources"]) == 0:
                block["content"] = ""

    # Generate HTML for resources display
    if new_resources:
        html_items = []
        for resource in new_resources:
            icon = "📄"  # Always use text file icon
            css_class = "resource-item text"
            path = resource["path"].replace("'", "\\'")  # Escape single quotes
            html_items.append(
                f'<div class="{css_class}" draggable="true" data-resource-name="{resource["name"]}" data-resource-type="text" data-resource-path="{resource["path"]}">'
                f"{icon} {resource['name']}"
                f'<span class="resource-delete" onclick="deleteResourceFromPanel(\'{path}\')">×</span>'
                f"</div>"
            )
        resources_html = "\n".join(html_items)
    else:
        resources_html = "<p style='color: #666; font-size: 12px;'>No text files uploaded yet.</p>"

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, blocks)

    return new_resources, blocks, gr.update(value=resources_html), outline, json_str


def load_example(example_id, session_id=None):
    """Load a predefined example based on the example ID."""
    if not example_id:
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), session_id

    # Map example IDs to file paths - now using .docpack files
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = {
        "1": examples_dir / "readme-generation.docpack",
        "2": examples_dir / "launch-documentation.docpack",
        "3": examples_dir / "marketing-report.docpack",
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
            gr.update(),  # resources_display
            session_id,  # session_id
        )

    # Use the import_outline function to load the example
    return import_outline(str(file_path), session_id)


def import_outline(file_path, session_id=None):
    """Import an outline from a .docpack file and convert to blocks format."""
    if not file_path:
        # Return 9 values: title, description, resources, blocks, outline, json, resources_display, import_file, session_id
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), None, session_id
    
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
                gr.update(),  # resources_display
                None,  # import_file
                session_id,  # session_id
            )
        
        # Use session directory for extraction
        session_dir = session_manager.get_session_dir(session_id)
        
        # Extract the docpack to session directory
        json_data, extracted_files = DocpackHandler.extract_package(file_path, session_dir)

        # Extract title and description
        title = json_data.get("title", "Document Title")
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
                gr.update(),  # resources_display
                None,  # import_file
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

        # Regenerate outline and JSON
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)

        # Generate resources HTML
        if resources:
            html_items = []
            for resource in resources:
                icon = "🖼️" if resource.get("type") == "image" else "📄"
                css_class = f"resource-item {resource.get('type', 'file')}"
                path = resource["path"].replace("'", "\\'")  # Escape single quotes
                html_items.append(
                    f'<div class="{css_class}" draggable="true" data-resource-name="{resource["name"]}" data-resource-type="text" data-resource-path="{resource["path"]}">'
                    f"{icon} {resource['name']}"
                    f'<span class="resource-delete" onclick="deleteResourceFromPanel(\'{path}\')">×</span>'
                    f"</div>"
                )
            resources_html = "\n".join(html_items)
        else:
            resources_html = "<p style='color: #666; font-size: 12px'>No resources uploaded yet</p>"

        # Return None for import_file to clear it, and include session_id
        return title, description, resources, blocks, outline, json_str, gr.update(value=resources_html), None, session_id

    except Exception as e:
        error_msg = f"Error importing file: {str(e)}"
        print(error_msg)
        # Return current values on error (including None for import_file and session_id)
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), None, session_id


def save_outline(title, outline_json, blocks):
    """Save the outline as a .docpack file with all resources bundled."""
    from datetime import datetime
    import shutil

    try:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Create filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
        docpack_name = f"{safe_title}_{timestamp}.docpack"
        docpack_path = output_dir / docpack_name

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
            resource_key_map=resource_key_map
        )

        # Return success (hidden message)
        return gr.update(visible=False)

    except Exception as e:
        error_msg = f"Error saving docpack: {str(e)}"
        return gr.update(value=error_msg, visible=True)


def render_block_resources(block_resources, block_type, block_id):
    """Render the resources inside a block."""
    if block_type == "text":
        # Text blocks always show the drop zone, never show resources
        return "Drop reference files here to upload text."

    # AI blocks show resources or drop zone
    if not block_resources:
        return "Drop reference files here for AI context."

    html = ""
    for resource in block_resources:
        icon = "📄"  # Always use text file icon
        name = resource.get("name", "Unknown")
        path = resource.get("path", "").replace("'", "\\'")  # Escape single quotes
        description = resource.get("description", "").replace('"', "&quot;")  # Escape quotes for HTML attribute

        # For AI blocks, show resource with description input
        html += f'''
        <div class="dropped-resource-container">
            <div class="dropped-resource">
                {icon} {name}
                <span class="remove-resource" onclick="removeBlockResource('{block_id}', '{path}')">×</span>
            </div>
            <input type="text"
                   class="resource-description"
                   placeholder="Describe why this resource is relevant..."
                   value="{description}"
                   oninput="updateResourceDescription('{block_id}', '{path}', this.value)">
        </div>
        '''

    return html


def render_blocks(blocks, focused_block_id=None):
    """Render blocks as HTML."""
    if not blocks:
        return "<div class='empty-blocks-message'>Click '+ Add AI' to add an AI generated section.</div><div class='empty-blocks-message'>Click '+ Add Text' to add a traditional text section.</div>"

    html = ""
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
                <button class='convert-btn convert-to-text' onclick='convertBlock("{block_id}", "text")'>T</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <textarea placeholder='This text will be used for AI content generation.\nType your AI instruction here...'
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
                <button class='convert-btn convert-to-ai' onclick='convertBlock("{block_id}", "ai")'>AI</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <textarea placeholder='This text will be copied into your document.\nType your text here...'
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
        return current_resources, gr.update(), None, gr.update(), gr.update(), session_id
    
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
                new_resources.append({"path": str(session_file_path), "name": file_name, "type": "text"})

    # Generate HTML for resources display
    if new_resources:
        html_items = []
        for resource in new_resources:
            icon = "📄"  # Always use text file icon
            css_class = "resource-item text"
            path = resource["path"].replace("'", "\\'")  # Escape single quotes
            html_items.append(
                f'<div class="{css_class}" draggable="true" data-resource-name="{resource["name"]}" data-resource-type="text" data-resource-path="{resource["path"]}">'
                f"{icon} {resource['name']}"
                f'<span class="resource-delete" onclick="deleteResourceFromPanel(\'{path}\')">×</span>'
                f"</div>"
            )
        resources_html = "\n".join(html_items)
    else:
        resources_html = "<p style='color: #666; font-size: 12px;'>No text files uploaded yet.</p>"

    # Regenerate outline with new resources
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, blocks)

    return new_resources, gr.update(value=resources_html), None, outline, json_str, session_id  # Return None to clear file upload


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
        initial_outline, initial_json = regenerate_outline_from_state("Document Title", "", [], initial_blocks)
        outline_state = gr.State(initial_outline)

        with gr.Row():
            # App name and explanation
            with gr.Column(elem_classes="app-header-col"):
                gr.Markdown("# Document Generator")
                gr.Markdown(" An AI tool for creating structured documents with customizable sections.")

            # Import and Save buttons
            with gr.Column():
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
                                    <div class="example-title">Business Report</div>
                                    <div class="example-desc">Marketing analysis and strategy</div>
                                </div>
                            """)
                    gr.Button(
                        "Import",
                        elem_id="import-builder-btn-id",
                        variant="secondary",
                        size="sm",
                        elem_classes="import-builder-btn",
                    )
                    save_builder_btn = gr.Button(
                        "Save",
                        elem_id="save-builder-btn-id",
                        variant="secondary",
                        size="sm",
                        elem_classes="save-builder-btn",
                    )

                # Status message for save operation
                save_status = gr.Markdown(visible=False, elem_classes="save-status-message")

                # Hidden file component for import
                import_file = gr.File(
                    label="Import Docpack", file_types=[".docpack"], visible=False, elem_id="import-file-input"
                )

        # Document title and description
        with gr.Row(elem_classes="header-section"):
            # Document title (narrower width)
            doc_title = gr.Textbox(
                value="Document Title",
                placeholder="Document Title",
                label=None,
                show_label=False,
                elem_id="doc-title-id",
                elem_classes="doc-title-box",
                scale=2,
                interactive=True,
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
                # File upload component styled as button
                gr.Button(
                    "Upload References",
                    variant="secondary",
                    size="sm",
                    elem_id="upload-resources-btn-id",
                    elem_classes="upload-resources-btn",
                )

                file_upload = gr.File(
                    label="Upload References",
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
                    elem_classes="upload-file-invisible-btn",
                    visible=False,
                )

                resources_display = gr.HTML(
                    value="<p style='color: #666; font-size: 12px'>No text files uploaded yet.</p>",
                    elem_classes="resources-display-area",
                )

            # Workspace column: AI, H, T buttons (aligned left)
            with gr.Column(scale=1, elem_classes="workspace-col"):
                with gr.Row(elem_classes="square-btn-row"):
                    ai_btn = gr.Button("+ Add AI", elem_classes="add-section-btn", size="sm")
                    new_btn = gr.Button("+ Add Text", elem_classes="secondary-workspace-btn", size="sm")

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

                    # Hidden components for updating block resources
                    update_resources_block_id = gr.Textbox(visible=False, elem_id="update-resources-block-id")
                    update_resources_input = gr.Textbox(visible=False, elem_id="update-resources-input")
                    update_resources_trigger = gr.Button(
                        "Update Resources", visible=False, elem_id="update-resources-trigger"
                    )

                    # Hidden components for removing block resources
                    remove_resource_block_id = gr.Textbox(visible=False, elem_id="remove-resource-block-id")
                    remove_resource_path = gr.Textbox(visible=False, elem_id="remove-resource-path")
                    remove_resource_trigger = gr.Button(
                        "Remove Resource", visible=False, elem_id="remove-resource-trigger"
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
                    update_desc_trigger = gr.Button("Update Description", visible=False, elem_id="update-desc-trigger")

                    # Hidden components for loading examples
                    example_id_input = gr.Textbox(visible=False, elem_id="example-id-input")
                    load_example_trigger = gr.Button("Load Example", visible=False, elem_id="load-example-trigger")

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
                    generated_content = gr.Markdown(
                        value="*Click 'Generate Document' to see the generated content here.*",
                        elem_classes="generated-content",
                    )

                # Debug panel for JSON display
                with gr.Column(elem_classes="debug-panel"):
                    gr.Markdown("### Debug Panel (JSON Output)")
                    json_output = gr.Code(value=initial_json, language="json", elem_classes="json-debug-output")

        # Handle file uploads (defined after json_output is created)
        file_upload.change(
            handle_file_upload,
            inputs=[file_upload, resources_state, doc_title, doc_description, blocks_state, session_state],
            outputs=[resources_state, resources_display, file_upload, outline_state, json_output, session_state],
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
        new_btn.click(
            fn=handle_add_text_block_top,
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
        delete_panel_resource_trigger.click(
            fn=delete_resource_from_panel,
            inputs=[resources_state, delete_panel_resource_path, doc_title, doc_description, blocks_state],
            outputs=[resources_state, blocks_state, resources_display, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

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

        # Generate document handler - update to return the download button state
        async def handle_generate_and_update_download(title, description, resources, blocks, session_id):
            """Generate document and update download button."""
            json_str, content, file_path, filename = await handle_document_generation(
                title, description, resources, blocks, session_id
            )

            if file_path:
                download_update = gr.update(value=file_path, interactive=True)
            else:
                download_update = gr.update(interactive=False)

            return json_str, content, download_update

        generate_doc_btn.click(
            fn=handle_generate_and_update_download,
            inputs=[doc_title, doc_description, resources_state, blocks_state, session_state],
            outputs=[json_output, generated_content, save_doc_btn],
        )

        # Save button handler
        save_builder_btn.click(fn=save_outline, inputs=[doc_title, json_output, blocks_state], outputs=save_status)

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
                resources_display,
                import_file,  # Add import_file to outputs to clear it
                session_state,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

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
                resources_display,
                session_state,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

    return app


def main():
    """Main entry point for the Document Builder app."""
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
