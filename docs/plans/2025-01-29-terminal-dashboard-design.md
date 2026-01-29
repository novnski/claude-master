# Claude Master Dashboard - Terminal Edition

**Design Document**
**Date:** 2025-01-29
**Status:** Approved

## Overview

A full-screen terminal-based dashboard for managing Claude Code configuration. Built with Python + Textual, featuring sidebar navigation, live file watching, and direct editing capabilities.

**Goals:**
- Provide terminal-native interface for Claude Code management
- Support browsing, editing, and visualizing agents/skills
- Enable creating new agents and skills
- Monitor active sessions and check for updates

---

## Architecture

**Technology Stack:**
- **Language:** Python 3.10+
- **TUI Framework:** Textual (with textual-dev for development tools)
- **Configuration Source:** ~/.claude/
- **State Management:** Textual's reactive message passing system

**Installation Methods:**
1. **pipx (recommended)** - Clean, isolated installation
2. **Single-file script** - Quick testing without install

---

## Layout Structure

```
+------------------+--------------------------+
|                  |  [Content Area]          |
|   Sidebar        |  - Agent Grid/List        |
|   - Agents       |  - Detail Panel           |
|   - Skills       |  - Editor (when active)   |
|   - Settings     |                          |
|   - Sessions     |                          |
|   - Updates      |                          |
+------------------+--------------------------+
| Status Bar: Active session | Last updated |
+-----------------------------------------------+
```

---

## Components

**Screen Components:**
1. **MainScreen** - Root container with Sidebar + ContentArea
2. **AgentsScreen** - Grid/list of agents with search/filter
3. **AgentDetail** - Individual agent view with edit button
4. **SkillsScreen** - List of skills with descriptions
5. **SkillDetail** - Individual skill view
6. **SettingsScreen** - Settings viewer with masked secrets
7. **SessionsScreen** - Active/recent sessions monitor
8. **RelationshipsScreen** - Text-based tree visualization
9. **EditorModal** - Configurable editor (external or built-in)

**Data Layer:**
```
ClaudeConfig (Singleton)
  ├── load() - reads ~/.claude/
  ├── watch() - file watcher for hot-reload
  ├── get_agents() - cached agent list
  ├── get_skills() - cached skill list
  ├── get_settings() - settings with mask
  └── save(path, content) - write file
```

**File Structure:**
```
src/
├── __main__.py           # entry point (claude-dashboard command)
├── app.py                # ClaudeDashboard app class
├── config/
│   └── claude_config.py  # Claude file watcher/loader
├── screens/
│   ├── __init__.py
│   ├── agents.py         # Agents list & detail
│   ├── skills.py         # Skills list & detail
│   ├── settings.py       # Settings viewer
│   ├── sessions.py       # Sessions monitor
│   └── relationships.py  # Tree visualization
├── widgets/
│   ├── __init__.py
│   └── editor.py         # Editor modal
└── utils/
    ├── __init__.py
    └── frontmatter.py    # YAML parser
```

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| File Not Found | Show empty state with "Create new" option |
| YAML Parse Error | Show inline error with line number |
| Permission Denied | Show warning, suggest fix |
| Watch Fails | Graceful degradation, manual refresh |

---

## Styling

Uses Textual's terminal-native CSS with semantic colors that adapt to terminal themes:
- `$primary` - Accent color
- `$surface` - Panel backgrounds
- `$panel` - Nested backgrounds
- `$success` / `$error` - Status colors

---

## Testing Strategy

**Unit Tests (pytest):**
- YAML frontmatter parsing
- Config loading and caching
- Message handling

**Integration Tests (textual test harness):**
- Screen navigation
- User interactions
- File change reactions

**Manual Testing:**
- Multiple terminal sizes
- Light/dark themes
- Hot-reload verification

---

## Implementation Phases

### Phase 1 - Core (MVP)
- Project setup (Textual app skeleton)
- Sidebar navigation
- Agents list & detail view
- YAML frontmatter parsing
- External editor integration

### Phase 2 - Additional
- Skills list & detail view
- Settings viewer
- File watcher for hot-reload
- Search/filter functionality

### Phase 3 - Advanced
- Relationships visualization (tree view)
- Sessions monitor
- Create new agents/skills
- Update checker

---

## Success Criteria

- [ ] Installable via `pipx install claude-dashboard`
- [ ] Runs as single script without install
- [ ] Browse and view agents/skills
- [ ] Edit files via $EDITOR
- [ ] Hot-reload on file changes
- [ ] Works across terminal sizes and themes
