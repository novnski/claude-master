# Claude Master Dashboard (Terminal Edition) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans

**Goal:** Build a terminal-based TUI dashboard for managing Claude Code configuration (agents, skills, settings) with browsing, editing, and visualization capabilities.

**Architecture:** Python + Textual TUI framework, sidebar navigation pattern, file watcher for hot-reload, singleton config layer for ~/.claude/ access.

**Tech Stack:** Python 3.10+, Textual (TUI), pyyaml (frontmatter), watchdog (file watching), pytest (testing).

---

## Phase 1: Project Foundation & Core UI

### Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/__init__.py`
- Create: `src/__main__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "claude-dashboard"
version = "0.1.0"
description = "Terminal dashboard for managing Claude Code configuration"
requires-python = ">=3.10"
dependencies = [
    "textual>=0.80.0",
    "pyyaml>=6.0",
    "watchdog>=4.0",
]

[project.scripts]
claude-dashboard = "claude_dashboard.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/claude_dashboard"]
```

**Step 2: Create README.md**

```markdown
# Claude Master Dashboard

Terminal-based TUI for managing Claude Code configuration.

## Install

```bash
pipx install claude-dashboard
```

## Run

```bash
claude-dashboard
```
```

**Step 3: Create src/__init__.py**
```python
# Empty file for package
```

**Step 4: Create src/__main__.py**

```python
from textual.app import App

class ClaudeDashboard(App):
    def on_mount(self):
        self.mount("Claude Master Dashboard - Coming Soon")

def main():
    app = ClaudeDashboard()
    app.run()

if __name__ == "__main__":
    main()
```

**Step 5: Test basic app runs**

Run: `python -m claude_dashboard`
Expected: App launches, shows text, exit with Ctrl+C

**Step 6: Initialize git and commit**

```bash
git init
git add .
git commit -m "feat: initial project setup with Textual app skeleton"
```

---

### Task 2: YAML Frontmatter Parser

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/frontmatter.py`
- Create: `tests/utils/test_frontmatter.py`

**Step 1: Write failing test**

Create `tests/utils/test_frontmatter.py`:

```python
import pytest
from claude_dashboard.utils.frontmatter import parse_frontmatter

def test_parse_agent_with_frontmatter():
    content = """---
name: architect
description: Design architecture
model: opus
---
This is the body content."""
    result = parse_frontmatter(content)
    assert result["name"] == "architect"
    assert result["description"] == "Design architecture"
    assert result["model"] == "opus"
    assert result["content"] == "This is the body content."

def test_parse_file_without_frontmatter():
    content = "Just plain content"
    result = parse_frontmatter(content)
    assert result["content"] == "Just plain content"
    assert "name" not in result

def test_parse_empty_frontmatter():
    content = """---
---
Body only"""
    result = parse_frontmatter(content)
    assert result["content"] == "Body only"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/utils/test_frontmatter.py -v`
Expected: FAIL - ModuleNotFoundError or function not defined

**Step 3: Create utils package**

Create `src/utils/__init__.py` (empty)

**Step 4: Implement minimal frontmatter parser**

Create `src/utils/frontmatter.py`:

```python
import re
import yaml
from typing import Any

def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content with optional YAML frontmatter

    Returns:
        Dict with frontmatter fields + 'content' key for body text
    """
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {"content": content}

    frontmatter_text = match.group(1)
    body_text = match.group(2)

    try:
        metadata = yaml.safe_load(frontmatter_text) or {}
        metadata["content"] = body_text
        return metadata
    except yaml.YAMLError:
        return {"content": body_text}
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/utils/test_frontmatter.py -v`
Expected: PASS (3/3 tests)

**Step 6: Commit**

```bash
git add tests/utils/test_frontmatter.py src/utils/
git commit -m "feat: add YAML frontmatter parser with tests"
```

---

### Task 3: Claude Configuration Layer

**Files:**
- Create: `src/config/__init__.py`
- Create: `src/config/claude_config.py`
- Create: `tests/config/test_claude_config.py`

**Step 1: Write failing test**

Create `tests/config/test_claude_config.py`:

```python
import pytest
from pathlib import Path
from claude_dashboard.config.claude_config import ClaudeConfig

@pytest.fixture
def mock_claude_dir(tmp_path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Create test agent
    (agents_dir / "architect.md").write_text("""---
name: architect
description: Design agent
---
Body content""")

    # Create test skill
    skill_dir = skills_dir / "brainstorming"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: brainstorming
description: Generate ideas
---
Skill content""")

    return tmp_path

def test_get_agents(mock_claude_dir):
    config = ClaudeConfig(claude_dir=mock_claude_dir)
    agents = config.get_agents()
    assert len(agents) == 1
    assert agents[0]["id"] == "architect"
    assert agents[0]["name"] == "architect"

def test_get_skills(mock_claude_dir):
    config = ClaudeConfig(claude_dir=mock_claude_dir)
    skills = config.get_skills()
    assert len(skills) == 1
    assert skills[0]["id"] == "brainstorming"
    assert skills[0]["name"] == "brainstorming"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/config/test_claude_config.py -v`
Expected: FAIL - Module not found

**Step 3: Create config package**

Create `src/config/__init__.py` (empty)

**Step 4: Implement ClaudeConfig**

Create `src/config/claude_config.py`:

```python
from pathlib import Path
from typing import Any
import os

from claude_dashboard.utils.frontmatter import parse_frontmatter

class ClaudeConfig:
    """Singleton for accessing Claude Code configuration."""

    _instance = None

    def __new__(cls, claude_dir: Path | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, claude_dir: Path | None = None):
        if self._initialized:
            return

        self.claude_dir = claude_dir or Path.home() / ".claude"
        self._initialized = True

    def get_agents(self) -> list[dict[str, Any]]:
        """Get all agents from ~/.claude/agents/*.md"""
        agents_dir = self.claude_dir / "agents"
        if not agents_dir.exists():
            return []

        agents = []
        for file in agents_dir.glob("*.md"):
            data = parse_frontmatter(file.read_text())
            data["id"] = file.stem
            data["path"] = str(file)
            agents.append(data)
        return agents

    def get_skills(self) -> list[dict[str, Any]]:
        """Get all skills from ~/.claude/skills/*/SKILL.md"""
        skills_dir = self.claude_dir / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for item in skills_dir.iterdir():
            if item.is_dir() or item.is_symlink():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    data = parse_frontmatter(skill_file.read_text())
                    data["id"] = item.name
                    data["path"] = str(skill_file)
                    skills.append(data)
        return skills
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/config/test_claude_config.py -v`
Expected: PASS (2/2 tests)

**Step 6: Commit**

```bash
git add tests/config/ src/config/
git commit -m "feat: add ClaudeConfig singleton for reading ~/.claude"
```

---

### Task 4: Main App with Sidebar

**Files:**
- Modify: `src/__main__.py`
- Create: `src/app.py`

**Step 1: Create app.py**

```python
from textual.app import App, ComposeResult
from textual.widgets import Sidebar, Header, Footer, Static
from textual.containers import Horizontal, Vertical

class ClaudeDashboard(App):
    """Main Claude Dashboard application."""

    CSS = """
    Screen {
        background: $panel;
    }
    Sidebar {
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield Sidebar(
                "Agents",
                "Skills",
                "Settings",
                "Sessions",
                "Updates",
            )
            with Vertical(id="content_area"):
                yield Static("Welcome to Claude Dashboard", id="main_content")
        yield Footer()

    def on_sidebar_highlighted(self, event: Sidebar.Highlighted) -> None:
        """Handle sidebar item highlight."""
        self.query_one("#main_content", Static).update(
            f"Selected: {event.item}"
        )

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        self.query_one("#main_content", Static).update(
            f"Opened: {event.item}"
        )
```

**Step 2: Update __main__.py**

```python
from claude_dashboard.app import ClaudeDashboard

def main():
    app = ClaudeDashboard()
    app.run()

if __name__ == "__main__":
    main()
```

**Step 3: Test the app**

Run: `python -m claude_dashboard`
Expected: App launches with sidebar, can navigate items with arrow keys

**Step 4: Commit**

```bash
git add src/__main__.py src/app.py
git commit -m "feat: add sidebar navigation to main app"
```

---

### Task 5: Agents Screen

**Files:**
- Create: `src/screens/__init__.py`
- Create: `src/screens/agents.py`

**Step 1: Create agents screen**

Create `src/screens/agents.py`:

```python
from textual.containers import Vertical, Horizontal
from textual.widgets import DataTable, Static
from textual.screen import ModalScreen

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
```

**Step 2: Update app.py to use AgentsScreen**

```python
from textual.app import App, ComposeResult
from textual.widgets import Sidebar, Header, Footer
from textual.containers import Horizontal, Vertical
from claude_dashboard.screens.agents import AgentsScreen

class ClaudeDashboard(App):
    """Main Claude Dashboard application."""

    CSS = """
    Screen {
        background: $panel;
    }
    Sidebar {
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Horizontal():
            yield Sidebar(
                "Agents",
                "Skills",
                "Settings",
            )
            with Vertical(id="content_area"):
                yield AgentsScreen()
        yield Footer()

    def on_sidebar_selected(self, event: Sidebar.Selected) -> None:
        """Handle sidebar item selection."""
        content_area = self.query_one("#content_area", Vertical)
        content_area.remove_children()

        if event.item == "Agents":
            content_area.mount(AgentsScreen())
```

**Step 3: Test agents screen**

Run: `python -m claude_dashboard`
Expected: Shows agents table with real data from ~/.claude/agents/

**Step 4: Commit**

```bash
git add src/screens/ src/app.py
git commit -m "feat: add agents screen with data table"
```

---

### Task 6: Agent Detail Screen

**Files:**
- Modify: `src/screens/agents.py`

**Step 1: Add AgentDetailScreen to agents.py**

Add to `src/screens/agents.py`:

```python
from textual.screen import ModalScreen
from textual.widgets import Button, Label

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
```

**Step 2: Update AgentsScreen to show detail on select**

Update `on_data_table_row_selected` in `AgentsScreen`:

```python
def on_data_table_row_selected(self, event):
    """Handle row selection."""
    table = self.query_one(DataTable)
    row_key = event.row_key
    cell = table.get_cell(row_key, "ID")
    agent_id = str(cell)

    from claude_dashboard.config.claude_config import ClaudeConfig
    config = ClaudeConfig()
    agents = config.get_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)

    if agent:
        self.app.push_screen(AgentDetailScreen(agent))
```

**Step 3: Test agent detail**

Run: `python -m claude_dashboard`
Expected: Selecting a row opens detail modal, Close button works

**Step 4: Commit**

```bash
git add src/screens/agents.py
git commit -m "feat: add agent detail modal screen"
```

---

### Task 7: External Editor Integration

**Files:**
- Modify: `src/screens/agents.py`
- Create: `src/utils/editor.py`

**Step 1: Create editor utility**

Create `src/utils/editor.py`:

```python
import os
import subprocess
from pathlib import Path

def open_editor(file_path: Path | str) -> None:
    """Open file in user's configured editor.

    Uses $EDITOR env var, defaults to 'vi'.
    """
    editor = os.environ.get("EDITOR", "vi")
    file_path = str(file_path)

    # Temporarily exit terminal UI
    subprocess.call([editor, file_path])
```

**Step 2: Update AgentDetailScreen to handle edit button**

Update `on_button_pressed` in `AgentDetailScreen`:

```python
from claude_dashboard.utils.editor import open_editor

def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "close":
        self.app.pop_screen()
    else:
        # Edit button
        from textual.app import App
        # Exit screen, edit file, then refresh
        self.app.pop_screen()
        self.app.exit()  # Exit TUI temporarily
        open_editor(self.agent_data["path"])
```

**Step 3: Test editor integration**

Run: `EDITOR=nano python -m claude_dashboard`
Expected: Clicking Edit opens nano, app exits

**Step 4: Commit**

```bash
git add src/utils/editor.py src/screens/agents.py
git commit -m "feat: add external editor integration"
```

---

## Phase 2: Additional Features

### Task 8: Skills Screen

**Files:**
- Create: `src/screens/skills.py`

**Step 1: Create skills screen**

Create `src/screens/skills.py`:

```python
from textual.containers import Vertical
from textual.widgets import DataTable

class SkillsScreen(Vertical):
    """Screen showing list of skills."""

    def compose(self):
        yield DataTable()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Description")

        from claude_dashboard.config.claude_config import ClaudeConfig
        config = ClaudeConfig()
        skills = config.get_skills()

        for skill in skills:
            table.add_row(
                skill["id"],
                skill.get("name", skill["id"]),
                skill.get("description", "")[:50]
            )
```

**Step 2: Update app.py to handle Skills selection**

Add to `on_sidebar_selected` in `app.py`:

```python
from claude_dashboard.screens.skills import SkillsScreen

# In on_sidebar_selected:
if event.item == "Skills":
    content_area.mount(SkillsScreen())
```

**Step 3: Test skills screen**

Run: `python -m claude_dashboard`
Expected: Skills sidebar item shows skills table

**Step 4: Commit**

```bash
git add src/screens/skills.py src/app.py
git commit -m "feat: add skills screen"
```

---

### Task 9: Settings Screen

**Files:**
- Create: `src/screens/settings.py`
- Modify: `src/config/claude_config.py`

**Step 1: Add get_settings to ClaudeConfig**

Add to `src/config/claude_config.py`:

```python
import json

def get_settings(self) -> dict[str, Any]:
    """Get settings with sensitive values masked."""
    settings_file = self.claude_dir / "settings.json"
    if not settings_file.exists():
        return {}

    with open(settings_file) as f:
        settings = json.load(f)

    # Mask API keys and tokens
    if "env" in settings:
        for key in settings["env"]:
            if any(word in key.upper() for word in ["KEY", "TOKEN", "SECRET"]):
                settings["env"][key] = "••••••••"

    return settings
```

**Step 2: Create settings screen**

Create `src/screens/settings.py`:

```python
from textual.containers import Vertical
from textual.widgets import Static
import json

class SettingsScreen(Vertical):
    """Screen showing Claude settings."""

    def compose(self):
        yield Static(id="settings_display")

    def on_mount(self):
        from claude_dashboard.config.claude_config import ClaudeConfig
        config = ClaudeConfig()
        settings = config.get_settings()

        display = self.query_one("#settings_display", Static)
        display.update(f"```json\n{json.dumps(settings, indent=2)}\n```")
```

**Step 3: Update app.py for Settings**

```python
from claude_dashboard.screens.settings import SettingsScreen

# In on_sidebar_selected:
if event.item == "Settings":
    content_area.mount(SettingsScreen())
```

**Step 4: Test settings screen**

Run: `python -m claude_dashboard`
Expected: Settings shown with masked secrets

**Step 5: Commit**

```bash
git add src/screens/settings.py src/config/claude_config.py
git commit -m "feat: add settings viewer with secret masking"
```

---

### Task 10: File Watcher for Hot-Reload

**Files:**
- Modify: `src/config/claude_config.py`
- Modify: `src/app.py`

**Step 1: Add file watching to ClaudeConfig**

Update `src/config/claude_config.py`:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from textual.message import Message

class ConfigChanged(Message):
    """Emitted when Claude config changes."""

class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith(('.md', '.json')):
            self.callback()

class ClaudeConfig:
    # ... existing code ...

    def start_watching(self, callback):
        """Start watching for config changes."""
        observer = Observer()
        handler = ConfigWatcher(callback)
        observer.schedule(handler, str(self.claude_dir), recursive=True)
        observer.start()
        return observer
```

**Step 2: Update app to watch and reload**

Update `src/app.py`:

```python
from claude_dashboard.config.claude_config import ClaudeConfig, ConfigChanged

class ClaudeDashboard(App):
    # ... existing code ...

    def on_mount(self):
        # Start file watcher
        config = ClaudeConfig()
        def on_config_change():
            self.post_message(ConfigChanged())
        self._observer = config.start_watching(on_config_change)

    def on_config_changed(self, event: ConfigChanged) -> None:
        """Refresh current screen when config changes."""
        # Re-mount current screen
        pass
```

**Step 3: Test hot-reload**

Run: `python -m claude-dashboard`
In another terminal: `touch ~/.claude/agents/test.md`
Expected: App refreshes

**Step 4: Commit**

```bash
git add src/config/claude_config.py src/app.py
git commit -m "feat: add file watcher for hot-reload"
```

---

## Phase 3: Advanced Features

### Task 11: Relationships Visualization

**Files:**
- Create: `src/screens/relationships.py`

**Step 1: Create relationships screen**

Create `src/screens/relationships.py`:

```python
from textual.containers import Vertical
from textual.widgets import Tree, TreeNode
from claude_dashboard.config.claude_config import ClaudeConfig

class RelationshipsScreen(Vertical):
    """Screen showing agent-skill relationships."""

    def compose(self):
        yield Tree("Agents")

    def on_mount(self):
        tree = self.query_one(Tree)
        config = ClaudeConfig()

        for agent in config.get_agents():
            agent_node = tree.root.add(agent["id"])

            if "skills" in agent:
                for skill_id in agent["skills"]:
                    agent_node.add_leaf(f"Skill: {skill_id}")

        tree.root.expand()
```

**Step 2: Update app.py for Relationships**

```python
from claude_dashboard.screens.relationships import RelationshipsScreen

# In on_sidebar_selected:
if event.item == "Relationships":
    content_area.mount(RelationshipsScreen())
```

**Step 3: Test relationships**

Run: `python -m claude_dashboard`
Expected: Tree view of agents and their skills

**Step 4: Commit**

```bash
git add src/screens/relationships.py src/app.py
git commit -m "feat: add agent-skill relationship tree visualization"
```

---

### Task 12: Sessions Monitor

**Files:**
- Create: `src/screens/sessions.py`

**Step 1: Create sessions screen**

Create `src/screens/sessions.py`:

```python
from textual.containers import Vertical
from textual.widgets import DataTable
from pathlib import Path

class SessionsScreen(Vertical):
    """Screen showing active/recent sessions."""

    def compose(self):
        yield DataTable()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Project", "Last Active", "Messages")

        # Find .claude projects
        # This is a placeholder - actual implementation depends on session storage
        table.add_row("example-project", "Just now", "42")
```

**Step 2: Update app.py**

```python
from claude_dashboard.screens.sessions import SessionsScreen

# Add to sidebar and on_sidebar_selected
```

**Step 3: Commit**

```bash
git add src/screens/sessions.py
git commit -m "feat: add sessions monitor (placeholder)"
```

---

### Task 13: Create New Agent/Skill

**Files:**
- Create: `src/widgets/create_modal.py`

**Step 1: Create creation modal**

Create `src/widgets/create_modal.py`:

```python
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical

class CreateAgentModal(ModalScreen):
    """Modal for creating new agent."""

    def compose(self):
        yield Label("Create New Agent")
        yield Input(placeholder="Agent ID", id="agent_id")
        yield Input(placeholder="Name", id="agent_name")
        yield Button("Create", variant="primary", id="create")
        yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "create":
            # Create agent file
            agent_id = self.query_one("#agent_id", Input).value
            name = self.query_one("#agent_name", Input).value

            from pathlib import Path
            claude_dir = Path.home() / ".claude" / "agents"
            agent_file = claude_dir / f"{agent_id}.md"

            content = f"""---
name: {name}
description: New agent
---
Agent description here."""

            agent_file.write_text(content)
            self.app.pop_screen()
```

**Step 2: Add create button to agents screen**

Add to `AgentsScreen`:
```python
yield Button("Create New Agent", id="create_agent")

def on_button_pressed(self, event):
    if event.button.id == "create_agent":
        self.app.push_screen(CreateAgentModal())
```

**Step 3: Test creation**

Run: `python -m claude_dashboard`
Expected: Create button opens modal, creates file

**Step 4: Commit**

```bash
git add src/widgets/create_modal.py src/screens/agents.py
git commit -m "feat: add create agent modal"
```

---

### Task 14: Update Checker

**Files:**
- Create: `src/utils/updater.py`

**Step 1: Create update checker**

Create `src/utils/updater.py`:

```python
import subprocess

def check_for_update() -> str | None:
    """Check if claude-code has updates available."""
    try:
        result = subprocess.run(
            ["npm", "outdated", "-g", "claude-code"],
            capture_output=True,
            text=True
        )
        if result.returncode == 1:  # outdated packages found
            return "Update available for claude-code"
    except FileNotFoundError:
        pass
    return None
```

**Step 2: Display in status bar**

Update `app.py`:
```python
from claude_dashboard.utils.updater import check_for_update

def on_mount(self):
    update_status = check_for_update()
    if update_status:
        self.query_one(Footer).update(update_status)
```

**Step 3: Commit**

```bash
git add src/utils/updater.py src/app.py
git commit -m "feat: add update checker for claude-code"
```

---

## Packaging & Distribution

### Task 15: pipx Installation

**Files:**
- Modify: `pyproject.toml`

**Step 1: Update pyproject.toml for proper packaging**

Ensure `[project.scripts]` entry exists:
```toml
[project.scripts]
claude-dashboard = "claude_dashboard.__main__:main"
```

**Step 2: Build package**

```bash
pip install build
python -m build
```

**Step 3: Test local install**

```bash
pip install --user .
claude-dashboard
```

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: finalize pyproject.toml for pipx installation"
```

---

### Task 16: Single-File Script Distribution

**Files:**
- Create: `scripts/create-singlefile.py`

**Step 1: Create bundler script**

Create `scripts/create-singlefile.py`:

```python
"""Bundle claude-dashboard into single Python script."""
import ast
import sys
from pathlib import Path

def bundle_source():
    """Combine all source files into single script."""
    output = ["#!/usr/bin/env python3", "# Claude Dashboard - Single File Distribution\n"]

    # Read each source file and append
    src_dir = Path("src/claude_dashboard")
    for py_file in src_dir.rglob("*.py"):
        rel_path = py_file.relative_to(src_dir)
        output.append(f"# === {rel_path} ===")
        output.append(py_file.read_text())

    Path("claude-dashboard.py").write_text("\n".join(output))
    print("Created: claude-dashboard.py")

if __name__ == "__main__":
    bundle_source()
```

**Step 2: Test single file**

```bash
python scripts/create-singlefile.py
python claude-dashboard.py
```

**Step 3: Commit**

```bash
git add scripts/create-singlefile.py
git commit -m "feat: add single-file script bundler"
```

---

## Verification

**Test complete installation:**

```bash
# Clean install test
pipx uninstall claude-dashboard || true
pipx install .
claude-dashboard
```

**Test single file:**
```bash
python claude-dashboard.py
```

**Verify all features:**
- [ ] Agents list shows real data
- [ ] Agent detail opens on select
- [ ] Edit button opens $EDITOR
- [ ] Skills list works
- [ ] Settings show with masked secrets
- [ ] File watcher refreshes on changes
- [ ] Relationships tree shows connections
- [ ] Create new agent works
