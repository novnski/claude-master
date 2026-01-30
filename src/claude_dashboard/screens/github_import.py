"""GitHub Import screen for importing skills from GitHub repositories."""

import os
import tempfile
import shutil
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, Button, DataTable, ProgressBar
from textual import work
from claude_dashboard.config.claude_config import ClaudeConfig, ConfigChanged


class GitHubImportScreen(Vertical):
    """Screen for importing skills from GitHub repositories."""

    CSS = """
    GitHubImportScreen {
        padding: 1;
    }
    #url_input {
        margin: 1 0;
    }
    #progress_section {
        display: none;
        margin: 1 0;
    }
    #progress_section.visible {
        display: block;
    }
    #skills_table {
        height: 1fr;
        margin: 1 0;
    }
    .button_row {
        height: auto;
        margin: 1 0;
    }
    #status_label {
        margin: 1 0;
    }
    """

    def __init__(self):
        super().__init__()
        self._temp_dir = None
        self._skills_dir = None
        self._available_skills = []

    def compose(self) -> ComposeResult:
        yield Label("[b]IMPORT SKILLS FROM GITHUB[/b]\n")
        yield Label("Enter a GitHub repository URL containing skills:")
        yield Label("(e.g., https://github.com/username/repo)", classes="dim")

        with Horizontal():
            yield Input(placeholder="https://github.com/...", id="url_input")
            yield Button("Analyze", variant="primary", id="analyze_btn")

        with Vertical(id="progress_section"):
            yield Label("Fetching repository...", id="status_label")
            yield ProgressBar(id="progress_bar", total=100)

        yield Label("\nAvailable Skills:")
        table = DataTable(id="skills_table")
        table.add_columns("Skill Name", "Description", "Status")
        table.cursor_type = "row"
        yield table

        with Horizontal(classes="button_row"):
            yield Button(
                "Import Selected", variant="primary", id="import_btn", disabled=True
            )
            yield Button(
                "Import All", variant="success", id="import_all_btn", disabled=True
            )
            yield Button("Refresh", id="refresh_btn")

    def on_mount(self):
        """Load any already-imported skills on mount."""
        self._refresh_skills_table()

    def _refresh_skills_table(self):
        """Refresh the skills table with currently available skills."""
        table = self.query_one("#skills_table", DataTable)
        table.clear()

        config = ClaudeConfig()
        skills = config.get_skills()

        for skill in skills:
            name = skill.get("name", skill.get("id", "Unknown"))
            desc = skill.get("description", "No description")
            table.add_row(name, desc, "[green]Installed[/green]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "analyze_btn":
            self._analyze_repository()
        elif event.button.id == "import_btn":
            self._import_selected_skill()
        elif event.button.id == "import_all_btn":
            self._import_all_skills()
        elif event.button.id == "refresh_btn":
            self._refresh_skills_table()
            self.app.notify("Skills list refreshed")

    @work(thread=True)
    def _analyze_repository(self) -> None:
        """Clone and analyze repository for available skills."""
        url_input = self.query_one("#url_input", Input)
        url = url_input.value.strip()

        if not url:
            self.app.notify("Please enter a GitHub URL", severity="error")
            return

        # Normalize URL
        if not url.startswith("https://github.com/") and not url.startswith(
            "git@github.com:"
        ):
            self.app.notify("Please enter a valid GitHub URL", severity="error")
            return

        # Show progress
        self._set_progress_visible(True)
        self._update_status("Cloning repository...")
        self._update_progress(10)

        try:
            # Create temp directory
            self._temp_dir = tempfile.mkdtemp(prefix="claude_skills_")

            # Clone repository
            repo_name = url.split("/")[-1].replace(".git", "")
            clone_path = Path(self._temp_dir) / repo_name

            self._update_progress(30)

            # Use git to clone
            import subprocess

            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.app.notify(f"Failed to clone: {result.stderr}", severity="error")
                self._set_progress_visible(False)
                return

            self._update_status("Analyzing skills...")
            self._update_progress(60)

            # Look for skills directory
            skills_path = clone_path / "skills"
            if not skills_path.exists():
                # Try root directory
                skills_path = clone_path

            self._skills_dir = skills_path
            self._available_skills = []

            # Scan for skill directories
            for item in skills_path.iterdir():
                if item.is_dir():
                    skill_file = item / "SKILL.md"
                    if skill_file.exists():
                        # Parse skill metadata
                        try:
                            from claude_dashboard.utils.frontmatter import (
                                parse_frontmatter,
                            )

                            data = parse_frontmatter(skill_file.read_text())
                            self._available_skills.append(
                                {
                                    "id": item.name,
                                    "name": data.get("name", item.name),
                                    "description": data.get(
                                        "description", "No description"
                                    ),
                                    "path": str(item),
                                }
                            )
                        except Exception:
                            # Still add even if parsing fails
                            self._available_skills.append(
                                {
                                    "id": item.name,
                                    "name": item.name,
                                    "description": "No description available",
                                    "path": str(item),
                                }
                            )

            self._update_progress(100)
            self._update_status(f"Found {len(self._available_skills)} skills")

            # Update table with available skills
            self._update_skills_table_with_available()

            # Enable import buttons
            self._enable_import_buttons()

        except subprocess.TimeoutExpired:
            self.app.notify("Clone operation timed out", severity="error")
        except Exception as e:
            self.app.notify(f"Error analyzing repository: {e}", severity="error")
        finally:
            self._set_progress_visible(False)

    def _update_skills_table_with_available(self):
        """Update the table with available skills from repo."""
        table = self.query_one("#skills_table", DataTable)
        table.clear()

        # Get currently installed skills
        config = ClaudeConfig()
        installed = {s["id"] for s in config.get_skills()}

        for skill in self._available_skills:
            status = "[red]Not installed[/red]"
            if skill["id"] in installed:
                status = "[green]Installed[/green]"
            table.add_row(skill["name"], skill["description"], status)

    def _import_selected_skill(self):
        """Import the selected skill."""
        table = self.query_one("#skills_table", DataTable)
        if table.selected_row is None:
            self.app.notify("Please select a skill to import", severity="error")
            return

        # Get selected skill
        row_idx = table.selected_row
        if row_idx < len(self._available_skills):
            skill = self._available_skills[row_idx]
            self._install_skill(skill)

    def _import_all_skills(self):
        """Import all available skills."""
        imported = 0
        failed = 0

        for skill in self._available_skills:
            if self._install_skill(skill, notify=False):
                imported += 1
            else:
                failed += 1

        if failed == 0:
            self.app.notify(f"Successfully imported {imported} skills")
        else:
            self.app.notify(
                f"Imported {imported} skills, {failed} failed", severity="warning"
            )

        self._refresh_skills_table()

    def _install_skill(self, skill: dict, notify: bool = True) -> bool:
        """Install a single skill to the local skills directory."""
        try:
            skills_dir = Path.home() / ".claude" / "skills"
            skills_dir.mkdir(parents=True, exist_ok=True)

            target_dir = skills_dir / skill["id"]
            source_dir = Path(skill["path"])

            if target_dir.exists():
                # Overwrite existing
                shutil.rmtree(target_dir)

            # Copy skill directory
            shutil.copytree(source_dir, target_dir)

            if notify:
                self.app.notify(f"Imported skill: {skill['name']}")
                self._refresh_skills_table()
                self.app.post_message(ConfigChanged())

            return True

        except Exception as e:
            if notify:
                self.app.notify(
                    f"Failed to import {skill['name']}: {e}", severity="error"
                )
            return False

    def _set_progress_visible(self, visible: bool):
        """Show or hide progress section."""
        progress_section = self.query_one("#progress_section", Vertical)
        if visible:
            progress_section.styles.display = "block"
        else:
            progress_section.styles.display = "none"

    def _update_status(self, message: str):
        """Update status label."""
        status_label = self.query_one("#status_label", Label)
        status_label.update(message)

    def _update_progress(self, value: int):
        """Update progress bar."""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.update(progress=value)

    def _enable_import_buttons(self):
        """Enable import buttons when skills are available."""
        import_btn = self.query_one("#import_btn", Button)
        import_all_btn = self.query_one("#import_all_btn", Button)
        import_btn.disabled = len(self._available_skills) == 0
        import_all_btn.disabled = len(self._available_skills) == 0

    def cleanup(self):
        """Cleanup temporary directory."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass
