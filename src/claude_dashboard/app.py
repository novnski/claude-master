"""Main Claude Dashboard application with sidebar navigation."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.messages import Message
from claude_dashboard.widgets import Sidebar
from claude_dashboard.screens.agents import AgentsScreen
from claude_dashboard.screens.skills import SkillsScreen
from claude_dashboard.screens.settings import SettingsScreen
from claude_dashboard.screens.sessions import SessionsScreen
from claude_dashboard.screens.relationships import RelationshipsScreen
from claude_dashboard.config.claude_config import ClaudeConfig, ConfigChanged
from claude_dashboard.utils.updater import check_for_update


class UpdateAvailable(Message):
    """Emitted when an update is available."""


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
                "Relationships",
            )
            with Vertical(id="content_area"):
                yield AgentsScreen()
        yield Footer()

    def on_mount(self):
        """Start file watcher and check for updates when app mounts."""
        config = ClaudeConfig()

        def on_config_change():
            self.post_message(ConfigChanged())

        self._observer = config.start_watching(on_config_change)

        # Check for updates
        update_status = check_for_update()
        if update_status:
            self.query_one(Footer).update(update_status)

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

        screens = {
            "Agents": AgentsScreen,
            "Skills": SkillsScreen,
            "Settings": SettingsScreen,
            "Sessions": SessionsScreen,
            "Relationships": RelationshipsScreen,
        }

        if event.item in screens:
            content_area.mount(screens[event.item]())

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        screens = {
            "Agents": AgentsScreen,
            "Skills": SkillsScreen,
            "Settings": SettingsScreen,
            "Sessions": SessionsScreen,
            "Relationships": RelationshipsScreen,
        }

        if event.item in screens:
            content_area.mount(screens[event.item]())
