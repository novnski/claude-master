"""Relationships screen showing agent-skill relationships as tree view."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Tree, Button, Label
from claude_dashboard.widgets.custom_header import CustomHeader
from claude_dashboard.config.claude_config import ClaudeConfig


class RelationshipsScreen(Vertical):
    """Tree view of agent hierarchy and delegation."""

    CSS = """
    RelationshipsScreen {
        height: 100%;
    }
    #tree_container {
        height: 1fr;
        padding: 1;
    }
    Tree {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield CustomHeader()
        yield Label("[b]VISUAL HIERARCHY[/b]")
        with Vertical(id="tree_container"):
            yield Tree("root (User)", id="agent_tree")

        with Horizontal():
            yield Button("EDIT SELECTED NODE", id="edit_node")
            yield Button("REFRESH", id="refresh")

    def on_mount(self):
        """Build and display agent hierarchy."""
        tree = self.query_one("#agent_tree", Tree)
        config = ClaudeConfig()

        # Get all agents
        agents = config.get_agents()

        # Build hierarchy - root is user
        for agent in agents:
            agent_label = f"ag_{agent.get('id', '?')}: {agent.get('name', 'Unknown')}"
            agent_node = tree.root.add_leaf(agent_label)

            # Add skills as child nodes
            if "skills" in agent and agent["skills"]:
                for skill_id in agent["skills"]:
                    agent_node.add_leaf(f"skill: {skill_id}")

            # Add model info
            model = agent.get("model", "N/A")
            agent_node.add_leaf(f"model: {model}")

        tree.root.expand()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh":
            self._refresh_tree()
        elif event.button.id == "edit_node":
            self._edit_selected_node()

    def _refresh_tree(self):
        """Refresh the tree from config."""
        tree = self.query_one("#agent_tree", Tree)
        tree.clear()
        self.on_mount()

    def _edit_selected_node(self):
        """Open editor for selected agent."""
        tree = self.query_one("#agent_tree", Tree)

        if not tree.cursor_node:
            self.app.notify("No node selected", severity="error")
            return

        node_label = str(tree.cursor_node.label)

        # Check if this is an agent node (starts with "ag_")
        if "ag_" in node_label:
            # Extract agent ID
            agent_id = node_label.split(":")[0].replace("ag_", "")

            config = ClaudeConfig()
            agents = config.get_agents()
            agent = next((a for a in agents if a["id"] == agent_id), None)

            if agent and "path" in agent:
                from claude_dashboard.screens.editor import EditorScreen
                self.app.push_screen(EditorScreen(agent["path"]))
            else:
                self.app.notify(f"Cannot find file for agent {agent_id}", severity="error")
        else:
            self.app.notify("Select an agent node to edit", severity="warning")
