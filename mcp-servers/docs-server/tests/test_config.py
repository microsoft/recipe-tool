"""Tests for configuration."""

from pathlib import Path

from docs_server.config import DocsServerSettings


def test_default_settings():
    """Test default settings."""
    settings = DocsServerSettings()

    assert settings.doc_paths == [Path(".")]
    assert settings.include_patterns == ["*.md", "*.txt", "*.rst"]
    assert settings.exclude_patterns == [".*", "__pycache__", "*.pyc"]
    assert settings.max_file_size == 2 * 1024 * 1024
    assert settings.host == "localhost"
    assert settings.port == 3003
    assert settings.enable_cache is True
    assert settings.cache_ttl == 300


def test_custom_settings():
    """Test custom settings."""
    settings = DocsServerSettings(
        doc_paths=[Path("/docs"), Path("/readme.md")],
        include_patterns=["*.md"],
        port=8080,
        enable_cache=False,
    )

    assert settings.doc_paths == [Path("/docs"), Path("/readme.md")]
    assert settings.include_patterns == ["*.md"]
    assert settings.port == 8080
    assert settings.enable_cache is False
