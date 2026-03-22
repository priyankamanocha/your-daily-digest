#!/usr/bin/env python3
"""
Eval runner for the daily-digest skill.

Run from repo root:
    python .claude/skills/daily-digest/evals/run_evals.py

What is automated:
  - freshness: since_window resolution (mirrors Step 0 parse logic)
  - freshness: validate_input.py exits 0 with correct since_window
  - error:     invalid --since values produce the right error strings
  - error:     no digest file is created for invalid inputs
  - digest:    structural checks on an existing digest file
               (section presence, counts, evidence fields, title length,
                quality warning presence, benchmark strings)

What requires a prior skill run (digest type sets):
  - The skill must have been invoked first to generate the digest file.
  - If the file is absent, the set is reported as SKIP with instructions.

Exit code: 0 if all run sets pass, 1 if any fail.
"""

import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EVALS_DIR = Path(__file__).parent
SKILL_DIR = EVALS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
REPO_ROOT = SKILL_DIR.parent.parent.parent  # .claude/skills/daily-digest -> repo root
SETS_DIR = EVALS_DIR / "sets"

# ---------------------------------------------------------------------------
# Since-window resolver (mirrors SKILL.md Step 0 logic)
# ---------------------------------------------------------------------------
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def resolve_since_window(since_raw: str, today: date) -> "dict | str":
    """
    Returns a since_window dict on success, or an error string on failure.
    Mirrors the resolution rules in SKILL.md Step 0.
    """
    if not since_raw or not since_raw.strip():
        return "--since requires a value. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."

    s = since_raw.strip().lower()

    # Positive integer
    try:
        n = int(s)
        if n < 1:
            return f"since={n} is not valid \u2014 minimum value is 1."
        if n == 1:
            return {
                "start_date": str(today - timedelta(days=1)),
                "end_date": str(today),
                "label": "last 24 hours",
            }
        return {
            "start_date": str(today - timedelta(days=n)),
            "end_date": str(today),
            "label": f"last {n} days",
        }
    except ValueError:
        pass

    if s == "yesterday":
        yesterday = today - timedelta(days=1)
        return {
            "start_date": str(yesterday),
            "end_date": str(yesterday),
            "label": f"yesterday ({yesterday})",
        }

    if s == "last month":
        return {
            "start_date": str(today - timedelta(days=30)),
            "end_date": str(today),
            "label": "last 30 days",
        }

    # "<month> <year>" e.g. "feb 2026"
    parts = s.split()
    if len(parts) == 2 and parts[0][:3] in _MONTH_MAP:
        try:
            m = _MONTH_MAP[parts[0][:3]]
            y = int(parts[1])
            start = date(y, m, 1)
            end = date(y, m + 1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
            label = f"{start.day} {start.strftime('%b')} \u2013 {end.day} {end.strftime('%b')} {y}"
            return {
                "start_date": str(start),
                "end_date": str(end),
                "label": label,
            }
        except (ValueError, KeyError):
            pass

    return (
        f"Could not interpret '--since {since_raw}'. "
        "Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."
    )


# ---------------------------------------------------------------------------
# Script helpers
# ---------------------------------------------------------------------------
def run_validate_input(payload: dict) -> "tuple[int, dict]":
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "validate_input.py"), json.dumps(payload)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    try:
        out = json.loads(result.stdout)
    except json.JSONDecodeError:
        out = {"raw": result.stdout, "stderr": result.stderr}
    return result.returncode, out


def build_digest_path(topic: str) -> Path:
    today = date.today()
    slug = re.sub(r"[^a-z0-9-]", "", topic.lower().replace(" ", "-"))[:50]
    return REPO_ROOT / f"digests/{today:%Y}/{today:%m}/digest-{today:%Y-%m-%d}-{slug}.md"


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------
def check(label: str, passed: bool, detail: str = "") -> dict:
    return {"label": label, "passed": passed, "detail": detail}


def count_section_items(content: str, section_header: str) -> int:
    """Count bullet/numbered items or ### headings in a digest section."""
    lines = content.splitlines()
    in_section = False
    count = 0
    for line in lines:
        if line.strip().startswith("## ") and section_header.lower() in line.lower():
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("## "):
                break
                # Anti-patterns and Resources use "- " bullets
            # Insights and Actions use "### " headings
            if line.strip().startswith("### "):
                count += 1
            elif line.strip().startswith("- ") and not line.strip().startswith("- Effort") and not line.strip().startswith("- Time") and not line.strip().startswith("- Steps") and not line.strip().startswith("- Expected"):
                count += 1
    return count


def extract_insight_titles(content: str) -> list:
    """Extract all ### titles from Key Insights section."""
    lines = content.splitlines()
    in_insights = False
    titles = []
    for line in lines:
        if "## Key Insights" in line:
            in_insights = True
            continue
        if in_insights:
            if line.strip().startswith("## "):
                break
            if line.strip().startswith("### "):
                titles.append(line.strip().lstrip("# ").strip())
    return titles


# ---------------------------------------------------------------------------
# Set runners
# ---------------------------------------------------------------------------
def run_digest_set(s: dict, today: date) -> list:
    inv = s["invocation"]
    checks_spec = s["checks"]
    results = []

    path = build_digest_path(inv["topic"])
    if not path.exists():
        results.append(check(
            "digest file exists",
            False,
            f"SKIP — file not found at {path.relative_to(REPO_ROOT)}. "
            f"Run: /daily-digest {inv['topic']} \"snippet1\" \"snippet2\" \"snippet3\" first.",
        ))
        return results

    content = path.read_text(encoding="utf-8")

    # Required sections
    for section in ["## Key Insights", "## Anti-patterns", "## Actions to Try", "## Resources"]:
        results.append(check(
            f"section present: {section}",
            section in content,
        ))

    # Section counts
    section_map = {
        "insights": "Key Insights",
        "antipatterns": "Anti-patterns",
        "actions": "Actions to Try",
        "resources": "Resources",
    }
    for key, header in section_map.items():
        if key not in checks_spec.get("section_counts", {}):
            continue
        lo, hi = checks_spec["section_counts"][key]
        count = count_section_items(content, header)
        passed = lo <= count <= hi
        results.append(check(
            f"count {key}: {count} in [{lo},{hi}]",
            passed,
            "" if passed else f"got {count}",
        ))

    # Insight evidence and source
    insight_count = count_section_items(content, "Key Insights")
    evidence_count = content.count("**Evidence**:")
    source_count = content.count("**Source**:")
    if checks_spec.get("all_insights_have_evidence"):
        results.append(check(
            "all insights have Evidence",
            evidence_count >= insight_count,
            f"found {evidence_count} Evidence fields, {insight_count} insights",
        ))
    if checks_spec.get("all_insights_have_source"):
        results.append(check(
            "all insights have Source",
            source_count >= insight_count,
            f"found {source_count} Source fields, {insight_count} insights",
        ))

    # Insight title length
    max_words = checks_spec.get("insight_title_max_words", 20)
    titles = extract_insight_titles(content)
    for title in titles:
        word_count = len(title.split())
        results.append(check(
            f"title <={max_words} words: \"{title[:40]}{'...' if len(title) > 40 else ''}\"",
            word_count <= max_words,
            f"{word_count} words",
        ))

    # Quality warning
    warning_present = "\u26a0\ufe0f Low-signal content" in content
    expected_warning = checks_spec.get("quality_warning", False)
    results.append(check(
        f"quality warning {'present' if expected_warning else 'absent'}",
        warning_present == expected_warning,
    ))

    # Benchmark strings
    for s_str in checks_spec.get("contains_strings", []):
        results.append(check(
            f"contains: \"{s_str}\"",
            s_str.lower() in content.lower(),
        ))

    return results


def run_freshness_set(s: dict, today: date) -> list:
    inv = s["invocation"]
    checks_spec = s["checks"]
    since_raw = inv["since"]
    results = []

    # Resolve since_window
    window = resolve_since_window(since_raw, today)
    if isinstance(window, str):
        results.append(check("since_window resolves (no error)", False, window))
        return results
    results.append(check("since_window resolves (no error)", True))

    # Label
    if "since_window_label" in checks_spec:
        expected_label = checks_spec["since_window_label"]
        results.append(check(
            f"since_window.label = \"{expected_label}\"",
            window["label"] == expected_label,
            f"got \"{window['label']}\"",
        ))

    # Start date by offset
    if "since_window_start_offset_days" in checks_spec:
        offset = checks_spec["since_window_start_offset_days"]
        expected_start = str(today - timedelta(days=offset))
        results.append(check(
            f"since_window.start_date = today - {offset}d ({expected_start})",
            window["start_date"] == expected_start,
            f"got {window['start_date']}",
        ))

    # Start date exact
    if "since_window_start_date" in checks_spec:
        expected = checks_spec["since_window_start_date"]
        results.append(check(
            f"since_window.start_date = {expected}",
            window["start_date"] == expected,
            f"got {window['start_date']}",
        ))

    # End date exact
    if "since_window_end_date" in checks_spec:
        expected = checks_spec["since_window_end_date"]
        results.append(check(
            f"since_window.end_date = {expected}",
            window["end_date"] == expected,
            f"got {window['end_date']}",
        ))

    # End date is today
    if checks_spec.get("since_window_end_is_today"):
        results.append(check(
            f"since_window.end_date = today ({today})",
            window["end_date"] == str(today),
            f"got {window['end_date']}",
        ))

    # validate_input.py accepts the resolved payload
    payload = {
        "topic": inv["topic"],
        "hints": [],
        "snippets": inv.get("snippets", []),
        "since": since_raw,
        "since_window": window,
        "no_diff": False,
    }
    exit_code, out = run_validate_input(payload)
    results.append(check(
        "validate_input.py exits 0",
        exit_code == 0,
        out.get("error", ""),
    ))

    # Digest file exists (if expected)
    if checks_spec.get("digest_created"):
        path = build_digest_path(inv["topic"])
        exists = path.exists()
        detail = "" if exists else f"SKIP — run /daily-digest {inv['topic']} first"
        results.append(check("digest file created", exists, detail))

    return results


def run_error_set(s: dict, today: date) -> list:
    results = []
    for case in s["cases"]:
        since_raw = case["since"]
        expected_error = case["expected_error"]
        label = f"--since \"{since_raw}\""

        window = resolve_since_window(since_raw, today)
        is_error = isinstance(window, str)
        results.append(check(
            f"{label}: resolves to error",
            is_error,
            f"got window instead: {window}" if not is_error else "",
        ))
        if is_error:
            contains = expected_error.rstrip(".") in window
            results.append(check(
                f"{label}: error contains \"{expected_error[:50]}\"",
                contains,
                f"got: \"{window}\"" if not contains else "",
            ))

        # No digest file created
        path = build_digest_path("freshness-test")
        results.append(check(
            f"{label}: no digest file created",
            not path.exists(),
            f"file unexpectedly exists at {path.relative_to(REPO_ROOT)}" if path.exists() else "",
        ))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    today = date.today()
    sets = sorted(SETS_DIR.glob("set-*.json"))

    if not sets:
        print("No eval sets found in", SETS_DIR)
        return 1

    all_passed = 0
    all_failed = 0
    all_skipped = 0

    for set_path in sets:
        with open(set_path, encoding="utf-8") as f:
            s = json.load(f)

        set_type = s["type"]
        print(f"\n{'='*60}")
        print(f"  {s['id']}: {s['description']}")
        print(f"{'='*60}")

        if set_type == "digest":
            results = run_digest_set(s, today)
        elif set_type == "freshness":
            results = run_freshness_set(s, today)
        elif set_type == "error":
            results = run_error_set(s, today)
        else:
            print(f"  Unknown type: {set_type}")
            continue

        for r in results:
            if "SKIP" in r.get("detail", ""):
                status = "SKIP"
                all_skipped += 1
            elif r["passed"]:
                status = "PASS"
                all_passed += 1
            else:
                status = "FAIL"
                all_failed += 1
            detail = f"  ({r['detail']})" if r["detail"] and "SKIP" not in r["detail"] else ""
            skip_note = f"\n       {r['detail']}" if "SKIP" in r.get("detail", "") else ""
            print(f"  [{status}] {r['label']}{detail}{skip_note}")

    print(f"\n{'='*60}")
    print(f"  Results: {all_passed} PASS  {all_failed} FAIL  {all_skipped} SKIP")
    print(f"{'='*60}\n")

    return 0 if all_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
