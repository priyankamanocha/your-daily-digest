#!/usr/bin/env python3
"""
Validate the canonical invocation payload for the daily-digest skill.

Usage:
    python validate_input.py <payload_json>

    Where <payload_json> is a JSON string:
    {
      "topic": "...",
      "hints": [...],
      "snippets": [...],
      "since": "...",
      "since_window": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "label": "..."},
      "no_diff": false
    }

Exit codes:
    0 = valid; prints {"valid": true, "topic": ..., "hints": ..., "snippets": ..., "since": ..., "since_window": ..., "no_diff": ...}
    1 = invalid; prints {"valid": false, "error": "..."}

See .claude/skills/daily-digest/resources/invocation-contract.md for field constraints.
"""

import sys
import re
import json
from datetime import date

TOPIC_MAX_LEN = 100
TOPIC_PATTERN = re.compile(r"^[a-zA-Z0-9\-_ ]+$")
HINTS_MAX_COUNT = 10
HINTS_MAX_LEN = 50


def validate(payload: dict) -> dict:
    topic = payload.get("topic", "")
    hints = payload.get("hints", [])
    snippets = payload.get("snippets", [])
    since = payload.get("since", "1")
    since_window = payload.get("since_window", {})
    no_diff = bool(payload.get("no_diff", False))

    # Topic
    if not topic:
        return {"valid": False, "error": "topic is required"}
    if not topic.strip():
        return {"valid": False, "error": "topic cannot be empty"}
    topic = topic.strip()
    if len(topic) > TOPIC_MAX_LEN:
        return {"valid": False, "error": f"topic exceeds {TOPIC_MAX_LEN} characters"}
    if not TOPIC_PATTERN.match(topic):
        return {"valid": False, "error": "topic contains invalid characters (use alphanumeric, hyphens, underscores, spaces)"}

    # Hints
    if len(hints) > HINTS_MAX_COUNT:
        return {"valid": False, "error": f"hints exceeds {HINTS_MAX_COUNT} items"}
    for h in hints:
        if len(h) > HINTS_MAX_LEN:
            return {"valid": False, "error": f'hint "{h[:20]}..." exceeds {HINTS_MAX_LEN} characters'}

    # since_window (validated only if present and non-empty)
    if since_window:
        today = date.today()

        start_str = since_window.get("start_date", "")
        end_str = since_window.get("end_date", "")

        if not start_str:
            return {"valid": False, "error": "since_window.start_date is required"}
        if not end_str:
            return {"valid": False, "error": "since_window.end_date is required"}

        try:
            start = date.fromisoformat(start_str)
        except ValueError:
            return {"valid": False, "error": "since_window.start_date is not a valid date (expected YYYY-MM-DD)"}

        try:
            end = date.fromisoformat(end_str)
        except ValueError:
            return {"valid": False, "error": "since_window.end_date is not a valid date (expected YYYY-MM-DD)"}

        if start > end:
            return {"valid": False, "error": "since_window.start_date must not be after end_date"}

        if start > today:
            return {"valid": False, "error": "since_window.start_date cannot be in the future"}

    # Snippets pass through without validation
    return {
        "valid": True,
        "topic": topic,
        "hints": hints,
        "snippets": snippets,
        "since": since,
        "since_window": since_window,
        "no_diff": no_diff,
    }


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "error": "invalid payload format"}))
        sys.exit(1)

    result = validate(payload)
    print(json.dumps(result))
    sys.exit(0 if result["valid"] else 1)
