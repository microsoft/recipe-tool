"""Minimal tests for UI components."""

from document_generator_app.ui import create_resource_editor, create_section_editor


def test_create_resource_editor():
    """Test that resource editor creates a dictionary of components."""
    editor = create_resource_editor()
    assert isinstance(editor, dict)
    assert "container" in editor
    assert "key" in editor
    assert "description" in editor
    assert "path" in editor
    assert "file" in editor
    assert "merge_mode" in editor


def test_create_section_editor():
    """Test that section editor creates a dictionary of components."""
    editor = create_section_editor()
    assert isinstance(editor, dict)
    assert "container" in editor
    assert "title" in editor
    assert "mode" in editor
    assert "prompt" in editor
    assert "refs" in editor
    assert "resource_key" in editor
