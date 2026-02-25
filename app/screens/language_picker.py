"""
Language picker modal — lets the user choose a spell-check language.
"""
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.widgets.option_list import Option
from textual.containers import Vertical

from app.state.settings import SUPPORTED_LANGUAGES


class LanguagePickerScreen(ModalScreen):
    """Modal for selecting the spell-check language."""

    DEFAULT_CSS = """
    LanguagePickerScreen {
        align: center middle;
    }
    LanguagePickerScreen #lang-container {
        width: 36;
        height: auto;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
    }
    LanguagePickerScreen #lang-title {
        text-align: center;
        color: $foreground;
        padding-bottom: 1;
    }
    LanguagePickerScreen OptionList {
        background: $panel;
        border: none;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        current = self.app.spell_language  # type: ignore[attr-defined]
        with Vertical(id="lang-container"):
            yield Label("🌐  Spell Check Language", id="lang-title")
            yield OptionList(
                *[
                    Option(
                        f"{'▶ ' if code == current else '  '}"
                        f"{name} ({code})",
                        id=code,
                    )
                    for code, name in SUPPORTED_LANGUAGES.items()
                ],
                id="lang-list",
            )

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        self.dismiss(event.option.id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
