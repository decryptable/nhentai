import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from nhentai.translator import NekoTranslator, TranslationError
from nhentai.enums import NekoEngine, Language
import requests


def _resp(json_data=None, status=200, content=b"img"):
    resp = MagicMock()
    resp.status_code = status
    resp.content = content
    resp.json.return_value = json_data or {}
    resp.text = str(json_data)
    resp.raise_for_status = MagicMock()
    if status >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    return resp


@pytest.fixture
def translator():
    with patch.object(NekoTranslator, "_fetch_proxies", return_value=[]):
        return NekoTranslator()


@pytest.fixture
def auth_translator():
    with patch.object(NekoTranslator, "_fetch_proxies", return_value=[]):
        return NekoTranslator(token="test-token")


def test_auth_header(auth_translator):
    assert auth_translator.headers["Authorization"] == "Bearer test-token"


def test_no_token_no_auth_header(translator):
    assert "Authorization" not in translator.headers


def test_parse_proxy_plain():
    from nhentai.providers.neko import _parse_proxy
    p = _parse_proxy("1.2.3.4:8080")
    assert p["http"] == "http://1.2.3.4:8080"
    assert p["https"] == "http://1.2.3.4:8080"


def test_parse_proxy_socks5():
    from nhentai.providers.neko import _parse_proxy
    p = _parse_proxy("socks5://1.2.3.4:1080")
    assert p["http"] == "socks5://1.2.3.4:1080"


def test_get_balance_anonymous(translator):
    quota_resp = _resp({"quota": 15})
    with patch.object(translator, "_request", return_value=quota_resp):
        bal = translator.get_balance()
    assert bal["quota"] == 15
    assert bal["email"] is None
    assert bal["plan"] == "Free"


def test_get_balance_authenticated(auth_translator):
    user_resp  = _resp({"email": "u@test.com", "level": 1})
    quota_resp = _resp({"quota": 100})

    with patch.object(auth_translator, "_request", side_effect=[user_resp, quota_resp]):
        bal = auth_translator.get_balance()
    assert bal["email"] == "u@test.com"
    assert bal["plan"] == "Lite"
    assert bal["quota"] == 100


def test_translate_file_not_found(translator):
    with pytest.raises(FileNotFoundError):
        translator.translate_file("/nonexistent/image.jpg")


def test_translate_file_invalid_engine(translator, tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake")
    with pytest.raises(ValueError):
        translator.translate_file(img, engine="bad_engine")


def test_translate_file_success(translator, tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake_image_data")

    upload_resp  = _resp({"manga_id": "abc123"})
    poll_resp    = _resp({"state": "completed"})
    result_bytes = b"translated_image"

    with patch.object(translator, "_request", side_effect=[upload_resp, poll_resp]), \
         patch("nhentai.providers.neko.requests.get", return_value=_resp(content=result_bytes)):
        result = translator.translate_file(img, tgt_lang=Language.ENGLISH, engine=NekoEngine.DEEPL)

    assert result == result_bytes


def test_translate_file_upload_rejected(translator, tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake")

    with patch.object(translator, "_request", return_value=_resp({"detail": "quota_exceeded"}, status=403)):
        with pytest.raises(TranslationError, match="Upload rejected"):
            translator.translate_file(img)


def test_translate_file_server_failure(translator, tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake")

    upload_resp = _resp({"manga_id": "abc123"})
    fail_resp   = _resp({"state": "failed", "detail": "processing error"})

    with patch.object(translator, "_request", side_effect=[upload_resp, fail_resp]):
        with pytest.raises(TranslationError, match="processing error"):
            translator.translate_file(img)


def test_translate_bytes_success(translator, tmp_path):
    result_bytes = b"translated"
    with patch.object(translator, "translate_file", return_value=result_bytes):
        out = translator.translate_bytes(b"raw_image", "test.jpg")
    assert out == result_bytes


def test_find_proxy_with_quota_found(tmp_path):
    with patch.object(NekoTranslator, "_fetch_proxies", return_value=["1.2.3.4:1080"]):
        t = NekoTranslator()
    with patch("nhentai.providers.neko.requests.get", return_value=_resp({"quota": 10})):
        proxy = t.find_proxy_with_quota()
    assert proxy is not None


def test_find_proxy_with_quota_none_found(tmp_path):
    with patch.object(NekoTranslator, "_fetch_proxies", return_value=["1.2.3.4:1080"]):
        t = NekoTranslator()
    with patch("nhentai.providers.neko.requests.get", return_value=_resp({"quota": 0})):
        proxy = t.find_proxy_with_quota()
    assert proxy is None
