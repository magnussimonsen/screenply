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
from app.widgets.sidebar import AppSidebar
from app.widgets.editor import AppEditor
from app.state.settings import SUPPORTED_LANGUAGES  # noqa: F401 (reserved for future use)


class MainScreen(Screen):
    """The primary screen of the application."""

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
        self.watch(self.app, "live_pdf_enabled",    self._on_live_pdf_changed,      init=False)

    def _on_spell_enabled_changed(self, enabled: bool) -> None:
        self._update_spell_label()

    def _on_live_pdf_changed(self, enabled: bool) -> None:
        self._update_live_pdf_label()

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
                self._update_live_pdf_label()   # refresh before showing
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
                pass  # TODO
            case "file-open":
                pass  # TODO
            case "file-save":
                pass  # TODO
            case "file-save-as":
                pass  # TODO
            case "file-quit":
                self.app.exit()
            # Export
            case "file-export-pdf":
                self._export(ext=".pdf")
            case "file-export-html":
                self._export(ext=".html")
            # View
            case "view-web":
                pass  # TODO
            case "view-paper":
                pass  # TODO
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
            case "settings-live-pdf-toggle":
                self.app.live_pdf_enabled = not self.app.live_pdf_enabled  # type: ignore

    def _update_spell_label(self) -> None:
        """Keep the Settings dropdown label in sync with spell-check state."""
        enabled = self.app.spell_check_enabled  # type: ignore
        label = "Turn Off Spell Check" if enabled else "Turn On Spell Check"
        try:
            item = self.query_one("#settings-spell-toggle", _MenuItem)
            item.update(label)
        except Exception:
            pass

    def _update_live_pdf_label(self) -> None:
        """Keep the Settings dropdown label in sync with live-PDF state."""
        enabled = self.app.live_pdf_enabled  # type: ignore
        label = "Turn Off Live PDF" if enabled else "Turn On Live PDF"
        try:
            item = self.query_one("#settings-live-pdf-toggle", _MenuItem)
            item.update(label)
        except Exception:
            pass

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
            self.app.notify(f"Exported: {os.path.basename(out_path)}", timeout=3)
        except Exception as exc:
            self.app.notify(f"Export failed: {exc}", severity="error", timeout=5)

    # ------------------------------------------------------------------
    # Spell check results -> status bar
    # ------------------------------------------------------------------

    def on_app_editor_spell_check_result(
        self, event: AppEditor.SpellCheckResult
    ) -> None:
        status = self.query_one(AppStatusBar)
        status.update_spell_status(event.enabled, event.error_count)
