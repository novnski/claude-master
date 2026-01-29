"""ShortcutsHelpScreen for displaying keyboard shortcuts."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Label, Button


class ShortcutsHelpScreen(ModalScreen):
    """Display all keyboard shortcuts."""

    CSS = """
    ShortcutsHelpScreen {
        background: $panel;
        border: thick $primary;
    }
    #help_container {
        padding: 2;
        min-width: 50;
    }
    """

    SHORTCUTS = {
        "Navigation": [
            ("?", "Show this help"),
            ("Ctrl+P", "Open command palette"),
            ("1-7", "Jump to sidebar item"),
            ("Tab", "Next item"),
            ("Shift+Tab", "Previous item"),
        ],
        "Actions": [
            ("N", "Create new agent (on Agents screen)"),
            ("E", "Edit selected"),
            ("Ctrl+S", "Save (in editor)"),
            ("Ctrl+Q", "Cancel/Quit"),
            ("Esc", "Go back / Close modal"),
        ],
        "Editor": [
            ("Ctrl+S", "Save file"),
            ("Ctrl+Q", "Close editor"),
            ("↑/↓", "Navigate lines"),
            ("Page Up/Down", "Scroll page"),
        ],
    }

    def compose(self) -> ComposeResult:
        with Vertical(id="help_container"):
            yield Label("[b]KEYBOARD SHORTCUTS[/b]\n")

            for category, shortcuts in self.SHORTCUTS.items():
                yield Label(f"[b]{category}:[/b]")
                for key, desc in shortcuts:
                    yield Label(f"  {key:20} - {desc}")
                yield Label("")

            yield Button("CLOSE", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()
