# AI Context System Implementation Guide

[document-generator]

**Date:** 6/13/2025 10:51:20 AM

# Quick Start - Copy This System

To swiftly integrate the AI context system into your project, follow this streamlined checklist. This guide allows you to set up the system using only Python's standard library, ensuring no external dependencies are required.

1. **Copy Core Files**
   
   - Copy the following essential Python scripts from the source repository:
     
     ```bash
     cp source_repo/tools/collect_files.py your_repo/tools/
     cp source_repo/tools/build_ai_context_files.py your_repo/tools/
     ```

2. **Set Up the Output Directory**
   
   - Create the necessary directory structure to store the generated files:
     
     ```bash
     mkdir -p your_repo/ai_context/generated
     ```

3. **Adjust Tasks Configuration**
   
   - Open `build_ai_context_files.py` in your new repo and modify the tasks list to suit your project's structure. Customize the patterns, exclusions, and inclusions in the `tasks` variable:
     
     ```python
     # Example editing tasks in build_ai_context_files.py
     tasks = [
         {
             "patterns": ["your_project_dir"],
             "output": "ai_context/generated/YOUR_OUTPUT_FILE.md",
             "exclude": collect_files.DEFAULT_EXCLUDE,
             "include": ["README.md"],
         },
     ]
     ```

4. **Run the Script**
   
   **Directly using Python:**

   - Navigate to your repository's root and execute:
     
     ```bash
     python tools/build_ai_context_files.py
     ```
   
   **Optional: Integrate with Make**

   - If preferred, define a Makefile to integrate more seamlessly into existing workflows:
     
     ```makefile
     make ai-context:
     	python tools/build_ai_context_files.py
     ```

Following these steps will establish the AI context functionality quickly within your existing project, providing immediate utility without the need for external resources or libraries.

# Core Files You Need

To effectively generate AI context within your project, ensure you have the following essential Python scripts. These files leverage Python’s standard library exclusively, eliminating the need for additional dependencies.

1. **Essential Files to Copy**
   
   - **`collect_files.py`**: This script is a utility for aggregating files based on specified patterns and outputs them into a markdown format. It's crucial for collecting and displaying file contents from various parts of your project.
     
     ```bash
     cp source_repo/tools/collect_files.py your_repo/tools/
     ```

   - **`build_ai_context_files.py`**: This script utilizes `collect_files.py` to compile project-specific files into comprehensive markdown documents, tailored for AI processing. It allows the customization of file collections through pattern-based task configurations.
     
     ```bash
     cp source_repo/tools/build_ai_context_files.py your_repo/tools/
     ```

2. **Optional File for External Documentation**

   - **`build_git_collector_files.py`**: Use this file if your project involves external documentation integration. It facilitates the collection of such documentation using external tools like `git-collector`.
     
     ```bash
     cp source_repo/tools/build_git_collector_files.py your_repo/tools/
     ```
     
     Note: This is not essential unless external document handling is needed.

3. **Minimal Directory Structure After Copying**

   After migrating these core files, your directory should look like this:

   ```
   your_repo/
   ├── tools/
   │   ├── collect_files.py
   │   ├── build_ai_context_files.py
   │   └── (optional) build_git_collector_files.py
   └── ai_context/
       └── generated/
   ```

By integrating these files and creating the basic directory structure, you are set to begin generating AI context files tailored to your project's needs, utilizing solely Python's built-in capabilities.

# Running the System

To generate and manage AI context files using this system, you have two primary options: direct execution with Python and optional Make integration for convenience.

## Direct Python Execution

The primary method to utilize the AI context system is directly through Python. This is the quickest, no-dependency-required method, and uses only the Python standard library. Follow these steps:

1. **Navigate to the Project Root**

   Ensure you start from the root of your project directory where your `tools` and `ai_context` directories are located.

   ```bash
   cd /path/to/your_repo
   ```

2. **Execute the Primary Script**

   Run the following command to build your AI context files:

   ```bash
   python tools/build_ai_context_files.py
   ```

   This command invokes the build process, collecting files as per your configured tasks and generating markdown outputs in the `ai_context/generated` directory.

## Optional Make Integration

For users who prefer integrating into a Make-based workflow, an optional Make target can streamline repeated executions and integrate with broader project automation.

### Configuring Make

1. **Add Makefile Target**

   Edit your project's Makefile to include a target for building AI context files. Ensure your Makefile is located appropriately to manage directory-wide builds:

   ```makefile
   ai-context-files: ## Build AI context files for development
   	@echo "Building AI context files..."
   	python tools/build_ai_context_files.py
   	@echo "AI context files generated"
   ```

2. **Run via Make**

   Once configured, simply use the command below in your project root to run the context build process with Make:

   ```bash
   make ai-context-files
   ```

### Note on Make Usage

Utilizing Make is entirely optional and serves as an additional utility for those familiar with or already using Makefile setups in their development process. The Python script will always be sufficient on its own, and is recommended for those seeking the minimal setup.

By following these steps, you can quickly generate AI context files, leveraging either command method based on your project’s needs and your development workflow preferences.

# Customize for Your Project

To adapt the `build_ai_context_files.py` script for your specific project structure, you will need to modify the tasks configuration according to your project's directory layout and file organization. Below are examples for various common project structures, illustrating how to customize the tasks configuration for each.

## Example 1: Standard Src/Lib Project Structure

```bash
project_root/
├── src/
│   ├── module1/
│   └── module2/
└── lib/
    └── utils/
```

For a project where source code is contained within `src/` and libraries or utility scripts are under `lib/`, your tasks configuration might look like:

```python
tasks = [
    {
        "patterns": ["src/**/*.py"],
        "output": "ai_context/generated/SRC_CODE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE + ["lib/**/*"],
        "include": ["README.md", "setup.py"],
    },
    {
        "patterns": ["lib/**/*.py"],
        "output": "ai_context/generated/LIB_CODE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
]
```

## Example 2: Apps and Components Structure

```bash
project_root/
├── apps/
│   ├── app1/
│   └── app2/
└── components/
    ├── component1/
    └── component2/
```

For a project divided into applications under `apps/` and shared components under `components/`, configure your tasks as follows:

```python
tasks = [
    {
        "patterns": ["apps/**/app*.py"],
        "output": "ai_context/generated/APPS_CODE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": ["apps/**/README.md"],
    },
    {
        "patterns": ["components/**/*.py"],
        "output": "ai_context/generated/COMPONENTS_CODE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": ["components/**/docs/*"],
    },
]
```

## Example 3: Mixed Code and Documentation

```bash
project_root/
├── source/
└── docs/
```

For projects with a clear separation of code and documentation, such as source files in `source/` and markdown documentation in `docs/`, you should adapt as:

```python
tasks = [
    {
        "patterns": ["source/**/*.py"],
        "output": "ai_context/generated/SOURCE_CODE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
    {
        "patterns": ["docs/**/*.md"],
        "output": "ai_context/generated/DOCUMENTATION.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
]
```

### Essential Patterns
Regardless of your project structure, the main patterns involve defining which file patterns to include for collection (`patterns`), where to output the collected data (`output`), and any specific files or directories to explicitly include or exclude (`include`, `exclude`). Tailor these configurations to reflect your project's organization, focusing on directories and extensions crucial for your context generation needs.

By adjusting these task configurations, you ensure the AI context system accurately reflects and compiles the code and resources most relevant to your project setting.

# Configuration Options

To successfully implement the AI context system, it's vital to understand and configure key options related to file selection and output management. Below is a concise guide on essential configuration aspects.

## Key Configuration Options

### Patterns
- **Patterns**: Used to specify which files or directories to include in the collection process. Patterns can incorporate wildcards and specific path segments that direct the script to gather the appropriate files for context generation. 
  
  ```python
  patterns = ["src/**/*.py"]
  ```

  This example pattern collects all Python files recursively within the `src` directory.

### Exclude/Include Lists
- **Exclude Lists**: Directs the tool to omit certain files or directories during collection. This is managed by merging user-defined exclusions with the `DEFAULT_EXCLUDE` list embedded in the script. 

  ```python
  exclude_patterns = collect_files.DEFAULT_EXCLUDE + ["build", "dist"]
  ```

  Utilize `DEFAULT_EXCLUDE` to efficiently bypass unnecessary directories like `__pycache__` and `node_modules`.

- **Include Lists**: Overrides exclusions for specific files, bringing them back into consideration when matched by the pattern. This ensures important files aren't missed.

  ```python
  include_patterns = ["README.md", "requirements.txt"]
  ```

### Output Paths
- **Output Paths**: Designate where the collected results should be saved. Define this path in the task configuration to manage a structured output of the AI context data.

  ```python
  output = "ai_context/generated/PROJECT_FILES.md"
  ```

## Performance Tips

### Efficient File Handling
- **Splitting Large Codebases**: Divide large projects into smaller, more manageable patterns to enhance performance. This improves manageability and speeds up the process of file collection and context generation.

- **Utilizing DEFAULT_EXCLUDE Effectively**: Make full use of the embedded `DEFAULT_EXCLUDE` list to dismiss non-essential files, thereby focusing resources and speeding up operations.

By correctly setting these configuration options, you ensure the AI context system runs smoothly, collecting relevant data while discarding non-crucial files, all while utilizing the Python standard library for seamless integration.

# Templates and Examples

To streamline the implementation of the AI context system, here are some practical configuration templates and examples that you can readily apply or modify according to your project’s needs.

## Ready-to-Use Task Configuration Templates

### Basic Template

Use this basic configuration template to start collecting files in your project:

```python
# Basic template for task configuration
from tools.collect_files import DEFAULT_EXCLUDE

tasks = [
    {
        "patterns": ["src/**/*.py"],  # Adjust this pattern to match your source files structure
        "output": "ai_context/generated/SOURCE_CODE.md",
        "exclude": DEFAULT_EXCLUDE,  # You can add more items to exclude if needed
        "include": ["README.md", "LICENSE"],  # Include files that must be part of the context
    },
]
```

### Extended Template with Detailed Customization

For projects with specific requirements, use the following detailed customization template:

```python
# Extended template for task configuration with detailed exclusions and inclusions
from tools.collect_files import DEFAULT_EXCLUDE

tasks = [
    {
        "patterns": ["project/**/*.py", "libs/**/*.py"],
        "output": "ai_context/generated/PROJECT_FILES.md",
        "exclude": DEFAULT_EXCLUDE + ["env", "build", "dist"],  # Add custom excludes
        "include": [
            "**/*.md",  # Include all markdown files
            "setup.py",  # Explicitly include setup files
        ],
    },
    # Add more task entries as needed
]
```

## Basic Troubleshooting Tips

While setting up the AI context tool, you may encounter some common issues. Here are quick troubleshooting tips:

- **No Files Found**: Ensure the `patterns` in your configuration accurately match the file paths in your project. Check for typos or misconfigurations in path patterns.

- **Permission Errors**: If permission errors occur, verify that your script has adequate file permissions. This might involve changing permissions of directories or running the script with elevated privileges (e.g., using `sudo` on Unix-based systems).

### Example Problem and Quick Fix

**Problem:**
   - Your script returns "No files matched the patterns".

**Quick Fix:**
   - Check the pattern syntax. Ensure your path patterns include proper wildcard usage (`*` for matching any set of characters). An example would be: `"src/**/*.py"` for matching all Python files in `src` and its subdirectories.

By employing these templates and tips, developers can quickly overcome common hurdles and configure the AI context system efficiently for their needs.