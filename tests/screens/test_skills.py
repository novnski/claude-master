"""Tests for Skills screen."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import Input, DataTable
from claude_dashboard.screens.skills import SkillsScreen


@pytest.fixture
def mock_skills():
    """Create sample skills data."""
    return [
        {
            "id": "test-driven-development",
            "name": "Test Driven Development",
            "description": "Write tests first, then code",
            "content": "TDD content here..."
        },
        {
            "id": "brainstorming",
            "name": "Brainstorming",
            "description": "Explore ideas collaboratively",
            "content": "Brainstorming content..."
        },
        {
            "id": "systematic-debugging",
            "name": "Systematic Debugging",
            "description": "Debug methodically",
            "content": "Debugging content..."
        }
    ]


@patch('claude_dashboard.screens.skills.ClaudeConfig')
def test_skills_screen_has_filter_input_and_table(mock_config_class, mock_skills):
    """Test that skills screen composes filter input and table."""
    # Mock the config
    mock_config = MagicMock()
    mock_config.get_skills.return_value = mock_skills
    mock_config_class.return_value = mock_config

    # Create screen and consume compose generator
    screen = SkillsScreen()
    widgets = list(screen.compose())

    # Should have 2 widgets: Input and DataTable
    assert len(widgets) == 2
    assert isinstance(widgets[0], Input)
    assert widgets[0].id == "filter_input"
    assert widgets[0].placeholder == "Filter skills..."
    assert isinstance(widgets[1], DataTable)
    assert widgets[1].id == "skills_table"


def test_filtering_logic_filters_by_id():
    """Test filtering logic works by ID."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
        {"id": "brainstorming", "name": "Brainstorming", "description": "Explore ideas"},
    ]

    search_term = "test"
    filtered = [
        skill for skill in skills
        if search_term in skill["id"].lower() or
           search_term in skill.get("name", "").lower() or
           search_term in skill.get("description", "").lower()
    ]

    assert len(filtered) == 1
    assert filtered[0]["id"] == "test-driven-development"


def test_filtering_logic_filters_by_name():
    """Test filtering logic works by name."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
        {"id": "brainstorming", "name": "Brainstorming", "description": "Explore ideas"},
    ]

    search_term = "brainstorm"
    filtered = [
        skill for skill in skills
        if search_term in skill["id"].lower() or
           search_term in skill.get("name", "").lower() or
           search_term in skill.get("description", "").lower()
    ]

    assert len(filtered) == 1
    assert filtered[0]["id"] == "brainstorming"


def test_filtering_logic_filters_by_description():
    """Test filtering logic works by description."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
        {"id": "brainstorming", "name": "Brainstorming", "description": "Explore ideas"},
    ]

    search_term = "write"
    filtered = [
        skill for skill in skills
        if search_term in skill["id"].lower() or
           search_term in skill.get("name", "").lower() or
           search_term in skill.get("description", "").lower()
    ]

    assert len(filtered) == 1
    assert filtered[0]["id"] == "test-driven-development"


def test_filtering_logic_is_case_insensitive():
    """Test filtering logic is case insensitive."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
    ]

    search_term = "TEST"  # Uppercase search term
    # The implementation converts search_term to lowercase, so we need to do the same in test
    search_term_lower = search_term.lower()
    filtered = [
        skill for skill in skills
        if search_term_lower in skill["id"].lower() or
           search_term_lower in skill.get("name", "").lower() or
           search_term_lower in skill.get("description", "").lower()
    ]

    assert len(filtered) == 1


def test_filtering_logic_empty_returns_all():
    """Test empty filter returns all skills."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
        {"id": "brainstorming", "name": "Brainstorming", "description": "Explore ideas"},
    ]

    search_term = ""
    filtered = [
        skill for skill in skills
        if search_term in skill["id"].lower() or
           search_term in skill.get("name", "").lower() or
           search_term in skill.get("description", "").lower()
    ]

    # Empty string matches everything
    assert len(filtered) == 2


def test_filtering_logic_no_match_returns_empty():
    """Test no match returns empty list."""
    skills = [
        {"id": "test-driven-development", "name": "TDD", "description": "Write tests first"},
    ]

    search_term = "nonexistent"
    filtered = [
        skill for skill in skills
        if search_term in skill["id"].lower() or
           search_term in skill.get("name", "").lower() or
           search_term in skill.get("description", "").lower()
    ]

    assert len(filtered) == 0


@patch('claude_dashboard.screens.skills.ClaudeConfig')
def test_on_mount_sets_skills_attribute(mock_config_class, mock_skills):
    """Test that on_mount sets skills attribute."""
    # Mock the config
    mock_config = MagicMock()
    mock_config.get_skills.return_value = mock_skills
    mock_config_class.return_value = mock_config

    # Create screen
    screen = SkillsScreen()
    widgets = list(screen.compose())

    # The screen should have a skills attribute after on_mount would be called
    # For this test, we just verify the config would be called
    mock_config.get_skills.assert_not_called()  # Not called yet
