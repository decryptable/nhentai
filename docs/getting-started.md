# Getting Started

## Installation

```bash
pip install "nhentai[all] @ git+https://github.com/decryptable/nhentai.git"
```

## Basic download

```python
from nhentai import NHentai, Downloader

gallery = NHentai("639456")          # accepts URL or bare ID
print(gallery.title["pretty"])
print(f"{gallery.num_pages} pages, {gallery.num_favorites} favorites")

dl = Downloader(gallery, output_dir="./downloads", workers=8)
paths = dl.download()
print(f"Saved {len(paths)} pages to {paths[0].parent}")
```

## With translation

Translation uses [NekoTranslate](https://nekotranslate.ai).
Anonymous mode is free but quota is per-IP. The library scans proxies automatically
to find one with remaining credits.

```python
from nhentai import NHentai, Downloader, NekoTranslator, Engine, Language

gallery = NHentai("639456")
translator = NekoTranslator()        # anonymous, auto proxy

dl = Downloader(
    gallery,
    output_dir="./downloads",
    translator=translator,
    translate_lang=Language.INDONESIAN,
    translate_engine=Engine.DEEPL,
)
paths = dl.download()
```

### Authenticated

```python
translator = NekoTranslator(token="YOUR_BEARER_TOKEN")
```

## Export to PDF

```python
pdf_path = dl.download(make_pdf=True)[0]
print(f"PDF saved to {pdf_path}")
```

PDF export requires `Pillow`. Install with `pip install nhentai[pdf]`.

## CLI

```bash
# Download only
nhentai 639456

# Translate to Indonesian
nhentai 639456 --translate --lang id

# Translate and export PDF
nhentai 639456 --translate --lang id --pdf

# Custom engine, output directory, and workers
nhentai 639456 --translate --engine google_cloud -o ./manga -w 8
```

## Engines

| Enum | Value | Name | Auth required |
|---|---|---|---|
| `Engine.GOOGLE` | `google_cloud` | Google Translate | No |
| `Engine.DEEPL` | `deepl` | DeepL | No |
| `Engine.AUTO` | `auto` | Auto-select | No |
| `Engine.DEEPSEEK` | `deepseekv31` | DeepSeek-V3.1 | Yes |
| `Engine.GPT5_MINI` | `gpt5_mini` | GPT-5 mini | Yes |
| `Engine.CLAUDE` | `claude45_sonnet` | Claude Sonnet 4.5 | Yes |
| `Engine.GPT5` | `gpt5` | GPT-5 | Yes |
