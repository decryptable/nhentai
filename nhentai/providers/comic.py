import os
import tempfile
import time
from pathlib import Path

import requests

from ..enums import ComicEngine, Language
from .base import BaseTranslator, TranslationError

COMIC_SERVER_URL = "https://comictranslator.com/server"
_UPLOAD_TIMEOUT = 60

_COMIC_LANG_MAP = {
    Language.ENGLISH: "English",
    Language.INDONESIAN: "Indonesian",
    Language.JAPANESE: "Japanese",
    Language.KOREAN: "Korean",
    Language.CHINESE: "Chinese",
    Language.FRENCH: "French",
    Language.GERMAN: "German",
    Language.SPANISH: "Spanish",
    Language.PORTUGUESE: "Portuguese",
    Language.ITALIAN: "Italian",
    Language.DUTCH: "Dutch",
    Language.POLISH: "Polish",
    Language.RUSSIAN: "Russian",
    Language.TURKISH: "Turkish",
    Language.ARABIC: "Arabic",
    Language.THAI: "Thai",
    Language.VIETNAMESE: "Vietnamese",
}

class ComicTranslator(BaseTranslator):
    """
    ComicTranslator.com API client.
    Automatically handles guest registration and credit management.
    """

    def __init__(self):
        self.token = None
        self.credits = 0.0
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Origin": "chrome-extension://liquiddev99@comictranslator.com",
            "Referer": "https://comictranslator.com/",
        })

    def _register_guest(self):
        import uuid
        visitor_id = str(uuid.uuid4()).replace("-", "")[:32]
        resp = self._session.post(
            f"{COMIC_SERVER_URL}/user/create-guest",
            json={"guest_id": visitor_id},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("accessToken")
            self.credits = data.get("credits", 0.0)
        else:
            raise TranslationError(f"Failed to register guest: {resp.text}")

    def get_balance(self) -> dict:
        if not self.token:
            try:
                self._register_guest()
            except Exception:
                return {"email": "Guest", "plan": "Free", "level": 0, "quota": 0}

        resp = self._session.get(
            f"{COMIC_SERVER_URL}/user/user-info",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            self.credits = data.get("credits", 0.0)
            return {
                "email": data.get("email", "Guest"),
                "plan": data.get("plan", "Free"),
                "level": 0,
                "quota": self.credits
            }
        return {"email": "Guest", "plan": "Free", "level": 0, "quota": 0}

    def translate_bytes(
        self,
        data: bytes,
        filename: str,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: ComicEngine | str = ComicEngine.GPT5_MINI,
    ) -> bytes:
        suffix = Path(filename).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            return self.translate_file(tmp_path, tgt_lang, engine)
        finally:
            if tmp_path.exists():
                os.unlink(tmp_path)

    def translate_url(
        self,
        url: str,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: ComicEngine | str = ComicEngine.GPT5_MINI,
        referer: str = "https://nhentai.net/",
    ) -> bytes:
        if not self.token or self.credits <= 0:
            self._register_guest()

        tgt_lang_obj = Language(tgt_lang) if not isinstance(tgt_lang, Language) else tgt_lang
        tgt_lang_name = _COMIC_LANG_MAP.get(tgt_lang_obj, "English")
        model = self._map_engine(engine)

        payload = {
            "url": url,
            "referer": referer,
            "toLang": tgt_lang_name,
            "translationModel": model,
            "fontFamily": "WildWords",
            "deeplAPIKey": ""
        }

        try:
            return self._request_v3("POST", f"{COMIC_SERVER_URL}/translate/v3", json=payload)
        except TranslationError as e:
            if any(x in str(e).lower() for x in ["credits", "unauthorized", "expired"]):
                self._register_guest()
                return self._request_v3("POST", f"{COMIC_SERVER_URL}/translate/v3", json=payload)
            raise

    def translate_file(
        self,
        image_path: Path,
        tgt_lang: Language | str = Language.ENGLISH,
        engine: ComicEngine | str = ComicEngine.GPT5_MINI,
    ) -> bytes:
        if not self.token or self.credits <= 0:
            self._register_guest()

        tgt_lang_obj = Language(tgt_lang) if not isinstance(tgt_lang, Language) else tgt_lang
        tgt_lang_name = _COMIC_LANG_MAP.get(tgt_lang_obj, "English")
        model = self._map_engine(engine)

        try:
            return self._upload_v3(image_path, tgt_lang_name, model)
        except TranslationError as e:
            if any(x in str(e).lower() for x in ["credits", "unauthorized", "expired"]):
                self._register_guest()
                return self._upload_v3(image_path, tgt_lang_name, model)
            raise

    def _map_engine(self, engine: ComicEngine | str) -> str:
        if isinstance(engine, ComicEngine):
            return engine.value
        return str(engine)

    def _request_v3(self, method: str, url: str, **kwargs) -> bytes:
        resp = self._session.request(
            method,
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            **kwargs,
            timeout=_UPLOAD_TIMEOUT
        )
        if resp.status_code != 200:
            raise TranslationError(f"Request failed: {resp.text}")

        return self._handle_response(resp)

    def _upload_v3(self, image_path: Path, to_lang: str, model: str) -> bytes:
        mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        with open(image_path, "rb") as f:
            resp = self._session.post(
                f"{COMIC_SERVER_URL}/upload/v3",
                headers={"Authorization": f"Bearer {self.token}"},
                data={
                    "toLang": to_lang,
                    "translationModel": model,
                    "fontFamily": "WildWords",
                    "deeplAPIKey": ""
                },
                files={"file": (image_path.name, f, mime)},
                timeout=_UPLOAD_TIMEOUT
            )

        if resp.status_code != 200:
            raise TranslationError(f"Upload failed: {resp.text}")

        return self._handle_response(resp)

    def _handle_response(self, resp: requests.Response) -> bytes:
        content_type = resp.headers.get("Content-Type", "")
        if "image" in content_type:
            return resp.content

        try:
            data = resp.json()
            if "cached_url" in data:
                return self._session.get(data["cached_url"]).content
            if "task_id" in data:
                return self._poll_task(data["task_id"])
            raise TranslationError(f"Unexpected response: {data}")
        except Exception as e:
            if "image" not in content_type:
                raise TranslationError(f"Failed to process response: {e}") from e
            return resp.content

    def _poll_task(self, task_id: str) -> bytes:
        max_attempts = 70
        poll_interval = 0.7
        for _ in range(max_attempts):
            resp = self._session.get(
                f"{COMIC_SERVER_URL}/task/{task_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                if status == "completed":
                    url = data.get("translated_url")
                    if url:
                        return self._session.get(url).content
                    raise TranslationError("Task completed but no URL returned.")
                if status == "failed":
                    raise TranslationError("Translation task failed.")
            time.sleep(poll_interval)
        raise TranslationError("Translation timed out.")
