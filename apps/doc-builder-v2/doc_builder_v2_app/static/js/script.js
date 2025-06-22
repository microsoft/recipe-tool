// Document Builder JavaScript

function setupUploadResource() {
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

// Update block heading function
function updateBlockHeading(blockId, heading) {
    // Set the block ID and heading in hidden inputs
    const blockIdInput = document.getElementById('update-heading-block-id');
    const headingInput = document.getElementById('update-heading-input');

    if (blockIdInput && headingInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const headingTextarea = headingInput.querySelector('textarea');

        if (blockIdTextarea && headingTextarea) {
            blockIdTextarea.value = blockId;
            headingTextarea.value = heading;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            headingTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the update button
            setTimeout(() => {
                const updateBtn = document.getElementById('update-heading-trigger');
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
                                    // Ensure auto-expand is setup before focusing
                                    setupAutoExpand();
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

// Auto-expand textarea function
function autoExpandTextarea(textarea) {
    // Store current scroll position of workspace
    const workspace = document.querySelector('.workspace-display');
    
    // Store the current height before changing
    const oldHeight = textarea.offsetHeight;
    
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';

    // Set height to scrollHeight plus a small buffer
    const newHeight = textarea.scrollHeight + 2;
    textarea.style.height = newHeight + 'px';
}

// Setup auto-expand for all textareas
function setupAutoExpand() {
    // Get all textareas in the document
    const textareas = document.querySelectorAll('textarea');

    textareas.forEach(textarea => {
        // Always setup/re-setup to handle re-renders
        
        // Initial sizing
        autoExpandTextarea(textarea);
        
        // Remove existing listeners by using a named function
        if (!textarea.autoExpandHandler) {
            textarea.autoExpandHandler = function() {
                autoExpandTextarea(this);
            };
            textarea.pasteHandler = function() {
                setTimeout(() => autoExpandTextarea(this), 10);
            };
            
            // Add event listeners
            textarea.addEventListener('input', textarea.autoExpandHandler);
            textarea.addEventListener('paste', textarea.pasteHandler);
        }
    });
}

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', function() {
    setupUploadResource();
    setupAutoExpand();
});

window.addEventListener('load', function() {
    setTimeout(setupUploadResource, 1000);
    setTimeout(setupAutoExpand, 100);
});

// Use MutationObserver for dynamic content
let debounceTimer;
const observer = new MutationObserver(function(mutations) {
    // Check if any mutations are relevant (new nodes added)
    let hasRelevantChanges = false;
    
    for (const mutation of mutations) {
        // Only care about added nodes
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Check if any added nodes contain textareas or are blocks
            for (const node of mutation.addedNodes) {
                if (node.nodeType === 1) { // Element node
                    if (node.classList?.contains('content-block') || 
                        node.querySelector?.('textarea') ||
                        node.tagName === 'TEXTAREA') {
                        hasRelevantChanges = true;
                        break;
                    }
                }
            }
        }
    }
    
    // Only run setup if relevant changes detected
    if (hasRelevantChanges) {
        setupUploadResource();
        
        // Debounce the setupAutoExpand to avoid multiple calls
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            setupAutoExpand();
        }, 100);
    }
});

if (document.body) {
    observer.observe(document.body, { 
        childList: true, 
        subtree: true
        // Removed attributes observation - we don't need it
    });
}

// Also add a global function that can be called
window.setupAutoExpand = setupAutoExpand;