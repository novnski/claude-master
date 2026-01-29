# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Master Dashboard (Terminal Edition)** - A terminal-based TUI application for managing Claude Code configuration, agents, and skills.

**Status:** Pre-implementation planning phase. See `docs/plans/` for comprehensive design and implementation plan.

**Technology Stack:**
- Python 3.10+
- Textual (TUI framework)
- PyYAML (frontmatter parsing)
- Watchdog (file watching)
- pytest (testing)

## Project Structure (Planned)

```
src/
├── __main__.py           # Entry point (claude-dashboard command)
├── app.py                # Main ClaudeDashboard app class
├── config/
│   └── claude_config.py  # Singleton for ~/.claude/ access
├── screens/              # UI screens (agents, skills, settings, sessions)
├── widgets/              # Reusable components (editor modal, etc.)
└── utils/                # Utilities (frontmatter parser, editor, updater)
```

## Development Commands (When Implemented)

```bash
# Run directly without installation
python -m claude_dashboard

# Install via pipx (recommended)
pipx install .

# Run tests
pytest

# Build for distribution
python -m build

# Create single-file script
python scripts/create-singlefile.py
```

## Architecture Patterns

### ClaudeConfig Singleton
The `ClaudeConfig` class provides centralized access to `~/.claude/`:
- `get_agents()` - Loads agents from `~/.claude/agents/*.md`
- `get_skills()` - Loads skills from `~/.claude/skills/*/SKILL.md`
- `get_settings()` - Loads settings with secret masking
- `start_watching()` - File watcher for hot-reload

### YAML Frontmatter Convention
Agents and skills use YAML frontmatter:

```yaml
---
name: architect
description: Designs architecture
model: opus
---
Body content here...
```

The `parse_frontmatter()` utility extracts this into a dict with `content` key for body text.

### Screen Navigation Pattern
Sidebar drives content switching via `on_sidebar_selected()`:
1. Clear `#content_area` container
2. Mount new screen (AgentsScreen, SkillsScreen, etc.)
3. Screen loads data from ClaudeConfig on mount

### Modal Detail Views
Detail screens (AgentDetail, SkillDetail) are modal overlays that:
- Show full metadata and content preview
- Provide "Edit" button that opens `$EDITOR`
- Require app exit/suspend for external editor

### File Watcher Hot-Reload
Watchdog observer monitors `~/.claude/` for `.md` and `.json` changes:
- Emits `ConfigChanged` message on modification
- Triggers screen refresh to reload data
- Graceful degradation if watching fails

## Key Design Decisions

### Installation Methods
Two distribution targets:
1. **pipx package** - Clean, isolated install via `pyproject.toml`
2. **Single-file script** - Portable Python script via bundler

### Editor Integration
Uses `$EDITOR` environment variable (defaults to `vi`) for editing:
- Requires app exit/suspend during editing
- Re-runs app after editor closes
- Simple, terminal-native approach

### Secret Masking
Settings display masks sensitive values:
- Keys containing "KEY", "TOKEN", or "SECRET" shown as `••••••••`
- Raw values never displayed in UI

## Implementation Reference

See implementation plan: `docs/plans/2025-01-29-terminal-dashboard.md`

See design document: `docs/plans/2025-01-29-terminal-dashboard-design.md`

The plan is organized into 16 tasks across 3 phases with exact code, commands, and expected outputs for each step.
