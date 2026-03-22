#!/usr/bin/env python3
"""
Read .watchlist.json from the current working directory.

Usage:
    python read_watchlist.py

Output (stdout, JSON):
    {"ok": true, "topics": [...]}   — file exists and is valid
    {"ok": true, "topics": []}      — file absent
    {"ok": false, "error": "..."}   — file exists but is unparseable

Exit code: always 0.
"""

import json
import sys
import os

WATCHLIST_FILE = ".watchlist.json"


def main():
    if not os.path.exists(WATCHLIST_FILE):
        print(json.dumps({"ok": True, "topics": []}))
        return

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        topics = data.get("topics", [])
        print(json.dumps({"ok": True, "topics": topics}))
    except (json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"ok": False, "error": f"Could not parse .watchlist.json: {e}"}))
    except (IOError, OSError) as e:
        print(json.dumps({"ok": False, "error": f"Could not read .watchlist.json: {e}"}))


if __name__ == "__main__":
    main()
