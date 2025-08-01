"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from recipe_executor.config import load_configuration
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..config import settings
from ..models.outline import Outline
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
    APP_ROOT = Path(__file__).resolve().parents[2]  # document_generator_v2_app parent
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_v2_app" / "recipes" / "document_generator_recipe.json"

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
        REPO_ROOT = Path(__file__).resolve().parents[5]
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

        # Update resource paths in outline with resolved paths
        for resource in outline.resources:
            if resource.key in resolved_resources:
                old_path = resource.path
                resource.path = str(resolved_resources[resource.key])
                logger.info(f"Updated resource {resource.key}: {old_path} -> {resource.path}")

        # Create updated outline with resolved paths
        data = outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)
        logger.info(f"Created outline file: {outline_path}")

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
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_v2_app" / "recipes" / "generate_docpack.json"
    DOCPACK_FILE_PACKAGE_PATH = APP_ROOT / "antenv" / "bin" / "docpack_file"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
        logger.info(f"DOCPACK_FILE_PACKAGE_PATH: {DOCPACK_FILE_PACKAGE_PATH}")
    else:
        # Fall back to repo structure
        REPO_ROOT = Path(__file__).resolve().parents[5]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "generate_docpack.json"
        RECIPE_ROOT = RECIPE_PATH.parent.parent
        logger.info(f"Using repo recipes: {RECIPE_PATH}")

    if dev_mode:
        DOCPACK_FILE_PACKAGE_PATH = ""  # use default path in development mode, set in recipe
        logger.info(f"DOCPACK_FILE_PACKAGE_PATH: {DOCPACK_FILE_PACKAGE_PATH}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "docpack_generation")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Prepare resource paths as comma-separated string
        resource_paths = []
        for resource in resources:
            if "path" in resource and resource["path"]:
                resource_paths.append(resource["path"])
        resources_str = ",".join(resource_paths)
        logger.info(f"Resource paths: {resources_str}")

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
                "resources": resources_str,
                "docpack_name": docpack_name,
                "recipe_root": str(RECIPE_ROOT),
                "docpack_file_package_path": str(DOCPACK_FILE_PACKAGE_PATH),
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

        # Read the generated outline
        outline_json = ""
        if outline_path.exists():
            outline_json = outline_path.read_text()
            logger.info(f"Generated outline loaded from: {outline_path}")
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
