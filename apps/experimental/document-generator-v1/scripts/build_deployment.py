#!/usr/bin/env python3
"""
Build script for Document Generator deployment.

This script prepares the document generator app for deployment by:
1. Bundling recipe files from the main recipes directory
2. Refreshing example docpacks with latest content
3. Creating a self-contained deployment package

Usage:
    python scripts/build_deployment.py
    make build
"""

import shutil
import sys
from pathlib import Path
import json

# Add the parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.refresh_examples import (  # noqa: E402
    collect_resource_files,
    convert_paths_for_docpack,
)
from document_generator_v1_app.package_handler import DocpackHandler  # noqa: E402


def get_repo_root() -> Path:
    """Get the repository root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / ".git").exists():
            return current
        # Also check for specific repo markers
        if (current / "recipes").exists() and (current / "apps").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find repository root")


def bundle_recipes(app_dir: Path, repo_root: Path) -> None:
    """Bundle recipe files into the app package."""
    print("📦 Bundling recipe files...")

    # Source and destination paths
    recipes_source = repo_root / "recipes" / "document_generator"
    recipes_dest = app_dir / "document_generator_v1_app" / "recipes"

    # Clean destination directory
    if recipes_dest.exists():
        shutil.rmtree(recipes_dest)

    # Copy recipe files
    recipes_dest.mkdir(parents=True, exist_ok=True)

    # Copy main recipe file
    main_recipe = recipes_source / "document_generator_recipe.json"
    if main_recipe.exists():
        shutil.copy2(main_recipe, recipes_dest / "document_generator_recipe.json")
        print(f"    Copied: {main_recipe.name}")
    else:
        print(f"    Warning: Main recipe not found at {main_recipe}")

    # Copy recipes subdirectory
    recipes_subdir_source = recipes_source / "recipes"
    recipes_subdir_dest = recipes_dest / "recipes"

    if recipes_subdir_source.exists():
        shutil.copytree(recipes_subdir_source, recipes_subdir_dest)
        recipe_files = list(recipes_subdir_dest.glob("*.json"))
        print(f"    Copied {len(recipe_files)} recipe files:")
        for recipe_file in sorted(recipe_files):
            print(f"      - {recipe_file.name}")
    else:
        print(f"    Warning: Recipes subdirectory not found at {recipes_subdir_source}")

    print(f"    ✓ Recipes bundled to: {recipes_dest}")


def refresh_examples(app_dir: Path, repo_root: Path) -> None:
    """Refresh example docpacks with latest content."""
    print("📄 Refreshing example docpacks...")

    # Source and destination paths
    examples_source = repo_root / "recipes" / "document_generator" / "examples"
    examples_dest = app_dir / "examples"

    # Clean destination directory
    if examples_dest.exists():
        shutil.rmtree(examples_dest)
    examples_dest.mkdir(parents=True, exist_ok=True)

    # Find all example JSON files
    example_files = list(examples_source.glob("*.json"))

    if not example_files:
        print(f"    Warning: No example files found in {examples_source}")
        return

    print(f"    Found {len(example_files)} example files:")

    for json_file in sorted(example_files):
        print(f"      Processing: {json_file.name}")

        try:
            # Load the JSON outline
            with open(json_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)

            # Collect referenced resource files (before path conversion)
            # Resource paths in JSON are relative to repo root, not examples directory
            resource_files = collect_resource_files(outline_data, repo_root)

            # Convert file paths to simple filenames for docpack format
            converted_outline = convert_paths_for_docpack(outline_data)

            # Create docpack filename
            docpack_name = json_file.stem + ".docpack"
            docpack_path = examples_dest / docpack_name

            # Create the docpack
            DocpackHandler.create_package(converted_outline, resource_files, docpack_path)

            print(f"        ✓ Created: {docpack_name}")
            if resource_files:
                print(f"          Bundled {len(resource_files)} resource files")

        except Exception as e:
            print(f"        ✗ Error processing {json_file.name}: {e}")

    print(f"    ✓ Examples refreshed in: {examples_dest}")


def create_gitignore_entry(app_dir: Path) -> None:
    """Add bundled recipes to .gitignore."""
    gitignore_path = app_dir / ".gitignore"
    recipes_entry = "document_generator_v1_app/recipes/"

    # Read existing .gitignore
    existing_lines = []
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_lines = [line.rstrip() for line in f.readlines()]

    # Add recipes entry if not present
    if recipes_entry not in existing_lines:
        existing_lines.append("")
        existing_lines.append("# Bundled recipes (generated by build script)")
        existing_lines.append(recipes_entry)

        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("\n".join(existing_lines) + "\n")

        print("    ✓ Added recipes to .gitignore")


def verify_build(app_dir: Path) -> bool:
    """Verify that the build completed successfully."""
    print("🔍 Verifying build...")

    errors = []

    # Check recipes directory
    recipes_dir = app_dir / "document_generator_v1_app" / "recipes"
    if not recipes_dir.exists():
        errors.append("Recipes directory not found")
    else:
        main_recipe = recipes_dir / "document_generator_recipe.json"
        if not main_recipe.exists():
            errors.append("Main recipe file not found")

        recipes_subdir = recipes_dir / "recipes"
        if not recipes_subdir.exists():
            errors.append("Recipes subdirectory not found")
        else:
            recipe_files = list(recipes_subdir.glob("*.json"))
            if len(recipe_files) < 7:  # Expected number of sub-recipes
                errors.append(f"Expected 7+ recipe files, found {len(recipe_files)}")

    # Check examples directory
    examples_dir = app_dir / "examples"
    if not examples_dir.exists():
        errors.append("Examples directory not found")
    else:
        docpack_files = list(examples_dir.glob("*.docpack"))
        if len(docpack_files) == 0:
            errors.append("No docpack files found in examples")

    if errors:
        print("    ✗ Build verification failed:")
        for error in errors:
            print(f"      - {error}")
        return False
    else:
        print("    ✓ Build verification passed")
        return True


def main():
    """Main build script execution."""
    print("🚀 Building Document Generator deployment package...\n")

    try:
        # Get paths
        app_dir = Path(__file__).parent.parent
        repo_root = get_repo_root()

        print(f"App directory: {app_dir}")
        print(f"Repository root: {repo_root}\n")

        # Bundle recipes
        bundle_recipes(app_dir, repo_root)
        print()

        # Refresh examples
        refresh_examples(app_dir, repo_root)
        print()

        # Update .gitignore
        create_gitignore_entry(app_dir)
        print()

        # Verify build
        success = verify_build(app_dir)
        print()

        if success:
            print("✅ Build completed successfully!")
            print(f"📁 Deployment package ready in: {app_dir}")
            print("\nThe app is now self-contained and ready for deployment.")
            print("All recipe files and examples are bundled within the app directory.")
        else:
            print("❌ Build failed! See errors above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Build failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
