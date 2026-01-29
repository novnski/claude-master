"""Skill Assignment Modal for assigning skills to agents."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Checkbox, Button
from claude_dashboard.config.claude_config import ClaudeConfig
from claude_dashboard.utils.frontmatter import update_frontmatter


class SkillAssignmentModal(ModalScreen):
    """Modal for assigning skills to an agent."""

    CSS = """
    SkillAssignmentModal {
        background: $panel;
        border: thick $primary;
    }
    #modal_container {
        padding: 1;
        min-width: 60;
    }
    #skills_list {
        height: 20;
    }
    Checkbox {
        margin: 0 1;
    }
    """

    def __init__(self, agent_id: str, enabled_skills: set = None, agent_path: str = None):
        super().__init__()
        self.agent_id = agent_id
        self.enabled_skills = enabled_skills or set()
        self.agent_path = agent_path

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_container"):
            yield Label(f"[b]ASSIGN SKILLS: {self.agent_id}[/b]")
            yield Label("Select enabled capabilities for this agent:")
            yield Label("")  # spacer

            # Add checkboxes for each skill
            config = ClaudeConfig()
            skills = config.get_skills()

            with ScrollableContainer(id="skills_list"):
                for skill in skills:
                    skill_id = skill["id"]
                    description = skill.get("description", "")[:40]
                    is_checked = skill_id in self.enabled_skills

                    yield Checkbox(
                        label=f"{skill_id:20} ({description})",
                        value=is_checked,
                        id=f"skill_{skill_id}"
                    )

            yield Label("")  # spacer
            with Horizontal():
                yield Button("SAVE", variant="primary", id="save")
                yield Button("CANCEL", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save":
            self._save_assignments()

    def _save_assignments(self):
        """Collect selected skills and save to agent file."""
        if not self.agent_path:
            self.app.notify(f"Cannot update agent {self.agent_id}: no file path", severity="error")
            return

        # Collect selected skill IDs
        selected_skills = []
        for checkbox in self.query(Checkbox):
            if checkbox.value:
                skill_id = checkbox.id.replace("skill_", "")
                selected_skills.append(skill_id)

        try:
            # Read current agent file
            from pathlib import Path
            agent_file = Path(self.agent_path)
            content = agent_file.read_text()

            # Update frontmatter with skills list
            updated_content = update_frontmatter(content, {"skills": selected_skills})

            # Write back to file
            agent_file.write_text(updated_content)

            self.app.notify(f"Assigned {len(selected_skills)} skills to {self.agent_id}")
            self.app.pop_screen()

            # Trigger refresh
            from claude_dashboard.config.claude_config import ConfigChanged
            self.app.post_message(ConfigChanged())
        except OSError as e:
            self.app.notify(f"Failed to update agent: {e}", severity="error")
