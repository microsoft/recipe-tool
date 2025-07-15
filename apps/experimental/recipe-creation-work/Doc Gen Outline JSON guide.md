# Doc Gen Outline JSON guide

[document-generator]

**Date:** 7/15/2025 02:21:01 PM

## Overview

In the Document Generator app, the outline JSON serves as a crucial framework for building documents. It acts as a blueprint that guides the structure and content generation process within the app. Users utilize this JSON to define the hierarchy and sections of their documents, incorporating various resources and prompts. Once set up, the outline JSON enables the AI-driven document generation to process and create comprehensive, structured documents efficiently. This functionality underscores the role of the outline JSON as a foundational component in the Document Generator, facilitating seamless content creation and customization according to user specifications.

## The Outline JSON

The Outline JSON in the Document Generator app acts as a blueprint for defining the structure of a document. This JSON structure includes several key components:

```json
{
  "title": "", 
  "general_instruction": "",
  "resources": [
    {
      "key": "",
      "path": "",
      "description": ""
    },
    ...
  ],
  "sections": [
    {
      "title": "",
      "prompt": "",
      "refs": [""],
      "sections": []
    },
    ...
  ]
}
```

### Elements of Outline JSON:

- **title**: This is the primary title of the document or project that describes the primary purpose or subject of the JSON structure.

- **general_instruction**: Offers general or overarching instructions for the document generation process, providing context and guidelines on how the content should be crafted.

- **resources**: An array of resources that provides supplementary materials required for document creation. Each resource object has:
  - **key**: A unique identifier for each resource, used to reference the resource within the document.
  - **path**: The file path or URL where the resource is located.
  - **description**: A short description that helps identify the content and purpose of the resource.

- **sections**: Contains an array of sections, which can include nested subsections. Each section object contains:
  - **title**: The title of the section or subsection within the document.
  - **prompt**: Specific instructions or queries intended to guide content generation for that particular section.
  - **refs**: A list of resource keys referenced by this section, which inform content development.
  - **sections**: Optionally, nested subsections, allowing for multi-level document hierarchies.

By understanding these elements, users can effectively construct and manipulate the JSON to produce robust and detailed documents, tailored to their project requirements. The flexibility and nested capacity of sections allow for intricate document architectures, leveraging AI capabilities to adapt and generate content efficiently and effectively. This structure forms the backbone of the Document Generator app's functionality, ensuring logical and coherent document creation.

### Outline Examples

This section provides three examples of outline JSONs used within the Document Generator app, showcasing their correct functionality. These practical examples include the actual JSON structures for real-world understanding and application:

#### Example 1: Annual Employee Performance Review

```json
{
  "title": "Annual Employee Performance Review",
  "general_instruction": "This is an annual performance review, to be written for an audience of both the employee and manager...",
  "resources": [
    {"key": "resource_1", "path": "/path/to/career-path-plans.txt", "description": "potential career paths..."},
    {"key": "resource_2", "path": "/path/to/employee-profile.txt", "description": "Basic work information and experience..."},
    ...
  ],
  "sections": [
    {"title": "Overview", "prompt": "Provide a short summary of the employee's role...", "refs": ["resource_2"], "sections": []},
    ...
  ]
}
```

This example illustrates a complex document with multiple sections and subsections, each leveraging specific resources for detailed reviews and goal-setting.

#### Example 2: README

```json
{
  "title": "README",
  "general_instruction": "Generate a production-ready README.md...",
  "resources": [
    {"key": "codebase_docs", "path": "path/to/RECIPE_EXECUTOR_BLUEPRINT_FILES.md", "description": "In-repo design docs, examples, etc."},
    ...
  ],
  "sections": [
    {"title": "Header", "prompt": "Produce an H1 title using the repository name...
    ...
  ]
}
```

This README example demonstrates a concise document relying heavily on updated references, designed for developers encountering a project for the first time.

#### Example 3: Customer Analytics Dashboard - Launch Documentation

```json
{
  "title": "Customer Analytics Dashboard - Launch Documentation",
  "general_instruction": "Create comprehensive launch documentation for our new B2B SaaS analytics product...",
  "resources": [
    {"key": "product_specs", "path": "recipes/document_generator/examples/resources/product_specs.md", "description": "Technical specifications, features, API details..."},
    ...
  ],
  "sections": [
    {"title": "Executive Summary", "prompt": "Create a compelling executive summary that highlights the key benefits..."},
    ...
  ]
}
```

This example focuses on producing structured documentation at the same level throughout, suitable for both technical stakeholders and business decision-makers.

These JSON outlines not only serve as templates for different document types but also provide a comprehensive view of how diverse content requirements are managed within the Document Generator app. Each example reflects the adaptability and structured approach necessary for generating organized and meaningful documents.

## The Document Generator App

The Document Generator app provides a seamless way for users to create structured documents through a user-friendly Gradio interface. At its core, the app utilizes the Outline JSON to define the document's structure, allowing users to employ nested sections and incorporate various resources.

### Creating and Interacting with Outline JSON

Users begin by creating an outline through the app's Visual Outline Editor, which supports up to four levels of nested sections. Users can upload text files or input URLs under the Resource Management section to serve as source material. These resources can include files like Markdown, JSON, source code, CSV, or any text-based format, though binary files like Word Docs and PDFs are unsupported. Each resource is assigned a unique key, which users reference within their prompts for context.

The Live JSON Preview feature displays the outline in real-time, allowing users to validate its structure before generating a document. Furthermore, users can import existing outlines by uploading a `.docpack` file or save current outlines for future use, utilizing the app's import/export capabilities.

### Using Outline JSON as Input to the Document Generator Recipe

The Document Generator utilizes a recipe system, where the outline JSON is a critical input. The recipe, as defined in `document_generator_recipe.json`, requires the path to the outline JSON alongside other parameters like the model for LLM generation and the output directory. The recipe then processes each section in the JSON, instructing the AI to generate content based on provided prompts and associated resources, ultimately compiling a complete and coherent document.

### Outline JSON within the Docpack

The Docpack serves as a comprehensive package containing the outline JSON and all associated resource files the user includes. The Docpack Handler ensures that this bundle, essentially a zip archive, manages all filename conflicts by using the resource keys as prefixes. This approach facilitates easy sharing and transportation of document projects, allowing users to seamlessly import complete docpacks into the app.

Through these methods, the Document Generator app leverages the Outline JSON to provide a robust framework for document generation, enabling users to define, preview, and generate tailored documents with ease.