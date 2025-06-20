// Document Builder JavaScript

function uploadResource() {
    // Try multiple selectors
    const uploadBtn = document.querySelector('.upload-resources-btn')

    if (uploadBtn) {
        uploadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const fileInput = document.querySelector('input[type="file"]');

            if (fileInput) {
                fileInput.click();
            }
        });
        return true;
    }
    return false;
}

// Delete block function
function deleteBlock(blockId) {
    // Set the block ID in the hidden textbox
    const blockIdInput = document.getElementById('delete-block-id');
    if (blockIdInput) {
        // Find the textarea element and set its value
        const textarea = blockIdInput.querySelector('textarea');
        if (textarea) {
            textarea.value = blockId;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the hidden delete button
            setTimeout(() => {
                const deleteBtn = document.getElementById('delete-trigger');
                if (deleteBtn) {
                    deleteBtn.click();
                }
            }, 100);
        }
    }
}

// Update block content function
function updateBlockContent(blockId, content) {
    // Set the block ID and content in hidden inputs
    const blockIdInput = document.getElementById('update-block-id');
    const contentInput = document.getElementById('update-content-input');

    if (blockIdInput && contentInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const contentTextarea = contentInput.querySelector('textarea');

        if (blockIdTextarea && contentTextarea) {
            blockIdTextarea.value = blockId;
            contentTextarea.value = content;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            contentTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the update button
            setTimeout(() => {
                const updateBtn = document.getElementById('update-trigger');
                if (updateBtn) {
                    updateBtn.click();
                }
            }, 100);
        }
    }
}

// Toggle block collapse function
function toggleBlockCollapse(blockId, shouldFocus = false) {
    // Set the block ID in the hidden input
    const blockIdInput = document.getElementById('toggle-block-id');
    if (blockIdInput) {
        const textarea = blockIdInput.querySelector('textarea');
        if (textarea) {
            textarea.value = blockId;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Trigger the hidden toggle button
            setTimeout(() => {
                const toggleBtn = document.getElementById('toggle-trigger');
                if (toggleBtn) {
                    toggleBtn.click();
                    
                    // If we should focus, wait for the block to expand then focus
                    if (shouldFocus) {
                        setTimeout(() => {
                            const block = document.querySelector(`[data-id="${blockId}"]`);
                            if (block) {
                                const textArea = block.querySelector('textarea');
                                if (textArea) {
                                    textArea.focus();
                                    // Move cursor to end of text
                                    textArea.setSelectionRange(textArea.value.length, textArea.value.length);
                                }
                            }
                        }, 200);
                    }
                }
            }, 100);
        }
    }
}

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', uploadResource);
window.addEventListener('load', function() {
    setTimeout(uploadResource, 1000);
});

// Use MutationObserver as backup for dynamic content
const observer = new MutationObserver(function() {
    if (uploadResource()) {
        observer.disconnect();
    }
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}