# Implementation Plan: Source Manifest Output

**Branch**: `003-source-manifest` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-source-manifest/spec.md`

## Summary

Write a sidecar `.manifest.json` file alongside every digest. The manifest records every discovered source (with credibility and freshness scores), deduplication decisions, quality rubric scores for each candidate, and the final section selections. Implemented as a new Python I/O script (`write_manifest.py`), a new reference file (`manifest-schema.md`), and orchestrator modifications to collect and pass manifest data at each relevant step.

## Technical Context

**Language/Version**: Python 3.8+ stdlib (`json`, `os`, `sys`, `pathlib`)
**Architecture**: Extension of the existing `daily-digest` skill
- **New script**: `write_manifest.py` — derives manifest path from digest path, writes JSON
- **New resource**: `manifest-schema.md` — manifest JSON schema reference for the orchestrator
- **Modified skill**: `daily-digest.md` — collects manifest data at steps 4–8, calls `write_manifest.py` at step 9
**Primary Dependencies**: None beyond existing skill dependencies
**Storage**: `digests/{YYYY}/{MM}/` — same directory as digest output
**Testing**: Manual invocation (snippets mode) + inspect manifest file contents
**Project Type**: Extension to existing Claude Code skill
**Performance Goals**: Manifest write adds <100ms to digest generation (single JSON serialise + write)
**Constraints**: Python stdlib only; manifest written only when digest is written; no breaking changes to existing digest output
**Scale/Scope**: One manifest per digest run; typical size <100KB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: feature extends `.claude/skills/daily-digest/` | I | ✅ |
| Skill format: frontmatter + User Input + Outline present | I + II | ✅ |
| Script scope: `write_manifest.py` performs I/O only (path derivation + JSON write) | II | ✅ |
| Reference material: manifest schema in `resources/manifest-schema.md`, not inline | II | ✅ |
| Evidence requirement: all insights include direct quote (unchanged) | III | ✅ |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges (unchanged) | III | ✅ |
| Partial failure returns digest with status, not error (manifest follows digest) | IV | ✅ |
| Preflight checks verify hard deps before discovery (unchanged) | IV | ✅ |
| Python stdlib only; `json` module used for serialisation | V | ✅ |

No violations. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/003-source-manifest/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── manifest-output-schema.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude/skills/daily-digest/
├── daily-digest.md                   # Modified: collect manifest data at steps 4–8, call write_manifest.py at step 9
├── scripts/
│   └── write_manifest.py             # New: derive manifest path from digest path, write JSON
└── resources/
    └── manifest-schema.md            # New: manifest JSON schema reference

digests/{YYYY}/{MM}/                  # Generated output (unchanged)
├── digest-{date}-{slug}.md
└── digest-{date}-{slug}.manifest.json  # New: sidecar manifest
```

**Structure Decision**: Minimal extension — one new script, one new resource file, orchestrator modifications only. No new directories.

**Orchestrator modification points** (steps that feed the manifest):

| Step | Data collected |
|------|---------------|
| Step 4 — Spawn agents | `sources[]` from each agent's SOURCE: lines |
| Step 5 — Assess status | `discovery_status`, `agents_succeeded`, `agents_failed` |
| Step 6 — Score credibility | `credibility_score`, `credibility_signal` added to each source record |
| Step 7 — Extract + dedup | `deduplication_groups[]`, `candidates[]` with quality scores |
| Step 8 — Apply rubric | `quality_pass`, `rejection_reason`, `section_selections` |
| Step 9 — Build + write | Call `write_manifest.py` with assembled payload after `write_digest.py` |

## Phase 0: Research

Complete. See [research.md](research.md).

Key decisions:
1. **Format**: JSON (Python `json` stdlib, machine-parseable, diff-friendly)
2. **Data collection**: Orchestrator assembles manifest payload during execution; passes to `write_manifest.py` at step 9
3. **Path derivation**: `write_manifest.py` replaces `.md` with `.manifest.json` in the digest path
4. **New script**: `write_manifest.py` (not extending `write_digest.py` — separate concerns)
5. **Schema versioning**: `schema_version: "1.0"` field in every manifest

## Phase 1: Design

Complete. See:
- [data-model.md](data-model.md) — SourceRecord, DeduplicationGroup, CandidateRecord, SectionSelections, ManifestFile entities
- [contracts/manifest-output-schema.md](contracts/manifest-output-schema.md) — script interface, file path contract, format guarantees

## Complexity Tracking

> No constitution violations. All gates pass (see Constitution Check above).

| Addition | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|-------------------------------------|
| `write_manifest.py` new script | I/O separation — distinct from `write_digest.py` (different input type, different output format, different path derivation) | Extending `write_digest.py` would conflate markdown and JSON writing, complicating both scripts |
| `manifest-schema.md` resource | Schema reference for the orchestrator to assemble the correct JSON structure | Inline in `daily-digest.md` would bloat the skill and bury the schema in execution steps |
