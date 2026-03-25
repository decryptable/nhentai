# NekoTranslator

Client for the [NekoTranslate](https://nekotranslate.ai) API.

Anonymous mode uses free per-IP quota and rotates proxies automatically.
Pass a `token` for authenticated (higher-quota) requests.

```python
from nhentai import NekoTranslator

# Anonymous — scans proxy list for available quota
translator = NekoTranslator()

# Authenticated
translator = NekoTranslator(token="YOUR_BEARER_TOKEN")

# Custom proxy source
translator = NekoTranslator(
    proxy_list_url="https://example.com/proxies.txt"
)

# Explicit proxy list
translator = NekoTranslator(
    proxies=["socks5://1.2.3.4:1080", "1.2.3.4:8080"]
)

# Translate a file — returns raw bytes
data = translator.translate_file("page.jpg", tgt_lang="id", engine="deepl")

# Translate raw bytes
data = translator.translate_bytes(image_bytes, filename="page.jpg", tgt_lang="id")

# Check balance
info = translator.get_balance()
# {"email": None, "plan": "Free", "level": 0, "quota": 12}
```

---

::: nhentai.translator.NekoTranslator

---

::: nhentai.translator.TranslationError
