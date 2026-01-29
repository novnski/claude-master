"""Update checker for claude-code."""

import subprocess


def check_for_update() -> str | None:
    """Check if claude-code has updates available.

    Returns:
        Message if update available, None otherwise
    """
    try:
        result = subprocess.run(
            ["npm", "outdated", "-g", "claude-code"],
            capture_output=True,
            text=True
        )
        if result.returncode == 1:  # outdated packages found
            return "Update available for claude-code"
    except FileNotFoundError:
        pass  # npm not installed
    return None
