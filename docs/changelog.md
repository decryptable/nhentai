# Changelog

## 0.1.3 — 2026-03-26

### Added
- Integrated [**termynal.py**](https://github.com/termynal/termynal.py) for interactive CLI animations in documentation.

### Changed
- Updated version to 0.1.3

## 0.1.2 — 2026-03-26

### Added
- New **Comic-Translator** provider supporting `/v3` API.
- Direct URL translation in `Downloader` (much faster as it avoids re-uploading).
- Interactive mode (`-i`) for CLI with provider/engine selection.
- `Provider` enum to separate translation source from AI engine.
- `ComicEngine` and `NekoEngine` for provider-specific model selection.

### Changed
- Refactored `nhentai/translator.py` into `nhentai/providers/` package for better maintainability.
- Updated `Downloader` to automatically attempt the fastest translation method first.
- Fixed `ruff` linting and improved test coverage to 80%+.

## 0.1.1 — 2026-03-26

### Added
- Support for proxy lists from both local files and raw URLs in CLI
- Enhanced `parse_proxy_list` function to detect and fetch URL-based proxy lists
- Comprehensive test coverage for new proxy list functionality

### Changed
- Updated version to 0.1.1

## 0.1.0 — 2026-03-26

Initial release.

- `NHentai` — gallery metadata via nhentai HTML scraping
- `Downloader` — parallel page download, optional translation, optional PDF export
- `NekoTranslator` — NekoTranslate API client with automatic proxy rotation
- `Engine` / `Language` — type-safe str enums
- CLI via `nhentai` command
