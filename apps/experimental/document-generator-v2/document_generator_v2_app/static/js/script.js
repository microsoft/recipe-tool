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
    // Skip document description - it's handled by setupDescriptionToggle
    const isDocDescription = textarea.closest('#doc-description-id');
    if (isDocDescription) {
        return;
    }
    
    // For other textareas, use height-based method
    textarea.style.height = 'auto';
    const newHeight = textarea.scrollHeight + 2;
    textarea.style.height = newHeight + 'px';
    textarea.style.maxHeight = '';
    textarea.style.overflow = 'hidden';
    textarea.classList.remove('scrollable');
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
        // Remove the watcher - it's causing issues
        // The setupDescriptionToggle handles everything needed
    }
}

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', function () {
    refresh();
    // Upload resource setup no longer needed - using Gradio's native component
    setupAutoExpand();
});

// Reset document description on new document
function resetDocumentDescription() {
    const docDescriptionBox = document.querySelector('.doc-description-box');
    const docDescriptionTextarea = document.querySelector('#doc-description-id textarea');

    if (docDescriptionBox && docDescriptionTextarea) {
        // Clear the textarea value
        docDescriptionTextarea.value = '';

        // Ensure the box is collapsed
        if (!docDescriptionBox.classList.contains('collapsed')) {
            docDescriptionBox.classList.add('collapsed');
        }

        // Reset the textarea height
        docDescriptionTextarea.style.height = 'auto';
        autoExpandTextarea(docDescriptionTextarea);

        // Hide the expand button
        const expandBtn = docDescriptionBox.querySelector('.desc-expand-btn');
        if (expandBtn) {
            expandBtn.style.display = 'none';
        }
    }
}

// Track if we're dragging from an external source
let isDraggingFromExternal = false;

// Clear draggedResource when dragging files from outside the browser
document.addEventListener('dragenter', function(e) {
    // Only clear draggedResource if we don't already have one AND this looks like an external drag
    if (!draggedResource && e.dataTransfer && e.dataTransfer.types) {
        // Check if this is likely an external file drag
        const hasFiles = e.dataTransfer.types.includes('Files') ||
                        e.dataTransfer.types.includes('application/x-moz-file');

        // Also check that it's not coming from our resource items
        const isFromResourceItem = e.target.closest('.resource-item');

        if (hasFiles && !isFromResourceItem && !isDraggingFromExternal) {
            isDraggingFromExternal = true;
            console.log('External file drag detected');
            draggedResource = null;
        }
    }
}, true); // Use capture phase to run before other handlers

// Reset the external drag flag when drag ends
document.addEventListener('dragleave', function(e) {
    // Check if we're leaving the document entirely
    if (e.clientX === 0 && e.clientY === 0) {
        isDraggingFromExternal = false;
    }
});

document.addEventListener('drop', function(e) {
    isDraggingFromExternal = false;
});

// Also reset when starting to drag a resource
document.addEventListener('dragstart', function(e) {
    if (e.target.closest('.resource-item')) {
        isDraggingFromExternal = false;
    }
});

// Setup observers for resource title changes in Gradio components
function setupResourceTitleObservers() {
    const resourceItems = document.querySelectorAll('.resource-item-gradio');
    console.log('Setting up title observers for', resourceItems.length, 'resource items');

    resourceItems.forEach((item, index) => {
        // Find the title textarea
        const titleTextarea = item.querySelector('.resource-title-gradio input');
        const pathDiv = item.querySelector('.resource-path-hidden');

        if (titleTextarea && pathDiv) {
            const resourcePath = pathDiv.getAttribute('data-path') || pathDiv.textContent.trim();
            console.log(`Resource ${index}: path="${resourcePath}"`);

            // Remove any existing listener to avoid duplicates
            titleTextarea.removeEventListener('input', titleTextarea._titleUpdateHandler);

            // Create and store the handler function
            titleTextarea._titleUpdateHandler = function() {
                const newTitle = this.value;
                console.log(`Title changed for resource "${resourcePath}": "${newTitle}"`);

                // Immediately update all dropped resources with this path
                const droppedResources = document.querySelectorAll('.dropped-resource[data-resource-path]');
                console.log(`Found ${droppedResources.length} dropped resources to check`);

                droppedResources.forEach(dropped => {
                    const droppedPath = dropped.getAttribute('data-resource-path');
                    console.log(`Checking dropped resource with path="${droppedPath}"`);

                    if (droppedPath === resourcePath) {
                        const titleSpan = dropped.querySelector('.dropped-resource-title');
                        if (titleSpan) {
                            console.log(`Updating title span to: "${newTitle}"`);
                            titleSpan.textContent = newTitle;
                        }
                    }
                });
            };

            // Add the event listener
            titleTextarea.addEventListener('input', titleTextarea._titleUpdateHandler);
            console.log(`Added input listener to resource ${index}`);
        } else {
            console.log(`Resource ${index}: Missing textarea or path div`);
        }
    });
}

window.addEventListener('load', function() {
    console.log('Window load event fired');
    // Upload resource setup no longer needed - using Gradio's native component
    setTimeout(setupAutoExpand, 100);
    // Also setup drag and drop on window load
    setTimeout(setupDragAndDrop, 200);
    setTimeout(setupFileUploadDragAndDrop, 250);
    // Setup description toggle button
    setTimeout(setupDescriptionToggle, 150);

    // Set up a global observer for the resources column
    setupResourceObserver();

    // Setup title observers for dynamic updates
    setTimeout(() => {
        console.log('About to call setupResourceTitleObservers');
        const resourceItems = document.querySelectorAll('.resource-item-gradio');
        console.log('Found', resourceItems.length, 'resource items before calling setup');
        setupResourceTitleObservers();
    }, 300);
});

// Function to set up observer for resources
function setupResourceObserver() {
    let resourceSetupTimeout;

    // Function to observe a resources area
    function observeResourcesArea(resourcesArea) {
        if (!resourcesArea) return;

        const resourceObserver = new MutationObserver((mutations) => {
            // Clear any pending timeout
            clearTimeout(resourceSetupTimeout);

            // Check if resource items were added
            let hasResourceChanges = false;
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 &&
                        (node.classList?.contains('resource-item') ||
                         node.querySelector?.('.resource-item'))) {
                        hasResourceChanges = true;
                    }
                });
            });

            if (hasResourceChanges) {
                console.log('Resources added, setting up drag and drop');
                // Wait a bit for DOM to stabilize then setup drag and drop
                resourceSetupTimeout = setTimeout(() => {
                    setupDragAndDrop();
                    setupResourceTitleObservers();
                }, 200);
            }
        });

        resourceObserver.observe(resourcesArea, {
            childList: true,
            subtree: true
        });

        return resourceObserver;
    }

    // Initial setup
    let currentObserver = observeResourcesArea(document.querySelector('.resources-display-area'));

    // Also watch for the resources area itself being replaced
    const columnObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const newResourcesArea = node.classList?.contains('resources-display-area') ?
                        node : node.querySelector?.('.resources-display-area');

                    if (newResourcesArea) {
                        console.log('Resources area replaced, setting up new observer');
                        // Disconnect old observer if it exists
                        if (currentObserver) {
                            currentObserver.disconnect();
                        }
                        // Set up new observer
                        currentObserver = observeResourcesArea(newResourcesArea);
                        // Setup drag and drop for any existing items
                        setTimeout(setupDragAndDrop, 200);
                        // Setup title observers too
                        setTimeout(setupResourceTitleObservers, 300);
                    }
                }
            });
        });
    });

    // Observe the resources column for replacements
    const resourcesCol = document.querySelector('.resources-col');
    if (resourcesCol) {
        columnObserver.observe(resourcesCol, {
            childList: true,
            subtree: true
        });
    }
}

// Prevent dropping resources on text inputs and file upload zones
function preventInvalidDrops() {
    // Helper function to check if element is invalid drop target
    function isInvalidDropTarget(element) {
        if (!element) return false;

        // Check if it's a text input
        if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
            return true;
        }

        // Check if it's part of a file upload component (Gradio file upload)
        if (element.closest('.resource-upload-gradio') ||
            element.closest('[data-testid="file"]') ||
            element.classList.contains('resource-upload-gradio')) {
            return true;
        }

        return false;
    }

    // Prevent drop on invalid targets
    document.addEventListener('dragover', function(e) {
        if (isInvalidDropTarget(e.target)) {
            if (draggedResource || window.currentDraggedResource) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'none';
                e.target.classList.add('no-drop');
            }
        }
    }, true);

    document.addEventListener('dragleave', function(e) {
        if (isInvalidDropTarget(e.target)) {
            e.target.classList.remove('no-drop');
        }
    }, true);

    document.addEventListener('drop', function(e) {
        if (isInvalidDropTarget(e.target)) {
            if (draggedResource || window.currentDraggedResource) {
                e.preventDefault();
                e.stopPropagation();
                e.target.classList.remove('no-drop');
                console.log('Prevented drop on invalid target:', e.target);
            }
        }
    }, true);

    // Clean up no-drop class when drag ends
    document.addEventListener('dragend', function(e) {
        document.querySelectorAll('.no-drop').forEach(el => {
            el.classList.remove('no-drop');
        });
    }, true);
}

// Call it once when the page loads
preventInvalidDrops();

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
                        node.classList?.contains('resource-item-gradio') ||
                        node.classList?.contains('block-resources') ||
                        node.querySelector?.('textarea') ||
                        node.querySelector?.('.resource-item') ||
                        node.querySelector?.('.resource-item-gradio') ||
                        node.querySelector?.('.block-resources') ||
                        node.tagName === 'TEXTAREA') {
                        hasRelevantChanges = true;
                        // Log when we detect resource items
                        if (node.classList?.contains('resource-item') ||
                            node.classList?.contains('resource-item-gradio') ||
                            node.querySelector?.('.resource-item') ||
                            node.querySelector?.('.resource-item-gradio')) {
                            console.log('Detected resource item change');
                        }
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
            setupResourceTitleObservers();
        }, 50);

        // Debounce the setupAutoExpand to avoid multiple calls
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            setupAutoExpand();
            setupDescriptionToggle();
            setupExampleSelection();
            setupResourceDescriptions();
            setupResourceUploadZones();
            setupResourceUploadText();
            preventResourceDrops();
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
                    // Focus the textarea after conversion
                    setTimeout(() => {
                        const block = document.querySelector(`[data-id="${blockId}"]`);
                        if (block) {
                            const textarea = block.querySelector('textarea');
                            if (textarea) {
                                textarea.focus();
                            }
                        }
                    }, 200);
                }
            }, 100);
        }
    }
}

// Focus textarea within a block
function focusBlockTextarea(blockId) {
    const block = document.querySelector(`[data-id="${blockId}"]`);
    if (block) {
        const textarea = block.querySelector('textarea');
        if (textarea) {
            textarea.focus();
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

    // Function to check if button should be visible
    function checkButtonVisibility() {
        if (isCollapsed) return;
        
        // Count actual lines in the textarea
        const lines = textarea.value.split('\n');
        let totalLines = lines.length; // Start with actual line breaks
        
        // Add wrapped lines - estimate ~80 chars per line for wider doc description
        lines.forEach((line, index) => {
            if (line.length > 80) {
                // Add extra lines for wrapping
                totalLines += Math.floor(line.length / 80);
            }
        });
        
        console.log('Doc desc - lines:', lines.length, 'totalLines:', totalLines);
        
        // Show button if content exceeds 2 lines
        if (totalLines > 2) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
        
        // Set rows attribute based on content, no max
        let rowsToShow = Math.max(2, totalLines);
        
        // Add 1 extra row if we have 3 or more rows for breathing room
        if (rowsToShow >= 3) {
            rowsToShow += 1;
        }
        
        console.log('Setting rows to:', rowsToShow);
        
        textarea.rows = rowsToShow;
        textarea.style.height = 'auto'; // Use auto instead of empty string
        textarea.style.minHeight = 'auto';
        textarea.style.maxHeight = 'none';
        textarea.style.overflow = 'hidden';
        
        // Never add scrollable class
        textarea.classList.remove('scrollable');
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
            textarea.style.height = ''; // Clear height
            textarea.style.maxHeight = ''; // Remove max height
            textarea.style.overflow = 'hidden'; // No scrollbars
            container.classList.remove('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Collapse';
            isCollapsed = false;
            textarea.classList.remove('scrollable'); // Remove scrollable class
            checkButtonVisibility(); // Use checkButtonVisibility like resources
            // Keep focus without moving cursor
            textarea.focus();

            // Trigger input event to update Gradio's state
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            // Collapse - save full text and show only first 2 lines
            fullText = textarea.value;
            textarea.value = getFirstTwoLines(fullText);
            textarea.rows = 2; // Force 2 rows
            textarea.style.height = ''; // Let rows control height
            textarea.style.maxHeight = ''; // Clear max height
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
        // Only update if not collapsed (unless typing to expand)
        if (!isCollapsed) {
            checkButtonVisibility();
        } else if (textarea.value !== getFirstTwoLines(fullText)) {
            // If collapsed and user is typing (not just the truncated value), expand
            toggleCollapse();
        }
    });
    
    // Also handle paste
    textarea.addEventListener('paste', function() {
        setTimeout(() => {
            if (!isCollapsed) {
                checkButtonVisibility();
            }
        }, 10);
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

    // Also setup resource upload zones
    setupResourceUploadText();

    // Add drag-over class when dragging files over the upload zone
    let dragCounter = 0;

    function addDragListeners(element) {
        element.addEventListener('dragenter', function(e) {
            e.preventDefault();
            // Only show drag-over effect if not dragging a resource
            if (!draggedResource) {
                dragCounter++;
                fileUploadZone.classList.add('drag-over');
            }
        });

        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // If dragging a resource, show "not allowed" cursor
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            } else {
                fileUploadZone.classList.add('drag-over');
            }
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
            // Block resource drops completely
            if (draggedResource) {
                e.stopPropagation();
                return false;
            }
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

    // Setup draggable resources - now look for Gradio resource components
    const resourceItems = document.querySelectorAll('.resource-item-gradio');
    console.log('Found Gradio resource items:', resourceItems.length);

    resourceItems.forEach((item, index) => {
        // Make sure the item is draggable
        item.setAttribute('draggable', 'true');

        // Just store the path on the element for reference during drag
        const pathHidden = item.querySelector('.resource-path-hidden');
        if (pathHidden) {
            const path = pathHidden.getAttribute('data-path') || pathHidden.textContent.trim();
            item.dataset.resourcePath = path;
            console.log(`Resource ${index} path:`, path);
        }

        // Also make child elements not draggable to prevent conflicts
        const inputs = item.querySelectorAll('input, textarea, button');
        inputs.forEach(input => {
            input.setAttribute('draggable', 'false');
        });

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

    if (dropZones.length === 0) {
        console.warn('No drop zones found! Blocks might not be rendered yet.');
        // Try again after a short delay
        setTimeout(() => {
            const retryDropZones = document.querySelectorAll('.block-resources');
            console.log('Retry - Found drop zones:', retryDropZones.length);
            setupDropZones(retryDropZones);
        }, 500);
    } else {
        setupDropZones(dropZones);
    }
}

function setupDropZones(dropZones) {
    dropZones.forEach((zone, index) => {
        // Remove existing listeners to avoid duplicates
        zone.removeEventListener('dragenter', handleDragEnter);
        zone.removeEventListener('dragover', handleDragOver);
        zone.removeEventListener('drop', handleDrop);
        zone.removeEventListener('dragleave', handleDragLeave);

        // Add new listeners
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleDrop);
        zone.addEventListener('dragleave', handleDragLeave);

        // Add data attribute to help debug
        zone.setAttribute('data-drop-zone-index', index);
        console.log(`Set up drop zone ${index} on element:`, zone);
    });
}

let draggedResource = null;

function handleDragStart(e) {
    console.log('handleDragStart called on:', e.target);

    // Prevent dragging when clicking on input elements
    if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
        e.preventDefault();
        return;
    }

    // For Gradio components, we need to extract data differently
    const resourceElement = e.target.closest('.resource-item-gradio');
    if (resourceElement) {
        console.log('Resource element found:', resourceElement);

        // Always extract current values dynamically to get latest updates
        console.log('Extracting current resource data...');

        // Look for elements - Gradio might have nested structures
        const titleInput = resourceElement.querySelector('.resource-title-gradio input[type="text"], .resource-title-gradio textarea');
        const descInput = resourceElement.querySelector('.resource-desc-gradio textarea');
        const pathDiv = resourceElement.querySelector('.resource-path-hidden');
        const filenameDiv = resourceElement.querySelector('.resource-filename');

        // Debug logging
        console.log('Title input found:', !!titleInput);
        if (titleInput) {
            console.log('Title input type:', titleInput.tagName);
            console.log('Title value:', titleInput.value);
        }

        console.log('Found elements:', {
            titleInput: !!titleInput,
            descInput: !!descInput,
            pathDiv: !!pathDiv,
            filenameDiv: !!filenameDiv
        });

        if (pathDiv && filenameDiv) {
            const path = pathDiv.getAttribute('data-path') || pathDiv.textContent.trim();
            const filename = filenameDiv.textContent.trim();
            // Get title from input/textarea value, fallback to filename
            const title = titleInput && titleInput.value ? titleInput.value.trim() : filename;
            const description = descInput && descInput.value ? descInput.value.trim() : '';

            draggedResource = {
                name: filename,
                title: title,
                path: path,
                type: 'text',
                description: description
            };
            console.log('Dynamically extracted resource:', draggedResource);
            console.log('Title being sent:', title);
            console.log('Filename being sent:', filename);
        }

        if (draggedResource) {
            console.log('Started dragging Gradio resource:', draggedResource);
            resourceElement.classList.add('dragging');
            document.body.classList.add('dragging-resource');
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('text/plain', JSON.stringify(draggedResource));

            // Set global variable to ensure it persists
            window.currentDraggedResource = draggedResource;
        } else {
            console.error('Could not extract resource data for drag');
        }
    }
}

function handleDragEnd(e) {
    // For Gradio components
    const resourceElement = e.target.closest('.resource-item-gradio');
    if (resourceElement) {
        resourceElement.classList.remove('dragging');
    } else {
        e.target.classList.remove('dragging');
    }

    // Remove dragging class from body
    document.body.classList.remove('dragging-resource');

    // Clear draggedResource after a small delay to ensure drop completes
    setTimeout(() => {
        draggedResource = null;
        window.currentDraggedResource = null;
    }, 100);
}

function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    const resource = draggedResource || window.currentDraggedResource;
    console.log('DragEnter event - draggedResource:', resource);

    if (resource) {
        e.currentTarget.classList.add('drag-over');
    }
}

function handleDragOver(e) {
    // Only prevent default for valid drop zones
    if (e.currentTarget.classList.contains('block-resources')) {
        e.preventDefault();
        e.stopPropagation();

        const resource = draggedResource || window.currentDraggedResource;

        // Debug logging - reduce verbosity
        if (!e.currentTarget.dataset.loggedOnce) {
            console.log('DragOver event - draggedResource:', resource);
            console.log('DragOver target:', e.currentTarget);
            e.currentTarget.dataset.loggedOnce = 'true';
        }

        // Only show drag-over effect if we're dragging a resource from the panel
        if (resource) {
            // Try different drop effects to get the right cursor
            e.dataTransfer.dropEffect = 'copy';
            e.currentTarget.classList.add('drag-over');

            // Force cursor style
            e.currentTarget.style.cursor = 'copy';
        }
    }
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
    e.currentTarget.style.cursor = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');

    const resource = draggedResource || window.currentDraggedResource;

    console.log('Drop event triggered');
    console.log('Drop target:', e.currentTarget);
    console.log('Drop zone index:', e.currentTarget.getAttribute('data-drop-zone-index'));
    console.log('Dragged resource:', resource);

    if (!resource) {
        console.error('No dragged resource found');
        return;
    }

    // Find the block ID from the parent content block
    const contentBlock = e.currentTarget.closest('.content-block');
    if (!contentBlock) {
        console.error('No parent content block found');
        console.log('Current target classes:', e.currentTarget.className);
        console.log('Parent element:', e.currentTarget.parentElement);
        return;
    }

    const blockId = contentBlock.dataset.id;
    console.log('Dropping resource on block:', blockId, resource);

    // Update the block's resources
    updateBlockResources(blockId, resource);

    // Clear both variables and remove body class
    draggedResource = null;
    window.currentDraggedResource = null;
    document.body.classList.remove('dragging-resource');
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
                            
                            // Re-setup resource descriptions after loading
                            setTimeout(() => {
                                setupResourceDescriptions();
                                // Doc description will be handled by the interval watcher
                            }, 500);
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
    const droppedResources = document.querySelectorAll('.dropped-resource[data-resource-path]');
    droppedResources.forEach(dropped => {
        // Check if this dropped resource matches the path
        if (dropped.getAttribute('data-resource-path') === resourcePath) {
            // Find the title span and update it
            const titleSpan = dropped.querySelector('.dropped-resource-title');
            if (titleSpan) {
                titleSpan.textContent = newTitle;
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
    // Handle Gradio resource descriptions
    const gradioDescTextareas = document.querySelectorAll('.resource-desc-gradio textarea');
    
    gradioDescTextareas.forEach(textarea => {
        const container = textarea.closest('.resource-desc-gradio');
        if (!container || container.dataset.toggleSetup) {
            return;
        }
        
        // Mark as setup
        container.dataset.toggleSetup = 'true';
        
        // Create expand/collapse button
        const button = document.createElement('button');
        button.className = 'desc-expand-btn';
        button.innerHTML = '⌵'; // Down chevron
        button.title = 'Collapse';
        button.style.display = 'none'; // Hidden by default
        
        // Add button to container
        container.appendChild(button);
        
        // Track collapsed state and full text
        let isCollapsed = false;
        let fullText = '';
        
        // Function to get first two lines of text
        function getFirstTwoLines(text) {
            const lines = text.split('\n');
            
            // Always show exactly 2 lines
            if (lines.length === 1) {
                // If only one line, just return it with ellipsis if it's long
                return lines[0].length > 50 ? lines[0].substring(0, 47) + '...' : lines[0];
            } else if (lines.length >= 2) {
                // Get exactly first two lines
                const firstLine = lines[0];
                const secondLine = lines[1];
                
                // If there are more than 2 lines or the second line is long, add ellipsis
                if (lines.length > 2 || secondLine.length > 50) {
                    // Truncate second line if needed to make room for ellipsis
                    const truncatedSecond = secondLine.length > 47 ? secondLine.substring(0, 47) : secondLine;
                    return firstLine + '\n' + truncatedSecond + '...';
                } else {
                    return firstLine + '\n' + secondLine;
                }
            }
            
            return text;
        }
        
        // Function to check if button should be visible
        function checkButtonVisibility() {
            if (isCollapsed) return;
            
            // Count actual lines in the textarea
            const lines = textarea.value.split('\n');
            let totalLines = lines.length; // Start with actual line breaks
            
            // Add wrapped lines - more accurate estimation
            // Resource panel is narrower, estimate ~35 chars per line at 11px font
            lines.forEach((line, index) => {
                if (line.length > 35) {
                    // Add extra lines for wrapping
                    totalLines += Math.floor(line.length / 35);
                }
            });
            
            // Show button if content exceeds 2 lines
            if (totalLines > 2) {
                button.style.display = 'block';
            } else {
                button.style.display = 'none';
            }
            
            // Set rows attribute based on content, no max
            let rowsToShow = Math.max(2, totalLines);
            
            // Add 1 extra row if we have 3 or more rows for breathing room
            if (rowsToShow >= 3) {
                rowsToShow += 1;
            }
            
            textarea.rows = rowsToShow;
            textarea.style.height = ''; // Let rows attribute control height
            textarea.style.minHeight = ''; // Clear any min-height
            textarea.style.maxHeight = ''; // Clear any max-height
            textarea.style.overflow = 'hidden'; // No scrollbars
            
            // Never add scrollable class
            textarea.classList.remove('scrollable');
        }
        
        // Toggle collapse/expand
        function toggleCollapse() {
            if (isCollapsed) {
                // Expand
                textarea.value = fullText;
                textarea.style.height = ''; // Clear height to let rows control it
                container.classList.remove('collapsed');
                button.innerHTML = '⌵';
                button.title = 'Collapse';
                isCollapsed = false;
                // Don't set rows to null - let checkButtonVisibility set it
                checkButtonVisibility();
                textarea.focus();
                
                // Trigger input event to update Gradio's state
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
            } else {
                // Collapse
                fullText = textarea.value;
                textarea.value = getFirstTwoLines(fullText);
                textarea.rows = 2; // Force exactly 2 rows
                textarea.style.height = ''; // Let rows attribute control height
                container.classList.add('collapsed');
                button.innerHTML = '⌵';
                button.title = 'Expand';
                isCollapsed = true;
                textarea.classList.remove('scrollable');
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
                const cursorPos = textarea.selectionStart;
                toggleCollapse();
                setTimeout(() => {
                    textarea.setSelectionRange(cursorPos, cursorPos);
                }, 0);
            }
        });
        
        // Check on input
        textarea.addEventListener('input', () => {
            checkButtonVisibility();
            if (isCollapsed) {
                toggleCollapse();
            }
        });
        
        // Initial check
        checkButtonVisibility();
        
        // If textarea has initial content, ensure proper display
        if (textarea.value && textarea.value.split('\n').length > 2) {
            checkButtonVisibility();
        }
        
        // Watch for value changes (e.g., from imports)
        const observer = new MutationObserver(() => {
            if (!isCollapsed && textarea.value !== fullText) {
                checkButtonVisibility();
            }
        });
        
        observer.observe(textarea, {
            attributes: true,
            attributeFilter: ['value']
        });
        
        // Also listen for programmatic value changes
        let lastValue = textarea.value;
        setInterval(() => {
            if (textarea.value !== lastValue && !isCollapsed) {
                lastValue = textarea.value;
                checkButtonVisibility();
            }
        }, 500);
    });

    // Also handle the old panel descriptions if they exist
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

// Handle resource file upload
function handleResourceFileUpload(resourcePath, fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    console.log('Uploading file to replace resource:', resourcePath, file.name);

    // Set the resource path
    const pathInput = document.getElementById('replace-resource-path');
    if (pathInput) {
        const pathTextarea = pathInput.querySelector('textarea');
        if (pathTextarea) {
            pathTextarea.value = resourcePath;
            pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    // Find the hidden file input component and set the file
    const hiddenFileInput = document.querySelector('#replace-resource-file input[type="file"]');
    if (hiddenFileInput) {
        // Create a new DataTransfer to set files on the hidden input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        hiddenFileInput.files = dataTransfer.files;

        // Trigger change event on the hidden file input
        hiddenFileInput.dispatchEvent(new Event('change', { bubbles: true }));

        // Trigger the replace button after a delay
        setTimeout(() => {
            const replaceBtn = document.getElementById('replace-resource-trigger');
            if (replaceBtn) {
                replaceBtn.click();

                // Add visual feedback to the upload zone
                const uploadZone = fileInput.closest('.resource-upload-zone');
                if (uploadZone) {
                    uploadZone.classList.add('upload-success');
                    const uploadText = uploadZone.querySelector('.upload-text');
                    if (uploadText) {
                        uploadText.textContent = '✓ File replaced';
                    }

                    // Reset after 2 seconds
                    setTimeout(() => {
                        uploadZone.classList.remove('upload-success');
                        uploadText.textContent = 'Drop file here to replace';
                    }, 2000);
                }
            }
        }, 100);
    }

    // Clear the file input
    fileInput.value = '';
}

// Prevent drops on resource textareas and inputs
function preventResourceDrops() {
    // Prevent drops on all textareas and inputs within resource items
    const resourceInputs = document.querySelectorAll('.resource-item input, .resource-item textarea');

    resourceInputs.forEach(element => {
        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            }
        });

        element.addEventListener('drop', function(e) {
            e.preventDefault();
            if (draggedResource) {
                e.stopPropagation();
                return false;
            }
        });
    });
}

// Function to setup resource upload text
function setupResourceUploadText() {
    // Function to replace the text in resource upload zones
    function replaceResourceUploadText() {
        const resourceUploadZones = document.querySelectorAll('.resource-upload-gradio');
        
        resourceUploadZones.forEach(zone => {
            // Find all text nodes and remove default Gradio text
            const wrapDivs = zone.querySelectorAll('.wrap');
            wrapDivs.forEach(wrapDiv => {
                // Hide the icon
                const icon = wrapDiv.querySelector('.icon-wrap');
                if (icon) {
                    icon.style.display = 'none';
                }
                
                // Replace the text content and remove spans with "- or -"
                wrapDiv.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const text = node.textContent;
                        if (text.includes('Drop File Here') || text.includes('Click to Upload') || text.includes('- or -')) {
                            node.textContent = '';
                        }
                    } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'SPAN') {
                        // Check if span contains "- or -" or other unwanted text
                        if (node.textContent.includes('- or -') || 
                            node.textContent.includes('Drop File Here') || 
                            node.textContent.includes('Click to Upload')) {
                            node.style.display = 'none';
                        }
                    }
                });
                
                // Also hide any .or class spans
                const orSpans = wrapDiv.querySelectorAll('.or, span.or');
                orSpans.forEach(span => {
                    span.style.display = 'none';
                });
                
                // Add our custom text if not already present
                if (!wrapDiv.querySelector('.custom-upload-text')) {
                    const customText = document.createElement('span');
                    customText.className = 'custom-upload-text';
                    customText.textContent = 'Drop file here to replace';
                    customText.style.fontSize = '11px';
                    customText.style.color = '#666';
                    wrapDiv.appendChild(customText);
                }
            });
        });
    }

    // Try to replace immediately
    replaceResourceUploadText();

    // Watch for changes in resource areas
    const resourcesArea = document.querySelector('.resources-display-area');
    if (resourcesArea) {
        const observer = new MutationObserver((mutations) => {
            replaceResourceUploadText();
        });

        observer.observe(resourcesArea, {
            childList: true,
            subtree: true
        });

        // Stop observing after 10 seconds
        setTimeout(() => observer.disconnect(), 10000);
    }
}

// Setup drag and drop for resource upload zones
function setupResourceUploadZones() {
    const uploadZones = document.querySelectorAll('.resource-upload-zone');

    uploadZones.forEach(zone => {
        let dragCounter = 0;

        zone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            // Only show drag-over effect if NOT dragging a resource
            if (!draggedResource) {
                dragCounter++;
                this.classList.add('drag-over');
            }
        });

        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            // If dragging a resource, show "not allowed" cursor
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            } else {
                // For external files, show "copy" cursor
                e.dataTransfer.dropEffect = 'copy';
            }
        });

        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                this.classList.remove('drag-over');
            }
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dragCounter = 0;
            this.classList.remove('drag-over');

            // Block resource drops completely
            if (draggedResource) {
                return false;
            }

            // Handle external file drops
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const fileInput = this.querySelector('.resource-file-input');
                const resourcePath = this.getAttribute('data-resource-path');

                if (fileInput && resourcePath) {
                    // Create a new DataTransfer to set files on input
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(e.dataTransfer.files[0]);
                    fileInput.files = dataTransfer.files;

                    // Trigger the change event
                    handleResourceFileUpload(resourcePath, fileInput);
                }
            }
        });
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
        setupResourceTitleObservers();
        setupResourceUploadZones();
        setupResourceUploadText();
        preventResourceDrops();
    }, 100);
});