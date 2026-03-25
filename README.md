# nhentai

Python library to download galleries from nhentai, with optional translation and PDF export.

## Installation

```bash
pip install git+https://github.com/decryptable/nhentai.git
```

With optional extras:

```bash
# PDF export support
pip install "nhentai[pdf] @ git+https://github.com/decryptable/nhentai.git"

# SOCKS proxy support
pip install "nhentai[socks] @ git+https://github.com/decryptable/nhentai.git"

# Everything
pip install "nhentai[all] @ git+https://github.com/decryptable/nhentai.git"
```

## Usage

### As a library

```python
from nhentai import NHentai, Downloader, NekoTranslator, Engine, Language

gallery = NHentai("639456")
print(gallery.title["pretty"])
print(f"{gallery.num_pages} pages")

# Download only
dl = Downloader(gallery, output_dir="./downloads")
paths = dl.download()

# Download + translate to Indonesian
translator = NekoTranslator()              # anonymous (free quota)
# translator = NekoTranslator(token="…")  # authenticated

dl = Downloader(
    gallery,
    output_dir="./downloads",
    translator=translator,
    translate_lang=Language.INDONESIAN,
    translate_engine=Engine.DEEPL,
)
paths = dl.download()

# Download + translate + PDF
pdf = dl.download(make_pdf=True)
```

### As a CLI

```bash
# Basic download
nhentai 639456

# Download and translate to Indonesian
nhentai 639456 --translate --lang id

# Download, translate, and export PDF
nhentai 639456 --translate --lang id --pdf

# With authentication token
nhentai 639456 --translate --token YOUR_TOKEN --engine claude

# Custom output directory and workers
nhentai 639456 -o ./manga -w 8
```

## Documentation

Full API docs: <https://decryptable.github.io/nhentai>

## Requirements

- Python ≥ 3.11
- `requests`, `beautifulsoup4`, `urllib3`
- `Pillow` (optional, for PDF export)
- `requests[socks]` (optional, for SOCKS proxy support)
