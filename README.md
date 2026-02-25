# Screenply

A terminal-based screenwriting app built with Python and [Textual](https://github.com/Textualize/textual).

## Tech

- **Python 3.10+**
- **Textual** — TUI framework (widgets, reactive state, themes, modal screens)

## Run

```bash
python makevenv.py
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Current features

- Menu bar with **File** and **View** dropdown menus (stubs)
- Collapsible **sidebar** (Table of Contents placeholder)
- **Status bar** with filename, save status, autosave indicator
- **Theme picker** — click 🎨 in the status bar to choose from 20 built-in themes

## Planned

- Screenplay editor with proper formatting (scene heading, action, dialogue, etc.)
- New / open / save / save-as file operations
- Table of Contents auto-generated from scene headings
- Web view and paper view export/preview
- Autosave
