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