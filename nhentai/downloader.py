import random
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests
import urllib3

from .enums import Language
from .nhentai import NHentai
from .translator import TranslationError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://nhentai.net/",
}


class DownloadError(Exception):
    """Raised when a page download fails."""


class Downloader:
    """
    Downloads pages from an :class:`NHentai` gallery, with optional translation and PDF export.

    :param gallery: Parsed gallery object.
    :param output_dir: Root directory for downloads. Gallery pages go into ``<output_dir>/<gallery_id>/``.
    :param workers: Number of parallel download threads.
    :param translator: Optional :class:`NekoTranslator`. If provided, each page is translated before saving.
    :param translate_lang: Target language for translation.
    :param translate_engine: Engine to use for translation.
    :param timeout: Per-request timeout in seconds.
    """

    def __init__(
        self,
        gallery: NHentai,
        output_dir: str | Path = ".",
        workers: int = 4,
        translator: Any | None = None,
        translate_lang: Language | str = Language.ENGLISH,
        translate_engine: str | Any = "deepl",
        timeout: int = 30,
        proxy_list: list[str] | None = None,
    ):
        self.gallery = gallery
        self.output_dir = Path(output_dir)
        self.workers = max(1, workers)
        self.translator: Any | None = translator
        self.translate_lang = Language(translate_lang) if not isinstance(translate_lang, Language) else translate_lang
        self.translate_engine = translate_engine
        self.timeout = timeout
        self.proxy_list = proxy_list or []

    def download(self, make_pdf: bool = False, progress_callback: Callable[[int, int, str], None] | None = None) -> list[Path]:
        """
        Download all pages. Returns a list of saved file paths (or a single PDF path if ``make_pdf=True``).

        :param make_pdf: Compile pages into a PDF after downloading. Requires Pillow.
        :param progress_callback: Optional callback to report progress: (current, total, status).
        :raises DownloadError: If a page fails to download.
        :raises RuntimeError: If ``make_pdf=True`` but Pillow is not installed.
        """
        import concurrent.futures

        gallery_target_dir = self.output_dir / str(self.gallery.id)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            urls = self.gallery.get_image_urls()
            results: list[Path | None] = [None] * len(urls)
            total = len(urls)

            def _update_progress(current: int, status: str):
                if progress_callback:
                    progress_callback(current, total, status)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures = {
                    pool.submit(self._download_page, url, tmp_path, i + 1, _update_progress): i
                    for i, url in enumerate(urls)
                }
                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    try:
                        results[idx] = future.result()
                    except Exception as exc:
                        # If one fails, we might want to cancel others or just let them finish/error
                        raise DownloadError(f"Failed to download page {idx + 1}: {exc}") from exc

            paths = [p for p in results if p is not None]

            if make_pdf:
                self.output_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = self._make_pdf(paths, self.output_dir)
                return [pdf_path]

            # If not PDF, move from temp to final destination
            gallery_target_dir.mkdir(parents=True, exist_ok=True)
            final_paths = []
            for p in paths:
                target = gallery_target_dir / p.name
                shutil.move(str(p), str(target))
                final_paths.append(target)
            return final_paths

    def _download_page(self, url: str, dest_dir: Path, page_num: int, progress_callback: Callable[[int, str], None] | None = None) -> Path:
        ext = url.rsplit(".", 1)[-1]
        out_path = dest_dir / f"{page_num:04d}.{ext}"

        if out_path.exists():
            return out_path

        # Try direct URL translation if supported (faster)
        if self.translator is not None and hasattr(self.translator, "translate_url"):
            if progress_callback:
                progress_callback(page_num, f"Translating page {page_num} (direct)")
            try:
                data = self.translator.translate_url(
                    url,
                    tgt_lang=self.translate_lang,
                    engine=self.translate_engine,
                    referer="https://nhentai.net/"
                )
                out_path = dest_dir / f"{page_num:04d}_translated.jpg"
                out_path.write_bytes(data)
                return out_path
            except (TranslationError, ConnectionError, Exception):
                pass

        if progress_callback:
            progress_callback(page_num, f"Downloading page {page_num}")

        data = self._fetch(url)

        if self.translator is not None:
            if progress_callback:
                progress_callback(page_num, f"Translating page {page_num}")
            try:
                data = self.translator.translate_bytes(
                    data,
                    filename=f"page.{ext}",
                    tgt_lang=self.translate_lang,
                    engine=self.translate_engine,
                )
                out_path = dest_dir / f"{page_num:04d}_translated.jpg"
            except (TranslationError, ConnectionError):
                pass

        out_path.write_bytes(data)
        if progress_callback:
            progress_callback(page_num, f"Saved page {page_num}")
        return out_path

    def _fetch(self, url: str) -> bytes:
        proxies = None
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            proxies = {"http": proxy, "https": proxy}

        try:
            resp = requests.get(
                url,
                headers=_DEFAULT_HEADERS,
                verify=False,
                timeout=self.timeout,
                stream=True,
                proxies=proxies,
            )
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.HTTPError as exc:
            raise DownloadError(f"HTTP {exc.response.status_code}: {url}") from exc
        except requests.exceptions.Timeout as exc:
            raise DownloadError(f"Timeout: {url}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise DownloadError(f"Connection error: {url}: {exc}") from exc

    def _make_pdf(self, image_paths: list[Path], dest_dir: Path) -> Path:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "Pillow is required for PDF export. Install with: pip install Pillow"
            ) from exc

        if not image_paths:
            raise ValueError("No images to create PDF from.")

        images = []
        for p in sorted(image_paths):
            try:
                images.append(Image.open(p).convert("RGB"))
            except Exception as exc:
                raise DownloadError(f"Failed to open {p} for PDF: {exc}") from exc

        # Use gallery title or ID for PDF filename
        title = self.gallery.title.get("pretty") or self.gallery.title.get("english") or str(self.gallery.id)
        # Sanitize filename (remove characters that might be invalid in some filesystems)
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
        filename = f"{safe_title} ({self.gallery.id}).pdf"

        pdf_path = dest_dir / filename
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        return pdf_path
