"""
Main editor area — the central writing canvas.
Uses Textual's TextArea for input.  When spell checking is enabled
(app.spell_check_enabled) a background worker scans the text after
each change, highlights misspelled words in-place, and posts the
error count to the status bar.
"""
from __future__ import annotations

import re
from collections import defaultdict
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import TextArea
from textual.widgets.text_area import TextAreaTheme
from textual.message import Message
from rich.style import Style

# Token name used in _highlights and registered in the theme
_SPELL_TOKEN = "spell.error"

# Rich style applied to misspelled words — red underline
_SPELL_STYLE = Style(color="red", underline=True)

# TextArea theme that adds only the spell-error style;
# all other values (cursor, selection, etc.) are auto-generated.
_SPELL_THEME = TextAreaTheme(
    name="screenply",
    syntax_styles={_SPELL_TOKEN: _SPELL_STYLE},
)

_WORD_RE = re.compile(
    r"[A-Za-z'\u00C0-\u024F\u00E6\u00F8\u00E5\u00C6\u00D8\u00C5]+"
)


class AppEditor(Widget):
    """The main screenplay editing area."""

    BINDINGS = [
        ("ctrl+d", "add_word_to_dict", "Add word to dictionary"),
    ]

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

    def on_mount(self) -> None:
        ta = self.query_one("#screenplay-textarea", TextArea)
        ta.register_theme(_SPELL_THEME)
        ta.theme = "screenply"

    # ------------------------------------------------------------------
    # Spell checking — public entry point
    # ------------------------------------------------------------------

    def _run_spell_check(self) -> None:
        enabled: bool = self.app.spell_check_enabled  # type: ignore[attr-defined]
        if not enabled:
            self._apply_spell_highlights({}, 0, enabled=False)
            return

        lang: str = self.app.spell_language  # type: ignore[attr-defined]
        text = self.query_one("#screenplay-textarea", TextArea).text

        self.run_worker(
            lambda: self._check_words(text, lang),
            thread=True,
            name="spell-check",
            exclusive=True,
        )

    # ------------------------------------------------------------------
    # Background worker — runs off the main thread
    # ------------------------------------------------------------------

    def _check_words(self, text: str, lang: str) -> None:
        from spellchecker import SpellChecker
        from app.state.settings import is_custom_language

        if is_custom_language(lang):
            from app.resources import RESOURCES_DIR
            import os
            dict_path = os.path.join(RESOURCES_DIR, f"{lang}.json.gz")
            sc = SpellChecker(language=None, local_dictionary=dict_path)
        else:
            sc = SpellChecker(language=lang)

        # Load user-added words so they are never flagged as errors
        from app.state.user_dict import load_user_words
        user_words = load_user_words(lang)
        if user_words:
            sc.word_frequency.load_words(list(user_words))

        # Find all words and check which are misspelled
        all_words = _WORD_RE.findall(text)
        misspelled: set[str] = sc.unknown(all_words)

        # Build highlight map: line -> [(start_col, end_col, token)]
        highlights: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
        for match in _WORD_RE.finditer(text):
            word = match.group()
            if word in misspelled:
                start = match.start()
                line = text[:start].count("\n")
                line_start = text.rfind("\n", 0, start) + 1
                col = start - line_start
                highlights[line].append((col, col + len(word), _SPELL_TOKEN))

        count = len(misspelled)
        self.app.call_from_thread(
            self._apply_spell_highlights, highlights, count, True
        )

    # ------------------------------------------------------------------
    # Main-thread: write highlights into TextArea and refresh
    # ------------------------------------------------------------------

    def _apply_spell_highlights(
        self,
        highlights: dict,
        count: int,
        enabled: bool,
    ) -> None:
        ta = self.query_one("#screenplay-textarea", TextArea)
        ta._highlights.clear()
        for line, spans in highlights.items():
            ta._highlights[line].extend(spans)
        ta._line_cache.clear()
        ta.refresh()
        self.post_message(self.SpellCheckResult(count, enabled=enabled))

    # ------------------------------------------------------------------
    # Triggers
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Add word to dictionary
    # ------------------------------------------------------------------

    def get_word_at_cursor(self) -> str:
        """Return the word under (or touching) the cursor, or ''."""
        ta = self.query_one("#screenplay-textarea", TextArea)
        row, col = ta.cursor_location
        lines = ta.text.split("\n")
        if row >= len(lines):
            return ""
        line = lines[row]
        # Expand left to the start of the word
        start = col
        while start > 0 and _WORD_RE.match(line[start - 1]):
            start -= 1
        # Expand right to the end of the word
        end = col
        while end < len(line) and _WORD_RE.match(line[end]):
            end += 1
        return line[start:end]

    def action_add_word_to_dict(self) -> None:
        """Open the add-word modal pre-filled with the word at the cursor."""
        word = self.get_word_at_cursor()
        from app.screens.add_word_screen import AddWordScreen

        def _on_confirm(result: str | None) -> None:
            if not result:
                return
            lang: str = self.app.spell_language  # type: ignore[attr-defined]
            from app.state.user_dict import add_user_word
            add_user_word(lang, result)
            self._run_spell_check()

        self.app.push_screen(AddWordScreen(word), _on_confirm)

    # ------------------------------------------------------------------
    # Triggers
    # ------------------------------------------------------------------

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Debounce: re-check 600 ms after user stops typing."""
        self.set_timer(0.6, self._run_spell_check, name="spell-debounce")
        if self.app.live_pdf_enabled:  # type: ignore[attr-defined]
            self.set_timer(3.0, self._do_live_pdf, name="live-pdf-debounce")

    def watch_app_spell_check_enabled(self, _: bool) -> None:
        self._run_spell_check()

    def watch_app_spell_language(self, _: str) -> None:
        self._run_spell_check()

    def watch_app_live_pdf_enabled(self, enabled: bool) -> None:
        if enabled:
            self._do_live_pdf()   # build once immediately when turned on

    # ------------------------------------------------------------------
    # Live PDF
    # ------------------------------------------------------------------

    def _do_live_pdf(self) -> None:
        """Build PDF in background and write to the preview/export path."""
        if not self.app.live_pdf_enabled:  # type: ignore[attr-defined]
            return
        text = self.query_one("#screenplay-textarea", TextArea).text
        current_path: str = self.app.current_file_path  # type: ignore[attr-defined]
        self.run_worker(
            lambda: self._build_pdf(text, current_path),
            thread=True,
            name="live-pdf",
            exclusive=True,
        )

    def _build_pdf(self, text: str, current_path: str) -> None:
        from app.utils.export import fountain_to_pdf, get_export_path
        out_path = get_export_path(current_path, ".pdf")
        try:
            fountain_to_pdf(text, out_path)
            self.app.call_from_thread(self._on_pdf_written, out_path)
        except Exception as exc:
            self.app.call_from_thread(
                self.app.notify, f"Live PDF error: {exc}", severity="error", timeout=4
            )

    def _on_pdf_written(self, out_path: str) -> None:
        self.app.notify(f"✓ PDF updated", timeout=2)
