#!/usr/bin/env python3
"""Convert Bank Zero CSV exports to YNAB-compatible CSV format."""

from __future__ import annotations

import csv
import glob
import io
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"
ARCHIVE_DIR = SCRIPT_DIR / "archive"
VERSION_FILE = SCRIPT_DIR / "VERSION"
DOWNLOADS_DIR = Path.home() / "Downloads"

BANKZERO_HEADER = "Transaction Id,Date,Day,Time,Type,Description 1,Description 2,Fee,Amount,Balance,Has Attachments"


def get_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "unknown"


def clean_amount(raw: str) -> str:
    val = raw.strip().replace(" ", "")
    try:
        num = float(val)
    except ValueError:
        return val
    if num == int(num):
        return str(int(num))
    return str(num)


def clean_filename(stem: str) -> str:
    cleaned = stem.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return cleaned.strip("_")


def is_bankzero_csv(path: Path) -> bool:
    try:
        first_line = path.read_text(encoding="utf-8-sig").split("\n", 1)[0].strip()
        return first_line == BANKZERO_HEADER
    except Exception:
        return False


def read_transactions(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def preview_transactions(rows: list[dict]) -> None:
    print(f"\n{BOLD}  ID  Date        Payee                          Amount{RESET}")
    print(f"  {'─' * 55}")
    for row in rows:
        txn_id = row["Transaction Id"].strip()
        date = row["Date"].strip()
        payee = row["Description 1"].strip()
        amount = clean_amount(row["Amount"])
        color = GREEN if not amount.startswith("-") else ""
        reset = RESET if color else ""
        print(f"  {txn_id:>3}  {date}  {payee:<30} {color}{amount:>10}{reset}")


def convert(rows: list[dict], max_txn_id: int | None = None) -> tuple[str, int]:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Date", "Payee", "Memo", "Amount", "Balance"])

    count = 0
    for row in rows:
        txn_id = int(row["Transaction Id"].strip())
        if max_txn_id is not None and txn_id > max_txn_id:
            break
        writer.writerow([
            row["Date"].strip(),
            row["Description 1"].strip(),
            row["Description 2"].strip(),
            clean_amount(row["Amount"]),
            row["Balance"].strip(),
        ])
        count += 1

    return out.getvalue(), count


def prompt(text: str, default: str = "") -> str:
    suffix = f" {DIM}[{default}]{RESET}" if default else ""
    try:
        val = input(f"{CYAN}>{RESET} {text}{suffix}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{DIM}Cancelled.{RESET}")
        sys.exit(0)
    return val or default


def ingest_file(source: Path) -> tuple[Path, Path | None]:
    """Copy a file into the input/ folder. Returns (dest, original_to_clean_up)."""
    INPUT_DIR.mkdir(exist_ok=True)
    dest = INPUT_DIR / source.name
    original = None
    if source.resolve() != dest.resolve():
        shutil.copy2(source, dest)
        original = source
        print(f"  Copied to {DIM}input/{source.name}{RESET}")
    return dest, original


def scan_downloads() -> list[Path]:
    """Find Bank Zero CSVs in ~/Downloads."""
    results = []
    for p in sorted(DOWNLOADS_DIR.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True):
        if is_bankzero_csv(p):
            results.append(p)
    return results


def pick_file() -> tuple[Path, Path | None]:
    """Pick a file from input/ or ~/Downloads. Returns (path, original_to_clean_up)."""
    INPUT_DIR.mkdir(exist_ok=True)
    csvs = sorted(glob.glob(str(INPUT_DIR / "*.csv")))

    if csvs:
        display = [Path(c).name for c in csvs]
        print(f"\n{BOLD}CSV files in input/:{RESET}\n")
        for i, name in enumerate(display, 1):
            print(f"  {CYAN}{i}{RESET}) {name}")

        choice = prompt("\nSelect a file (number or name)")

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(csvs):
                return Path(csvs[idx]), None
            print(f"{RED}Invalid selection.{RESET}")
            sys.exit(1)

        path = INPUT_DIR / choice
        if path.exists():
            return path, None
        print(f"{RED}File not found: {choice}{RESET}")
        sys.exit(1)

    # No files in input/ — scan Downloads
    print(f"\n{DIM}No CSV files in input/ — scanning ~/Downloads...{RESET}")
    downloads = scan_downloads()

    if not downloads:
        print(f"\n{YELLOW}No Bank Zero CSV files found in input/ or ~/Downloads.{RESET}")
        print(f"{DIM}Drop a Bank Zero CSV onto run.command, or place files in input/{RESET}")
        sys.exit(1)

    print(f"\n{BOLD}Bank Zero CSVs found in ~/Downloads:{RESET}\n")
    for i, p in enumerate(downloads, 1):
        print(f"  {CYAN}{i}{RESET}) {p.name}")

    choice = prompt("\nSelect a file to import (number or name)")

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(downloads):
            return ingest_file(downloads[idx])
        print(f"{RED}Invalid selection.{RESET}")
        sys.exit(1)

    path = DOWNLOADS_DIR / choice
    if path.exists():
        return ingest_file(path)
    print(f"{RED}File not found: {choice}{RESET}")
    sys.exit(1)


def archive_inputs(original_source: Path | None = None) -> None:
    """Move all CSVs from input/ to archive/, and remove the original source file."""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    count = 0

    for src in INPUT_DIR.glob("*.csv"):
        dest = ARCHIVE_DIR / f"{stamp}_{src.name}"
        shutil.move(str(src), str(dest))
        count += 1

    if original_source and original_source.exists():
        original_source.unlink()
        print(f"{DIM}  Removed {original_source.name} from {original_source.parent}{RESET}")

    if count:
        print(f"{DIM}  Archived {count} input file(s) to archive/{RESET}")


def reveal_in_finder(path: Path) -> None:
    try:
        subprocess.run(["open", "-R", str(path)], check=True)
    except Exception:
        pass


def main() -> None:
    version = get_version()
    print(f"\n{BOLD}Bank Zero → YNAB Converter{RESET}  {DIM}v{version}{RESET}")
    print(f"{DIM}{'─' * 30}{RESET}")

    original_source = None
    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
        if not source.exists():
            print(f"{RED}File not found: {source}{RESET}")
            sys.exit(1)
        path, original_source = ingest_file(source)
    else:
        path, original_source = pick_file()

    print(f"\n{DIM}Reading {path.name}...{RESET}")

    rows = read_transactions(path)
    total = len(rows)
    print(f"  Found {BOLD}{total}{RESET} transactions")

    preview_transactions(rows)

    max_id_str = prompt(
        f"\nInclude up to transaction ID",
        default=str(total),
    )
    try:
        max_id = int(max_id_str)
    except ValueError:
        print(f"{RED}Invalid number.{RESET}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_name = f"{clean_filename(path.stem)}_ynab.csv"
    out_path = OUTPUT_DIR / out_name

    result, count = convert(rows, max_id)
    out_path.write_text(result, encoding="utf-8")

    print(f"\n{GREEN}Done!{RESET} Wrote {BOLD}{count}{RESET} transactions to {BOLD}{out_path.name}{RESET}")

    archive_inputs(original_source)
    print()

    reveal_in_finder(out_path)


if __name__ == "__main__":
    main()
