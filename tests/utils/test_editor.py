"""Tests for editor utility module."""

import logging
from pathlib import Path
from unittest.mock import patch
import pytest

from claude_dashboard.utils.editor import open_editor


class TestOpenEditorLogging:
    """Test that open_editor uses logging instead of print."""

    def test_logs_error_when_file_not_found(self, tmp_path, caplog):
        """Should log error when file doesn't exist."""
        non_existent = tmp_path / "does_not_exist.txt"

        with caplog.at_level(logging.ERROR):
            open_editor(non_existent)

        assert "File not found" in caplog.text
        assert str(non_existent) in caplog.text

    def test_logs_warning_when_editor_exits_with_nonzero(self, tmp_path, caplog):
        """Should log warning when editor exits with nonzero code."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("subprocess.call") as mock_call:
            mock_call.return_value = 1
            with caplog.at_level(logging.WARNING):
                open_editor(test_file)

        assert "exited with code 1" in caplog.text

    def test_logs_error_when_editor_not_found(self, tmp_path, caplog):
        """Should log error when editor executable is not found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch.dict("os.environ", {"EDITOR": "nonexistent_editor_xyz"}):
            with patch("subprocess.call", side_effect=FileNotFoundError):
                with caplog.at_level(logging.ERROR):
                    open_editor(test_file)

        assert "not found" in caplog.text
        assert "nonexistent_editor_xyz" in caplog.text

    def test_logs_error_on_generic_exception(self, tmp_path, caplog):
        """Should log error on generic exception."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch("subprocess.call", side_effect=RuntimeError("test error")):
            with caplog.at_level(logging.ERROR):
                open_editor(test_file)

        assert "Failed to open editor" in caplog.text
        assert "test error" in caplog.text
