from typing import Any, Dict, List, Literal, Union
import logging

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template


def _has_unrendered_tags(s: str) -> bool:
    """
    Detect if the string still contains Liquid tags that need rendering.
    """
    return "{{" in s or "{%" in s


class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: JSON-serialisable literal, list, dict or Liquid template string rendered against
               the current context.
        nested_render: Whether to render templates recursively until no tags remain.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """

    key: str
    value: Union[str, List[Any], Dict[str, Any]]
    nested_render: bool = False
    if_exists: Literal["overwrite", "merge"] = "overwrite"


class SetContextStep(BaseStep[SetContextConfig]):
    """
    Step to set or update an artifact in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, SetContextConfig.model_validate(config))

    async def execute(self, context: ContextProtocol) -> None:
        key = self.config.key
        raw_value = self.config.value
        nested = self.config.nested_render
        existed = key in context

        # Render the provided value (single or nested passes)
        value = self._render_value(raw_value, context, nested)

        strategy = self.config.if_exists
        if strategy == "overwrite":
            context[key] = value
        elif strategy == "merge":
            if existed:
                old = context[key]
                merged = self._merge(old, value)
                context[key] = merged
            else:
                context[key] = value
        else:
            raise ValueError(f"Unknown if_exists strategy: '{strategy}'")

        self.logger.info(f"SetContextStep: key='{key}', strategy='{strategy}', existed={existed}")

    def _render_value(self, raw: Any, context: ContextProtocol, nested: bool) -> Any:
        """
        Recursively render Liquid templates in strings, lists, and dicts.

        If nested is True, re-render strings until no tags remain or no change.
        """
        if isinstance(raw, str):
            if not nested:
                return render_template(raw, context)
            # nested rendering loop
            result = render_template(raw, context)
            while _has_unrendered_tags(result):
                prev = result
                result = render_template(result, context)
                if result == prev:
                    break
            return result

        if isinstance(raw, list):
            return [self._render_value(item, context, nested) for item in raw]

        if isinstance(raw, dict):
            return {k: self._render_value(v, context, nested) for k, v in raw.items()}

        # Other JSON-serialisable types pass through
        return raw

    def _merge(self, old: Any, new: Any) -> Any:
        """
        Shallow merge helper for merging existing and new values.

        Merge semantics:
        - str + str => concatenate
        - list + list or item => append
        - dict + dict => shallow dict merge
        - mismatched types => [old, new]
        """
        # String concatenation
        if isinstance(old, str) and isinstance(new, str):
            return old + new

        # List append
        if isinstance(old, list):  # type: ignore
            if isinstance(new, list):  # type: ignore
                return old + new  # type: ignore
            return old + [new]  # type: ignore

        # Dict shallow merge
        if isinstance(old, dict) and isinstance(new, dict):  # type: ignore
            merged = old.copy()  # type: ignore
            merged.update(new)  # type: ignore
            return merged

        # Fallback for mismatched types
        return [old, new]
