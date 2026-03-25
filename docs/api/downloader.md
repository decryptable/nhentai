# Downloader

Downloads pages from a gallery with optional per-page translation and PDF export.

```python
from nhentai import NHentai, Downloader, NekoTranslator, Engine, Language

gallery = NHentai("639456")

# Download only
dl = Downloader(gallery, output_dir="./downloads", workers=8)
paths = dl.download()

# Download + translate + PDF
translator = NekoTranslator()
dl = Downloader(
    gallery,
    output_dir="./downloads",
    translator=translator,
    translate_lang=Language.INDONESIAN,
    translate_engine=Engine.DEEPL,
)
pdf = dl.download(make_pdf=True)
```

If a page fails to translate, the original image is saved instead (silent fallback).

---

::: nhentai.downloader.Downloader

---

::: nhentai.downloader.DownloadError
