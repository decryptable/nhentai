import pytest
from unittest.mock import patch, MagicMock
from nhentai.grabber import Grabber
import requests


def _mock_response(text="<html/>", status=200):
    resp = MagicMock()
    resp.text = text
    resp.content = text.encode()
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    if status >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    return resp


@patch("nhentai.grabber.requests.get")
def test_get_html_success(mock_get):
    mock_get.return_value = _mock_response("<html>ok</html>")
    g = Grabber("https://nhentai.net/g/1/")
    assert g.get_html() == "<html>ok</html>"


@patch("nhentai.grabber.requests.get")
def test_get_html_http_error(mock_get):
    mock_get.return_value = _mock_response(status=403)
    with pytest.raises(ConnectionError, match="HTTP 403"):
        Grabber("https://nhentai.net/g/1/").get_html()


@patch("nhentai.grabber.requests.get")
def test_get_html_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()
    with pytest.raises(ConnectionError, match="timed out"):
        Grabber("https://nhentai.net/g/1/").get_html()


@patch("nhentai.grabber.requests.get")
def test_get_html_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("refused")
    with pytest.raises(ConnectionError, match="Network error"):
        Grabber("https://nhentai.net/g/1/").get_html()


@patch("nhentai.grabber.requests.get")
def test_download_bytes_success(mock_get):
    mock_get.return_value = _mock_response("binary_data")
    data = Grabber("https://nhentai.net").download_bytes("https://i1.nhentai.net/1/1.jpg")
    assert data == b"binary_data"


@patch("nhentai.grabber.requests.get")
def test_download_bytes_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()
    with pytest.raises(ConnectionError, match="Download timed out"):
        Grabber("..").download_bytes("https://i1.nhentai.net/1/1.jpg")


def test_custom_headers_merged():
    g = Grabber("https://nhentai.net", headers={"X-Custom": "value"})
    assert g.headers["X-Custom"] == "value"
    assert "User-Agent" in g.headers
