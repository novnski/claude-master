"""Create Agent Modal for creating new agents."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical
from pathlib import Path
import re


class CreateAgentModal(ModalScreen):
    """Modal for creating new agent."""

    CSS = """
    CreateAgentModal {
        background: $panel;
        border: thick $primary;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Create New Agent")
        yield Input(placeholder="Agent ID", id="agent_id")
        yield Input(placeholder="Name", id="agent_name")
        yield Button("Create", variant="primary", id="create")
        yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "create":
            agent_id = self.query_one("#agent_id", Input).value
            name = self.query_one("#agent_name", Input).value

            # Validate required fields
            if not agent_id or not name:
                self.app.notify("Agent ID and Name are required", severity="error")
                return

            # Validate agent_id is safe (alphanumeric, hyphens, underscores only)
            if not re.match(r'^[a-zA-Z0-9_-]+$', agent_id):
                self.app.notify(
                    "Agent ID must contain only letters, numbers, hyphens, and underscores",
                    severity="error"
                )
                return

            claude_dir = Path.home() / ".claude" / "agents"
            agent_file = claude_dir / f"{agent_id}.md"

            # Check for duplicate
            if agent_file.exists():
                self.app.notify(f"Agent '{agent_id}' already exists", severity="error")
                return

            content = f"""---
name: {name}
description: New agent
---
Agent description here."""

            # Write with error handling
            try:
                agent_file.write_text(content)
                self.app.pop_screen()
                self.app.notify(f"Agent '{agent_id}' created successfully")
            except OSError as e:
                self.app.notify(f"Failed to create agent: {e}", severity="error")
