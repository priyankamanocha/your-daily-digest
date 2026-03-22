#!/usr/bin/env python3
"""
Add or remove a topic from .watchlist.json in the current working directory.

Usage:
    python write_watchlist.py add    '<{"name": "...", "label": "...", "added_at": "..."}>'
    python write_watchlist.py remove '<{"name": "..."}>'

Output (stdout, JSON):
    {"ok": true, "action": "added",          "total": N}
    {"ok": true, "action": "already_exists", "total": N}
    {"ok": true, "action": "removed",        "total": N}
    {"ok": true, "action": "not_found",      "total": N}
    {"ok": false, "error": "..."}

Exit code: 0 on success, 1 on I/O error.
"""

import json
import sys
import os

WATCHLIST_FILE = ".watchlist.json"


def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return {"version": "1", "topics": []}
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_watchlist(data):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"ok": False, "error": "Usage: write_watchlist.py <add|remove> <topic_json>"}))
        sys.exit(1)

    action = sys.argv[1].lower()
    try:
        topic_input = json.loads(sys.argv[2])
    except (json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"ok": False, "error": f"Invalid topic JSON: {e}"}))
        sys.exit(1)

    try:
        data = load_watchlist()
        topics = data.get("topics", [])

        if action == "add":
            name = topic_input.get("name", "").strip()
            # Case-insensitive duplicate check
            for t in topics:
                if t.get("name", "").lower() == name.lower():
                    print(json.dumps({"ok": True, "action": "already_exists", "total": len(topics)}))
                    return
            topics.append(topic_input)
            data["topics"] = topics
            save_watchlist(data)
            print(json.dumps({"ok": True, "action": "added", "total": len(topics)}))

        elif action == "remove":
            name = topic_input.get("name", "").strip().lower()
            original_count = len(topics)
            topics = [t for t in topics if t.get("name", "").lower() != name]
            data["topics"] = topics
            if len(topics) < original_count:
                save_watchlist(data)
                print(json.dumps({"ok": True, "action": "removed", "total": len(topics)}))
            else:
                print(json.dumps({"ok": True, "action": "not_found", "total": len(topics)}))

        else:
            print(json.dumps({"ok": False, "error": f"Unknown action: {action}. Use 'add' or 'remove'."}))
            sys.exit(1)

    except (IOError, OSError) as e:
        print(json.dumps({"ok": False, "error": f"File I/O error: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
