"""Sessions screen showing active/recent sessions."""

from textual.containers import Vertical
from textual.widgets import DataTable


class SessionsScreen(Vertical):
    """Screen showing active/recent sessions."""

    CSS = """
    SessionsScreen {
        height: 100%;
    }
    DataTable {
        height: 1fr;
    }
    """

    def compose(self):
        yield DataTable()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Project", "Last Active", "Messages")

        # Placeholder - actual implementation depends on session storage
        table.add_row("claude-master-dashboard", "Just now", "42")
