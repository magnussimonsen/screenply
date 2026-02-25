# Screenply — TODO & Session Context

## How to run
```powershell
.venv\Scripts\activate
python main.py
```

## Tech stack
- **Python 3.10+** / `.venv/`
- **Textual 8.0.0** — TUI framework
- **pyspellchecker 0.8.4** — spell checking
- **screenplain 0.11.1** — Fountain → PDF / HTML export
- **reportlab 4.x** — PDF rendering backend for screenplain
- **tkinter** (stdlib) — native OS file dialogs

---

## ✅ Completed features

### Core app
- [x] Virtual environment setup (`makevenv.py`)
- [x] Full app scaffold — menu bar, sidebar, editor, status bar
- [x] File / View / Settings dropdown menus
- [x] Theme picker modal (20 built-in Textual themes, click 🎨 in status bar)
- [x] Page-on-desk layout — 72-char centered "paper" column in editor

### File operations
- [x] New Script (Ctrl+N)
- [x] Open Script (Ctrl+O) — native Windows file picker via tkinter
- [x] Save Script (Ctrl+S) — saves in-place, falls through to Save As if unsaved
- [x] Save Script As — native Windows save dialog via tkinter
- [x] Load Big Fish example (File menu) — loads `app/example_script/Big-Fish.fountain`
- [x] Export as PDF (File menu) — opens in system PDF viewer
- [x] Export as HTML (File menu) — opens in browser
- [x] Status bar tracks filename + Saved/Unsaved state

### Spell checking
- [x] Visual red-underline highlights on misspelled words (TextArea _highlights)
- [x] Background worker + 600 ms debounce
- [x] Norwegian dictionary (LibreOffice source, 333,669 words) at `app/resources/no.json.gz`
- [x] 13 supported languages (Settings → Select Language…)
- [x] Toggle via Settings menu or click spell slot in status bar
- [x] Add word to user dictionary (Ctrl+D or Settings → Add Word to Dictionary…)
  - Per-language, saved to `app/resources/user_<lang>.json`

### Live HTML preview
- [x] Settings → Turn On Live HTML Preview
  - Opens default browser automatically on first toggle
  - Writes `<filename>.preview.html` next to the open script
  - Browser tab auto-refreshes every 2 s via `<meta http-equiv="refresh">`
  - Rebuilds 1.5 s after user stops typing (~0.08 s generation time)
  - Status bar shows "✓ Preview updated" after each rebuild

### Notifications
- [x] All notifications shown inline in status bar (no pop-ups)
  - Normal messages in foreground colour, errors in `$error` (red)
  - Auto-clears after 4 seconds

### Dictionary tooling
- [x] `scripts/download_dict.py` — converts any LibreOffice Hunspell .dic to pyspellchecker format

---

## ⬜ Todo — next session

### High priority
- [ ] **Sidebar Table of Contents** — parse `INT./EXT.` scene headings from editor text,
      populate `AppSidebar` with clickable scene list.
      Hook: watch `TextArea.Changed`, extract headings with regex,
      update a `ListView` or list of `_MenuItem`-style `Static` widgets in the sidebar.
      Clicking a scene should scroll the editor to that line (`TextArea.scroll_to_region`).

- [ ] **Autosave** — add `autosave_enabled: reactive[bool]` to `ScreenplyApp`,
      toggle via Settings menu, use `set_interval(60, _autosave)` in `MainScreen`.
      Status bar already has an "Autosave: OFF" slot ready to update.

- [ ] **New script from template** — when File → New Script, offer a minimal
      Fountain template (Title, Author, first scene heading) instead of blank editor.

### Medium priority
- [ ] **Paper View screen** — a read-only `ModalScreen` or pushed `Screen` that renders
      the Fountain text as formatted screenplay using `screenplain`'s AST:
      scene headings in caps, action, character centred, dialogue indented.
      Use a Textual `ScrollableContainer` with `Static` rows.
      Bind a key (e.g. F5) to toggle it.

- [ ] **Word count in status bar** — add a `#status-wordcount` slot, update on
      `TextArea.Changed` with a debounce (count words with `len(text.split())`).

- [ ] **Fountain syntax highlighting in editor** — register a custom `TextAreaTheme`
      with token styles for slug lines (bold/caps), character names (bold),
      transitions (right-aligned colour). Requires a Tree-sitter grammar or
      a manual regex highlighter similar to the spell-check highlight mechanism.

### Low priority / Nice to have
- [ ] **"Unsaved changes" confirmation on New/Open** — before wiping the editor,
      check `AppStatusBar.is_saved`; if False, show a confirm modal
      (`ModalScreen` with "Save / Discard / Cancel" buttons).

- [ ] **Recent files list** — persist last 5 opened paths to
      `app/resources/recent_files.json`, show under File menu.

- [ ] **Dark/light desk background** — the area outside the page column uses
      `$background`; could expose a setting to choose desk colour independently
      of the Textual theme (e.g. always dark even in light themes).

- [ ] **Export as FDX** — `screenplain.export.fdx` already exists in the package;
      wire it to a "Export as Final Draft…" menu item.

- [ ] **Norwegian compound-word spell checking** — the current LibreOffice .dic
      contains only stems. Processing the .aff affix file would generate all
      compound forms (e.g. `barnehagelærer`). See `scripts/download_dict.py`
      for the conversion entry point.

---

## Key file map

```
main.py                          Entry point
app/app.py                       ScreenplyApp — reactives: spell_check_enabled,
                                   spell_language, current_file_path,
                                   live_preview_enabled
app/app.tcss                     Global layout CSS
app/screens/main_screen.py       Full layout, all menu handlers, file ops
app/screens/theme_picker.py      Theme selector modal
app/screens/language_picker.py   Spell language modal
app/screens/add_word_screen.py   Add-to-dictionary modal
app/screens/file_path_screen.py  Text-input path modal (fallback, not used for
                                   open/save — those use native dialogs)
app/widgets/menu_bar.py          AppMenuBar, DropdownMenu, FILE/VIEW/SETTINGS_ITEMS
app/widgets/editor.py            AppEditor — TextArea, spell highlights, live preview
app/widgets/status_bar.py        AppStatusBar — filename, saved, spell, notice, theme
app/widgets/sidebar.py           AppSidebar — collapsible, TOC placeholder
app/state/settings.py            SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
app/state/user_dict.py           load/add/remove user dictionary words per language
app/utils/export.py              fountain_to_pdf, fountain_to_html, fountain_to_html_live,
                                   get_export_path
app/utils/dialogs.py             ask_open_path, ask_save_as_path (tkinter native dialogs)
app/resources/no.json.gz         Norwegian dictionary (333,669 words)
app/resources/user_<lang>.json   Per-language user word additions (gitignored)
app/example_script/Big-Fish.fountain  Example script for testing
scripts/download_dict.py         Convert LibreOffice .dic → pyspellchecker .json.gz
```

## Known patterns / gotchas
- **Cross-widget reactive watching**: always use `self.watch(self.app, "attr", cb, init=False)`
  in `on_mount` — NOT `watch_app_<attr>` naming convention (doesn't work for non-App widgets).
- **Background workers**: use `self.run_worker(fn, thread=True)`.
  Results back to main thread via `self.app.call_from_thread(...)`.
  `webbrowser.open()` and Textual DOM calls MUST be on main thread.
- **load_text() fires Changed**: after calling `TextArea.load_text()`, use
  `call_after_refresh(lambda: status.set_file(..., saved=True))` to override
  the spurious "unsaved" state the Changed event would set.
- **Dropdowns**: owned by `MainScreen`, not `AppMenuBar` — so they float over
  the full layout and aren't clipped by the `height:1` menu bar.
