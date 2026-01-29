"""Skills screen showing list of skills from ~/.claude/skills/."""

from textual.containers import Vertical
from textual.widgets import DataTable, Label
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

    def compose(self):
        yield DataTable()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Description")

        config = ClaudeConfig()
        skills = config.get_skills()

        if not skills:
            # Show message if no skills found
            table.add_row("", "No skills found", "Check ~/.claude/skills/")
            return

        for skill in skills:
            description = skill.get("description", "")
            # Truncate description to fit in table
            display_desc = description[:50] + "..." if len(description) > 50 else description
            table.add_row(
                skill["id"],
                skill.get("name", skill["id"]),
                display_desc
            )
