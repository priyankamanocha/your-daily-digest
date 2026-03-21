# CLI Contract: validate_digest.py

**Branch**: `004-post-write-validator` | **Date**: 2026-03-21

## Interface

```
python .claude/skills/daily-digest/scripts/validate_digest.py <digest_path>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `digest_path` | Yes | Path to the digest Markdown file to validate. Absolute or relative to the working directory. |

No flags, switches, or options. Single positional argument only.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed (or skipped). Digest is valid. |
| `1` | One or more checks failed. See report for details. |

No other exit codes are used. All error conditions (missing file, unreadable file, empty file) exit with code 1.

---

## Standard Output

The full validation report is printed to stdout on every run, regardless of pass/fail status.

**Format**:

```
Validation Report: <digest_filename>
Generated: <YYYY-MM-DD HH:MM:SS>

CHECKS
------
[PASS] Structure: all 4 required headings present
[FAIL] Count — Key Insights: found 0, expected 1–3
[PASS] Count — Anti-patterns: found 3, expected 2–4
[PASS] Count — Actions to Try: found 2, expected 1–3
[PASS] Count — Resources: found 4, expected 3–5
[FAIL] Evidence — "Title of Failing Insight": Evidence field missing or malformed
[PASS] Formatting: no unclosed code blocks detected
[SKIP] Low-signal warning: Discovery status is 'complete' — check not applicable

SUMMARY
-------
Status: FAIL
Total checks: 7 (run) + 1 (skipped)
Passed: 5  Failed: 2  Skipped: 1
```

---

## Standard Error

Used only for unexpected runtime errors (e.g., file permission denied, I/O errors).

Normal validation failures (missing evidence, wrong counts) are reported via stdout, not stderr.

---

## Report File

In addition to stdout, the report is written to:

```
<digest_dir>/<digest_filename>.validation.txt
```

The content is identical to the stdout output. The file is created (or overwritten) on every run.

**Example**: If the digest is `digests/2026/03/digest-2026-03-21-claude-code.md`, the report file is `digests/2026/03/digest-2026-03-21-claude-code.md.validation.txt`.

---

## Invocation Examples

### Called by the daily-digest orchestrator (post-write)

```bash
python .claude/skills/daily-digest/scripts/validate_digest.py "$FILE_PATH"
```

Where `$FILE_PATH` is the path returned by `build_path.py`.

### Called standalone via /validate-digest or directly

```bash
python .claude/skills/daily-digest/scripts/validate_digest.py digests/2026/03/digest-2026-03-21-claude-code.md
```

### Error case: file not found

```
Validation Report: nonexistent.md
Generated: 2026-03-21 14:32:00

ERROR: File not found: nonexistent.md

Status: FAIL
```

Exit code: `1`

---

## Constraints

- Python 3.8+ stdlib only — no third-party packages
- Cross-platform: must work on Windows, macOS, and Linux
- Read-only access to the digest file — must not modify it
- Report file write failure (e.g., permission denied) MUST print an error to stderr and exit with code 1
