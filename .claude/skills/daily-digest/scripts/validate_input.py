#!/usr/bin/env python3
"""
Validate topic and hints for autonomous discovery.

Usage:
    python validate_input.py <topic> [hints]

Exit codes:
    0 = valid
    1 = invalid (error printed to stdout)
"""

import sys
import re
import json

TOPIC_MAX_LEN = 100
TOPIC_PATTERN = re.compile(r"^[a-zA-Z0-9\-_ ]+$")
HINTS_MAX_COUNT = 10
HINTS_MAX_LEN = 50


def validate(topic: str, hints_str: str = "") -> dict:
    # Topic
    if not topic or not topic.strip():
        return {"valid": False, "error": "topic is required"}
    topic = topic.strip()
    if len(topic) > TOPIC_MAX_LEN:
        return {"valid": False, "error": f"topic exceeds {TOPIC_MAX_LEN} characters"}
    if not TOPIC_PATTERN.match(topic):
        return {"valid": False, "error": "topic contains invalid characters (use alphanumeric, hyphens, underscores)"}

    # Hints
    hints = []
    if hints_str:
        hints = list(dict.fromkeys(h.strip() for h in hints_str.split(",") if h.strip()))
        if len(hints) > HINTS_MAX_COUNT:
            return {"valid": False, "error": f"hints exceeds {HINTS_MAX_COUNT} items"}
        for h in hints:
            if len(h) > HINTS_MAX_LEN:
                return {"valid": False, "error": f'hint "{h[:20]}..." exceeds {HINTS_MAX_LEN} characters'}

    return {"valid": True, "topic": topic, "hints": hints}


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else ""
    hints = sys.argv[2] if len(sys.argv) > 2 else ""
    result = validate(topic, hints)
    print(json.dumps(result))
    sys.exit(0 if result["valid"] else 1)
