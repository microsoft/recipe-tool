# Document Generator V2

A Gradio application for generating documents with an enhanced interface.

## Features

- Document title and content editing
- Live preview of document
- Clean and intuitive interface

## Quick Start

### Development Mode

From the workspace root, run:

```bash
make install
document-generator-app --dev
```

The app will open at `http://localhost:8000`

### Deployment Mode

From the project root, run:

```bash
make build                 # Bundle recipes

# Then deploy the entire app directory
# The app will automatically use bundled recipes
```

See [Azure Deployment Guide](AZURE_DEPLOYMENT.md) for detailed deployment instructions.