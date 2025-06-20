import gradio as gr
from pathlib import Path

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
        # State to track resources
        resources_state = gr.State([])

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
                    # Placeholder blocks - you can add more content blocks here
                    gr.Textbox(
                        value="Content Block 1",
                        label=None,
                        elem_classes="content-block"
                    )
                    gr.Textbox(
                        value="Content Block 2",
                        label=None,
                        elem_classes="content-block"
                    )

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

    return app

def main():
    """Main entry point for the Document Builder app."""
    app = create_app()
    app.launch()

if __name__ == "__main__":
    main()