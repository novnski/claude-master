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

### Quick Install (Recommended)

Run the install script directly:

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/claude-master-dashboard/main/install.sh | bash
```

Or download and run:

```bash
wget https://raw.githubusercontent.com/yourusername/claude-master-dashboard/main/install.sh
chmod +x install.sh
./install.sh
```

### Manual Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/claude-master-dashboard.git
   cd claude-master-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install textual pyyaml watchdog
   ```

3. **Run the dashboard:**
   ```bash
   python -m claude_dashboard
   ```

### Optional: Install as pipx package

```bash
pipx install .
```

Then run with:
```bash
claude-dashboard
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
