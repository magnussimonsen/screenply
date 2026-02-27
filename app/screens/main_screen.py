"""
Main screen — composes the top-level layout.
Handles all menu actions and routes spell-check results to the status bar.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal

from app.widgets.menu_bar import (
    AppMenuBar, DropdownMenu, _MenuItem,
    FILE_ITEMS, VIEW_ITEMS, SETTINGS_ITEMS,
)
from app.widgets.status_bar import AppStatusBar
from app.widgets.sidebar import AppSidebar, _TocEntry
from app.widgets.editor import AppEditor
from app.state.settings import SUPPORTED_LANGUAGES  # noqa: F401 (reserved for future use)


class MainScreen(Screen):
    """The primary screen of the application."""

    BINDINGS = [
        ("ctrl+n", "new_file",  "New"),
        ("ctrl+o", "open_file", "Open"),
        ("ctrl+s", "save_file", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield AppMenuBar()
        with Horizontal(id="main-content"):
            yield AppSidebar()
            yield AppEditor()
        yield AppStatusBar()
        yield DropdownMenu(FILE_ITEMS,     col=0,  id="dropdown-file")
        yield DropdownMenu(VIEW_ITEMS,     col=8,  id="dropdown-view")
        yield DropdownMenu(SETTINGS_ITEMS, col=16, id="dropdown-settings")

    # ------------------------------------------------------------------
    # Menu toggles
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        """Register watchers on app-level reactives after DOM is ready."""
        self.watch(self.app, "spell_check_enabled", self._on_spell_enabled_changed, init=False)
        self.watch(self.app, "live_preview_enabled", self._on_live_preview_changed,  init=False)

    def _on_spell_enabled_changed(self, enabled: bool) -> None:
        self._update_spell_label()

    def _on_live_preview_changed(self, enabled: bool) -> None:
        self._update_live_preview_label()

    def _close_all(self) -> None:
        for dd in self.query(DropdownMenu):
            dd.hide()

    def on_app_menu_bar_toggle_menu(self, event: AppMenuBar.ToggleMenu) -> None:
        dd = self.query_one(f"#dropdown-{event.menu_id}", DropdownMenu)
        currently_visible = dd.display
        self._close_all()
        if not currently_visible:
            if event.menu_id == "settings":
                self._update_spell_label()
                self._update_live_preview_label()   # refresh before showing
            dd.show()

    # ------------------------------------------------------------------
    # Menu item actions
    # ------------------------------------------------------------------

    def on__menu_item_selected(self, event: _MenuItem.Selected) -> None:
        self._close_all()
        self._handle_item(event.item_id)

    def _handle_item(self, item_id: str) -> None:
        match item_id:
            # File
            case "file-new":
                self._file_new()
            case "file-open":
                self._file_open()
            case "file-load-big-fish":
                self._load_example_script()
            case "file-load-template":
                self._load_template()
            case "file-save":
                self._file_save()
            case "file-save-as":
                self._file_save_as()
            case "file-quit":
                self.app.exit()
            # Export
            case "file-export-pdf":
                self._export(ext=".pdf")
            case "file-export-html":
                self._export(ext=".html")
            # View
            case "view-web":
                self.app.view_mode = "web"  # type: ignore
            case "view-paper":
                self.app.view_mode = "paper"  # type: ignore
            # Settings
            case "settings-spell-toggle":
                self.app.spell_check_enabled = not self.app.spell_check_enabled  # type: ignore
            case "settings-language":
                from app.screens.language_picker import LanguagePickerScreen
                def apply_lang(lang: str | None) -> None:
                    if lang:
                        self.app.spell_language = lang  # type: ignore
                self.app.push_screen(LanguagePickerScreen(), apply_lang)
            case "settings-add-word":
                # Delegate to the editor — it uses the word at the cursor
                self.query_one(AppEditor).action_add_word_to_dict()
            case "settings-remove-word":
                from app.state.user_dict import load_user_words, remove_user_word
                from app.screens.remove_word_screen import RemoveWordScreen
                lang: str = self.app.spell_language  # type: ignore
                words = list(load_user_words(lang))
                def _on_remove(word: str | None) -> None:
                    if word:
                        remove_user_word(lang, word)
                        self.query_one(AppEditor)._run_spell_check()
                        self._flash(f"Removed \u2018{word}\u2019 from dictionary")
                self.app.push_screen(RemoveWordScreen(words), _on_remove)
            case "settings-live-pdf-toggle":
                self.app.live_preview_enabled = not self.app.live_preview_enabled  # type: ignore
            case "settings-paper-width":
                from app.screens.paper_width_screen import PaperWidthScreen
                current = self.app.paper_width  # type: ignore
                def apply_width(width: int | None) -> None:
                    if width is not None:
                        self.app.paper_width = width  # type: ignore
                self.app.push_screen(
                    PaperWidthScreen(current, title="Set Paper Width", min_width=40, max_width=200),
                    apply_width,
                )
            case "settings-sidebar-width":
                from app.screens.paper_width_screen import PaperWidthScreen
                current = self.app.sidebar_width  # type: ignore
                def apply_sidebar_width(width: int | None) -> None:
                    if width is not None:
                        self.app.sidebar_width = width  # type: ignore
                self.app.push_screen(
                    PaperWidthScreen(current, title="Set Sidebar Width", min_width=10, max_width=60),
                    apply_sidebar_width,
                )

    def _update_spell_label(self) -> None:
        """Keep the Settings dropdown label in sync with spell-check state."""
        enabled = self.app.spell_check_enabled  # type: ignore
        label = "Turn Off Spell Check" if enabled else "Turn On Spell Check"
        try:
            item = self.query_one("#settings-spell-toggle", _MenuItem)
            item.update(label)
        except Exception:
            pass

    def _update_live_preview_label(self) -> None:
        """Keep the Settings dropdown label in sync with live-preview state."""
        enabled = self.app.live_preview_enabled  # type: ignore
        label = "Turn Off Live HTML Preview" if enabled else "Turn On Live HTML Preview"
        try:
            item = self.query_one("#settings-live-pdf-toggle", _MenuItem)
            item.update(label)
        except Exception:
            pass

    def _load_example_script(self) -> None:
        import os
        from textual.widgets import TextArea
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "example_script", "Big-Fish.fountain"
        )
        path = os.path.normpath(path)
        try:
            text = open(path, encoding="utf-8").read()
            self.query_one("#screenplay-textarea", TextArea).load_text(text)
            self.app.current_file_path = path  # type: ignore
            self._flash("Loaded: Big Fish")
            self.call_after_refresh(lambda p=path: self.query_one(AppStatusBar).set_file(p, saved=True))
        except Exception as exc:
            self._flash(f"Could not load Big Fish: {exc}", error=True)

    def _load_template(self) -> None:
        import os
        from textual.widgets import TextArea
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "example_script", "template.fountain"
        )
        path = os.path.normpath(path)
        try:
            text = open(path, encoding="utf-8").read()
            self.query_one("#screenplay-textarea", TextArea).load_text(text)
            self.app.current_file_path = ""  # type: ignore  — treat as unsaved new doc
            self._flash("Loaded: Screenplay Template")
            self.call_after_refresh(lambda: self.query_one(AppStatusBar).set_file("", saved=False))
        except Exception as exc:
            self._flash(f"Could not load template: {exc}", error=True)

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _file_new(self) -> None:
        from textual.widgets import TextArea
        self.query_one("#screenplay-textarea", TextArea).load_text("")
        self.app.current_file_path = ""  # type: ignore
        self.call_after_refresh(lambda: self.query_one(AppStatusBar).set_file("", saved=True))

    def _file_open(self) -> None:
        import os
        from textual.widgets import TextArea
        current: str = self.app.current_file_path  # type: ignore
        initial = current if current else os.getcwd()

        def _dialog() -> None:
            from app.utils.dialogs import ask_open_path
            path = ask_open_path(initial)
            if not path:
                return
            try:
                text = open(path, encoding="utf-8").read()
                def _apply() -> None:
                    self.query_one("#screenplay-textarea", TextArea).load_text(text)
                    self.app.current_file_path = path  # type: ignore
                    self._flash(f"Opened: {os.path.basename(path)}")
                    self.call_after_refresh(lambda p=path: self.query_one(AppStatusBar).set_file(p, saved=True))
                self.app.call_from_thread(_apply)
            except Exception as exc:
                self.app.call_from_thread(
                    self._flash, f"Could not open file: {exc}", True
                )
        self.run_worker(_dialog, thread=True, name="open-dialog")

    def _file_save(self) -> None:
        current: str = self.app.current_file_path  # type: ignore
        if current:
            self._write_file(current)
        else:
            self._file_save_as()

    def _file_save_as(self) -> None:
        import os
        current: str = self.app.current_file_path  # type: ignore
        initial = current if current else os.path.join(os.getcwd(), "script.fountain")

        def _dialog() -> None:
            from app.utils.dialogs import ask_save_as_path
            path = ask_save_as_path(initial)
            if not path:
                return
            if not os.path.splitext(path)[1]:
                path += ".fountain"
            self.app.call_from_thread(self._write_file, path)
        self.run_worker(_dialog, thread=True, name="save-as-dialog")

    def _write_file(self, path: str) -> None:
        import os
        text = self.query_one("#screenplay-textarea").text  # type: ignore[attr-defined]
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            self.app.current_file_path = path  # type: ignore
            self.query_one(AppStatusBar).set_file(path, saved=True)
            self._flash(f"Saved: {os.path.basename(path)}")
        except Exception as exc:
            self._flash(f"Could not save: {exc}", error=True)

    # ------------------------------------------------------------------
    # Track unsaved changes
    # ------------------------------------------------------------------

    def on_text_area_changed(self, event) -> None:  # type: ignore[override]
        self.query_one(AppStatusBar).is_saved = False

    # ------------------------------------------------------------------
    # Table of Contents
    # ------------------------------------------------------------------

    def on_app_editor_toc_updated(self, event: AppEditor.TocUpdated) -> None:
        """Forward fresh scene list to the sidebar."""
        self.query_one(AppSidebar).update_toc(event.scenes)

    def on__toc_entry_selected(self, event: _TocEntry.Selected) -> None:
        """Jump the editor cursor to the selected scene heading."""
        from textual.widgets import TextArea
        ta = self.query_one("#screenplay-textarea", TextArea)
        ta.move_cursor((event.line_no, 0))
        ta.focus()

    # ------------------------------------------------------------------
    # Keyboard action handlers (bound in app.py)
    # ------------------------------------------------------------------

    def action_new_file(self) -> None:
        self._file_new()

    def action_open_file(self) -> None:
        self._file_open()

    def action_save_file(self) -> None:
        self._file_save()

    def _export(self, ext: str) -> None:
        """Export the current editor text to PDF or HTML and open it."""
        import os
        from app.utils.export import get_export_path, fountain_to_pdf, fountain_to_html
        text = self.query_one("#screenplay-textarea").text  # type: ignore[attr-defined]
        out_path = get_export_path(self.app.current_file_path, ext)  # type: ignore
        try:
            if ext == ".pdf":
                fountain_to_pdf(text, out_path)
            else:
                fountain_to_html(text, out_path)
            os.startfile(out_path)
            self._flash(f"Exported: {os.path.basename(out_path)}")
        except Exception as exc:
            self._flash(f"Export failed: {exc}", error=True)

    # ------------------------------------------------------------------
    # Spell check results -> status bar
    # ------------------------------------------------------------------

    def on_app_editor_spell_check_result(
        self, event: AppEditor.SpellCheckResult
    ) -> None:
        status = self.query_one(AppStatusBar)
        status.update_spell_status(event.enabled, event.error_count)

    def on_app_editor_notification(
        self, event: AppEditor.Notification
    ) -> None:
        """Route editor notifications (e.g. live PDF updates) to status bar."""
        self._flash(event.text, error=event.error)

    # ------------------------------------------------------------------
    # Inline notification helper
    # ------------------------------------------------------------------

    def _flash(self, text: str, error: bool = False) -> None:
        """Show *text* in the status bar notice slot."""
        try:
            self.query_one(AppStatusBar).flash_message(text, error=error)
        except Exception:
            pass  # status bar not yet mounted (e.g. during tests)
