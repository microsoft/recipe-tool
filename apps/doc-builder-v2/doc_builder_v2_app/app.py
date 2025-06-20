import gradio as gr
from pathlib import Path
import uuid

def add_ai_block(blocks):
    """Add an AI content block."""
    new_block = {
        'id': str(uuid.uuid4()),
        'type': 'ai',
        'content': '',
        'resources': [],
        'collapsed': False
    }
    return blocks + [new_block]

def add_heading_block(blocks):
    """Add a heading block."""
    new_block = {
        'id': str(uuid.uuid4()),
        'type': 'heading',
        'content': 'New Heading',
        'collapsed': False
    }
    return blocks + [new_block]

def add_text_block(blocks):
    """Add a text block."""
    new_block = {
        'id': str(uuid.uuid4()),
        'type': 'text',
        'content': '',
        'resources': [],
        'collapsed': False
    }
    return blocks + [new_block]

def delete_block(blocks, block_id):
    """Delete a block by its ID."""
    return [block for block in blocks if block['id'] != block_id]

def update_block_content(blocks, block_id, content):
    """Update the content of a specific block."""
    for block in blocks:
        if block['id'] == block_id:
            block['content'] = content
            break
    return blocks

def toggle_block_collapse(blocks, block_id):
    """Toggle the collapsed state of a specific block."""
    for block in blocks:
        if block['id'] == block_id:
            block['collapsed'] = not block.get('collapsed', False)
            break
    return blocks

def render_blocks(blocks):
    """Render blocks as HTML."""
    if not blocks:
        return "<div style='color: #999; text-align: center; padding: 20px;'>Click AI, H, or T to add content blocks</div>"
    
    html = ""
    for block in blocks:
        block_id = block['id']
        is_collapsed = block.get('collapsed', False)
        collapsed_class = 'collapsed' if is_collapsed else ''
        
        if block['type'] == 'ai':
            # Preview text for collapsed state
            preview_text = block['content'][:50] + '...' if len(block['content']) > 50 else block['content'] or 'AI content block'
            
            html += f"""
            <div class='content-block ai-block {collapsed_class}' data-id='{block_id}'>
                <div class='block-header'>
                    <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                        <span class='collapse-icon'>{'▶' if is_collapsed else '▼'}</span>
                    </button>
                    <span class='block-type-label'>AI Block</span>
                    <span class='block-preview' style='display: {"inline" if is_collapsed else "none"}'>{preview_text}</span>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                </div>
                <div class='block-content' style='display: {"none" if is_collapsed else "block"}'>
                    <textarea placeholder='AI will generate content here based on resources...' 
                              oninput='updateBlockContent("{block_id}", this.value)'
                              style='width: 100%; min-height: 150px; border: none; resize: vertical;'>{block['content']}</textarea>
                    <div class='block-resources' style='margin-top: 10px; min-height: 40px; border: 1px dashed #ccc; padding: 5px;'>
                        Drop resources here
                    </div>
                </div>
            </div>
            """
        elif block['type'] == 'heading':
            html += f"""
            <div class='content-block heading-block {collapsed_class}' data-id='{block_id}'>
                <div class='block-header'>
                    <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                        <span class='collapse-icon'>{'▶' if is_collapsed else '▼'}</span>
                    </button>
                    <span class='block-type-label'>Heading</span>
                    <span class='block-preview' style='display: {"inline" if is_collapsed else "none"}'>{block['content']}</span>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                </div>
                <div class='block-content' style='display: {"none" if is_collapsed else "block"}'>
                    <input type='text' value='{block['content']}' 
                           oninput='updateBlockContent("{block_id}", this.value)'
                           style='width: 100%; font-size: 18px; font-weight: bold; border: none;'/>
                </div>
            </div>
            """
        elif block['type'] == 'text':
            # Preview text for collapsed state
            preview_text = block['content'][:50] + '...' if len(block['content']) > 50 else block['content'] or 'Text block'
            
            html += f"""
            <div class='content-block text-block {collapsed_class}' data-id='{block_id}'>
                <div class='block-header'>
                    <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                        <span class='collapse-icon'>{'▶' if is_collapsed else '▼'}</span>
                    </button>
                    <span class='block-type-label'>Text Block</span>
                    <span class='block-preview' style='display: {"inline" if is_collapsed else "none"}'>{preview_text}</span>
                    <button class='delete-btn' onclick='deleteBlock("{block_id}")'>×</button>
                </div>
                <div class='block-content' style='display: {"none" if is_collapsed else "block"}'>
                    <textarea placeholder='Enter your text here...' 
                              oninput='updateBlockContent("{block_id}", this.value)'
                              style='width: 100%; min-height: 100px; border: none; resize: vertical;'>{block['content']}</textarea>
                    <div class='block-resources' style='margin-top: 10px; min-height: 40px; border: 1px dashed #ccc; padding: 5px;'>
                        Drop resources here
                    </div>
                </div>
            </div>
            """
    
    return html

def handle_file_upload(files, current_resources):
    """Handle uploaded files and return HTML display of file names."""
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
        
        # Initialize with default blocks
        initial_blocks = [
            {
                'id': str(uuid.uuid4()),
                'type': 'heading',
                'content': 'Introduction',
                'collapsed': False
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'ai',
                'content': '',
                'resources': [],
                'collapsed': False
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'heading',
                'content': 'Details',
                'collapsed': False
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'text',
                'content': '',
                'resources': [],
                'collapsed': False
            }
        ]
        blocks_state = gr.State(initial_blocks)

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
                        "Import Builder",
                        elem_id="import-builder-btn-id",
                        variant="secondary",
                        size="sm",
                        elem_classes="import-builder-btn"
                    )
                    save_builder_btn = gr.Button(
                        "Save Builder",
                        elem_id="save-builder-btn-id",
                        variant="primary",
                        size="sm",
                        elem_classes="save-builder-btn"
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
                interactive=True
            )

            # Document description (75% width)
            doc_description = gr.Textbox(
                value="",
                placeholder="Explain what this document is about. Include specifics such as purpose, audience, style, format, etc.",
                label=None,
                show_label=False,
                elem_id="doc-description-id",
                scale=3,
                interactive=True
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
                    elem_classes="upload-resources-btn")

                file_upload = gr.File(
                    label="Upload Resources",
                    file_count="multiple",
                    file_types=["image", ".pdf", ".txt", ".md", ".doc", ".docx"],
                    elem_classes="upload-file-invisible-btn",
                    visible=False
                )

                resources_display = gr.HTML(
                    value="<p style='color: #666; font-size: 12px'>No resources uploaded yet</p>",
                    elem_classes="resources-display-area"
                )

                # Handle file uploads
                file_upload.change(
                    handle_file_upload,
                    inputs=[file_upload, resources_state],
                    outputs=[resources_state, resources_display, file_upload]
                )

            # Workspace column: AI, H, T buttons (aligned left)
            with gr.Column(scale=1, elem_classes="workspace-col"):
                # Button group container
                with gr.Group(elem_classes="square-btn-group"):
                    with gr.Row(elem_classes="square-btn-row"):
                        ai_btn = gr.Button(
                            "AI",
                            elem_classes="square-btn ai-btn",
                            size="sm"
                        )
                        h_btn = gr.Button(
                            "H",
                            elem_classes="square-btn h-btn",
                            size="sm"
                        )
                        t_btn = gr.Button(
                            "T",
                            elem_classes="square-btn t-btn",
                            size="sm"
                        )

                # Workspace panel for stacking content blocks
                with gr.Column(elem_classes="workspace-display"):
                    blocks_display = gr.HTML(
                        value=render_blocks(initial_blocks),
                        elem_classes="blocks-container"
                    )
                    
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

            # Generated document column: Generate and Save Document buttons (aligned right)
            with gr.Column(scale=1, elem_classes="generate-col"):
                with gr.Row():
                    # Add empty space to push buttons to the right
                    gr.HTML("<div style='flex: 1;'></div>")
                    generate_doc_btn = gr.Button(
                        "Generate Document",
                        elem_classes="generate-btn",
                        variant="primary",
                        size="sm"
                    )
                    save_doc_btn = gr.Button(
                        "Save Document",
                        elem_classes="save-doc-btn",
                        variant="secondary",
                        size="sm"
                    )

                # Generated document display panel
                with gr.Column(elem_classes="generate-display"):
                    generated_content = gr.Markdown(
                        value="*Click 'Generate Document' to see the generated content here*",
                        elem_classes="generated-content"
                    )
        
        # Connect button clicks to add blocks
        ai_btn.click(
            fn=add_ai_block,
            inputs=blocks_state,
            outputs=blocks_state
        ).then(
            fn=render_blocks,
            inputs=blocks_state,
            outputs=blocks_display
        )
        
        h_btn.click(
            fn=add_heading_block,
            inputs=blocks_state,
            outputs=blocks_state
        ).then(
            fn=render_blocks,
            inputs=blocks_state,
            outputs=blocks_display
        )
        
        t_btn.click(
            fn=add_text_block,
            inputs=blocks_state,
            outputs=blocks_state
        ).then(
            fn=render_blocks,
            inputs=blocks_state,
            outputs=blocks_display
        )
        
        # Delete block handler
        delete_trigger.click(
            fn=delete_block,
            inputs=[blocks_state, delete_block_id],
            outputs=blocks_state
        ).then(
            fn=render_blocks,
            inputs=blocks_state,
            outputs=blocks_display
        )
        
        # Update block content handler
        update_trigger.click(
            fn=update_block_content,
            inputs=[blocks_state, update_block_id, update_content_input],
            outputs=blocks_state
        )
        
        # Toggle collapse handler
        toggle_trigger.click(
            fn=toggle_block_collapse,
            inputs=[blocks_state, toggle_block_id],
            outputs=blocks_state
        ).then(
            fn=render_blocks,
            inputs=blocks_state,
            outputs=blocks_display
        )

    return app

def main():
    """Main entry point for the Document Builder app."""
    app = create_app()
    app.launch()

if __name__ == "__main__":
    main()