"""Custom header widget that avoids Textual's Header race condition."""

from textual.app import ComposeResult
from textual.widgets import Label
from textual.widget import Widget


class CustomHeader(Widget):
    """Simple header widget that displays title and subtitle.

    This widget avoids the race condition in Textual's built-in Header widget
    where query_one() is called in _on_mount() before children are composed.
    """

    DEFAULT_CSS = """
    CustomHeader {
        height: 1;
        dock: top;
        background: $panel;
        padding: 0 1;
    }
    CustomHeader > Label {
        width: 100%;
        text-align: center;
        content-align: center middle;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._label: Label | None = None

    def compose(self) -> ComposeResult:
        yield Label("")

    def on_mount(self) -> None:
        """Get reference to label."""
        self._label = self.query_one(Label)

    def set_title(self, title: str, subtitle: str = "") -> None:
        """Set the header title."""
        if subtitle:
            text = f"{title} — {subtitle}"
        else:
            text = title
        if self._label:
            self._label.update(text)
