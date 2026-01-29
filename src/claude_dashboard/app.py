"""Main Claude Dashboard application with sidebar navigation."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.messages import Message
from textual import events
from pathlib import Path
from claude_dashboard.sidebar import Sidebar
from claude_dashboard.themes import get_current_theme, get_available_themes, set_theme
from claude_dashboard.screens.agents import AgentsScreen
from claude_dashboard.screens.skills import SkillsScreen
from claude_dashboard.screens.settings import SettingsScreen
from claude_dashboard.screens.sessions import SessionsScreen
from claude_dashboard.screens.relationships import RelationshipsScreen
from claude_dashboard.screens.analytics import AnalyticsScreen
from claude_dashboard.screens.marketplace import MarketplaceScreen
from claude_dashboard.config.claude_config import ClaudeConfig, ConfigChanged
from claude_dashboard.utils.updater import check_for_update


class UpdateAvailable(Message):
    """Emitted when an update is available."""


class ClaudeDashboard(App):
    """Main Claude Dashboard application."""

    SCREENS = {
        "Agents": AgentsScreen,
        "Skills": SkillsScreen,
        "Settings": SettingsScreen,
        "Sessions": SessionsScreen,
        "Analytics": AnalyticsScreen,
        "Relationships": RelationshipsScreen,
        "Marketplace": MarketplaceScreen,
    }

    CSS = """
    Screen {
        background: $panel;
    }
    Sidebar {
        background: $surface;
    }
    """

    def _load_theme(self) -> None:
        """Load current theme and apply to app."""
        theme_name = get_current_theme()
        themes = get_available_themes()

        if theme_name in themes:
            css_path = Path(themes[theme_name])
            if css_path.exists():
                # Read CSS and apply
                css_content = css_path.read_text()
                # Combine with existing CSS
                self.CSS += f"\n\n/* Theme: {theme_name} */\n{css_content}"

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield Sidebar(
                "Agents",
                "Skills",
                "Settings",
                "Sessions",
                "Analytics",
                "Updates",
                "Relationships",
                "Marketplace",
            )
            with Vertical(id="content_area"):
                yield AgentsScreen()
        yield Footer()

    def on_mount(self):
        """Start file watcher, load theme, and check for updates when app mounts."""
        self._load_theme()

        config = ClaudeConfig()

        def on_config_change():
            self.post_message(ConfigChanged())

        self._observer = config.start_watching(on_config_change)

        # Check for updates
        update_status = check_for_update()
        if update_status:
            self.query_one(Footer).update(update_status)

    def on_unmount(self) -> None:
        """Clean up observer when app unmounts."""
        if hasattr(self, '_observer') and self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=5.0)

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

        if event.item in self.SCREENS:
            content_area.mount(self.SCREENS[event.item]())

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item in self.SCREENS:
            content_area.mount(self.SCREENS[event.item]())

    def on_key(self, event: events.Key) -> None:
        """Handle global keyboard shortcuts."""
        if event.key == "ctrl+p":
            from claude_dashboard.widgets.command_palette import CommandPalette
            self.push_screen(CommandPalette())
        elif event.key == "question":
            from claude_dashboard.screens.shortcuts_help import ShortcutsHelpScreen
            self.push_screen(ShortcutsHelpScreen())
        elif event.key in "12345678":
            # Number keys jump to sidebar items
            self._jump_to_sidebar_item(int(event.key))

    def _jump_to_sidebar_item(self, number: int) -> None:
        """Jump to sidebar item by number.

        Args:
            number: The number key pressed (1-8)
        """
        sidebar_items = [
            "Agents", "Skills", "Settings", "Sessions",
            "Analytics", "Updates", "Relationships", "Marketplace"
        ]

        if 0 <= number - 1 < len(sidebar_items):
            item = sidebar_items[number - 1]
            content_area = self.query_one("#content_area", Vertical)
            content_area.remove_children()

            if item in self.SCREENS:
                content_area.mount(self.SCREENS[item]())
