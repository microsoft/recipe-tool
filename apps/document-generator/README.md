# Document Generator

A powerful AI document generation tool that creates structured documents from outlines and resource files using Large Language Models.

<img width="1838" height="898" alt="image" src="https://github.com/user-attachments/assets/56db6bf3-ac91-49b3-b7d3-92c32a5af2df" />


## Overview

Document Generator is a web-based application that helps users create comprehensive documents by:
- Converting natural language prompts into structured document templates
- Integrating multiple resource files (CSV, TXT, JSON, etc.) as context
- Using AI to generate content from template sections
- Exporting/importing document templates as "docpacks"
- Downloading generated document

<img width="1877" height="670" alt="image" src="https://github.com/user-attachments/assets/89b946b1-b810-40c8-95e2-4258800dd453" />

<img width="1882" height="691" alt="image" src="https://github.com/user-attachments/assets/58d4232d-59ab-45c8-9404-de4a7a05a36c" />


## Quick Start

1. Local Development Setup (Linux)
   ```bash
   # Clone repository
   git clone https://github.com/microsoft/recipe-tool.git
   cd recipe-tool

   # Install
   make install
   source .venv/bin/activate

   # Update environment variables
   cp .env.example .env
   # Change RECIPE_EXECUTOR_OPENAI_API_KEY to OPENAI_API_KEY. (as of 2025-08-04)
   # Fill in OPENAI_API_KEY.
   
   # Run
   document-generator-app
   ```
   > NOTE: If the deployment step `make build` has been run, instead run the app with the `--dev` option.
   ```
   document-generator-app --dev
   ```

2. Open locally running webapp in your browser. (localhost:8000)
3. Start with one of three approaches:
   - **Start with a Prompt**: Type what document you want to create or try an example prompt
   - **Build Manually**: Create your template section by section
   - **Load Template**: Use a pre-built example template

## How to Use

### Creating Documents

1. **Start with a Prompt**
   - Enter a description of your document (e.g., "Create a comprehensive README for my Python project")
   - Upload relevant UTF-8 files (CSVs, text files, JSON, etc.)
   - Click "Draft"
   - The AI will create a template for your structured document.
  
   <img width="875" height="598" alt="image" src="https://github.com/user-attachments/assets/0dfbbb4a-38c5-497a-9afb-32e07ab1dc03" />




2. **Update Resources**
   - Update, add, or remove UTF-8 files (CSVs, text files, JSON, etc.)
   <img width="203" height="104" alt="image" src="https://github.com/user-attachments/assets/a55ca837-1ddd-45e0-a048-7f5e15b94e9a" />


3. **Edit Your Outline**
   - Add sections and subsections
      - "+ Add section" adds a new section to the very bottom.
      - "+" button inserts a new section below.
      - "->" button tabs in the section to become a subsection
   - For each section, choose:
     - **AI**: Write a prompt with context for AI-generated content
     - **Text**: Written text or reference file is include directly
    
   <img width="789" height="581" alt="image" src="https://github.com/user-attachments/assets/7d6e6287-a387-4714-ba31-b7aa3cb26780" />


4. **Generate Document**
   - Click "▷ Generate"
   - The AI processes each section using your prompts and resources
   - Download the generated Markdown document
  
   <img width="803" height="190" alt="image" src="https://github.com/user-attachments/assets/62a7fd33-6c45-4759-ac96-b382adfe7d05" />


### Working with Templates (Docpacks)

- **Save**: Export your outline and resources as a .docpack file
- **Import**: Import a docpack to reuse document structures
- **New**: Start with a fresh template
- **Template Examples**: Pre-built templates for common documents:
  - Technical documentation
  - Project reports or proposals
  - Performance reviews
<img width="603" height="301" alt="image" src="https://github.com/user-attachments/assets/1bfa2066-0c04-4044-b024-d5ba959df7be" />


## Architecture

### Components

```
document-generator/
├── document_generator_app/
│   ├── app.py              # Gradio UI and main application
│   ├── config.py           # Configuration and settings
│   ├── executor/
│   │   └── runner.py       # Document and template generation engine
│   ├── models/
│   │   └── outline.py      # Template model
│   ├── recipes/            # AI workflow definitions, executed by generation engine
│   └── static/             # UI assets (CSS, JS, images)
├── examples/               # Sample documents and templates
└── scripts/                # Deployment utilities
```

### Technology Stack

- **Frontend**: Gradio 5.30+ with custom theming
- **Backend**: Python 3.11+, FastAPI (via Gradio)
- **AI Integration**: OpenAI/Azure OpenAI API
- **Processing**: Recipe-executor framework
- **Package Management**: uv/pip

## Deployment

### Azure App Service

1. **Build deployment package**:
   ```bash
   # From root
   cd apps/document-generator
   make build
   ```

2. **Configure App Service**:
   See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed instructions.

3. **Deploy to Azure**:
   ```bash
   ./deploy.sh --name <app_name> --resource-group <resource_group> [--slot <slot_name>]
   ```


## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

```
