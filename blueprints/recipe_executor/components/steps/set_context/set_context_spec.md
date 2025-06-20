# SetContextStep Component Specification

## Purpose

The **SetContextStep** component provides a declarative way for recipes to create or update artifacts in the shared execution context.

## Core Requirements

- Accept a **key** (string) that identifies the artifact in `ContextProtocol`.
- Accept a **value** that may be:
  - Any JSON-serializable literal, **or**
  - A Liquid template string rendered against the current context before assignment.
- If `nested_render` is true, recursively render the `value` using context data until all variables are resolved, ignoring any template variables that are wrapped in `{% raw %}` tags
- Support an **if_exists** strategy with the following options:
  - `"overwrite"` (default) – replace the existing value.
  - `"merge"` – combine the existing and new values using type-aware rules.
- Implement shallow merge semantics when `if_exists="merge"`:
  | Existing type | New type | Result |
  | ------------- | -------------- | --------------------------------------------------------------- |
  | `str` | `str` | Concatenate: `old + new` |
  | `list` | `list` or item | Append: `old + new` |
  | `dict` | `dict` | Shallow dict merge; keys in `new` overwrite duplicates in `old` |
  | Mismatched | any | Create a 2-item list `[old, new]` |

## Implementation Considerations

- **Template rendering**:
  - When `value` is a string, call `render_template(value, context)` before assignment.
  - When `value` is a list or dict, call `render_template` on each item, all the way down.
  - If `nested_render` is true, recursively render the `value` using context data until all variables are resolved, ignoring any template variables that are wrapped in `{% raw %}` tags
    - When `true`, after the initial `render_template` pass on `value`, repeat rendering while the string both changes **and** still contains Liquid tags (`{{` or `{%}`), ignoring `{% raw %}`. This ensures nested templates inside your `value` get fully expanded.
- **Merge helper**: Encapsulate merge logic in a small private function to keep `execute()` readable.

## Logging

- _Info_: one-line message indicating `key`, `strategy`, and whether the key previously existed.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context read/write operations.
- **Context**: Uses `Context` for storing artifacts.
- **Step Base**: Inherits from `BaseStep` and uses `StepConfig` for validation.
- **Utilities**: Calls `render_template` for Liquid evaluation.

### External Libraries

None

### Configuration Dependencies

None.

## Error Handling

- Raise `ValueError` for unknown `if_exists` values.
- Allow merge helper to fall back to `[old, new]` to avoid hard failures on type mismatch.
- Propagate template rendering errors unchanged for visibility.

## Output Files

- `recipe_executor/steps/set_context.py` – implementation of **SetContextStep**.
