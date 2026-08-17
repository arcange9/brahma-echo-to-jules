import json, os, sys
from pathlib import Path

def _get_config_path() -> Path:
    """Resolve config path for both frozen and dev modes."""
    if getattr(sys, "frozen", False):
        # In frozen mode, use per-user writable config dir
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            config_dir = Path(local_app_data) / "Brahma Echo" / "config"
        else:
            config_dir = Path(sys.executable).parent / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "api_keys.json"
    return Path(__file__).parent / "api_keys.json"

_CONFIG_PATH = _get_config_path()

def get_config() -> dict:
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # First run — try to copy from template
        try:
            _template = None
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                _template = Path(sys._MEIPASS) / "config" / "templates" / "api_keys.json"
            else:
                _template = Path(__file__).parent / "templates" / "api_keys.json"
            if _template and _template.exists():
                import shutil
                _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(_template, _CONFIG_PATH)
                with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"gemini_api_key": "", "openrouter_api_key": "", "os_system": "windows"}
    except Exception:
        return {"gemini_api_key": "", "openrouter_api_key": "", "os_system": "windows"}

def get_os() -> str:
    """Returns: 'windows' | 'mac' | 'linux'"""
    return get_config().get("os_system", "windows").lower()

def is_windows() -> bool: return get_os() == "windows"
def is_mac()     -> bool: return get_os() == "mac"
def is_linux()   -> bool: return get_os() == "linux"
