"""Analytics screen showing token usage and cost analytics."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Header
from claude_dashboard.utils.usage_tracker import UsageTracker


class AnalyticsScreen(Vertical):
    """Screen showing token usage and cost analytics."""

    CSS = """
    AnalyticsScreen {
        height: 100%;
    }
    #chart_container {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    .section {
        margin-bottom: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="chart_container"):
            yield Label("", id="total_cost")
            yield Label("", id="daily_chart")
            yield Label("", id="agent_breakdown")

    def on_mount(self):
        """Load and display usage data."""
        container = self.query_one("#chart_container", Vertical)

        # Check if usage data exists
        if UsageTracker.get_usage_data() is None:
            container.remove_children()
            container.mount(Label("[yellow]No usage data found[/yellow]"))
            container.mount(Label(""))
            container.mount(Label("Usage tracking requires:"))
            container.mount(Label("  • ~/.claude/logs/usage.json file"))
            container.mount(Label("  • Or Claude Code to write usage logs"))
            return

        self._load_analytics()

    def _load_analytics(self):
        """Load and render analytics data."""
        # Total cost
        total_cost = UsageTracker.get_total_cost(7)
        self.query_one("#total_cost", Label).update(
            f"[b]TOKEN USAGE (Last 7 Days)[/b]\n"
            f"TOTAL COST: ${total_cost:.2f}"
        )

        # Daily chart
        daily_data = UsageTracker.get_daily_usage(7)
        labels = [d["date"][5:] for d in daily_data]  # Remove year
        values = [d["tokens"] for d in daily_data]

        chart = UsageTracker.render_ascii_chart(values, labels)
        self.query_one("#daily_chart", Label).update(
            f"\n[b]Daily Volume:[/b]\n{chart}"
        )

        # Agent breakdown
        agents = UsageTracker.get_agent_breakdown()
        if agents:
            self._render_agent_table(agents)
        else:
            self.query_one("#agent_breakdown", Label).update(
                "\n[b]Cost by Agent:[/b]\nNo agent data available"
            )

    def _render_agent_table(self, agents: list):
        """Render agent breakdown table."""
        # Sort by token usage
        agents_sorted = sorted(agents, key=lambda x: x["tokens"], reverse=True)

        lines = ["\n[b]Cost by Agent:[/b]"]
        for agent in agents_sorted:
            tokens = agent["tokens"]
            if tokens >= 1000:
                tokens_str = f"{tokens//1000}k"
            else:
                tokens_str = str(tokens)
            lines.append(f"  {agent['id']:20} {tokens_str:>10}")

        self.query_one("#agent_breakdown", Label).update("\n".join(lines))
