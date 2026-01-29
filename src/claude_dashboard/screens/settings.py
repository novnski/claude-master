"""Settings screen showing Claude configuration with masked secrets."""

import json
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Header
from claude_dashboard.config.claude_config import ClaudeConfig


class SettingsScreen(Vertical):
    """Screen showing Claude settings."""

    CSS = """
    SettingsScreen {
        height: 100%;
    }
    #settings_container {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    Static {
        background: $panel;
    }
    """

    def compose(self):
        yield Header()
        with Vertical(id="settings_container"):
            yield Static(id="settings_display")

    def on_mount(self):
        config = ClaudeConfig()
        settings = config.get_settings()

        display = self.query_one("#settings_display", Static)

        if not settings:
            display.update("[yellow]No settings file found at ~/.claude/settings.json[/yellow]")
            return

        # Format settings as JSON for display
        formatted = json.dumps(settings, indent=2)
        display.update(f"```json\n{formatted}\n```")
