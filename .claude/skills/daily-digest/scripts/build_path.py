#!/usr/bin/env python3
"""
Build the output file path for a digest.

Usage:
    python build_path.py <payload_json>

    Where <payload_json> is a JSON string: {"topic": "...", "hints": [...], "snippets": [...]}

Output:
    digests/YYYY/MM/digest-YYYY-MM-DD-<topic-slug>.md
"""

import sys
import re
import json
from datetime import datetime


def build_path(topic: str) -> str:
    now = datetime.now()
    slug = re.sub(r"[^a-z0-9-]", "", topic.lower().replace(" ", "-"))[:50]
    return f"digests/{now:%Y}/{now:%m}/digest-{now:%Y-%m-%d}-{slug}.md"


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    topic = payload.get("topic", "untitled")
    print(build_path(topic))
