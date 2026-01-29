"""Relationships screen showing agent-skill relationships."""

from textual.containers import Vertical
from textual.widgets import Tree
from claude_dashboard.config.claude_config import ClaudeConfig


class RelationshipsScreen(Vertical):
    """Screen showing agent-skill relationships."""

    CSS = """
    RelationshipsScreen {
        height: 100%;
    }
    Tree {
        height: 1fr;
    }
    """

    def compose(self):
        yield Tree("Agents")

    def on_mount(self):
        tree = self.query_one(Tree)
        config = ClaudeConfig()

        for agent in config.get_agents():
            agent_node = tree.root.add(agent["id"])

            if "skills" in agent:
                for skill_id in agent["skills"]:
                    agent_node.add_leaf(f"Skill: {skill_id}")

        tree.root.expand()
