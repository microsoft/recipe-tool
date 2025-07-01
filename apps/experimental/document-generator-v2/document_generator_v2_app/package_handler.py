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
        resource_key_map: Optional[Dict[str, str]] = None
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
                
                # Determine archive name with conflict resolution
                if resource_key_map and original_path_str in resource_key_map:
                    # Use resource key as prefix
                    resource_key = resource_key_map[original_path_str]
                    archive_name = f"{resource_key}_{resource_file.name}"
                else:
                    # Fallback: use index as prefix if no key available
                    archive_name = f"resource_{i+1}_{resource_file.name}"
                
                # Ensure uniqueness (shouldn't happen with keys, but just in case)
                base_name = archive_name
                counter = 1
                while archive_name in used_names:
                    stem = Path(base_name).stem
                    suffix = Path(base_name).suffix
                    archive_name = f"{stem}_{counter}{suffix}"
                    counter += 1
                
                used_names.add(archive_name)
                path_to_archive_name[original_path_str] = archive_name
                
                # Add file to archive
                zf.write(resource_file, archive_name)
            
            # Update outline data with new archive names
            updated_outline = outline_data.copy()
            if "resources" in updated_outline:
                for resource in updated_outline["resources"]:
                    if "path" in resource and resource["path"]:
                        original_path = str(Path(resource["path"]).resolve())
                        if original_path in path_to_archive_name:
                            # Update to archive name (without directory)
                            resource["path"] = path_to_archive_name[original_path]
                        else:
                            # Fallback: just use filename if not found in map
                            resource["path"] = Path(resource["path"]).name
            
            # Always include outline.json
            zf.writestr("outline.json", json.dumps(updated_outline, indent=2))

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
                    # Extract to files directory with original archive name
                    zf.extract(file_info, files_dir)

        # Read outline.json
        outline_path = extract_dir / "outline.json"
        if not outline_path.exists():
            raise ValueError("Package does not contain outline.json")

        with open(outline_path, "r") as f:
            outline_data = json.load(f)

        # Update resource paths to point to extracted files
        resource_files = []
        if "resources" in outline_data:
            for resource in outline_data["resources"]:
                if "path" in resource and resource["path"]:
                    # Update path to extracted location
                    extracted_path = files_dir / resource["path"]
                    if extracted_path.exists():
                        resource["path"] = str(extracted_path)
                        resource_files.append(extracted_path)

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

    @staticmethod
    def list_package_contents(package_path: Path) -> Dict[str, List[str]]:
        """List contents of a docpack without extracting.
        
        Args:
            package_path: Path to the .docpack file
            
        Returns:
            Dictionary with 'outline' and 'resources' lists
        """
        contents = {"outline": [], "resources": []}
        
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                for filename in zf.namelist():
                    if filename == "outline.json":
                        contents["outline"].append(filename)
                    else:
                        contents["resources"].append(filename)
            return contents
        except Exception:
            return contents