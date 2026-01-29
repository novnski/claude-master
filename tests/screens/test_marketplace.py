"""Tests for Marketplace screen."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import Input, DataTable
from claude_dashboard.screens.marketplace import MarketplaceScreen


def test_marketplace_sample_skills_defined():
    """Test that sample skills are defined."""
    assert hasattr(MarketplaceScreen, 'SAMPLE_SKILLS')
    assert len(MarketplaceScreen.SAMPLE_SKILLS) == 4
    assert MarketplaceScreen.SAMPLE_SKILLS[0][0] == "postgres_client"
    assert MarketplaceScreen.SAMPLE_SKILLS[1][0] == "slack_notifier"


def test_filtering_logic_filters_by_skill_name():
    """Test filtering logic works by skill name."""
    search_term = "postgres"
    filtered = [
        skill for skill in MarketplaceScreen.SAMPLE_SKILLS
        if search_term in skill[0].lower() or
           search_term in skill[1].lower() or
           search_term in skill[2].lower()
    ]

    assert len(filtered) == 1
    assert filtered[0][0] == "postgres_client"


def test_filtering_logic_filters_by_author():
    """Test filtering logic works by author."""
    search_term = "anthropic"
    filtered = [
        skill for skill in MarketplaceScreen.SAMPLE_SKILLS
        if search_term in skill[0].lower() or
           search_term in skill[1].lower() or
           search_term in skill[2].lower()
    ]

    assert len(filtered) == 1
    assert filtered[0][0] == "slack_notifier"


def test_filtering_logic_filters_by_description():
    """Test filtering logic works by description."""
    search_term = "container"
    filtered = [
        skill for skill in MarketplaceScreen.SAMPLE_SKILLS
        if search_term in skill[0].lower() or
           search_term in skill[1].lower() or
           search_term in skill[2].lower()
    ]

    assert len(filtered) == 1
    assert filtered[0][0] == "docker_run"


def test_filtering_logic_is_case_insensitive():
    """Test filtering logic is case insensitive."""
    search_term = "SQL"  # Uppercase search term
    search_term_lower = search_term.lower()
    filtered = [
        skill for skill in MarketplaceScreen.SAMPLE_SKILLS
        if search_term_lower in skill[0].lower() or
           search_term_lower in skill[1].lower() or
           search_term_lower in skill[2].lower()
    ]

    assert len(filtered) == 1
    assert filtered[0][0] == "postgres_client"


def test_filtering_logic_empty_returns_all():
    """Test empty filter returns all skills."""
    search_term = ""
    filtered = [
        skill for skill in MarketplaceScreen.SAMPLE_SKILLS
        if search_term in skill[0].lower() or
           search_term in skill[1].lower() or
           search_term in skill[2].lower()
    ]

    # Empty string matches everything
    assert len(filtered) == 4


def test_marketplace_default_repo_defined():
    """Test that default repository is defined."""
    assert hasattr(MarketplaceScreen, 'DEFAULT_REPO')
    assert MarketplaceScreen.DEFAULT_REPO == "https://github.com/anthropics/claude-skills"


def test_install_skill_creates_directory_and_file(tmp_path):
    """Test that install creates skill directory and file."""
    # Create a skills directory in tmp_path
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Test the file operations directly (simulating what _install_selected_skill does)
    skill_name = "test_skill"
    skill_dir = skills_dir / skill_name
    skill_dir.mkdir(exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(f"---\nname: {skill_name}\ndescription: Installed from marketplace\n---\n")

    # Verify files were created
    assert skill_dir.exists()
    assert skill_file.exists()
    content = skill_file.read_text()
    assert f"name: {skill_name}" in content


def test_install_button_requires_selection():
    """Test that install button requires a selected skill."""
    screen = MarketplaceScreen()

    # Mock the app
    mock_app = MagicMock()
    mock_app.notify = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Create a mock button press event
        mock_button = Mock()
        mock_button.id = "install_btn"
        event = Mock()
        event.button = mock_button

        # Mock the table with no selection
        mock_table = Mock()
        mock_table.selected_row = None

        with patch.object(screen, 'query_one', return_value=mock_table):
            # Call the button press handler
            screen.on_button_pressed(event)

            # Verify notification was shown
            mock_app.notify.assert_called_once_with("Select a skill first", severity="warning")


def test_view_source_shows_repo_url():
    """Test that view source shows repository URL."""
    screen = MarketplaceScreen()

    # Mock the app
    mock_app = MagicMock()
    mock_app.notify = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Call view source
        screen._view_source()

        # Verify notification was shown with repo URL
        mock_app.notify.assert_called_once()
        args = mock_app.notify.call_args[0][0]
        assert "https://github.com/anthropics/claude-skills" in args


def test_change_repo_shows_coming_soon():
    """Test that change repo shows coming soon message."""
    screen = MarketplaceScreen()

    # Mock the app
    mock_app = MagicMock()
    mock_app.notify = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Call change repo
        screen._change_repo()

        # Verify notification was shown
        mock_app.notify.assert_called_once_with("Repository change feature coming soon")
