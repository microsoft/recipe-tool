# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
from recipe_executor.protocols import ContextProtocol
```

_(The `ContextProtocol` interface is imported for typing or interface reference, while `Context` is the concrete class you instantiate.)_

## Initialization

You can create a Context with or without initial data:

```python
# Create an empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"input": "example data"})

# With configuration values
context = Context(config={"run_mode": "test"})

# With both artifacts and configuration
context = Context(
    artifacts={"input": "example data"},
    config={"run_mode": "test"}
)
```

When providing initial artifacts or config, Context will deep-copy them. Changes to the original dictionaries after creation won’t affect the Context.

## Core API

Once you have a Context, you use it like a dictionary for artifacts:

### Storing Values

```python
context["result"] = 42
```

Stores the value `42` under the key `"result"` in the context’s artifacts.

### Retrieving Values

```python
value = context["result"]          # Retrieves the value for "result" (KeyError if missing)
value_or_default = context.get("missing", default_value)
```

Use `context[key]` for direct access (which will throw an error if the key is not present), or `context.get(key, default)` to safely retrieve a value with a fallback.

### Checking for Keys

```python
if "result" in context:
    # Key exists in context
    print(context["result"])
```

The `in` operator checks if a given artifact key exists in the context.

### Iterating over Keys

```python
for key in context:
    print(key, context[key])

# Or equivalently:
for key in context.keys():
    print(key, context[key])
```

Context supports iteration, yielding each artifact key (internally, it iterates over a snapshot list of keys to avoid issues if you modify the context during iteration). You can also call `keys()` to get an iterator of keys explicitly. The `len(context)` function returns the number of artifacts currently stored.

### Getting All Values

```python
snapshot = context.dict()
```

`dict()` returns a deep copy of all artifacts in the context as a regular Python dictionary. This is useful if you need to inspect or serialize the entire state without risk of modifying the Context itself.

```python
snapshot_json = context.json()
```

`json()` returns a JSON string representation of the context’s artifacts. This is useful for logging or sending the context over a network.

### Cloning the Context

```python
new_context = context.clone()
```

The `clone()` method creates a deep copy of the Context, including all artifacts and configuration. The returned object is a new `Context` instance that can be modified independently of the original. This is often used when running sub-recipes or parallel steps to ensure each execution has an isolated context state.

### Configuration Management

The Context class manages configuration values separately from artifacts. You can retrieve the entire configuration dictionary with `get_config()`, or set it with `set_config()`. This allows you to manage recipe-specific configuration values without cluttering the artifact namespace.

```python
# Get a configuration value
config = context.get_config()
api_key = config.get("api_key")

# Set a configuration value
context.set_config(config)
```

## Important Notes

- **Shared State**: The Context is shared across all steps in a recipe execution. Any step that writes to the context (e.g., `context["x"] = value`) is making that data available to subsequent steps. This is how data flows through a recipe.
- **No Thread Safety**: The Context class does not implement any locking or thread-safety mechanisms. It assumes sequential access. If you need to use it in parallel, each parallel thread or process should work on a cloned copy of the Context to avoid race conditions (as done in the Parallel step implementation).
- **Protocols Interface**: The `Context` class implements the `ContextProtocol` interface defined in the Protocols component. When writing code that interacts with contexts, you can use `ContextProtocol` in type hints to allow any context implementation. In practice, you will typically use the provided `Context` class unless you extend the system.
- **Configuration vs Artifacts**: Remember that context configuration is only available via `context.get_config()` and `context.set_config()`. It is not manipulated via the dictionary interface (`__getitem__`/`__setitem__`). This separation is by convention; Context does not prevent you from modifying the configuration, so it is up to developers to decide how to manage configuration values.
