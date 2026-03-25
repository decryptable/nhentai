import pytest
from nhentai.cdn import CDN


def test_ext_from_type_known():
    assert CDN.ext_from_type("j") == "jpg"
    assert CDN.ext_from_type("p") == "png"
    assert CDN.ext_from_type("w") == "webp"
    assert CDN.ext_from_type("g") == "gif"


def test_ext_from_type_unknown_defaults_to_jpg():
    assert CDN.ext_from_type("x") == "jpg"
    assert CDN.ext_from_type("") == "jpg"


def test_get_image_url_format():
    cdn = CDN()
    url = cdn.get_image_url(123456, 1, "jpg")
    assert url.startswith("https://i")
    assert "nhentai.net" in url
    assert "/galleries/123456/1.jpg" in url


def test_get_thumb_url_format():
    cdn = CDN()
    url = cdn.get_thumb_url(123456, 3, "webp")
    assert url.startswith("https://t")
    assert "/galleries/123456/3t.webp" in url


def test_get_cover_url_format():
    cdn = CDN()
    url = cdn.get_cover_url(123456, "jpg")
    assert url.startswith("https://t")
    assert "/galleries/123456/cover.jpg" in url


def test_get_image_url_random_host():
    cdn = CDN()
    hosts = {cdn.get_image_url(1, 1).split("/")[2] for _ in range(50)}
    assert len(hosts) >= 1
    for h in hosts:
        assert h in CDN._image_hosts
