"""
Left sidebar — Table of Contents panel.
Supports expand / collapse via the toggle button.
"""
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static
from textual.containers import Vertical


_COLLAPSED_WIDTH = 3   # just wide enough for the toggle arrow
_EXPANDED_WIDTH  = 28  # normal sidebar width


class AppSidebar(Widget):
    """Collapsible left sidebar containing the Table of Contents."""

    expanded: reactive[bool] = reactive(True)

    DEFAULT_CSS = f"""
    AppSidebar {{
        width: {_EXPANDED_WIDTH};
        height: 100%;
        background: $panel;
        border-right: solid $primary-darken-1;
        layout: vertical;
    }}
    AppSidebar #sidebar-toggle {{
        width: 100%;
        height: 1;
        background: $primary-darken-2;
        border: none;
        text-align: right;
    }}
    AppSidebar #toc-placeholder {{
        padding: 1 1;
        color: $text-muted;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Button("◀ Close", id="sidebar-toggle")
        with Vertical(id="sidebar-content"):
            yield Label("Table of Contents", id="toc-header")
            yield Static(
                "[dim]— placeholder —\n\n"
                "Scenes will appear here\nonce implemented.[/dim]",
                id="toc-placeholder",
                markup=True,
            )

    # ------------------------------------------------------------------
    # Toggle behaviour
    # ------------------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "sidebar-toggle":
            self.expanded = not self.expanded

    def watch_expanded(self, value: bool) -> None:
        toggle = self.query_one("#sidebar-toggle", Button)
        content = self.query_one("#sidebar-content")

        if value:
            self.styles.width = _EXPANDED_WIDTH
            toggle.label = "◀ Close"
            content.display = True
        else:
            self.styles.width = _COLLAPSED_WIDTH
            toggle.label = "▶"
            content.display = False
