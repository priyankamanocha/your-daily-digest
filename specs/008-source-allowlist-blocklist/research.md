# Research: Source Allowlist / Blocklist

**Branch**: `008-source-allowlist-blocklist` | **Date**: 2026-03-22

---

## Decision 1: Config File Format

**Decision**: JSON (`sources.json` at project root)

**Rationale**: The spec assumed YAML, but `pyyaml` is a third-party package — using it would violate Constitution Principle V (Python stdlib only). Python's `json` module is stdlib, fully compatible with Python 3.8+, produces human-readable, version-controllable files, and requires no additional tooling. JSON satisfies FR-011 ("human-readable and version-controllable").

**Alternatives considered**:
- YAML — rejected: requires `pyyaml` (third-party), violates Constitution V
- TOML — rejected: `tomllib` is stdlib only from Python 3.11+; project targets Python 3.8+
- INI/properties — rejected: `configparser` cannot express nested per-topic structure cleanly
- Custom line format — rejected: adds bespoke parsing complexity with no benefit over JSON

**Spec impact**: Assumption in spec.md updated to reflect JSON. FR-011 still passes (JSON is human-readable and version-controllable).

---

## Decision 2: Pipeline Integration Points

**Decision**: Three integration points in `daily-digest.md`

1. **Step 1.5 (new — after Preflight Checks)**: Load `sources.json` if present → `FILTER_CONFIG`. On syntax error, halt immediately (FR-008). If absent, `FILTER_CONFIG = null` (proceed normally per FR-009).
2. **Between Steps 4 and 5**: After discovery agents return results, apply blocklist to `manifest_sources`. Mark blocked sources with `filter_action = "blocked"`, remove them from the active candidate pool before scoring.
3. **Step 8 (modified)**: During content selection, apply allowlist guarantee: any allowlisted source with fresh content that scores ≥ 2 on at least 1 quality dimension is included regardless of ranking. Mark with `filter_action = "boosted"`. All other sources marked `filter_action = "unaffected"`.

**Rationale**: Blocklist runs pre-scoring (FR-004: "excluded before scoring"). Allowlist runs at selection (FR-005: guaranteed inclusion subject to quality floor). Config loading runs pre-discovery so a bad config halts before wasting compute (FR-008, SC-004).

**Alternatives considered**:
- Applying blocklist at agent level (inside agent prompts) — rejected: agents are separate skill files with their own contracts; coupling filter config to agents creates distributed state
- Applying allowlist at scoring step — rejected: scoring determines rank; guaranteed inclusion must override rank, so it belongs at selection not scoring

---

## Decision 3: Conflict Resolution Order

**Decision**: Four-tier precedence (highest to lowest):
1. Topic-level block
2. Topic-level allow
3. Global block
4. Global allow

**Rationale**: Block always overrides allow at the same scope level (clarified Q1). Topic-level overrides global (FR-006). Combining: a topic-level block is the strongest signal; a global allow is the weakest.

**Algorithm**:
```
For each source:
  if source in topic_blocks → filter_action = "blocked"
  elif source in topic_allows → filter_action = "boosted" (subject to quality floor)
  elif source in global_blocks → filter_action = "blocked"
  elif source in global_allows → filter_action = "boosted" (subject to quality floor)
  else → filter_action = "unaffected"
```

---

## Decision 4: Domain Matching Algorithm

**Decision**: Exact host-level matching with `www.` normalization only

**Rationale**: Confirmed in clarification Q3 — no wildcards. A bare domain entry (e.g., `example.com`) matches:
- `example.com` (exact)
- `www.example.com` (www-prefix normalization)

It does NOT match `blog.example.com` or any other subdomain.

**Algorithm** (Python stdlib, `urllib.parse`):
```python
from urllib.parse import urlparse

def extract_host(url_or_handle):
    if url_or_handle.startswith("@"):
        return url_or_handle.lower()
    parsed = urlparse(url_or_handle if "://" in url_or_handle else "https://" + url_or_handle)
    host = parsed.hostname or ""
    return host.lower()

def matches_entry(source_url, entry):
    source_host = extract_host(source_url)
    entry_normalized = extract_host(entry)
    return source_host == entry_normalized or source_host == "www." + entry_normalized
```

Handle matching is case-insensitive exact match (e.g., `@Researcher` matches `@researcher`).

---

## Decision 5: New Script vs. Inline Logic

**Decision**: New script `load_source_filters.py` for I/O (file read + JSON parse + structural validation). Matching and application logic stays in the skill's Outline (business logic in prompt, per Constitution Principle II).

**Script responsibilities** (I/O only):
- Read `sources.json` from project root
- Parse JSON (stdlib `json` module)
- Validate top-level structure (has `global` and/or `topics` keys)
- Output validated filter config as JSON to stdout, or error message on failure

**Skill Outline responsibilities** (business logic):
- Apply conflict resolution precedence
- Apply host matching algorithm
- Mark `filter_action` on each source record
- Enforce allowlist guarantee during Step 8 selection

---

## Decision 6: Manifest Impact

**Decision**: Add `filter_action` field to every SourceRecord in the manifest

**Values**: `"blocked"` | `"boosted"` | `"unaffected"`

Blocked sources still appear in `manifest.sources` (for auditability, per FR-012) but are absent from `manifest.candidates` and all section selections. The manifest schema (`manifest-schema.md`) gains one new field on SourceRecord.

**Empty filter config**: When `FILTER_CONFIG` is null (no `sources.json`), all sources get `filter_action = "unaffected"` and the manifest is unchanged in practice.
