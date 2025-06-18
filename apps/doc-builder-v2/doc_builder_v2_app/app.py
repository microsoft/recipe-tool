import gradio as gr
from pathlib import Path

def handle_file_upload(files):
    """Handle uploaded files and return HTML display of file names."""
    if not files:
        return "<p style='color: #666; font-size: 12px'>No resources uploaded yet</p>"
    
    file_html = "<div style='padding: 5px;'>"
    for file in files:
        file_name = Path(file.name).name
        file_html += f"""
        <div style='padding: 4px 8px; margin: 2px 0; background-color: #f5f5f5; 
                    border: 1px solid #4a9d9e; border-radius: 4px; font-size: 12px;'>
            {file_name}
        </div>
        """
    file_html += "</div>"
    return file_html

def create_app():
    """Create and return the Document Builder Gradio app."""

    # Load custom CSS
    css_path = Path(__file__).parent / "static" / "css" / "styles.css"
    with open(css_path, "r") as f:
        custom_css = f.read()

    with gr.Blocks(css=custom_css) as app:
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
                file_upload = gr.File(
                    label="Upload Resources",
                    file_count="multiple",
                    elem_classes="upload-file-btn",
                    show_label=False,
                    container=False
                )
                
                resources_display = gr.HTML(
                    value="<p style='color: #666; font-size: 12px'>No resources uploaded yet</p>",
                    elem_classes="resources-display-area"
                )
                
                # Handle file uploads
                file_upload.change(
                    fn=handle_file_upload,
                    inputs=file_upload,
                    outputs=resources_display
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
                workspace_display = gr.HTML(
                    "<div style='height: 500px; background-color: white; border-radius: 4px; padding: 10px;'>Workspace</div>",
                    elem_classes="workspace-display"
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
                generated_display = gr.HTML(
                    "<div style='height: 500px; background-color: white; border-radius: 4px; padding: 10px;'>Generated Document</div>",
                    elem_classes="generated-display"
                )

    return app

def main():
    """Main entry point for the Document Builder app."""
    app = create_app()
    app.launch()

if __name__ == "__main__":
    main()