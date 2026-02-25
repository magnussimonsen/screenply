"""
Simple file-path input modal — used for both Open and Save As.

Dismissed with the entered path (str) on confirm, or None on cancel.
"""
from __future__ import annotations

import os
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical, Horizontal


class FilePathScreen(ModalScreen[str | None]):
    """Prompt the user for a file path."""

    DEFAULT_CSS = """
    FilePathScreen {
        align: center middle;
    }
    FilePathScreen > Vertical {
        width: 70;
        height: auto;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    FilePathScreen Label#fp-title {
        text-style: bold;
        width: 1fr;
        content-align: center middle;
        margin-bottom: 1;
        color: $foreground;
    }
    FilePathScreen Label#fp-hint {
        color: $foreground;
        margin-bottom: 1;
    }
    FilePathScreen Input {
        margin-bottom: 1;
    }
    FilePathScreen Horizontal {
        height: auto;
        align: center middle;
    }
    FilePathScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, title: str, initial_path: str = "") -> None:
        super().__init__()
        self._title = title
        self._initial_path = initial_path or os.getcwd()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title, id="fp-title")
            yield Label("File path:", id="fp-hint")
            yield Input(value=self._initial_path, id="fp-input")
            with Horizontal():
                yield Button("OK", variant="primary", id="fp-ok")
                yield Button("Cancel", variant="default", id="fp-cancel")

    def on_mount(self) -> None:
        inp = self.query_one("#fp-input", Input)
        inp.focus()
        inp.cursor_position = len(inp.value)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fp-ok":
            path = self.query_one("#fp-input", Input).value.strip()
            self.dismiss(path if path else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Allow pressing Enter in the Input to confirm."""
        path = event.value.strip()
        self.dismiss(path if path else None)
