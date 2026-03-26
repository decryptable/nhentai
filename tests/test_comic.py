import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from nhentai.providers.comic import ComicTranslator, TranslationError, ComicEngine
from nhentai.enums import Language

def _resp(json_data=None, status=200, content=b"img", headers=None):
    resp = MagicMock()
    resp.status_code = status
    resp.content = content
    resp.json.return_value = json_data or {}
    resp.text = str(json_data)
    resp.headers = headers or {}
    return resp

def test_comic_register_guest():
    ct = ComicTranslator()
    register_resp = _resp({"accessToken": "test-token", "credits": 20.0})
    with patch.object(ct._session, "post", return_value=register_resp):
        ct._register_guest()
    assert ct.token == "test-token"
    assert ct.credits == 20.0

def test_comic_get_balance():
    ct = ComicTranslator()
    register_resp = _resp({"accessToken": "test-token", "credits": 20.0})
    info_resp = _resp({"email": "guest@test.com", "plan": "free", "credits": 15.0})
    
    with patch.object(ct._session, "post", return_value=register_resp), \
         patch.object(ct._session, "get", return_value=info_resp):
        bal = ct.get_balance()
    
    assert bal["quota"] == 15.0
    assert bal["email"] == "guest@test.com"

def test_comic_translate_url_success():
    ct = ComicTranslator()
    url = "https://test.com/img.jpg"
    
    register_resp = _resp({"accessToken": "test-token", "credits": 20.0})
    translate_resp = _resp(content=b"translated_image", headers={"Content-Type": "image/jpeg"})
    
    with patch.object(ct._session, "post", return_value=register_resp), \
         patch.object(ct._session, "request", return_value=translate_resp):
        result = ct.translate_url(url)
    
    assert result == b"translated_image"

def test_comic_translate_file_success(tmp_path):
    ct = ComicTranslator()
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake_image")
    
    register_resp = _resp({"accessToken": "test-token", "credits": 20.0})
    upload_resp = _resp(content=b"translated_image", headers={"Content-Type": "image/jpeg"})
    
    with patch.object(ct._session, "post", side_effect=[register_resp, upload_resp]):
        result = ct.translate_file(img)
    
    assert result == b"translated_image"

def test_comic_translate_file_task_polling(tmp_path):
    ct = ComicTranslator()
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake_image")
    
    register_resp = _resp({"accessToken": "test-token", "credits": 20.0})
    upload_resp = _resp({"task_id": "task123"}, headers={"Content-Type": "application/json"})
    poll_resp1 = _resp({"status": "processing"})
    poll_resp2 = _resp({"status": "completed", "translated_url": "https://cdn.com/res.jpg"})
    download_resp = _resp(content=b"downloaded_image", headers={"Content-Type": "image/jpeg"})
    
    with patch.object(ct._session, "post", side_effect=[register_resp, upload_resp]), \
         patch.object(ct._session, "get", side_effect=[poll_resp1, poll_resp2, download_resp]), \
         patch("time.sleep"):
        result = ct.translate_file(img)
    
    assert result == b"downloaded_image"

def test_comic_map_engine():
    ct = ComicTranslator()
    assert ct._map_engine(ComicEngine.GEMINI_FLASH) == "Gemini2.5Flash"
    assert ct._map_engine("deepseek") == "deepseek"
