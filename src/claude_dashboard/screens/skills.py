"""Skills screen showing list of skills from ~/.claude/skills/."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Label, Input
from claude_dashboard.config.claude_config import ClaudeConfig


class SkillsScreen(Vertical):
    """Screen showing list of skills."""

    CSS = """
    SkillsScreen {
        height: 100%;
    }
    DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter skills...", id="filter_input")
        yield DataTable(id="skills_table")

    def on_mount(self):
        table = self.query_one("#skills_table", DataTable)
        table.add_columns("ID", "Name", "Description")

        config = ClaudeConfig()
        self.skills = config.get_skills()

        if not self.skills:
            # Show message if no skills found
            table.add_row("", "No skills found", "Check ~/.claude/skills/")
            return

        self._populate_table(self.skills)

    def _populate_table(self, skills: list):
        """Populate table with given skills."""
        table = self.query_one("#skills_table", DataTable)
        table.clear()

        for skill in skills:
            description = skill.get("description", "")
            display_desc = description[:50] + "..." if len(description) > 50 else description
            table.add_row(
                skill["id"],
                skill.get("name", skill["id"]),
                display_desc
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter table based on input."""
        if event.input.id == "filter_input":
            search_term = event.value.lower()

            filtered = [
                skill for skill in (self.skills or [])
                if search_term in skill["id"].lower() or
                   search_term in skill.get("name", "").lower() or
                   search_term in skill.get("description", "").lower()
            ]

            if not filtered:
                table = self.query_one("#skills_table", DataTable)
                table.clear()
                table.add_row("", "No matching skills", "")
            else:
                self._populate_table(filtered)
