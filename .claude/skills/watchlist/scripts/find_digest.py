#!/usr/bin/env python3
"""
Check whether a digest file exists for a given topic and date.

Usage:
    python find_digest.py <topic_name> <YYYY-MM-DD>

Output (stdout, JSON):
    {"exists": true, "path": "digests/YYYY/MM/digest-YYYY-MM-DD-slug.md"}
    {"exists": false, "path": null}

Exit code: always 0.
"""

import json
import sys
import re
import os


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:50]


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"exists": False, "path": None}))
        return

    name = sys.argv[1]
    date_str = sys.argv[2]  # YYYY-MM-DD

    slug = slugify(name)

    try:
        year, month, _ = date_str.split("-")
    except ValueError:
        print(json.dumps({"exists": False, "path": None}))
        return

    path = f"digests/{year}/{month}/digest-{date_str}-{slug}.md"

    if os.path.exists(path):
        print(json.dumps({"exists": True, "path": path}))
    else:
        print(json.dumps({"exists": False, "path": None}))


if __name__ == "__main__":
    main()
