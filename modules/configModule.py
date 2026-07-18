# modules/config.py
import json
from pathlib import Path

from modules.platformModules import config_dir

# config_dir should already point at wherever you resolved it —
# same Path object you're using elsewhere for the config directory.
CONFIG_FILE = Path(config_dir) / "config.json"

_DEFAULTS = {
    "appearance_mode": "System",
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge over defaults rather than trusting the file wholesale —
            # this way, if a future app version adds a new setting key,
            # an existing user's older config.json (which won't have that
            # key yet) still gets a sane default instead of a KeyError.
            return {**_DEFAULTS, **data}
        except (json.JSONDecodeError, OSError):
            pass  # corrupt/unreadable file — fall through to defaults
    return dict(_DEFAULTS)


def save_config(data: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"  ✗ Failed to save config: {e}")


def get_setting(key, default=None):
    return load_config().get(key, default)


def set_setting(key, value):
    data = load_config()
    data[key] = value
    save_config(data)
