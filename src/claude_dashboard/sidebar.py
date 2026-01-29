"""Custom widgets for Claude Dashboard."""

from textual.widgets import OptionList
from textual.message import Message


class Sidebar(OptionList):
    """A sidebar navigation widget wrapping OptionList.

    This widget provides a simplified API for sidebar navigation,
    emitting Highlighted and Selected messages with string items
    instead of Option objects.
    """

    class Highlighted(Message):
        """Emitted when a sidebar item is highlighted."""

        def __init__(self, item: str) -> None:
            self.item = item
            super().__init__()

    class Selected(Message):
        """Emitted when a sidebar item is selected."""

        def __init__(self, item: str) -> None:
            self.item = item
            super().__init__()

    def __init__(self, *items: str, **kwargs) -> None:
        """Initialize sidebar with string items.

        Args:
            *items: String items to add to the sidebar
            **kwargs: Additional arguments passed to OptionList
        """
        super().__init__(*items, **kwargs)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Convert OptionList highlight to Sidebar highlight."""
        self.post_message(self.Highlighted(str(event.option.prompt)))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Convert OptionList selection to Sidebar selection."""
        self.post_message(self.Selected(str(event.option.prompt)))
