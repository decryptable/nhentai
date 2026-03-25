import os
import tempfile
import time
from itertools import cycle
from pathlib import Path

import requests
import requests.exceptions
import urllib3

from .enums import Engine, Language

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://nekotranslate.ai/api/v2"
PLAN_NAMES = ["Free", "Lite", "Standard", "Ultimate"]

_UPLOAD_TIMEOUT     = 60
_POLL_TIMEOUT       = 15
_DOWNLOAD_TIMEOUT   = 60
_POLL_INTERVAL      = 2
_POLL_MAX_RETRIES   = 5
_QUOTA_SCAN_TIMEOUT = 8
_PROXY_MAX_ATTEMPTS = 15


class TranslationError(Exception):
    """Raised when the NekoTranslate server reports a translation failure."""


def _parse_proxy(entry: str) -> dict:
    entry = entry.strip()
    if "://" not in entry:
        entry = f"http://{entry}"
    return {"http": entry, "https": entry}


def _fmt_error(resp: requests.Response) -> str:
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text or str(resp.status_code)
    return f"HTTP {resp.status_code}: {detail}"


class NekoTranslator:
    """
    NekoTranslate API client.

    Anonymous (no token): uses free quota per IP, rotates proxies automatically.
    Authenticated: pass token from nhentai.net localStorage.
    """

    def __init__(
        self,
        token: str | None = None,
        proxy_list_url: str | None = None,
        proxies: list[str] | None = None,
    ):
        """
        :param token: Bearer token for authenticated requests (optional).
        :param proxy_list_url: URL to a plain-text proxy list. Defaults to proxifly socks5 list.
        :param proxies: Explicit proxy list (overrides proxy_list_url).
        """
        self.token = token
        self.headers: dict[str, str] = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

        raw = proxies or self._fetch_proxies(proxy_list_url)
        self._proxy_list = [_parse_proxy(p) for p in raw if p.strip()]
        self._proxy_cycle = cycle(self._proxy_list) if self._proxy_list else None

    @staticmethod
    def _fetch_proxies(url: str | None = None) -> list[str]:
        if not url:
            url = (
                "https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt"
            )
        try:
            resp = requests.get(url, timeout=10)
            return [line.strip() for line in resp.text.splitlines() if line.strip()]
        except Exception:
            return []

    def _request(
        self,
        method: str,
        url: str,
        use_proxy: bool = False,
        force_proxy: dict | None = None,
        **kwargs,
    ) -> requests.Response:
        if force_proxy:
            return requests.request(method, url, proxies=force_proxy, verify=False, **kwargs)
        if not use_proxy or not self._proxy_cycle:
            return requests.request(method, url, **kwargs)

        last_exc = None
        for _ in range(_PROXY_MAX_ATTEMPTS):
            proxy = next(self._proxy_cycle)
            try:
                resp = requests.request(method, url, proxies=proxy, verify=False, **kwargs)
                if resp.status_code != 429:
                    return resp
            except requests.exceptions.RequestException as exc:
                last_exc = exc
        if last_exc:
            raise last_exc
        raise ConnectionError("All proxy attempts failed.")

    def find_proxy_with_quota(self) -> dict | None:
        """Returns the first proxy with remaining anonymous quota, or None."""
        for proxy in self._proxy_list:
            try:
                resp = requests.get(
                    f"{BASE_URL}/get-quota",
                    proxies=proxy,
                    verify=False,
                    timeout=_QUOTA_SCAN_TIMEOUT,
                )
                if resp.status_code == 200 and resp.json().get("quota", 0) > 0:
                    return proxy
            except requests.exceptions.RequestException:
                continue
        return None

    def get_balance(self) -> dict:
        """Returns ``{"email", "plan", "level", "quota"}``."""
        result: dict = {"email": None, "plan": PLAN_NAMES[0], "level": 0, "quota": None}

        if self.token:
            try:
                resp = self._request(
                    "GET", f"{BASE_URL}/get-user", headers=self.headers, timeout=_POLL_TIMEOUT,
                )
                if resp.status_code == 200:
                    user = resp.json()
                    result["email"] = user.get("email")
                    level = user.get("level", 0)
                    result["level"] = level
                    result["plan"] = PLAN_NAMES[level] if level < len(PLAN_NAMES) else f"Level {level}"
            except requests.exceptions.RequestException:
                pass

        try:
            resp = self._request(
                "GET", f"{BASE_URL}/get-quota",
                headers=self.headers,
                use_proxy=bool(self._proxy_list),
                timeout=_POLL_TIMEOUT,
            )
            if resp.status_code == 200:
                result["quota"] = resp.json().get("quota")
        except requests.exceptions.RequestException:
            pass

        return result

    def translate_file(
        self,
        image_path: str | Path,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: Engine | str = Engine.DEEPL,
    ) -> bytes:
        """
        Translate an image file and return the result as bytes.

        :param image_path: Path to the source image.
        :param tgt_lang: Target language (``Language`` enum or ISO code string).
        :param engine: Translation engine (``Engine`` enum or string).
        :raises FileNotFoundError: If image_path does not exist.
        :raises TranslationError: On API rejection or failure.
        :raises ConnectionError: On network issues.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        if not image_path.is_file():
            raise ValueError(f"Not a file: {image_path}")

        engine = Engine(engine)
        tgt_lang = Language(tgt_lang) if not isinstance(tgt_lang, Language) else tgt_lang

        force_proxy = None
        if not self.token and self._proxy_list:
            force_proxy = self.find_proxy_with_quota()
            if force_proxy is None:
                raise TranslationError("All proxies have exhausted anonymous quota.")

        manga_id = self._upload(image_path, tgt_lang, engine, force_proxy)
        result_url = self._poll(manga_id)
        return self._download(result_url)

    def translate_bytes(
        self,
        data: bytes,
        filename: str,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: Engine | str = Engine.DEEPL,
    ) -> bytes:
        """
        Translate raw image bytes. Writes to a temp file, translates, returns result bytes.

        :param data: Raw image bytes.
        :param filename: Used only to determine file extension.
        """
        suffix = Path(filename).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            return self.translate_file(tmp_path, tgt_lang, engine)
        finally:
            os.unlink(tmp_path)

    def _upload(self, image_path: Path, tgt_lang: Language, engine: Engine, force_proxy: dict | None) -> str:
        mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        try:
            with open(image_path, "rb") as f:
                resp = self._request(
                    "POST", f"{BASE_URL}/translate",
                    use_proxy=True,
                    force_proxy=force_proxy,
                    headers=self.headers,
                    data={"tgt_lang": tgt_lang.value, "engine": engine.value},
                    files={"files": (image_path.name, f, mime)},
                    timeout=_UPLOAD_TIMEOUT,
                )
        except requests.exceptions.Timeout as exc:
            raise ConnectionError(f"Upload timed out after {_UPLOAD_TIMEOUT}s.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"Connection lost during upload: {exc}") from exc

        if resp.status_code != 200:
            raise TranslationError(f"Upload rejected — {_fmt_error(resp)}")

        manga_id = resp.json().get("manga_id")
        if not manga_id:
            raise TranslationError("Server returned no manga_id.")
        return manga_id

    def _poll(self, manga_id: str) -> str:  # noqa: PLR0912
        poll_url = f"{BASE_URL}/get-manga/{manga_id}"
        result_url = f"{BASE_URL}/static/mangas/{manga_id}/1.jpeg"
        errors = 0

        while True:
            try:
                resp = self._request("GET", poll_url, headers=self.headers, timeout=_POLL_TIMEOUT)
                errors = 0
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                errors += 1
                if errors >= _POLL_MAX_RETRIES:
                    raise ConnectionError("Polling failed too many times in a row.") from exc
                time.sleep(_POLL_INTERVAL)
                continue

            if resp.status_code != 200:
                errors += 1
                if errors >= _POLL_MAX_RETRIES:
                    raise ConnectionError(f"Poll returned {resp.status_code} repeatedly.")
            else:
                state = resp.json().get("state", "unknown")
                if state == "completed":
                    return result_url
                if state == "failed":
                    raise TranslationError(
                        f"Server reported failure: {resp.json().get('detail', 'unknown')}"
                    )
                errors = 0

            time.sleep(_POLL_INTERVAL)

    def _download(self, url: str) -> bytes:
        try:
            resp = requests.get(url, timeout=_DOWNLOAD_TIMEOUT)
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.Timeout as exc:
            raise ConnectionError("Download timed out.") from exc
        except requests.exceptions.HTTPError as exc:
            raise ConnectionError(f"Download failed: HTTP {exc.response.status_code}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"Download connection error: {exc}") from exc
