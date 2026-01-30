"""Create Skill Wizard for creating new skills."""

import random
import re
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, Button, Select
from claude_dashboard.config.claude_config import ConfigChanged
from claude_dashboard.utils.path_utils import sanitize_filename


class CreateSkillWizard(ModalScreen):
    """3-step wizard for creating new skills."""

    CSS = """
    CreateSkillWizard {
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
    """

    TEMPLATES = [
        ("Empty Skill", "empty"),
        ("API Integration", "api"),
        ("Data Processing", "data"),
        ("Utility", "utility"),
    ]

    def __init__(self):
        super().__init__()
        self.step = 1
        self.generated_id = f"sk_{random.randint(1000, 9999)}"
        self.data = {"name": "", "id": "", "description": "", "template": "empty"}

    def compose(self) -> ComposeResult:
        with Vertical(id="wizard_container"):
            yield Label(f"[b]CREATE NEW SKILL[/b]\n")
            yield Label(f"Step {self.step}/3: BASIC INFO", id="step_title")

            # Step 1: Basic Info
            with Vertical(id="step1", classes="step"):
                yield Label("Name:")
                yield Input(placeholder="Skill name", id="skill_name")
                yield Label("")
                yield Label(f"ID: (Auto-generated: {self.generated_id})")
                yield Label("")
                yield Label("Description:")
                yield Input(
                    placeholder="Brief description of what this skill does",
                    id="skill_description",
                )

            # Step 2: Template Selection (hidden initially)
            with Vertical(id="step2", classes="step"):
                yield Label("Template:")
                yield Select(
                    options=self.TEMPLATES, value="empty", id="template_select"
                )

            # Step 3: Review (hidden initially)
            with Vertical(id="step3", classes="step"):
                yield Label("Review:")
                yield Label("", id="review_text")

            yield Label("")  # spacer
            with Horizontal():
                yield Button("BACK", id="back", disabled=True)
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
            name_input = self.query_one("#skill_name", Input)
            if not name_input.value.strip():
                self.app.notify("Please enter a skill name", severity="error")
                return
            self.data["name"] = name_input.value.strip()
            self.data["id"] = self._sanitize_id(name_input.value.strip())

            desc_input = self.query_one("#skill_description", Input)
            self.data["description"] = desc_input.value.strip()

        elif self.step == 2:
            template_select = self.query_one("#template_select", Select)
            value = template_select.value
            if value is not None and not isinstance(
                value, type(template_select).NoSelection
            ):
                self.data["template"] = str(value)
            else:
                self.data["template"] = "empty"

            # Update review text
            review_text = self.query_one("#review_text", Label)
            review_text.update(
                f"Name: {self.data['name']}\n"
                f"ID: {self.data['id']}\n"
                f"Description: {self.data['description']}\n"
                f"Template: {self.data['template']}"
            )

        elif self.step == 3:
            self._create_skill()
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
        step_titles = {1: "BASIC INFO", 2: "TEMPLATE", 3: "REVIEW"}
        self.query_one("#step_title", Label).update(
            f"Step {self.step}/3: {step_titles[self.step]}"
        )

        # Show/hide step containers
        for i in range(1, 4):
            step_container = self.query_one(f"#step{i}", Vertical)
            step_container.styles.display = "block" if i == self.step else "none"

        # Update button states
        back_btn = self.query_one("#back", Button)
        next_btn = self.query_one("#next", Button)
        back_btn.disabled = self.step == 1
        next_btn.label = "CREATE" if self.step == 3 else "NEXT"

    def _sanitize_id(self, name: str) -> str:
        """Sanitize skill name into a valid ID."""
        # Convert to lowercase, replace spaces with underscores
        id_str = name.lower().replace(" ", "_")
        # Remove any non-alphanumeric characters except underscores
        id_str = re.sub(r"[^a-z0-9_]", "", id_str)
        # Ensure it starts with a letter
        if id_str and not id_str[0].isalpha():
            id_str = "sk_" + id_str
        # Use sanitize_filename as additional safety
        id_str = sanitize_filename(id_str)
        return id_str or self.generated_id

    def _create_skill(self):
        """Create the skill directory and SKILL.md file."""
        skills_dir = Path.home() / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        skill_dir = skills_dir / self.data["id"]

        # Check if skill already exists
        if skill_dir.exists():
            self.app.notify(
                f"Skill '{self.data['id']}' already exists", severity="error"
            )
            return

        try:
            # Create skill directory
            skill_dir.mkdir(parents=True, exist_ok=True)

            # Generate SKILL.md content based on template
            template_content = self._get_template_content()

            skill_file = skill_dir / "SKILL.md"
            with open(skill_file, "w") as f:
                f.write(template_content)

            self.app.notify(f"Created skill: {self.data['name']} ({self.data['id']})")
            self.app.pop_screen()

            # Trigger refresh
            self.app.post_message(ConfigChanged())

        except FileExistsError:
            self.app.notify(
                f"Skill '{self.data['id']}' already exists", severity="error"
            )
        except OSError as e:
            self.app.notify(f"Failed to create skill: {e}", severity="error")

    def _get_template_content(self) -> str:
        """Generate SKILL.md content based on template."""
        template = self.data["template"]

        base_frontmatter = f"""---
name: {self.data["name"]}
description: {self.data["description"]}
---

"""

        if template == "api":
            return (
                base_frontmatter
                + """# API Integration Skill

This skill provides integration with external APIs.

## Usage

```python
from your_module import make_api_call

result = make_api_call(endpoint, data)
```

## Configuration

Add API credentials to your ~/.claude/settings.json:

```json
{
  "env": {
    "API_KEY": "your-api-key"
  }
}
```
"""
            )
        elif template == "data":
            return (
                base_frontmatter
                + """# Data Processing Skill

This skill provides data transformation and processing capabilities.

## Usage

```python
from your_module import process_data

result = process_data(input_data)
```

## Features

- Data validation
- Format conversion
- Batch processing
"""
            )
        elif template == "utility":
            return (
                base_frontmatter
                + """# Utility Skill

This skill provides various utility functions.

## Usage

Import and use the functions as needed:

```python
from your_module import utility_function

result = utility_function(args)
```

## Functions

- `function1()` - Description
- `function2()` - Description
"""
            )
        else:  # empty
            return (
                base_frontmatter
                + """# {name}

This is a custom skill for Claude Code.

## Description

Add your skill description here.

## Usage

Explain how to use this skill.
""".format(name=self.data["name"])
            )
