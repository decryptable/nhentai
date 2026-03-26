The library provides multiple translation providers that implement the `BaseTranslator` interface.

### NekoTranslator
Client for the [NekoTranslate](https://nekotranslate.ai) API. Supports anonymous mode with automatic proxy rotation.

```python
from nhentai import NekoTranslator, NekoEngine, Language

translator = NekoTranslator(token="YOUR_BEARER_TOKEN") # token is optional
data = translator.translate_file("page.jpg", tgt_lang=Language.INDONESIAN, engine=NekoEngine.DEEPL)
```

---

::: nhentai.translator.NekoTranslator

### ComicTranslator
Client for the [Comic-Translator](https://comictranslator.com) API. Automatically handles guest registration and supports direct URL translation.

```python
from nhentai import ComicTranslator, ComicEngine, Language

translator = ComicTranslator()
# Direct URL translation (Faster)
data = translator.translate_url("https://i.nhentai.net/...", tgt_lang=Language.ENGLISH, engine=ComicEngine.GEMINI_FLASH)
```

---

::: nhentai.translator.ComicTranslator

---

::: nhentai.translator.TranslationError
