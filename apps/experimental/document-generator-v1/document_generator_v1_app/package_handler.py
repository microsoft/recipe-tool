"""Package handler for .docpack files.

Handles creation and extraction of .docpack files which are zip archives
containing an outline.json file and associated resource files.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DocpackHandler:
    """Handles .docpack file creation and extraction."""

    @staticmethod
    def create_package(outline_data: Dict[str, Any], resource_files: List[Path], output_path: Path) -> None:
        """Create a .docpack file from outline data and resource files.

        Args:
            outline_data: The outline JSON data
            resource_files: List of resource file paths to include
            output_path: Where to save the .docpack file
        """
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Always include outline.json
            zf.writestr("outline.json", json.dumps(outline_data, indent=2))

            # Add resource files with their original names
            for resource_file in resource_files:
                if resource_file.exists():
                    zf.write(resource_file, resource_file.name)

    @staticmethod
    def extract_package(package_path: Path, extract_dir: Path) -> Tuple[Dict[str, Any], List[Path]]:
        """Extract a .docpack file to a directory with organized structure.

        Args:
            package_path: Path to the .docpack file
            extract_dir: Session directory to extract to

        Returns:
            Tuple of (outline_data, list_of_resource_file_paths)
        """
        extract_dir.mkdir(parents=True, exist_ok=True)

        # Create files subdirectory for uploaded files
        files_dir = extract_dir / "files"
        files_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(package_path, "r") as zf:
            # Extract outline.json to extract_dir
            if "outline.json" in zf.namelist():
                zf.extract("outline.json", extract_dir)

            # Extract all other files to files/ subdirectory
            for file_info in zf.filelist:
                if file_info.filename != "outline.json":
                    # Extract to files directory
                    file_info.filename = Path(file_info.filename).name  # Remove any path components
                    zf.extract(file_info, files_dir)

        # Read outline.json
        outline_path = extract_dir / "outline.json"
        if not outline_path.exists():
            raise ValueError("Package does not contain outline.json")

        with open(outline_path, "r") as f:
            outline_data = json.load(f)

        # Find all resource files in files directory
        resource_files = [f for f in files_dir.iterdir() if f.is_file()]

        return outline_data, resource_files

    @staticmethod
    def validate_package(package_path: Path) -> bool:
        """Validate that a file is a valid .docpack.

        Args:
            package_path: Path to check

        Returns:
            True if valid .docpack, False otherwise
        """
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                files = zf.namelist()
                return "outline.json" in files
        except zipfile.BadZipFile:
            return False
