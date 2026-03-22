# Contract Delta: Invocation Contract — Digest Diffing

**Branch**: `007-digest-diffing` | **Date**: 2026-03-22
**Base contract**: `.claude/skills/daily-digest/resources/invocation-contract.md`

This document describes the changes made to the invocation contract by the digest diffing feature. The base contract file is updated in-place during implementation.

---

## Payload Schema (updated)

```json
{
  "topic": "<string>",
  "hints": ["<string>", ...],
  "snippets": ["<string>", ...],
  "no_diff": false
}
```

## New Field

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `no_diff` | bool | No | `false` | When `true`, skip digest diffing entirely; all discovered items pass through |

## Updated Parsing Rules (Step 0 addition)

After the existing flag extraction steps, add:

4. If `--no-diff` is present as a standalone flag in the remaining argument string, set `no_diff = true` and remove the flag. Otherwise `no_diff = false`.

## Updated Payload Serialization

```
PAYLOAD_JSON = {"topic": "...", "hints": [...], "snippets": [...], "no_diff": false}
```

## Validation

No validation errors are added for `no_diff`. It is a presence/absence boolean flag — invalid values default to `false`.

## New Script Interface: diff_digest.py

This script is called at Step 3.5 (when `no_diff == false`).

**Command**:
```bash
python .claude/skills/daily-digest/scripts/diff_digest.py <topic_slug> [--window-days 7]
```

**Output** (stdout, JSON):

Success case (qualifying baseline found):
```json
{
  "found": true,
  "baseline_date": "2026-03-21",
  "baseline_path": "digests/2026/03/digest-2026-03-21-claude-cowork.md",
  "sections": {
    "key_insights": ["Title A", "Title B"],
    "anti_patterns": ["Pattern Name X"],
    "actions": ["Action Title 1"],
    "resources": ["Resource Title 1"]
  }
}
```

No baseline case:
```json
{"found": false}
```

**Exit codes**:
- `0`: Success (even when `found: false` — that is a normal outcome, not an error)
- `1`: Unexpected I/O or argument error; skill proceeds as if `found: false`

## Skill Outline Changes Summary

| Step | Change |
|---|---|
| Step 0 | Parse `--no-diff` flag → `payload.no_diff` |
| Step 3.5 (new) | If `no_diff == false`: call `diff_digest.py`, store result as `diff_baseline` |
| Step 8 | After quality selection: filter repeats using `diff_baseline` if `found == true`; assemble `DiffResult` |
| Step 9 | If `diff_result.suppressed_count > 0`: append footer note |
