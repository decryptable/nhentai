import pytest
from nhentai.enums import NekoEngine, ComicEngine, Language, Provider


def test_provider_is_str_subclass():
    assert isinstance(Provider.NEKO, str)
    assert Provider.NEKO == "neko"
    assert Provider.COMIC == "comic"


def test_neko_engine_is_str_subclass():
    assert isinstance(NekoEngine.DEEPL, str)
    assert NekoEngine.DEEPL.value == "deepl"


def test_comic_engine_is_str_subclass():
    assert isinstance(ComicEngine.GPT5_MINI, str)
    assert ComicEngine.GPT5_MINI.value == "GPT-5-mini"


def test_language_is_str_subclass():
    assert isinstance(Language.ENGLISH, str)
    assert Language.ENGLISH.value == "en"


def test_language_from_string():
    assert Language("en") is Language.ENGLISH


def test_language_invalid_raises():
    with pytest.raises(ValueError):
        Language("zz")


def test_neko_engine_usable_as_dict_key():
    d = {NekoEngine.DEEPL: "foo"}
    assert d["deepl"] == "foo"
