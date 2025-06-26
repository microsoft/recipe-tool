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
            self.session_dirs[session_id] = session_dir

        return self.session_dirs[session_id]

    def cleanup_all(self):
        """Clean up all session directories on shutdown"""
        for session_dir in self.session_dirs.values():
            shutil.rmtree(session_dir, ignore_errors=True)


# Global instance
session_manager = SessionManager()
