let drake = null;
let originalOrder = [];
let autoScrollInterval = null;
let focusedBlockIndex = null;

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
    const pageContainer = document.querySelector('.page-panel');
    if (!pageContainer) return;

    const rect = pageContainer.getBoundingClientRect();
    const scrollMargin = 50; // Distance from edge to trigger scroll
    const mouseY = e.clientY;

    // Check if mouse is near top or bottom of page panel
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
            const blockContainer = handle.closest('.block-container');
            const isBlockWrapper = blockContainer !== null;
            
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

// Resource drag and drop functionality
function initializeResourceDragDrop() {
    // Add event listeners to draggable resources
    document.addEventListener('dragstart', function(e) {
        if (e.target.classList.contains('resource-item')) {
            e.target.classList.add('dragging');
            document.body.classList.add('dragging-resource');
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('text/plain', JSON.stringify({
                name: e.target.dataset.resourceName,
                type: e.target.dataset.resourceType,
                path: e.target.dataset.resourcePath
            }));
        }
    });

    document.addEventListener('dragend', function(e) {
        if (e.target.classList.contains('resource-item')) {
            e.target.classList.remove('dragging');
            document.body.classList.remove('dragging-resource');
        }
    });

    // Add event listeners to drop zones
    document.addEventListener('dragover', function(e) {
        // Check if we're over a text input or textarea
        const isOverTextInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
                               e.target.closest('.block-heading') || e.target.closest('.block-content');

        // Only allow dropping on resources drop zone
        if (e.target.classList.contains('resources-drop-zone') || e.target.closest('.resources-drop-zone')) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            const dropZone = e.target.closest('.resources-drop-zone') || e.target;
            dropZone.classList.add('drag-over');
        } else if (isOverTextInput) {
            // Explicitly prevent dropping on text areas
            e.preventDefault();
            e.dataTransfer.dropEffect = 'none';
        } else {
            // Prevent dropping elsewhere
            e.dataTransfer.dropEffect = 'none';
        }
    });

    document.addEventListener('dragleave', function(e) {
        if (e.target.classList.contains('resources-drop-zone')) {
            e.target.classList.remove('drag-over');
        }
    });

    document.addEventListener('drop', function(e) {
        // Prevent default drop behavior everywhere
        e.preventDefault();

        // Only process drops on resources drop zone
        const dropZone = e.target.classList.contains('resources-drop-zone') ? e.target : e.target.closest('.resources-drop-zone');
        if (dropZone) {
            dropZone.classList.remove('drag-over');

            try {
                const resourceData = JSON.parse(e.dataTransfer.getData('text/plain'));
                const icon = resourceData.type === 'image' ? '🖼️' : '📄';

                // Get the block index from the drop zone
                const blockIndex = parseInt(dropZone.dataset.blockIndex);

                // Add the resource to the drop zone
                const resourceHtml = `<span class="dropped-resource">${icon} ${resourceData.name}</span>`;

                // If it's the first resource, replace the placeholder text
                if (dropZone.textContent.trim() === 'Drop resources here') {
                    dropZone.innerHTML = resourceHtml;
                } else {
                    dropZone.innerHTML += resourceHtml;
                }

                // Trigger an update to store the resource in the block state
                const resourceUpdateBtn = document.getElementById('resource-update-trigger');
                const resourceUpdateData = document.getElementById('resource-update-data');
                if (resourceUpdateBtn && resourceUpdateData) {
                    const textarea = resourceUpdateData.querySelector('textarea');
                    if (textarea) {
                        textarea.value = JSON.stringify({
                            blockIndex: blockIndex,
                            resource: resourceData
                        });
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        setTimeout(() => {
                            resourceUpdateBtn.click();
                        }, 50);
                    }
                }
            } catch (err) {
                console.error('Failed to process dropped resource:', err);
            }
        }
    });
}


// Focus tracking functionality
function initializeFocusTracking() {
    console.log('Initializing focus tracking...');
    
    // Function to update focused block
    function updateFocusedBlock(blockElement) {
        // Remove focused class from all blocks
        document.querySelectorAll('.block-container').forEach(block => {
            block.classList.remove('focused');
        });
        
        if (!blockElement) return;
        
        // Add focused class to current block
        blockElement.classList.add('focused');
        
        // Find the index of this block
        const mainContainer = document.querySelector('.main-container');
        if (!mainContainer) {
            console.error('Main container not found');
            return;
        }
        
        const allBlocks = Array.from(mainContainer.children);
        let visibleIndex = -1;
        
        for (let i = 0; i < allBlocks.length; i++) {
            if (allBlocks[i].style.display !== 'none' && !allBlocks[i].style.display) {
                visibleIndex++;
                const containerInBlock = allBlocks[i].querySelector('.block-container');
                if (containerInBlock === blockElement) {
                    focusedBlockIndex = visibleIndex;
                    console.log('Setting focused block index to:', visibleIndex);
                    
                    // Update the hidden input
                    const focusedInput = document.querySelector('#focused-block-index textarea');
                    if (focusedInput) {
                        focusedInput.value = visibleIndex.toString();
                        focusedInput.dispatchEvent(new Event('input', { bubbles: true }));
                        focusedInput.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        console.log('Updated textarea value to:', focusedInput.value);
                    } else {
                        console.error('Could not find #focused-block-index textarea');
                    }
                    break;
                }
            }
        }
    }
    
    // Add event listeners for focus on textareas within blocks
    document.addEventListener('focusin', function(e) {
        if (e.target.tagName === 'TEXTAREA') {
            const blockContainer = e.target.closest('.block-container');
            if (blockContainer) {
                updateFocusedBlock(blockContainer);
            }
        }
    });
    
    // Also handle clicks on block containers
    document.addEventListener('click', function(e) {
        const blockContainer = e.target.closest('.block-container');
        if (blockContainer) {
            updateFocusedBlock(blockContainer);
        } else if (!e.target.closest('.add-content-btn')) {
            // Clear focus if clicking outside
            updateFocusedBlock(null);
            focusedBlockIndex = -1;
            const focusedInput = document.querySelector('#focused-block-index textarea');
            if (focusedInput) {
                focusedInput.value = '-1';
                focusedInput.dispatchEvent(new Event('input', { bubbles: true }));
                focusedInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    });
    
    // Remove focus highlight when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.block-container') && !e.target.closest('.add-content-btn')) {
            document.querySelectorAll('.block-container').forEach(block => {
                block.classList.remove('focused');
            });
            focusedBlockIndex = null;
            // Update hidden input
            const focusedInput = document.getElementById('focused-block-index');
            if (focusedInput) {
                const textarea = focusedInput.querySelector('textarea');
                if (textarea) {
                    textarea.value = '-1';
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        }
    });
}

// Heading block functionality (only prevent Enter key)
function initializeHeadingBlocks() {
    console.log('Initializing heading block restrictions...');
    
    function attachHeadingRestrictions() {
        const textareas = document.querySelectorAll('.block-text textarea');
        textareas.forEach(textarea => {
            const blockContainer = textarea.closest('.block-container');
            const isHeading = blockContainer && blockContainer.classList.contains('heading-block');
            
            // Remove any existing listeners to avoid duplicates
            textarea.removeEventListener('keydown', handleKeydown);
            
            function handleKeydown(e) {
                // Prevent Enter key in heading blocks
                if (isHeading && e.key === 'Enter') {
                    e.preventDefault();
                    return false;
                }
            }
            
            // Add keydown listener for heading blocks only
            if (isHeading) {
                textarea.addEventListener('keydown', handleKeydown);
            }
        });
    }
    
    // Initial attachment
    attachHeadingRestrictions();
    
    // Re-attach when DOM changes (for dynamically added blocks)
    const observer = new MutationObserver(function(mutations) {
        const hasNewTextarea = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node => 
                node.nodeType === 1 && (
                    node.matches && node.matches('.block-text textarea') ||
                    node.querySelector && node.querySelector('.block-text textarea')
                )
            );
        });
        
        if (hasNewTextarea) {
            setTimeout(attachHeadingRestrictions, 100);
        }
    });
    
    const container = document.querySelector('.main-container');
    if (container) {
        observer.observe(container, {
            childList: true,
            subtree: true
        });
    }
}

// Indentation functionality for blocks
function initializeIndentationButtons() {
    console.log('Initializing indentation buttons...');
    
    function attachIndentationHandlers() {
        // Find all indent buttons
        for (let i = 0; i < 50; i++) { // MAX_BLOCKS = 50
            const leftBtn = document.querySelector(`.indent-left-${i}`);
            const rightBtn = document.querySelector(`.indent-right-${i}`);
            
            if (leftBtn) {
                // Create closure to capture the index
                (function(index) {
                    const handleLeftClick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`Left indent clicked for block ${index}`);
                        
                        // Simple approach: find the block container in the same row as the button
                        const blockContainer = leftBtn.closest('.row').querySelector('.block-container');
                        
                        if (blockContainer) {
                            const currentMargin = parseInt(blockContainer.style.marginLeft || 0);
                            const newMargin = Math.max(0, currentMargin - 20);
                            blockContainer.style.marginLeft = newMargin + 'px';
                            console.log(`Set margin-left to ${newMargin}px for block ${index}`);
                        } else {
                            console.error('Could not find block container');
                        }
                    };
                    
                    leftBtn.removeEventListener('click', leftBtn._handleLeftClick);
                    leftBtn._handleLeftClick = handleLeftClick;
                    leftBtn.addEventListener('click', handleLeftClick);
                })(i);
            }
            
            if (rightBtn) {
                // Create closure to capture the index
                (function(index) {
                    const handleRightClick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`Right indent clicked for block ${index}`);
                        
                        // Simple approach: find the block container in the same row as the button
                        const blockContainer = rightBtn.closest('.row').querySelector('.block-container');
                        
                        if (blockContainer) {
                            const currentMargin = parseInt(blockContainer.style.marginLeft || 0);
                            const newMargin = Math.min(200, currentMargin + 20);
                            blockContainer.style.marginLeft = newMargin + 'px';
                            console.log(`Set margin-left to ${newMargin}px for block ${index}`);
                        } else {
                            console.error('Could not find block container');
                        }
                    };
                    
                    rightBtn.removeEventListener('click', rightBtn._handleRightClick);
                    rightBtn._handleRightClick = handleRightClick;
                    rightBtn.addEventListener('click', handleRightClick);
                })(i);
            }
        }
    }
    
    // Initial attachment
    attachIndentationHandlers();
    
    // Re-attach when DOM changes
    const observer = new MutationObserver(function(mutations) {
        const hasNewButtons = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node => 
                node.nodeType === 1 && (
                    node.classList && (
                        Array.from(node.classList).some(cls => cls.includes('indent-left-') || cls.includes('indent-right-'))
                    ) ||
                    node.querySelector && (
                        node.querySelector('[class*="indent-left-"]') || 
                        node.querySelector('[class*="indent-right-"]')
                    )
                )
            );
        });
        
        if (hasNewButtons) {
            setTimeout(attachIndentationHandlers, 100);
        }
    });
    
    const container = document.querySelector('.main-container');
    if (container) {
        observer.observe(container, {
            childList: true,
            subtree: true
        });
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeDragula, 1000);
    setTimeout(initializeResourceDragDrop, 1100);
    setTimeout(initializeFocusTracking, 1200);
    setTimeout(initializeHeadingBlocks, 1300);
    setTimeout(initializeIndentationButtons, 1400);
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
        setTimeout(initializeResourceDragDrop, 300);
        setTimeout(initializeFocusTracking, 400);
        setTimeout(initializeHeadingBlocks, 500);
        setTimeout(initializeIndentationButtons, 600);
    }
});

if (document.body) {
    observer.observe(document.body, {
        attributes: true,
        subtree: true,
        attributeFilter: ['style']
    });
}