"""Reusable settings sidebar component for Gradio apps."""

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import gradio as gr
from pydantic import BaseModel

from .config_manager import get_env_or_default, get_model_string, get_setting, is_override
from .config_manager import save_settings as save_config


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

    def get_label_suffix(key: str, default_value: Any = None) -> str:
        """Get label suffix based on where the value comes from."""
        # Reload settings to get fresh data
        if is_override(key):
            return ""  # No suffix for overrides
        elif get_env_or_default(key):
            return " [ENV]"
        else:
            return " [DEFAULT]"

    # Get current model from config/environment - this already calls get_setting which loads fresh data
    current_model = get_model_string()
    model_parts = current_model.split("/")
    current_provider = model_parts[0] if len(model_parts) > 0 else "openai"
    current_model_name = model_parts[1] if len(model_parts) > 1 else "o4-mini"
    current_deployment = model_parts[2] if len(model_parts) > 2 else ""

    with gr.Column():
        gr.Markdown("### Model Configuration")
        # Model provider dropdown - mark openai as default
        provider_choices = [f"{p} [DEFAULT]" if p == "openai" else p for p in config.model_providers]
        # Match the value with choices - if openai is in choices with [DEFAULT], use that
        if current_provider == "openai" and "openai [DEFAULT]" in provider_choices:
            provider_value = "openai [DEFAULT]"
        else:
            provider_value = current_provider

        provider = gr.Dropdown(
            label="Model Provider" + get_label_suffix("MODEL"),
            choices=provider_choices,
            value=provider_value,
            interactive=True,
        )
        components["provider"] = provider

        # Model selection (dynamic based on provider) - mark o4-mini as default for openai
        model_choices = config.model_configs.get(current_provider, [])
        if current_provider == "openai":
            model_choices = [f"{m} [DEFAULT]" if m == "o4-mini" else m for m in model_choices]
            # Only show [DEFAULT] if we're actually using the default
            if current_model_name == "o4-mini" and not is_override("MODEL") and get_env_or_default("MODEL") is None:
                model_value = "o4-mini [DEFAULT]"
            else:
                model_value = current_model_name
        else:
            model_value = current_model_name

        model_name = gr.Dropdown(
            label="Model" + get_label_suffix("MODEL"),
            choices=model_choices,
            value=model_value,
            interactive=True,
        )
        components["model_name"] = model_name

        # Azure deployment name (only shown for Azure)
        azure_deployment = gr.Textbox(
            label="Azure Deployment Name" + get_label_suffix("AZURE_OPENAI_DEPLOYMENT_NAME"),
            placeholder="Optional - defaults to model name",
            value=current_deployment,
            visible=(current_provider == "azure"),
            interactive=True,
        )
        components["azure_deployment"] = azure_deployment

        # Max tokens
        max_tokens_str = get_setting("MAX_TOKENS")
        # Only convert to int if we have a value, otherwise keep None for empty field
        try:
            max_tokens_value = int(max_tokens_str) if max_tokens_str and max_tokens_str.strip() else None
        except (ValueError, TypeError):
            max_tokens_value = None

        # gr.Number doesn't support None/empty, so we'll use Textbox with number validation
        max_tokens = gr.Textbox(
            label="Max Tokens" + get_label_suffix("MAX_TOKENS"),
            value=str(max_tokens_value) if max_tokens_value is not None else "",
            placeholder="Leave empty for model default",
            interactive=True,
            info="Number between 1-128000, or leave empty for model default",
        )
        components["max_tokens"] = max_tokens

    with gr.Column():
        gr.Markdown("### API Configuration")
        # Create inputs for each environment variable
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")

            # Determine visibility based on provider
            visible = provider_match is None or provider_match == current_provider

            # Create label with suffix
            label = var_config["label"] + get_label_suffix(var_name, var_config.get("default"))

            if var_config["type"] == "password":
                component = gr.Textbox(
                    label=label,
                    type="password",
                    value=get_setting(var_name, ""),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "checkbox":
                default_val = var_config.get("default", False)
                saved_val = get_setting(var_name, "")
                checkbox_val = saved_val.lower() in ("1", "true", "yes") if saved_val else default_val
                component = gr.Checkbox(
                    label=label,
                    value=checkbox_val,
                    visible=visible,
                    interactive=True,
                )
            elif var_config["type"] == "dropdown":
                # Mark the default choice
                choices = var_config.get("choices", [])
                default_val = var_config.get("default", "")
                if default_val and default_val in choices:
                    # Add [DEFAULT] marker to the default choice
                    marked_choices = [f"{choice} [DEFAULT]" if choice == default_val else choice for choice in choices]
                else:
                    marked_choices = choices

                current_value = get_setting(var_name, default_val)
                # Match the value with the choices - if it has [DEFAULT] in choices, use that
                default_choice = f"{default_val} [DEFAULT]"
                if current_value == default_val and default_choice in marked_choices:
                    display_value = default_choice
                else:
                    display_value = current_value

                component = gr.Dropdown(
                    label=label,
                    choices=marked_choices,
                    value=display_value,
                    visible=visible,
                    interactive=True,
                )
            else:  # text
                component = gr.Textbox(
                    label=label,
                    value=get_setting(var_name, var_config.get("default", "")),
                    placeholder=var_config.get("placeholder", ""),
                    visible=visible,
                    interactive=True,
                )

            components[var_name] = component

    # Save and status
    with gr.Row():
        save_btn = gr.Button("💾 Save Settings", variant="primary", scale=2)
        clear_btn = gr.Button("🔄 Clear Overrides", variant="secondary", scale=1)
        components["save_btn"] = save_btn
        components["clear_btn"] = clear_btn

    status = gr.Markdown("", visible=False)
    components["status"] = status

    # Set up event handlers
    def update_model_choices(provider: str):
        """Update model choices based on provider selection."""
        # Remove [DEFAULT] tag if present
        provider = provider.replace(" [DEFAULT]", "")

        models = config.model_configs.get(provider, [])

        # Add default markers for openai
        if provider == "openai":
            marked_models = [f"{m} [DEFAULT]" if m == "o4-mini" else m for m in models]
            default_value = (
                "o4-mini [DEFAULT]" if models and "o4-mini" in models else (marked_models[0] if marked_models else "")
            )
        else:
            marked_models = models
            default_value = models[0] if models else ""

        # Return individual updates instead of dictionary
        model_update = gr.update(choices=marked_models, value=default_value)
        azure_update = gr.update(visible=(provider == "azure"))

        # Provider-specific visibility updates
        provider_updates = []
        for var_name, var_config in config.env_vars.items():
            provider_match = var_config.get("provider")
            if provider_match is not None:
                visible = provider_match == provider
                provider_updates.append(gr.update(visible=visible))
            else:
                provider_updates.append(gr.update())

        return [model_update, azure_update] + provider_updates

    # Connect provider change to update function
    outputs = [components["model_name"], components["azure_deployment"]]
    outputs.extend([components[var_name] for var_name in config.env_vars.keys()])

    provider.change(
        fn=update_model_choices,
        inputs=[provider],
        outputs=outputs,
    )

    def save_settings(*args) -> str:
        """Save settings to environment and optionally call callback."""
        try:
            # Map positional arguments to kwargs based on the order we defined in save_inputs
            arg_names = ["provider", "model_name", "azure_deployment", "max_tokens"]
            arg_names.extend(config.env_vars.keys())

            kwargs = {}
            for i, value in enumerate(args):
                if i < len(arg_names):
                    # Clean [DEFAULT] tags from dropdown values
                    if isinstance(value, str) and "[DEFAULT]" in value:
                        value = value.replace(" [DEFAULT]", "")
                    kwargs[arg_names[i]] = value

            # Build model string
            provider = kwargs.get("provider", "openai")
            model_name = kwargs.get("model_name", "o4-mini")
            azure_deployment = kwargs.get("azure_deployment", "")

            if provider == "azure" and azure_deployment:
                model_str = f"{provider}/{model_name}/{azure_deployment}"
            else:
                model_str = f"{provider}/{model_name}"

            # Prepare settings dict for config file
            settings_to_save = {
                "MODEL": model_str,
            }

            # Add max_tokens if provided
            max_tokens_value = kwargs.get("max_tokens")
            if max_tokens_value is not None and max_tokens_value != "":
                try:
                    # Validate it's a number
                    int_value = int(max_tokens_value)
                    if 1 <= int_value <= 128000:
                        settings_to_save["MAX_TOKENS"] = str(int_value)
                except (ValueError, TypeError):
                    pass  # Ignore invalid values

            # Add all other settings
            for var_name in config.env_vars.keys():
                value = kwargs.get(var_name)
                if value is not None and value != "":
                    if isinstance(value, bool):
                        settings_to_save[var_name] = "true" if value else "false"
                    else:
                        settings_to_save[var_name] = str(value)

            # Save to config file
            save_config(settings_to_save)

            # Prepare callback data
            settings = {
                "model": model_str,
                "max_tokens": kwargs.get("max_tokens"),
            }
            settings.update({k: v for k, v in kwargs.items() if k in config.env_vars})

            # Call callback if provided
            if on_save:
                on_save(settings)

            return "✅ Settings saved! Your changes are active for new operations."

        except Exception as e:
            return f"❌ Error saving settings: {str(e)}"

    # Connect save button
    # Create a list of inputs with proper ordering for kwargs
    save_inputs = [
        components["provider"],
        components["model_name"],
        components["azure_deployment"],
        components["max_tokens"],
    ]
    # Add all environment variable inputs in the order they were created
    for var_name in config.env_vars.keys():
        if var_name in components:
            save_inputs.append(components[var_name])

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

    # Clear button handler
    def clear_overrides():
        """Clear all config overrides and return to env/defaults."""
        try:
            config_path = Path.home() / ".config" / "recipe-tool" / "settings.json"
            if config_path.exists():
                config_path.unlink()
            return "✅ All overrides cleared! Values reset to environment/defaults."
        except Exception as e:
            return f"❌ Error clearing overrides: {str(e)}"

    clear_btn.click(
        fn=clear_overrides,
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
        return os.getenv("OLLAMA_DEFAULT_MODEL", "ollama/llama3.1")
    else:
        # Final fallback to OpenAI
        return "openai/o4-mini"
