import argparse
import os
import signal
import sys
from pathlib import Path

from .downloader import Downloader, DownloadError
from .enums import Engine, Language
from .nhentai import NHentai
from .translator import NekoTranslator


def _signal_handler(sig, frame):
    print("\nInterrupted.")
    os._exit(130)


def main():
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(
        prog="nhentai",
        description="nhentai downloader with optional translation",
    )
    parser.add_argument("url", help="Gallery URL or ID (e.g. 639456 or https://nhentai.net/g/639456/)")
    parser.add_argument("-o", "--output", default=".", help="Output directory (default: .)")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Parallel download workers (default: 4)")
    parser.add_argument("--translate", action="store_true", help="Translate pages before saving")
    parser.add_argument("--lang", default=Language.ENGLISH.value,
                        choices=[lang.value for lang in Language],
                        metavar="LANG",
                        help=f"Target language (default: {Language.ENGLISH.value})")
    parser.add_argument(
        "--engine", default=Engine.DEEPL.value,
        choices=[e.value for e in Engine],
        metavar="ENGINE",
        help=f"Translation engine (default: {Engine.DEEPL.value}). Choices: {', '.join(e.value for e in Engine)}"
    )
    parser.add_argument("--token", default=None, help="NekoTranslate Bearer token")
    args = parser.parse_args()

    try:
        gallery = NHentai(args.url)
    except (ConnectionError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    title = gallery.title.get("pretty") or gallery.title.get("english", f"#{gallery.id}")
    print(f"{title} ({gallery.num_pages} pages)")

    translator = None
    if args.translate:
        translator = NekoTranslator(token=args.token)

    downloader = Downloader(
        gallery=gallery,
        output_dir=args.output,
        workers=args.workers,
        translator=translator,
        translate_lang=args.lang,
        translate_engine=args.engine,
    )

    try:
        results = downloader.download(make_pdf=True)
    except DownloadError as exc:
        print(f"Download error: {exc}")
        sys.exit(1)

    print(f"PDF saved to: {results[0]}")
