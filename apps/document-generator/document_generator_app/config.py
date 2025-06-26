"""Configuration settings for the Document Generator app."""

from typing import NamedTuple, List


class ExampleOutline(NamedTuple):
    """Configuration for an example document outline."""

    name: str
    path: str


class Settings:
    """Configuration settings for the Document Generator app."""

    # App settings
    app_title: str = "Document Generator"
    app_description: str = "Create structured documents with AI assistance"

    # Example outlines
    example_outlines: List[ExampleOutline] = [
        ExampleOutline(
            name="README Generator",
            path="../../recipes/document_generator/examples/readme.json",
        ),
        ExampleOutline(
            name="Product Launch Documentation",
            path="../../recipes/document_generator/examples/launch-documentation.json",
        ),
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.


# Create global settings instance
settings = Settings()
