"""
Modal for setting the paper (editor) width.

Dismissed with the new integer width when confirmed,
or None when cancelled.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical, Horizontal

# Default limits (can be overridden per-instance)
_DEFAULT_MIN = 10
_DEFAULT_MAX = 200


class PaperWidthScreen(ModalScreen[int | None]):
    """Generic integer-width picker dialog."""

    DEFAULT_CSS = """
    PaperWidthScreen {
        align: center middle;
    }
    PaperWidthScreen > Vertical {
        width: 50;
        height: auto;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    PaperWidthScreen Label#pw-title {
        text-style: bold;
        width: 1fr;
        content-align: center middle;
        margin-bottom: 1;
        color: $foreground;
    }
    PaperWidthScreen Label#pw-hint {
        color: $foreground;
        margin-bottom: 1;
    }
    PaperWidthScreen Label#pw-error {
        color: $error;
        height: 1;
        margin-bottom: 1;
    }
    PaperWidthScreen Input {
        margin-bottom: 1;
    }
    PaperWidthScreen Horizontal {
        height: auto;
        align: center middle;
    }
    PaperWidthScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        current_width: int = 72,
        title: str = "Set Paper Width",
        min_width: int = _DEFAULT_MIN,
        max_width: int = _DEFAULT_MAX,
    ) -> None:
        super().__init__()
        self._current_width = current_width
        self._title = title
        self._min_width = min_width
        self._max_width = max_width

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title, id="pw-title")
            yield Label(
                f"Enter column width ({self._min_width}\u2013{self._max_width}). "
                f"Current: {self._current_width}",
                id="pw-hint",
            )
            yield Input(value=str(self._current_width), id="pw-input")
            yield Label("", id="pw-error")
            with Horizontal():
                yield Button("Apply", variant="primary", id="pw-confirm")
                yield Button("Cancel", variant="default", id="pw-cancel")

    def on_mount(self) -> None:
        inp = self.query_one("#pw-input", Input)
        inp.focus()
        inp.cursor_position = len(inp.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pw-confirm":
            self._try_confirm()
        elif event.button.id == "pw-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:  # Enter key
        self._try_confirm()

    def _try_confirm(self) -> None:
        raw = self.query_one("#pw-input", Input).value.strip()
        try:
            value = int(raw)
        except ValueError:
            self._show_error("Please enter a whole number.")
            return
        if not (self._min_width <= value <= self._max_width):
            self._show_error(f"Width must be between {self._min_width} and {self._max_width}.")
            return
        self.dismiss(value)

    def _show_error(self, msg: str) -> None:
        self.query_one("#pw-error", Label).update(msg)

    def action_cancel(self) -> None:
        self.dismiss(None)
