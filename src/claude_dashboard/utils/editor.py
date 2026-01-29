"""External editor integration for opening files."""

import os
import subprocess
from pathlib import Path


def open_editor(file_path: Path | str) -> None:
    """Open file in user's configured editor.

    Uses $EDITOR env var, defaults to 'vi'.

    Args:
        file_path: Path to file to edit
    """
    editor = os.environ.get("EDITOR", "vi")
    file_path = Path(file_path)

    # Validate file exists
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return

    try:
        result = subprocess.call([editor, str(file_path)])
        if result != 0:
            print(f"Editor exited with code {result}")
    except FileNotFoundError:
        print(f"Error: Editor '{editor}' not found. Please set $EDITOR or ensure editor is installed.")
    except Exception as e:
        print(f"Error: Failed to open editor: {e}")
