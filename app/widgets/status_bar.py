"""
Bottom status bar.
Displays: filename | save status | autosave | spell errors  (spacer)  theme
"""
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static
from textual import events


class AppStatusBar(Widget):
    """Application status bar shown at the bottom of the screen."""

    filename: reactive[str] = reactive("Untitled", init=False)
    is_saved: reactive[bool] = reactive(True, init=False)
    autosave: reactive[bool] = reactive(False, init=False)

    DEFAULT_CSS = """
    AppStatusBar {
        height: 1;
        dock: bottom;
        background: $primary;
        color: $foreground;
        layout: horizontal;
    }
    AppStatusBar Label, AppStatusBar Static {
        padding: 0 1;
        color: $foreground;
    }
    AppStatusBar .divider {
        color: $primary-lighten-2;
    }
    AppStatusBar #status-spacer {
        width: 1fr;
    }
    AppStatusBar #status-spell {
        padding: 0 2;
    }
    AppStatusBar #status-spell:hover {
        background: $primary-lighten-1;
    }
    AppStatusBar #status-spell.spell-errors {
        color: $error;
    }
    AppStatusBar #status-spell.spell-off {
        color: $primary-lighten-3;
    }
    AppStatusBar #status-theme {
        padding: 0 2;
        background: $primary-darken-1;
    }
    AppStatusBar #status-theme:hover {
        background: $primary-lighten-1;
        color: $foreground;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(self._filename_text, id="status-filename")
        yield Label("\u2502", classes="divider")
        yield Label(self._saved_text,    id="status-saved")
        yield Label("\u2502", classes="divider")
        yield Label(self._autosave_text, id="status-autosave")
        yield Label("\u2502", classes="divider", id="spell-divider")
        yield Label("\u2717 Spell OFF", id="status-spell", classes="spell-off")
        yield Static("",                 id="status-spacer")
        yield Static(f"\U0001f3a8 {self.app.theme}", id="status-theme")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def _filename_text(self) -> str:
        return f"  {self.filename}"

    @property
    def _saved_text(self) -> str:
        return "Saved" if self.is_saved else "Unsaved"

    @property
    def _autosave_text(self) -> str:
        return "Autosave: ON" if self.autosave else "Autosave: OFF"

    # ------------------------------------------------------------------
    # Watchers
    # ------------------------------------------------------------------

    def watch_filename(self, value: str) -> None:
        self.query_one("#status-filename", Label).update(f"  {value}")

    def watch_is_saved(self, value: bool) -> None:
        self.query_one("#status-saved", Label).update(
            "Saved" if value else "Unsaved"
        )

    def watch_autosave(self, value: bool) -> None:
        self.query_one("#status-autosave", Label).update(
            "Autosave: ON" if value else "Autosave: OFF"
        )

    # ------------------------------------------------------------------
    # Spell check status (called by MainScreen)
    # ------------------------------------------------------------------

    def update_spell_status(
        self, enabled: bool, error_count: int = 0
    ) -> None:
        label = self.query_one("#status-spell", Label)
        divider = self.query_one("#spell-divider", Label)
        divider.display = True
        if not enabled:
            label.update("✗ Spell OFF")
            label.remove_class("spell-errors")
            label.add_class("spell-off")
        else:
            label.remove_class("spell-off")
            if error_count == 0:
                label.update("✓ Spelling OK")
                label.remove_class("spell-errors")
            else:
                label.update(f"⚠ {error_count} spelling error{'s' if error_count != 1 else ''}")
                label.add_class("spell-errors")
                label.update(f"\u26a0 {error_count} spelling error{'s' if error_count != 1 else ''}")
                label.add_class("spell-errors")

    # ------------------------------------------------------------------
    # Theme picker — click the theme label to open the picker modal
    # ------------------------------------------------------------------

    def on_click(self, event: events.Click) -> None:
        # Toggle spell check when clicking the spell slot
        spell_label = self.query_one("#status-spell", Label)
        if spell_label.region.contains(event.screen_x, event.screen_y):
            self.app.spell_check_enabled = not self.app.spell_check_enabled  # type: ignore[attr-defined]
            return

        # Open theme picker when clicking the theme label
        theme_label = self.query_one("#status-theme", Static)
        if theme_label.region.contains(event.screen_x, event.screen_y):
            from app.screens.theme_picker import ThemePickerScreen
            def apply_theme(theme: str | None) -> None:
                if theme:
                    theme_label.update(f"\U0001f3a8 {theme}")
            self.app.push_screen(ThemePickerScreen(), apply_theme)
