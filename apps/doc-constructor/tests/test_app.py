"""Tests for the Document Constructor app."""

import pytest
from doc_constructor_app.app import (
    initialize_blocks,
    add_block_after,
    delete_block,
    update_block_content,
    reorder_blocks
)


def test_initialize_blocks():
    """Test that initial blocks are created correctly."""
    blocks = initialize_blocks()
    assert len(blocks) == 1
    assert 'id' in blocks[0]
    assert blocks[0]['content'] == ''


def test_add_block_after():
    """Test adding a block after a specific block."""
    blocks = initialize_blocks()
    original_id = blocks[0]['id']
    
    new_blocks = add_block_after(blocks, original_id)
    assert len(new_blocks) == 2
    assert new_blocks[0]['id'] == original_id
    assert new_blocks[1]['id'] != original_id
    assert new_blocks[1]['content'] == ''


def test_delete_block():
    """Test deleting blocks."""
    # Start with two blocks
    blocks = initialize_blocks()
    blocks = add_block_after(blocks, blocks[0]['id'])
    assert len(blocks) == 2
    
    # Delete one block
    remaining = delete_block(blocks, blocks[0]['id'])
    assert len(remaining) == 1
    assert remaining[0]['id'] == blocks[1]['id']
    
    # Try to delete the last block (should not delete)
    still_one = delete_block(remaining, remaining[0]['id'])
    assert len(still_one) == 1


def test_update_block_content():
    """Test updating block content."""
    blocks = initialize_blocks()
    block_id = blocks[0]['id']
    
    updated = update_block_content(blocks, block_id, "New content")
    assert updated[0]['content'] == "New content"


def test_reorder_blocks():
    """Test reordering blocks."""
    # Create three blocks
    blocks = initialize_blocks()
    blocks = add_block_after(blocks, blocks[0]['id'])
    blocks = add_block_after(blocks, blocks[1]['id'])
    
    # Get original order
    original_ids = [b['id'] for b in blocks]
    
    # Reverse the order
    new_order = original_ids[::-1]
    reordered = reorder_blocks(blocks, new_order)
    
    # Check new order
    assert [b['id'] for b in reordered] == new_order
    # Check content is preserved
    for i, block_id in enumerate(new_order):
        original_block = next(b for b in blocks if b['id'] == block_id)
        assert reordered[i]['content'] == original_block['content']