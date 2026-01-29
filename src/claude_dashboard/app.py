"""Main Claude Dashboard application with sidebar navigation."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from claude_dashboard.widgets import Sidebar


class ClaudeDashboard(App):
    """Main Claude Dashboard application."""

    CSS = """
    Screen {
        background: $panel;
    }
    Sidebar {
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield Sidebar(
                "Agents",
                "Skills",
                "Settings",
                "Sessions",
                "Updates",
            )
            with Vertical(id="content_area"):
                yield Static("Welcome to Claude Dashboard", id="main_content")
        yield Footer()

    def on_sidebar_highlighted(self, event: Sidebar.Highlighted) -> None:
        """Handle sidebar item highlight."""
        self.query_one("#main_content", Static).update(
            f"Selected: {event.item}"
        )

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        self.query_one("#main_content", Static).update(
            f"Opened: {event.item}"
        )
