import gradio as gr
from typing import List, Dict, Any, Tuple
import uuid
import json

def initialize_blocks():
    """Initialize with one AI content block and one manual content block"""
    return [
        {
            'id': str(uuid.uuid4()),
            'type': 'ai-content-block',
            'header': '',
            'content': '',
            'position': 0
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'manual-content-block',
            'header': '',
            'content': '',
            'position': 1
        }
    ]

# CSS for styling
custom_css = """
.wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
}

.main-layout {
    display: flex;
    gap: 10px;
    width: 100%;
    max-width: 1400px;
    padding: 20px;
    position: relative;
}

.resources-panel {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    flex-shrink: 0;
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    height: 700px;
    overflow-y: auto;
    box-sizing: border-box;
}

/* Override Gradio's default column sizing */
.resources-panel.col {
    min-width: 240px !important;
    flex: 0 0 240px !important;
}

/* Target the specific Gradio column container */
.main-layout > .col:first-child {
    min-width: 240px !important;
    max-width: 240px !important;
    flex: 0 0 240px !important;
}

/* Target the page container wrapper (component 15) */
.main-layout > .col:last-child {
    flex: 1 1 auto !important;
    max-width: none !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
}

/* Ensure the page container itself is properly aligned */
.main-layout .page-container {
    margin-left: 0 !important;
}

.resources-panel h3 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 14px;
    color: #333;
}

.resources-panel h4 {
    margin-top: 15px;
    margin-bottom: 8px;
    font-size: 12px;
    color: #555;
}

.compact-file-upload {
    font-size: 12px !important;
}

.compact-file-upload .wrap {
    padding: 8px !important;
    min-height: 110px !important;
    height: 110px !important;
}

.compact-file-upload .wrap > div {
    min-height: 110px !important;
    height: 110px !important;
}

/* The main upload label */
.compact-file-upload > label {
    font-size: 12px !important;
    font-weight: normal !important;
}

/* The drop zone text */
.compact-file-upload .wrap span {
    font-size: 10px !important;
}

/* Override the center text in upload area */
.compact-file-upload .center {
    font-size: 10px !important;
}

.resource-item {
    display: flex;
    align-items: center;
    padding: 6px;
    margin-bottom: 4px;
    background-color: white;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    font-size: 11px;
    word-break: break-all;
    gap: 4px;
}

.resource-item.image {
    border-left: 3px solid #FFD670;  /* Soft yellow */
}

.resource-item.file {
    border-left: 3px solid #FF8C42;  /* Tangerine orange */
}

.page-container {
    max-width: 900px;
    height: 700px;
    margin: 0;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 40px;
    overflow-y: auto;
    overflow-x: hidden;
    box-sizing: border-box;
}

/* Hide scrollbar while keeping scroll functionality */
.page-container::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
}

.page-container {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
}

.main-container {
    max-width: 100%;
    margin: 0 auto;
    padding-bottom: 28px;  /* Extra padding at bottom */
}

.block-container {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    padding-top: 15px;
    margin-bottom: 3px;
    background-color: white;
    position: relative !important;
    height: 150px;  /* Fixed height instead of min-height */
    overflow: visible !important;
    cursor: move !important;
}

/* Visual distinction for AI content blocks */
.block-container.ai-content-block {
    border-left: 3px solid #5B9EBD;
}

/* Visual distinction for manual content blocks */
.block-container.manual-content-block {
    border-left: 3px solid #9EBD5B;
}




/* Dragula styles */
.gu-mirror {
    position: fixed !important;
    margin: 0 !important;
    z-index: 9999 !important;
    opacity: 0.8;
    transform: rotate(3deg);
}

.gu-hide {
    display: none !important;
}

.gu-unselectable {
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}

.gu-transit {
    opacity: 0.2;
}

.delete-btn {
    position: absolute !important;
    top: 10px !important;
    right: 10px !important;
    min-width: 20px !important;
    width: 20px !important;
    height: 20px !important;
    padding: 0 !important;
    z-index: 10 !important;
    border-radius: 4px !important;
    font-size: 11px !important;
    opacity: 1 !important;
}

.add-btn {
    position: absolute !important;
    bottom: 10px !important;
    min-width: 20px !important;
    height: 20px !important;
    padding: 0 2px !important;
    border-radius: 4px !important;
    font-size: 10px !important;
    opacity: 1 !important;
}

.add-ai-btn {
    right: 35px !important;  /* Position to the left of manual button */
    width: 30px !important;  /* Slightly wider for "+AI" text */
}

.add-manual-btn {
    width: 20px !important;  /* Keep manual button square */
    right: 10px !important;  /* Right-most position */
    background-color: #9EBD5B !important;
    border-color: #9EBD5B !important;
    color: white !important;
}

.add-manual-btn:hover {
    background-color: #8CAB4A !important;
    border-color: #8CAB4A !important;
}

.block-header {
    display: block !important;
    width: 100% !important;
    margin-bottom: 8px !important;
    padding-right: 50px !important;  /* Reduced padding for more typing space */
    padding-left: 0 !important;  /* Ensure no left padding */
    height: 30px !important;
}

.block-header input {
    width: 100% !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 2px 0 !important;
    padding-left: 0 !important;  /* Align with content */
    margin-left: 0 !important;
    font-family: inherit !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    height: 24px !important;
}

/* Aggressively remove ALL borders and backgrounds EXCEPT buttons */
.block-container *:not(button):not(.delete-btn):not(.add-btn),
.block-container div,
.block-container .gradio-container,
.block-container .gradio-textbox,
.block-container .gradio-column,
.block-container .gradio-row,
.block-container .wrap,
.block-container .form {
    border: none !important;
    border-top: none !important;
    border-bottom: none !important;
    border-left: none !important;
    border-right: none !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

/* Only make non-button elements transparent */
.block-container *:not(button):not(.delete-btn):not(.add-btn) {
    background: transparent !important;
}

/* Specifically target the space between textboxes */
.block-header + *,
.block-header ~ *:not(.block-content),
.gradio-column > div:not(.block-header):not(.block-content) {
    border: none !important;
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Remove all margins between elements */
.block-header,
.block-header > *,
.block-header .gradio-textbox {
    margin-bottom: 0 !important;
}

.block-content,
.block-content > *,
.block-content .gradio-textbox {
    margin-top: 0 !important;
}

.block-content {
    display: block !important;
    width: 100% !important;
    padding-right: 50px !important;  /* Reduced padding for more typing space */
    padding-left: 0 !important;  /* Ensure no left padding */
    height: calc(150px - 70px);  /* Adjusted for better fit */
}

.block-content textarea {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    resize: none !important;
    background: transparent !important;
    padding: 0 !important;
    padding-left: 0 !important;  /* Align with header */
    margin-left: 0 !important;
    font-family: inherit !important;
    font-size: inherit !important;
    height: 80px !important;  /* Larger content area */
    overflow: hidden !important;
}

/* Change primary button colors to muted sea blue */
.gradio-button.primary,
.gr-button.primary,
button.primary,
[variant="primary"] {
    background-color: #5B9EBD !important;  /* Muted sea blue */
    border-color: #5B9EBD !important;
    color: white !important;
}

.gradio-button.primary:hover,
.gr-button.primary:hover,
button.primary:hover,
[variant="primary"]:hover {
    background-color: #4A8CAB !important;  /* Slightly darker on hover */
    border-color: #4A8CAB !important;
}
"""

MAX_BLOCKS = 20  # Maximum number of blocks to pre-create

# JavaScript for Dragula
custom_js = """
<script src='https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.js'></script>
<link href='https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.css' rel='stylesheet'>
<script>
let drake = null;
let originalOrder = [];
let autoScrollInterval = null;

function getVisibleBlocks() {
    const container = document.querySelector('.main-container');
    if (!container) return [];
    
    const visibleBlocks = [];
    const children = Array.from(container.children);
    
    children.forEach((child, index) => {
        if (child.style.display !== 'none' && !child.style.display.includes('none')) {
            visibleBlocks.push({element: child, originalIndex: index});
        }
    });
    
    return visibleBlocks;
}

// Auto-scroll functionality
function startAutoScroll(pageContainer, direction, speed = 5) {
    stopAutoScroll();
    autoScrollInterval = setInterval(() => {
        pageContainer.scrollTop += direction * speed;
    }, 20);
}

function stopAutoScroll() {
    if (autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
    }
}

function handleDragAutoScroll(e) {
    const pageContainer = document.querySelector('.page-container');
    if (!pageContainer) return;
    
    const rect = pageContainer.getBoundingClientRect();
    const scrollMargin = 50; // Distance from edge to trigger scroll
    const mouseY = e.clientY;
    
    // Check if mouse is near top or bottom of page container
    if (mouseY < rect.top + scrollMargin) {
        // Scroll up
        const speed = Math.max(1, (scrollMargin - (mouseY - rect.top)) / 10);
        startAutoScroll(pageContainer, -1, speed);
    } else if (mouseY > rect.bottom - scrollMargin) {
        // Scroll down
        const speed = Math.max(1, (scrollMargin - (rect.bottom - mouseY)) / 10);
        startAutoScroll(pageContainer, 1, speed);
    } else {
        // Stop scrolling if not near edges
        stopAutoScroll();
    }
}

function initializeDragula() {
    console.log('Initializing Dragula...');
    
    // Check if dragula is loaded
    if (typeof dragula === 'undefined') {
        console.log('Dragula not loaded yet, retrying...');
        setTimeout(initializeDragula, 500);
        return;
    }
    
    const container = document.querySelector('.main-container');
    if (!container) {
        console.log('Container not found, retrying...');
        setTimeout(initializeDragula, 100);
        return;
    }
    
    // Destroy existing drake if it exists
    if (drake) {
        console.log('Destroying existing drake');
        drake.destroy();
    }
    
    // Debug: log what we find
    console.log('Container children:', container.children.length);
    console.log('First few children:', Array.from(container.children).slice(0, 3));
    
    // Create dragula instance
    drake = dragula([container], {
        moves: function (el, source, handle, sibling) {
            console.log('Checking if can move:', el);
            console.log('Element classes:', el.className);
            console.log('Element display:', el.style.display);
            
            // Check if this is a visible block wrapper (Gradio Group)
            const isVisible = el.style.display !== 'none' && !el.style.display;
            
            // The element might be the Gradio wrapper, check if it contains our block
            // or if the handle is within a block-container
            const isBlockWrapper = handle.closest('.block-container') !== null;
            
            console.log('Is visible:', isVisible, 'Is block wrapper:', isBlockWrapper);
            return isVisible && isBlockWrapper;
        },
        accepts: function (el, target, source, sibling) {
            return true;
        },
        invalid: function (el, handle) {
            // Don't drag if clicking on buttons or textareas
            const isButton = handle.tagName === 'BUTTON' || handle.closest('button');
            const isTextarea = handle.tagName === 'TEXTAREA' || handle.closest('textarea');
            if (isButton || isTextarea) {
                console.log('Invalid handle - button or textarea');
                return true;
            }
            return false;
        },
        mirrorContainer: document.body
    });
    
    console.log('Dragula initialized successfully');
    
    // Handle drag start
    drake.on('drag', function(el, source) {
        console.log('Drag started');
        // Store original order
        originalOrder = getVisibleBlocks().map(b => b.originalIndex);
        console.log('Original order:', originalOrder);
        
        // Add mousemove listener for auto-scroll
        document.addEventListener('mousemove', handleDragAutoScroll);
    });
    
    // Handle drag end (whether dropped or cancelled)
    drake.on('dragend', function(el) {
        console.log('Drag ended');
        // Remove mousemove listener and stop any scrolling
        document.removeEventListener('mousemove', handleDragAutoScroll);
        stopAutoScroll();
    });
    
    // Handle drop
    drake.on('drop', function(el, target, source, sibling) {
        console.log('Block dropped');
        
        // IMPORTANT: Cancel the drop to revert DOM changes
        // We'll handle the reorder through Gradio instead
        drake.cancel(true);
        
        // Get the current visible blocks in their ORIGINAL order
        const visibleBlocks = getVisibleBlocks();
        
        // Find where the block was and where it was trying to go
        let fromIdx = -1;
        let toIdx = -1;
        
        // Find the dragged element's original position
        for (let i = 0; i < visibleBlocks.length; i++) {
            if (visibleBlocks[i].element === el) {
                fromIdx = i;
                break;
            }
        }
        
        // Find where it would have been inserted
        if (sibling) {
            // Dropped before a sibling
            for (let i = 0; i < visibleBlocks.length; i++) {
                if (visibleBlocks[i].element === sibling) {
                    toIdx = i;
                    break;
                }
            }
        } else {
            // Dropped at the end
            toIdx = visibleBlocks.length - 1;
        }
        
        // Adjust toIdx if moving down
        if (fromIdx < toIdx) {
            toIdx--;
        }
        
        if (fromIdx !== -1 && toIdx !== -1 && fromIdx !== toIdx) {
            console.log('Moving block from', fromIdx, 'to', toIdx);
            
            // Trigger reorder in Gradio
            const reorderBtn = document.getElementById('reorder-trigger');
            const orderInput = document.getElementById('reorder-indices');
            
            if (reorderBtn && orderInput) {
                const textarea = orderInput.querySelector('textarea');
                if (textarea) {
                    textarea.value = JSON.stringify({
                        from: fromIdx,
                        to: toIdx
                    });
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    setTimeout(() => {
                        reorderBtn.click();
                    }, 50);
                }
            }
        }
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeDragula, 1000);
});

// Reinitialize when Gradio updates
const observer = new MutationObserver(function(mutations) {
    const needsReinit = mutations.some(mutation => {
        return mutation.type === 'attributes' && 
               mutation.attributeName === 'style' &&
               mutation.target.querySelector && 
               mutation.target.querySelector('.block-container');
    });
    
    if (needsReinit) {
        setTimeout(initializeDragula, 200);
    }
});

if (document.body) {
    observer.observe(document.body, {
        attributes: true,
        subtree: true,
        attributeFilter: ['style']
    });
}
</script>
"""

def create_interface():
    with gr.Blocks(title="Document Constructor", css=custom_css, head=custom_js) as app:
        gr.Markdown("# Document Constructor")
        gr.Markdown("Create and organize your document with reorderable text blocks. Drag blocks to reorder them.")
        
        # Initialize blocks
        initial_blocks = initialize_blocks()
        
        # State to track blocks and resources
        blocks_state = gr.State(initial_blocks)
        resources_state = gr.State([])
        
        # Hidden components for drag-drop communication
        with gr.Row(visible=False):
            reorder_indices = gr.Textbox(elem_id="reorder-indices", visible=False)
            reorder_trigger = gr.Button("Reorder", elem_id="reorder-trigger", visible=False)
        
        # Create wrapper for proper centering
        with gr.Column(elem_classes="wrapper"):
            # Main layout with resources panel and page container
            with gr.Row(elem_classes="main-layout"):
                # Resources panel
                with gr.Column(elem_classes="resources-panel"):
                    
                    # File upload
                    file_upload = gr.File(
                        label="Upload Files/Images",
                        file_count="multiple",
                        file_types=["image", ".pdf", ".txt", ".md", ".doc", ".docx"],
                        type="filepath",
                        elem_classes="compact-file-upload"
                    )
                    
                    # Resources display
                    gr.Markdown("#### Uploaded Resources")
                    resources_display = gr.HTML(
                        value="<p style='color: #666; font-size: 12px;'>No resources uploaded yet</p>"
                    )
            
                # Create all block components (hidden by default)
                block_components = []
                
                # Page container
                with gr.Column(elem_classes="page-container"):
                    with gr.Column(elem_classes="main-container"):
                        for i in range(MAX_BLOCKS):
                            # Set initial visibility and class for first two blocks
                            initial_visible = i < 2
                            initial_class = "block-container"
                            if i == 0:
                                initial_class += " ai-content-block"
                            elif i == 1:
                                initial_class += " manual-content-block"
                            
                            with gr.Group(visible=initial_visible, elem_classes=initial_class) as block_group:
                                # Use a Column to ensure vertical stacking
                                with gr.Column():
                                    # Header textbox - placeholder will be set dynamically
                                    header_input = gr.Textbox(
                                        value="",
                                        placeholder="Header (optional)",
                                        show_label=False,
                                        elem_classes="block-header",
                                        max_lines=1
                                    )
                                    
                                    # Content text area - placeholder will be set dynamically
                                    text_area = gr.Textbox(
                                        value="",
                                        placeholder="Type your content here...",
                                        lines=3,
                                        max_lines=10,
                                        show_label=False,
                                        elem_classes="block-content"
                                    )
                                
                                # Then the buttons
                                delete_btn = gr.Button(
                                    "x", 
                                    size="sm", 
                                    elem_classes="delete-btn",
                                    interactive=(i != 0),
                                    visible=(i == 0)
                                )
                                
                                # Add buttons for both types
                                add_ai_btn = gr.Button("+AI", size="sm", elem_classes="add-btn add-ai-btn", variant="primary")
                                add_manual_btn = gr.Button("+", size="sm", elem_classes="add-btn add-manual-btn")
                            
                            block_components.append({
                                'group': block_group,
                                'header': header_input,
                                'text': text_area,
                                'add_ai': add_ai_btn,
                                'add_manual': add_manual_btn,
                                'delete': delete_btn,
                                'index': i
                            })
        
        def update_ui_visibility(blocks):
            """Update which blocks are visible"""
            updates = []
            
            for i, comp in enumerate(block_components):
                if i < len(blocks):
                    # This block should be visible
                    # Set placeholders and CSS class based on block type
                    block_type = blocks[i].get('type', 'ai-content-block')
                    header_placeholder = "Instruction for heading (optional)" if block_type == 'ai-content-block' else "Heading (optional)"
                    content_placeholder = "Type your instruction for content here..." if block_type == 'ai-content-block' else "Type your content here..."
                    elem_classes = f"block-container {block_type}"
                    
                    updates.extend([
                        gr.update(visible=True, elem_classes=elem_classes),  # group
                        gr.update(value=blocks[i].get('header', ''), placeholder=header_placeholder),  # header
                        gr.update(value=blocks[i]['content'], placeholder=content_placeholder),  # text
                        gr.update(visible=True),  # add ai button
                        gr.update(visible=True),  # add manual button
                        gr.update(visible=(len(blocks) > 1), interactive=(len(blocks) > 1))  # delete button
                    ])
                else:
                    # This block should be hidden
                    updates.extend([
                        gr.update(visible=False),  # group
                        gr.update(value=""),  # header
                        gr.update(value=""),  # text
                        gr.update(),  # add ai button
                        gr.update(),  # add manual button
                        gr.update()  # delete button
                    ])
            
            return updates
        
        def add_block_after(blocks, index, block_type):
            """Add a new block after the specified index"""
            if len(blocks) < MAX_BLOCKS:
                new_block = {
                    'id': str(uuid.uuid4()),
                    'type': block_type,
                    'header': '',
                    'content': '',
                    'position': index + 1
                }
                blocks.insert(index + 1, new_block)
            return blocks
        
        def delete_block(blocks, index):
            """Delete a block at the specified index"""
            if len(blocks) > 1 and index < len(blocks):
                blocks.pop(index)
            return blocks
        
        def update_block_header(blocks, index, header):
            """Update the header of a specific block"""
            if index < len(blocks):
                blocks[index]['header'] = header
            return blocks
        
        def update_block_content(blocks, index, content):
            """Update the content of a specific block"""
            if index < len(blocks):
                blocks[index]['content'] = content
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
            all_outputs.extend([comp['group'], comp['header'], comp['text'], comp['add_ai'], comp['add_manual'], comp['delete']])
        
        # Wire up event handlers for each block
        for i, comp in enumerate(block_components):
            # Header change handler
            comp['header'].change(
                lambda header, blocks, idx=i: update_block_header(blocks, idx, header),
                inputs=[comp['header'], blocks_state],
                outputs=[blocks_state]
            )
            
            # Text change handler
            comp['text'].change(
                lambda content, blocks, idx=i: update_block_content(blocks, idx, content),
                inputs=[comp['text'], blocks_state],
                outputs=[blocks_state]
            )
            
            # Add AI button handler
            comp['add_ai'].click(
                lambda blocks, idx=i: add_block_after(blocks, idx, 'ai-content-block'),
                inputs=[blocks_state],
                outputs=[blocks_state]
            ).then(
                update_ui_visibility,
                inputs=[blocks_state],
                outputs=all_outputs
            )
            
            # Add Manual button handler
            comp['add_manual'].click(
                lambda blocks, idx=i: add_block_after(blocks, idx, 'manual-content-block'),
                inputs=[blocks_state],
                outputs=[blocks_state]
            ).then(
                update_ui_visibility,
                inputs=[blocks_state],
                outputs=all_outputs
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
        
        # Export functionality
        gr.Markdown("---")
        export_btn = gr.Button("Export Document", variant="primary")
        export_output = gr.Textbox(label="Exported Content", lines=10, visible=False)
        
        def export_document(blocks):
            sections = []
            for block in blocks:
                if block.get('header', '').strip() or block['content'].strip():
                    section = ""
                    if block.get('header', '').strip():
                        section += f"## {block['header']}\n"
                    if block['content'].strip():
                        section += block['content']
                    sections.append(section)
            
            content = "\n\n".join(sections)
            if not content:
                content = "(No content to export)"
            return gr.update(value=content, visible=True)
        
        export_btn.click(
            export_document,
            inputs=[blocks_state],
            outputs=[export_output]
        )
        
        # Debug info
        with gr.Accordion("Debug Info", open=False):
            debug_output = gr.JSON(label="Current Blocks State")
            
            def update_debug(blocks):
                return blocks
            
            # Update debug info when blocks change
            blocks_state.change(
                update_debug,
                inputs=[blocks_state],
                outputs=[debug_output]
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
                        f'<div class="{css_class}">{icon} {resource["name"]}</div>'
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
        
    return app

def main():
    """Main entry point for the application"""
    app = create_interface()
    app.launch()

if __name__ == "__main__":
    main()