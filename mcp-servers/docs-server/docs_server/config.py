"""Configuration for the documentation server."""

from pathlib import Path
from typing import List, Union, Sequence

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DocsServerSettings(BaseSettings):
    """Settings for the documentation server."""

    model_config = SettingsConfigDict(
        env_prefix="DOCS_SERVER_",
        env_file=".env",
        extra="ignore",
    )

    # Paths to documentation files or URLs
    doc_paths: Sequence[Union[Path, str]] = Field(
        default_factory=lambda: [Path(".")],
        description="List of paths to documentation files/directories or URLs",
    )

    @field_validator("doc_paths", mode="before")
    def validate_doc_paths(cls, v):
        """Convert doc_paths to appropriate types."""
        if not isinstance(v, list):
            v = [v]

        result = []
        for item in v:
            if isinstance(item, str) and item.startswith(("http://", "https://")):
                # Keep URLs as strings
                result.append(item)
            else:
                # Convert file paths to Path objects
                result.append(Path(item))
        return result

    # File patterns to include
    include_patterns: List[str] = Field(
        default_factory=lambda: ["*.md", "*.txt", "*.rst"],
        description="File patterns to include when scanning directories",
    )

    # File patterns to exclude
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [".*", "__pycache__", "*.pyc"],
        description="File patterns to exclude when scanning directories",
    )

    # Maximum file size to process (in bytes)
    max_file_size: int = Field(
        default=2 * 1024 * 1024,  # 2MB
        description="Maximum file size to process in bytes",
    )

    # Server settings
    host: str = Field(
        default="localhost",
        description="Host for SSE server",
    )

    port: int = Field(
        default=3003,
        description="Port for SSE server",
    )

    # Cache settings
    enable_cache: bool = Field(
        default=True,
        description="Enable caching of documentation content",
    )

    cache_ttl: int = Field(
        default=300,  # 5 minutes
        description="Cache time-to-live in seconds",
    )
