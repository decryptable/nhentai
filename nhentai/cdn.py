import random

EXT_MAP = {"j": "jpg", "p": "png", "w": "webp", "g": "gif"}


class CDN:
    """Builds nhentai CDN image URLs with random host selection for load balancing."""

    _thumb_hosts = ["t1.nhentai.net", "t2.nhentai.net", "t3.nhentai.net", "t4.nhentai.net"]
    _image_hosts = ["i1.nhentai.net", "i2.nhentai.net", "i3.nhentai.net", "i4.nhentai.net"]

    def get_image_url(self, media_id: int, page: int, ext: str = "webp") -> str:
        """Full-resolution page URL."""
        host = random.choice(self._image_hosts)
        return f"https://{host}/galleries/{media_id}/{page}.{ext}"

    def get_thumb_url(self, media_id: int, page: int, ext: str = "webp") -> str:
        """Thumbnail URL for a specific page."""
        host = random.choice(self._thumb_hosts)
        return f"https://{host}/galleries/{media_id}/{page}t.{ext}"

    def get_cover_url(self, media_id: int, ext: str = "webp") -> str:
        """Cover image URL."""
        host = random.choice(self._thumb_hosts)
        return f"https://{host}/galleries/{media_id}/cover.{ext}"

    @staticmethod
    def ext_from_type(t: str) -> str:
        """Convert nhentai page type code (``j``/``p``/``w``/``g``) to file extension."""
        return EXT_MAP.get(t, "jpg")
