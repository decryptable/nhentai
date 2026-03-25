from .cdn import CDN
from .grabber import Grabber
from .parser import Parser


class NHentai:
    """
    Fetches and exposes metadata for a single nhentai gallery.

    Accepts either a full URL (``https://nhentai.net/g/639456/``) or a bare gallery ID (``"639456"``).
    """

    BASE_URL = "https://nhentai.net"

    def __init__(self, url: str):
        """
        :param url: Gallery URL or numeric ID string.
        :raises ConnectionError: If the page cannot be fetched.
        :raises ValueError: If gallery data cannot be parsed.
        """
        if not url.startswith("http"):
            url = f"{self.BASE_URL}/g/{url.strip('/')}"
        self.url = url
        self._grabber = Grabber(url)
        self._cdn = CDN()
        self._info = Parser(self._grabber.get_html()).parse_gallery_info()

    @property
    def id(self) -> int:
        """Gallery ID."""
        return int(self._info["id"])

    @property
    def media_id(self) -> int:
        """Internal media ID used in CDN URLs."""
        return int(self._info["media_id"])

    @property
    def title(self) -> dict:
        """Dict with keys ``english``, ``japanese``, ``pretty``."""
        return self._info["title"]

    @property
    def num_pages(self) -> int:
        """Total number of pages."""
        return self._info["num_pages"]

    @property
    def num_favorites(self) -> int:
        """Number of times this gallery has been favorited."""
        return self._info["num_favorites"]

    @property
    def upload_date(self) -> int:
        """Upload timestamp (Unix epoch)."""
        return self._info["upload_date"]

    @property
    def tags(self) -> list[dict]:
        """Tags of type ``tag``."""
        return [t for t in self._info["tags"] if t["type"] == "tag"]

    @property
    def artists(self) -> list[dict]:
        """Tags of type ``artist``."""
        return [t for t in self._info["tags"] if t["type"] == "artist"]

    @property
    def groups(self) -> list[dict]:
        """Tags of type ``group``."""
        return [t for t in self._info["tags"] if t["type"] == "group"]

    @property
    def languages(self) -> list[dict]:
        """Tags of type ``language``."""
        return [t for t in self._info["tags"] if t["type"] == "language"]

    @property
    def categories(self) -> list[dict]:
        """Tags of type ``category``."""
        return [t for t in self._info["tags"] if t["type"] == "category"]

    @property
    def pages_info(self) -> list[dict]:
        """Raw page info list from gallery JSON (contains ``t``, ``w``, ``h`` per page)."""
        return self._info["images"]["pages"]

    def get_image_urls(self) -> list[str]:
        """Full-resolution image URLs for all pages, in order."""
        return [
            self._cdn.get_image_url(
                self.media_id, i + 1,
                ext=CDN.ext_from_type(page["t"])
            )
            for i, page in enumerate(self.pages_info)
        ]

    def get_cover_url(self) -> str:
        """Cover image URL."""
        ext = CDN.ext_from_type(self._info["images"]["cover"]["t"])
        return self._cdn.get_cover_url(self.media_id, ext)

    def info(self) -> dict:
        """Raw gallery info dict as returned by the API."""
        return self._info
