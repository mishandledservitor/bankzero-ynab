# Bank Zero → YNAB Converter

Converts Bank Zero CSV statement exports into the CSV format that YNAB (You Need A Budget) expects for import.

## What it does

- Strips unnecessary columns (Transaction Id, Day, Time, Type, Fee, Has Attachments)
- Renames columns to YNAB format: `Description 1` → `Payee`, `Description 2` → `Memo`
- Cleans up amounts (removes whitespace, drops trailing `.00`)
- Lets you cut off at a specific transaction ID so you only import new transactions
- Output filename is auto-generated from the input name — no prompts
- Always outputs to the `output/` folder inside the repo
- Archives processed inputs automatically after each run
- Removes the original source file from Downloads (or wherever it came from) to keep things tidy
- Opens Finder to reveal the output file, then auto-closes Terminal

## Folder structure

```
bankzero-ynab/
├── input/          ← Bank Zero CSVs land here (auto or manual)
├── output/         ← YNAB-ready files always go here
├── archive/        ← Processed inputs are moved here with a timestamp
├── run.command     ← Double-click or drag-and-drop launcher
├── bankzero_to_ynab.py
├── VERSION
└── CHANGELOG.md
```

## Usage

### Option 1: Drag and drop

Drag a Bank Zero CSV onto **`run.command`** in Finder. The file is copied into `input/`, converted, and the output is saved to `output/`.

### Option 2: Double-click

Double-click **`run.command`**. It lists CSV files already in `input/` and walks you through the rest.

### Option 3: Auto-scan ~/Downloads

If `input/` is empty and no file was dropped, the app automatically scans `~/Downloads` for Bank Zero CSVs (identified by their header row). Pick one and it gets imported into `input/` before conversion.

### Option 4: Place files manually

Copy Bank Zero CSVs into the `input/` folder, then double-click `run.command` to pick and convert.

### What happens

1. Preview all transactions with color-coded amounts
2. Ask which transaction ID to include up to (defaults to all)
3. Auto-name the output (e.g. `BankZero 02 Apr-26 Thu 06h59.csv` → `bankzero_02_apr_26_thu_06h59_ynab.csv`)
4. Save to `output/` and reveal in Finder
5. Archive processed inputs to `archive/` with a timestamp prefix
6. Remove the original source file from Downloads (or wherever it was dragged from)
7. Terminal window auto-closes

## Output format

```csv
Date,Payee,Memo,Amount,Balance
2026-04-01,STRATUM @ Firstrand,STRATUM   400415819 NETCASH,-539,790.67
```

## Versioning

Version is tracked in the `VERSION` file and displayed in the CLI header. See [CHANGELOG.md](CHANGELOG.md) for release history.

## Requirements

- macOS
- Python 3.6+
- No external dependencies
