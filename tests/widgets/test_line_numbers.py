"""Tests for LineNumbers widget."""

import pytest
from textual.app import App
from textual.widgets import Static


def test_line_numbers_widget_import():
    """Test that LineNumbers widget can be imported."""
    from claude_dashboard.widgets.line_numbers import LineNumbers
    assert LineNumbers is not None


def test_line_numbers_initial_state(app_with_line_numbers):
    """Test that LineNumbers initializes with default state."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)
    assert line_numbers.line_count == 0


def test_line_numbers_set_line_count(app_with_line_numbers):
    """Test that set_line_count updates the display."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)

    # Set to 5 lines
    line_numbers.set_line_count(5)

    # Check that the reactive property updated
    assert line_numbers.line_count == 5

    # Check that the display shows lines 1-5
    expected_text = "1\n2\n3\n4\n5"
    assert line_numbers.renderable.plain == expected_text


def test_line_numbers_reacts_to_line_count_change(app_with_line_numbers):
    """Test that the widget updates display when line_count changes."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)

    # Directly set the reactive property
    line_numbers.line_count = 3

    # Check display updated
    expected_text = "1\n2\n3"
    assert line_numbers.renderable.plain == expected_text


def test_line_handles_zero_lines(app_with_line_numbers):
    """Test that LineNumbers handles zero lines correctly."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)

    line_numbers.set_line_count(0)

    # Should show empty text
    assert line_numbers.renderable.plain == ""


def test_line_numbers_handles_single_line(app_with_line_numbers):
    """Test that LineNumbers handles a single line correctly."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)

    line_numbers.set_line_count(1)

    expected_text = "1"
    assert line_numbers.renderable.plain == expected_text


def test_line_numbers_handles_many_lines(app_with_line_numbers):
    """Test that LineNumbers handles many lines (100+)."""
    line_numbers = app_with_line_numbers.query_one(LineNumbers)

    line_numbers.set_line_count(150)

    # Check first few lines
    text = line_numbers.renderable.plain
    lines = text.split('\n')
    assert lines[0] == "1"
    assert lines[1] == "2"
    assert lines[-1] == "150"


@pytest.fixture
def app_with_line_numbers():
    """Create a test app with LineNumbers widget mounted."""
    from claude_dashboard.widgets.line_numbers import LineNumbers

    class TestApp(App):
        def compose(self):
            yield LineNumbers()

    app = TestApp()
    async with app.run_test() as pilot:
        yield app
