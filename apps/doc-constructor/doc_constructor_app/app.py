import gradio as gr
import uuid
import json
import os

def initialize_blocks():
    """Initialize with starter blocks"""
    return [
        {
            'id': str(uuid.uuid4()),
            'type': 'heading-block',
            'text': '',
            'resources': [],
            'position': 0
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'ai-content-block',
            'text': '',
            'resources': [],
            'position': 1
        }
    ]

# Load CSS from external file
def load_css():
    """Load CSS from external file"""
    css_path = os.path.join(os.path.dirname(__file__), 'static/css/styles.css')
    with open(css_path, 'r') as f:
        return f.read()

custom_css = load_css()

MAX_BLOCKS = 50  # Maximum number of blocks to pre-create

# Load JavaScript from external file
def load_js():
    """Load JavaScript from external file and wrap with necessary tags"""
    js_path = os.path.join(os.path.dirname(__file__), 'static/js/scripts.js')
    with open(js_path, 'r') as f:
        js_content = f.read()

    # Return the complete head content including external libraries and our script
    return f"""
<script src='https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.js'></script>
<link href='https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.css' rel='stylesheet'>
<script>
{js_content}
</script>
"""

custom_js = load_js()

def create_interface():
    with gr.Blocks(title="Document Builder", css=custom_css, head=custom_js) as app:
        # Top header with title and import/save buttons
        with gr.Row(elem_classes="top-header"):
            with gr.Column(scale=3):
                gr.Markdown("# Document Builder")
                gr.Markdown("Create and organize your document with reorderable text blocks. Drag blocks to reorder them.")
            with gr.Column(scale=1, elem_classes="top-right-buttons"):
                with gr.Row():
                    import_btn = gr.Button("Import Builder", variant="secondary", size="sm")
                    save_btn = gr.Button("Save Builder", variant="secondary", size="sm", elem_classes="save-builder-btn")

        # Initialize blocks
        initial_blocks = initialize_blocks()

        # State to track blocks, resources, and focused block
        blocks_state = gr.State(initial_blocks)
        resources_state = gr.State([])
        focused_block_state = gr.State(-1)

        # Hidden components for drag-drop communication and focus tracking
        with gr.Row(visible=False):
            reorder_indices = gr.Textbox(elem_id="reorder-indices", visible=False)
            reorder_trigger = gr.Button("Reorder", elem_id="reorder-trigger", visible=False)
            resource_update_data = gr.Textbox(elem_id="resource-update-data", visible=False)
            resource_update_trigger = gr.Button("Update Resource", elem_id="resource-update-trigger", visible=False)
            focused_block_index = gr.Textbox(elem_id="focused-block-index", value="-1", visible=False)

            # Hidden file upload component
            file_upload = gr.File(
                label="Upload",
                file_count="multiple",
                file_types=["image", ".pdf", ".txt", ".md", ".doc", ".docx"],
                type="filepath",
                visible=False
            )

        # Create wrapper for proper centering
        with gr.Column(elem_classes="wrapper"):
            # Header section with title and instruction
            with gr.Row(elem_classes="header-section"):
                document_title = gr.Textbox(
                    label="",
                    placeholder="Enter document title",
                    value="Document Title",
                    elem_classes="title-input",
                    show_label=False,
                    scale=1
                )
                general_instruction = gr.Textbox(
                    label="",
                    placeholder="Explain what this document is about. Include specifics such as style, format, audience, references, etc.",
                    value="",
                    elem_classes="instruction-input",
                    show_label=False,
                    scale=1
                )

            # Main layout
            with gr.Row(elem_classes="main-layout"):
                # Create all block components (hidden by default)
                block_components = []

                # Column to contain all center content
                with gr.Column(elem_classes="center-content-wrapper"):
                    # Button row above panels
                    with gr.Row(elem_classes="action-buttons-row"):
                        # Upload Resources button
                        upload_resources_btn = gr.Button("Upload Resources", variant="secondary", elem_classes="upload-resources-btn")

                        # Add content buttons
                        add_ai_content_btn = gr.Button("AI", elem_classes="add-content-btn blue-btn")
                        add_heading_btn = gr.Button("H", elem_classes="add-content-btn green-btn")
                        add_content_btn = gr.Button("T", elem_classes="add-content-btn green-btn")

                        # Spacer
                        gr.HTML('<div style="flex: 1;"></div>')

                        # Generate button on the right
                        generate_btn = gr.Button("Generate Document", variant="primary", elem_classes="generate-btn")
                        save_doc_btn = gr.Button("Save Document", variant="secondary", elem_classes="save-doc-btn")

                    # Row containing resources, page panel and generated panel
                    with gr.Row(elem_classes="panels-row"):
                        # Resources display
                        with gr.Column(elem_classes="resources-display-column"):
                            resources_display = gr.HTML(
                                value="<p style='color: #666; font-size: 12px;'>No resources uploaded yet</p>",
                                elem_classes="resources-display-area"
                            )

                        # Page panel
                        with gr.Column(elem_classes="page-panel"):
                            with gr.Column(elem_classes="main-container"):
                                for i in range(MAX_BLOCKS):
                                    # Set initial visibility and class for first two blocks
                                    initial_visible = i < 2
                                    initial_class = "block-container"
                                    if i == 0:
                                        initial_class += " heading-block"
                                    elif i == 1:
                                        initial_class += " ai-content-block"

                                    with gr.Group(visible=initial_visible, elem_classes=initial_class) as block_group:
                                        # Use a Column to ensure vertical stacking
                                        with gr.Column():
                                            # Content text area - placeholder will be set dynamically
                                            text = gr.Textbox(
                                                value="",
                                                placeholder="",
                                                lines=8,
                                                max_lines=8,
                                                show_label=False,
                                                elem_classes="block-text"
                                            )

                                            # Resources drop zone
                                            resources = gr.HTML(
                                                value='<div class="resources-drop-zone">Drop resources here</div>',
                                                elem_classes="block-resources"
                                            )

                                        # Then the delete button only
                                        delete_btn = gr.Button(
                                            "x",
                                            size="sm",
                                            elem_classes="delete-btn",
                                            interactive=(i != 0),
                                            visible=(i == 0)
                                        )

                                    block_components.append({
                                        'group': block_group,
                                        'text': text,
                                        'resources': resources,
                                        'delete': delete_btn,
                                        'index': i
                                    })

                        # Generated document panel
                        with gr.Column(elem_classes="generated-panel"):
                            generated_content = gr.Markdown(
                                value="*Click 'Generate Document' to see the generated content here*",
                                elem_classes="generated-content"
                            )

        def update_ui_visibility(blocks):
            """Update which blocks are visible"""
            updates = []

            for i, comp in enumerate(block_components):
                if i < len(blocks):
                    # This block should be visible
                    # Set placeholders and CSS class based on block type
                    block_type = blocks[i].get('type')

                    # Set placeholders based on block type
                    if block_type == 'ai-content-block':
                        text_placeholder = "Type your AI content instruction here..."
                        show_text = True
                        show_resources = True
                    elif block_type == 'heading-block':
                        text_placeholder = "Heading"
                        show_text = True
                        show_resources = False
                    else:  # content-block
                        text_placeholder = "Text"
                        show_text = True
                        show_resources = False

                    elem_classes = f"block-container {block_type}"

                    # Generate resources HTML
                    resources_html = '<div class="resources-drop-zone" data-block-index="' + str(i) + '">'
                    if blocks[i].get('resources', []):
                        for resource in blocks[i]['resources']:
                            icon = "🖼️" if resource['type'] == 'image' else "📄"
                            resources_html += f'<span class="dropped-resource">{icon} {resource["name"]}</span>'
                    else:
                        resources_html += 'Drop resources here'
                    resources_html += '</div>'

                    # Check if this is a permanent block
                    is_permanent = blocks[i].get('permanent', False)

                    updates.extend([
                        gr.update(visible=True, elem_classes=elem_classes),  # group
                        gr.update(value=blocks[i].get('text'), placeholder=text_placeholder, visible=show_text),  # text
                        gr.update(value=resources_html, visible=show_resources),  # resources
                        gr.update(visible=(not is_permanent and len(blocks) > 1), interactive=(not is_permanent and len(blocks) > 1))  # delete button
                    ])
                else:
                    # This block should be hidden
                    updates.extend([
                        gr.update(visible=False),  # group
                        gr.update(value=""),  # text
                        gr.update(value=""),  # resources
                        gr.update()  # delete button
                    ])

            return updates

        def add_block_after(blocks, index, block_type):
            """Add a new block after the specified index"""
            if len(blocks) < MAX_BLOCKS:
                # If index is -1 or None, add at the end
                insert_index = len(blocks) if index == -1 or index is None else index + 1

                new_block = {
                    'id': str(uuid.uuid4()),
                    'type': block_type,
                    'text': '',
                    'resources': [],
                    'position': insert_index
                }
                blocks.insert(insert_index, new_block)

                # Update positions for all blocks after the insertion
                for i in range(insert_index + 1, len(blocks)):
                    blocks[i]['position'] = i
            return blocks

        def delete_block(blocks, index):
            """Delete a block at the specified index"""
            if len(blocks) > 1 and index < len(blocks):
                # Don't delete permanent blocks
                if not blocks[index].get('permanent', False):
                    blocks.pop(index)
            return blocks

        def update_block_text(blocks, index, text):
            """Update the text of a specific block"""
            if index < len(blocks):
                blocks[index]['text'] = text
            return blocks

        def update_block_resources(blocks, resource_update_json):
            """Update resources for a specific block"""
            try:
                if not resource_update_json:
                    return blocks

                update_data = json.loads(resource_update_json)
                block_index = update_data.get('blockIndex')
                resource = update_data.get('resource')

                if block_index is not None and block_index < len(blocks) and resource:
                    if 'resources' not in blocks[block_index]:
                        blocks[block_index]['resources'] = []
                    blocks[block_index]['resources'].append(resource)

                return blocks
            except Exception as e:
                print(f"Resource update error: {e}")
                return blocks

        def reorder_blocks(blocks, move_info_json):
            """Reorder blocks based on drag-drop"""
            try:
                if not move_info_json:
                    return blocks

                move_info = json.loads(move_info_json)
                from_idx = move_info.get('from')
                to_idx = move_info.get('to')

                if from_idx is None or to_idx is None or from_idx == to_idx:
                    return blocks

                # Create a copy of blocks
                new_blocks = blocks.copy()

                # Remove the block from its current position
                moved_block = new_blocks.pop(from_idx)

                # Insert at new position
                new_blocks.insert(to_idx, moved_block)

                return new_blocks
            except Exception as e:
                print(f"Reorder error: {e}")
                return blocks

        # Collect all outputs for visibility updates
        all_outputs = []
        for comp in block_components:
            all_outputs.extend([comp['group'], comp['text'], comp['resources'], comp['delete']])

        # Wire up event handlers for each block
        for i, comp in enumerate(block_components):
            # text change handler
            comp['text'].change(
                lambda text, blocks, idx=i: update_block_text(blocks, idx, text),
                inputs=[comp['text'], blocks_state],
                outputs=[blocks_state]
            )

            # Delete button handler
            comp['delete'].click(
                lambda blocks, idx=i: delete_block(blocks, idx),
                inputs=[blocks_state],
                outputs=[blocks_state]
            ).then(
                update_ui_visibility,
                inputs=[blocks_state],
                outputs=all_outputs
            )

        # Initial UI update
        app.load(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        # Wire up the reorder trigger
        reorder_trigger.click(
            reorder_blocks,
            inputs=[blocks_state, reorder_indices],
            outputs=[blocks_state]
        ).then(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        # Wire up the resource update trigger
        resource_update_trigger.click(
            update_block_resources,
            inputs=[blocks_state, resource_update_data],
            outputs=[blocks_state]
        ).then(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        # Button click handlers (to be implemented)
        def import_design():
            # TODO: Implement import functionality
            pass

        def save_design(blocks):
            # TODO: Implement save functionality
            pass

        def generate_document(blocks, doc_title, doc_instruction):
            """Generate document JSON from blocks content"""
            if not blocks:
                return "No content to generate."

            # Initialize the document structure
            document_json = {
                "title": doc_title if doc_title else "Untitled Document",
                "general_instruction": doc_instruction if doc_instruction else "Generate a comprehensive document based on the sections below.",
                "resources": [],
                "sections": []
            }

            # Track unique resources
            resource_map = {}  # path -> resource object
            resource_counter = 1

            # Variables to track state while processing blocks
            last_heading_text = ""

            # Process blocks to build the JSON structure
            for i, block in enumerate(blocks):
                block_type = block.get('type', '')
                text = block.get('text', '').strip()
                block_resources = block.get('resources', [])

                # Process block based on type
                if block_type == 'heading-block':
                    # Store the heading text for potential use with the next AI content block
                    last_heading_text = text

                elif block_type == 'ai-content-block':
                    # Create a new section
                    section = {
                        "title": last_heading_text,  # Use the last heading text, or empty string if none
                        "prompt": text,
                        "refs": []
                    }

                    # Add resources references for this section
                    for resource in block_resources:
                        resource_key = f"resource_{resource_counter}"
                        if resource['path'] not in resource_map:
                            resource_map[resource['path']] = {
                                "key": resource_key,
                                "path": resource['path'],
                                "description": f"{resource['type'].title()} file: {resource['name']}"
                            }
                            resource_counter += 1
                        else:
                            resource_key = resource_map[resource['path']]['key']

                        if resource_key not in section['refs']:
                            section['refs'].append(resource_key)

                    document_json['sections'].append(section)

                    # Reset last_heading_text since we've used it
                    last_heading_text = ""

                elif block_type == 'content-block':
                    # Regular content blocks are treated as supplementary text
                    # They could be added to a previous section if needed, but based on the
                    # document structure, we'll skip them for now since sections are driven by AI blocks
                    pass

            # Add all unique resources to the document
            document_json['resources'] = list(resource_map.values())

            # If no general instruction was set, use a default
            if not document_json['general_instruction']:
                document_json['general_instruction'] = "Generate a comprehensive document based on the sections below."

            # Format as pretty JSON
            import json
            json_output = json.dumps(document_json, indent=2)

            # Return formatted JSON wrapped in markdown code block
            return f"```json\n{json_output}\n```"

        import_btn.click(
            import_design,
            inputs=[],
            outputs=[]
        )

        save_btn.click(
            save_design,
            inputs=[blocks_state],
            outputs=[]
        )

        generate_btn.click(
            generate_document,
            inputs=[blocks_state, document_title, general_instruction],
            outputs=[generated_content]
        )

        # File upload handler
        def handle_file_upload(files, current_resources):
            """Handle file uploads and update resources state."""
            if not files:
                return current_resources, gr.update(), None

            # Add new files to resources
            new_resources = current_resources.copy() if current_resources else []

            for file_path in files:
                if file_path and file_path not in [r['path'] for r in new_resources]:
                    import os
                    file_name = os.path.basename(file_path)
                    file_ext = os.path.splitext(file_name)[1].lower()

                    # Determine if it's an image
                    is_image = file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']

                    new_resources.append({
                        'path': file_path,
                        'name': file_name,
                        'type': 'image' if is_image else 'file'
                    })

            # Generate HTML for resources display
            if new_resources:
                html_items = []
                for resource in new_resources:
                    icon = "🖼️" if resource['type'] == 'image' else "📄"
                    css_class = f"resource-item {resource['type']}"
                    html_items.append(
                        f'<div class="{css_class}" draggable="true" data-resource-name="{resource["name"]}" data-resource-type="{resource["type"]}" data-resource-path="{resource["path"]}">{icon} {resource["name"]}</div>'
                    )
                resources_html = '\n'.join(html_items)
            else:
                resources_html = "<p style='color: #666; font-size: 12px;'>No resources uploaded yet</p>"

            return new_resources, gr.update(value=resources_html), None  # Return None to clear file upload

        # Wire up file upload
        file_upload.change(
            handle_file_upload,
            inputs=[file_upload, resources_state],
            outputs=[resources_state, resources_display, file_upload]
        )

        # Function to add block at the end
        def add_block_at_end(blocks, block_type):
            """Add a new block at the end of the document"""
            if len(blocks) < MAX_BLOCKS:
                new_block = {
                    'id': str(uuid.uuid4()),
                    'type': block_type,
                    'text': '',
                    'resources': [],
                    'position': len(blocks)
                }
                blocks.append(new_block)
            return blocks

        def add_block_at_focused_position(blocks, focused_index, block_type, focused_idx_str):
            """Add a new block after the focused block, or at the end if no focus"""
            # Try to use the textbox value directly as it's more current
            try:
                idx_from_textbox = int(focused_idx_str)
                print(f"Focused index from textbox: {idx_from_textbox}")
            except:
                idx_from_textbox = -1

            # Use the most recent value
            idx = idx_from_textbox if idx_from_textbox >= 0 else focused_index

            print(f"Adding block - Final index: {idx}, Block type: {block_type}, Total blocks: {len(blocks)}")

            if isinstance(idx, int) and idx >= 0 and idx < len(blocks):
                # Add after the focused block
                print(f"Adding after block at index {idx}")
                return add_block_after(blocks, idx, block_type), idx
            else:
                # Add at the end
                print(f"Index out of range or invalid, adding at end")
                return add_block_at_end(blocks, block_type), -1

        # Function to update focused block state
        def update_focused_block(focused_idx_str):
            """Update the focused block state from the hidden textbox"""
            try:
                idx = int(focused_idx_str)
                print(f"Updating focused block state to: {idx}")
                return idx
            except:
                print(f"Failed to parse focused index: {focused_idx_str}")
                return -1

        # Wire up focus tracking with both change and input events
        focused_block_index.change(
            update_focused_block,
            inputs=[focused_block_index],
            outputs=[focused_block_state]
        )

        focused_block_index.input(
            update_focused_block,
            inputs=[focused_block_index],
            outputs=[focused_block_state]
        )

        # Wire up the new add content buttons to use focused position
        add_content_btn.click(
            lambda blocks, focused_idx, textbox_val: add_block_at_focused_position(blocks, focused_idx, 'content-block', textbox_val),
            inputs=[blocks_state, focused_block_state, focused_block_index],
            outputs=[blocks_state, focused_block_state]
        ).then(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        add_ai_content_btn.click(
            lambda blocks, focused_idx, textbox_val: add_block_at_focused_position(blocks, focused_idx, 'ai-content-block', textbox_val),
            inputs=[blocks_state, focused_block_state, focused_block_index],
            outputs=[blocks_state, focused_block_state]
        ).then(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        add_heading_btn.click(
            lambda blocks, focused_idx, textbox_val: add_block_at_focused_position(blocks, focused_idx, 'heading-block', textbox_val),
            inputs=[blocks_state, focused_block_state, focused_block_index],
            outputs=[blocks_state, focused_block_state]
        ).then(
            update_ui_visibility,
            inputs=[blocks_state],
            outputs=all_outputs
        )

        # Add JavaScript to make upload buttons work
        app.load(
            None,
            None,
            None,
            js="""
            function() {
                // Function to trigger hidden file upload
                function triggerFileUpload() {
                    const fileInput = document.querySelector('input[type="file"][multiple]');
                    if (fileInput) {
                        fileInput.click();
                    }
                }

                // Add click handler to Upload Resources button
                setTimeout(() => {
                    // Upload Resources button
                    const uploadResourcesBtn = document.querySelector('.upload-resources-btn');
                    if (uploadResourcesBtn) {
                        uploadResourcesBtn.addEventListener('click', triggerFileUpload);
                    }
                }, 1000);
            }
            """
        )


    return app

def main():
    """Main entry point for the application"""
    app = create_interface()
    app.launch()

if __name__ == "__main__":
    main()