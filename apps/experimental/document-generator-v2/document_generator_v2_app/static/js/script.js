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

function setupUploadResource() {
    // Try multiple selectors
    const uploadBtn = document.querySelector('.upload-resources-btn')

    if (uploadBtn) {
        // Remove any existing listeners first
        uploadBtn.replaceWith(uploadBtn.cloneNode(true));
        const newUploadBtn = document.querySelector('.upload-resources-btn');

        newUploadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Find the file input that is NOT the import file input
            const fileInputs = document.querySelectorAll('input[type="file"]');
            let uploadFileInput = null;

            for (const input of fileInputs) {
                // Skip the import file input
                if (!input.closest('#import-file-input')) {
                    uploadFileInput = input;
                    break;
                }
            }

            if (uploadFileInput) {
                uploadFileInput.click();
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
        // For description, cap at max-height (200px)
        const maxHeight = 200;
        textarea.style.height = Math.min(newHeight, maxHeight) + 'px';
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
    setupUploadResource();
    setupAutoExpand();
});

window.addEventListener('load', function() {
    setTimeout(setupUploadResource, 1000);
    setTimeout(setupAutoExpand, 100);
    // Also setup drag and drop on window load
    setTimeout(setupDragAndDrop, 200);
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
        setupUploadResource();
        setupImportButton();

        // Delay drag and drop setup slightly to ensure DOM is ready
        setTimeout(() => {
            setupDragAndDrop();
        }, 50);

        // Debounce the setupAutoExpand to avoid multiple calls
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            setupAutoExpand();
            setupDescriptionToggle();
            setupExampleSelection();
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
    button.innerHTML = '⌄'; // Down chevron
    button.title = 'Collapse';

    // Insert button
    container.appendChild(button);

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
            textarea.style.maxHeight = '200px';
            textarea.style.overflow = '';  // Reset to CSS default
            container.classList.remove('collapsed');
            button.innerHTML = '⌄';
            button.title = 'Collapse';
            isCollapsed = false;
            autoExpandTextarea(textarea);
            // Focus at the end
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);

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
            button.innerHTML = '⌃';  // Up chevron
            button.title = 'Expand';
            isCollapsed = true;
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
            e.preventDefault();
            toggleCollapse();
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

// Call setup on initial load
document.addEventListener('DOMContentLoaded', function () {
    refresh();
    setupImportButton();
    setupUploadResource();
    setupExampleSelection();
    // Delay initial drag and drop setup
    setTimeout(() => {
        setupDragAndDrop();
    }, 100);
});