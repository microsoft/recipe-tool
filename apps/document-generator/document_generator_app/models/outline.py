"""
Data models for the Document Generator app.
Defines Resource, Section, and Outline dataclasses with serialization utilities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from jsonschema import validate


@dataclass
class Resource:
    key: str
    path: str
    description: str
    merge_mode: str


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)
    _mode: Optional[str] = field(default=None, init=False, repr=False)  # Internal mode tracking

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None values and empty refs to match schema."""
        result = {"title": self.title}

        # Use mode to determine which fields to include
        if self._mode == "Static" and self.resource_key is not None:
            result["resource_key"] = self.resource_key
        else:
            # Default to prompt mode
            if self.prompt is not None:
                result["prompt"] = self.prompt
            if self.refs:  # Only include refs if not empty
                result["refs"] = self.refs

        # Always include sections array (even if empty)
        result["sections"] = [s.to_dict() for s in self.sections]

        return result


def section_from_dict(data: Dict[str, Any]) -> Section:
    section = Section(
        title=data.get("title", ""),
        prompt=data.get("prompt"),
        refs=list(data.get("refs", [])),
        resource_key=data.get("resource_key"),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )
    # Set mode based on loaded data
    if section.resource_key is not None:
        section._mode = "Static"
    else:
        section._mode = "Prompt"
    return section


@dataclass
class Outline:
    title: str
    general_instruction: str
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert outline to dict with proper section serialization."""
        return {
            "title": self.title,
            "general_instruction": self.general_instruction,
            "resources": [asdict(r) for r in self.resources],
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        res_list: List[Resource] = []
        for r in data.get("resources", []):
            res_list.append(
                Resource(
                    key=r.get("key", ""),
                    path=r.get("path", ""),
                    description=r.get("description", ""),
                    merge_mode=r.get("merge_mode", "concat"),
                )
            )
        sec_list: List[Section] = [section_from_dict(s) for s in data.get("sections", [])]
        return cls(
            title=data.get("title", ""),
            general_instruction=data.get("general_instruction", ""),
            resources=res_list,
            sections=sec_list,
        )


# JSON Schema for outline validation
OUTLINE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Outline",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "general_instruction": {"type": "string"},
        "resources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "path": {"type": "string"},
                    "description": {"type": "string"},
                    "merge_mode": {"type": "string", "enum": ["concat", "dict"]},
                },
                "required": ["key", "path", "description"],
                "additionalProperties": False,
            },
        },
        "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
    },
    "definitions": {
        "section": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "prompt": {"type": "string"},
                "refs": {"type": "array", "items": {"type": "string"}},
                "resource_key": {"type": "string"},
                "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
            },
            "required": ["title"],
            "oneOf": [{"required": ["prompt"]}, {"required": ["resource_key"]}],
            "additionalProperties": False,
        }
    },
    "required": ["title", "general_instruction", "resources", "sections"],
    "additionalProperties": False,
}


def validate_outline(data: dict) -> None:
    """
    Validate outline data against the JSON schema.
    Raises jsonschema.ValidationError on failure.
    """
    validate(instance=data, schema=OUTLINE_SCHEMA)
