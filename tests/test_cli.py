import argparse
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from nhentai.cli import parse_proxy_list, main, interactive_mode


class TestParseProxyList:
    def test_parse_proxy_list_local_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("127.0.0.1:8080\nsocks5://10.0.0.1:1080\n")
            f.flush()
            path = f.name

        try:
            proxies = parse_proxy_list(path)
            assert proxies == ["http://127.0.0.1:8080", "socks5://10.0.0.1:1080"]
        finally:
            os.unlink(path)

    def test_parse_proxy_list_url(self):
        mock_response = MagicMock()
        mock_response.text = "127.0.0.1:8080\nsocks5://10.0.0.1:1080\n"
        with patch("requests.get", return_value=mock_response):
            proxies = parse_proxy_list("https://example.com/proxies.txt")
            assert proxies == ["http://127.0.0.1:8080", "socks5://10.0.0.1:1080"]

    def test_parse_proxy_list_empty_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("\n127.0.0.1:8080\n\nsocks5://10.0.0.1:1080\n\n")
            f.flush()
            path = f.name

        try:
            proxies = parse_proxy_list(path)
            assert proxies == ["http://127.0.0.1:8080", "socks5://10.0.0.1:1080"]
        finally:
            os.unlink(path)

    def test_parse_proxy_list_invalid_file(self):
        with patch("logging.warning") as mock_warn:
            proxies = parse_proxy_list("/nonexistent/file")
            assert proxies == []
            mock_warn.assert_called_once()

    def test_parse_proxy_list_invalid_url(self):
        with patch("requests.get", side_effect=Exception("Network error")), patch(
            "logging.warning"
        ) as mock_warn:
            proxies = parse_proxy_list("https://invalid.example.com")
            assert proxies == []
            mock_warn.assert_called_once_with("Failed to load proxy list: Network error")

    def test_parse_proxy_list_default_type(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("127.0.0.1:8080\n")
            f.flush()
            path = f.name

        try:
            proxies = parse_proxy_list(path, default_type="socks4")
            assert proxies == ["socks4://127.0.0.1:8080"]
        finally:
            os.unlink(path)


class TestMain:
    @patch("sys.argv", ["nhentai", "639456", "--proxy-list", "proxies.txt"])
    @patch("nhentai.cli.parse_proxy_list", return_value=["http://127.0.0.1:8080"])
    @patch("nhentai.cli.NHentai")
    @patch("nhentai.cli.Downloader")
    @patch("nhentai.cli.get_console")
    def test_main_with_proxy_list_file(self, mock_console, mock_downloader, mock_nhentai, mock_parse_proxy):
        mock_gallery = MagicMock()
        mock_gallery.title.get.return_value = "Test Gallery"
        mock_gallery.num_pages = 5
        mock_nhentai.return_value = mock_gallery

        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        mock_downloader_instance.download.return_value = [Path("output/test.pdf")]

        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        main()

        mock_parse_proxy.assert_called_once_with("proxies.txt", "http")
        mock_downloader.assert_called_once()
        args = mock_downloader.call_args[1]
        assert args["proxy_list"] == ["http://127.0.0.1:8080"]

    @patch("sys.argv", ["nhentai", "639456", "--proxy-list", "https://example.com/proxies.txt"])
    @patch("nhentai.cli.parse_proxy_list", return_value=["http://127.0.0.1:8080"])
    @patch("nhentai.cli.NHentai")
    @patch("nhentai.cli.Downloader")
    @patch("nhentai.cli.get_console")
    def test_main_with_proxy_list_url(self, mock_console, mock_downloader, mock_nhentai, mock_parse_proxy):
        mock_gallery = MagicMock()
        mock_gallery.title.get.return_value = "Test Gallery"
        mock_gallery.num_pages = 5
        mock_nhentai.return_value = mock_gallery

        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        mock_downloader_instance.download.return_value = [Path("output/test.pdf")]

        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        main()

        mock_parse_proxy.assert_called_once_with("https://example.com/proxies.txt", "http")
        mock_downloader.assert_called_once()
        args = mock_downloader.call_args[1]
        assert args["proxy_list"] == ["http://127.0.0.1:8080"]

    @patch("sys.argv", ["nhentai", "639456"])
    @patch("nhentai.cli.NHentai")
    @patch("nhentai.cli.Downloader")
    @patch("nhentai.cli.get_console")
    def test_main_without_proxy_list(self, mock_console, mock_downloader, mock_nhentai):
        mock_gallery = MagicMock()
        mock_gallery.title.get.return_value = "Test Gallery"
        mock_gallery.num_pages = 5
        mock_nhentai.return_value = mock_gallery

        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        mock_downloader_instance.download.return_value = [Path("output/test.pdf")]

        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        main()

        mock_downloader.assert_called_once()
        args = mock_downloader.call_args[1]
        assert args["proxy_list"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])