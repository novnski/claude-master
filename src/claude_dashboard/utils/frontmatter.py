import re
import yaml
from typing import Any


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content with optional YAML frontmatter

    Returns:
        Dict with frontmatter fields + 'content' key for body text
    """
    # Normalize line endings for cross-platform compatibility
    normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')

    match = re.match(r'^---\n(.*?)\n---\n([\s\S]*)', normalized_content, re.DOTALL)
    if not match:
        # Try empty frontmatter case (no content between --- markers)
        match = re.match(r'^---\n---\n([\s\S]*)', normalized_content, re.DOTALL)
        if match:
            return {"content": match.group(1)}
        return {"content": content}

    frontmatter_text = match.group(1)
    body_text = match.group(2)

    try:
        metadata = yaml.safe_load(frontmatter_text) or {}
        metadata["content"] = body_text
        return metadata
    except yaml.YAMLError:
        return {"content": body_text}
