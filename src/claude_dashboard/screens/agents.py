"""Agents screen showing list of agents from ~/.claude/agents/."""

from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import DataTable, Button, Label
from claude_dashboard.utils.editor import open_editor
from claude_dashboard.config.claude_config import ClaudeConfig


class AgentDetailScreen(ModalScreen):
    """Modal showing agent details."""

    CSS = """
    AgentDetailScreen {
        background: $panel;
        border: thick $primary;
    }
    """

    def __init__(self, agent_data: dict):
        super().__init__()
        self.agent_data = agent_data

    def compose(self):
        yield Label(f"[b]{self.agent_data.get('name', self.agent_data['id'])}[/b]")
        yield Label(f"ID: {self.agent_data['id']}")
        yield Label(f"Model: {self.agent_data.get('model', 'N/A')}")
        yield Label(f"\n{self.agent_data.get('description', 'No description')}")
        yield Label(f"\n[b]Content:[/b]\n{self.agent_data.get('content', '')[:500]}")
        yield Button("Edit (External)", variant="primary")
        yield Button("Close", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()
        else:
            # Edit button - validate path first
            if "path" not in self.agent_data:
                self.app.notify("No file path available for this agent", severity="error")
                return
            self.app.pop_screen()
            self.app.exit()  # Exit TUI temporarily
            open_editor(self.agent_data["path"])


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
        yield Button("Create New Agent", id="create_agent")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Description", "Model")

        # Load agents from config
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
        table = self.query_one(DataTable)
        row_key = event.row_key
        cell = table.get_cell(row_key, "ID")
        agent_id = str(cell)

        config = ClaudeConfig()
        agents = config.get_agents()
        agent = next((a for a in agents if a["id"] == agent_id), None)

        if agent:
            self.app.push_screen(AgentDetailScreen(agent))

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button press for create agent."""
        if event.button.id == "create_agent":
            from claude_dashboard.widgets_modals.create_modal import CreateAgentModal
            self.app.push_screen(CreateAgentModal())
