"""Tests for ShortcutsHelpScreen."""

import pytest
from claude_dashboard.screens.shortcuts_help import ShortcutsHelpScreen


def test_shortcuts_help_shortcuts_dict():
    """Test that SHORTCUTS dict has expected structure."""
    shortcuts = ShortcutsHelpScreen.SHORTCUTS

    # Check categories exist
    assert "Navigation" in shortcuts
    assert "Actions" in shortcuts
    assert "Editor" in shortcuts

    # Check that each category has a list of tuples
    for category, shortcut_list in shortcuts.items():
        assert isinstance(shortcut_list, list)
        for item in shortcut_list:
            assert isinstance(item, tuple)
            assert len(item) == 2
            key, desc = item
            assert isinstance(key, str)
            assert isinstance(desc, str)


def test_shortcuts_help_css_defined():
    """Test that CSS is properly defined."""
    screen = ShortcutsHelpScreen()
    assert screen.CSS is not None
    assert "ShortcutsHelpScreen" in screen.CSS
    assert "#help_container" in screen.CSS


def test_shortcuts_help_expected_shortcuts():
    """Test that expected shortcuts are defined."""
    shortcuts = ShortcutsHelpScreen.SHORTCUTS

    # Check for essential shortcuts
    all_shortcuts = []
    for category_shortcuts in shortcuts.values():
        all_shortcuts.extend(category_shortcuts)

    # Check that key shortcuts exist
    shortcut_keys = [k for k, _ in all_shortcuts]
    assert "?" in shortcut_keys  # Help shortcut
    assert "Ctrl+P" in shortcut_keys  # Command palette
    assert "Ctrl+S" in shortcut_keys  # Save
    assert "Ctrl+Q" in shortcut_keys  # Quit


def test_shortcuts_help_has_compose_method():
    """Test that compose method exists."""
    screen = ShortcutsHelpScreen()
    assert hasattr(screen, 'compose')
    assert callable(screen.compose)


def test_shortcuts_help_has_button_handler():
    """Test that button press handler is defined."""
    screen = ShortcutsHelpScreen()
    assert hasattr(screen, 'on_button_pressed')
    assert callable(screen.on_button_pressed)


def test_shortcuts_help_screen_is_modal():
    """Test that ShortcutsHelpScreen is a modal screen."""
    from textual.screen import ModalScreen
    assert issubclass(ShortcutsHelpScreen, ModalScreen)


def test_shortcuts_help_shortcuts_content():
    """Test that shortcuts have meaningful content."""
    shortcuts = ShortcutsHelpScreen.SHORTCUTS

    # Each shortcut should have a non-empty key and description
    for category, shortcut_list in shortcuts.items():
        for key, desc in shortcut_list:
            assert len(key) > 0, f"Empty key in {category}"
            assert len(desc) > 0, f"Empty description for key '{key}' in {category}"
