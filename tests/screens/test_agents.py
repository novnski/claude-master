"""Tests for Agents screen."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from claude_dashboard.screens.agents import AgentDetailScreen
from claude_dashboard.config.claude_config import ClaudeConfig


@pytest.fixture
def agent_data():
    """Create sample agent data."""
    return {
        "id": "test-agent",
        "name": "Test Agent",
        "description": "A test agent for testing",
        "model": "claude-3-5-sonnet-20241022",
        "path": "/tmp/test_agent.py",
        "content": "Test agent content"
    }


@patch('claude_dashboard.screens.agents.open_editor')
def test_agent_detail_screen_edit_button_uses_suspend_not_exit(mock_open_editor, agent_data, tmp_path):
    """Test that edit button uses app.suspend() instead of app.exit()."""
    # Create a temporary file for the agent
    agent_file = tmp_path / "test_agent.py"
    agent_file.write_text("# Test agent content")
    agent_data["path"] = str(agent_file)

    # Create the screen with a mocked app
    screen = AgentDetailScreen(agent_data)

    # Mock the app property
    mock_app = MagicMock()
    mock_app.pop_screen = Mock()
    mock_app.suspend = Mock()
    mock_app.exit = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Create a mock button press event for edit button (no id = edit button)
        mock_button = Mock()
        mock_button.id = None
        event = Mock()
        event.button = mock_button

        # Call the button press handler
        screen.on_button_pressed(event)

        # Verify that pop_screen was called to close the modal
        mock_app.pop_screen.assert_called_once()

        # Verify that app.suspend() was called (NOT app.exit())
        mock_app.suspend.assert_called_once()
        mock_app.exit.assert_not_called()

        # Verify open_editor was called with the correct path
        mock_open_editor.assert_called_once_with(str(agent_file))


@patch('claude_dashboard.screens.agents.open_editor')
def test_agent_detail_screen_close_button_pops_screen(mock_open_editor, agent_data):
    """Test that close button pops the screen."""
    screen = AgentDetailScreen(agent_data)

    # Mock the app property
    mock_app = MagicMock()
    mock_app.pop_screen = Mock()
    mock_app.suspend = Mock()
    mock_app.exit = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Create a mock button press event for close button
        mock_button = Mock()
        mock_button.id = "close"
        event = Mock()
        event.button = mock_button

        # Call the button press handler
        screen.on_button_pressed(event)

        # Verify that pop_screen was called
        mock_app.pop_screen.assert_called_once()

        # Verify that suspend was NOT called (it's the close button)
        mock_app.suspend.assert_not_called()
        mock_app.exit.assert_not_called()

        # Verify open_editor was NOT called
        mock_open_editor.assert_not_called()


def test_agent_detail_screen_edit_button_without_path_shows_error(agent_data):
    """Test that edit button without path shows error notification."""
    # Remove path from agent data
    agent_data_without_path = agent_data.copy()
    agent_data_without_path.pop("path", None)

    screen = AgentDetailScreen(agent_data_without_path)

    # Mock the app property
    mock_app = MagicMock()
    mock_app.pop_screen = Mock()
    mock_app.suspend = Mock()
    mock_app.exit = Mock()
    mock_app.notify = Mock()

    with patch.object(type(screen), 'app', new_callable=lambda: property(lambda self: mock_app)):
        # Create a mock button press event for edit button
        mock_button = Mock()
        mock_button.id = None
        event = Mock()
        event.button = mock_button

        # Call the button press handler
        screen.on_button_pressed(event)

        # Verify that notification was shown
        mock_app.notify.assert_called_once_with(
            "No file path available for this agent",
            severity="error"
        )

        # Verify that pop_screen, suspend, and exit were NOT called
        mock_app.pop_screen.assert_not_called()
        mock_app.suspend.assert_not_called()
        mock_app.exit.assert_not_called()
