"""
App-wide settings.
Stored as reactive attributes on ScreenplyApp so any widget can
read or react to changes.  This module just provides the constants.
"""

# Languages bundled with pyspellchecker
_BUILTIN_LANGUAGES: set[str] = {
    "en", "de", "es", "fr", "it", "pt",
    "nl", "ru", "ar", "eu", "fa", "lv",
}

# Languages with a local dictionary in app/resources/<code>.json.gz
_CUSTOM_LANGUAGES: set[str] = {"no"}


def is_custom_language(code: str) -> bool:
    return code in _CUSTOM_LANGUAGES


SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "no": "Norwegian",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "ar": "Arabic",
    "eu": "Basque",
    "fa": "Persian",
    "lv": "Latvian",
}

DEFAULT_LANGUAGE = "en"
