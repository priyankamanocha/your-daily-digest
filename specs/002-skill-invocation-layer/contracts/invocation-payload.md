# Contract: Invocation Payload

**Feature**: 002-skill-invocation-layer
**Date**: 2026-03-21
**Runtime location**: `.claude/skills/daily-digest/resources/invocation-contract.md`

This document defines the interface contract between the skill entrypoint and all consumers (orchestrator steps, helper scripts). It will be created as a `resources/` file during implementation.

---

## Payload Schema

```json
{
  "topic":    "<string>",
  "hints":    ["<string>", ...],
  "snippets": ["<string>", ...]
}
```

### Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `topic` | string | **Yes** | Subject to research. Stripped of leading/trailing whitespace. |
| `hints` | array of strings | No | YouTube channels or @handles to prioritise. Empty array if not provided. |
| `snippets` | array of strings | No | Pre-supplied content strings for test/manual mode. Empty array if not provided. |

### Field Constraints

| Field | Constraint | Error message |
|---|---|---|
| `topic` | Non-empty after strip | `"topic is required"` |
| `topic` | ≤100 characters | `"topic exceeds 100 characters"` |
| `topic` | Matches `^[a-zA-Z0-9\-_ ]+$` | `"topic contains invalid characters (use alphanumeric, hyphens, underscores)"` |
| `hints` | ≤10 items | `"hints exceeds 10 items"` |
| each hint | ≤50 characters | `"hint \"<preview>...\" exceeds 50 characters"` |
| `snippets` | No constraint on count or length | — |

---

## Producer

**Who**: Skill Outline Step 0 (entrypoint section of `daily-digest.md`)
**How**: Parses raw `$ARGUMENTS` string → constructs payload object → serializes to JSON string (`PAYLOAD_JSON`)

### Parsing Rules

```
Input:  <topic> [--hints <h1,h2,...>] ["snippet1" "snippet2" ...]

1. Extract --hints <value>: comma-split, strip each item → hints list
2. Extract quoted strings (not part of --hints) → snippets list
3. Remaining unquoted text (excluding --hints flag and its value) → topic string
4. Default hints = [], snippets = [] if not present
```

---

## Consumers

| Consumer | How payload is received | Fields used |
|---|---|---|
| `validate_input.py` | Single JSON string argument: `python validate_input.py "$PAYLOAD_JSON"` | `topic`, `hints`, `snippets` |
| `build_path.py` | Single JSON string argument: `python build_path.py "$PAYLOAD_JSON"` | `topic` |
| Orchestrator (Step 3–7) | In-memory: reads `payload.topic`, `payload.hints`, `payload.snippets` from validated result | `topic`, `hints`, `snippets` |

---

## Response Contracts

### `validate_input.py` response

**Success** (exit code 0):
```json
{"valid": true, "topic": "<stripped topic>", "hints": ["<h1>", ...], "snippets": ["<s1>", ...]}
```

**Failure** (exit code 1):
```json
{"valid": false, "error": "<human-readable message>"}
```

### `build_path.py` response

**Success** (exit code 0, stdout):
```
digests/YYYY/MM/digest-YYYY-MM-DD-<topic-slug>.md
```

---

## Versioning

This contract is versioned with the skill. Changes to field names, types, or constraints require:
1. Updating `resources/invocation-contract.md`
2. Updating all consumers listed above
3. Re-running `/validate-digest` to confirm end-to-end behaviour
