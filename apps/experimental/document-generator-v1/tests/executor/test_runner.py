import pytest

from document_generator_app.executor.runner import generate_document


@pytest.mark.asyncio
async def test_generate_document_not_implemented():
    # For now, stub returns empty string or raises
    result = await generate_document(None)
    assert isinstance(result, str)
