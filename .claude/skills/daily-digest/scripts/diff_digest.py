#!/usr/bin/env python3
"""
Find the most recent qualifying previous digest for a topic and parse its sections.

Usage:
    python diff_digest.py <topic_slug> [--window-days N]

    topic_slug  : the URL-safe slug derived from the topic name (same logic as build_path.py)
    --window-days N : maximum age in days for a qualifying baseline (default: 7, inclusive)

Output (stdout, JSON):
    Found:    {"found": true, "baseline_date": "YYYY-MM-DD", "baseline_path": "...",
               "sections": {"key_insights": [...], "anti_patterns": [...],
                            "actions": [...], "resources": [...]}}
    Not found: {"found": false}

Exit codes:
    0 : success (including "not found" — that is a normal outcome)
    1 : unexpected argument or I/O error (skill treats this as "not found")
"""

import sys
import os
import re
import json
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIGEST_PATTERN = re.compile(r"^digest-(\d{4}-\d{2}-\d{2})-(.+)\.md$")

# Section heading patterns
_HEADING3 = re.compile(r"^### (.+)$", re.MULTILINE)
_BOLD_LABEL = re.compile(r"^\s*[-*]?\s*\*\*(.+?)\*\*:", re.MULTILINE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _tokenise(title: str) -> set:
    """Lowercase, strip punctuation, return non-empty tokens."""
    tokens = re.sub(r"[^a-z0-9 ]", "", title.lower()).split()
    return set(tokens)


def _extract_section_titles(block: str, use_heading3: bool) -> list:
    """Extract item titles from a section block using the appropriate pattern."""
    if use_heading3:
        return [m.group(1).strip() for m in _HEADING3.finditer(block)]
    else:
        return [m.group(1).strip() for m in _BOLD_LABEL.finditer(block)]


def _parse_sections(content: str) -> dict:
    """
    Split digest content on '## ' boundaries and extract titles per section.
    Returns dict with keys: key_insights, anti_patterns, actions, resources.
    """
    # Normalise line endings
    content = content.replace("\r\n", "\n")

    # Split on level-2 headings (## )
    parts = re.split(r"\n## ", "\n" + content)

    sections = {
        "key_insights": [],
        "anti_patterns": [],
        "actions": [],
        "resources": [],
    }

    for part in parts:
        first_line = part.split("\n", 1)[0].strip()
        body = part.split("\n", 1)[1] if "\n" in part else ""

        lower = first_line.lower()
        if "key insight" in lower:
            sections["key_insights"] = _extract_section_titles(body, use_heading3=True)
        elif "anti-pattern" in lower or "antipattern" in lower:
            sections["anti_patterns"] = _extract_section_titles(body, use_heading3=False)
        elif "action" in lower:
            sections["actions"] = _extract_section_titles(body, use_heading3=True)
        elif "resource" in lower:
            sections["resources"] = _extract_section_titles(body, use_heading3=False)

    return sections


def find_baseline(slug: str, window_days: int) -> dict:
    """
    Walk digests/ looking for files matching digest-YYYY-MM-DD-{slug}.md.
    Returns the most recent one within window_days of today (inclusive),
    excluding today's own file.
    Returns {"found": false} if none qualifies.
    """
    today = date.today()
    candidates = []

    digests_root = "digests"
    if not os.path.isdir(digests_root):
        return {"found": False}

    for dirpath, _dirs, filenames in os.walk(digests_root):
        for fname in filenames:
            m = DIGEST_PATTERN.match(fname)
            if not m:
                continue
            file_date_str, file_slug = m.group(1), m.group(2)
            if file_slug != slug:
                continue
            file_date = _parse_date(file_date_str)
            if file_date is None:
                continue
            if file_date == today:
                continue  # skip today's own file
            age_days = (today - file_date).days
            if age_days <= window_days:
                candidates.append((file_date, os.path.join(dirpath, fname)))

    if not candidates:
        return {"found": False}

    # Most recent first
    candidates.sort(key=lambda x: x[0], reverse=True)
    baseline_date, baseline_path = candidates[0]

    try:
        with open(baseline_path, encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return {"found": False}
        sections = _parse_sections(content)
    except (OSError, IOError):
        return {"found": False}
    except Exception:
        return {"found": False}

    return {
        "found": True,
        "baseline_date": baseline_date.isoformat(),
        "baseline_path": baseline_path.replace("\\", "/"),
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"found": False}))
        sys.exit(1)

    slug = args[0]
    window_days = 7

    # Parse --window-days N
    for i, arg in enumerate(args[1:], 1):
        if arg == "--window-days" and i + 1 < len(args):
            try:
                window_days = int(args[i + 1])
            except ValueError:
                pass

    try:
        result = find_baseline(slug, window_days)
    except Exception:
        result = {"found": False}
        sys.exit(1)

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
