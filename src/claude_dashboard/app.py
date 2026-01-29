"""Main Claude Dashboard application with sidebar navigation."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from claude_dashboard.widgets import Sidebar
from claude_dashboard.screens.agents import AgentsScreen


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
                yield AgentsScreen()
        yield Footer()

    def on_sidebar_highlighted(self, event: Sidebar.Highlighted) -> None:
        """Handle sidebar item highlight."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item == "Agents":
            content_area.mount(AgentsScreen())

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item == "Agents":
            content_area.mount(AgentsScreen())
