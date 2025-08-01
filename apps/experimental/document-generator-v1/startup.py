#!/usr/bin/env python3
"""
Startup script for deployment environments.
"""

import sys
import traceback
from pathlib import Path


def main():
    """Start the document generator application."""
    try:
        # Add current directory to Python path for imports
        app_dir = Path(__file__).parent
        sys.path.insert(0, str(app_dir))

        from document_generator_v1_app.main import main as app_main

        app_main()

    except Exception as e:
        print(f"Startup failed: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
