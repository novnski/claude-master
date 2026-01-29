import pytest
from claude_dashboard.utils.frontmatter import parse_frontmatter


def test_parse_agent_with_frontmatter():
    content = """---
name: architect
description: Design architecture
model: opus
---
This is the body content."""
    result = parse_frontmatter(content)
    assert result["name"] == "architect"
    assert result["description"] == "Design architecture"
    assert result["model"] == "opus"
    assert result["content"] == "This is the body content."


def test_parse_file_without_frontmatter():
    content = "Just plain content"
    result = parse_frontmatter(content)
    assert result["content"] == "Just plain content"
    assert "name" not in result


def test_parse_empty_frontmatter():
    content = """---
---
Body only"""
    result = parse_frontmatter(content)
    assert result["content"] == "Body only"


def test_parse_with_windows_line_endings():
    content = "---\r\nname: test\r\n---\r\nBody content"
    result = parse_frontmatter(content)
    assert result["name"] == "test"
    assert result["content"] == "Body content"


def test_parse_with_multiline_body():
    content = """---
name: test
---
Line 1
Line 2
Line 3"""
    result = parse_frontmatter(content)
    assert result["name"] == "test"
    assert result["content"] == "Line 1\nLine 2\nLine 3"


def test_parse_with_malformed_yaml():
    content = """---
key: value: invalid
---
Body"""
    result = parse_frontmatter(content)
    # Should fall back to content on YAML error
    assert result["content"] == "Body"


def test_parse_empty_body_after_frontmatter():
    content = """---
name: test
---
"""
    result = parse_frontmatter(content)
    assert result["name"] == "test"
    assert result["content"] == ""
