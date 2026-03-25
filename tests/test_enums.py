import pytest
from nhentai.enums import Engine, Language


def test_engine_is_str_subclass():
    assert isinstance(Engine.DEEPL, str)


def test_engine_value():
    assert Engine.DEEPL.value == "deepl"
    assert Engine.GOOGLE.value == "google_cloud"
    assert Engine.GPT5.value == "gpt5"


def test_engine_from_string():
    assert Engine("deepl") is Engine.DEEPL
    assert Engine("gpt5") is Engine.GPT5


def test_engine_invalid_raises():
    with pytest.raises(ValueError):
        Engine("not_an_engine")


def test_language_is_str_subclass():
    assert isinstance(Language.ENGLISH, str)


def test_language_value():
    assert Language.ENGLISH.value == "en"
    assert Language.INDONESIAN.value == "id"
    assert Language.JAPANESE.value == "ja"


def test_language_from_string():
    assert Language("en") is Language.ENGLISH
    assert Language("id") is Language.INDONESIAN


def test_language_invalid_raises():
    with pytest.raises(ValueError):
        Language("zz")


def test_engine_usable_as_dict_key():
    d = {Engine.DEEPL: "foo"}
    assert d["deepl"] == "foo"


def test_engine_equality_with_string():
    assert Engine.DEEPL == "deepl"
    assert Language.ENGLISH == "en"
