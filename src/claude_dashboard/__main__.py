import sys
import argparse

from claude_dashboard.app import ClaudeDashboard


def uninstall() -> None:
    """Uninstall the Claude Dashboard application."""
    import shutil
    import subprocess
    from pathlib import Path

    # Check if running under pipx
    pipx_env = Path.home() / ".local" / "pipx" / "venvs" / "claude-dashboard"
    is_pipx = pipx_env.exists()

    if is_pipx:
        print("Uninstalling Claude Dashboard (installed via pipx)...")
        try:
            subprocess.run(["pipx", "uninstall", "claude-dashboard"], check=True)
            print("Uninstalled successfully!")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Note: Could not run pipx uninstall automatically.")
            print("Please run: pipx uninstall claude-dashboard")
            return

    # Check if we can find the installation location
    try:
        import claude_dashboard
        module_path = Path(claude_dashboard.__file__).parent.parent.parent
        print(f"Installation location: {module_path}")

        if module_path.exists() and "site-packages" in str(module_path):
            print("\nUninstalling via pip...")
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "claude-dashboard", "-y"],
                check=True
            )
            print("Uninstalled successfully!")
        else:
            print("\nThis appears to be a development installation.")
            print("To remove, simply delete the source directory:")
            print(f"  rm -rf {module_path}")
    except Exception as e:
        print(f"Could not determine installation method: {e}")
        print("\nManual uninstall options:")
        print("  pipx uninstall claude-dashboard   # if installed via pipx")
        print("  pip uninstall claude-dashboard    # if installed via pip")
        print("  rm -rf <source-dir>               # if running from source")


def main():
    parser = argparse.ArgumentParser(
        prog="claude-dashboard",
        description="Terminal dashboard for managing Claude Code configuration"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall the Claude Dashboard application"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="claude-dashboard 0.1.0"
    )

    args = parser.parse_args()

    if args.uninstall:
        uninstall()
        return

    app = ClaudeDashboard()
    app.run()


if __name__ == "__main__":
    main()
