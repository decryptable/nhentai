# Enums

`Engine` and `Language` are `str` subclasses, so they work transparently
as plain strings in any context (requests, JSON, `str` comparisons).

```python
from nhentai import Engine, Language

# Both forms are valid anywhere an engine/language is accepted
Engine.DEEPL == "deepl"          # True
Language("id") is Language.INDONESIAN  # True

# IDE autocomplete works on all members
Engine.GOOGLE
Engine.DEEPL
Engine.AUTO
Engine.DEEPSEEK
Engine.GPT5_MINI
Engine.CLAUDE
Engine.GPT5

Language.ENGLISH
Language.INDONESIAN
Language.JAPANESE
# ... and 30+ more
```

---

::: nhentai.enums.Engine

---

::: nhentai.enums.Language
