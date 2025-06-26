"""Tests for the app module."""

from unittest.mock import MagicMock, patch


class TestMain:
    """Tests for main function."""

    @patch("recipe_tool_app.app.argparse.ArgumentParser")
    @patch("recipe_tool_app.app.create_app")
    @patch("recipe_tool_app.app.settings")
    def test_main_with_args(self, mock_settings, mock_create_app, mock_parser_class):
        """Test main function with command line arguments."""
        # Setup
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_args = MagicMock(host="127.0.0.1", port=8080, no_mcp=True, debug=True)
        mock_parser.parse_args.return_value = mock_args

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        mock_settings.to_launch_kwargs.return_value = {}

        # Import and call main
        from recipe_tool_app.app import main

        main()

        # Verify settings were updated
        assert mock_settings.host == "127.0.0.1"
        assert mock_settings.port == 8080
        assert mock_settings.mcp_server is False
        assert mock_settings.debug is True

        # Verify app was launched
        mock_app.launch.assert_called_once()
