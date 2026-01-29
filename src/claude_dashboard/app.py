"""Main Claude Dashboard application with sidebar navigation."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from claude_dashboard.widgets import Sidebar
from claude_dashboard.screens.agents import AgentsScreen
from claude_dashboard.screens.skills import SkillsScreen
from claude_dashboard.screens.settings import SettingsScreen
from claude_dashboard.config.claude_config import ClaudeConfig, ConfigChanged


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

    def on_mount(self):
        """Start file watcher when app mounts."""
        config = ClaudeConfig()

        def on_config_change():
            self.post_message(ConfigChanged())

        self._observer = config.start_watching(on_config_change)

    def on_config_changed(self, event: ConfigChanged) -> None:
        """Refresh current screen when config changes."""
        content_area = self.query_one("#content_area", Vertical)
        # Re-mount current screen to refresh data
        children = content_area.children
        if children:
            current_screen = children[0]
            if hasattr(current_screen, 'on_mount'):
                # Call on_mount to refresh data
                current_screen.on_mount()

    def on_sidebar_highlighted(self, event: Sidebar.Highlighted) -> None:
        """Handle sidebar item highlight."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item == "Agents":
            content_area.mount(AgentsScreen())
        elif event.item == "Skills":
            content_area.mount(SkillsScreen())
        elif event.item == "Settings":
            content_area.mount(SettingsScreen())

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item == "Agents":
            content_area.mount(AgentsScreen())
        elif event.item == "Skills":
            content_area.mount(SkillsScreen())
        elif event.item == "Settings":
            content_area.mount(SettingsScreen())
