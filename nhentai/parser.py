from json import JSONDecodeError, loads

from bs4 import BeautifulSoup


class Parser:
    """Extracts gallery JSON from an nhentai HTML page."""

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def parse_gallery_info(self) -> dict:
        """
        Parse and return the gallery info dict from the embedded ``window._gallery`` script.

        :raises ValueError: If the script tag is missing or JSON is malformed.
        """
        script = self.soup.find(
            "script",
            string=lambda t: t and "window._gallery = JSON.parse(" in t,
        )
        if not script:
            raise ValueError("Gallery data not found. Page may require login or structure has changed.")

        raw = script.string.split("window._gallery = JSON.parse(")[1].split(");")[0]
        try:
            return loads(loads(raw))
        except (JSONDecodeError, ValueError) as exc:
            raise ValueError(f"Failed to parse gallery JSON: {exc}") from exc
