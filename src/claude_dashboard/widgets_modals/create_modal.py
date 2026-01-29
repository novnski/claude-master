"""Create Agent Wizard for creating new agents."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, Button, Select, RadioButton, RadioSet
from pathlib import Path
import random

from claude_dashboard.config.claude_config import ConfigChanged


class CreateAgentWizard(ModalScreen):
    """3-step wizard for creating new agents."""

    CSS = """
    CreateAgentWizard {
        background: $panel;
        border: thick $primary;
    }
    #wizard_container {
        padding: 2;
        min-width: 60;
    }
    .step {
        margin-bottom: 1;
    }
    RadioSet {
        margin: 1 0;
    }
    """

    TEMPLATES = [
        ("Empty Agent", "empty"),
        ("Coder", "coder"),
        ("Analyst", "analyst"),
        ("Debugger", "debugger"),
    ]

    MODELS = [
        ("Claude 3 Opus", "claude-3-opus"),
        ("Claude 3.5 Sonnet", "claude-3-5-sonnet"),
        ("Claude 3 Haiku", "claude-3-haiku"),
    ]

    def __init__(self):
        super().__init__()
        self.step = 1
        self.generated_id = f"ag_{random.randint(1000, 9999)}"  # Generate once
        self.data = {
            "name": "",
            "id": "",
            "model": "claude-3-5-sonnet",
            "template": "empty"
        }

    def compose(self) -> ComposeResult:
        with Vertical(id="wizard_container"):
            yield Label(f"[b]CREATE NEW AGENT[/b]\n")
            yield Label(f"Step {self.step}/3: BASIC INFO", id="step_title")

            # Step 1: Basic Info
            with Vertical(id="step1", classes="step"):
                yield Label("Name:")
                yield Input(placeholder="Agent name", id="agent_name")
                yield Label("")
                yield Label(f"ID: (Auto-generated: {self.generated_id})")

            # Step 2: Model Selection (hidden initially)
            with Vertical(id="step2", classes="step", display="none"):
                yield Label("Model Selection:")
                with RadioSet(id="model_select"):
                    yield RadioButton("Claude 3 Opus", value="claude-3-opus")
                    yield RadioButton("Claude 3.5 Sonnet", value="claude-3-5-sonnet", checked=True)
                    yield RadioButton("Claude 3 Haiku", value="claude-3-haiku")

            # Step 3: Template (hidden initially)
            with Vertical(id="step3", classes="step", display="none"):
                yield Label("Template:")
                yield Select(
                    options=self.TEMPLATES,
                    value="empty",
                    id="template_select"
                )

            yield Label("")  # spacer
            with Horizontal():
                yield Button("BACK", id="back", disabled=(self.step == 1))
                yield Button("NEXT", variant="primary", id="next")
                yield Button("CANCEL", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "next":
            self._next_step()
        elif event.button.id == "back":
            self._prev_step()

    def _next_step(self):
        """Move to next step, validating current step."""
        if self.step == 1:
            name_input = self.query_one("#agent_name", Input)
            if not name_input.value.strip():
                self.app.notify("Please enter an agent name", severity="error")
                return
            self.data["name"] = name_input.value.strip()
            self.data["id"] = self.generated_id

        elif self.step == 2:
            model_set = self.query_one("#model_select", RadioSet)
            selected_button = model_set.pressed_button
            if selected_button:
                self.data["model"] = selected_button.value
            else:
                self.data["model"] = "claude-3-5-sonnet"

        elif self.step == 3:
            template_select = self.query_one("#template_select", Select)
            self.data["template"] = template_select.value
            self._create_agent()
            return

        # Move to next step
        self.step += 1
        self._update_step_display()

    def _prev_step(self):
        """Move to previous step."""
        if self.step > 1:
            self.step -= 1
            self._update_step_display()

    def _update_step_display(self):
        """Show/hide steps based on current step."""
        # Update step title
        step_titles = {
            1: "BASIC INFO",
            2: "MODEL SELECTION",
            3: "TEMPLATE"
        }
        self.query_one("#step_title", Label).update(
            f"Step {self.step}/3: {step_titles[self.step]}"
        )

        # Show/hide step containers
        for i in range(1, 4):
            step_container = self.query_one(f"#step{i}", Vertical)
            step_container.display = (i == self.step)

        # Update button states
        self.query_one("#back", Button).disabled = (self.step == 1)
        self.query_one("#next", Button).label = "CREATE" if self.step == 3 else "NEXT"

    def _create_agent(self):
        """Create the agent file."""
        agents_dir = Path.home() / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        file_path = agents_dir / f"{self.data['id']}.md"

        # Generate agent file content
        frontmatter = f"""---
name: {self.data['name']}
model: {self.data['model']}
description: >
  {self.data['name']} - {self.data['template']} agent
---

You are {self.data['name']}, a Claude AI assistant configured as a {self.data['template']} agent.
"""

        # Use x mode (exclusive creation) - fails if file exists
        try:
            with open(file_path, 'x') as f:
                f.write(frontmatter)
            self.app.notify(f"Created agent: {self.data['name']} ({self.data['id']})")
            self.app.pop_screen()

            # Trigger refresh
            self.app.post_message(ConfigChanged())
        except FileExistsError:
            self.app.notify(f"Agent '{self.data['id']}' already exists", severity="error")
        except OSError as e:
            self.app.notify(f"Failed to create agent: {e}", severity="error")
