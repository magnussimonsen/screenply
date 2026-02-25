"""
Native OS file dialogs via tkinter.

These functions block until the user closes the dialog, so always call
them from a background worker thread, never from the Textual main thread.
"""
from __future__ import annotations

import os


def ask_open_path(initial_path: str = "") -> str | None:
    """Show a native Open-File dialog.  Returns the chosen path or None."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)

    initial_dir = os.path.dirname(initial_path) if initial_path else os.getcwd()

    path = filedialog.askopenfilename(
        parent=root,
        title="Open Script",
        initialdir=initial_dir,
        filetypes=[
            ("Fountain scripts", "*.fountain"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path if path else None


def ask_save_as_path(initial_path: str = "") -> str | None:
    """Show a native Save-As dialog.  Returns the chosen path or None."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)

    initial_dir = os.path.dirname(initial_path) if initial_path else os.getcwd()
    initial_file = os.path.basename(initial_path) if initial_path else "script.fountain"

    path = filedialog.asksaveasfilename(
        parent=root,
        title="Save Script As",
        initialdir=initial_dir,
        initialfile=initial_file,
        defaultextension=".fountain",
        filetypes=[
            ("Fountain scripts", "*.fountain"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path if path else None
