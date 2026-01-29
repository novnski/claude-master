"""Usage tracking utility for Claude Code analytics."""

from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class UsageTracker:
    """Track and retrieve Claude usage data."""

    USAGE_FILE = Path.home() / ".claude" / "logs" / "usage.json"

    @classmethod
    def get_usage_data(cls) -> Optional[Dict]:
        """Load usage data from file."""
        if not cls.USAGE_FILE.exists():
            return None

        try:
            return json.loads(cls.USAGE_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return None

    @classmethod
    def get_daily_usage(cls, days: int = 7) -> List[Dict]:
        """Get usage data for the last N days."""
        data = cls.get_usage_data()
        if not data:
            return []

        # Generate daily entries
        daily = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily.append({
                "date": date,
                "tokens": data.get("daily", {}).get(date, 0),
                "cost": data.get("costs", {}).get(date, 0.0)
            })

        return list(reversed(daily))

    @classmethod
    def get_agent_breakdown(cls) -> List[Dict]:
        """Get token usage by agent."""
        data = cls.get_usage_data()
        if not data:
            return []

        agents = data.get("agents", {})
        return [
            {"id": agent_id, "tokens": tokens}
            for agent_id, tokens in agents.items()
        ]

    @classmethod
    def get_total_cost(cls, days: int = 7) -> float:
        """Get total cost for the last N days."""
        daily = cls.get_daily_usage(days)
        return sum(day["cost"] for day in daily)

    @classmethod
    def render_ascii_chart(cls, values: List[int], labels: List[str]) -> str:
        """Generate ASCII bar chart from values."""
        if not values:
            return "No data available"

        max_val = max(values) if max(values) > 0 else 1
        lines = []

        for label, value in zip(labels, values):
            # Scale bar to 20 characters max
            bar_length = int((value / max_val) * 20)
            bar = "█" * bar_length

            # Format value with K suffix for thousands
            if value >= 1000:
                value_str = f"{value//1000}k"
            else:
                value_str = str(value)

            lines.append(f"{label:10} {bar:20} {value_str:>6}")

        return "\n".join(lines)
