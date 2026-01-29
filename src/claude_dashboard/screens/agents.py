"""Agents screen showing list of agents from ~/.claude/agents/."""

from textual.containers import Vertical
from textual.widgets import DataTable


class AgentsScreen(Vertical):
    """Screen showing list of agents."""

    CSS = """
    AgentsScreen {
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
        table.add_columns("ID", "Name", "Description", "Model")

        # Load agents from config
        from claude_dashboard.config.claude_config import ClaudeConfig
        config = ClaudeConfig()
        agents = config.get_agents()

        for agent in agents:
            table.add_row(
                agent["id"],
                agent.get("name", agent["id"]),
                agent.get("description", "")[:50],
                agent.get("model", "")
            )

    def on_data_table_row_selected(self, event):
        """Handle row selection."""
        # Show detail view (TODO in next task)
        pass
