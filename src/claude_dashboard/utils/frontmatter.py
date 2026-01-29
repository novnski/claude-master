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


def update_frontmatter(content: str, updates: dict[str, Any]) -> str:
    """Update YAML frontmatter in markdown content.

    Args:
        content: Raw markdown content with optional YAML frontmatter
        updates: Dict of fields to update in frontmatter

    Returns:
        Updated markdown content with modified frontmatter
    """
    # Normalize line endings
    normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')

    match = re.match(r'^---\n(.*?)\n---\n([\s\S]*)', normalized_content, re.DOTALL)
    body_text = ""

    if match:
        frontmatter_text = match.group(1)
        body_text = match.group(2)
        try:
            metadata = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            metadata = {}
    else:
        # No frontmatter exists, start with empty metadata
        metadata = {}
        # Check if there's an empty frontmatter case
        empty_match = re.match(r'^---\n---\n([\s\S]*)', normalized_content, re.DOTALL)
        if empty_match:
            body_text = empty_match.group(1)
        else:
            body_text = normalized_content

    # Apply updates
    metadata.update(updates)

    # Build new frontmatter without trailing '...'
    import io
    output = io.StringIO()
    yaml.dump(metadata, output, default_flow_style=False, sort_keys=False)
    new_frontmatter = output.getvalue().rstrip()
    if new_frontmatter.endswith('...'):
        new_frontmatter = new_frontmatter[:-3].rstrip()

    return f"---\n{new_frontmatter}\n---\n{body_text}"
