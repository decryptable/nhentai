import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://nhentai.net/",
}


class Grabber:
    """Fetches raw HTML or image bytes from a URL with nhentai-compatible headers."""

    def __init__(self, url: str, timeout: int = 30, headers: dict | None = None):
        """
        :param url: Target URL.
        :param timeout: Request timeout in seconds.
        :param headers: Additional headers merged with defaults.
        """
        self.url = url
        self.timeout = timeout
        self.headers = {**_DEFAULT_HEADERS, **(headers or {})}

    def get_html(self) -> str:
        """Fetch and return the HTML of :attr:`url`.

        :raises ConnectionError: On HTTP error, timeout, or network failure.
        """
        try:
            resp = requests.get(
                self.url, headers=self.headers, verify=False,
                timeout=self.timeout, allow_redirects=True,
            )
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as exc:
            raise ConnectionError(f"HTTP {exc.response.status_code} fetching {self.url}") from exc
        except requests.exceptions.Timeout as exc:
            raise ConnectionError(f"Request timed out after {self.timeout}s: {self.url}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"Network error fetching {self.url}: {exc}") from exc

    def download_bytes(self, url: str) -> bytes:
        """Download and return raw bytes from *url*.

        :raises ConnectionError: On HTTP error, timeout, or network failure.
        """
        try:
            resp = requests.get(
                url, headers=self.headers, verify=False,
                timeout=self.timeout, stream=True,
            )
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.HTTPError as exc:
            raise ConnectionError(f"HTTP {exc.response.status_code} downloading {url}") from exc
        except requests.exceptions.Timeout as exc:
            raise ConnectionError(f"Download timed out: {url}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"Network error downloading {url}: {exc}") from exc
