"""Tests for the RecipeExecutorCore class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from recipe_executor_app.core import RecipeExecutorCore


@pytest.fixture
def recipe_core():
    """Create a RecipeExecutorCore instance for testing."""
    # Mock the Executor
    with patch("recipe_executor_app.core.Executor") as mock_executor_class:
        # Create a mock executor instance
        mock_executor = MagicMock()
        mock_executor.execute = AsyncMock()
        mock_executor_class.return_value = mock_executor

        # Create the core with the mocked executor
        core = RecipeExecutorCore()

        # Return both the core and the mock for assertions
        yield core, mock_executor


class TestRecipeExecutorCore:
    """Tests for the RecipeExecutorCore class."""

    @pytest.mark.asyncio
    async def test_execute_recipe_from_file(self, recipe_core):
        """Test executing a recipe from a file."""
        # Setup
        core, mock_executor = recipe_core
        recipe_file = "/path/to/recipe.json"
        context_vars = "key1=value1,key2=value2"

        # Mock context.dict() to return a dictionary
        mock_executor.execute.return_value = None
        mock_context_dict = {"key1": "value1", "key2": "value2", "output": "Test output"}
        with patch("recipe_executor_app.core.Context") as mock_context_class:
            mock_context = MagicMock()
            mock_context.dict.return_value = mock_context_dict
            mock_context_class.return_value = mock_context

            # Execute
            result = await core.execute_recipe(recipe_file, None, context_vars)

            # Verify
            assert "formatted_results" in result
            assert "raw_json" in result
            assert "debug_context" in result
            assert "Test output" in result["formatted_results"]
            mock_executor.execute.assert_called_once_with(recipe_file, mock_context)

    @pytest.mark.asyncio
    async def test_execute_recipe_from_text(self, recipe_core):
        """Test executing a recipe from text."""
        # Setup
        core, mock_executor = recipe_core
        recipe_text = '{"steps": []}'
        context_vars = "key1=value1"

        # Mock the temporary file creation
        mock_temp_path = "/tmp/recipe_12345.json"
        with patch("recipe_executor_app.core.create_temp_file") as mock_create_temp:
            mock_create_temp.return_value = (mock_temp_path, lambda: None)

            # Mock context.dict() to return a dictionary
            mock_executor.execute.return_value = None
            mock_context_dict = {"key1": "value1", "result": "Test result"}
            with patch("recipe_executor_app.core.Context") as mock_context_class:
                mock_context = MagicMock()
                mock_context.dict.return_value = mock_context_dict
                mock_context_class.return_value = mock_context

                # Execute
                result = await core.execute_recipe(None, recipe_text, context_vars)

                # Verify
                assert "formatted_results" in result
                assert "raw_json" in result
                assert "debug_context" in result
                assert "Test result" in result["formatted_results"]
                mock_executor.execute.assert_called_once_with(mock_temp_path, mock_context)

    @pytest.mark.asyncio
    async def test_execute_recipe_with_error(self, recipe_core):
        """Test executing a recipe that raises an error."""
        # Setup
        core, mock_executor = recipe_core
        recipe_file = "/path/to/recipe.json"

        # Make the executor raise an exception
        mock_executor.execute.side_effect = ValueError("Test error")

        # Execute
        result = await core.execute_recipe(recipe_file, None, None)

        # Verify
        assert "formatted_results" in result
        assert "Error" in result["formatted_results"]
        assert "Test error" in result["formatted_results"]

    @pytest.mark.asyncio
    async def test_execute_recipe_no_input(self, recipe_core):
        """Test executing a recipe with no file or text input."""
        # Setup
        core, _ = recipe_core

        # Execute
        result = await core.execute_recipe(None, None, None)

        # Verify
        assert "formatted_results" in result
        assert "Error" in result["formatted_results"]
        assert "No recipe provided" in result["formatted_results"]

    @pytest.mark.asyncio
    async def test_load_recipe(self, recipe_core):
        """Test loading a recipe file."""
        # Setup
        core, _ = recipe_core
        recipe_path = "/path/to/recipe.json"
        recipe_content = '{"name": "Test Recipe", "description": "A test recipe", "steps": []}'

        # Mock the file operations
        with (
            patch("os.path.exists") as mock_exists,
            patch("recipe_executor_app.core.read_file") as mock_read_file,
        ):
            # Set up the mocks - the function tries multiple paths
            mock_exists.return_value = True
            mock_read_file.return_value = recipe_content

            # Execute
            result = await core.load_recipe(recipe_path)

            # Verify
            assert "recipe_content" in result
            assert "structure_preview" in result
            assert result["recipe_content"] == recipe_content
            assert "Test Recipe" in result["structure_preview"]
            assert "A test recipe" in result["structure_preview"]

    # Test removed - find_examples method no longer exists in RecipeExecutorCore
    # Examples are now configured through settings.example_recipes
