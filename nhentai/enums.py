from enum import StrEnum


class Provider(StrEnum):
    """Translation provider."""

    NEKO  = "neko"
    COMIC = "comic"


class NekoEngine(StrEnum):
    """NekoTranslate engines."""

    GOOGLE     = "google_cloud"
    DEEPL      = "deepl"
    DEEPSEEK   = "deepseekv31"
    GPT5_MINI  = "gpt5_mini"
    CLAUDE     = "claude45_sonnet"
    GPT5       = "gpt5"


class ComicEngine(StrEnum):
    """ComicTranslator engines."""

    GEMINI_FLASH = "Gemini2.5Flash"
    GPT5_MINI    = "GPT-5-mini"
    GPT5         = "GPT-5.1"
    DEEPSEEK     = "Deepseek"
    GROK         = "Grok4fast"
    KIMI         = "KimiK2"


class Language(StrEnum):
    """ISO 639-1 target language codes supported by NekoTranslate."""

    ENGLISH    = "en"
    INDONESIAN = "id"
    JAPANESE   = "ja"
    KOREAN     = "ko"
    CHINESE    = "zh"
    FRENCH     = "fr"
    GERMAN     = "de"
    SPANISH    = "es"
    PORTUGUESE = "pt"
    ITALIAN    = "it"
    DUTCH      = "nl"
    POLISH     = "pl"
    RUSSIAN    = "ru"
    TURKISH    = "tr"
    ARABIC     = "ar"
    THAI       = "th"
    VIETNAMESE = "vi"
    UKRAINIAN  = "uk"
    CZECH      = "cs"
    DANISH     = "da"
    FINNISH    = "fi"
    NORWEGIAN  = "no"
    SWEDISH    = "sv"
    ROMANIAN   = "ro"
    HUNGARIAN  = "hu"
    BULGARIAN  = "bg"
    GREEK      = "el"
    SLOVAK     = "sk"
    SLOVENIAN  = "sl"
    ESTONIAN   = "et"
    LATVIAN    = "lv"
    LITHUANIAN = "lt"
    CROATIAN   = "hr"
    ICELANDIC  = "is"
