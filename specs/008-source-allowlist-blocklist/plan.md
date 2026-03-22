# Implementation Plan: Source Allowlist / Blocklist

**Branch**: `008-source-allowlist-blocklist` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-source-allowlist-blocklist/spec.md`

## Summary

Add persistent per-topic source filtering to the `daily-digest` skill. Users create an optional `sources.json` file at the repo root listing trusted sources (allowlist) and noisy sources (blocklist) per topic or globally. Blocked sources are excluded before scoring. Allowlisted sources with fresh content and a minimum quality score are guaranteed inclusion. The config is loaded in preflight and all filter decisions are recorded in the sidecar manifest.

## Technical Context

**Language/Version**: Python 3.8+, stdlib only
**Primary Dependencies**: `json` (stdlib), `urllib.parse` (stdlib)
**Storage**: `sources.json` at repo root (optional, user-managed file)
**Testing**: Manual invocation (snippets mode) + `/validate-digest`
**Target Platform**: Claude Code session
**Project Type**: Claude Code Skill (markdown prompt + Python utility scripts)
**Performance Goals**: No new latency beyond a single synchronous file read before discovery
**Constraints**: Python stdlib only; no third-party packages; script scope is I/O only
**Scale/Scope**: Config file supports any number of topics; no rule count limit enforced (practical limit is human maintainability)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: feature delivered as `.claude/skills/<name>/<name>.md` | I | ✅ Feature extends existing `daily-digest.md` skill |
| Skill format: frontmatter + User Input + Outline present | I + II | ✅ Existing format preserved; new steps added to Outline |
| Script scope: scripts perform I/O only, no business logic | II | ✅ `load_source_filters.py` reads file and validates structure only; matching/application logic in Outline |
| Reference material in `resources/`, not inline | II | ✅ No new reference material needed inline |
| Evidence requirement: all insights include direct quote | III | ✅ Not affected by this feature |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges | III | ✅ Not affected (allowlist guarantee adds sources, counts still enforced) |
| Partial failure returns digest with status, not error | IV | ✅ Config syntax error halts pre-discovery — this is a hard user error, not a partial discovery failure |
| Preflight checks verify hard deps before discovery | IV | ✅ Config loading added to preflight step (Step 1.5) |
| Python stdlib only; no third-party packages | V | ✅ JSON (stdlib) used instead of YAML — see research.md Decision 1 |

**No violations. Complexity Tracking table omitted.**

## Project Structure

### Documentation (this feature)

```text
specs/008-source-allowlist-blocklist/
├── plan.md                              # This file
├── research.md                          # Phase 0: decisions on format, pipeline, matching
├── data-model.md                        # Phase 1: entities and schema
├── quickstart.md                        # Phase 1: user-facing usage guide
├── contracts/
│   └── filter-config-schema.md          # Phase 1: sources.json contract
├── checklists/
│   └── requirements.md                  # Spec quality checklist
└── tasks.md                             # Phase 2 output (/speckit.tasks command)
```

### Source Code Changes

```text
.claude/skills/daily-digest/
├── daily-digest.md                      # MODIFIED: add Steps 1.5 + filter application in Steps 4–5 and 8
├── scripts/
│   └── load_source_filters.py           # NEW: read + validate sources.json, output filter config as JSON
└── resources/
    └── manifest-schema.md               # MODIFIED: add filter_action field to SourceRecord

sources.json                             # NEW (user-created, not committed by default): source filter config
```

**Structure Decision**: No new top-level directories. One new script under `scripts/`, two modified skill files (`daily-digest.md`, `manifest-schema.md`), and a user-managed optional config at the repo root.

## Phase 0: Research

See [research.md](research.md) for full findings. Summary of decisions:

| Question | Decision |
|----------|----------|
| Config file format | JSON (`sources.json`) — YAML requires third-party `pyyaml`; JSON is stdlib |
| Pipeline: blocklist | Applied between Steps 4 and 5, before scoring |
| Pipeline: allowlist | Applied in Step 8 (guaranteed inclusion at selection, not ranking) |
| Config load point | New Step 1.5 (after preflight, before input validation) |
| Conflict resolution | Topic block → Topic allow → Global block → Global allow |
| Domain matching | Exact host-level; `example.com` also matches `www.example.com`; no wildcards |
| Handle matching | Case-insensitive exact match; platform-agnostic |
| Manifest impact | Add `filter_action` field to every SourceRecord |
| New script scope | `load_source_filters.py` — file I/O and structural validation only |

## Phase 1: Design

### Step 1.5 — Load Source Filters (new Outline step)

Insert between existing Step 1 (Preflight Checks) and Step 2 (Validate Input):

```
Run: python .claude/skills/daily-digest/scripts/load_source_filters.py

Exit 0: parse stdout JSON → FILTER_CONFIG (object with global + topics)
Exit 1: halt immediately with error from stdout ({"error": "<message>"})
Exit 2: FILTER_CONFIG = null (no sources.json — proceed normally)
```

### Blocklist Application (between Steps 4 and 5)

After all discovery agents return results, before Step 5 (Assess Discovery Status):

```
For each source in manifest_sources:
  Resolve effective_action using FILTER_CONFIG conflict-resolution precedence
  Set source.filter_action = effective_action
  If effective_action == "blocked":
    Remove source from active candidate pool (keep in manifest_sources for audit)
```

Topic matching: case-insensitive comparison of config topic key against `payload.topic`.
Host matching: per research.md Decision 4 (`urllib.parse` + `www.` normalization).
Handle matching: case-insensitive exact comparison of `@handle` strings.

If `FILTER_CONFIG` is null: set all sources to `filter_action = "unaffected"`, no filtering applied.

### Allowlist Guarantee (Step 8 modification)

During content selection after quality rubric scoring:

```
For each source with filter_action == "boosted":
  If source has content within freshness window
  AND source scores >= 2 on at least 1 quality dimension:
    Include in digest regardless of ranking
    These count toward section totals (1–3 insights, etc.)
```

If including boosted sources pushes a section above its maximum, the boosted source takes precedence and the lowest-ranking non-boosted candidate is dropped.

### load_source_filters.py Contract

```
Input:  none (reads sources.json from cwd)
Output: JSON to stdout
Exit 0: {"filter_config": {<global+topics object>}}
Exit 1: {"error": "sources.json: <message>"}
Exit 2: {"filter_config": null}
```

Validation checks (in order):
1. File read — if IOError, exit 2
2. JSON parse — if invalid, exit 1 with line number from exception
3. Root is an object — if not, exit 1
4. `global` is object (if present) — if not, exit 1
5. `global.allow` / `global.block` are arrays of non-empty strings (if present) — if not, exit 1
6. `topics` is object (if present) — if not, exit 1
7. Each topic value is object with optional `allow`/`block` arrays of non-empty strings — if not, exit 1

### manifest-schema.md Change

Add to SourceRecord field table:

| Field | Type | Notes |
|-------|------|-------|
| `filter_action` | enum or null | `"blocked"` \| `"boosted"` \| `"unaffected"`. `null` for legacy manifests written before this feature. |

Blocked sources remain in `manifest.sources` but are absent from `manifest.candidates` and all `section_selections`.
