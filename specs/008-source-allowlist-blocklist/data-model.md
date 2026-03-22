# Data Model: Source Allowlist / Blocklist

**Branch**: `008-source-allowlist-blocklist` | **Date**: 2026-03-22

---

## Entities

### FilterEntry

A single rule identifying one source (domain or handle) and the action to apply.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `value` | string | Yes | Non-empty. Domain (e.g., `reuters.com`) or handle (e.g., `@researcher`). Max 100 chars. |
| `list_type` | enum | Yes | `"allow"` or `"block"` |
| `scope` | enum | Yes | `"topic"` (scoped to a named topic) or `"global"` (all topics) |
| `topic` | string | Conditional | Required when `scope = "topic"`. Case-insensitive match against `payload.topic`. |

**Identity**: A FilterEntry is uniquely identified by `(value, list_type, scope, topic)`. Duplicate entries for the same `(value, scope, topic)` with different `list_type` are a conflict — resolved by block-wins rule.

**Validation rules**:
- `value` must not be empty after stripping whitespace
- Handle entries must start with `@`
- Domain entries must not start with `@`
- `topic` field must not be empty when `scope = "topic"`

---

### FilterConfig

The complete in-memory representation of all filter rules loaded from `sources.json`.

| Field | Type | Description |
|-------|------|-------------|
| `global.allow` | string[] | Domain/handle entries applied to all topics as an allowlist |
| `global.block` | string[] | Domain/handle entries applied to all topics as a blocklist |
| `topics` | object | Map of topic name → `{ allow: string[], block: string[] }` |

**Null state**: When `sources.json` does not exist, `FilterConfig` is null. The skill proceeds with no filtering — all sources receive `filter_action = "unaffected"`.

**Conflict within a topic** (same value in both `allow` and `block` for the same topic): block takes precedence. The effective action is `"blocked"`.

**Precedence order** (highest to lowest):
1. Topic-level block
2. Topic-level allow
3. Global block
4. Global allow

---

### FilteredSourceRecord

An extension of the existing `SourceRecord` (defined in `manifest-schema.md`) with one additional field.

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `filter_action` | enum | `"blocked"` \| `"boosted"` \| `"unaffected"` | The outcome of filter evaluation for this source |

- `"blocked"`: Source matched a block rule and is excluded from candidate pool and digest output. Still present in `manifest.sources` for auditability.
- `"boosted"`: Source matched an allow rule and is guaranteed inclusion in the digest if it has fresh content and scores ≥ 2 on at least 1 quality dimension.
- `"unaffected"`: No filter rule matched; source proceeds through normal ranking.

**When `FilterConfig` is null**: All sources receive `filter_action = "unaffected"`.

---

## sources.json Schema

The on-disk config file. Parsed by `load_source_filters.py`.

```json
{
  "global": {
    "allow": ["trusted-source.org", "@researchlab"],
    "block": ["spamsite.com", "@noisyaccount"]
  },
  "topics": {
    "AI safety": {
      "allow": ["alignmentforum.org"],
      "block": ["clickbait-ai.com"]
    },
    "climate": {
      "block": ["denialblog.net"]
    }
  }
}
```

**Structural validation** (enforced by `load_source_filters.py`):
- Top-level must be a JSON object
- `global` (if present) must be an object with optional `allow` and/or `block` arrays of strings
- `topics` (if present) must be an object where each value is an object with optional `allow` and/or `block` arrays of strings
- All entries in `allow`/`block` arrays must be non-empty strings
- At least one of `global` or `topics` must be present (empty file `{}` is valid but produces no rules)
- Unknown top-level keys are ignored

**File location**: `sources.json` at the repository root (same directory as `CLAUDE.md`).

---

## State Transitions

```
sources.json absent
  → FilterConfig = null
  → all sources: filter_action = "unaffected"
  → digest produced normally

sources.json present, valid
  → FilterConfig loaded
  → each source evaluated against conflict-resolution precedence
  → blocked sources: removed from candidate pool
  → boosted sources: guaranteed inclusion at Step 8 (if quality floor met)

sources.json present, syntax error
  → load_source_filters.py exits 1
  → skill halts before discovery with error message
  → no digest produced
```

---

## Relationship to Existing Data Model

| Existing Entity | Change |
|----------------|--------|
| `SourceRecord` (manifest-schema.md) | Add `filter_action` field (string enum, default `"unaffected"`) |
| `PAYLOAD_JSON` (invocation-contract.md) | No change — filter config is loaded separately |
| `manifest.sources` | Now includes blocked sources (for auditability); `filter_action` distinguishes them |
| `manifest.candidates` | Blocked sources are excluded; boosted sources guaranteed if quality floor met |
