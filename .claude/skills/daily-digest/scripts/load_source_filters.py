#!/usr/bin/env python3
"""
Load and validate sources.json from the current working directory.

Usage:
    python load_source_filters.py

Output (stdout, JSON):
    Exit 0: {"filter_config": {"global": {...}, "topics": {...}}}
    Exit 1: {"error": "sources.json: <message>"}
    Exit 2: {"filter_config": null}   (file not found — proceed without filtering)

Exit codes:
    0 = file loaded and valid
    1 = file present but invalid
    2 = file not found

This script performs I/O and validation only. Domain matching logic lives in daily-digest.md.
"""

import json
import sys
import os

SOURCES_FILE = "sources.json"


def err(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def validate_string_array(value, path):
    if not isinstance(value, list):
        err(f"sources.json: '{path}' must be an array of strings")
    for i, entry in enumerate(value):
        if not isinstance(entry, str):
            err(f"sources.json: '{path}' must be an array of strings")
        if not entry:
            err(f"sources.json: empty entry in '{path}'")


def main():
    if not os.path.exists(SOURCES_FILE):
        print(json.dumps({"filter_config": None}))
        sys.exit(2)

    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            raw = f.read()
    except (IOError, OSError) as e:
        err(f"sources.json: could not read file: {e}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        err(f"sources.json: invalid JSON at line {e.lineno}")

    if not isinstance(data, dict):
        err("sources.json: root must be an object")

    # Validate global section
    if "global" in data:
        g = data["global"]
        if not isinstance(g, dict):
            err("sources.json: 'global' must be an object")
        if "allow" in g:
            validate_string_array(g["allow"], "global.allow")
        if "block" in g:
            validate_string_array(g["block"], "global.block")

    # Validate topics section
    if "topics" in data:
        t = data["topics"]
        if not isinstance(t, dict):
            err("sources.json: 'topics' must be an object")
        for topic_name, topic_val in t.items():
            if not isinstance(topic_val, dict):
                err(f"sources.json: topic '{topic_name}' must be an object")
            if "allow" in topic_val:
                validate_string_array(topic_val["allow"], f"topics.{topic_name}.allow")
            if "block" in topic_val:
                validate_string_array(topic_val["block"], f"topics.{topic_name}.block")

    # Unknown top-level keys are silently ignored
    filter_config = {
        "global": data.get("global", {}),
        "topics": data.get("topics", {}),
    }

    print(json.dumps({"filter_config": filter_config}))
    sys.exit(0)


if __name__ == "__main__":
    main()
