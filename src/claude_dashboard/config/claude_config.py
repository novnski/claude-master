"""Claude configuration singleton for accessing ~/.claude directory."""

from pathlib import Path
from typing import Any

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
