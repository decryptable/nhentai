# nhentai

A Python library to download nhentai galleries with optional manga translation and PDF export.

## Features

- Parallel downloads with configurable worker threads
- Translation via [NekoTranslate](https://nekotranslate.ai), with automatic proxy rotation for anonymous use
- PDF export — compile a gallery into a single file
- Type-safe `Engine` and `Language` enums with full IDE autocomplete
- CLI — usable without writing code

## Installation

```bash
pip install git+https://github.com/decryptable/nhentai.git
```

With optional extras:

```bash
# PDF support
pip install "nhentai[pdf] @ git+https://github.com/decryptable/nhentai.git"

# SOCKS proxy support
pip install "nhentai[socks] @ git+https://github.com/decryptable/nhentai.git"

# Everything
pip install "nhentai[all] @ git+https://github.com/decryptable/nhentai.git"
```

## Quick start

```python
from nhentai import NHentai, Downloader

gallery = NHentai("639456")
print(gallery.title["pretty"])

dl = Downloader(gallery, output_dir="./downloads")
paths = dl.download()
```

See [Getting Started](getting-started.md) for more examples.
