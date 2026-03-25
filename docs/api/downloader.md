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

## Proxy Support

The downloader supports proxy lists for enhanced connectivity. Proxy lists can be provided as local files or URLs.

### Using Local Proxy List File

```python
dl = Downloader(
    gallery,
    output_dir="./downloads",
    proxy_list=["http://127.0.0.1:8080", "socks5://10.0.0.1:1080"]
)
```

### Using URL-based Proxy List

```python
dl = Downloader(
    gallery,
    output_dir="./downloads",
    proxy_list=["https://example.com/proxies.txt"]
)
```

The downloader will automatically fetch proxy lists from URLs and use them for requests.

---

::: nhentai.downloader.Downloader

---

::: nhentai.downloader.DownloadError
