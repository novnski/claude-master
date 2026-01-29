import pytest
from pathlib import Path
from claude_dashboard.config.claude_config import ClaudeConfig


@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock Claude directory with test agents and skills."""
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
    """Test that get_agents returns list of agents with metadata."""
    config = ClaudeConfig(claude_dir=mock_claude_dir)
    agents = config.get_agents()
    assert len(agents) == 1
    assert agents[0]["id"] == "architect"
    assert agents[0]["name"] == "architect"
    assert agents[0]["description"] == "Design agent"


def test_get_skills(mock_claude_dir):
    """Test that get_skills returns list of skills with metadata."""
    config = ClaudeConfig(claude_dir=mock_claude_dir)
    skills = config.get_skills()
    assert len(skills) == 1
    assert skills[0]["id"] == "brainstorming"
    assert skills[0]["name"] == "brainstorming"
    assert skills[0]["description"] == "Generate ideas"
