"""
Left sidebar — Table of Contents panel.
Supports expand / collapse via the toggle button.
Scene headings parsed from the editor text are shown as clickable entries.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static
from textual.containers import Vertical, ScrollableContainer
from textual import events


_COLLAPSED_WIDTH = 3   # just wide enough for the toggle arrow
_EXPANDED_WIDTH  = 28  # normal sidebar width


class _TocEntry(Static):
    """A single clickable scene-heading entry in the TOC."""

    class Selected(Message):
        def __init__(self, line_no: int) -> None:
            super().__init__()
            self.line_no = line_no

    DEFAULT_CSS = """
    _TocEntry {
        width: 1fr;
        height: 1;
        padding: 0 1;
        color: $foreground;
        background: transparent;
        overflow: hidden;
    }
    _TocEntry:hover {
        background: $primary;
        color: $foreground;
    }
    """

    def __init__(self, line_no: int, text: str, **kwargs) -> None:
        super().__init__(text, **kwargs)
        self._line_no = line_no

    def on_click(self, event: events.Click) -> None:
        event.stop()
        self.post_message(self.Selected(self._line_no))


class AppSidebar(Widget):
    """Collapsible left sidebar containing the Table of Contents."""

    expanded: reactive[bool] = reactive(True)
    _last_scenes: list[tuple[int, str]]

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
    AppSidebar #toc-header {{
        padding: 0 1;
        text-style: bold;
        color: $foreground;
        height: 1;
        background: $panel;
    }}
    AppSidebar #toc-empty {{
        padding: 1 1;
        color: $text-muted;
    }}
    AppSidebar #toc-scroll {{
        width: 1fr;
        height: 1fr;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Button("◀ Close", id="sidebar-toggle")
        with Vertical(id="sidebar-content"):
            yield Label("Table of Contents", id="toc-header")
            with ScrollableContainer(id="toc-scroll"):
                yield Static(
                    "[dim]No scenes yet.[/dim]",
                    markup=True,
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        self._last_scenes = []
        self.watch(self.app, "sidebar_width", self._on_sidebar_width_changed, init=False)

    def update_toc(self, scenes: list[tuple[int, str]]) -> None:
        """Replace TOC entries with a fresh list of (line_no, heading) pairs."""
        self._last_scenes = scenes
        scroll = self.query_one("#toc-scroll", ScrollableContainer)
        # remove_children() is async; mount new widgets after the refresh cycle
        max_chars = max(4, int(self.styles.width.value) - 2)

        def _remount() -> None:
            if not scenes:
                scroll.mount(Static("[dim]No scenes yet.[/dim]", markup=True))
                return
            for line_no, heading in scenes:
                display = heading if len(heading) <= max_chars else heading[:max_chars - 1] + "…"
                scroll.mount(_TocEntry(line_no, display))

        scroll.remove_children()
        self.call_after_refresh(_remount)

    # ------------------------------------------------------------------
    # Toggle behaviour
    # ------------------------------------------------------------------

    def _on_sidebar_width_changed(self, width: int) -> None:
        if self.expanded:
            self.styles.width = width
        self.update_toc(self._last_scenes)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "sidebar-toggle":
            self.expanded = not self.expanded

    def watch_expanded(self, value: bool) -> None:
        toggle = self.query_one("#sidebar-toggle", Button)
        content = self.query_one("#sidebar-content")

        if value:
            self.styles.width = self.app.sidebar_width  # type: ignore
            toggle.label = "◀ Close"
            content.display = True
        else:
            self.styles.width = _COLLAPSED_WIDTH
            toggle.label = "▶"
            content.display = False
