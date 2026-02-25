"""
scripts/download_dict.py

Downloads a LibreOffice/OpenOffice Hunspell .dic file and converts it
to the pyspellchecker gzipped-JSON format used by this app.

Usage:
    python scripts/download_dict.py <lang_code> <dic_url>

Examples:
    # Norwegian Bokmål
    python scripts/download_dict.py no https://raw.githubusercontent.com/LibreOffice/dictionaries/master/no/nb_NO.dic

    # English (US)
    python scripts/download_dict.py en https://raw.githubusercontent.com/LibreOffice/dictionaries/master/en/en_US.dic

    # German
    python scripts/download_dict.py de https://raw.githubusercontent.com/LibreOffice/dictionaries/master/de/de_DE_frami.dic

The output is saved to app/resources/<lang_code>.json.gz
After generating, add the lang_code to _CUSTOM_LANGUAGES in app/state/settings.py
if it is not already a pyspellchecker built-in language.
"""

import sys
import os
import json
import gzip

try:
    import requests
except ImportError:
    print("requests is not installed. Run: pip install requests")
    sys.exit(1)

# Folder where dictionaries are stored
RESOURCES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "app", "resources"
)


def download_and_convert(lang_code: str, dic_url: str) -> None:
    print(f"Downloading {dic_url} ...")
    r = requests.get(dic_url, timeout=30)
    r.raise_for_status()

    # Detect encoding — LibreOffice dicts are usually UTF-8 or ISO-8859-1
    text = r.content.decode("utf-8", errors="replace")
    lines = text.splitlines()

    # First line is the word count; skip it
    word_lines = lines[1:]

    # Parse words — strip Hunspell flags (everything after the first '/')
    # Also skip comment lines starting with '#'
    words: dict[str, int] = {}
    for line in word_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        word = line.split("/")[0]  # drop /FLAGS
        if word:
            # Give every word an equal weight of 1 — pyspellchecker
            # uses this for ranking suggestions.  Providing a uniform
            # weight means all dictionary words are treated equally.
            words[word] = 1

    os.makedirs(RESOURCES_DIR, exist_ok=True)
    out_path = os.path.join(RESOURCES_DIR, f"{lang_code}.json.gz")

    with gzip.open(out_path, "wt", encoding="utf-8") as f:
        json.dump(words, f)

    print(f"Saved {len(words):,} words → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    lang_code_arg = sys.argv[1]
    dic_url_arg   = sys.argv[2]
    download_and_convert(lang_code_arg, dic_url_arg)
