# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Master Dashboard (Terminal Edition)** - A fully implemented terminal-based TUI application for managing Claude Code configuration, agents, and skills.

**Technology Stack:**
- Python 3.10+ (with type hints)
- Textual 0.80+ (async TUI framework)
- PyYAML (frontmatter parsing)
- Watchdog (file watching for hot-reload)
- pytest (testing)

## Development Commands

```bash
# Run directly without installation
python -m claude_dashboard

# Uninstall the application
claude-dashboard --uninstall

# Install via pipx (recommended)
pipx install .

# Run tests
pytest

# Run tests with coverage
pytest --cov=claude_dashboard

# Run specific test file
pytest tests/screens/test_agents.py

# Run with debug output (shows dev tools overlay)
TEXTUAL_DEBUG=1 python -m claude_dashboard

# Build for distribution
python -m build

# Create single-file script
python scripts/create-singlefile.py
```

## Architecture Overview

The app follows a classic Textual TUI architecture with a central app class, sidebar navigation, and screen-based content areas.

### ClaudeConfig Singleton
`src/claude_dashboard/config/claude_config.py` - Centralized access to `~/.claude/`:
- `get_agents()` - Loads from `~/.claude/agents/*.md`
- `get_skills()` - Loads from `~/.claude/skills/*/SKILL.md`
- `get_settings()` - Loads settings with secret masking for keys containing "KEY", "TOKEN", or "SECRET"
- `start_watching()` - Returns Watchdog Observer that emits `ConfigChanged` message on `.md`/`.json` modifications

### YAML Frontmatter Convention
All agents and skills use YAML frontmatter parsed by `utils/frontmatter.py`:

```yaml
---
name: architect
description: Designs architecture
model: opus
---
Body content here...
```

The `parse_frontmatter()` function returns a dict with frontmatter fields plus a `content` key for the body text.

### Screen Navigation Pattern
`app.py` implements the main navigation flow:
1. `Sidebar` widget wraps Textual's `OptionList`, emitting `Highlighted`/`Selected` messages with string items
2. `on_sidebar_selected()` clears `#content_area` and mounts the appropriate screen
3. Each screen loads data from `ClaudeConfig` on mount via `on_mount()`
4. `on_config_changed()` handler refreshes the current screen when files change

### Screen Types
- **List Screens** (AgentsScreen, SkillsScreen): Display tables with search/filter, open detail modals on select
- **Detail Screens** (AgentDetail, SkillDetail): Modal overlays showing full metadata and content preview
- **Editor Screens** (EditorScreen): Full-screen editor with syntax highlighting for 9+ languages
- **Utility Screens** (SettingsScreen, AnalyticsScreen, RelationshipsScreen, MarketplaceScreen)

### Modal System
Detail screens are pushed as modal overlays using `app.push_screen()`. The `EditorScreen` is also modal and handles file I/O directly.

### Theme System
`themes/__init__.py` manages theme switching:
- Themes are CSS files in `themes/*.css` (default, light, high_contrast)
- Current theme stored in `~/.claude/dashboard-state.json`
- `get_current_theme()`/`set_theme()` read/write this state file
- App loads theme CSS in `_load_theme()` during mount

### Command Palette
`widgets/command_palette.py` - Modal screen (Ctrl+P) with fuzzy search over available commands (Switch Theme, Create New Agent, etc.).

### Editor Integration
The `EditorScreen` provides inline editing with:
- Language auto-detection from file extension (9 languages: markdown, python, javascript, typescript, json, yaml, bash, plaintext)
- `LineNumbers` widget synced with TextArea scrolling
- Save/cancel keyboard shortcuts (Ctrl+S, Ctrl+Q)

Note: The app no longer uses external `$EDITOR` - all editing happens in the TUI.

### File Watcher Hot-Reload
Watchdog observer started in `app.on_mount()`:
- Monitors `~/.claude/` recursively for `.md` and `.json` changes
- Emits `ConfigChanged` message on modification
- Each screen implements `on_config_changed()` to refresh its data
- Observer stopped cleanly in `on_unmount()`

### Message Bus Pattern
Textual's message system connects components:
- `Sidebar.Selected` → screen switching
- `ConfigChanged` → screen refresh
- `UpdateAvailable` → footer notification
- Custom action messages from modals back to parent screens

## Directory Structure

```
src/claude_dashboard/
├── __main__.py           # Entry point for `claude-dashboard` command
├── app.py                # Main ClaudeDashboard app class
├── sidebar.py            # Sidebar navigation widget
├── config/
│   └── claude_config.py  # ClaudeConfig singleton
├── screens/              # All screen implementations
│   ├── agents.py         # Agent list and detail
│   ├── skills.py         # Skills browser
│   ├── settings.py       # Settings viewer
│   ├── sessions.py       # Session management
│   ├── analytics.py      # Token usage charts
│   ├── relationships.py  # Agent-skill tree view
│   ├── marketplace.py    # Community skills
│   ├── editor.py         # Full-screen inline editor
│   └── shortcuts_help.py # Keyboard shortcuts overlay
├── widgets/              # Reusable widgets
│   ├── command_palette.py # Ctrl+P command palette
│   └── line_numbers.py   # Editor line numbers
├── widgets_modals/       # Modal-specific widgets
│   ├── create_modal.py   # Create agent/skill modal
│   └── skill_assignment.py # Skill assignment interface
├── themes/               # CSS theme files
│   ├── default.css
│   ├── light.css
│   └── high_contrast.css
└── utils/                # Utilities
    ├── frontmatter.py    # YAML frontmatter parser
    ├── editor.py         # Editor utilities
    ├── updater.py        # Update checker
    └── usage_tracker.py  # Token usage tracking
```

## Key Implementation Details

### Type Hints
Codebase uses modern Python type hints (`dict[str, Any]`, `Path | None`, etc.) requiring Python 3.10+.

### Async Architecture
Textual is async-first; `on_mount()`, message handlers, and screen compositions use async/await patterns.

### Error Handling
File operations catch `OSError`, `PermissionError`, `UnicodeDecodeError` and skip unreadable files gracefully.

### Distribution Targets
1. **pipx package** - Standard Python packaging via `pyproject.toml` with `[project.scripts]` entry point
2. **Single-file script** - `scripts/create-singlefile.py` bundles everything into a portable Python script

### Uninstall Command
`--uninstall` flag auto-detects installation method:
- Checks for pipx venv directory and runs `pipx uninstall`
- For pip installs, runs `pip uninstall -y claude-dashboard`
- For standalone script, deletes the script file itself
- Falls back to manual instructions if auto-detection fails
