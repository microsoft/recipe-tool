#!/usr/bin/env python3
"""Helper script to create docpack from outline - to be used with recipe-executor."""

import json
import sys
from pathlib import Path

# Add parent directories to path to import docpack
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from docpack import DocpackHandler


def main():
    # Get parameters from environment or command line
    import os
    output_dir = os.environ.get('OUTPUT_DIR', 'output')
    docpack_name = os.environ.get('DOCPACK_NAME', 'document.docpack')
    
    outline_path = Path(output_dir) / 'outline.json'
    output_path = Path(output_dir) / docpack_name
    
    # Load outline
    with open(outline_path, 'r') as f:
        outline_data = json.load(f)
    
    # Collect resource files
    resource_files = []
    for resource in outline_data.get('resources', []):
        resource_path = Path(resource.get('path', ''))
        if resource_path.exists():
            resource_files.append(resource_path)
    
    # Create docpack
    DocpackHandler.create_package(
        outline_data=outline_data,
        resource_files=resource_files,
        output_path=output_path
    )
    
    print(f'Created docpack: {output_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())