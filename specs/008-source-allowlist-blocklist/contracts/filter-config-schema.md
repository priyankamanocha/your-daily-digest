# Filter Config Schema: sources.json

This file is the single source of truth for the `sources.json` config format consumed by the `daily-digest` skill.

---

## File Location

```
{repo-root}/sources.json
```

The file is optional. Its absence is a normal condition — the skill runs without filtering.

---

## Top-Level Schema

```json
{
  "global": {
    "allow": ["<entry>", ...],
    "block": ["<entry>", ...]
  },
  "topics": {
    "<topic-name>": {
      "allow": ["<entry>", ...],
      "block": ["<entry>", ...]
    }
  }
}
```

Both `global` and `topics` are optional. An empty object `{}` is valid (produces no rules).

---

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `global` | object | No | Rules applied to every digest run regardless of topic |
| `global.allow` | string[] | No | Domains/handles to prioritize globally |
| `global.block` | string[] | No | Domains/handles to exclude globally |
| `topics` | object | No | Map of topic name → per-topic rules |
| `topics.<name>` | object | No | Rules for the named topic only |
| `topics.<name>.allow` | string[] | No | Domains/handles to prioritize for this topic |
| `topics.<name>.block` | string[] | No | Domains/handles to exclude for this topic |

---

## Entry Format

Each entry in an `allow` or `block` array is a string in one of two forms:

| Form | Example | Matches |
|------|---------|---------|
| Domain | `"reuters.com"` | `reuters.com` and `www.reuters.com` only |
| Handle | `"@researchlab"` | `@researchlab` (case-insensitive, any platform) |

**No wildcard syntax** — entries are exact host-level matches. To target a specific subdomain, use its full name (e.g., `"blog.reuters.com"`).

---

## Constraints

| Field | Constraint | Error |
|-------|------------|-------|
| File | Must be valid JSON | Halt: `"sources.json: invalid JSON at line N"` |
| `global` | Must be an object if present | Halt: `"sources.json: 'global' must be an object"` |
| `topics` | Must be an object if present | Halt: `"sources.json: 'topics' must be an object"` |
| Each topic value | Must be an object | Halt: `"sources.json: topic '<name>' must be an object"` |
| Each `allow`/`block` | Must be an array of strings | Halt: `"sources.json: '<path>' must be an array of strings"` |
| Each entry | Non-empty string | Halt: `"sources.json: empty entry in '<path>'"` |
| File absent | Not an error | Proceed with no filtering |
| File empty (`{}`) | Not an error | Proceed with no rules |

---

## Conflict Resolution

When the same source appears in multiple rule sets, this precedence order applies (highest wins):

1. Topic-level `block`
2. Topic-level `allow`
3. Global `block`
4. Global `allow`

A source in both `allow` and `block` within the same topic is always blocked (block wins).

---

## Allowlist Guarantee

An allowlisted source is **guaranteed inclusion** in the digest if:
- The source has content within the active freshness window, AND
- The source's content scores ≥ 2 on at least 1 quality dimension

If neither condition is met, the source is not included (no error or warning is raised).

---

## Validation

Validation is performed by `load_source_filters.py`:

```bash
python .claude/skills/daily-digest/scripts/load_source_filters.py
```

Reads `sources.json` from the current working directory.

| Exit code | Meaning |
|-----------|---------|
| `0` | File loaded and valid. JSON filter config written to stdout. |
| `1` | File present but invalid. Error message written to stdout as `{"error": "<message>"}`. |
| `2` | File not found. Outputs `{"filter_config": null}` — proceed without filtering. |

---

## Example

```json
{
  "global": {
    "block": ["contentfarm.io", "@spambot"]
  },
  "topics": {
    "AI safety": {
      "allow": ["alignmentforum.org", "@paulchristiano"],
      "block": ["hypesite.ai"]
    },
    "climate": {
      "allow": ["carbonbrief.org"],
      "block": ["denialblog.net", "oilsponsored.com"]
    }
  }
}
```
