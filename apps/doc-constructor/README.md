# 📝 Document Constructor App

Gradio web interface for creating documents with draggable, reorderable text blocks.

## Quick Start

```bash
# From this directory
make install          # Install dependencies
make run             # Launch app

# Or using the installed command
doc-constructor-app
```

## Features

- Start with a single text block, add unlimited blocks
- Drag and drop blocks to reorder
- Text content preserved during all operations
- Smart delete controls (last block can't be deleted)
- Export combined document

## Purpose

A Gradio interface for creating documents by managing reorderable text content blocks where users can write, add, delete, and rearrange blocks dynamically.

## Initial State

- Single default content block with empty text area for user input
- This initial block cannot be deleted (no delete option shown)
- Has a '+' button to add new blocks

## Core Behaviors

### Adding Blocks

- Each block has a '+' button in lower right that creates a new empty block immediately after it
- Once 2+ blocks exist, all blocks show an 'x' delete button in upper right
- New blocks are created with empty text areas ready for user input

### Deleting Blocks

- 'x' delete button appears on all blocks when 2+ blocks exist
- When only 1 block remains, its 'x' button is greyed out/disabled
- Deleting a block preserves all text in remaining blocks

### Text Editing

- Each block contains a text area where users can type freely
- Text content is preserved during all operations (add, delete, reorder)
- Text areas should be responsive and allow multi-line input

### Drag & Drop Reordering

- All blocks can be dragged to new positions
- Visual feedback during drag (cursor change, highlight drop zones)
- Text content remains intact during reordering
- Smooth animation for position changes

## Technical Requirements

- Maintain unique IDs for each block to preserve text during reordering
- State management to track block order and content
- Real-time UI updates on all operations

## Dependencies

- Gradio
- JavaScript drag-and-drop library (if Gradio's native components cannot handle drag/drop)
  - Acceptable to use SortableJS or similar for drag functionality
  - Must preserve Gradio's state management and text content
