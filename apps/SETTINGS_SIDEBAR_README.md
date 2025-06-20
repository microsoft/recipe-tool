# Settings Sidebar Component

A reusable Gradio component for managing LLM and API settings across apps using Gradio's native sidebar.

## Features

- **Model Configuration**: Select provider (OpenAI, Azure, Anthropic, Ollama) and model
- **API Keys Management**: Secure input fields for API keys
- **Azure Support**: Full Azure OpenAI configuration including managed identity
- **Environment Variables**: Automatically saves settings to environment
- **Provider-Specific UI**: Shows only relevant settings for selected provider
- **Native Sidebar**: Uses Gradio's built-in `gr.Sidebar` component

## Usage

### Basic Usage

```python
from your_app.settings_sidebar import create_settings_sidebar
import gradio as gr

with gr.Blocks() as app:
    # Create settings in the sidebar
    with gr.Sidebar():
        gr.Markdown("### ⚙️ Settings")
        components = create_settings_sidebar()
    
    # Your main UI content
    # Your app content here
```

### With Callback

```python
def on_settings_save(settings: Dict[str, Any]) -> None:
    """Handle settings updates."""
    print(f"Model: {settings['model']}")
    print(f"Max tokens: {settings['max_tokens']}")

with gr.Sidebar():
    gr.Markdown("### ⚙️ Settings")
    components = create_settings_sidebar(on_save=on_settings_save)
```

### Custom Configuration

```python
from your_app.settings_sidebar import SettingsConfig

config = SettingsConfig(
    default_model="anthropic/claude-3-5-sonnet",
    model_providers=["openai", "anthropic"],  # Limit providers
    env_vars={
        # Add custom environment variables
        "CUSTOM_VAR": {
            "label": "Custom Setting",
            "type": "text",
            "provider": None,
            "required": False,
        }
    }
)

with gr.Sidebar():
    gr.Markdown("### ⚙️ Settings")
    components = create_settings_sidebar(config=config)
```

## Environment Variables

The sidebar manages these environment variables:

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `AZURE_OPENAI_BASE_URL`: Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Azure API key (optional with managed identity)
- `AZURE_OPENAI_API_VERSION`: API version (default: 2025-03-01-preview)
- `AZURE_USE_MANAGED_IDENTITY`: Enable managed identity authentication
- `AZURE_MANAGED_IDENTITY_CLIENT_ID`: Specific managed identity to use
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `LOG_LEVEL`: Application log level

## Model String Format

Models are identified using the format: `provider/model_name[/deployment_name]`

Examples:
- `openai/gpt-4o`
- `azure/gpt-4o/my-deployment`
- `anthropic/claude-3-5-sonnet`
- `ollama/llama3.2`

## Integration with Recipe Executor

The settings sidebar automatically updates the recipe executor context with:
- `model`: The selected model string
- `max_tokens`: Optional token limit

These values are available in recipes for LLM generation steps.

## Copying to Other Apps

To use in another app:

1. Copy `settings_sidebar.py` to your app directory
2. Import and use as shown above
3. The component is self-contained and portable

## Features

- **Auto-save to environment**: Settings persist across app restarts
- **Dynamic UI**: Shows only relevant fields based on provider
- **Validation**: Ensures required fields are set
- **Status feedback**: Visual confirmation when settings are saved
- **Responsive design**: Adapts to different screen sizes