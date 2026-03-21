# Quickstart: Post-Write Digest Validator

**Branch**: `004-post-write-validator` | **Date**: 2026-03-21

## What This Is

A Python script (`validate_digest.py`) that checks any written digest file against the format contract defined in `digest-template.md`. It runs automatically after every `write_digest.py` call and can also be invoked standalone on any existing digest.

## Prerequisites

- Python 3.8+ (same requirement as all other scripts in this project)
- A digest file written by the `daily-digest` skill

## Standalone Usage

Validate any digest file:

```bash
python .claude/skills/daily-digest/scripts/validate_digest.py <path-to-digest>
```

**Example**:
```bash
python .claude/skills/daily-digest/scripts/validate_digest.py digests/2026/03/digest-2026-03-21-claude-code.md
```

Exit 0 = valid. Exit 1 = check failures (see report).

## Checking the Report

After running, two identical reports are available:

1. **Terminal**: printed to stdout immediately
2. **File**: `<digest-path>.validation.txt` in the same directory as the digest

## What Gets Checked

| Check | What It Validates |
|-------|------------------|
| Structure | All 4 required section headings are present |
| Count — Key Insights | 1–3 insight items (### sub-headings) |
| Count — Anti-patterns | 2–4 anti-pattern items (- ** list items) |
| Count — Actions to Try | 1–3 action items (### sub-headings) |
| Count — Resources | 3–5 resource items (- ** list items) |
| Evidence | Every insight has `**Evidence**: "quoted text"` |
| Formatting | No unclosed fenced code blocks |
| Low-signal warning | `⚠️ Low-signal content` footer present when Discovery line says `partial` or `timeout` |

## Integration Point in daily-digest.md

The script is called in Step 9, immediately after `write_digest.py`:

```
### 9. Build Output Path and Write Digest

python .claude/skills/daily-digest/scripts/build_path.py "$TOPIC"
python .claude/skills/daily-digest/scripts/write_digest.py "$FILE_PATH" "$CONTENT"
python .claude/skills/daily-digest/scripts/validate_digest.py "$FILE_PATH"
```

If the validator exits with code 1, the orchestrator stops and reports the validation failures. The digest file remains on disk for inspection.

## Testing with Fixture Files

To test the validator during development, create a minimal digest fixture and run:

```bash
python .claude/skills/daily-digest/scripts/validate_digest.py tests/fixtures/digest-valid.md
python .claude/skills/daily-digest/scripts/validate_digest.py tests/fixtures/digest-missing-evidence.md
```

Expected exit codes: 0 for valid fixtures, 1 for invalid fixtures.

## Relationship to /validate-digest

`/validate-digest` runs the full skill against benchmark inputs and checks the results. `validate_digest.py` validates any already-written digest file. They are complementary:

- `/validate-digest` → checks skill quality against known inputs (benchmark-level)
- `validate_digest.py` → checks every written digest against the format contract (post-write gate)
