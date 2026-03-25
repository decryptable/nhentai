import json
import pytest
from nhentai.parser import Parser

_GALLERY = {
    "id": 1,
    "media_id": "111111",
    "title": {"english": "Test", "japanese": "テスト", "pretty": "Test"},
    "images": {
        "pages": [{"t": "j", "w": 1280, "h": 1808}],
        "cover": {"t": "j", "w": 350, "h": 494},
        "thumbnail": {"t": "j", "w": 250, "h": 353},
    },
    "scanlator": "",
    "upload_date": 1700000000,
    "tags": [],
    "num_pages": 1,
    "num_favorites": 0,
}

_ENCODED = json.dumps(json.dumps(_GALLERY))


def _make_html(script_content: str) -> str:
    return f"<html><body><script>{script_content}</script></body></html>"


def test_parse_gallery_info_success():
    html = _make_html(f"window._gallery = JSON.parse({_ENCODED});")
    result = Parser(html).parse_gallery_info()
    assert result["id"] == 1
    assert result["media_id"] == "111111"
    assert result["title"]["pretty"] == "Test"


def test_parse_gallery_info_missing_script():
    with pytest.raises(ValueError, match="not found"):
        Parser("<html><body></body></html>").parse_gallery_info()


def test_parse_gallery_info_malformed_json():
    html = _make_html('window._gallery = JSON.parse("not_valid_json");')
    with pytest.raises(ValueError, match="Failed to parse"):
        Parser(html).parse_gallery_info()


def test_parse_gallery_pages():
    html = _make_html(f"window._gallery = JSON.parse({_ENCODED});")
    result = Parser(html).parse_gallery_info()
    assert len(result["images"]["pages"]) == 1
    assert result["images"]["pages"][0]["t"] == "j"
