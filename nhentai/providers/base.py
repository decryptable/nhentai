from abc import ABC, abstractmethod
from pathlib import Path

from ..enums import Language


class BaseTranslator(ABC):
    """Base class for all translation providers."""

    @abstractmethod
    def get_balance(self) -> dict:
        """Returns quota/credits and plan info."""
        pass

    @abstractmethod
    def translate_bytes(
        self,
        data: bytes,
        filename: str,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: str | None = None,
    ) -> bytes:
        """Translate raw image bytes."""
        pass

    @abstractmethod
    def translate_file(
        self,
        image_path: Path,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: str | None = None,
    ) -> bytes:
        """Translate an image file."""
        pass

class TranslationError(Exception):
    """Raised when the translation server reports a failure."""
    pass
