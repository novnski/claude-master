"""Settings screen showing Claude configuration with masked secrets."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Header, Button, Label
from textual.screen import Screen
from claude_dashboard.config.claude_config import ClaudeConfig
from pathlib import Path


class SettingsScreen(Vertical):
    """Settings screen with masked secrets and raw editor access."""

    CSS = """
    SettingsScreen {
        height: 100%;
    }
    #settings_container {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    .section {
        padding: 1;
        margin-bottom: 1;
        border: solid $panel;
    }
    .masked {
        color: $warning;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="settings_container"):
            # Core Configuration
            yield Static("[b]# CORE CONFIGURATION[/b]", classes="section")
            yield Static("Your Claude Code settings are stored in:")
            yield Static("~/.claude/settings.json")

            # API Keys (Masked)
            yield Static("\n[b]# API KEYS (Masked)[/b]", classes="section")
            yield Static("Anthropic API Key:", classes="masked-label")
            yield Static("********************", id="anthropic_key", classes="masked")
            yield Button("Edit", id="edit_anthropic", variant="default")

            yield Static("")
            yield Static("Brave Search Key:", classes="masked-label")
            yield Static("•••••••••", id="brave_key", classes="masked")
            yield Button("Edit", id="edit_brave", variant="default")

            # Source File Link
            yield Static("\n[b]# SOURCE FILE[/b]", classes="section")
            yield Static("Location: ~/.claude/claude.md")
            yield Static("")
            yield Button("OPEN RAW CLAUDE.MD EDITOR", id="open_raw_editor", variant="primary")

    def on_mount(self):
        """Load and mask settings."""
        config = ClaudeConfig()
        settings = config.get_settings()

        if not settings:
            self.query_one("#settings_container", Vertical).mount(
                Static("[yellow]No settings file found at ~/.claude/settings.json[/yellow]")
            )
            return

        # Mask and display sensitive values
        for key, value in settings.items():
            if self._is_sensitive(key):
                masked = "•" * min(len(str(value)), 16)
                if "anthropic" in key.lower():
                    self.query_one("#anthropic_key", Static).update(masked)
                elif "brave" in key.lower():
                    self.query_one("#brave_key", Static).update(masked)

    def _is_sensitive(self, key: str) -> bool:
        """Check if a key contains sensitive information."""
        sensitive_keywords = ["key", "token", "secret", "password", "api"]
        return any(keyword in key.lower() for keyword in sensitive_keywords)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "open_raw_editor":
            self._open_raw_editor()
        elif event.button.id == "edit_anthropic":
            self.app.notify(
                "To edit API keys, edit ~/.claude/settings.json directly\n"
                "or use the Raw Editor to modify claude.md"
            )
        elif event.button.id == "edit_brave":
            self.app.notify(
                "To edit API keys, edit ~/.claude/settings.json directly\n"
                "or use the Raw Editor to modify claude.md"
            )

    def _open_raw_editor(self):
        """Open inline editor for claude.md."""
        from claude_dashboard.screens.editor import EditorScreen

        claude_md_path = Path.home() / ".claude" / "claude.md"
        self.app.push_screen(EditorScreen(str(claude_md_path)))
