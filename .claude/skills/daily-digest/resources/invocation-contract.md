# Invocation Contract: daily-digest

This file is the single source of truth for the canonical invocation payload.
Both `daily-digest.md` (Outline Step 0) and all affected helper scripts reference this document.

## Payload Schema

```json
{"topic": "<string>", "hints": ["<string>", ...], "snippets": ["<string>", ...], "no_diff": false}
```

## Field Definitions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Subject to research |
| `hints` | list[string] | No | `[]` | YouTube channels or @handles to prioritise |
| `snippets` | list[string] | No | `[]` | Pre-supplied content strings for test/manual mode |
| `no_diff` | bool | No | `false` | When `true`, skip digest diffing entirely; all discovered items pass through unfiltered |

## Field Constraints

| Field | Constraint | Error |
|-------|-----------|-------|
| `topic` | Non-empty after stripping whitespace | `"topic is required"` |
| `topic` | ≤ 100 characters | `"topic exceeds 100 characters"` |
| `topic` | Matches `^[a-zA-Z0-9\-_ ]+$` | `"topic contains invalid characters (use alphanumeric, hyphens, underscores)"` |
| `hints` | ≤ 10 items | `"hints exceeds 10 items"` |
| each hint | ≤ 50 characters | `"hint \"<preview>...\" exceeds 50 characters"` |
| `snippets` | No constraint on count or length | — |

## Mode Routing

| Condition | Mode |
|-----------|------|
| `snippets` is empty (or all items blank after strip) | Autonomous discovery |
| `snippets` has ≥ 1 non-blank item | Test / manual mode |

## Parsing Rules (applied at Step 0)

Input: `<topic> [--hints <h1,h2,...>] [--no-diff] ["snippet1" "snippet2" ...]`

1. Extract `--hints <value>` if present → comma-split → `hints` list; remove flag and value from string
2. If `--no-diff` is present as a standalone flag, set `no_diff = true` and remove it from string; otherwise `no_diff = false`
3. Extract remaining quoted strings → `snippets` list; discard empty or whitespace-only entries
4. Remaining non-flag tokens → space-join → `topic` string

## Validation

Validation is delegated to `validate_input.py`. Call with the serialized payload JSON string:

```bash
python .claude/skills/daily-digest/scripts/validate_input.py "$PAYLOAD_JSON"
```

Exit code 0 = valid. Exit code 1 = invalid; read `error` field from JSON output for the message.
