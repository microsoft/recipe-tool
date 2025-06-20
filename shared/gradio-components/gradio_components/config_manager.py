"""Simple config file management for Recipe Tool settings."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = Path.home() / ".config" / "recipe-tool"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def load_settings() -> Dict[str, Any]:
    """Load settings from config file.
    
    Returns:
        Dict containing settings, empty dict if file doesn't exist
    """
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, return empty dict
            return {}
    
    return {}


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to config file as overrides only.
    
    Only saves values that differ from environment variables or defaults.
    Removes values that match env vars or are empty.
    
    Args:
        settings: Dictionary of settings to save
    """
    config_path = get_config_path()
    
    # Start with existing settings
    existing = load_settings()
    
    # Process each setting
    for key, value in settings.items():
        env_value = os.getenv(key)
        
        # Remove empty values or values that match environment
        if value is None or value == "" or (env_value and str(value) == str(env_value)):
            existing.pop(key, None)
        else:
            # Only save if it's different from environment
            existing[key] = value
    
    # Save the updated settings
    if existing:
        with open(config_path, "w") as f:
            json.dump(existing, f, indent=2)
    elif config_path.exists():
        # Remove empty config file
        config_path.unlink()


def get_setting(key: str, default: Optional[Any] = None) -> Any:
    """Get a specific setting value.
    
    Args:
        key: Setting key to retrieve
        default: Default value if key doesn't exist
        
    Returns:
        Setting value or default
    """
    # First check environment variable (allows override)
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    # Then check config file
    settings = load_settings()
    return settings.get(key, default)


def get_env_or_default(key: str, default: Optional[Any] = None) -> Any:
    """Get value from environment only (not config).
    
    Args:
        key: Setting key to retrieve
        default: Default value if not in environment
        
    Returns:
        Environment value or default
    """
    return os.getenv(key, default)


def is_override(key: str) -> bool:
    """Check if a setting is overridden in config file.
    
    Args:
        key: Setting key to check
        
    Returns:
        True if value is from config file, False if from env/default
    """
    settings = load_settings()
    return key in settings


def get_model_string() -> str:
    """Get the current model string from config or environment."""
    # Check for explicit model setting first
    model = get_setting("MODEL")
    if model:
        return model
    
    # Otherwise, try to construct from available info
    # This maintains backward compatibility
    if get_setting("OPENAI_API_KEY"):
        return "openai/o4-mini"
    elif get_setting("AZURE_OPENAI_BASE_URL"):
        deployment = get_setting("AZURE_OPENAI_DEPLOYMENT_NAME", "o4-mini")
        return f"azure/o4-mini/{deployment}"
    elif get_setting("ANTHROPIC_API_KEY"):
        return "anthropic/claude-3-5-sonnet"
    elif get_setting("OLLAMA_BASE_URL", "http://localhost:11434"):
        return get_setting("OLLAMA_DEFAULT_MODEL", "ollama/llama3.1")
    else:
        # Final fallback to OpenAI
        return "openai/o4-mini"