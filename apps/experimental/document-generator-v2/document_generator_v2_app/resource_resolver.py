"""Resource resolution for document generation.

Handles resolving resources at generation time:
- Uploaded files: resolved to session files directory
- URLs: downloaded to session temp directory
"""

import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .models.outline import Resource
from .session import session_manager


def resolve_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve a resource to a local file path for generation.

    Args:
        resource: Resource object with path (file or URL)
        session_id: Session ID for directory resolution

    Returns:
        Path to local file for use in generation

    Raises:
        FileNotFoundError: If uploaded file doesn't exist
        urllib.error.URLError: If URL download fails
    """
    if resource.path.startswith(("http://", "https://")):
        # URL: download to temp directory
        return _download_url_resource(resource, session_id)
    else:
        # Uploaded file: resolve to files directory
        return _resolve_file_resource(resource, session_id)


def _resolve_file_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve uploaded file resource to local path."""
    files_dir = session_manager.get_files_dir(session_id)
    file_path = files_dir / resource.path

    if not file_path.exists():
        raise FileNotFoundError(f"Resource file not found: {resource.path}")

    return file_path


def _download_url_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Download URL resource to temp directory."""
    temp_dir = session_manager.get_temp_dir(session_id)

    # Generate filename from URL
    parsed_url = urlparse(resource.path)
    filename = Path(parsed_url.path).name

    # If no filename in URL, use resource key
    if not filename or filename == "/":
        filename = f"{resource.key}.downloaded"

    target_path = temp_dir / filename

    # Download the file
    try:
        urllib.request.urlretrieve(resource.path, target_path)
        return target_path
    except Exception as e:
        raise urllib.error.URLError(f"Failed to download {resource.path}: {str(e)}")


def resolve_all_resources(outline_data: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Path]:
    """Resolve all resources in an outline to local paths.

    Args:
        outline_data: Outline dictionary with resources
        session_id: Session ID for directory resolution

    Returns:
        Dictionary mapping resource keys to resolved file paths
    """
    from .models.outline import Outline

    outline = Outline.from_dict(outline_data)
    resolved_resources = {}

    for resource in outline.resources:
        if resource.key:
            resolved_resources[resource.key] = resolve_resource(resource, session_id)

    return resolved_resources
