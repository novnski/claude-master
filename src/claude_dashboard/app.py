"""Main Claude Dashboard application with sidebar navigation."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Label
from textual.message import Message
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
from claude_dashboard.screens.github_import import GitHubImportScreen
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
        "Import from GitHub": GitHubImportScreen,
    }

    BINDINGS = [
        ("ctrl+p", "command_palette", "Command Palette"),
        ("ctrl+q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("1", "jump(1)", "Agents"),
        ("2", "jump(2)", "Skills"),
        ("3", "jump(3)", "Settings"),
        ("4", "jump(4)", "Sessions"),
        ("5", "jump(5)", "Analytics"),
        ("6", "jump(6)", "Relationships"),
        ("7", "jump(7)", "Import"),
    ]

    CSS = """
    Screen {
        background: $panel;
    }
    Sidebar {
        background: $surface;
        width: 30;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._theme_css = ""
        self._current_theme = None
        self._observer = None
        self._config = None
        # Track current screen for proper cleanup
        self._current_screen = None

    def _load_theme(self) -> None:
        """Load current theme CSS file path for Textual to load."""
        theme_name = get_current_theme()
        themes = get_available_themes()

        if theme_name in themes:
            css_path = Path(themes[theme_name])
            if css_path.exists():
                self._theme_css = css_path.read_text()
                self._current_theme = theme_name

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
                "Relationships",
                "Import from GitHub",
            )
            with Vertical(id="content_area"):
                yield AgentsScreen()
        yield Footer()

    def on_mount(self):
        """Start file watcher, load theme, and check for updates when app mounts."""
        self._load_theme()

        # Initialize config singleton
        self._config = ClaudeConfig()

        def on_config_change():
            # Invalidate cache when files change
            if self._config:
                self._config.invalidate_cache()
            self.post_message(ConfigChanged())

        # Only start watching if not already watching
        if not self._observer:
            self._observer = self._config.start_watching(on_config_change)

        # Check for updates
        update_status = check_for_update()
        if update_status:
            footer = self.query_one(Footer)
            # Update footer with custom message
            footer.remove_children()
            footer.mount(Label(update_status))

    def on_unmount(self) -> None:
        """Clean up observer when app unmounts."""
        if self._observer:
            try:
                if self._observer.is_alive():
                    self._observer.stop()
                    self._observer.join(timeout=5.0)
                    if self._observer.is_alive():
                        self.notify(
                            "Warning: File watcher did not stop cleanly",
                            severity="warning",
                        )
            except Exception:
                pass
            finally:
                self._observer = None

    async def on_config_changed(self, event: ConfigChanged) -> None:
        """Refresh current screen when config changes."""
        content_area = self.query_one("#content_area", Vertical)
        children = list(content_area.children)
        if children:
            current_screen = children[0]
            # Try to refresh the screen
            try:
                if hasattr(current_screen, "on_mount"):
                    result = current_screen.on_mount()
                    if asyncio.iscoroutine(result):
                        await result
            except Exception:
                pass

    def _cleanup_current_screen(self) -> None:
        """Properly cleanup current screen to prevent memory leaks."""
        if self._current_screen:
            # Call cleanup if available
            cleanup_method = getattr(self._current_screen, "cleanup", None)
            if callable(cleanup_method):
                try:
                    cleanup_method()
                except Exception:
                    pass
            self._current_screen = None

    def on_sidebar_highlighted(self, event: Sidebar.Highlighted) -> None:
        """Handle sidebar item highlight."""
        content_area = self.query_one("#content_area", Vertical)

        # Properly cleanup current screen
        self._cleanup_current_screen()

        # Remove all children
        for child in list(content_area.children):
            child.remove()
        content_area.remove_children()

        if event.item in self.SCREENS:
            self._current_screen = self.SCREENS[event.item]()
            content_area.mount(self._current_screen)

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)

        # Properly cleanup current screen
        self._cleanup_current_screen()

        # Remove all children
        for child in list(content_area.children):
            child.remove()
        content_area.remove_children()

        if event.item in self.SCREENS:
            self._current_screen = self.SCREENS[event.item]()
            content_area.mount(self._current_screen)

    def action_command_palette(self) -> None:
        """Show command palette."""
        from claude_dashboard.widgets.command_palette import CommandPalette

        self.push_screen(CommandPalette())

    def action_help(self) -> None:
        """Show keyboard shortcuts help."""
        from claude_dashboard.screens.shortcuts_help import ShortcutsHelpScreen

        self.push_screen(ShortcutsHelpScreen())

    def action_jump(self, number: int) -> None:
        """Jump to sidebar item by number."""
        sidebar_items = [
            "Agents",
            "Skills",
            "Settings",
            "Sessions",
            "Analytics",
            "Relationships",
            "Import from GitHub",
        ]

        if 0 <= number - 1 < len(sidebar_items):
            item = sidebar_items[number - 1]
            content_area = self.query_one("#content_area", Vertical)

            # Properly cleanup current screen
            self._cleanup_current_screen()

            # Remove all children
            for child in list(content_area.children):
                child.remove()
            content_area.remove_children()

            if item in self.SCREENS:
                self._current_screen = self.SCREENS[item]()
                content_area.mount(self._current_screen)

    def on_key(self, event: events.Key) -> None:
        """Handle global keyboard shortcuts."""
        if event.key == "ctrl+p":
            event.stop()
            self.action_command_palette()
        elif event.key == "question":
            event.stop()
            self.action_help()
        elif event.key in "1234567":
            # Number keys jump to sidebar items
            event.stop()
            self.action_jump(int(event.key))

    def switch_theme(self, theme_name: str) -> None:
        """Switch theme - requires restart to apply."""
        set_theme(theme_name)
        self.notify(f"Theme changed to {theme_name.capitalize()} (restart to apply)")
