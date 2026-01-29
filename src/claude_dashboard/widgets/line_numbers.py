"""LineNumbers widget for Claude Dashboard editor."""

from textual.widgets import Static
from textual.reactive import reactive


class LineNumbers(Static):
    """Displays line numbers for the editor."""

    DEFAULT_CSS = """
    LineNumbers {
        width: 5;
        text-align: right;
        padding-right: 1;
        color: $text-dim;
        background: $surface;
    }
    """

    line_count = reactive(0)

    def watch_line_count(self, old_count: int, new_count: int) -> None:
        """Update display when line count changes."""
        lines = "\n".join(str(i) for i in range(1, new_count + 1))
        self.update(lines)

    def set_line_count(self, count: int) -> None:
        """Set the number of lines to display."""
        self.line_count = count
