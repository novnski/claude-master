"""Theme system for Claude Dashboard."""

from pathlib import Path
from typing import Dict
import json

THEMES_DIR = Path(__file__).parent
STATE_FILE = Path.home() / ".claude" / "dashboard-state.json"


def get_available_themes() -> Dict[str, str]:
    """Get mapping of theme names to CSS file paths."""
    themes = {}
    for css_file in THEMES_DIR.glob("*.css"):
        themes[css_file.stem] = str(css_file)
    return themes


def get_current_theme() -> str:
    """Get currently configured theme."""
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        return data.get("theme", "default")
    return "default"


def set_theme(theme_name: str) -> None:
    """Set current theme in state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"theme": theme_name}
    STATE_FILE.write_text(json.dumps(data, indent=2))
