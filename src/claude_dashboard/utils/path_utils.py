"""Path utilities for safe file operations."""

import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and unsafe characters.

    Args:
        filename: The filename to sanitize

    Returns:
        A safe filename with path traversal removed and unsafe characters replaced
    """
    # First, extract just the filename component (remove any path)
    filename = Path(filename).name

    # Replace unsafe characters with underscores
    # Keep alphanumeric, dashes, underscores, and dots
    safe_name = re.sub(r"[^\w\-_.]", "_", filename)

    # Remove leading dots (hidden files) and dashes
    safe_name = safe_name.lstrip(".-")

    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"

    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100]

    return safe_name


def safe_path_join(base_dir: Path, *paths: str) -> Path:
    """Safely join paths, ensuring result stays within base_dir.

    Args:
        base_dir: The base directory that must contain the result
        *paths: Path components to join

    Returns:
        A Path that is guaranteed to be within base_dir

    Raises:
        ValueError: If the resulting path would escape base_dir
    """
    base_dir = base_dir.resolve()

    # Sanitize each path component
    sanitized = [sanitize_filename(p) for p in paths]

    # Join paths
    result = base_dir.joinpath(*sanitized)

    # Resolve and verify it's within base_dir
    try:
        result = result.resolve()
        result.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Path '{paths}' would escape base directory '{base_dir}'")

    return result
