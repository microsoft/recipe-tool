"""Package handler for .docpack files with conflict-safe file naming.

Handles creation and extraction of .docpack files which are zip archives
containing an outline.json file and associated resource files.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class DocpackHandler:
    """Handles .docpack file creation and extraction with filename conflict resolution."""

    @staticmethod
    def create_package(
        outline_data: Dict[str, Any],
        resource_files: List[Path],
        output_path: Path,
        resource_key_map: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a .docpack file from outline data and resource files.

        This version handles filename conflicts by using resource keys as prefixes.

        Args:
            outline_data: The outline JSON data
            resource_files: List of resource file paths to include
            output_path: Where to save the .docpack file
            resource_key_map: Optional mapping of file paths to resource keys
        """
        # Track used archive names to ensure uniqueness
        used_names = set()
        path_to_archive_name = {}

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Process resources to handle potential filename conflicts
            for i, resource_file in enumerate(resource_files):
                if not resource_file.exists():
                    continue

                original_path_str = str(resource_file)

                # Keep original filename, handle conflicts with counter suffix only if needed
                archive_name = resource_file.name

                # Only add suffix if there's a conflict
                if archive_name in used_names:
                    base_stem = resource_file.stem
                    suffix = resource_file.suffix
                    counter = 1

                    # Find a unique name
                    while archive_name in used_names:
                        archive_name = f"{base_stem}_{counter}{suffix}"
                        counter += 1

                used_names.add(archive_name)
                path_to_archive_name[original_path_str] = archive_name

                # Write file to archive
                zf.write(resource_file, archive_name)

            # Update resource paths in outline data
            updated_outline = json.loads(json.dumps(outline_data))  # Deep copy
            for resource in updated_outline.get("resources", []):
                original_path = resource.get("path", "")
                if original_path in path_to_archive_name:
                    resource["path"] = path_to_archive_name[original_path]

            # Write outline.json
            zf.writestr("outline.json", json.dumps(updated_outline, indent=2))

    @staticmethod
    def extract_package(package_path: Path, extract_dir: Path) -> Tuple[Dict[str, Any], List[Path]]:
        """Extract a .docpack file and return outline data and extracted files.

        Args:
            package_path: Path to the .docpack file
            extract_dir: Directory to extract files to

        Returns:
            Tuple of (outline_data, list_of_extracted_file_paths)
        """
        extracted_files = []

        with zipfile.ZipFile(package_path, "r") as zf:
            # Extract all files
            for member in zf.namelist():
                if member != "outline.json":
                    # Extract resource file
                    zf.extract(member, extract_dir)
                    extracted_path = extract_dir / member
                    extracted_files.append(extracted_path)

            # Read and parse outline.json
            outline_json = zf.read("outline.json")
            outline_data = json.loads(outline_json)

            # Update resource paths to absolute paths
            for resource in outline_data.get("resources", []):
                archive_name = resource.get("path", "")
                if archive_name:
                    resource["path"] = str(extract_dir / archive_name)

        return outline_data, extracted_files