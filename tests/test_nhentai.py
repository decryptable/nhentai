import json
import pytest
from unittest.mock import patch, MagicMock
from nhentai.nhentai import NHentai

_GALLERY = {
    "id": 639456,
    "media_id": "3856349",
    "title": {"english": "Test Gallery", "japanese": "テスト", "pretty": "Test Gallery"},
    "images": {
        "pages": [
            {"t": "j", "w": 1280, "h": 1808},
            {"t": "w", "w": 1280, "h": 1808},
            {"t": "p", "w": 1280, "h": 1808},
        ],
        "cover": {"t": "j", "w": 350, "h": 494},
        "thumbnail": {"t": "j", "w": 250, "h": 353},
    },
    "scanlator": "",
    "upload_date": 1700000000,
    "tags": [
        {"id": 1, "type": "tag",      "name": "big breasts", "url": "/tag/big-breasts/", "count": 100},
        {"id": 2, "type": "artist",   "name": "gen",          "url": "/artist/gen/",     "count": 10},
        {"id": 3, "type": "language", "name": "english",      "url": "/lang/english/",   "count": 1000},
        {"id": 4, "type": "category", "name": "doujinshi",    "url": "/cat/doujinshi/",  "count": 500},
        {"id": 5, "type": "group",    "name": "enji",         "url": "/group/enji/",     "count": 5},
    ],
    "num_pages": 3,
    "num_favorites": 17601,
}

_HTML = f"<html><body><script>window._gallery = JSON.parse({json.dumps(json.dumps(_GALLERY))});</script></body></html>"


def _make_gallery():
    with patch("nhentai.nhentai.Grabber") as MockGrabber:
        MockGrabber.return_value.get_html.return_value = _HTML
        return NHentai("https://nhentai.net/g/639456/")


def test_properties():
    g = _make_gallery()
    assert g.id == 639456
    assert g.media_id == 3856349
    assert g.num_pages == 3
    assert g.num_favorites == 17601
    assert g.upload_date == 1700000000


def test_title():
    g = _make_gallery()
    assert g.title["pretty"] == "Test Gallery"
    assert g.title["english"] == "Test Gallery"


def test_tags_filtering():
    g = _make_gallery()
    assert all(t["type"] == "tag" for t in g.tags)
    assert all(t["type"] == "artist" for t in g.artists)
    assert all(t["type"] == "language" for t in g.languages)
    assert all(t["type"] == "category" for t in g.categories)
    assert all(t["type"] == "group" for t in g.groups)


def test_get_image_urls_count():
    g = _make_gallery()
    urls = g.get_image_urls()
    assert len(urls) == 3


def test_get_image_urls_extensions():
    g = _make_gallery()
    urls = g.get_image_urls()
    assert urls[0].endswith(".jpg")
    assert urls[1].endswith(".webp")
    assert urls[2].endswith(".png")


def test_accepts_bare_id():
    with patch("nhentai.nhentai.Grabber") as MockGrabber:
        MockGrabber.return_value.get_html.return_value = _HTML
        g = NHentai("639456")
        assert "nhentai.net/g/639456" in g.url


def test_get_cover_url():
    g = _make_gallery()
    url = g.get_cover_url()
    assert "cover.jpg" in url


def test_info_returns_dict():
    g = _make_gallery()
    assert isinstance(g.info(), dict)
    assert "id" in g.info()
