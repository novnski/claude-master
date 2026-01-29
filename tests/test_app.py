"""Tests for ClaudeDashboard app."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from claude_dashboard.app import ClaudeDashboard
from claude_dashboard.config.claude_config import ClaudeConfig


@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock Claude directory with test agents and skills."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    return tmp_path


def test_on_unmount_stops_observer(mock_claude_dir):
    """Test that on_unmount properly stops and joins the observer thread."""
    # Create app with mocked ClaudeConfig
    with patch('claude_dashboard.app.ClaudeConfig') as mock_config_class:
        mock_config = Mock(spec=ClaudeConfig)
        mock_config_class.return_value = mock_config

        # Create a mock observer
        mock_observer = Mock()
        mock_observer.is_alive.return_value = True
        mock_config.start_watching.return_value = mock_observer

        # Create and mount the app
        app = ClaudeDashboard()
        app.on_mount()

        # Verify observer was started
        assert hasattr(app, '_observer')
        assert app._observer is not None

        # Unmount the app
        app.on_unmount()

        # Verify observer was stopped and joined with timeout
        mock_observer.is_alive.assert_called_once()
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once_with(timeout=5.0)


def test_on_unmount_handles_no_observer():
    """Test that on_unmount handles case where observer doesn't exist."""
    app = ClaudeDashboard()

    # Should not raise exception even if _observer doesn't exist
    app.on_unmount()


def test_on_unmount_handles_dead_observer(mock_claude_dir):
    """Test that on_unmount handles case where observer is already dead."""
    with patch('claude_dashboard.app.ClaudeConfig') as mock_config_class:
        mock_config = Mock(spec=ClaudeConfig)
        mock_config_class.return_value = mock_config

        # Create a mock observer that is not alive
        mock_observer = Mock()
        mock_observer.is_alive.return_value = False
        mock_config.start_watching.return_value = mock_observer

        app = ClaudeDashboard()
        app.on_mount()

        # Unmount should not try to stop a dead observer
        app.on_unmount()

        # stop and join should not be called
        mock_observer.stop.assert_not_called()
        mock_observer.join.assert_not_called()
