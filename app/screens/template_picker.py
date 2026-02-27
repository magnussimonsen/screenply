"""
Modal for picking a screenplay template language.

Dismissed with the chosen filename (relative to example_script/),
or None when cancelled.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical, Horizontal
from textual import events


_TEMPLATES: list[tuple[str, str]] = [
    ("English",   "template_en.fountain"),
    ("Norwegian", "template_no.fountain"),
]


class TemplatePickerScreen(ModalScreen[str | None]):
    """Ask the user which language template to load."""

    DEFAULT_CSS = """
    TemplatePickerScreen {
        align: center middle;
    }
    TemplatePickerScreen > Vertical {
        width: 44;
        height: auto;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    TemplatePickerScreen Label#tp-title {
        text-style: bold;
        width: 1fr;
        content-align: center middle;
        margin-bottom: 1;
        color: $foreground;
    }
    TemplatePickerScreen Button {
        width: 1fr;
        margin-bottom: 1;
    }
    TemplatePickerScreen #tp-cancel {
        margin-top: 0;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Load Screenplay Template", id="tp-title")
            for i, (label, filename) in enumerate(_TEMPLATES):
                yield Button(label, id=f"tp-{i}", name=filename)
            yield Button("Cancel", variant="default", id="tp-cancel")

    def on_mount(self) -> None:
        # Focus the first template button
        self.query(Button).first().focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tp-cancel":
            self.dismiss(None)
            return
        self.dismiss(event.button.name)

    def action_cancel(self) -> None:
        self.dismiss(None)
