# Getting Started

## Installation

<!-- termynal -->
```bash
$ pip install git+https://github.com/decryptable/nhentai.git
---> 100%
Successfully installed nhentai-0.1.2
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

PDF export requires `Pillow`.

<!-- termynal -->
```bash
$ pip install "nhentai[pdf] @ git+https://github.com/decryptable/nhentai.git"
---> 100%
Successfully installed Pillow-10.2.0
```

## CLI

### Basic Download
<!-- termynal -->
```bash
$ nhentai 639456
[Neko's Adventure] (24 pages)
Downloading... 1/24
Downloading... 12/24
Downloading... 24/24
Done. Saved to: ./639456/639456.pdf
```

### With Translation (Neko)
<!-- termynal -->
```bash
$ nhentai 639456 --translate --lang id --engine deepl
[Neko's Adventure] (24 pages)
Translating (deepl)... 1/24
Translating (deepl)... 12/24
Translating (deepl)... 24/24
Done. Saved to: ./639456/639456.pdf
```

### With Translation (Comic-Translator)
<!-- termynal -->
```bash
$ nhentai 639456 --translate --provider comic --engine GPT-5-mini
[Neko's Adventure] (24 pages)
Translating (GPT-5-mini)... 1/24
Translating (GPT-5-mini)... 24/24
Done. Saved to: ./639456/639456.pdf
```

### Interactive Mode
<!-- termynal -->
```bash
$ nhentai -i
Interactive Mode
> Enter gallery URL or ID: 639456
> Output directory (.): .
> Parallel download workers (4): 8
> Translate pages? (y/n): y
> Translation provider (neko/comic): neko
> Target language (en/id/jp/zh): id
> Translation engine (google_cloud/deepl/auto/deepseekv31/gpt5_mini/claude45_sonnet/gpt5): deepl
> NekoTranslate Bearer token (leave empty to skip): 
> Generate PDF? (y/n): y
> Enable verbose logging? (y/n): n
> Use proxy? (y/n): n
[Neko's Adventure] (24 pages)
Done. Saved to: ./639456/639456.pdf
```

### Help
<!-- termynal -->
```bash
$ nhentai --help
usage: nhentai [-h] [--version] [url] [-o OUTPUT] [-w WORKERS] [--translate] 
               [--provider {neko,comic}] [--lang {en,id,jp,zh}]
               [--engine ENGINE] [--token TOKEN] [--no-pdf] [--interactive]

nhentai downloader with optional translation
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
