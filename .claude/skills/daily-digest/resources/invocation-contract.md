# Invocation Contract: daily-digest

This file is the single source of truth for the canonical invocation payload.
Both `daily-digest.md` (Outline Step 0) and all affected helper scripts reference this document.

## Payload Schema

```json
{
  "topic": "<string>",
  "hints": ["<string>", ...],
  "snippets": ["<string>", ...],
  "since": "<string>",
  "since_window": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "label": "<string>"
  }
}
```

## Field Definitions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Subject to research |
| `hints` | list[string] | No | `[]` | YouTube channels or @handles to prioritise |
| `snippets` | list[string] | No | `[]` | Pre-supplied content strings for test/manual mode |
| `since` | string | No | `"1"` | Raw `--since` value from user input |
| `since_window` | object | No | 24-hour window | Resolved date range for discovery filtering |

## Field Constraints

| Field | Constraint | Error |
|-------|-----------|-------|
| `topic` | Non-empty after stripping whitespace | `"topic is required"` |
| `topic` | ≤ 100 characters | `"topic exceeds 100 characters"` |
| `topic` | Matches `^[a-zA-Z0-9\-_ ]+$` | `"topic contains invalid characters (use alphanumeric, hyphens, underscores)"` |
| `hints` | ≤ 10 items | `"hints exceeds 10 items"` |
| each hint | ≤ 50 characters | `"hint \"<preview>...\" exceeds 50 characters"` |
| `snippets` | No constraint on count or length | — |
| `--since` (if present) | Must not be empty string | `"--since requires a value. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."` |
| `--since` (if numeric) | Must be positive integer ≥ 1 | `"since={N} is not valid — minimum value is 1."` |
| `since_window.start_date` | Valid YYYY-MM-DD, ≤ today | `"since_window.start_date is not a valid date"` |
| `since_window.start_date` | ≤ `end_date` | `"since_window.start_date must not be after end_date"` |
| Unrecognised expression | Halt with example | `"Could not interpret '--since {value}'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."` |

## Mode Routing

| Condition | Mode |
|-----------|------|
| `snippets` is empty (or all items blank after strip) | Autonomous discovery |
| `snippets` has ≥ 1 non-blank item | Test / manual mode |

`--since` applies to autonomous discovery only. Snippets are always processed regardless of date.

## Parsing Rules (applied at Step 0)

Input: `<topic> [--hints <h1,h2,...>] [--since <value>] ["snippet1" "snippet2" ...]`

1. Extract `--since <value>` if present → `since_raw`; remove flag and value from string. If absent, `since_raw = "1"`.
2. Extract `--hints <value>` if present → comma-split → `hints` list; remove flag and value from string.
3. Extract remaining quoted strings → `snippets` list; discard empty or whitespace-only entries.
4. Remaining non-flag tokens → space-join → `topic` string.
5. Resolve `since_raw` → `since_window` (see Resolution Rules below).
6. Serialize full payload to `PAYLOAD_JSON`.

`--since` is parsed before `--hints`. Argument order does not matter for flags.

## Resolution Rules

| `since` input | `start_date` | `end_date` | `label` |
|---|---|---|---|
| `"1"` (default) | today − 1 day | today | `"last 24 hours"` |
| `"N"` (N > 1, positive integer) | today − N days | today | `"last N days"` |
| `"yesterday"` | yesterday | yesterday | `"yesterday (YYYY-MM-DD)"` |
| `"last month"` | today − 30 days | today | `"last 30 days"` |
| `"<month> <year>"` e.g. `"feb 2026"` | first of that month | last of that month | `"1 Feb – 28 Feb 2026"` |
| `""` (empty) | — | — | halt with error |
| `"0"` or negative | — | — | halt with error |
| unrecognised | — | — | halt with error |

## Validation

Validation is delegated to `validate_input.py`. Call with the serialized payload JSON string:

```bash
python .claude/skills/daily-digest/scripts/validate_input.py "$PAYLOAD_JSON"
```

Exit code 0 = valid. Exit code 1 = invalid; read `error` field from JSON output for the message.

## Agent Argument Contract

Discovery agents receive `--since-start <YYYY-MM-DD>` in addition to existing arguments:

```
<topic> [--hints <h1,h2,...>] --since-start <YYYY-MM-DD>
```

`--since-start` is always present (injected from `since_window.start_date`). Agents filter out sources with a known publication date earlier than `--since-start`. Sources with no detectable date are included with `[undated]` in the summary field.
