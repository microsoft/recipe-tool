"""Minimal tests for UI components."""

from unittest.mock import MagicMock, patch
from document_generator_app.ui import create_resource_editor, create_section_editor


@patch("document_generator_app.ui.gr")
def test_create_resource_editor(mock_gr):
    """Test that resource editor creates a dictionary of components."""
    # Mock gradio components to avoid page attribute issues
    mock_gr.Column.return_value.__enter__.return_value = MagicMock()
    mock_gr.Textbox.return_value = MagicMock()
    mock_gr.TextArea.return_value = MagicMock()
    mock_gr.File.return_value = MagicMock()
    mock_gr.Radio.return_value = MagicMock()
    mock_gr.Markdown.return_value = MagicMock()
    mock_gr.Tabs.return_value.__enter__.return_value = MagicMock()
    mock_gr.TabItem.return_value.__enter__.return_value = MagicMock()

    editor = create_resource_editor()
    assert isinstance(editor, dict)
    assert "container" in editor
    assert "key" in editor
    assert "description" in editor
    assert "path" in editor
    assert "file" in editor
    assert "file_source_tabs" in editor


@patch("document_generator_app.ui.gr")
def test_create_section_editor(mock_gr):
    """Test that section editor creates a dictionary of components."""
    # Mock gradio components to avoid page attribute issues
    mock_gr.Column.return_value.__enter__.return_value = MagicMock()
    mock_gr.Textbox.return_value = MagicMock()
    mock_gr.TextArea.return_value = MagicMock()
    mock_gr.Radio.return_value = MagicMock()
    mock_gr.Dropdown.return_value = MagicMock()
    mock_gr.Markdown.return_value = MagicMock()
    mock_gr.Tabs.return_value.__enter__.return_value = MagicMock()
    mock_gr.TabItem.return_value.__enter__.return_value = MagicMock()

    editor = create_section_editor()
    assert isinstance(editor, dict)
    assert "container" in editor
    assert "title" in editor
    assert "content_mode_tabs" in editor
    assert "prompt" in editor
    assert "refs" in editor
    assert "resource_key" in editor
    assert "prompt_tab" in editor
    assert "static_tab" in editor
