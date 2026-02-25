"""
Export helpers — Fountain text → PDF / HTML.

All functions are intentionally free of Textual dependencies so they can
be called from background workers.
"""
from __future__ import annotations

import os
import tempfile
from io import StringIO, BytesIO


def get_export_path(current_file_path: str, ext: str) -> str:
    """
    Derive an output path from the currently open file.
    Falls back to a temp file when no file is open yet.

    *ext* should include the dot, e.g. ``".pdf"`` or ``".html"``.
    """
    if current_file_path:
        base = os.path.splitext(current_file_path)[0]
        return base + ext
    return os.path.join(tempfile.gettempdir(), f"screenply_preview{ext}")


def fountain_to_pdf(text: str, out_path: str) -> None:
    """Parse *text* as Fountain markup and write a PDF to *out_path*."""
    from screenplain.parsers.fountain import parse
    from screenplain.export.pdf import to_pdf

    screenplay = parse(StringIO(text))
    buf = BytesIO()
    to_pdf(screenplay, buf)
    with open(out_path, "wb") as fh:
        fh.write(buf.getvalue())


def fountain_to_html(text: str, out_path: str) -> None:
    """Parse *text* as Fountain markup and write a standalone HTML to *out_path*."""
    import os
    from screenplain.parsers.fountain import parse
    from screenplain.export import html as html_module
    from screenplain.export.html import convert_full

    # Use the CSS that ships with screenplain
    default_css = os.path.join(os.path.dirname(html_module.__file__), "default.css")
    screenplay = parse(StringIO(text))
    with open(out_path, "w", encoding="utf-8") as fh:
        convert_full(screenplay, fh, css_file=default_css)
