"""
Modal for adding a word to the user dictionary.

Dismissed with the (possibly edited) word string when confirmed,
or None when cancelled.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical, Horizontal


class AddWordScreen(ModalScreen[str | None]):
    """Ask the user to confirm (or edit) a word before adding it."""

    DEFAULT_CSS = """
    AddWordScreen {
        align: center middle;
    }
    AddWordScreen > Vertical {
        width: 50;
        height: auto;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    AddWordScreen Label#aw-title {
        text-style: bold;
        width: 1fr;
        content-align: center middle;
        margin-bottom: 1;
        color: $foreground;
    }
    AddWordScreen Label#aw-hint {
        color: $foreground;
        margin-bottom: 1;
    }
    AddWordScreen Input {
        margin-bottom: 1;
    }
    AddWordScreen Horizontal {
        height: auto;
        align: center middle;
    }
    AddWordScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Add"),
    ]

    def __init__(self, word: str = "") -> None:
        super().__init__()
        self._initial_word = word

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add to Dictionary", id="aw-title")
            yield Label("Word to add (you can edit it):", id="aw-hint")
            yield Input(value=self._initial_word, id="aw-input")
            with Horizontal():
                yield Button("Add", variant="primary", id="aw-confirm")
                yield Button("Cancel", variant="default", id="aw-cancel")

    def on_mount(self) -> None:
        inp = self.query_one("#aw-input", Input)
        inp.focus()
        # Place cursor at end
        inp.cursor_position = len(inp.value)

    def action_confirm(self) -> None:
        word = self.query_one("#aw-input", Input).value.strip()
        self.dismiss(word if word else None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "aw-confirm":
            self.action_confirm()
        else:
            self.action_cancel()
