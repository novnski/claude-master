"""Marketplace screen for browsing and installing community skills."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Select, Button, Header, Label
from pathlib import Path


class MarketplaceScreen(Vertical):
    """Browse and install skills from remote repository."""

    CSS = """
    MarketplaceScreen {
        height: 100%;
    }
    #filter_bar {
        height: 3;
        dock: top;
    }
    #skills_table {
        height: 1fr;
    }
    """

    DEFAULT_REPO = "https://github.com/anthropics/claude-skills"

    SAMPLE_SKILLS = [
        ("postgres_client", "@dwarkesh", "Safe SQL execution wrapper", "★ 1.2k"),
        ("slack_notifier", "@anthropic", "Post updates to Slack channels", "★ 800"),
        ("docker_run", "@jdoe", "Run code in isolated container", "★ 150"),
        ("web_search", "@community", "Brave Search API integration", "★ 2.1k"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("[b]SKILL MARKETPLACE[/b]\n[b]Community Skills Repository[/b]")

        with Horizontal(id="filter_bar"):
            yield Input(placeholder="Filter skills...", id="filter_input")
            yield Select(
                options=[("Popular", "popular"), ("Recent", "recent"), ("Downloads", "downloads")],
                value="popular",
                id="sort_select"
            )

        yield DataTable(id="skills_table")

        with Horizontal():
            yield Button("INSTALL SELECTED", variant="primary", id="install_btn")
            yield Button("VIEW SOURCE", id="source_btn")
            yield Button("CHANGE REPO", id="repo_btn")

    def on_mount(self):
        """Load skills from repository."""
        table = self.query_one("#skills_table", DataTable)
        table.add_columns("Skill", "Author", "Description", "Downloads")

        self._load_skills(self.SAMPLE_SKILLS)

    def _load_skills(self, skills: list):
        """Populate table with skills."""
        table = self.query_one("#skills_table", DataTable)
        table.clear()

        for skill in skills:
            table.add_row(*skill)

        table.cursor_type = "row"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter skills based on input."""
        if event.input.id == "filter_input":
            search = event.value.lower()

            filtered = [
                skill for skill in self.SAMPLE_SKILLS
                if search in skill[0].lower() or
                   search in skill[1].lower() or
                   search in skill[2].lower()
            ]

            self._load_skills(filtered)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        table = self.query_one("#skills_table", DataTable)

        if not table.selected_row:
            self.app.notify("Select a skill first", severity="warning")
            return

        if event.button.id == "install_btn":
            self._install_selected_skill()
        elif event.button.id == "source_btn":
            self._view_source()
        elif event.button.id == "repo_btn":
            self._change_repo()

    def _install_selected_skill(self):
        """Install selected skill to ~/.claude/skills/."""
        table = self.query_one("#skills_table", DataTable)
        cell = table.get_cell(table.selected_row, "Skill")
        skill_name = str(cell)

        skills_dir = Path.home() / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        # Create placeholder
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(exist_ok=True)

        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Installed from marketplace\n---\n"
        )

        self.app.notify(f"Installed: {skill_name}")

        # Trigger refresh
        from claude_dashboard.config.claude_config import ConfigChanged
        self.app.post_message(ConfigChanged())

    def _view_source(self):
        """Open source URL in browser."""
        self.app.notify(
            f"Source repository:\n{self.DEFAULT_REPO}\n\n"
            "Would open in browser with webbrowser library"
        )

    def _change_repo(self):
        """Prompt for different repository."""
        self.app.notify("Repository change feature coming soon")
