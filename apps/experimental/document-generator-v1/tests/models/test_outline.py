"""Tests for outline models."""

from document_generator_app.models.outline import Resource, Section, Outline, validate_outline


def test_outline_dataclass():
    o = Outline(title="T", general_instruction="GI")
    assert o.title == "T"
    assert o.general_instruction == "GI"
    assert isinstance(o.resources, list)
    assert isinstance(o.sections, list)


def test_resource_dataclass():
    r = Resource(key="k", path="/p", description="d", merge_mode="concat")
    assert r.key == "k"
    assert r.path == "/p"
    assert r.description == "d"
    assert r.merge_mode == "concat"


def test_section_dataclass():
    s = Section(title="S")
    assert s.title == "S"
    assert s.prompt is None
    assert s.resource_key is None
    assert s.refs == []
    assert s.sections == []


def test_section_serialization():
    """Test that sections serialize correctly for validation."""
    # Test prompt-based section
    s1 = Section(title="Prompt Section", prompt="Do something", refs=["ref1"])
    d1 = s1.to_dict()
    assert "prompt" in d1
    assert "refs" in d1
    assert "resource_key" not in d1

    # Test resource-based section
    s2 = Section(title="Resource Section", resource_key="key1")
    d2 = s2.to_dict()
    assert "resource_key" in d2
    assert "prompt" not in d2
    assert "refs" not in d2


def test_outline_validation():
    """Test that a valid outline passes validation."""
    outline = Outline(
        title="Test",
        general_instruction="Instructions",
        resources=[Resource("key1", "/path", "desc", "concat")],
        sections=[Section("Section 1", prompt="Generate")],
    )

    # Should not raise
    validate_outline(outline.to_dict())
