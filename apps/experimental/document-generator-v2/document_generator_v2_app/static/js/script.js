// Document Builder JavaScript



function refresh() {
    const url = new URL(window.location);
    elements = document.getElementsByClassName("dark")
    if (elements.length != 0) {
        console.log(elements)
        elements[0].classList.remove("dark");
        console.log('Refreshing in light mode');
    }
}


// Toggle debug panel visibility
function toggleDebugPanel() {
    const content = document.getElementById('debug-panel-content');
    const icon = document.getElementById('debug-collapse-icon');

    if (content) {
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
            if (icon) {
                icon.textContent = '⌵';
                icon.style.transform = 'rotate(180deg)';  // Rotate down chevron to point up
            }
        } else {
            content.style.display = 'none';
            if (icon) {
                icon.textContent = '⌵';
                icon.style.transform = 'rotate(0deg)';  // Normal down chevron
            }
        }
    }
}

// No longer needed - using Gradio's native file upload component

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
function toggleBlockCollapse(blockId) {
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
                }
            }, 100);
        }
    }
}

// Expand block if collapsed when heading is focused
function expandBlockOnHeadingFocus(blockId) {
    // Find the block element using data-id attribute
    const block = document.querySelector(`[data-id="${blockId}"]`);
    if (block && block.classList.contains('collapsed')) {
        // Store reference to the heading input and cursor position
        const headingInput = block.querySelector('.block-heading-inline');
        const cursorPosition = headingInput ? headingInput.selectionStart : 0;
        
        // If the block is collapsed, expand it
        toggleBlockCollapse(blockId);
        
        // Use a longer delay and multiple attempts to ensure focus is restored
        let attempts = 0;
        const maxAttempts = 5;
        
        const restoreFocus = () => {
            attempts++;
            const updatedBlock = document.querySelector(`[data-id="${blockId}"]`);
            const updatedHeading = updatedBlock ? updatedBlock.querySelector('.block-heading-inline') : null;
            
            if (updatedHeading && !updatedBlock.classList.contains('collapsed')) {
                // Block has expanded, restore focus
                updatedHeading.focus();
                // Restore cursor position
                updatedHeading.setSelectionRange(cursorPosition, cursorPosition);
            } else if (attempts < maxAttempts) {
                // Try again after a short delay
                setTimeout(restoreFocus, 100);
            }
        };
        
        // Start trying after initial delay
        setTimeout(restoreFocus, 200);
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

    // Check if this is the description textarea
    const isDescription = textarea.closest('#doc-description-id');
    if (isDescription) {
        // Calculate max height for 10 lines
        const lineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight);
        const padding = parseInt(window.getComputedStyle(textarea).paddingTop) +
                       parseInt(window.getComputedStyle(textarea).paddingBottom);
        const tenLinesHeight = (lineHeight * 10) + padding;

        // First check if content would exceed 10 lines (show scrollbar when starting 11th line)
        const wouldExceedTenLines = newHeight > tenLinesHeight;

        // Set max-height to exactly 10 lines
        textarea.style.maxHeight = tenLinesHeight + 'px';

        // Set height to min of scrollHeight or 10 lines height
        textarea.style.height = Math.min(newHeight, tenLinesHeight) + 'px';

        // Add scrollable class if content exceeds 10 lines
        if (wouldExceedTenLines) {
            textarea.classList.add('scrollable');
        } else {
            textarea.classList.remove('scrollable');
        }
    } else {
        textarea.style.height = newHeight + 'px';
    }
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

    // Special handling for the document description to ensure proper initial height
    const docDescription = document.querySelector('#doc-description-id textarea');
    if (docDescription) {
        // Set minimum height for 2 lines
        const lineHeight = parseInt(window.getComputedStyle(docDescription).lineHeight);
        const padding = parseInt(window.getComputedStyle(docDescription).paddingTop) +
                       parseInt(window.getComputedStyle(docDescription).paddingBottom);
        const minHeight = (lineHeight * 2) + padding;
        docDescription.style.minHeight = minHeight + 'px';
        autoExpandTextarea(docDescription);
    }
}

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', function () {
    refresh();
    // Upload resource setup no longer needed - using Gradio's native component
    setupAutoExpand();
});

window.addEventListener('load', function() {
    // Upload resource setup no longer needed - using Gradio's native component
    setTimeout(setupAutoExpand, 100);
    // Also setup drag and drop on window load
    setTimeout(setupDragAndDrop, 200);
    setTimeout(setupFileUploadDragAndDrop, 250);
    // Setup description toggle button
    setTimeout(setupDescriptionToggle, 150);
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
                        node.classList?.contains('resource-item') ||
                        node.classList?.contains('block-resources') ||
                        node.querySelector?.('textarea') ||
                        node.querySelector?.('.resource-item') ||
                        node.querySelector?.('.block-resources') ||
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
        refresh();
        // Upload resource setup no longer needed - using Gradio's native component
        setupImportButton();

        // Delay drag and drop setup slightly to ensure DOM is ready
        setTimeout(() => {
            setupDragAndDrop();
            setupFileUploadDragAndDrop();
        }, 50);

        // Debounce the setupAutoExpand to avoid multiple calls
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            setupAutoExpand();
            setupDescriptionToggle();
            setupExampleSelection();
            setupResourceDescriptions();
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

// Update block indent function
function updateBlockIndent(blockId, direction) {
    // Set focused block when indenting
    setFocusedBlock(blockId);

    // Set the block ID and direction in hidden inputs
    const blockIdInput = document.getElementById('indent-block-id');
    const directionInput = document.getElementById('indent-direction');

    if (blockIdInput && directionInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const directionTextarea = directionInput.querySelector('textarea');

        if (blockIdTextarea && directionTextarea) {
            blockIdTextarea.value = blockId;
            directionTextarea.value = direction;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            directionTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the update button
            setTimeout(() => {
                const indentBtn = document.getElementById('indent-trigger');
                if (indentBtn) {
                    indentBtn.click();
                }
            }, 100);
        }
    }
}

// Set focused block function
function setFocusedBlock(blockId, skipRender = false) {
    const focusIdInput = document.getElementById('focus-block-id');
    if (focusIdInput) {
        const textarea = focusIdInput.querySelector('textarea');
        if (textarea) {
            textarea.value = blockId;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Only trigger render if not skipping
            if (!skipRender) {
                setTimeout(() => {
                    const focusBtn = document.getElementById('focus-trigger');
                    if (focusBtn) {
                        focusBtn.click();
                    }
                }, 100);
            }
        }
    }
}


// Add block after function - adds same type as the block being clicked
function addBlockAfter(blockId) {
    // Get the block element to determine its type
    const blockElement = document.querySelector(`[data-id="${blockId}"]`);
    if (blockElement) {
        // Determine type based on class
        let blockType = 'ai'; // default
        if (blockElement.classList.contains('text-block')) {
            blockType = 'text';
        }

        // Set the values in hidden inputs
        const blockIdInput = document.getElementById('add-after-block-id');
        const typeInput = document.getElementById('add-after-type');

        if (blockIdInput && typeInput) {
            const blockIdTextarea = blockIdInput.querySelector('textarea');
            const typeTextarea = typeInput.querySelector('textarea');

            if (blockIdTextarea && typeTextarea) {
                blockIdTextarea.value = blockId;
                typeTextarea.value = blockType;

                // Dispatch input events
                blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                typeTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the add after button
                setTimeout(() => {
                    const addAfterBtn = document.getElementById('add-after-trigger');
                    if (addAfterBtn) {
                        addAfterBtn.click();
                    }
                }, 100);
            }
        }
    }
}

// Convert block type function
function convertBlock(blockId, toType) {
    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('convert-block-id');
    const typeInput = document.getElementById('convert-type');

    if (blockIdInput && typeInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const typeTextarea = typeInput.querySelector('textarea');

        if (blockIdTextarea && typeTextarea) {
            blockIdTextarea.value = blockId;
            typeTextarea.value = toType;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            typeTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the convert button
            setTimeout(() => {
                const convertBtn = document.getElementById('convert-trigger');
                if (convertBtn) {
                    convertBtn.click();
                }
            }, 100);
        }
    }
}

// Delete resource from panel function
function deleteResourceFromPanel(resourcePath) {
    // Set the value in hidden input
    const resourcePathInput = document.getElementById('delete-panel-resource-path');

    if (resourcePathInput) {
        const resourcePathTextarea = resourcePathInput.querySelector('textarea');

        if (resourcePathTextarea) {
            resourcePathTextarea.value = resourcePath;

            // Dispatch input event
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the delete button
            setTimeout(() => {
                const deleteBtn = document.getElementById('delete-panel-resource-trigger');
                if (deleteBtn) {
                    deleteBtn.click();
                }
            }, 100);
        }
    }
}

// Remove resource from block function
function removeBlockResource(blockId, resourcePath) {
    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('remove-resource-block-id');
    const resourcePathInput = document.getElementById('remove-resource-path');

    if (blockIdInput && resourcePathInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const resourcePathTextarea = resourcePathInput.querySelector('textarea');

        if (blockIdTextarea && resourcePathTextarea) {
            blockIdTextarea.value = blockId;
            resourcePathTextarea.value = resourcePath;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the remove button
            setTimeout(() => {
                const removeBtn = document.getElementById('remove-resource-trigger');
                if (removeBtn) {
                    removeBtn.click();
                }
            }, 100);
        }
    }
}

// Debounce timer for resource descriptions
let descriptionDebounceTimers = {};

// Update resource description function with debouncing
function updateResourceDescription(blockId, resourcePath, description) {
    // Create unique key for this input
    const timerKey = `${blockId}-${resourcePath}`;

    // Clear existing timer for this input
    if (descriptionDebounceTimers[timerKey]) {
        clearTimeout(descriptionDebounceTimers[timerKey]);
    }

    // Update all other description text boxes for the same resource immediately
    const allDescInputs = document.querySelectorAll('.resource-description');
    allDescInputs.forEach(input => {
        // Check if this input is for the same resource but different block
        if (input.getAttribute('oninput') &&
            input.getAttribute('oninput').includes(`'${resourcePath}'`) &&
            !input.getAttribute('oninput').includes(`'${blockId}'`)) {
            input.value = description;
        }
    });

    // Set new timer with 50ms delay (0.05 seconds after user stops typing)
    descriptionDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs
        const blockIdInput = document.getElementById('update-desc-block-id');
        const resourcePathInput = document.getElementById('update-desc-resource-path');
        const descTextInput = document.getElementById('update-desc-text');

        if (blockIdInput && resourcePathInput && descTextInput) {
            const blockIdTextarea = blockIdInput.querySelector('textarea');
            const resourcePathTextarea = resourcePathInput.querySelector('textarea');
            const descTextTextarea = descTextInput.querySelector('textarea');

            if (blockIdTextarea && resourcePathTextarea && descTextTextarea) {
                blockIdTextarea.value = blockId;
                resourcePathTextarea.value = resourcePath;
                descTextTextarea.value = description;

                // Dispatch input events
                blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                descTextTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-desc-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete descriptionDebounceTimers[timerKey];
    }, 50); // Wait 50ms after user stops typing
}

// Load resource content into text block
function loadResourceContent(blockId, resourcePath) {
    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('load-resource-block-id');
    const resourcePathInput = document.getElementById('load-resource-path');

    if (blockIdInput && resourcePathInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const resourcePathTextarea = resourcePathInput.querySelector('textarea');

        if (blockIdTextarea && resourcePathTextarea) {
            blockIdTextarea.value = blockId;
            resourcePathTextarea.value = resourcePath;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the load button
            setTimeout(() => {
                const loadBtn = document.getElementById('load-resource-trigger');
                if (loadBtn) {
                    loadBtn.click();
                }
            }, 100);
        }
    }
}

// Setup description expand/collapse button
function setupDescriptionToggle() {
    const container = document.querySelector('#doc-description-id');
    const textarea = container?.querySelector('textarea');

    if (!container || !textarea || container.dataset.toggleSetup) {
        return;
    }

    // Mark as setup
    container.dataset.toggleSetup = 'true';

    // Create expand/collapse button
    const button = document.createElement('button');
    button.className = 'desc-expand-btn';
    button.innerHTML = '⌵'; // Down chevron
    button.title = 'Collapse';

    // Find the input container (parent of textarea) and insert button there
    const inputContainer = textarea.parentElement;
    if (inputContainer) {
        inputContainer.style.position = 'relative'; // Ensure container is positioned
        inputContainer.appendChild(button);
    }

    // Track collapsed state and full text
    let isCollapsed = false;
    let fullText = '';

    // Function to get first two lines of text
    function getFirstTwoLines(text) {
        const lines = text.split('\n');
        // Take first two lines
        let firstTwo = lines.slice(0, 2).join('\n');

        // If the second line exists and there's more content, add ellipsis
        if (lines.length > 2 || (lines.length === 2 && lines[1].length > 50)) {
            firstTwo += '...';
        }

        return firstTwo;
    }

    // Function to check if button should be visible and handle scrollbar
    function checkButtonVisibility() {
        const lineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight);
        const padding = parseInt(window.getComputedStyle(textarea).paddingTop) +
                       parseInt(window.getComputedStyle(textarea).paddingBottom);
        const twoLinesHeight = (lineHeight * 2) + padding;

        // Show button if content exceeds 2 lines
        if (textarea.scrollHeight > twoLinesHeight && !isCollapsed) {
            button.style.display = 'block';
        } else if (!isCollapsed) {
            button.style.display = 'none';
        }

        // Add scrollable class if content exceeds 10 lines
        const tenLinesHeight = (lineHeight * 10) + padding;
        // Check if we're starting the 11th line
        if (!isCollapsed && textarea.scrollHeight > tenLinesHeight) {
            textarea.classList.add('scrollable');
        } else {
            textarea.classList.remove('scrollable');
        }
    }

    // Toggle collapse/expand
    function toggleCollapse() {
        const lineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight);
        const padding = parseInt(window.getComputedStyle(textarea).paddingTop) +
                       parseInt(window.getComputedStyle(textarea).paddingBottom);
        const twoLinesHeight = (lineHeight * 2) + padding;

        if (isCollapsed) {
            // Expand - restore full text
            textarea.value = fullText;
            textarea.style.height = 'auto';
            // Calculate 10 lines height
            const calcLineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight);
            const calcPadding = parseInt(window.getComputedStyle(textarea).paddingTop) +
                               parseInt(window.getComputedStyle(textarea).paddingBottom);
            const tenLinesHeight = (calcLineHeight * 10) + calcPadding;

            textarea.style.maxHeight = tenLinesHeight + 'px';
            textarea.style.overflow = '';  // Reset to CSS default
            container.classList.remove('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Collapse';
            isCollapsed = false;
            textarea.classList.remove('scrollable'); // Remove scrollable class first
            autoExpandTextarea(textarea);
            // Check if scrollbar is needed after expansion
            if (textarea.scrollHeight > tenLinesHeight) {
                textarea.classList.add('scrollable');
            }
            // Keep focus without moving cursor
            textarea.focus();

            // Trigger input event to update Gradio's state
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            // Collapse - save full text and show only first 2 lines
            fullText = textarea.value;
            textarea.value = getFirstTwoLines(fullText);
            textarea.style.height = twoLinesHeight + 'px';
            textarea.style.maxHeight = twoLinesHeight + 'px';
            textarea.style.overflow = 'hidden';
            container.classList.add('collapsed');
            button.innerHTML = '⌵';  // Same chevron, will rotate with CSS
            button.title = 'Expand';
            isCollapsed = true;
            textarea.classList.remove('scrollable'); // Remove scrollable class when collapsed
            // Remove focus to prevent scrolling
            textarea.blur();
        }
    }

    // Button click handler
    button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleCollapse();
    });

    // Click on collapsed textarea to expand
    textarea.addEventListener('click', (e) => {
        if (isCollapsed) {
            // Get cursor position before expanding
            const cursorPos = textarea.selectionStart;
            toggleCollapse();
            // Restore cursor position after expanding
            setTimeout(() => {
                textarea.setSelectionRange(cursorPos, cursorPos);
            }, 0);
        }
    });

    // Check on input
    textarea.addEventListener('input', () => {
        checkButtonVisibility();
        // Auto-expand if typing while collapsed
        if (isCollapsed) {
            toggleCollapse();
        }
    });

    // Initial check
    checkButtonVisibility();
}

// Also add a global function that can be called
window.setupAutoExpand = setupAutoExpand;

// Setup import button functionality
function setupImportButton() {
    const importBtn = document.getElementById('import-builder-btn-id');
    console.log('Setting up import button, found:', importBtn);

    if (importBtn) {
        // Remove any existing listeners first
        importBtn.replaceWith(importBtn.cloneNode(true));
        const newImportBtn = document.getElementById('import-builder-btn-id');

        newImportBtn.addEventListener('click', function(e) {
            console.log('Import button clicked');
            e.preventDefault();
            e.stopPropagation();

            // Find the import file input
            const importFileInput = document.querySelector('#import-file-input input[type="file"]');
            console.log('Import file input found:', importFileInput);

            if (importFileInput) {
                importFileInput.click();
            } else {
                console.error('Import file input not found');
            }
        });
    }
}

// Setup drag and drop for file upload zone
function setupFileUploadDragAndDrop() {
    const fileUploadZone = document.querySelector('.file-upload-dropzone');
    if (!fileUploadZone) return;

    // Function to replace the text
    function replaceDropText() {
        const wrapDivs = document.querySelectorAll('.file-upload-dropzone .wrap');
        wrapDivs.forEach(wrapDiv => {
            if (wrapDiv.textContent.includes('Drop File Here')) {
                wrapDiv.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                        node.textContent = node.textContent.replace('Drop File Here', 'Drop Text File Here');
                    }
                });
            }
        });
    }

    // Try to replace immediately
    replaceDropText();

    // Watch for changes in case the content is dynamically updated
    const observer = new MutationObserver((mutations) => {
        replaceDropText();
    });

    observer.observe(fileUploadZone, {
        childList: true,
        subtree: true,
        characterData: true
    });

    // Stop observing after 5 seconds to avoid performance issues
    setTimeout(() => observer.disconnect(), 5000);

    // Add drag-over class when dragging files over the upload zone
    let dragCounter = 0;

    function addDragListeners(element) {
        element.addEventListener('dragenter', function(e) {
            e.preventDefault();
            dragCounter++;
            fileUploadZone.classList.add('drag-over');
        });

        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            fileUploadZone.classList.add('drag-over');
        });

        element.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                fileUploadZone.classList.remove('drag-over');
            }
        });

        element.addEventListener('drop', function(e) {
            e.preventDefault();
            dragCounter = 0;
            fileUploadZone.classList.remove('drag-over');
        });
    }

    // Add listeners to the main zone
    addDragListeners(fileUploadZone);

    // Also add to all child elements to ensure we catch all events
    const allChildren = fileUploadZone.querySelectorAll('*');
    allChildren.forEach(child => {
        addDragListeners(child);
    });

    // Watch for new elements being added and attach listeners
    const dragObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element node
                    addDragListeners(node);
                    const newChildren = node.querySelectorAll('*');
                    newChildren.forEach(child => addDragListeners(child));
                }
            });
        });
    });

    dragObserver.observe(fileUploadZone, {
        childList: true,
        subtree: true
    });

    // Stop observing after 5 seconds
    setTimeout(() => dragObserver.disconnect(), 5000);
}

// Drag and drop functionality for resources
function setupDragAndDrop() {
    console.log('Setting up drag and drop...');

    // Setup draggable resources
    const resourceItems = document.querySelectorAll('.resource-item');
    console.log('Found resource items:', resourceItems.length);

    resourceItems.forEach(item => {
        // Remove existing listeners to avoid duplicates
        item.removeEventListener('dragstart', handleDragStart);
        item.removeEventListener('dragend', handleDragEnd);

        // Add new listeners
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });

    // Setup drop zones
    const dropZones = document.querySelectorAll('.block-resources');
    console.log('Found drop zones:', dropZones.length);

    dropZones.forEach((zone, index) => {
        // Remove existing listeners to avoid duplicates
        zone.removeEventListener('dragover', handleDragOver);
        zone.removeEventListener('drop', handleDrop);
        zone.removeEventListener('dragleave', handleDragLeave);

        // Add new listeners
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleDrop);
        zone.addEventListener('dragleave', handleDragLeave);

        // Add data attribute to help debug
        zone.setAttribute('data-drop-zone-index', index);
    });
}

let draggedResource = null;

function handleDragStart(e) {
    draggedResource = {
        name: e.target.dataset.resourceName,
        title: e.target.dataset.resourceTitle || e.target.dataset.resourceName, // Include title
        path: e.target.dataset.resourcePath,
        type: e.target.dataset.resourceType
    };
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'copy';
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');

    console.log('Drop event triggered on zone:', e.currentTarget.getAttribute('data-drop-zone-index'));

    if (!draggedResource) {
        console.error('No dragged resource found');
        return;
    }

    // Find the block ID from the parent content block
    const contentBlock = e.currentTarget.closest('.content-block');
    if (!contentBlock) {
        console.error('No parent content block found');
        return;
    }

    const blockId = contentBlock.dataset.id;
    console.log('Dropping resource on block:', blockId, draggedResource);

    // Update the block's resources
    updateBlockResources(blockId, draggedResource);

    draggedResource = null;
}

// Function to update block resources
function updateBlockResources(blockId, resource) {
    console.log('updateBlockResources called with:', blockId, resource);

    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('update-resources-block-id');
    const resourceInput = document.getElementById('update-resources-input');

    console.log('Found inputs:', !!blockIdInput, !!resourceInput);

    if (blockIdInput && resourceInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea');
        const resourceTextarea = resourceInput.querySelector('textarea');

        if (blockIdTextarea && resourceTextarea) {
            blockIdTextarea.value = blockId;
            resourceTextarea.value = JSON.stringify(resource);

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            resourceTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the update button
            setTimeout(() => {
                const updateBtn = document.getElementById('update-resources-trigger');
                if (updateBtn) {
                    updateBtn.click();
                }
            }, 100);
        }
    }
}

// Setup example selection functionality
function setupExampleSelection() {
    const exampleItems = document.querySelectorAll('.examples-dropdown-item');

    exampleItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            const exampleId = this.getAttribute('data-example');
            console.log('Selected example:', exampleId);

            // Set the example ID in hidden input
            const exampleIdInput = document.getElementById('example-id-input');
            if (exampleIdInput) {
                const textarea = exampleIdInput.querySelector('textarea');
                if (textarea) {
                    textarea.value = exampleId;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));

                    // Trigger the load example button
                    setTimeout(() => {
                        const loadExampleBtn = document.getElementById('load-example-trigger');
                        if (loadExampleBtn) {
                            loadExampleBtn.click();
                        }
                    }, 100);
                }
            }

            // Hide dropdown after selection
            const dropdown = document.getElementById('examples-dropdown-id');
            if (dropdown) {
                dropdown.style.display = 'none';
                // Re-show on next hover
                setTimeout(() => {
                    dropdown.style.removeProperty('display');
                }, 300);
            }
        });
    });
}

// Debounce timer for resource titles
let titleDebounceTimers = {};

// Update resource title function with debouncing
function updateResourceTitle(resourcePath, newTitle) {
    // Create unique key for this input
    const timerKey = resourcePath;

    // Clear existing timer for this input
    if (titleDebounceTimers[timerKey]) {
        clearTimeout(titleDebounceTimers[timerKey]);
    }

    // Update data attributes on the resource item for dragging
    const resourceItems = document.querySelectorAll('.resource-item');
    resourceItems.forEach(item => {
        if (item.getAttribute('data-resource-path') === resourcePath) {
            item.setAttribute('data-resource-title', newTitle);
        }
    });

    // Immediately update all dropped resources in AI blocks with this path
    const droppedResources = document.querySelectorAll('.dropped-resource');
    droppedResources.forEach(dropped => {
        // Find the remove button which contains the resource path
        const removeBtn = dropped.querySelector('.remove-resource');
        if (removeBtn) {
            // Extract the path from the onclick attribute
            const onclickAttr = removeBtn.getAttribute('onclick');
            if (onclickAttr && onclickAttr.includes(resourcePath.replace(/'/g, "\\'"))) {
                // Update the text content (no icon anymore)
                dropped.childNodes[0].textContent = newTitle + ' ';
            }
        }
    });

    // Set new timer with 50ms delay (0.05 seconds after user stops typing)
    titleDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs
        const pathInput = document.getElementById('update-title-resource-path');
        const titleInput = document.getElementById('update-title-text');

        if (pathInput && titleInput) {
            const pathTextarea = pathInput.querySelector('textarea');
            const titleTextarea = titleInput.querySelector('textarea');

            if (pathTextarea && titleTextarea) {
                pathTextarea.value = resourcePath;
                titleTextarea.value = newTitle;

                // Dispatch input events
                pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                titleTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-title-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete titleDebounceTimers[timerKey];
    }, 50); // Wait 50ms after user stops typing
}

// Debounce timer for resource panel descriptions
let panelDescriptionDebounceTimers = {};

// Update resource description from panel with debouncing
function updateResourcePanelDescription(resourcePath, newDescription) {
    // Create unique key for this input
    const timerKey = `panel-${resourcePath}`;

    // Clear existing timer for this input
    if (panelDescriptionDebounceTimers[timerKey]) {
        clearTimeout(panelDescriptionDebounceTimers[timerKey]);
    }

    // Set new timer with 50ms delay
    panelDescriptionDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs - reusing the title inputs as per Python code
        const pathInput = document.getElementById('update-title-resource-path');
        const descInput = document.getElementById('update-title-text');

        if (pathInput && descInput) {
            const pathTextarea = pathInput.querySelector('textarea');
            const descTextarea = descInput.querySelector('textarea');

            if (pathTextarea && descTextarea) {
                pathTextarea.value = resourcePath;
                descTextarea.value = newDescription;

                // Dispatch input events
                pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                descTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button for description
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-panel-desc-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete panelDescriptionDebounceTimers[timerKey];
    }, 50);
}

// Toggle resource description collapse/expand
function toggleResourceDescription(resourceId) {
    const resourceItem = document.getElementById(resourceId);
    if (resourceItem) {
        const container = resourceItem.querySelector('.resource-description-container');
        const textarea = container.querySelector('.resource-panel-description');
        const button = container.querySelector('.desc-expand-btn');

        const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
        const padding = 8; // 4px top + 4px bottom
        const twoLinesHeight = (lineHeight * 2) + padding;

        // Function to get first two lines with ellipsis
        function getFirstTwoLinesWithEllipsis(text) {
            if (!text) return '';
            const lines = text.split('\n');
            let firstTwo = lines.slice(0, 2).join('\n');

            // Add ellipsis if there's more content
            if (lines.length > 2 || (lines.length === 2 && lines[1].length > 20)) {
                firstTwo += '...';
            }
            return firstTwo;
        }

        if (container.classList.contains('collapsed')) {
            // Expand - restore original text
            container.classList.remove('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Collapse';
            textarea.value = textarea.dataset.originalValue || textarea.value.replace(/\.\.\.$/,'');
            textarea.style.height = 'auto';
            textarea.style.maxHeight = '180px';
            textarea.style.overflow = ''; // Reset to CSS default
            textarea.classList.remove('scrollable');
            container.classList.remove('has-scrollbar');

            // Recalculate height and scrollability
            const scrollHeight = textarea.scrollHeight;
            textarea.style.height = Math.min(scrollHeight, 180) + 'px';
            if (scrollHeight > 180) {
                textarea.classList.add('scrollable');
                container.classList.add('has-scrollbar');
            }

            // Restore cursor position if available
            if (textarea.dataset.cursorPos) {
                const cursorPos = parseInt(textarea.dataset.cursorPos);
                textarea.focus();
                textarea.setSelectionRange(cursorPos, cursorPos);
                delete textarea.dataset.cursorPos;
            } else {
                textarea.focus();
            }
        } else {
            // Collapse - save original and show first 2 lines with ellipsis
            textarea.dataset.originalValue = textarea.value;
            container.classList.add('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Expand';
            textarea.value = getFirstTwoLinesWithEllipsis(textarea.dataset.originalValue);
            textarea.style.height = twoLinesHeight + 'px';
            textarea.style.maxHeight = twoLinesHeight + 'px';
            textarea.style.overflow = 'hidden';
            textarea.classList.remove('scrollable');
            container.classList.remove('has-scrollbar');
            textarea.blur();
        }
    }
}

// Setup auto-expand for resource descriptions
function setupResourceDescriptions() {
    const descTextareas = document.querySelectorAll('.resource-panel-description');

    descTextareas.forEach(textarea => {
        // Store original value without ellipsis
        if (!textarea.dataset.originalValue) {
            textarea.dataset.originalValue = textarea.value;
        }

        // Set minimum height for 2 lines
        const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
        const padding = 8; // 4px top + 4px bottom
        const minHeight = (lineHeight * 2) + padding;
        textarea.style.minHeight = minHeight + 'px';

        // Function to get first two lines with ellipsis
        function getFirstTwoLinesWithEllipsis(text) {
            if (!text) return '';
            const lines = text.split('\n');
            let firstTwo = lines.slice(0, 2).join('\n');

            // Add ellipsis if there's more content
            if (lines.length > 2 || (lines.length === 2 && lines[1].length > 20)) {
                firstTwo += '...';
            }
            return firstTwo;
        }

        // Auto-expand handler
        const autoExpand = function() {
            const container = this.closest('.resource-description-container');
            const button = container.querySelector('.desc-expand-btn');
            const isCollapsed = container.classList.contains('collapsed');

            // Store original value if typing
            if (!isCollapsed && this === document.activeElement) {
                this.dataset.originalValue = this.value;
            }

            if (!isCollapsed) {
                // Reset height to auto to get correct scrollHeight
                this.style.height = 'auto';
                const scrollHeight = this.scrollHeight;

                // Set height to scrollHeight, capped at max-height (180px)
                const newHeight = Math.min(scrollHeight, 180);
                this.style.height = newHeight + 'px';

                // Add scrollable class only if content exceeds 10 lines
                // Check against newHeight (before capping) to show scrollbar when starting 11th line
                const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
                const padding = 8; // 4px top + 4px bottom
                const tenLinesHeight = (lineHeight * 10) + padding;

                if (this.style.height === 'auto' && this.scrollHeight > tenLinesHeight) {
                    this.classList.add('scrollable');
                    container.classList.add('has-scrollbar');
                } else if (parseFloat(this.style.height) >= 180) {
                    // Also check if we're at max height
                    this.classList.add('scrollable');
                    container.classList.add('has-scrollbar');
                } else {
                    this.classList.remove('scrollable');
                    container.classList.remove('has-scrollbar');
                }

                // Check button visibility - moved inside the !isCollapsed block
                // Get actual computed line height and padding
                const computedLineHeight = parseFloat(window.getComputedStyle(this).lineHeight);
                const computedPadding = parseInt(window.getComputedStyle(this).paddingTop) +
                                       parseInt(window.getComputedStyle(this).paddingBottom);
                const computedTwoLinesHeight = (computedLineHeight * 2) + computedPadding;

                // Reset height temporarily to get accurate scrollHeight
                const currentHeight = this.style.height;
                this.style.height = 'auto';
                const actualScrollHeight = this.scrollHeight;
                this.style.height = currentHeight;

                // Count actual lines of text
                const lines = this.value.split('\n');
                let actualLineCount = 0;
                for (let line of lines) {
                    // Count wrapped lines too - approximate based on line length
                    // Resource panel is about 170px wide, ~15-20 chars per line at 11px font
                    actualLineCount += 1 + Math.floor(line.length / 20);
                }

                // Show button only when starting the 3rd line (similar to doc description)
                // Don't use trim() - count empty lines too
                if (actualLineCount > 2) {
                    button.style.display = 'block';
                } else {
                    button.style.display = 'none';
                    container.classList.remove('collapsed');
                }
            }
        };

        // Add event listeners
        textarea.addEventListener('input', autoExpand);
        textarea.addEventListener('paste', function() {
            setTimeout(() => autoExpand.call(this), 10);
        });

        // Click to expand when collapsed
        textarea.addEventListener('click', function(e) {
            const container = this.closest('.resource-description-container');
            if (container.classList.contains('collapsed')) {
                // Get cursor position before expanding
                const cursorPos = this.selectionStart;
                const resourceId = container.closest('.resource-item').id;

                // Store cursor position in dataset to use after expansion
                this.dataset.cursorPos = cursorPos;

                toggleResourceDescription(resourceId);
            }
        });

        // Initial sizing
        autoExpand.call(textarea);
    });
}

// Call setup on initial load
document.addEventListener('DOMContentLoaded', function () {
    refresh();
    setupImportButton();
    // Upload resource setup no longer needed - using Gradio's native component
    setupExampleSelection();
    // Delay initial drag and drop setup
    setTimeout(() => {
        setupDragAndDrop();
        setupResourceDescriptions();
    }, 100);
});