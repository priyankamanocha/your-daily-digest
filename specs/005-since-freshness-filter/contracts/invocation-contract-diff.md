# Contract Change: Invocation Contract

**Source of truth**: `.claude/skills/daily-digest/resources/invocation-contract.md`
**Change type**: Additive (new optional field, backwards compatible)

## New Argument

```
/daily-digest <topic> [--hints <h1,h2>] [--since <value>] ["snippet1" ...]
```

`--since` is parsed before `--hints`. If both are present, order does not matter.

## Payload Schema Change

**Before**:
```json
{"topic": "<string>", "hints": ["<string>", ...], "snippets": ["<string>", ...]}
```

**After**:
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

## New Field Constraints

| Field | Constraint | Error |
|---|---|---|
| `--since` (if present) | Must not be empty string | `"--since requires a value"` |
| `--since` (if numeric) | Must be positive integer ≥ 1 | `"since must be a positive number (minimum: 1)"` |
| `since_window.start_date` | Valid YYYY-MM-DD, not in the future | `"since_window.start_date is not a valid date"` |
| `since_window.start_date` | ≤ `end_date` | `"since_window.start_date must not be after end_date"` |
| Unrecognised expression | Halt with example | `"Could not interpret '--since <value>'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."` |

## Mode Routing (unchanged)

`--since` does not affect mode routing. Snippets mode is still triggered by non-empty `snippets`. `--since` applies to autonomous discovery only.

## Agent Argument Contract

Discovery agents now always receive `--since-start <YYYY-MM-DD>`:

```
<topic> [--hints <h1,h2>] --since-start <YYYY-MM-DD>
```

Agents MUST filter sources with a known publication date earlier than `--since-start`. Undated sources are included with an `[undated]` flag.

## Backwards Compatibility

- Omitting `--since` is equivalent to `--since 1` (24-hour window). Existing invocations are unaffected.
- The `Sources:` line added to digest output is additive and does not break existing consumers.
