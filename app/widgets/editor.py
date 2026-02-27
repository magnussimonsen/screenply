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

# Fountain scene headings: lines starting with INT/EXT/etc. or forced with '.'
_SCENE_RE = re.compile(
    r"^(?:INT\.?/EXT\.?|I/E\.?|INT\.?|EXT\.?|\.)[ \t]+.+",
    re.IGNORECASE,
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

    class Notification(Message):
        """Carries a status-bar message from background work."""
        def __init__(self, text: str, error: bool = False) -> None:
            super().__init__()
            self.text = text
            self.error = error

    class TocUpdated(Message):
        """Fired whenever the scene-heading list changes."""
        def __init__(self, scenes: list[tuple[int, str]]) -> None:
            super().__init__()
            self.scenes = scenes  # [(line_number, heading_text), ...]

    DEFAULT_CSS = """
    AppEditor {
        width: 1fr;
        height: 100%;
        /* Desk — slightly darker than the page */
        background: $background;
        padding: 0;
        align: center top;
    }
    AppEditor TextArea {
        /* Page — 72 chars wide:  8 left-margin + 60 content + 4 right-margin */
        width: 72;
        height: 100%;
        background: $surface;
        border: none;
        /* Left indent mimics the 1.5" screenplay margin */
        padding: 1 4 1 8;
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
        # Watch app-level reactives the correct way (self.watch, not watch_app_*)
        self.watch(self.app, "live_preview_enabled", self._on_live_preview_toggled, init=False)
        self.watch(self.app, "spell_check_enabled",  self._run_spell_check,         init=False)
        self.watch(self.app, "spell_language",       self._run_spell_check,         init=False)
        self.watch(self.app, "paper_width",          self._on_paper_width_changed,  init=True)
        self.watch(self.app, "view_mode",            self._on_view_mode_changed,    init=False)


    # ------------------------------------------------------------------
    # Paper width
    # ------------------------------------------------------------------

    def _on_paper_width_changed(self, width: int) -> None:
        """Update the TextArea column width when the paper_width setting changes."""
        if self.app.view_mode == "paper":  # type: ignore
            try:
                ta = self.query_one("#screenplay-textarea", TextArea)
                ta.styles.width = width
            except Exception:
                pass

    def _on_view_mode_changed(self, mode: str) -> None:
        """Switch between full-width web view and fixed-width paper view."""
        try:
            ta = self.query_one("#screenplay-textarea", TextArea)
            if mode == "web":
                ta.styles.width = "1fr"
            else:  # paper
                ta.styles.width = self.app.paper_width  # type: ignore
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Spell checking — public entry point
    # ------------------------------------------------------------------

    def _run_spell_check(self, _=None) -> None:
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
        self.set_timer(0.4, self._scan_toc, name="toc-debounce")
        if self.app.live_preview_enabled:  # type: ignore[attr-defined]
            self.set_timer(1.5, self._do_live_preview, name="live-preview-debounce")

    def _scan_toc(self) -> None:
        """Scan the text for Fountain scene headings and broadcast TocUpdated."""
        text = self.query_one("#screenplay-textarea", TextArea).text
        scenes: list[tuple[int, str]] = []
        for line_no, line in enumerate(text.splitlines()):
            stripped = line.strip()
            if _SCENE_RE.match(stripped):
                # Remove forced-slug dot prefix for display
                label = stripped.lstrip(". \t") if stripped.startswith(".") else stripped
                scenes.append((line_no, label))
        self.post_message(self.TocUpdated(scenes))

    def _on_live_preview_toggled(self, enabled: bool) -> None:
        if enabled:
            self._do_live_preview(open_browser=True)

    # ------------------------------------------------------------------
    # Live HTML preview
    # ------------------------------------------------------------------

    def _do_live_preview(self, open_browser: bool = False) -> None:
        """Build HTML preview in background; optionally open browser."""
        if not self.app.live_preview_enabled:  # type: ignore[attr-defined]
            return
        text = self.query_one("#screenplay-textarea", TextArea).text
        current_path: str = self.app.current_file_path  # type: ignore[attr-defined]
        self.run_worker(
            lambda: self._build_html_preview(text, current_path, open_browser),
            thread=True,
            name="live-preview",
            exclusive=True,
        )

    def _build_html_preview(self, text: str, current_path: str, open_browser: bool) -> None:
        from app.utils.export import fountain_to_html_live, get_export_path
        out_path = get_export_path(current_path, ".preview.html")
        try:
            fountain_to_html_live(text, out_path)
            if open_browser:
                # webbrowser.open must run on the main thread
                url = "file:///" + out_path.replace("\\", "/")
                self.app.call_from_thread(self._open_browser, url)
            self.app.call_from_thread(
                self.post_message, self.Notification("\u2713 Preview updated")
            )
        except Exception as exc:
            self.app.call_from_thread(
                self.post_message, self.Notification(f"Preview error: {exc}", error=True)
            )

    def _open_browser(self, url: str) -> None:
        import webbrowser
        webbrowser.open(url)
