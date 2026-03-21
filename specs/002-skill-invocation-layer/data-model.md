# Data Model: Skill Invocation Layer

**Feature**: 002-skill-invocation-layer
**Date**: 2026-03-21

## Invocation Payload

The canonical structured object produced by the entrypoint. It is the single source of truth for invocation data throughout a skill run.

### Fields

| Field | Type | Required | Default | Constraints |
|---|---|---|---|---|
| `topic` | string | Yes | — | 1–100 chars; alphanumeric, hyphens, underscores, spaces only |
| `hints` | list[string] | No | `[]` | 0–10 items; each item ≤50 chars |
| `snippets` | list[string] | No | `[]` | 0–N items; empty-string items are ignored |

### Validation Rules

- `topic` after stripping whitespace must be non-empty
- `topic` must match pattern `^[a-zA-Z0-9\-_ ]+$`
- `hints` list length must not exceed 10
- Each hint must not exceed 50 characters
- Snippet items that are empty or whitespace-only are discarded before mode selection

### Mode Routing (derived from payload)

| Condition | Mode |
|---|---|
| `snippets` is empty (or all items blank after strip) | Autonomous discovery |
| `snippets` has ≥1 non-blank item | Test / manual mode |

### Wire Format

Serialized as a compact JSON string for transport to scripts:

```json
{"topic": "AI agents", "hints": ["channel1", "channel2"], "snippets": []}
```

Produced by the entrypoint step in the skill Outline; consumed by `validate_input.py` and `build_path.py`.

---

## Entity Relationships

```
$ARGUMENTS (raw string)
    │
    ▼ (Outline Step 0 — entrypoint)
Invocation Payload  ──────────────────────────────────────┐
    │                                                      │
    ▼ (Step 2)                                             ▼ (Step 9)
validate_input.py                                    build_path.py
  └─ returns validated payload or error                └─ returns digest file path
    │
    ▼ (Step 3)
Mode selection
  ├─ snippets present → Test mode (Step 8)
  └─ no snippets      → Discovery mode (Steps 4–7)
                              │
                              ▼
                    Agents receive payload.topic, payload.hints
```

---

## Unchanged Entities

These entities exist in the current skill and are not modified by this feature:

| Entity | Description |
|---|---|
| Digest | Output markdown file written by `write_digest.py`; keyed by date + topic slug |
| Discovery Agent | Parallel subagent for web/video/social discovery; receives topic + hints extracted from payload |
| Credibility Score | Source quality score applied during synthesis; defined in `credibility-rules.md` |
