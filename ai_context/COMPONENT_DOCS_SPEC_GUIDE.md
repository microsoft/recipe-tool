# Comprehensive Guide to Creating Effective Component Documentation and Specifications

## Introduction

This guide outlines how to create high-quality component documentation and specifications that enable AI-assisted code generation in a modular software architecture. When documentation and specifications work together effectively, they form a complete blueprint that allows for predictable, reliable code generation with minimal human intervention.

### Purpose of This Guide

This guide serves multiple purposes:

- To help **evaluate candidate specifications** to determine if they contain sufficient information
- To generate **clarifying questions** when information is insufficient
- To create clear, comprehensive **documentation and specification files** that support modular AI code generation

### Core Principles of Documentation and Specification

- **Separation of Concerns**: Documentation focuses on component usage, while specifications focus on component implementation
- **Complete Information**: Together, documentation and specifications must provide all information needed for both component users and implementers
- **Clear Boundaries**: Explicit API contracts and interfaces enable independent development
- **Implementation Freedom**: Specifications should constrain only what's necessary, allowing creative implementation approaches
- **Consistency**: Terminology, structure, and formatting should be consistent across all components

## A Complete Blueprint

Component documentation and specifications are two sides of the same coin. They should be created in tandem to ensure that the component is well-defined and easy to use. The documentation is the contract between the component and its consumers and represents the external knowledge of the component, while the specifications provides the remaining details needed for implementation and any internal-only knowledge of the component. The documentation should remain stable from version to version because other components depend on it. The specifications may change more frequently as the architecture evolves, as new features are added, as the implementation is improved, or as the architecture is restructured. Specifications should avoid unnecessary details or content already covered in the documentation.

The goal is to create a complete blueprint that allows for independent implementation of each component while ensuring that the components work together seamlessly. This guide provides best practices for both documentation and specifications, as well as common pitfalls to avoid.

## Component Documentation Best Practices

### Structure and Organization

Well-structured documentation includes:

- **Importing Section**: How to import the component
- **Basic Usage**: Simple examples showing common use cases
- **API Reference**: Detailed description of each method/function
- **Example Patterns**: More complex usage examples
- **Integration Guidelines**: How to use with other components
- **Important Notes**: Critical things developers should know

### Code Examples

Effective code examples should:

- Start with the simplest possible use case
- Progress to more complex scenarios
- Include comments explaining key parts
- Show both initialization and usage
- Optionally demonstrate error handling where not obvious
- Be as concise as possible but complete enough to run if copied

Example:

```python
# Create context and executor
context = Context()
executor = Executor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_files", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)
```

### API Documentation Guidelines

#### Public vs. Internal API Distinction

When documenting APIs, it's critical to distinguish between:

- **Public APIs**: Methods and functions intended for use by component consumers
- **Internal APIs**: Methods and functions used only within the component

**Public APIs** should be fully documented in the **documentation file**, while **internal APIs** should be documented in the **specification file**.

#### Method Documentation

Document each _consumer exposed_ method with:

- Method signature with type hints
- Purpose description
- Parameter explanations
- Return value description
- Possible exceptions/errors
- Usage examples
- Any side effects or important notes

##### Public API Method Example (for Docs)

```python
def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

##### Internal API Method Example (for Specs)

```python
def _normalize_model_identifier(model_id: str) -> Tuple[str, str]:
    """
    Parse and normalize a model identifier string into provider and model name.

    This is an internal method used by the LLM component to standardize model identifiers.

    Args:
        model_id (str): Model identifier in format 'provider:model_name'

    Returns:
        Tuple[str, str]: (provider, model_name) tuple

    Raises:
        ValueError: If model_id format is invalid
    """
```

#### API Documentation Best Practices

- Document all parameters, including optional ones
- Be explicit about parameter types and constraints
- Document all potential return values and their meanings
- List all exceptions that might be raised and why
- Provide complete method signatures with type hints
- Include short, focused usage examples
- Indicate thread safety considerations
- Mark methods as "experimental" or "stable" when relevant
- Use consistent documentation style across all methods

### Integration Examples

Show how components work together:

- Demonstrate common integration patterns
- Illustrate correct sequencing of operations
- Show data flow between components
- Include common use cases in the larger system

Example:

```python
# Initialize components
context = Context(artifacts={"component_id": "utils"})
logger = init_logger()
executor = Executor()

# Execute recipe with context and logger
executor.execute("recipes/generate_component.json", context, logger)

# Access results from context
result = context["generation_result"]
```

### Important Notes & Warnings

Highlight critical information:

- Common pitfalls or misunderstandings
- Performance considerations
- Thread safety concerns
- Order-dependent operations

Example:

```markdown
- The context is mutable and shared between steps
- Values can be of any type
- Configuration is read-only in typical usage (but not enforced)
- Step authors should document keys they read/write
- Context provides no thread safety - it's designed for sequential execution
```

## Implementation Detail Guidelines

The level of implementation detail in a specification should be carefully calibrated to provide sufficient guidance without over-constraining implementation. Follow these guidelines for determining appropriate detail levels:

### When to Use Minimal Detail

Use minimal implementation details (general principles only) when:

- The component has a straightforward implementation with common patterns
- Multiple valid implementation approaches exist
- The component serves primarily as a data structure or simple utility
- The exact implementation details are not critical to system integration

Example (Context component):

```markdown
## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
```

### When to Use Moderate Detail

Use moderate implementation details (with some specific guidance) when:

- The component has specific requirements that constrain implementation choices
- Certain implementation patterns are preferred for performance or maintainability
- The component interacts with other components in ways that require specific approaches
- There are known pitfalls or challenges that should be avoided

Example (LLM component):

```markdown
## Implementation Considerations

- Use a clear provider:model_name identifier format
- Do not pass api keys directly to model classes
- Use PydanticAI's provider-specific model classes, passing only the model name
- Create a PydanticAI Agent with the model and a structured output type
- CRITICAL: make sure to return the result.data in the call_llm method
```

### When to Use High Detail

Use high implementation details (possibly with code snippets) when:

- The component interacts with external libraries in specific ways
- The implementation requires precise code patterns
- Documentation for critical libraries is limited or complex
- The component serves as a critical integration point
- A specific algorithm or approach is required

Example (Azure OpenAI component):

````markdown
## Implementation Hints

```python
azure_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

openai_model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```
````

````

### Balancing Detail and Flexibility

Always aim for the minimum level of detail needed for successful implementation. When in doubt:
- Focus on the "what" more than the "how"
- Specify constraints and requirements clearly
- Add detail for complex integrations or non-obvious implementations
- Provide examples for clarification, not prescription
- Consider whether details belong in the spec or in component documentation

## Component Specification Best Practices

### Structure and Organization

A well-structured component specification MUST include all of the following sections. If a section does not apply to the component, explicitly include the section header followed by "None" to indicate intentional omission:

- **Component Title**: Clear, concise name that reflects the component's purpose
- **Purpose Statement**: 2-3 sentences describing what the component does and why it exists
- **Core Requirements**: Bulleted list of essential functionality
- **Implementation Considerations**: Guidance on how to approach the implementation
- **Implementation Hints**: Integration guidance for complex dependencies (use "None" if no special integration instructions exist)
- **Component Dependencies**: Other components this one interacts with
- **Output Files**: List of files to be generated from this specification
- **Logging**: Required messages for debugging and monitoring (use "None" if the component does not require logging)
- **Error Handling**: Expected approach to failures and edge cases

## Implementation Section Naming

The implementation section may use one of three standard variations, based on the level of detail and specificity needed:

- **Implementation Considerations** (Standard): Use for general guidance on implementation approach without dictating exact solutions. This is the default option suitable for most components.

   Example:
   ```markdown
   ## Implementation Considerations

   - Use simple dictionary-based storage internally
   - Copy input dictionaries to prevent external modification
   - Provide clear error messages for missing keys
````

- **Implementation Hints** (Targeted): Use for brief, specific suggestions or tips that guide implementation without full code examples.

  Example:

  ````markdown
  ## Implementation Hints

  ```python
  azure_client = AsyncAzureOpenAI(
      azure_ad_token_provider=token_provider,
      azure_endpoint=AZURE_OPENAI_ENDPOINT,
      api_version=AZURE_OPENAI_API_VERSION,
      azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
  )
  ```
  ````

  ```

  ```

When working with families of related components (e.g., multiple steps), maintain consistency in section naming across the family. Each component should use the same section variants as other components of the same type.

### Purpose Statement Clarity

The purpose statement should:

- Define the component's role in the larger system
- Establish boundaries of responsibility
- Avoid implementation details
- Be understandable without deep technical knowledge

Example:

```markdown
The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.
```

### Requirement Specificity

Requirements should be:

- Actionable and verifiable
- Focused on what, not how
- Free of ambiguity
- Collectively exhaustive (cover all needed functionality)
- Individually clear (one requirement per bullet)

Example:

```markdown
- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Ensure data isolation between different executions
```

### Implementation Guidance

Provide direction without over-constraining by:

- Suggesting approaches without dictating exact implementations
- Highlighting technical constraints or performance considerations
- Addressing known challenges or trade-offs
- Ensuring alignment with architectural principles

Example:

```markdown
- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
```

### Dependency Clarity

When specifying dependencies, use a standardized approach with clear categorization:

#### Categorization Structure

```markdown
## Component Dependencies

### Internal Components

- **[Component Name]** - Brief description of relationship and usage

### External Libraries

- **[Library Name]** - Brief description of how this library is used

### Configuration Dependencies

- **[Config Name]** - Description of required configuration values
```

#### Relationship Description Format

Use consistent phrasing to describe relationships:

- "Uses X for Y" - When directly using functionality
- "Relies on X to Y" - When dependent on functionality
- "Interacts with X through Y" - When indirectly connected
- "Extends X to provide Y" - When building upon another component

#### Required vs. Optional Indication

Clearly indicate which dependencies are required versus optional:

```markdown
- **Context** - (Required) Uses Context for data sharing between steps
- **Logger** - (Optional) Uses Logger for detailed execution tracking
```

#### Dependency Context

Provide brief context explaining _why_ the dependency exists, not just what it is:

```markdown
- **Step Registry** - Uses STEP_REGISTRY to dynamically look up and instantiate step classes by their type names, enabling extensibility
```

#### Example of Well-Documented Dependencies

```markdown
## Component Dependencies

### Internal Components

- **Context** - (Required) Uses Context to retrieve input values and store generation results
- **LLM** - (Required) Uses call_llm function to interact with language models
- **Utils** - (Required) Uses render_template for dynamic content resolution
- **Logger** - (Optional) Uses Logger for tracing execution flow and debugging

### External Libraries

- **PydanticAI** - (Required) Uses Agent and Model classes for structured LLM interactions
- **Liquid** - (Required) Uses Liquid for template rendering within template strings

### Configuration Dependencies

- **MODEL_IDENTIFIER** - (Required) Environment variable specifying the default LLM model to use in format "provider:model_name"
```

If a component has no dependencies in a particular category, explicitly state "None" for that category:

```markdown
### External Libraries

None
```

### Logging Requirements

For logging sections:

- Specify log levels (e.g., debug, info, error)
- Define minimally required (non-exhaustive) log messages for each level

### Error Handling Specificity

For error handling sections:

- Identify expected error conditions
- Specify how each error should be handled
- Define error communication mechanisms
- Clarify recovery expectations

Example:

```markdown
- Validate recipe format before execution begins
- Check that step types exist in the registry before instantiation
- Verify each step is properly structured before execution
- Provide specific error messages identifying problematic steps
```

### Output Files

The Output Files section defines the physical artifacts that should be generated from this specification:

- List each file with its full relative path from the project root
- Include a brief description of each file's purpose
- For multi-file components, clearly indicate all required files
- Include any special naming conventions or path requirements
- For single-file components, at minimum specify the primary implementation file

Example:

```markdown
## Output Files

- `recipe_executor/steps/registry.py` - Main registry implementation with STEP_REGISTRY dictionary
- `recipe_executor/steps/__init__.py` - Package initialization with step registration code
```

This section helps standardize file organization and ensures that implementations follow consistent naming conventions. It also makes explicit the tangible outputs expected from the specification.

### Dependency Integration Considerations

- Provide hints or suggestions for integrating this component with its dependencies
- For complex integrations include limited example snippets from the dependency's documentation
- Avoid overloading this section with too much detail, prefer loading of documentation in the recipe

## Docs vs. Specs Content Separation

### Clear Separation Principles

Documentation and specifications serve different audiences and purposes. This separation is crucial for maintainability, clarity, and the success of modular AI code generation.

#### Documentation (Docs)

- **Primary Audience**: Component consumers (other developers)
- **Purpose**: Enables correct usage of the component
- **Content Stability**: Should remain stable as it serves as a contract with consumers
- **Focus**: External-facing functionality, APIs, and integration patterns

#### Specification (Specs)

- **Primary Audience**: Component implementers
- **Purpose**: Guides correct implementation of the component
- **Content Stability**: May evolve as implementation details change
- **Focus**: Internal details, requirements, and implementation guidance

### Content Placement Decision Tree

Use this decision tree to determine whether content belongs in documentation or specifications:

```
Does the information directly help someone USE the component?
├── YES → Is it about the external API or behavior?
│   ├── YES → Documentation
│   └── NO → Consider further...
└── NO → Is it about HOW the component works internally?
    ├── YES → Specification
    └── NO → Consider if the content is needed at all

Is the information needed by component CONSUMERS?
├── YES → Documentation
└── NO → Is it needed by component IMPLEMENTERS?
    ├── YES → Specification
    └── NO → Consider if the content is needed at all

Would this information change if the implementation changed?
├── YES → Specification
└── NO → Documentation
```

### Content Placement Checklist

#### Documentation Should Contain:

- Public API method signatures and descriptions
- Import statements and initialization examples
- Usage examples for common scenarios
- Integration examples with other components
- Input/output formats consumers need to know
- Public configuration options and environment variables
- Public error types and handling examples
- Performance characteristics relevant to usage

#### Specification Should Contain:

- Internal architecture and design decisions
- Implementation algorithms and patterns
- Internal method signatures and behavior
- Implementation constraints and considerations
- Integration with internal dependencies
- Logging requirements and formats
- Internal error handling strategies
- Complete list of environment variables
- Output file structure and organization

### The Component Documentation and Specifications Relationship

#### Complementary Focus

- **Documentation**: Focus on usage, examples, developer experience, and serves as the stable contract, detailing external knowledge of the component
- **Specifications**: Focus on requirements, constraints, architectural fit, and any implementation details not covered in the documentation, focusing on internal knowledge of the component
- Together, they should provide a complete picture that provides all necessary information for implementation and usage while avoiding redundancy

### Consistent Terminology

- Use identical terms for core concepts across specs and docs
- Define terms clearly in both documents
- Maintain consistent naming conventions for methods, parameters, and classes
- For implementation sections, use the appropriate variant based on content:
  - **Implementation Considerations**: General guidance on implementation approach
  - **Implementation Hints**: Brief suggestions or tips for implementation
- Maintain section name consistency within component families (e.g., all step components should use the same section names and structure)
- When a component belongs to a family (like steps), follow the patterns established by existing components in that family
- For implementation sections, use the appropriate variant based on content:
  - **Implementation Considerations**: General guidance on implementation approach
  - **Implementation Hints**: Brief suggestions or tips for implementation

### Functional Coverage Alignment

- Any requirement in the spec that is important for consumers of the component should be addressed in the documentation
- Documentation shouldn't introduce functionality not mentioned in specs

## Optimizing for Modular AI Code Generation

### Evaluation Criteria for Candidate Specs

When evaluating a candidate specification to determine if it has sufficient information for implementation, use the following criteria:

#### Essential Information (Must Have)

- **Clear Purpose**: Does it define what the component does and why it exists?
- **Complete Requirements**: Does it list all essential functionality?
- **Component Boundaries**: Does it clearly define inputs, outputs, and interfaces?
- **Integration Points**: Does it specify how it interacts with other components?
- **Output Files**: Does it specify exactly which files should be generated?

#### Clarity Assessment

- **Unambiguous Requirements**: Are requirements specific and verifiable?
- **Consistent Terminology**: Are terms used consistently throughout?
- **Appropriate Detail**: Does it provide the right level of implementation guidance?
- **Error Handling**: Are error cases and failure responses defined?

#### Sufficiency Examples

**Insufficient Requirement**:

```markdown
- Handle authentication for users
```

**Sufficient Requirement**:

```markdown
- Verify JWT tokens using PyJWT and extract user claims
- Support role-based access control with at least "admin" and "user" roles
- Provide middleware and dependency functions for FastAPI route protection
```

**Insufficient Implementation Guidance**:

```markdown
- Use good logging practices
```

**Sufficient Implementation Guidance**:

```markdown
- Log debug information for recipe start, file name, parsed payload, and completion
- Log specific error messages identifying problematic steps
- Include original exceptions for debugging
```

#### Candidate Spec Evaluation Checklist

When evaluating a candidate spec, answer these questions:

- [ ] Does it include all required sections (or explicitly mark them as "None")?
- [ ] Are the requirements specific and verifiable?
- [ ] Is the implementation guidance appropriate for the component complexity?
- [ ] Are component dependencies clearly identified?
- [ ] Are output files explicitly defined?
- [ ] Are error conditions and handling specified?
- [ ] Is the terminology consistent with other components?
- [ ] Does it avoid over-constraining the implementation?

### Explicit Boundaries

- Clearly define where one component ends and another begins
- Specify exact interfaces and contracts
- Make inputs and outputs unambiguous
- Define error states and handling explicitly

### Context Sufficiency

- Provide enough information for an isolated implementation, these components will be built in parallel and in isolation
- Include cross-references to related components when needed
- Supply concrete examples that illustrate expected behavior
- Clarify architectural principles that should guide implementation
- If a component is a building block, specify how it fits into the larger architecture
- If an integration is complex, it may be appropriate to include limited example snippets from the dependency's documentation
- Avoid overloading the specification with too much detail, prefer loading of documentation in the recipe

### Implementation Independence

- Focus on what the component does, not exactly how it does it
- Allow for creative implementations within constraints
- Specify constraints clearly but don't over-constrain
- Separate required behavior from implementation suggestions

### Testability Focus

- Include clear success criteria
- Define expected behaviors for edge cases
- Specify performance expectations where relevant
- Provide examples of valid and invalid inputs/outputs

## Modular Building-Block Approach Considerations

### Interface Stability

- Define stable connecting points between components
- Clearly mark which interfaces are public vs. internal, limit documentation to public interfaces
- Avoid breaking changes to public interfaces, this is the contract with the rest of the system

### Independent Regeneration Support

- Design components that can be replaced without breaking others
- Document all cross-component dependencies
- Ensure all state transitions are explicit
- Avoid hidden dependencies or assumptions
- Anticipate that code generation will result in internal implementation differences over time, but the external interfaces and behavior must be well enough defined to remain consistent

### Compatibility with Parallel Development

- Design components that can be developed independently, in parallel, and in isolation
- Provide clear interfaces and contracts for each component
- Document how variants might differ
- Specify minimum viable implementations
- Clarify how different implementations might be evaluated

### Evolution Path Support

- Document anticipated extension points
- Separate core functionality from optional features
- Establish clear versioning expectations

## Environment Variable Documentation

Environment variables provide crucial configuration for components. Proper documentation of environment variables is essential for both component users and implementers.

### Documentation vs. Specification Placement

#### Environment Variables in Documentation

Document in the component documentation only:

- Environment variables that component consumers must set to use the component
- Environment variables that change behavior in a way that affects component users
- Common configuration patterns with example values
- Default values and fallback behaviors

#### Environment Variables in Specification

Document in the component specification:

- Complete list of all supported environment variables (including those in docs)
- Internal-only environment variables used by the implementation
- Validation requirements and error handling for missing variables
- Format and value constraints for each variable
- Interaction between variables and precedence rules

### Environment Variable Documentation Format

For both docs and specs, use a consistent format:

```markdown
- **VARIABLE_NAME** - (Required|Optional) Brief description of purpose. Format: [format description]. Default: [default value if any].
```

Example for documentation:

```markdown
## Configuration

This component uses the following environment variables:

- **LLM_MODEL_NAME** - (Optional) Specifies the default model to use. Format: "provider:model". Default: "openai:gpt-4o".
- **LLM_API_KEY** - (Required) The API key for authenticating with the LLM provider.
```

Example for specification:

```markdown
## Configuration Dependencies

- **LLM_MODEL_NAME** - (Optional) Specifies the default model to use. Format: "provider:model". Default: "openai:gpt-4o".
- **LLM_API_KEY** - (Required) The API key for authenticating with the LLM provider. No default value.
- **LLM_TIMEOUT_SECONDS** - (Optional) Maximum time to wait for LLM response. Format: Integer seconds. Default: 30.
- **LLM_INTERNAL_CACHE_SIZE** - (Optional) Internal cache size for response caching. Format: Integer MB. Default: 100.
```

## Version Compatibility Guidelines

Components evolve over time. Proper documentation of version compatibility helps maintain stability while enabling innovation.

### Documenting API Compatibility

#### In Documentation

- Mark experimental APIs clearly as "Experimental" or "Beta"
- Document deprecated methods with alternatives
- Include version numbers where features were introduced or modified
- Provide migration guides for breaking changes

Example:

```markdown
### get_user_data(user_id: str) -> Dict[str, Any]

> _Added in v1.2.0_

Retrieves user data by ID.

### get_user(user_id: str) -> UserProfile

> _Added in v2.0.0. Replaces deprecated get_user_data()_

Retrieves a structured UserProfile object for the specified user.
```

#### In Specification

- Document version compatibility requirements
- Define semantic versioning policies
- Specify backward compatibility expectations
- Include transition plans for deprecated functionality

Example:

```markdown
## Version Compatibility

- This component follows semantic versioning (MAJOR.MINOR.PATCH)
- Public API changes that break backward compatibility require a MAJOR version increment
- New features that maintain backward compatibility increment the MINOR version
- Breaking changes must be avoided when possible
- Deprecated functionality should remain for at least one MAJOR version with warnings
```

## Common Pitfalls to Avoid

### Documentation Pitfalls

- **Incompleteness**: Failing to document all methods or parameters
- **Outdated examples**: Examples that no longer work with current code
- **Missing error handling**: Examples that don't show how to handle failures
- **Inconsistent style**: Mixing different coding styles in examples
- **Assuming context**: Not explaining prerequisites or dependencies
- **Internal details**: Including too much implementation detail that should be in the spec
- **Undocumented public API**: Failing to document all public methods and properties
- **Missing version information**: Not indicating when APIs were added or modified

### Specification Pitfalls

- **Ambiguity**: Vague requirements open to multiple interpretations
- **Implementation dictation**: Focusing too much on how instead of what
- **Missing constraints**: Failing to specify important limitations
- **Over-specification**: Constraining implementation unnecessarily
- **Inconsistent terminology**: Using multiple terms for the same concept
- **Overlapping content**: Duplicating information already in the documentation
- **Skipping required sections**: Omitting sections rather than explicitly marking them as "None"
- **Undefined output files**: Failing to specify exactly which files should be generated
- **Inconsistent section naming**: Using section names that don't match the template structure
- **Missing implementation guidance**: Not providing sufficient direction for implementation
- **Unbounded requirements**: Requirements without clear success criteria

### Required vs. Optional Content

While all sections are required to be present in the specification, some sections may legitimately have no content for certain components. In these cases:

- Always include the section header (e.g., "## Logging")
- Add "None" as the section content to explicitly indicate that the omission is intentional
- Do not simply skip sections that don't apply

This approach ensures that:

- All sections are consciously considered during specification creation
- LLM tools can reliably process specifications with a consistent structure
- Accidental omissions are prevented
- Readers can distinguish between "not applicable" and "forgotten"

Examples:

```markdown
## Logging

None
```

```markdown
## Dependency Integration Considerations

None
```

## Content Separation Examples

The following examples demonstrate proper separation of content between documentation and specification files for the same component.

### Proper Documentation Example

This example shows a well-structured documentation file that focuses on public API usage:

````markdown
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
```
````

## Initialization

The Context can be initialized with optional artifacts and configuration:

```python
# Method signature
def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the Context with optional artifacts and configuration.

    Args:
        artifacts: Initial artifacts to store
        config: Configuration values
    """
```

Examples:

```python
# Empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"spec": "specification content"})

# With configuration
context = Context(config={"output_dir": "./output"})

# With both
context = Context(
    artifacts={"spec": "specification content"},
    config={"output_dir": "./output"}
)
```

## Core API

### Storing Values

```python
# Usage example
context["key"] = value
```

### Retrieving Values

```python
# Usage examples
value = context["key"]  # Raises KeyError if not found
value = context.get("key", default=None)  # Returns default if not found
```

## Important Notes

- Context is mutable and shared between steps
- Values can be of any type
- Configuration is read-only in typical usage (but not enforced)
- Step authors should document keys they read/write
- Context provides no thread safety - it's designed for sequential execution

````

### Proper Specification Example

This example shows a well-structured specification file for the same component, focusing on implementation requirements:

```markdown
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements

- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Provide a clone() method that returns a deep copy of the context
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Use deep copy operations for the clone() method
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
- Maintain minimal state with clear separation of concerns

## Component Dependencies

### Internal Components

None

### External Libraries

- **copy** - (Required) Uses deepcopy for context cloning operations

### Configuration Dependencies

None

## Output Files

- `recipe_executor/context/context.py` - Main Context class implementation
- `recipe_executor/context/__init__.py` - Package exports for the Context class

## Logging

- Debug: Log context initialization with configuration parameters
- Info: None

## Error Handling

- Raise KeyError with descriptive message when accessing non-existent keys
- Include key name in error messages for easier debugging
- No special handling for setting values (all types allowed)

## Dependency Integration Considerations

None
````

### Ineffective Documentation Example

This example shows a poorly structured documentation file that doesn't adequately explain component usage:

````markdown
# Context Usage

The Context class is used to store data. You can create it like this:

```python
c = Context()
```
````

You can store and retrieve data:

```python
c["key"] = value
x = c["key"]
```

Make sure to handle errors.

````

### Ineffective Specification Example

This example shows a poorly structured specification file that doesn't provide adequate implementation guidance:

```markdown
# Context Component Specification

The Context will be a global data store object for passing data between steps. It should be as flexible as possible and handle all data types. We should consider potential threading issues, performance optimizations, and potential for future extensions.

It will probably need to be a dictionary-like object, maybe with some extra features. Make sure to include good error handling.

We might add namespacing later, so keep that in mind.
````

### Effective Specification Example

**Example: Context Component Specification**

```markdown
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements

- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
- Maintain minimal state with clear separation of concerns

## Component Dependencies

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Output Files

- `recipe_executor/context/context.py` - Main Context class implementation
- `recipe_executor/context/__init__.py` - Package exports for the Context class

## Logging

- Debug: Log all key-value pairs stored in the context
- Info: No specific info-level logging required

## Error Handling

- Raise KeyError with descriptive message when accessing non-existent keys
- No special handling for setting values (all types allowed)

## Dependency Integration Considerations

None
```

**Example: LLM Component Specification with Complex Dependencies**

```markdown
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI for consistent handling and validation of LLM responses
- Implement basic error handling
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Do not pass api keys directly to model classes, the model classes will load them from the environment
- Use PydanticAI's provider-specific model classes, passing only the model name
- Create a PydanticAI Agent with the model and a structured output type
- Use the `run_sync` method of the Agent to make requests
- CRITICAL: make sure to return the result.data in the call_llm method

## Component Dependencies

### Internal Components

- **Models** - (Required) Uses FileGenerationResult and FileSpec for structured output validation
- **Azure OpenAI** - (Required) Uses get_azure_openai_model for Azure OpenAI model initialization

### External Libraries

- **pydantic-ai** - (Required) Relies on PydanticAI for model initialization, request handling, and response processing
- **openai** - (Required) Uses the OpenAI Python client for API interactions with OpenAI models
- **anthropic** - (Required) Uses the Anthropic Python client for API interactions with Claude models
- **google-generativeai** - (Required) Uses the Google Generative AI client for Gemini models

### Configuration Dependencies

- **MODEL_IDENTIFIER** - (Required) Environment variable specifying the default LLM model in format "provider:model_name"
- **OPENAI_API_KEY** - (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY** - (Required for Anthropic) API key for Anthropic access
- **GOOGLE_API_KEY** - (Required for Gemini) API key for Google Generative AI access
- **AZURE_OPENAI_API_KEY** - (Required for Azure) API key for Azure OpenAI if not using managed identity

## Output Files

- `recipe_executor/llm/llm.py` - Main implementation with provider-specific handling
- `recipe_executor/llm/__init__.py` - Package exports for the LLM interface

## Logging

- Debug: Log full request payload before making call and then full response payload after receiving it
- Info: Log model name and provider (no payload details) and response times

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging
- Include provider-specific error handling for each supported LLM service

## Dependency Integration Considerations

### PydanticAI Integration

- Use the pydantic-ai library for model initialization, request handling, and response processing
- Create provider-specific model instances based on the provider prefix in the model identifier
- Pass the appropriate structured output type to the Agent constructor
- Use the run_sync method for synchronous LLM calls
```

### Ineffective Specification Example

```markdown
# Context Component Specification

The Context will be a global data store object for passing data between steps. It should be as flexible as possible and handle all data types. We should consider potential threading issues, performance optimizations, and potential for future extensions.

It will probably need to be a dictionary-like object, maybe with some extra features. Make sure to include good error handling.

We might add namespacing later, so keep that in mind.
```

## Implementation Examples Across Components

To ensure consistency across component families, refer to these example patterns from existing component types:

### Step Component Pattern

Step components should follow this documentation and specification pattern:

**Documentation Structure**:

- Configuration parameters
- Usage in recipes (JSON examples)
- Integration with other steps
- Error handling from a user perspective

**Specification Structure**:

- Core requirements specific to this step type
- Integration with step registry
- Logging specifics relevant to step execution
- Error handling implementation

### Core Component Pattern

Core components (like Context, Executor) should follow this pattern:

**Documentation Structure**:

- Public API methods with examples
- Initialization options
- Common usage patterns
- Integration with other core components

**Specification Structure**:

- Internal architecture
- Processing flow diagrams
- State management approach
- Performance considerations

## Documentation Template

For quick reference, here's a documentation template:

````markdown
# ComponentName Usage

## Importing

```python
from package.module import ComponentName
```
````

## Initialization

```python
component = ComponentName(param1="value", param2=42)
```

## Core API

### Method1

Signature, description, examples

### Method2

Signature, description, examples

## Common Usage Patterns

Examples of typical use cases

## Integration with Other Components

How this component works with others

## Important Notes

Critical information for users

````

## Specification Template

For quick reference, here's a specification template:

```markdown
# ComponentName Specification

## Purpose

What this component does and why it exists.

## Core Requirements

- Requirement 1
- Requirement 2
- ...

## Implementation Considerations

- Implementation guidance 1
- Implementation guidance 2
- ...

## Component Dependencies

### Internal Components

- **Component1** - (Required|Optional) Relationship description

### External Libraries

- **Library1** - (Required|Optional) Usage description

### Configuration Dependencies

- **CONFIG_VAR** - (Required|Optional) Purpose description

## Output Files

- `path/to/file1.py` - Purpose description
- `path/to/file2.py` - Purpose description

## Logging

- Debug: Required debug log messages
- Info: Required info log messages
- Error: Required error log messages

## Error Handling

- Error scenario 1 handling approach
- Error scenario 2 handling approach

## Dependency Integration Considerations

Specific integration guidance (or "None")
````

## Conclusion

Creating effective component specifications and documentation is crucial for enabling AI-assisted code generation in a modular architecture. By following these guidelines, you can create clear, comprehensive blueprints that allow for reliable and predictable implementation of each building block in your system. Each AI code generation pass may result in differences in the generated code, but the external interfaces and behavior should remain consistent. This will help ensure that the components can be developed in parallel and in isolation, while still being compatible with the overall system architecture.

The proper separation of concerns between documentation (focused on component usage) and specification (focused on component implementation) is essential for maintaining clarity and long-term maintainability. Documentation acts as a stable contract with consumers, while specifications provide the implementation guidance needed to fulfill that contract.

Remember that the goal is to provide sufficient information for independent implementation while maintaining compatibility with the overall system architecture. When specifications and documentation work together effectively, they create a foundation for an efficient, adaptable development process that leverages AI capabilities while preserving architectural integrity.
