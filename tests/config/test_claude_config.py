import pytest
from pathlib import Path
from unittest.mock import patch
from claude_dashboard.config.claude_config import ClaudeConfig


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the ClaudeConfig singleton before each test."""
    ClaudeConfig._instance = None
    yield


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


def test_singleton_rejects_different_claude_dir(mock_claude_dir, tmp_path):
    """Test that singleton raises ValueError when initialized with different directory."""
    # First initialization with one directory
    config1 = ClaudeConfig(claude_dir=mock_claude_dir)

    # Create a different directory
    different_dir = tmp_path / "different"
    different_dir.mkdir()

    # Attempting to initialize with a different directory should raise ValueError
    with pytest.raises(ValueError, match="already initialized with"):
        ClaudeConfig(claude_dir=different_dir)


def test_singleton_allows_same_claude_dir(mock_claude_dir):
    """Test that singleton allows reinitialization with the same directory."""
    config1 = ClaudeConfig(claude_dir=mock_claude_dir)
    config2 = ClaudeConfig(claude_dir=mock_claude_dir)

    # Should return the same instance
    assert config1 is config2


def test_get_agents_handles_permission_error(mock_claude_dir):
    """Test that get_agents gracefully handles PermissionError."""
    agents_dir = mock_claude_dir / "agents"

    # Create another file that will raise PermissionError
    unreadable_file = agents_dir / "unreadable.md"
    unreadable_file.write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise PermissionError for the unreadable file
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.name == "unreadable.md":
            raise PermissionError(f"Permission denied: {self}")
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        agents = config.get_agents()

    # Should return only the architect agent from the fixture, not crash
    assert len(agents) == 1
    assert agents[0]["id"] == "architect"


def test_get_agents_handles_unicode_decode_error(mock_claude_dir):
    """Test that get_agents gracefully handles UnicodeDecodeError."""
    agents_dir = mock_claude_dir / "agents"

    # Create another file
    bad_encoding_file = agents_dir / "bad_encoding.md"
    bad_encoding_file.write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise UnicodeDecodeError
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.name == "bad_encoding.md":
            raise UnicodeDecodeError('utf-8', b'\x80', 0, 1, 'invalid start byte')
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        agents = config.get_agents()

    # Should return only the architect agent from the fixture, not crash
    assert len(agents) == 1
    assert agents[0]["id"] == "architect"


def test_get_agents_handles_os_error(mock_claude_dir):
    """Test that get_agents gracefully handles OSError."""
    agents_dir = mock_claude_dir / "agents"

    # Create another file
    error_file = agents_dir / "error.md"
    error_file.write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise OSError
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.name == "error.md":
            raise OSError(f"I/O error: {self}")
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        agents = config.get_agents()

    # Should return only the architect agent from the fixture, not crash
    assert len(agents) == 1
    assert agents[0]["id"] == "architect"


def test_get_skills_handles_permission_error(mock_claude_dir):
    """Test that get_skills gracefully handles PermissionError."""
    skills_dir = mock_claude_dir / "skills"

    # Create another skill with unreadable file
    bad_skill_dir = skills_dir / "bad_skill"
    bad_skill_dir.mkdir()
    (bad_skill_dir / "SKILL.md").write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise PermissionError for the bad skill
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.parent.name == "bad_skill":
            raise PermissionError(f"Permission denied: {self}")
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        skills = config.get_skills()

    # Should return only the brainstorming skill from the fixture, not crash
    assert len(skills) == 1
    assert skills[0]["id"] == "brainstorming"


def test_get_skills_handles_unicode_decode_error(mock_claude_dir):
    """Test that get_skills gracefully handles UnicodeDecodeError."""
    skills_dir = mock_claude_dir / "skills"

    # Create another skill with bad encoding
    bad_skill_dir = skills_dir / "bad_skill"
    bad_skill_dir.mkdir()
    (bad_skill_dir / "SKILL.md").write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise UnicodeDecodeError
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.parent.name == "bad_skill":
            raise UnicodeDecodeError('utf-8', b'\x80', 0, 1, 'invalid start byte')
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        skills = config.get_skills()

    # Should return only the brainstorming skill from the fixture, not crash
    assert len(skills) == 1
    assert skills[0]["id"] == "brainstorming"


def test_get_skills_handles_os_error(mock_claude_dir):
    """Test that get_skills gracefully handles OSError."""
    skills_dir = mock_claude_dir / "skills"

    # Create another skill that will error
    bad_skill_dir = skills_dir / "bad_skill"
    bad_skill_dir.mkdir()
    (bad_skill_dir / "SKILL.md").write_text("content")

    config = ClaudeConfig(claude_dir=mock_claude_dir)

    # Mock read_text to raise OSError
    original_read_text = Path.read_text
    def mock_read_text(self):
        if self.parent.name == "bad_skill":
            raise OSError(f"I/O error: {self}")
        return original_read_text(self)

    with patch.object(Path, 'read_text', mock_read_text):
        skills = config.get_skills()

    # Should return only the brainstorming skill from the fixture, not crash
    assert len(skills) == 1
    assert skills[0]["id"] == "brainstorming"


def test_get_settings_handles_json_decode_error(mock_claude_dir):
    """Test that get_settings gracefully handles JSONDecodeError."""
    import json

    # Create a malformed settings.json file
    settings_file = mock_claude_dir / "settings.json"
    settings_file.write_text('{"invalid": json, "missing": quote}')

    config = ClaudeConfig(claude_dir=mock_claude_dir)
    settings = config.get_settings()

    # Should return an error dict instead of crashing
    assert "error" in settings
    assert "Invalid JSON in settings.json" in settings["error"]


def test_get_settings_masks_sensitive_values(mock_claude_dir):
    """Test that get_settings masks API keys and tokens."""
    # Create a valid settings.json with sensitive values
    settings_file = mock_claude_dir / "settings.json"
    settings_file.write_text('{"env": {"API_KEY": "secret123", "NORMAL_VAR": "value"}}')

    config = ClaudeConfig(claude_dir=mock_claude_dir)
    settings = config.get_settings()

    # API key should be masked
    assert settings["env"]["API_KEY"] == "••••••••"
    # Normal variable should not be masked
    assert settings["env"]["NORMAL_VAR"] == "value"


def test_get_settings_returns_empty_dict_when_missing(mock_claude_dir):
    """Test that get_settings returns empty dict when settings.json doesn't exist."""
    config = ClaudeConfig(claude_dir=mock_claude_dir)
    settings = config.get_settings()

    # Should return empty dict
    assert settings == {}
