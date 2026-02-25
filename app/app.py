"""
Main Textual App class for Screenply.
"""
from textual.app import App
from textual.reactive import reactive

from app.screens.main_screen import MainScreen
from app.state.settings import DEFAULT_LANGUAGE


class ScreenplyApp(App):
    """Screenply — a terminal screenwriting application."""

    CSS_PATH = "app.tcss"    # relative to this file's directory

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    # ------------------------------------------------------------------
    # App-wide settings (reactive so widgets can watch for changes)
    # ------------------------------------------------------------------
    spell_check_enabled: reactive[bool] = reactive(False)
    spell_language: reactive[str] = reactive(DEFAULT_LANGUAGE)

    def on_mount(self) -> None:
        self.push_screen(MainScreen())
