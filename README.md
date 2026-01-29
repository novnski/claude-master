# Claude Master Dashboard

A terminal-based TUI application for managing Claude Code configuration, agents, and skills.

![Dashboard](https://img.shields.io/badge/Textual-TUI-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green)

## Features

- **Agent Management** - View, create, and edit agents with inline editing
- **Skill Browser** - Browse and manage your skills
- **Inline Editor** - Full-screen editor with syntax highlighting (9+ languages)
- **Analytics** - Token usage visualization with ASCII charts
- **Orchestration View** - Tree view of agent hierarchies and skill assignments
- **Theme System** - Dark, light, and high-contrast themes
- **Command Palette** - Quick access to all features (Ctrl+P)
- **Keyboard Shortcuts** - Efficient navigation with number keys and shortcuts
- **Skill Marketplace** - Browse and install community skills

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⭘                          ClaudeDashboard                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ ☰                    │  Agents > Your Agents                              │
│ [●] Agents           │  ┌─────────────────────────────────────────────────┐ │
│ [ ] Skills           │  │ ID            Name         Description         │ │
│ [ ] Settings         │  ├─────────────────────────────────────────────────┤ │
│ [ ] Sessions         │  │ code-reviewer  code-reviewer Expert code review │ │
│ [ ] Analytics        │  │ test-runner    test-runner   Test execution     │ │
│ [ ] Relationships    │  │ architect      architect     Software design    │ │
│ [ ] Marketplace      │  └─────────────────────────────────────────────────┘ │
│                      │                                                       │
│                      │  [Create New Agent]                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation

### One-Line Install (Recommended)

**Just run this - everything is automatic:**

```bash
curl -sSL https://raw.githubusercontent.com/novnski/claude-master/main/install.sh | bash
```

**That's it!** The script will:
- ✓ Check Python version (requires 3.10+)
- ✓ Install all dependencies automatically
- ✓ Detect your shell (bash, zsh, fish)
- ✓ Add `claude-dashboard` command to your PATH
- ✓ Update your shell config automatically
- ✓ Work in new terminal sessions

**Then just open a new terminal and run:**
```bash
claude-dashboard
```

### Manual Install

If you prefer manual installation:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/novnski/claude-master.git
   cd claude-master
   ```

2. **Install dependencies:**
   ```bash
   pip install textual pyyaml watchdog
   ```

3. **Run the dashboard:**
   ```bash
   python -m claude_dashboard
   ```

## Usage

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `?` | Show help |
| `Ctrl+P` | Open command palette |
| `N` | Create new agent |
| `E` | Edit selected |
| `Ctrl+S` | Save |
| `Ctrl+Q` | Cancel/Quit |
| `1-8` | Jump to sidebar items |
| `Esc` | Go back/close modal |

### Navigation

- **Arrow Keys** - Navigate lists and menus
- **Enter** - Select item / Open detail
- **Tab** - Move between fields
- `Ctrl+C` - Quit application

### Creating Agents

1. Press `N` or click "Create New Agent"
2. Enter agent name (ID is auto-generated)
3. Select model (Opus/Sonnet/Haiku)
4. Choose template (Empty, Coder, Analyst)
5. Click "Create & Edit" to finish

### Editing Files

- Click "Edit" on any agent or skill to open the inline editor
- Supports: `.md`, `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.sh`, `.txt`
- Press `Ctrl+S` to save, `Ctrl+Q` to cancel

### Theme Switching

1. Press `Ctrl+P` to open command palette
2. Select "Switch Theme"
3. Choose from: default, light, high_contrast

## Configuration

The dashboard reads from your `~/.claude/` directory:

- **Agents:** `~/.claude/agents/*.md`
- **Skills:** `~/.claude/skills/*/SKILL.md`
- **Settings:** `~/.claude/settings.json`
- **Theme State:** `~/.claude/dashboard-state.json`

## Requirements

- Python 3.10 or higher
- Textual 0.44.0 or higher
- PyYAML
- Watchdog

## Development

```bash
# Run tests
pytest

# Run with debug output
TEXTUAL_DEBUG=1 python -m claude_dashboard

# Create distribution
python -m build
```

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
