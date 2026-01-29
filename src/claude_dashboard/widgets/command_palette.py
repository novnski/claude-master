"""Command Palette widget for Claude Dashboard."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, DataTable
from textual.containers import Vertical
from claude_dashboard.themes import get_available_themes, get_current_theme, set_theme


class CommandPalette(ModalScreen):
    """Command palette for quick access to features."""

    CSS = """
    CommandPalette {
        background: $panel;
        border: thick $primary;
    }
    #command_input {
        margin: 1;
    }
    #commands_table {
        height: 1fr;
        margin: 0 1;
    }
    """

    COMMANDS = [
        ("Switch Theme", "theme"),
        ("Create New Agent", "create_agent"),
        ("Open Settings", "settings"),
        ("Show Keyboard Shortcuts", "shortcuts"),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type a command...", id="command_input")
        yield DataTable(id="commands_table")

    def on_mount(self):
        table = self.query_one("#commands_table", DataTable)
        table.add_columns("Command")

        for name, _ in self.COMMANDS:
            table.add_row(name)

        table.cursor_type = "row"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands based on input."""
        search = event.value.lower()
        table = self.query_one("#commands_table", DataTable)

        table.clear()
        table.add_columns("Command")
        for name, cmd_id in self.COMMANDS:
            if search in name.lower():
                table.add_row(name)

    def on_data_table_row_selected(self, event):
        """Execute selected command."""
        table = self.query_one("#commands_table", DataTable)
        cell = table.get_cell(event.row_key, "Command")
        command = str(cell)

        self.app.pop_screen()
        self._execute_command(command)

    def _execute_command(self, command: str):
        """Execute the selected command."""
        if command == "Switch Theme":
            self._show_theme_switcher()
        elif command == "Create New Agent":
            # Placeholder for now - CreateAgentModal will be available later
            self.app.notify("Create Agent feature coming soon!", severity="info")
        elif command == "Open Settings":
            content_area = self.app.query_one("#content_area")
            content_area.remove_children()
            from claude_dashboard.screens.settings import SettingsScreen
            content_area.mount(SettingsScreen())
        elif command == "Show Keyboard Shortcuts":
            from claude_dashboard.screens.shortcuts_help import ShortcutsHelpScreen
            self.app.push_screen(ShortcutsHelpScreen())

    def _show_theme_switcher(self):
        """Show theme selection dialog."""
        themes = list(get_available_themes().keys())
        # Simple implementation - cycle through themes
        current = get_current_theme()
        current_idx = themes.index(current) if current in themes else 0
        next_idx = (current_idx + 1) % len(themes)
        set_theme(themes[next_idx])
        self.app.notify(f"Theme changed to {themes[next_idx].capitalize()}")
        # Restart app to apply theme
        self.app.exit()
