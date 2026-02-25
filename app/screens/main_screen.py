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
from app.state.settings import SUPPORTED_LANGUAGES


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

    def _close_all(self) -> None:
        for dd in self.query(DropdownMenu):
            dd.hide()

    def on_app_menu_bar_toggle_menu(self, event: AppMenuBar.ToggleMenu) -> None:
        dd = self.query_one(f"#dropdown-{event.menu_id}", DropdownMenu)
        currently_visible = dd.display
        self._close_all()
        if not currently_visible:
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
            # View
            case "view-web":
                pass  # TODO
            case "view-paper":
                pass  # TODO
            # Settings
            case "settings-spell-toggle":
                self.app.spell_check_enabled = not self.app.spell_check_enabled  # type: ignore
                self._update_spell_label()
            case "settings-language":
                from app.screens.language_picker import LanguagePickerScreen
                def apply_lang(lang: str | None) -> None:
                    if lang:
                        self.app.spell_language = lang  # type: ignore
                        self._update_spell_label()
                self.app.push_screen(LanguagePickerScreen(), apply_lang)

    def _update_spell_label(self) -> None:
        """Update the Settings menu toggle label to reflect current state."""
        enabled = self.app.spell_check_enabled  # type: ignore
        label = "Disable Spell Check" if enabled else "Enable Spell Check"
        dd = self.query_one("#dropdown-settings", DropdownMenu)
        try:
            item = dd.query("#settings-spell-toggle").first(_MenuItem)
            item.update(label)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Spell check results -> status bar
    # ------------------------------------------------------------------

    def on_app_editor_spell_check_result(
        self, event: AppEditor.SpellCheckResult
    ) -> None:
        status = self.query_one(AppStatusBar)
        status.update_spell_status(event.enabled, event.error_count)
