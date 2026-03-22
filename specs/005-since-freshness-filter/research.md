# Research: Since Freshness Filter

**Feature**: 005-since-freshness-filter
**Date**: 2026-03-22

## Overview

No external technologies are introduced. Research focuses on design decisions: payload extension, window resolution, agent communication, and interaction with existing systems.

---

## Decision Log

### D-001: Where does `--since` live in the payload?

**Decision**: Two fields added to `PAYLOAD_JSON`:
- `since` (string) — the raw user input (e.g. `"7"`, `"yesterday"`, `"feb 2026"`)
- `since_window` (object) — the resolved date range: `{start_date, end_date, label}`

**Rationale**: Separating raw input from resolved output keeps Step 0 (resolution) and Step 2 (validation) responsibilities clean. Downstream steps (agents, digest writer) consume only `since_window` — they never need to re-parse the raw value.

**Alternatives considered**:
- Store only the resolved window: rejected — loses auditability of what the user typed, makes error messages less precise
- Store only the raw value and re-resolve later: rejected — forces every consumer to implement resolution logic

---

### D-002: How is the freshness window communicated to discovery agents?

**Decision**: Pass `--since-start <YYYY-MM-DD>` as an additional flag in the agent argument string. The orchestrator constructs: `{topic} [--hints ...] --since-start <start_date>`.

**Rationale**: Consistent with the existing `--hints` pattern. Agents receive a single clean string and parse flags from it. ISO 8601 date format is unambiguous and requires no further interpretation.

**Alternatives considered**:
- Pass the full window object as JSON: rejected — breaks the simple string argument contract; agents would need JSON parsing
- Pass number of days instead of a date: rejected — agents would need to compute the cutoff date themselves (business logic in agents, violates Principle II)

---

### D-003: How does `--since` interact with the existing freshness-policy.md?

**Decision**: They are independent concerns. No change to `freshness-policy.md`.

- `--since` = **discovery filter** — determines which sources agents consider at all. Applied before any scoring.
- `freshness-policy.md` = **freshness score** — ranks sources that pass the filter. A source 2 days old scores 3; a source 25 days old scores 1. Both can appear in the same digest if both are within the `--since` window.

**Rationale**: The freshness score was designed for ranking, not gating. Mixing the two would create an inconsistency: a 30-day window with `--since 30` would still score old sources low, which is correct (they're relatively stale within the window). The filter and scorer are orthogonal.

---

### D-004: Where does natural language date resolution happen?

**Decision**: In `SKILL.md` Step 0 (LLM reasoning), not in a Python script.

**Rationale**: The constitution (Principle II) states business logic belongs in the skill Outline. Date resolution ("feb 2026" → `2026-02-01` to `2026-02-28`) is LLM-executable reasoning, not I/O. No Python stdlib date library is needed for this.

**Alternatives considered**:
- `parse_since.py` — rejected; adds a file for logic Claude can do inline, violates Principle V (no new scripts unless existing files cannot handle it)
- Absorb into `validate_input.py` — rejected; conflates resolution with validation; validation should check the already-resolved window, not re-implement resolution

---

### D-005: What does `validate_input.py` validate for `--since`?

**Decision**: `validate_input.py` validates the already-resolved `since_window` object, not the raw `since` string. Specifically:
- `start_date` must be a valid ISO 8601 date string (`YYYY-MM-DD`)
- `end_date` must be a valid ISO 8601 date string
- `start_date` ≤ `end_date`
- `start_date` ≤ today (no future windows)

**Rationale**: By the time validation runs (Step 2), resolution is already complete (Step 0). The script acts as a sanity check on the resolved output — consistent with its existing role as a boundary validator.

---

### D-006: What does the no-content fallback message include?

**Decision**: The fallback message includes the active window label:

```
No relevant content discovered for '{topic}' in the {label}.

Try widening the time window: /daily-digest "{topic}" --since 7
Or provide content manually: /daily-digest "{topic}" "[snippet 1]"
```

**Rationale**: Without the window in the message, the user cannot diagnose why discovery returned nothing. Including it also implicitly teaches the `--since` flag.

---

### D-007: Where does the active window appear in the digest output?

**Decision**: Add a `Sources:` metadata line to the digest header, directly below the `Discovery:` line.

```
Generated: 2026-03-22 09:00
Discovery: complete
Sources: last 24 hours
```

**Rationale**: FR-010 requires the window to be visible. The header is the natural location — it's already where run metadata lives. No new section needed.
