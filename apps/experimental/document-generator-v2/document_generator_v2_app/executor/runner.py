"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..models.outline import Outline


async def generate_document(outline: Optional[Outline]) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    # Allow stub invocation without an outline for initial tests
    if outline is None:
        return ""
    import urllib.request
    from urllib.parse import urlparse

    REPO_ROOT = Path(__file__).resolve().parents[5]
    RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
    RECIPE_ROOT = RECIPE_PATH.parent

    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve resource paths: download URLs or locate local files
        for res in outline.resources:
            if res.path:
                parsed = urlparse(res.path)
                if parsed.scheme in ("http", "https"):
                    dest = Path(tmpdir) / Path(parsed.path).name
                    urllib.request.urlretrieve(res.path, dest)
                    res.path = str(dest)
                else:
                    p = Path(res.path)
                    if not p.exists():
                        p2 = RECIPE_ROOT / res.path
                        if p2.exists():
                            res.path = str(p2)
                    else:
                        res.path = str(p)

        data = outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)

        logger = init_logger(log_dir=tmpdir)
        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
                "output_root": str(tmpdir),
            }
        )
        executor = Executor(logger)
        await executor.execute(str(RECIPE_PATH), context)

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        if not filename:
            return context.get("document", "")

        document_path = output_root / f"{filename}.md"
        try:
            return document_path.read_text()
        except FileNotFoundError:
            return f"Generated file not found: {document_path}"
