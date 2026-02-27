"""
Top menu bar — File and View menus.

Textual's Button widget has opinionated internal CSS that fights theme
variables, so we use Static widgets for the top-level labels and catch
mouse clicks manually.  Dropdown panels are owned by MainScreen so they
can float over the full layout.
"""
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static
from textual import events


# ---------------------------------------------------------------------------
# Dropdown panel (owned by MainScreen, not by AppMenuBar)
# ---------------------------------------------------------------------------

FILE_ITEMS = [
    ("New Script",      "file-new"),
    ("Open Script…",    "file-open"),
    ("Load Big Fish",   "file-load-big-fish"),
    ("Load Template",   "file-load-template"),
    None,
    ("Save Script",     "file-save"),
    ("Save Script As…", "file-save-as"),
    None,
    ("Export as PDF",   "file-export-pdf"),
    ("Export as HTML",  "file-export-html"),
    None,
    ("Quit",            "file-quit"),
]

VIEW_ITEMS = [
    ("Web View",   "view-web"),
    ("Paper View", "view-paper"),
]

SETTINGS_ITEMS = [
    ("Turn On Spell Check",       "settings-spell-toggle"),
    None,
    ("Select Language…",          "settings-language"),
    ("Add Word to Dictionary…",   "settings-add-word"),
    ("Remove Word from Dictionary…", "settings-remove-word"),
    None,
    ("Turn On Live HTML Preview",  "settings-live-pdf-toggle"),
    None,
    ("Set Paper Width…",           "settings-paper-width"),
    ("Set Sidebar Width…",         "settings-sidebar-width"),
]


class _MenuItem(Static):
    """A single clickable item inside a dropdown."""

    class Selected(Message):
        def __init__(self, item_id: str) -> None:
            super().__init__()
            self.item_id = item_id

    def __init__(self, text: str, item_id: str, **kwargs):
        super().__init__(text, **kwargs)
        self._item_id = item_id

    def on_click(self, event: events.Click) -> None:
        event.stop()
        self.post_message(self.Selected(self._item_id))


class DropdownMenu(Widget):
    """Floating dropdown panel.  Mount on the Screen, not on the MenuBar."""

    DEFAULT_CSS = """
    DropdownMenu {
        layer: overlay;
        background: $panel;
        border: solid $primary;
        width: 24;
        height: auto;
        display: none;
        padding: 0;
    }
    DropdownMenu _MenuItem {
        width: 100%;
        height: 1;
        background: transparent;
        color: $foreground;
        padding: 0 2;
    }
    DropdownMenu _MenuItem:hover {
        background: $primary;
        color: $foreground;
    }
    DropdownMenu Static.sep {
        height: 1;
        color: $primary-darken-1;
        padding: 0 1;
    }
    """

    def __init__(self, items: list, col: int, **kwargs):
        super().__init__(**kwargs)
        self._items = items
        self._col = col

    def compose(self) -> ComposeResult:
        for item in self._items:
            if item is None:
                yield Static("─" * 22, classes="sep")
            else:
                label, item_id = item
                yield _MenuItem(label, item_id=item_id, id=item_id)

    def show(self) -> None:
        self.styles.offset = (self._col, 1)
        self.display = True
        self.focus()

    def hide(self) -> None:
        self.display = False


# ---------------------------------------------------------------------------
# Clickable menu label (avoids Button's internal CSS)
# ---------------------------------------------------------------------------

class _MenuLabel(Static):
    """A plain text label that posts ToggleMenu when clicked."""

    class Clicked(Message):
        def __init__(self, menu_id: str, col: int) -> None:
            super().__init__()
            self.menu_id = menu_id
            self.col = col

    def __init__(self, text: str, menu_id: str, **kwargs):
        super().__init__(text, **kwargs)
        self._menu_id = menu_id

    def on_click(self, event: events.Click) -> None:
        event.stop()
        self.post_message(self.Clicked(self._menu_id, self.region.x))


# ---------------------------------------------------------------------------
# Menu bar
# ---------------------------------------------------------------------------

class AppMenuBar(Widget):
    """Horizontal bar with File / View labels."""

    # Re-export so MainScreen can listen for it
    class ToggleMenu(Message):
        def __init__(self, menu_id: str, col: int) -> None:
            super().__init__()
            self.menu_id = menu_id
            self.col = col

    DEFAULT_CSS = """
    AppMenuBar {
        dock: top;
        height: 1;
        background: $primary-darken-2;
        layout: horizontal;
    }
    AppMenuBar _MenuLabel {
        height: 1;
        width: auto;
        min-width: 8;
        padding: 0 1;
        color: $foreground;
        background: transparent;
    }
    AppMenuBar _MenuLabel:hover {
        background: $primary;
        color: $foreground;
    }
    """

    def compose(self) -> ComposeResult:
        yield _MenuLabel(" File ",     menu_id="file",     id="menu-lbl-file")
        yield _MenuLabel(" View ",     menu_id="view",     id="menu-lbl-view")
        yield _MenuLabel(" Settings ", menu_id="settings", id="menu-lbl-settings")

    def on__menu_label_clicked(self, event: _MenuLabel.Clicked) -> None:
        self.post_message(self.ToggleMenu(event.menu_id, event.col))
