import argparse
import logging
import os
import signal
import sys

from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm, Prompt

from .downloader import Downloader, DownloadError
from .enums import Engine, Language
from .nhentai import NHentai
from .translator import NekoTranslator


def _signal_handler(sig, frame):
    print("\nInterrupted.")
    os._exit(130)


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )


def get_console():
    try:
        return Console(force_terminal=True, soft_wrap=True)
    except Exception:
        return Console(force_terminal=False, soft_wrap=True)


def interactive_mode():
    console = get_console()

    console.print("[bold]Interactive Mode[/bold]")
    console.print()

    url = Prompt.ask("Enter gallery URL or ID")
    if not url.strip():
        console.print("[red]URL/ID is required.[/red]")
        sys.exit(1)

    output = Prompt.ask("Output directory", default=".")
    workers = Prompt.ask("Parallel download workers", default="4")

    try:
        workers = int(workers)
        if workers <= 0:
            raise ValueError
    except ValueError:
        console.print("[red]Workers must be a positive integer.[/red]")
        sys.exit(1)

    translate = Confirm.ask("Translate pages?", default=False)

    lang = Language.ENGLISH.value
    engine = Engine.DEEPL.value
    token = None

    if translate:
        lang = Prompt.ask(
            "Target language",
            choices=[lang.value for lang in Language],
            default=Language.ENGLISH.value
        )
        engine = Prompt.ask(
            "Translation engine",
            choices=[e.value for e in Engine],
            default=Engine.DEEPL.value
        )
        token = Prompt.ask("NekoTranslate Bearer token (leave empty to skip)", password=True)

    make_pdf = Confirm.ask("Generate PDF?", default=True)
    verbose = Confirm.ask("Enable verbose logging?", default=False)
    use_proxy = Confirm.ask("Use proxy?", default=False)

    proxy_list = None
    proxy_type = "http"

    if use_proxy:
        proxy_list = Prompt.ask("Proxy list file path")
        proxy_type = Prompt.ask(
            "Default proxy type",
            choices=["http", "https", "socks4", "socks5"],
            default="http"
        )

    return argparse.Namespace(
        url=url,
        output=output,
        workers=workers,
        translate=translate,
        lang=lang,
        engine=engine,
        token=token,
        make_pdf=make_pdf,
        verbose=verbose,
        proxy_list=proxy_list,
        proxy_type=proxy_type,
        interactive=True
    )


def parse_proxy_list(path_or_url: str, default_type: str = "http"):
    import requests
    proxies = []
    try:
        if path_or_url.startswith(("http://", "https://")):
            # Treat as URL
            resp = requests.get(path_or_url, timeout=30)
            resp.raise_for_status()
            content = resp.text
        else:
            # Treat as local file path
            with open(path_or_url, encoding="utf-8") as f:
                content = f.read()

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if "://" in line:
                proxies.append(line)
            else:
                proxies.append(f"{default_type}://{line}")
    except Exception as exc:
        logging.warning(f"Failed to load proxy list: {exc}")
    return proxies


def main():
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(
        prog="nhentai",
        description="nhentai downloader with optional translation",
    )
    parser.add_argument("url", nargs="?", help="Gallery URL or ID (e.g. 639456 or https://nhentai.net/g/639456/)")
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
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--proxy-list", help="Path to proxy list file")
    parser.add_argument("--proxy-type", default="http", choices=["http", "https", "socks4", "socks5"],
                        help="Default proxy type if not specified in list (default: http)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Use interactive mode")
    args = parser.parse_args()

    if args.interactive:
        args = interactive_mode()

    if not args.url:
        print("Error: URL or ID is required.")
        sys.exit(1)

    setup_logging(verbose=args.verbose)
    console = get_console()

    try:
        gallery = NHentai(args.url)
    except (ConnectionError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    title = gallery.title.get("pretty") or gallery.title.get("english", f"#{gallery.id}")
    console.print(f"[bold]{title}[/bold] ([cyan]{gallery.num_pages}[/cyan] pages)")

    translator = None
    if args.translate:
        translator = NekoTranslator(token=args.token)

    proxy_list = parse_proxy_list(args.proxy_list, args.proxy_type) if args.proxy_list else []

    downloader = Downloader(
        gallery=gallery,
        output_dir=args.output,
        workers=args.workers,
        translator=translator,
        translate_lang=args.lang,
        translate_engine=args.engine,
        proxy_list=proxy_list,
    )

    def progress_callback(current: int, total: int, status: str):
        # Truncate long status messages to prevent UI breakage
        max_status_length = console.width - 15  # Leave space for " X/XXX" part
        if len(status) > max_status_length:
            status = status[:max_status_length-3] + "..."
        console.print(f"[dim]{status}[/dim] {current}/{total}")

    try:
        results = downloader.download(make_pdf=not args.no_pdf, progress_callback=progress_callback)
    except DownloadError as exc:
        console.print(f"[red]Download error:[/red] {exc}")
        sys.exit(1)

    console.print(f"[green]Done.[/green] Saved to: {results[0]}")
