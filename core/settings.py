import json
import os

USER_DATA_DIR = "user_data"
SETTINGS_PATH = os.path.join(USER_DATA_DIR, "settings.json")
THEMES_DIR = os.path.join(USER_DATA_DIR, "themes")

default_settings = {
    "autosave": True,
    "font_size": 12,
    "theme": "dark"  # default theme name (must have dark.qss in themes/)
}

def ensure_user_data_dirs():
    """Ensure user_data and themes folders exist."""
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)

def load_settings():
    ensure_user_data_dirs()
    if not os.path.exists(SETTINGS_PATH):
        save_settings(default_settings)
    try:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        # fallback to default if file corrupted
        return default_settings.copy()

def save_settings(settings):
    ensure_user_data_dirs()
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

def list_themes():
    """Return list of theme names (without .qss extension) in themes directory"""
    ensure_user_data_dirs()
    return [f[:-4] for f in os.listdir(THEMES_DIR) if f.endswith(".qss")]

def load_theme(name):
    """Load .qss theme stylesheet text by theme name"""
    ensure_user_data_dirs()
    path = os.path.join(THEMES_DIR, f"{name}.qss")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
