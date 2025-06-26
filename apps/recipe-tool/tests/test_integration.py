"""Integration tests for the recipe_tool_app package."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_executor():
    """Create a mock Executor that can be used across tests."""
    executor = AsyncMock()
    executor.execute = AsyncMock()
    return executor


@pytest.mark.asyncio
async def test_core_to_utils_integration(mock_executor):
    """Test integration between core and utils from recipe-executor."""
    from recipe_tool_app.core import RecipeToolCore
    from recipe_tool_app.recipe_processor import find_recipe_output, generate_preview

    # Create core with mock executor (not used in these tests but verifies it can be created)
    _ = RecipeToolCore(executor=mock_executor)

    # Test that find_recipe_output works
    with patch("recipe_tool_app.recipe_processor.read_file") as mock_read:
        mock_read.return_value = '{"name": "Test"}'
        # Create a mock FileSpec object
        mock_filespec = MagicMock()
        mock_filespec.path = "test.json"
        context = {"generated_recipe": [mock_filespec], "output_root": "output"}
        result = find_recipe_output(context)
        assert result == '{"name": "Test"}'

    # Test that generate_preview works
    recipe = {"name": "Test", "steps": []}
    preview = generate_preview(recipe, 1.0)
    assert "Test" in preview
    assert "**Steps**: 0" in preview


@pytest.mark.asyncio
async def test_recipe_creation_flow():
    """Test the complete recipe creation flow."""
    from recipe_tool_app.core import RecipeToolCore

    # Create a mock executor
    mock_executor = MagicMock()
    mock_executor.execute = MagicMock()

    # Create core instance
    core = RecipeToolCore(executor=mock_executor)

    # Test with no input
    result = await core.create_recipe(idea_text="", idea_file=None, reference_files=None, context_vars=None)

    # Verify error response
    assert result["recipe_json"] == ""
    assert "Error" in result["structure_preview"]
    assert "No idea provided" in result["structure_preview"]


def test_recipe_executor_integration():
    """Test that recipe-executor components can be imported and used."""
    # Import recipe-executor components
    from recipe_executor_app.app import create_executor_block
    from recipe_executor_app.core import RecipeExecutorCore

    # Verify they are callable
    assert callable(create_executor_block)
    assert callable(RecipeExecutorCore)

    # Create an instance to verify it works
    core = RecipeExecutorCore()
    assert hasattr(core, "execute_recipe")
    assert hasattr(core, "load_recipe")
