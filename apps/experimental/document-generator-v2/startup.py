#!/usr/bin/env python3
"""
Startup script for deployment environments.
"""

import sys
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from document_generator_v2_app.app import main

    main()
