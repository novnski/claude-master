"""EditorScreen for inline editing of agent and skill files."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal
from textual.widgets import Header, Footer, TextArea, Label
from textual import events
from pathlib import Path

from claude_dashboard.widgets.line_numbers import LineNumbers


class EditorScreen(Screen):
    """Full-screen editor for editing agent and skill files."""

    CSS = """
    EditorScreen {
        height: 100%;
    }
    #editor_header {
        padding: 0 1;
        background: $surface;
        height: 2;
    }
    #editor_container {
        height: 1fr;
    }
    TextArea {
        height: 1fr;
        border: none;
    }
    LineNumbers {
        height: 1fr;
    }
    """

    LANGUAGE_MAP = {
        ".md": "markdown",
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sh": "bash",
        ".txt": "plaintext",
    }

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = Path(file_path).expanduser()
        self.language = self._detect_language()
        self.original_content = self._read_file()

    def _detect_language(self) -> str:
        """Detect language from file extension."""
        suffix = self.file_path.suffix.lower()
        return self.LANGUAGE_MAP.get(suffix, "plaintext")

    def _read_file(self) -> str:
        """Read file content."""
        if self.file_path.exists():
            return self.file_path.read_text()
        return ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"Editing: {self.file_path}  [{self.language.upper()}]", id="editor_header")
        with Horizontal(id="editor_container"):
            yield LineNumbers(id="line_numbers")
            yield TextArea(self.original_content, id="editor", language=self.language)
        yield Footer()

    def on_mount(self):
        """Initialize line numbers after mount."""
        text_area = self.query_one("#editor", TextArea)
        line_numbers = self.query_one(LineNumbers)

        # Set initial line count
        line_count = text_area.text.count("\n") + 1
        line_numbers.set_line_count(line_count)

        # Watch for text changes to update line numbers
        self.watch_text_area(text_area)

    def watch_text_area(self, text_area: TextArea):
        """Set up watching for text changes."""
        # Use reactive on TextArea to watch changes
        text_area.text_changed = lambda: self._update_line_numbers()

    def _update_line_numbers(self):
        """Update line numbers based on current text."""
        text_area = self.query_one("#editor", TextArea)
        line_numbers = self.query_one(LineNumbers)

        line_count = text_area.text.count("\n") + 1
        line_numbers.set_line_count(line_count)

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "ctrl+s":
            self._save_file()
        elif event.key == "ctrl+q" or event.key == "escape":
            self.app.pop_screen()

    def _save_file(self):
        """Save current content to file."""
        text_area = self.query_one("#editor", TextArea)
        content = text_area.text

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        self.file_path.write_text(content)

        self.app.notify(f"Saved: {self.file_path.name}")
