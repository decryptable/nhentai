# NHentai

Fetches and exposes metadata for a single nhentai gallery.

Accepts either a full URL or a bare gallery ID:

```python
from nhentai import NHentai

gallery = NHentai("639456")
gallery = NHentai("https://nhentai.net/g/639456/")
```

---

::: nhentai.nhentai.NHentai
