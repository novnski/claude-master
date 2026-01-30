"""Claude configuration singleton for accessing ~/.claude directory."""

import copy
import json
import time
import threading
from pathlib import Path
from typing import Any, Callable
from textual.message import Message

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from claude_dashboard.utils.frontmatter import parse_frontmatter


class ClaudeConfig:
    """Singleton for accessing Claude Code configuration."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, claude_dir: Path | None = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, claude_dir: Path | None = None):
        claude_dir = claude_dir or Path.home() / ".claude"

        if self._initialized:
            if self.claude_dir != claude_dir:
                raise ValueError(
                    f"ClaudeConfig already initialized with {self.claude_dir}, "
                    f"cannot reinitialize with {claude_dir}"
                )
            return

        self.claude_dir = claude_dir
        self._initialized = True
        # Cache with TTL (time-to-live)
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 5  # seconds
        self._cache_lock = threading.Lock()

    def _get_cached(self, key: str) -> Any | None:
        """Get cached data if still valid."""
        with self._cache_lock:
            if key in self._cache:
                timestamp = self._cache_timestamps.get(key, 0)
                if time.time() - timestamp < self._cache_ttl:
                    return self._cache[key]
            return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Set cached data with current timestamp."""
        with self._cache_lock:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()

    def invalidate_cache(self) -> None:
        """Clear all cached data."""
        with self._cache_lock:
            self._cache.clear()
            self._cache_timestamps.clear()

    def get_agents(self) -> list[dict[str, Any]]:
        """Get all agents from ~/.claude/agents/*.md"""
        cached = self._get_cached("agents")
        if cached is not None:
            return cached

        agents_dir = self.claude_dir / "agents"
        if not agents_dir.exists():
            return []

        agents = []
        for file in agents_dir.glob("*.md"):
            try:
                data = parse_frontmatter(file.read_text())
                data["id"] = file.stem
                data["path"] = str(file)
                agents.append(data)
            except (OSError, PermissionError, UnicodeDecodeError):
                # Skip files that can't be read
                continue

        self._set_cached("agents", agents)
        return agents

    def get_skills(self) -> list[dict[str, Any]]:
        """Get all skills from ~/.claude/skills/*/SKILL.md"""
        cached = self._get_cached("skills")
        if cached is not None:
            return cached

        skills_dir = self.claude_dir / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for item in skills_dir.iterdir():
            if item.is_dir() or item.is_symlink():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    try:
                        data = parse_frontmatter(skill_file.read_text())
                        data["id"] = item.name
                        data["path"] = str(skill_file)
                        skills.append(data)
                    except (OSError, PermissionError, UnicodeDecodeError):
                        # Skip files that can't be read
                        continue

        self._set_cached("skills", skills)
        return skills

    def get_settings(self) -> dict[str, Any]:
        """Get settings with sensitive values masked."""
        cached = self._get_cached("settings")
        if cached is not None:
            return cached

        settings_file = self.claude_dir / "settings.json"
        if not settings_file.exists():
            return {}

        try:
            with open(settings_file) as f:
                settings = json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in settings.json: {e}"}

        # Create a copy before masking to avoid modifying original
        settings = copy.copy(settings)  # Shallow copy is enough for masking

        # Mask API keys and tokens
        if "env" in settings:
            for key in settings["env"]:
                if any(word in key.upper() for word in ["KEY", "TOKEN", "SECRET"]):
                    settings["env"][key] = "••••••••"

        self._set_cached("settings", settings)
        return settings

    def start_watching(self, callback: Callable[[], None]) -> Observer:
        """Start watching for config changes.

        Args:
            callback: Function to call when config changes

        Returns:
            Observer instance that can be stopped later
        """
        observer = Observer()
        handler = ConfigWatcher(callback)
        observer.schedule(handler, str(self.claude_dir), recursive=True)
        observer.start()
        return observer


class ConfigChanged(Message):
    """Emitted when Claude config changes."""


class ConfigWatcher(FileSystemEventHandler):
    """Watches for changes to Claude config files with debouncing."""

    def __init__(self, callback: Callable[[], None], debounce_seconds: float = 0.5):
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self._pending = False
        self._lock = threading.Lock()
        self._timer = None

    def on_modified(self, event):
        """Handle file modification events with debouncing."""
        if event.src_path.endswith(".md") or event.src_path.endswith(".json"):
            self._trigger_callback()

    def _trigger_callback(self):
        """Trigger callback with debouncing."""
        with self._lock:
            if self._pending:
                return
            self._pending = True
            # Cancel any existing timer
            if self._timer:
                self._timer.cancel()
            # Start new timer
            self._timer = threading.Timer(self.debounce_seconds, self._run_callback)
            self._timer.start()

    def _run_callback(self):
        """Execute the callback and reset pending state."""
        with self._lock:
            self._pending = False
            self._timer = None
        self.callback()

    def stop(self):
        """Stop the debounce timer."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
