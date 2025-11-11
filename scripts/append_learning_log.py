"""Append a change entry to LEARNING_GUIDE.md

Usage:
    python scripts/append_learning_log.py --title "Title" --why "Reason" --files file1,file2 --result "Tests passed"
"""
import argparse
import datetime
from pathlib import Path


def append_entry(title: str, why: str, files: list[str], result: str):
    guide = Path(__file__).resolve().parents[1] / "LEARNING_GUIDE.md"
    # Use timezone-aware UTC timestamp to avoid deprecation warnings
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = [
        "\n---\n",
        f"### Change: {title}\n",
        f"- Timestamp: {ts} UTC\n",
        f"- Why: {why}\n",
        "- Files changed:\n",
    ]
    for f in files:
        entry.append(f"  - {f}\n")
    entry.append(f"- Test result: {result}\n")
    entry.append("\n")

    with open(guide, "a", encoding="utf-8") as fh:
        fh.writelines(entry)
    print(f"Appended change entry to {guide}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--files", required=True, help="Comma-separated list of files changed")
    p.add_argument("--result", required=True, help="Test/validation result summary")
    args = p.parse_args()
    files = [s.strip() for s in args.files.split(",") if s.strip()]
    append_entry(args.title, args.why, files, args.result)


if __name__ == "__main__":
    main()
