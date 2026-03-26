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

The library supports multiple translation providers.

### [NekoTranslate](https://nekotranslate.ai) (Default)
Anonymous mode is free but quota is per-IP. The library rotates proxies automatically.

```python
from nhentai import NHentai, Downloader, NekoTranslator, NekoEngine, Language

gallery = NHentai("639456")
translator = NekoTranslator()

dl = Downloader(
    gallery,
    output_dir="./downloads",
    translator=translator,
    translate_lang=Language.INDONESIAN,
    translate_engine=NekoEngine.DEEPL,
)
paths = dl.download()
```

### [Comic-Translator](https://comictranslator.com)
Excellent for manga-style translation with visual text replacement. Faster via direct URL translation.

```python
from nhentai import NHentai, Downloader, ComicTranslator, ComicEngine, Language

gallery = NHentai("639456")
translator = ComicTranslator() # auto guest account

dl = Downloader(
    gallery,
    output_dir="./downloads",
    translator=translator,
    translate_lang=Language.ENGLISH,
    translate_engine=ComicEngine.GPT5_MINI,
)
paths = dl.download()
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

# Translate using Neko (default)
nhentai 639456 --translate --lang id --engine deepl

# Translate using Comic-Translator
nhentai 639456 --translate --provider comic --engine GPT-5-mini

# Interactive mode
nhentai -i
```

## Engines

### NekoEngine
| Enum | Value | Name | Auth required |
|---|---|---|---|
| `NekoEngine.GOOGLE` | `google_cloud` | Google Translate | No |
| `NekoEngine.DEEPL` | `deepl` | DeepL | No |
| `NekoEngine.AUTO` | `auto` | Auto-select | No |
| `NekoEngine.DEEPSEEK` | `deepseekv31` | DeepSeek-V3.1 | Yes |
| `NekoEngine.GPT5_MINI` | `gpt5_mini` | GPT-5 mini | Yes |
| `NekoEngine.CLAUDE` | `claude45_sonnet` | Claude Sonnet 4.5 | Yes |
| `NekoEngine.GPT5` | `gpt5` | GPT-5 | Yes |

### ComicEngine
| Enum | Value | Name |
|---|---|---|
| `ComicEngine.GEMINI_FLASH` | `Gemini2.5Flash` | Gemini 2.5 Flash |
| `ComicEngine.GPT5_MINI` | `GPT-5-mini` | GPT-5.1 mini |
| `ComicEngine.GPT5` | `GPT-5.1` | GPT-5.1 |
| `ComicEngine.DEEPSEEK` | `Deepseek` | Deepseek |
| `ComicEngine.GROK` | `Grok4fast` | Grok v4 fast |
| `ComicEngine.KIMI` | `KimiK2` | Kimi K2 |
