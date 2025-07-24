#!/usr/bin/env python3
"""Command-line interface for docpack operations."""

import argparse
import json
import sys
from pathlib import Path

from .handler import DocpackHandler


def cmd_create(args):
    """Create a docpack from an outline JSON file."""
    outline_path = Path(args.outline)
    output_path = Path(args.output)
    
    if not outline_path.exists():
        print(f"Error: Outline file not found: {outline_path}", file=sys.stderr)
        return 1
    
    # Load outline data
    with open(outline_path, "r") as f:
        outline_data = json.load(f)
    
    # Collect resource files
    resource_files = []
    for resource in outline_data.get("resources", []):
        resource_path = Path(resource.get("path", ""))
        if resource_path.exists():
            resource_files.append(resource_path)
        else:
            print(f"Warning: Resource file not found: {resource_path}", file=sys.stderr)
    
    # Create the docpack
    try:
        DocpackHandler.create_package(
            outline_data=outline_data,
            resource_files=resource_files,
            output_path=output_path
        )
        print(f"Created docpack: {output_path}")
        return 0
    except Exception as e:
        print(f"Error creating docpack: {e}", file=sys.stderr)
        return 1


def cmd_extract(args):
    """Extract a docpack to a directory."""
    package_path = Path(args.package)
    extract_dir = Path(args.dir)
    
    if not package_path.exists():
        print(f"Error: Package file not found: {package_path}", file=sys.stderr)
        return 1
    
    try:
        outline_data, resource_files = DocpackHandler.extract_package(package_path, extract_dir)
        print(f"Extracted to: {extract_dir}")
        print(f"Outline: {extract_dir / 'outline.json'}")
        print(f"Resources: {len(resource_files)} files")
        return 0
    except Exception as e:
        print(f"Error extracting docpack: {e}", file=sys.stderr)
        return 1


def cmd_validate(args):
    """Validate a docpack file."""
    package_path = Path(args.package)
    
    if not package_path.exists():
        print(f"Error: Package file not found: {package_path}", file=sys.stderr)
        return 1
    
    if DocpackHandler.validate_package(package_path):
        print(f"Valid docpack: {package_path}")
        return 0
    else:
        print(f"Invalid docpack: {package_path}", file=sys.stderr)
        return 1


def cmd_list(args):
    """List contents of a docpack."""
    package_path = Path(args.package)
    
    if not package_path.exists():
        print(f"Error: Package file not found: {package_path}", file=sys.stderr)
        return 1
    
    try:
        contents = DocpackHandler.list_package_contents(package_path)
        print(f"Docpack: {package_path}")
        print(f"Outline files: {', '.join(contents['outline'])}")
        print(f"Resources ({len(contents['resources'])} files):")
        for resource in contents['resources']:
            print(f"  - {resource}")
        return 0
    except Exception as e:
        print(f"Error listing docpack: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for the docpack CLI."""
    parser = argparse.ArgumentParser(description="Docpack file management tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a docpack from an outline")
    create_parser.add_argument("--outline", "-o", required=True, help="Path to outline.json file")
    create_parser.add_argument("--output", "-p", required=True, help="Output docpack file path")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract a docpack")
    extract_parser.add_argument("package", help="Path to .docpack file")
    extract_parser.add_argument("--dir", "-d", default=".", help="Directory to extract to")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a docpack")
    validate_parser.add_argument("package", help="Path to .docpack file")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List docpack contents")
    list_parser.add_argument("package", help="Path to .docpack file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handlers
    commands = {
        "create": cmd_create,
        "extract": cmd_extract,
        "validate": cmd_validate,
        "list": cmd_list,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())