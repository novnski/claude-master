"""External editor integration for opening files."""

import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def open_editor(file_path: Path | str) -> None:
    """Open file in user's configured editor.

    Uses $EDITOR env var, defaults to 'vi'.

    Args:
        file_path: Path to file to edit
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    editor = os.environ.get("EDITOR", "vi")

    try:
        result = subprocess.call([editor, str(file_path)])
        if result != 0:
            logger.warning(f"Editor exited with code {result}")
    except FileNotFoundError:
        logger.error(f"Editor '{editor}' not found. Please set $EDITOR or ensure editor is installed.")
    except Exception as e:
        logger.error(f"Failed to open editor: {e}")
