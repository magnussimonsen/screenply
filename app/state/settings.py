"""
App-wide settings.
Stored as reactive attributes on ScreenplyApp so any widget can
read or react to changes.  This module just provides the constants.
"""

# Languages bundled with pyspellchecker
SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
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
