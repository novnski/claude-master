#!/usr/bin/env python3
"""Bundle claude-dashboard into single Python script for distribution.

This script combines all source modules into a single executable Python file
that can be run directly without installation.
"""

from pathlib import Path
import os
import stat
import base64
import tempfile
import sys


def create_simple_bundle():
    """Create a self-extracting bundle.

    This approach creates a script that extracts the source files to a
    temporary directory and runs them.
    """
    print("Creating self-extracting bundle...")

    # Get the project root directory
    project_root = Path.cwd()
    src_dir = project_root / "src" / "claude_dashboard"
    
    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}")
        sys.exit(1)

    files = list(src_dir.rglob("*"))

    # Read all files and encode them
    file_data = {}
    for file_path in files:
        if file_path.is_file():
            rel_path = str(file_path.relative_to(src_dir))
            content = file_path.read_bytes()
            file_data[rel_path] = base64.b64encode(content).decode("ascii")

    # Build the script
    script_lines = [
        "#!/usr/bin/env python3",
        "# Claude Dashboard - Self-Extracting Bundle",
        "# ",
        "# This is a standalone version of claude-dashboard.",
        "# Before running, install dependencies:",
        "#   pip install textual pyyaml watchdog",
        "# ",
        "# Or use pipx for a complete installation:",
        "#   pipx install claude-dashboard",
        "# ",
        "",
        "import base64",
        "import os",
        "import sys",
        "import tempfile",
        "import shutil",
        "from pathlib import Path",
        "",
        "",
        "# Embedded files (base64 encoded)",
        "_FILES = {",
    ]

    # Add file data
    for rel_path, b64_content in sorted(file_data.items()):
        script_lines.append(f'    "{rel_path}": "{b64_content}",')

    script_lines.extend([
        "}",
        "",
        "",
        "def check_dependencies():",
        '    """Check if required dependencies are installed."""',
        "    missing = []",
        "    for module in ['textual', 'yaml', 'watchdog']:",
        "        try:",
        "            __import__(module)",
        "        except ImportError:",
            "            missing.append(module)",
        "    if missing:",
        "        print('Error: Missing required dependencies:', ', '.join(missing))",
        "        print()",
        "        print('To install dependencies, run:')",
        "        print('  pip install textual pyyaml watchdog')",
        "        print()",
        "        print('Or install claude-dashboard with pipx for a complete setup:')",
        "        print('  pipx install claude-dashboard')",
        "        sys.exit(1)",
        "",
        "",
        "def extract_and_run():",
        '    """Extract files to temp directory and run."""',
        "    check_dependencies()",
        "    ",
        "    temp_dir = Path(tempfile.mkdtemp(prefix='claude-dashboard-'))",
        "    try:",
        "        # Create claude_dashboard directory in temp",
        "        pkg_dir = temp_dir / 'claude_dashboard'",
        "        pkg_dir.mkdir()",
        "        ",
        "        # Extract files",
        "        for rel_path, b64_content in _FILES.items():",
        "            file_path = pkg_dir / rel_path",
        "            file_path.parent.mkdir(parents=True, exist_ok=True)",
        "            file_path.write_bytes(base64.b64decode(b64_content))",
        "",
        "        # Add temp directory to Python path",
        "        sys.path.insert(0, str(temp_dir))",
        "        ",
        "        # Import and run",
        "        from claude_dashboard.__main__ import main",
        "        main()",
        "        ",
        "    finally:",
        "        # Cleanup temp directory",
        "        if temp_dir.exists():",
        "            shutil.rmtree(temp_dir, ignore_errors=True)",
        "",
        "",
        "if __name__ == '__main__':",
        "    extract_and_run()",
    ])

    # Write output
    output_content = "\n".join(script_lines)
    output_path = project_root / "claude-dashboard.py"
    output_path.write_text(output_content, encoding="utf-8")

    # Make executable
    output_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"Created: {output_path}")
    print(f"Size: {len(output_content)} bytes")
    print(f"Files bundled: {len(file_data)}")
    return output_path


if __name__ == "__main__":
    create_simple_bundle()
