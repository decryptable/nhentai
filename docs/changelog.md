# Changelog

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
