"""
Brahma Echo — Centralized Path Helper
Handles resource resolution for both development and PyInstaller frozen modes.

In development: resources are in the project root (next to main.py).
When frozen:   resources are in sys._MEIPASS (PyInstaller bundle).
Writable user data goes to %LOCALAPPDATA%/Brahma Echo/ (per-user, always writable).
"""

import sys
import os
from pathlib import Path


def is_frozen() -> bool:
    """True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def get_resource_dir() -> Path:
    """
    Directory containing bundled, read-only resources (assets, config templates, core, etc.)
    In dev: the project root (next to main.py).
    Frozen: sys._MEIPASS (PyInstaller's temp extraction dir).
    """
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_install_dir() -> Path:
    """
    Directory where the exe lives (for finding sibling files in onedir mode).
    In dev: same as resource dir.
    Frozen: the directory containing the exe.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_user_data_dir() -> Path:
    """
    Per-user writable data directory.
    Windows: %LOCALAPPDATA%/Brahma Echo/
    Falls back to install dir if LOCALAPPDATA is unavailable.
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        data_dir = Path(local_app_data) / "Brahma Echo"
    else:
        data_dir = get_install_dir() / "user_data"

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """
    Writable config directory. In frozen mode, uses per-user app data.
    In dev, uses the project's config/ directory.
    """
    if is_frozen():
        config_dir = get_user_data_dir() / "config"
    else:
        config_dir = get_resource_dir() / "config"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_resource_path(*parts) -> Path:
    """
    Resolve a bundled resource path (read-only).
    Example: get_resource_path("assets", "Brahma_Lite_Logo.png")
    """
    return get_resource_dir().joinpath(*parts)


def get_config_path(filename: str) -> Path:
    """Get the full path for a writable config file."""
    return get_config_dir() / filename


def ensure_config_from_template(filename: str, template: dict | None = None) -> Path:
    """
    If a config file doesn't exist in the writable config dir, create it from template.
    Returns the path to the config file.
    """
    target = get_config_path(filename)
    if not target.exists() and template is not None:
        import json
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2)
    return target


def get_memory_dir() -> Path:
    """Directory for memory/persistence files."""
    if is_frozen():
        return get_user_data_dir() / "memory"
    return get_resource_dir() / "memory"


def get_logs_dir() -> Path:
    """Directory for log files."""
    if is_frozen():
        logs = get_user_data_dir() / "logs"
    else:
        logs = get_resource_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def get_plugin_dir() -> Path:
    """Directory for user plugins."""
    if is_frozen():
        return get_user_data_dir() / "plugins"
    return get_resource_dir() / "plugins"


def get_log_file(name: str = "brahma_echo.log") -> Path:
    """Get a log file path."""
    return get_logs_dir() / name
