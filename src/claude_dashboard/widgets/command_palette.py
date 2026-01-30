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
        ("Create New Skill", "create_skill"),
        ("Open Settings", "settings"),
        ("Show Keyboard Shortcuts", "shortcuts"),
        ("Import Skills from GitHub", "import_github"),
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

        # Focus input
        input_widget = self.query_one("#command_input", Input)
        input_widget.focus()

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
        # Get the cell at the cursor position
        cursor_row = table.cursor_row
        if cursor_row is not None:
            cell = table.get_cell_at(cursor_row, 0)
            command = str(cell)
            self.app.pop_screen()
            self._execute_command(command)

    def _execute_command(self, command: str):
        """Execute the selected command."""
        if command == "Switch Theme":
            self._show_theme_switcher()
        elif command == "Create New Agent":
            from claude_dashboard.widgets_modals.create_modal import CreateAgentWizard

            self.app.push_screen(CreateAgentWizard())
        elif command == "Create New Skill":
            from claude_dashboard.widgets_modals.create_skill_wizard import (
                CreateSkillWizard,
            )

            self.app.push_screen(CreateSkillWizard())
        elif command == "Open Settings":
            content_area = self.app.query_one("#content_area")
            for child in list(content_area.children):
                child.remove()
            content_area.remove_children()
            from claude_dashboard.screens.settings import SettingsScreen

            content_area.mount(SettingsScreen())
        elif command == "Show Keyboard Shortcuts":
            from claude_dashboard.screens.shortcuts_help import ShortcutsHelpScreen

            self.app.push_screen(ShortcutsHelpScreen())
        elif command == "Import Skills from GitHub":
            content_area = self.app.query_one("#content_area")
            for child in list(content_area.children):
                child.remove()
            content_area.remove_children()
            from claude_dashboard.screens.github_import import GitHubImportScreen

            content_area.mount(GitHubImportScreen())

    def _show_theme_switcher(self):
        """Show theme selection dialog with live switching."""
        themes = list(get_available_themes().keys())
        current = get_current_theme()
        current_idx = themes.index(current) if current in themes else 0
        next_idx = (current_idx + 1) % len(themes)
        new_theme = themes[next_idx]

        # Use the app's switch_theme method if available
        if hasattr(self.app, "switch_theme"):
            self.app.switch_theme(new_theme)
        else:
            # Fallback: set theme and notify
            set_theme(new_theme)
            self.app.notify(
                f"Theme changed to {new_theme.capitalize()} (restart to apply)"
            )
