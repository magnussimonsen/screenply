"""
Per-language user dictionary.

Words are persisted in app/resources/user_<lang>.json
(plain JSON list, human-readable).

Public API
----------
- load_user_words(lang)  -> frozenset[str]
- add_user_word(lang, word) -> None
- remove_user_word(lang, word) -> None
"""
from __future__ import annotations

import json
import os

from app.resources import RESOURCES_DIR


def _path(lang: str) -> str:
    return os.path.join(RESOURCES_DIR, f"user_{lang}.json")


def load_user_words(lang: str) -> frozenset[str]:
    """Return all custom words added for *lang*.  Never raises."""
    path = _path(lang)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return frozenset(str(w) for w in data)
    except FileNotFoundError:
        return frozenset()
    except Exception:
        return frozenset()


def add_user_word(lang: str, word: str) -> None:
    """Persist *word* to the user dictionary for *lang*."""
    word = word.strip()
    if not word:
        return
    words = set(load_user_words(lang))
    words.add(word)
    _save(lang, words)


def remove_user_word(lang: str, word: str) -> None:
    """Remove *word* from the user dictionary for *lang* (no-op if absent)."""
    words = set(load_user_words(lang))
    words.discard(word)
    _save(lang, words)


def _save(lang: str, words: set[str]) -> None:
    path = _path(lang)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(sorted(words), fh, ensure_ascii=False, indent=2)
