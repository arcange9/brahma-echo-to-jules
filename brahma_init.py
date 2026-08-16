"""
Brahma Echo — First-Run Initialization
Ensures user-writable config files exist before the app starts.
Copies templates from the bundle to the user data directory on first run.
"""

import json
import os
import shutil
from pathlib import Path

from brahma_paths import (
    get_resource_dir,
    get_config_dir,
    get_user_data_dir,
    get_memory_dir,
    get_plugin_dir,
    ensure_config_from_template,
)


# Config files that should be writable and user-specific
WRITABLE_CONFIGS = {
    "api_keys.json": {
        "gemini_api_key": "",
        "openrouter_api_key": "",
        "openrouter_model": "anthropic/claude-3.5-sonnet",
        "os_system": "windows",
    },
    "app_settings.json": {
        "wake_word": "brahma echo",
        "voice_enabled": True,
        "auto_start": False,
        "minimize_to_tray": True,
        "theme": "dark",
        "language": "en",
    },
    "discord_bot.json": {
        "enabled": False,
        "token": "",
        "prefix": "!",
    },
}


def initialize_user_data():
    """
    Create user-writable config files from templates on first run.
    Safe to call on every startup — only creates files that don't exist.
    """
    config_dir = get_config_dir()
    memory_dir = get_memory_dir()
    plugin_dir = get_plugin_dir()

    # Ensure directories exist
    config_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # Create config files from templates
    for filename, template in WRITABLE_CONFIGS.items():
        target = config_dir / filename
        if not target.exists():
            # Check if there's a template in the bundle
            template_path = get_resource_dir() / "config" / "templates" / filename
            if template_path.exists():
                shutil.copy2(template_path, target)
            else:
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(template, f, indent=2)

    # Copy brahma_connect.json if it doesn't exist (it has sensible defaults)
    bc_source = get_resource_dir() / "config" / "brahma_connect.json"
    bc_target = config_dir / "brahma_connect.json"
    if not bc_target.exists() and bc_source.exists():
        shutil.copy2(bc_source, bc_target)

    # Create a marker file so we know initialization happened
    marker = get_user_data_dir() / ".initialized"
    if not marker.exists():
        marker.write_text("Brahma Echo initialized\n", encoding="utf-8")

    return config_dir


def get_api_key_path() -> Path:
    """Path to the user's API keys config file."""
    return get_config_dir() / "api_keys.json"


def get_app_settings_path() -> Path:
    """Path to the app settings config file."""
    return get_config_dir() / "app_settings.json"


def load_api_keys() -> dict:
    """Load API keys, creating from template if needed."""
    path = get_api_key_path()
    if not path.exists():
        initialize_user_data()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"gemini_api_key": "", "openrouter_api_key": "", "os_system": "windows"}


def is_api_key_configured() -> bool:
    """Check if at least the Gemini API key is set."""
    keys = load_api_keys()
    return bool(keys.get("gemini_api_key", "").strip())
