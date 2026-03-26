# Enums

`NekoEngine`, `ComicEngine`, `Provider` and `Language` are `str` subclasses, so they work transparently
as plain strings in any context (requests, JSON, `str` comparisons).

```python
from nhentai import NekoEngine, ComicEngine, Provider, Language

# Both forms are valid anywhere an engine/language is accepted
NekoEngine.DEEPL == "deepl"          # True
Provider.COMIC == "comic"            # True
Language("id") is Language.INDONESIAN  # True
```

---

::: nhentai.enums.Provider

---

::: nhentai.enums.NekoEngine

---

::: nhentai.enums.ComicEngine

---

::: nhentai.enums.Language
