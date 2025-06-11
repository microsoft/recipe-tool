# Document Constructor - Draggable Blocks Component

## Purpose

A Gradio interface for constructing documents by arranging different types of text/content blocks through drag and drop.

## Inputs

- Initial blocks data (list of dicts with type, content, position)
- Block type selector (heading, content, image, grid, blank)
- Add new block button

## Outputs

- Ordered list of blocks with their content
- Export button to generate final document

## Behavior

1. Display blocks vertically in order
2. Each block shows type indicator and content preview
3. Hover shows grab cursor
4. Drag to reorder blocks
5. Click block to edit content
6. Delete button on each block

## Block Types

- **Heading**: Optional section headers
- **Content**: Main text/instructions
- **Image**: Placeholder or uploaded images
- **Grid**: Table/grid layout blocks
- **Blank**: Spacer blocks

## Dependencies

- Gradio
- No external drag libraries (use Gradio's native components)
