"""Reusable settings sidebar component for Gradio apps."""

import os
from typing import Any, Callable, Dict, List, Optional

import gradio as gr
from pydantic import BaseModel


class SettingsConfig(BaseModel):
    """Configuration for the settings sidebar."""

    # Model settings
    model_providers: List[str] = ["openai", "azure", "anthropic", "ollama"]
    default_model: str = "openai/o4-mini"

    # Environment variable definitions
    env_vars: Dict[str, Dict[str, Any]] = {
        # OpenAI
        "OPENAI_API_KEY": {
            "label": "OpenAI API Key",
            "type": "password",
            "provider": "openai",
            "required": True,
        },
        # Anthropic
        "ANTHROPIC_API_KEY": {
            "label": "Anthropic API Key",
            "type": "password",
            "provider": "anthropic",
            "required": True,
        },
        # Azure OpenAI
        "AZURE_OPENAI_BASE_URL": {
            "label": "Azure OpenAI Base URL",
            "type": "text",
            "provider": "azure",
            "required": True,
            "placeholder": "https://your-resource.openai.azure.com/",
        },
        "AZURE_OPENAI_API_KEY": {
            "label": "Azure OpenAI API Key",
            "type": "password",
            "provider": "azure",
            "required": False,  # Not required if using managed identity
        },
        "AZURE_OPENAI_API_VERSION": {
            "label": "Azure API Version",
            "type": "text",
            "provider": "azure",
            "default": "2025-03-01-preview",
            "required": False,
        },
        "AZURE_USE_MANAGED_IDENTITY": {
            "label": "Use Azure Managed Identity",
            "type": "checkbox",
            "provider": "azure",
            "default": False,
            "required": False,
        },
        "AZURE_MANAGED_IDENTITY_CLIENT_ID": {
            "label": "Azure Managed Identity Client ID",
            "type": "text",
            "provider": "azure",
            "required": False,
            "placeholder": "Optional - specific managed identity to use",
        },
        # Ollama
        "OLLAMA_BASE_URL": {
            "label": "Ollama Base URL",
            "type": "text",
            "provider": "ollama",
            "default": "http://localhost:11434",
            "required": False,
        },
        # General
        "LOG_LEVEL": {
            "label": "Log Level",
            "type": "dropdown",
            "provider": None,
            "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "default": "INFO",
            "required": False,
        },
    }

    # Model configurations
    model_configs: Dict[str, List[str]] = {
        "openai": ["gpt-4o", "gpt-4.1", "o3", "o4-mini"],
        "azure": ["gpt-4o", "gpt-4.1", "o3", "o4-mini"],
        "anthropic": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
        "ollama": ["llama3.2", "mistral", "gemma2", "phi3"],
    }


def create_settings_sidebar(
    config: Optional[SettingsConfig] = None,
    on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Create settings components for the Gradio sidebar.

    Args:
        config: Settings configuration (uses defaults if not provided)
        on_save: Optional callback when settings are saved

    Returns:
        Dict of component references
    """
    if config is None:
        config = SettingsConfig()

    components = {}

    with gr.Accordion("Model Configuration", open=True):
        # Model provider dropdown
        provider = gr.Dropdown(
            label="Model Provider",
            choices=config.model_providers,
            value=config.default_model.split("/")[0],
            interactive=True,
        )
        components["provider"] = provider

        # Model selection (dynamic based on provider)
        model_name = gr.Dropdown(
            label="Model",
            choices=config.model_configs.get(config.default_model.split("/")[0], []),
            value=config.default_model.split("/")[1] if "/" in config.default_model else "",
            interactive=True,
        )
        components["model_name"] = model_name

        # Azure deployment name (only shown for Azure)
        azure_deployment = gr.Textbox(
            label="Azure Deployment Name",
            placeholder="Optional - defaults to model name",
            visible=False,
            interactive=True,
        )
        components["azure_deployment"] = azure_deployment

        # Max tokens
        max_tokens = gr.Number(
            label="Max Tokens",
            value=None,
            minimum=1,
            maximum=128000,
            step=1,
            interactive=True,
            info="Leave empty for model default",
        )
        components["max_tokens"] = max_tokens

    with gr.Accordion("API Configuration", open=False):
        # Create inputs for each environment variable
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")

            # Determine visibility based on provider
            visible = provider_match is None or provider_match == config.default_model.split("/")[0]

            if var_config["type"] == "password":
                component = gr.Textbox(
                    label=var_config["label"],
                    type="password",
                    value=os.getenv(var_name, ""),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "checkbox":
                default_val = var_config.get("default", False)
                env_val = os.getenv(var_name, "").lower() in ("1", "true", "yes")
                component = gr.Checkbox(
                    label=var_config["label"],
                    value=env_val if os.getenv(var_name) else default_val,
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "dropdown":
                component = gr.Dropdown(
                    label=var_config["label"],
                    choices=var_config.get("choices", []),
                    value=os.getenv(var_name, var_config.get("default", "")),
                    visible=visible,
                    interactive=True,
                )
            else:  # text
                component = gr.Textbox(
                    label=var_config["label"],
                    value=os.getenv(var_name, var_config.get("default", "")),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )

            components[var_name] = component

    # Save and status
    with gr.Row():
        save_btn = gr.Button("💾 Save Settings", variant="primary", scale=2)
        components["save_btn"] = save_btn

    status = gr.Markdown("", visible=False)
    components["status"] = status

    # Set up event handlers
    def update_model_choices(provider: str) -> Dict[str, Any]:
        """Update model choices based on provider selection."""
        models = config.model_configs.get(provider, [])
        updates = {
            "model_name": gr.update(choices=models, value=models[0] if models else ""),
            "azure_deployment": gr.update(visible=(provider == "azure")),
        }

        # Update visibility of provider-specific settings
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")
            if provider_match is not None:
                visible = provider_match == provider
                updates[var_name] = gr.update(visible=visible)

        return updates

    # Connect provider change to update function
    outputs = [components["model_name"], components["azure_deployment"]]
    outputs.extend([components[var_name] for var_name in config.env_vars.keys()])

    provider.change(
        fn=update_model_choices,
        inputs=[provider],
        outputs=outputs,
    )

    def save_settings(**kwargs) -> str:
        """Save settings to environment and optionally call callback."""
        try:
            # Build model string
            provider = kwargs.get("provider", "openai")
            model_name = kwargs.get("model_name", "o4-mini")
            azure_deployment = kwargs.get("azure_deployment", "")

            if provider == "azure" and azure_deployment:
                model_str = f"{provider}/{model_name}/{azure_deployment}"
            else:
                model_str = f"{provider}/{model_name}"

            # Prepare settings dict
            settings = {
                "model": model_str,
                "max_tokens": kwargs.get("max_tokens"),
            }

            # Set environment variables
            for var_name in config.env_vars.keys():
                value = kwargs.get(var_name)
                if value is not None and value != "":
                    if isinstance(value, bool):
                        os.environ[var_name] = "true" if value else "false"
                    else:
                        os.environ[var_name] = str(value)

            # Add env vars to settings
            settings.update({k: v for k, v in kwargs.items() if k in config.env_vars})

            # Call callback if provided
            if on_save:
                on_save(settings)

            return "✅ Settings saved successfully!"

        except Exception as e:
            return f"❌ Error saving settings: {str(e)}"

    # Connect save button
    save_inputs = list(components.values())[:-2]  # Exclude save_btn and status
    save_btn.click(
        fn=save_settings,
        inputs=save_inputs,
        outputs=[status],
    ).then(
        lambda: gr.update(visible=True),
        outputs=[status],
    ).then(
        lambda: gr.update(visible=False),
        outputs=[status],
        js="() => new Promise(resolve => setTimeout(() => resolve(), 3000))",
    )

    return components


def get_model_string_from_env() -> str:
    """Get the current model string from environment or use default."""
    # Check for explicit model env var first
    if os.getenv("MODEL"):
        return os.getenv("MODEL", "openai/o4-mini")

    # Otherwise, try to construct from available info
    # Default to OpenAI if available
    if os.getenv("OPENAI_API_KEY"):
        return "openai/o4-mini"
    elif os.getenv("AZURE_OPENAI_BASE_URL"):
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o4-mini")
        return f"azure/o4-mini/{deployment}"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic/claude-3-5-sonnet"
    elif os.getenv("OLLAMA_BASE_URL"):
        # Use environment variable or default to a more common model
        return os.getenv("OLLAMA_DEFAULT_MODEL", "ollama/llama3.2")
    else:
        # Final fallback to OpenAI
        return "openai/o4-mini"
