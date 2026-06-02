"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
import logging
import os
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from recipe_executor.config import load_configuration
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..config import settings
from ..models.outline import Outline, Resource
from ..resource_resolver import resolve_all_resources
from ..session import session_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_document(
    outline: Optional[Outline], session_id: Optional[str] = None, dev_mode: bool = False
) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    logger.info(f"Starting document generation for session: {session_id}")
    logger.info(f"Running in {'development' if dev_mode else 'production'} mode")

    # Allow stub invocation without an outline for initial tests
    if outline is None:
        logger.warning("No outline provided, returning empty document")
        return ""

    # First try bundled recipes (for deployment), then fall back to repo structure (for development)
    APP_ROOT = Path(__file__).resolve().parents[2]  # document_generator_app parent
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "document_generator_recipe.json"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        # Use bundled recipes (deployment mode)
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
    else:
        # Fall back to repo structure (development mode)
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using repo recipes: {RECIPE_PATH}")
        logger.info(f"Recipe exists: {RECIPE_PATH.exists()}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "execution")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Resolve all resources using the new resolver
        logger.info("Resolving resources...")
        outline_data = outline.to_dict()
        logger.info(f"Outline data: {json.dumps(outline_data, indent=2)}")

        resolved_resources = resolve_all_resources(outline_data, session_id)
        logger.info(f"Resolved resources: {resolved_resources}")

        # Update resource paths in outline with resolved paths, converting docx to text if needed
        for resource in outline.resources:
            if resource.key in resolved_resources:
                old_path = resource.path
                resolved_path = str(resolved_resources[resource.key])

                # Always update the path to the resolved path (keeps original file reference)
                resource.path = resolved_path

                # If it's a docx file, convert it to text and save as .txt file
                if resolved_path.lower().endswith(".docx"):
                    try:
                        from ..app import docx_to_text

                        text_content = docx_to_text(resolved_path)

                        # Create a text file version
                        txt_path = resolved_path.replace(".docx", ".txt")
                        with open(txt_path, "w", encoding="utf-8") as f:
                            f.write(text_content)

                        # Set txt_path for recipe executor to use
                        resource.txt_path = txt_path
                        logger.info(
                            f"Converted docx to text: {resource.key}: {old_path} -> {resolved_path}, txt_path: {txt_path}"
                        )
                    except Exception as e:
                        filename = os.path.basename(resolved_path)
                        logger.error(f"Error converting docx file {filename}: {e}")
                        # Re-raise with user-friendly message if it's a protection issue
                        if "protected or encrypted" in str(e):
                            raise e  # Error already includes filename from docx_to_text
                        # Keep txt_path as None on other errors
                else:
                    logger.info(f"Updated resource {resource.key}: {old_path} -> {resource.path}")

        # Create updated outline for recipe execution (use txt_path when available)
        execution_outline = Outline(
            title=outline.title,
            general_instruction=outline.general_instruction,
            resources=[
                Resource(
                    key=res.key,
                    path=res.txt_path if res.txt_path else res.path,  # Use txt_path for recipe execution
                    title=res.title,
                    description=res.description,
                    merge_mode=res.merge_mode,
                    txt_path=res.txt_path,
                )
                for res in outline.resources
            ],
            sections=outline.sections,
        )

        data = execution_outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)
        logger.info(f"Created outline file for recipe execution: {outline_path}")

        recipe_logger = init_logger(log_dir=tmpdir)

        # Load configuration from environment variables
        config = load_configuration()

        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
                "output_root": str(session_dir),  # Use session directory for output
                "model": settings.model_id,  # Use configured model
            },
            config=config,  # Pass configuration to context
        )
        logger.info(f"Context artifacts: {context.dict()}")

        executor = Executor(recipe_logger)
        logger.info(f"Executing recipe: {RECIPE_PATH}")
        await executor.execute(str(RECIPE_PATH), context)
        logger.info("Recipe execution completed")

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        logger.info(f"Output root: {output_root}")
        logger.info(f"Document filename: {filename}")
        logger.info(f"All context keys: {list(context.keys())}")

        if not filename:
            document_content = context.get("document", "")
            logger.info(f"No filename, returning document from context (length: {len(document_content)})")
            return document_content

        document_path = output_root / f"{filename}.md"
        logger.info(f"Looking for document at: {document_path}")

        try:
            content = document_path.read_text()
            logger.info(f"Successfully read document (length: {len(content)})")
            return content
        except FileNotFoundError:
            logger.error(f"Generated file not found: {document_path}")
            # List files in output directory for debugging
            if output_root.exists():
                files = list(output_root.glob("*"))
                logger.info(f"Files in output directory: {files}")
            return f"Generated file not found: {document_path}"
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error generating document: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"


async def generate_docpack_from_prompt(
    prompt: str, resources: List[Dict[str, str]], session_id: Optional[str] = None, dev_mode: bool = False
) -> Tuple[str, str]:
    """
    Generate a docpack outline from user prompt and uploaded resources.

    Args:
        prompt: User's description of the document they want to create
        resources: List of uploaded resource files with 'path' and 'name' keys
        session_id: Optional session ID for file management
        dev_mode: Whether running in development mode

    Returns:
        Tuple of (docpack_path, outline_json) where:
        - docpack_path: Path to the generated .docpack file
        - outline_json: JSON string of the generated outline
    """
    logger.info(f"Starting docpack generation for session: {session_id}")
    logger.info(f"Running in {'development' if dev_mode else 'production'} mode")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Resources: {len(resources)} files")

    # Setup paths
    APP_ROOT = Path(__file__).resolve().parents[2]
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "generate_docpack.json"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
    else:
        # Fall back to repo structure
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "generate_docpack.json"
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using repo recipes: {RECIPE_PATH}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "docpack_generation")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Extract resource paths and convert docx to text if needed
        # Keep track of original paths and their converted versions
        resource_paths = []
        docx_conversion_map = {}  # Maps txt_path -> original_docx_path

        for resource in resources:
            if "path" in resource and resource["path"]:
                resource_path = resource["path"]

                # If it's a docx file, convert it to text and save as .txt file
                if resource_path.lower().endswith(".docx"):
                    try:
                        from ..app import docx_to_text

                        text_content = docx_to_text(resource_path)

                        # Create a text file version
                        txt_path = resource_path.replace(".docx", ".txt")
                        with open(txt_path, "w", encoding="utf-8") as f:
                            f.write(text_content)

                        resource_paths.append(txt_path)
                        docx_conversion_map[txt_path] = resource_path  # Remember the original path
                        logger.info(f"Converted docx to text: {resource_path} -> {txt_path}")
                    except Exception as e:
                        logger.error(f"Error converting docx file {resource_path}: {e}")
                        # Re-raise with user-friendly message if it's a protection issue
                        if "protected or encrypted" in str(e):
                            raise e
                        resource_paths.append(resource_path)  # Fall back to original path for other errors
                else:
                    resource_paths.append(resource_path)

        logger.info(f"Resource paths: {resource_paths}")

        # Initialize recipe logger
        recipe_logger = init_logger(log_dir=tmpdir)

        # Load configuration
        config = load_configuration()

        # Create timestamp-based docpack name
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        docpack_name = f"{timestamp}.docpack"

        # Create context for the recipe
        context = Context(
            artifacts={
                "model": settings.model_id,
                "output_root": str(session_dir),
                "document_description": prompt,
                "resources": resource_paths,
                "docpack_name": docpack_name,
                "recipe_root": str(RECIPE_ROOT),
            },
            config=config,
        )
        logger.info(f"Context artifacts: {context.dict()}")

        # Execute the generate_docpack recipe
        executor = Executor(recipe_logger)
        logger.info(f"Executing recipe: {RECIPE_PATH}")
        await executor.execute(str(RECIPE_PATH), context)
        logger.info("Recipe execution completed")

        # Get the generated files
        output_root = Path(context.get("output_root", tmpdir))
        docpack_path = output_root / docpack_name
        outline_path = output_root / "outline.json"

        # Read the generated outline and fix docx paths
        outline_json = ""
        if outline_path.exists():
            outline_json = outline_path.read_text()
            logger.info(f"Generated outline loaded from: {outline_path}")

            # If we have docx conversions, fix the paths in the outline
            if docx_conversion_map:
                try:
                    import json

                    outline_data = json.loads(outline_json)

                    # Fix resource paths to point back to original docx files
                    for resource in outline_data.get("resources", []):
                        resource_path = resource.get("path", "")
                        if resource_path in docx_conversion_map:
                            original_path = docx_conversion_map[resource_path]
                            logger.info(f"Restoring original path: {resource_path} -> {original_path}")
                            resource["path"] = original_path  # Restore original docx path
                            resource["txt_path"] = resource_path  # Keep txt path for future use

                    # Save the fixed outline
                    outline_json = json.dumps(outline_data, indent=2)
                    logger.info("Fixed outline paths to preserve original docx references")

                except Exception as e:
                    logger.error(f"Error fixing outline paths: {e}")
                    # Continue with original outline_json if fixing fails

        else:
            logger.error(f"Outline file not found at: {outline_path}")

        # Check if docpack was created
        if not docpack_path.exists():
            logger.error(f"Docpack file not found at: {docpack_path}")
            # List files for debugging
            if output_root.exists():
                files = list(output_root.glob("*"))
                logger.info(f"Files in output directory: {files}")
            return "", outline_json

        logger.info(f"Successfully generated docpack at: {docpack_path}")
        return str(docpack_path), outline_json

    except Exception as e:
        logger.error(f"Error generating docpack: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
