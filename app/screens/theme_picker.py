"""
Theme picker modal screen.
Opened from the status bar; displays all built-in themes in a list.
"""
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.widgets.option_list import Option
from textual.containers import Vertical
from textual.theme import BUILTIN_THEMES


class ThemePickerScreen(ModalScreen):
    """Modal that lets the user pick a Textual theme."""

    DEFAULT_CSS = """
    ThemePickerScreen {
        align: center middle;
    }
    ThemePickerScreen #picker-container {
        width: 40;
        height: auto;
        max-height: 26;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
    }
    ThemePickerScreen #picker-title {
        text-align: center;
        color: $foreground;
        padding-bottom: 1;
    }
    ThemePickerScreen OptionList {
        background: $panel;
        border: none;
        height: auto;
        max-height: 20;
    }
    """

    def compose(self) -> ComposeResult:
        themes = list(BUILTIN_THEMES.keys())
        current = self.app.theme

        with Vertical(id="picker-container"):
            yield Label("🎨  Select Theme", id="picker-title")
            yield OptionList(
                *[
                    Option(
                        f"{'▶ ' if t == current else '  '}{t}",
                        id=t,
                    )
                    for t in themes
                ],
                id="theme-list",
            )

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        self.app.theme = event.option.id
        self.dismiss(event.option.id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
