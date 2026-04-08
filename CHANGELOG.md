# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-04-08

### Fixed

- Removed stray leading blank line in output CSV that was breaking YNAB import

## [1.3.0] - 2026-04-02

### Added

- Original source file (from ~/Downloads or drag-and-drop) is removed after archiving to keep things tidy

## [1.2.0] - 2026-04-02

### Changed

- Output filename is now fully automatic — derived from input name, no prompt
- Output always goes to `output/` folder inside the repo
- Terminal window auto-closes after completion (Finder stays open showing the output)

### Removed

- Output file path prompt

## [1.1.0] - 2026-04-02

### Added

- Auto-scan `~/Downloads` for Bank Zero CSVs when `input/` is empty (detected by header row)
- `archive/` folder — processed inputs are moved here with a timestamp prefix after each run
- Files sorted by most recently modified when scanning Downloads

## [1.0.0] - 2026-04-02

### Added

- Interactive CLI that walks through file selection, transaction preview, and ID cutoff
- `input/` folder for ingesting Bank Zero CSV exports
- `output/` folder for YNAB-ready CSV files
- Drag-and-drop support: drop a CSV onto `run.command` to auto-ingest and convert
- Double-click `run.command` to pick from files already in `input/`
- Auto-generated output filenames (lowercased, cleaned, `_ynab` suffix)
- Finder window opens automatically to reveal the output file after conversion
- Color-coded transaction preview (green for credits)
- Version display in CLI header
- `VERSION` file for tracking releases

## [0.2.0] - 2026-04-02

### Added

- Drag-and-drop: drop a CSV onto `run.command` to skip file picker
- Auto-named output files based on cleaned input filename

### Changed

- Renamed `run.sh` to `run.command` for native macOS double-click support

## [0.1.0] - 2026-04-02

### Added

- Initial converter script with Bank Zero CSV to YNAB CSV transformation
- Interactive CLI with file picker, transaction preview, and ID cutoff
- `run.sh` launcher
