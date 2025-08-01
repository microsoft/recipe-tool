#!/usr/bin/env python3
"""
Script to refresh example docpacks from source JSON files.

This script converts the example JSON files in the recipes directory
to .docpack files in the document-generator app examples directory.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from document_generator_app.package_handler import DocpackHandler  # noqa: E402


def get_recipe_examples_dir() -> Path:
    """Get the path to the recipe examples directory."""
    # From apps/document-generator, go to repo root then recipes
    app_dir = Path(__file__).parent.parent
    repo_root = app_dir.parent.parent
    return repo_root / "recipes" / "document_generator" / "examples"


def get_app_examples_dir() -> Path:
    """Get the path to the app examples directory."""
    return Path(__file__).parent.parent / "examples"


def convert_paths_for_docpack(outline_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert file paths in outline to simple filenames for docpack format.

    This removes directory paths since docpacks store files with simple names.
    """
    converted = outline_data.copy()

    if "resources" in converted:
        for resource in converted["resources"]:
            if "path" in resource and resource["path"]:
                # Convert path to just filename
                original_path = Path(resource["path"])
                resource["path"] = original_path.name

    return converted


def collect_resource_files(outline_data: Dict[str, Any], base_dir: Path) -> List[Path]:
    """Collect actual resource files referenced in the outline.

    Args:
        outline_data: The outline JSON data
        base_dir: Base directory to resolve relative paths from

    Returns:
        List of resource file paths that exist
    """
    resource_files = []

    if "resources" in outline_data:
        for resource in outline_data["resources"]:
            if "path" in resource and resource["path"]:
                # Resolve the path relative to the base directory
                resource_path = base_dir / resource["path"]

                if resource_path.exists():
                    resource_files.append(resource_path)
                    print(f"    Found resource: {resource_path}")
                else:
                    print(f"    ⚠️  Resource not found: {resource_path}")

    return resource_files


def refresh_examples():
    """Refresh all example docpacks from source JSON files."""
    recipe_examples_dir = get_recipe_examples_dir()
    app_examples_dir = get_app_examples_dir()

    # Ensure app examples directory exists
    app_examples_dir.mkdir(exist_ok=True)

    # Find all JSON files in recipe examples
    json_files = list(recipe_examples_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON example files found in {recipe_examples_dir}")
        return

    print(f"Found {len(json_files)} example files to convert:")

    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        try:
            # Load the JSON outline
            with open(json_file, "r") as f:
                outline_data = json.load(f)

            # Collect actual resource files (before path conversion)
            repo_root = get_recipe_examples_dir().parent.parent.parent
            resource_files = collect_resource_files(outline_data, repo_root)

            # Convert paths for docpack format
            converted_outline = convert_paths_for_docpack(outline_data)

            # Create docpack filename
            docpack_name = json_file.stem + ".docpack"
            docpack_path = app_examples_dir / docpack_name

            # Create the docpack with bundled resource files
            DocpackHandler.create_package(converted_outline, resource_files, docpack_path)

            print(f"  ✓ Created: {docpack_path}")
            print(f"    Title: {outline_data.get('title', 'N/A')}")
            print(f"    Resources: {len(outline_data.get('resources', []))} ({len(resource_files)} bundled)")
            print(f"    Sections: {len(outline_data.get('sections', []))}")

        except Exception as e:
            print(f"  ✗ Error processing {json_file.name}: {e}")

    print(f"\n✓ Refresh complete. Docpacks saved to: {app_examples_dir}")


if __name__ == "__main__":
    refresh_examples()
