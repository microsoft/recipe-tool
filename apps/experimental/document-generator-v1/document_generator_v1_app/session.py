"""
Session management for multi-user hosting.

Provides session-scoped temporary directories to isolate user data.
"""

import uuid
import tempfile
from pathlib import Path
import shutil
import atexit
from typing import Optional


class SessionManager:
    """Dead simple session directory management"""

    def __init__(self):
        self.session_dirs = {}
        atexit.register(self.cleanup_all)

    def get_session_dir(self, session_id: Optional[str] = None) -> Path:
        """Get unique temp directory for session"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.session_dirs:
            session_dir = Path(tempfile.gettempdir()) / f"doc-gen-{session_id}"
            session_dir.mkdir(exist_ok=True)

            # Create subdirectories for organized file management
            (session_dir / "files").mkdir(exist_ok=True)  # Uploaded files (stored in docpack)
            (session_dir / "temp").mkdir(exist_ok=True)  # Generated files, downloaded URLs

            self.session_dirs[session_id] = session_dir

        return self.session_dirs[session_id]

    def get_files_dir(self, session_id: Optional[str] = None) -> Path:
        """Get files directory for session (for uploaded files)"""
        return self.get_session_dir(session_id) / "files"

    def get_temp_dir(self, session_id: Optional[str] = None) -> Path:
        """Get temp directory for session (for generated files and downloaded URLs)"""
        return self.get_session_dir(session_id) / "temp"

    def cleanup_all(self):
        """Clean up all session directories on shutdown"""
        for session_dir in self.session_dirs.values():
            shutil.rmtree(session_dir, ignore_errors=True)


# Global instance
session_manager = SessionManager()
