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

    # Currently open file path (empty string = unsaved new document)
    current_file_path: reactive[str] = reactive("")

    # Live preview — rebuild HTML automatically while the user writes
    live_preview_enabled: reactive[bool] = reactive(False)

    # Paper view — width of the editor column (in terminal columns)
    paper_width: reactive[int] = reactive(72)

    # Sidebar width (in terminal columns)
    sidebar_width: reactive[int] = reactive(28)

    # View mode — "paper" (fixed-width) or "web" (full-width)
    view_mode: reactive[str] = reactive("paper")

    def on_mount(self) -> None:
        self.push_screen(MainScreen())
