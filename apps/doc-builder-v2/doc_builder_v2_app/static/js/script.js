// Document Builder JavaScript

function setupUploadButton() {
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

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', setupUploadButton);
window.addEventListener('load', function() {
    setTimeout(setupUploadButton, 1000);
});

// Use MutationObserver as backup for dynamic content
const observer = new MutationObserver(function() {
    if (setupUploadButton()) {
        observer.disconnect();
    }
});

if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
}