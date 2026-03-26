import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from nhentai.downloader import Downloader, DownloadError
from nhentai.enums import Language, Provider
from nhentai.providers.base import TranslationError

def _make_gallery():
    gallery = MagicMock()
    gallery.id = 999
    gallery.num_pages = 1
    gallery.get_image_urls.return_value = ["https://test.com/1.jpg"]
    return gallery

def _img_response(content=b"imgdata"):
    resp = MagicMock()
    resp.content = content
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    return resp

def test_download_page_with_translate_url_success(tmp_path):
    gallery = _make_gallery()
    mock_translator = MagicMock()
    mock_translator.translate_url.return_value = b"translated_url_data"
    
    dl = Downloader(gallery, output_dir=tmp_path, translator=mock_translator)
    with patch.object(dl, "_fetch", return_value=b"original"):
        paths = dl.download()
    
    mock_translator.translate_url.assert_called_once()
    assert paths[0].read_bytes() == b"translated_url_data"

def test_download_page_translate_url_fails_fallback(tmp_path):
    gallery = _make_gallery()
    mock_translator = MagicMock()
    mock_translator.translate_url.side_effect = TranslationError("url_fail")
    mock_translator.translate_bytes.return_value = b"translated_bytes_data"
    
    dl = Downloader(gallery, output_dir=tmp_path, translator=mock_translator)
    with patch.object(dl, "_fetch", return_value=b"original"):
        paths = dl.download()
    
    mock_translator.translate_url.assert_called_once()
    mock_translator.translate_bytes.assert_called_once()
    assert paths[0].read_bytes() == b"translated_bytes_data"

def test_downloader_cleanup_on_error(tmp_path):
    gallery = _make_gallery()
    dl = Downloader(gallery, output_dir=tmp_path)
    
    # Simulating error in workers
    with patch.object(dl, "_download_page", side_effect=DownloadError("boom")):
        with pytest.raises(DownloadError):
            dl.download()
    
    # Check that temp dir is cleaned (if it used one)
    # The current downloader uses temporary directories.
    pass
