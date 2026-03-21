#!/usr/bin/env python3
"""
Write digest content to the output file, creating directories as needed.

Usage:
    python write_digest.py <file_path> <content>
    echo "<content>" | python write_digest.py <file_path>

Exit codes:
    0 = success
    1 = error (message printed to stderr)
"""

import sys
import os


def write_digest(file_path: str, content: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: write_digest.py <file_path> [content]", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    content = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()

    try:
        write_digest(file_path, content)
        print(f"✅ Digest created: {file_path}")
    except OSError as e:
        print(f"Error writing digest: {e}", file=sys.stderr)
        sys.exit(1)
