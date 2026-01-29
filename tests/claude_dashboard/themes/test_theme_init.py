"""Tests for theme system initialization."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from claude_dashboard.themes import get_current_theme, set_theme, STATE_FILE


class TestGetCurrentTheme:
    """Tests for get_current_theme function."""

    def test_returns_default_when_no_state_file(self, tmp_path):
        """Test that default theme is returned when state file doesn't exist."""
        with patch('claude_dashboard.themes.STATE_FILE', tmp_path / "nonexistent.json"):
            assert get_current_theme() == "default"

    def test_returns_theme_from_valid_state_file(self, tmp_path):
        """Test that theme is read from valid state file."""
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"theme": "midnight"}))

        with patch('claude_dashboard.themes.STATE_FILE', state_file):
            assert get_current_theme() == "midnight"

    def test_returns_default_when_state_file_missing_theme_key(self, tmp_path):
        """Test that default is returned when state file exists but has no theme key."""
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({"other_key": "value"}))

        with patch('claude_dashboard.themes.STATE_FILE', state_file):
            assert get_current_theme() == "default"

    def test_returns_default_when_state_file_has_invalid_json(self, tmp_path):
        """Test that default is returned when state file contains corrupted JSON."""
        state_file = tmp_path / "state.json"
        state_file.write_text("{invalid json content")

        with patch('claude_dashboard.themes.STATE_FILE', state_file):
            # Should not raise json.JSONDecodeError
            assert get_current_theme() == "default"

    def test_returns_default_when_state_file_has_io_error(self, tmp_path):
        """Test that default is returned when state file cannot be read."""
        # Create a directory instead of a file to cause IOError
        state_file = tmp_path / "state"
        state_file.mkdir()

        with patch('claude_dashboard.themes.STATE_FILE', state_file):
            # Should not raise IOError
            assert get_current_theme() == "default"
