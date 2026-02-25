"""
Main editor area — the central writing canvas.
Uses Textual's TextArea for input.  When spell checking is enabled
(app.spell_check_enabled) a background worker scans the text after
each change and posts the misspelled-word count to the status bar.
"""
from __future__ import annotations

import re
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import TextArea
from textual.message import Message


class AppEditor(Widget):
    """The main screenplay editing area."""

    # Posted whenever the spell-check count changes so the status bar
    # can update without the editor needing a direct reference to it.
    class SpellCheckResult(Message):
        def __init__(self, error_count: int, enabled: bool) -> None:
            super().__init__()
            self.error_count = error_count
            self.enabled = enabled

    DEFAULT_CSS = """
    AppEditor {
        width: 1fr;
        height: 100%;
        background: $surface;
        padding: 0;
    }
    AppEditor TextArea {
        width: 100%;
        height: 100%;
        background: $surface;
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield TextArea(
            id="screenplay-textarea",
            language=None,
            show_line_numbers=False,
        )

    # ------------------------------------------------------------------
    # Spell checking
    # ------------------------------------------------------------------

    def _run_spell_check(self) -> None:
        """Run spell check on current text; post result message."""
        enabled: bool = self.app.spell_check_enabled  # type: ignore[attr-defined]
        if not enabled:
            self.post_message(self.SpellCheckResult(0, enabled=False))
            return

        lang: str = self.app.spell_language  # type: ignore[attr-defined]
        text = self.query_one("#screenplay-textarea", TextArea).text

        # Run in a worker thread so we don't freeze the UI
        self.run_worker(
            lambda: self._check_words(text, lang),
            thread=True,
            name="spell-check",
            exclusive=True,
        )

    def _check_words(self, text: str, lang: str) -> None:
        from spellchecker import SpellChecker
        sc = SpellChecker(language=lang)
        words = re.findall(r"[A-Za-z'\u00C0-\u024F]+", text)
        misspelled = sc.unknown(words)
        count = len(misspelled)
        # Post result back on the main thread via call_from_thread
        self.app.call_from_thread(
            self.post_message, self.SpellCheckResult(count, enabled=True)
        )

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Re-run spell check 600 ms after the user stops typing."""
        # Cancel any pending check and schedule a new one
        self.set_timer(0.6, self._run_spell_check, name="spell-debounce")

    # Watch app-level settings so we re-check when they change
    def watch_app_spell_check_enabled(self, _: bool) -> None:
        self._run_spell_check()

    def watch_app_spell_language(self, _: str) -> None:
        self._run_spell_check()
