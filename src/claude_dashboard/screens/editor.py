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
        """Read file content with proper encoding handling."""
        if not self.file_path.exists():
            return ""

        # Try multiple encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                return self.file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except (PermissionError, OSError) as e:
                self.app.notify(f"Error reading file: {e}", severity="error")
                return ""

        # If all encodings fail, try binary mode with replacement
        try:
            raw_bytes = self.file_path.read_bytes()
            return raw_bytes.decode("utf-8", errors="replace")
        except (PermissionError, OSError) as e:
            self.app.notify(f"Error reading file: {e}", severity="error")
            return ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            f"Editing: {self.file_path}  [{self.language.upper()}]", id="editor_header"
        )
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

    def on_text_area_changed(self) -> None:
        """Handle text area changes to update line numbers."""
        self._update_line_numbers()

    def _update_line_numbers(self):
        """Update line numbers based on current text."""
        text_area = self.query_one("#editor", TextArea)
        line_numbers = self.query_one(LineNumbers)

        line_count = text_area.text.count("\n") + 1
        line_numbers.set_line_count(line_count)

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "ctrl+s":
            event.stop()
            self._save_file()
        elif event.key == "ctrl+q" or event.key == "escape":
            event.stop()
            self.app.pop_screen()

    def _save_file(self):
        """Save current content to file with atomic write and backup."""
        text_area = self.query_one("#editor", TextArea)
        content = text_area.text

        # Validate file path
        if not self.file_path or not isinstance(self.file_path, Path):
            self.app.notify("Invalid file path", severity="error")
            return

        try:
            # Check if path is a directory
            if self.file_path.is_dir():
                self.app.notify("Cannot save to a directory", severity="error")
                return

            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if file exists
            if self.file_path.exists():
                backup_path = self.file_path.with_suffix(
                    self.file_path.suffix + ".backup"
                )
                backup_path.write_bytes(self.file_path.read_bytes())

            # Write to temporary file first (atomic write)
            temp_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
            temp_path.write_text(content, encoding="utf-8")

            # Replace original with temp
            temp_path.replace(self.file_path)

            self.app.notify(f"Saved: {self.file_path.name}")
        except PermissionError as e:
            self.app.notify(f"Permission denied: {e}", severity="error")
        except OSError as e:
            self.app.notify(f"Error saving file: {e}", severity="error")
        except Exception as e:
            self.app.notify(f"Unexpected error: {e}", severity="error")
