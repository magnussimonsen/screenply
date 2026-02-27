"""
Modal for removing a word from the user dictionary.

Shows the full list of words for the current language.
Dismissed with the selected word string, or None when cancelled.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListView, ListItem, Static
from textual.containers import Vertical, Horizontal


class RemoveWordScreen(ModalScreen[str | None]):
    """Let the user pick a word to remove from the dictionary."""

    DEFAULT_CSS = """
    RemoveWordScreen {
        align: center middle;
    }
    RemoveWordScreen > Vertical {
        width: 50;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    RemoveWordScreen Label#rw-title {
        text-style: bold;
        width: 1fr;
        content-align: center middle;
        margin-bottom: 1;
        color: $foreground;
    }
    RemoveWordScreen Label#rw-hint {
        color: $foreground;
        margin-bottom: 1;
    }
    RemoveWordScreen ListView {
        height: auto;
        max-height: 20;
        border: solid $primary-darken-1;
        margin-bottom: 1;
    }
    RemoveWordScreen Horizontal {
        height: auto;
        align: center middle;
    }
    RemoveWordScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, words: list[str]) -> None:
        super().__init__()
        self._words = sorted(words)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Remove from Dictionary", id="rw-title")
            if self._words:
                yield Label("Select a word to remove:", id="rw-hint")
                yield ListView(
                    *[ListItem(Static(w), name=w) for w in self._words],
                    id="rw-list",
                )
            else:
                yield Label(
                    "Your dictionary is empty — nothing to remove.",
                    id="rw-hint",
                )
            with Horizontal():
                if self._words:
                    yield Button("Remove", variant="error", id="rw-confirm")
                yield Button("Cancel", variant="default", id="rw-cancel")

    def on_mount(self) -> None:
        if self._words:
            self.query_one("#rw-list", ListView).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rw-confirm":
            self._try_remove()
        else:
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Double-click / Enter on a list item confirms immediately
        self.dismiss(event.item.name)

    def _try_remove(self) -> None:
        lv = self.query_one("#rw-list", ListView)
        if lv.highlighted_child is not None:
            self.dismiss(lv.highlighted_child.name)

    def action_cancel(self) -> None:
        self.dismiss(None)
