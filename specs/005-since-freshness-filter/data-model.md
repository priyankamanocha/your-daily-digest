# Data Model: Since Freshness Filter

**Feature**: 005-since-freshness-filter
**Date**: 2026-03-22

## Payload Extensions

The canonical `PAYLOAD_JSON` gains two new fields:

```json
{
  "topic": "<string>",
  "hints": ["<string>", ...],
  "snippets": ["<string>", ...],
  "since": "<string>",
  "since_window": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "label": "<human-readable string>"
  }
}
```

### `since` field

| Property | Value |
|---|---|
| Type | string |
| Required | No |
| Default | `"1"` (injected during Step 0 if flag absent) |
| Description | Raw user input from `--since` flag |
| Examples | `"1"`, `"7"`, `"yesterday"`, `"last month"`, `"feb 2026"` |

### `since_window` field

| Property | Value |
|---|---|
| Type | object |
| Required | Yes (always present after Step 0) |
| Description | Resolved date range derived from `since` |

#### `since_window` sub-fields

| Field | Type | Description | Example |
|---|---|---|---|
| `start_date` | string (YYYY-MM-DD) | Earliest eligible publication date (inclusive) | `"2026-03-21"` |
| `end_date` | string (YYYY-MM-DD) | Latest eligible publication date (always run date) | `"2026-03-22"` |
| `label` | string | Human-readable description for digest output | `"last 24 hours"` |

## Resolution Rules

| `since` input | `start_date` | `label` |
|---|---|---|
| `"1"` (default) | run date − 1 day | `"last 24 hours"` |
| `"N"` (positive integer) | run date − N days | `"last N days"` |
| `"yesterday"` | previous calendar day | `"yesterday (YYYY-MM-DD)"` |
| `"last month"` | run date − 30 days | `"last 30 days"` |
| `"<month> <year>"` (e.g. `"feb 2026"`) | first day of that month | `"1 Feb – 28 Feb 2026"` |
| invalid / empty | — | halt with error (no window produced) |

`end_date` is always the run date for all cases.

## Agent Argument Extension

Agents receive an updated argument string:

```
<topic> [--hints <h1,h2,...>] --since-start <YYYY-MM-DD>
```

`--since-start` is always present (injected with the resolved `start_date`). Agents filter out any source whose publication date is before `--since-start`. Undated sources are included regardless, flagged as `undated`.

## Validation Rules (validate_input.py)

Applied to the resolved `since_window` object:

| Check | Error message |
|---|---|
| `start_date` parses as valid date | `"since_window.start_date is not a valid date"` |
| `end_date` parses as valid date | `"since_window.end_date is not a valid date"` |
| `start_date` ≤ `end_date` | `"since_window.start_date must not be after end_date"` |
| `start_date` ≤ today | `"since_window.start_date cannot be in the future"` |

## Digest Header Change

```
Generated: {YYYY-MM-DD HH:MM}
Discovery: {status}
Sources: {since_window.label}
```

`Sources:` line is always present, including in snippets mode (where it shows `"manual"` for the existing discovery mode).

## Unchanged

- `freshness-policy.md` scoring rules — unchanged (orthogonal to discovery filter)
- Quality rubric — unchanged
- Manifest schema — `since_window` is not written to the manifest (run metadata only)
