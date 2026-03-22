# Implementation Plan: Topic Watchlists

**Branch**: `006-topic-watchlists` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-topic-watchlists/spec.md`

## Summary

Add a `/watchlist` skill that lets users save a personal list of topics and refresh all of them with a single command. On `refresh`, the skill iterates the watchlist, skips topics that already have a digest today (detected by filename pattern), and invokes the existing `daily-digest` skill for each remaining topic. Management subcommands (`add`, `remove`, `list`) read and write a gitignored JSON config file in the project root. No new discovery logic is introduced — the watchlist is a thin orchestration layer over the existing `daily-digest` skill.

## Technical Context

**Language/Version**: Python 3.8+, stdlib only
**Primary Dependencies**: None — reuses existing `daily-digest` skill and scripts
**Storage**: `.watchlist.json` in project root (gitignored); filesystem scan of `digests/` for freshness detection
**Testing**: Manual invocation (snippets mode) + `/validate-digest` for per-topic digest quality; functional testing of add/remove/list via direct skill invocation
**Target Platform**: Claude Code skill runtime (Windows/macOS/Linux)
**Project Type**: Claude Code skill (orchestrator over existing skill)
**Performance Goals**: Sequential topic processing; no latency targets beyond user-session responsiveness
**Constraints**: Python stdlib only; no third-party packages; no scheduling; no background execution
**Scale/Scope**: Single default watchlist per project; up to ~20 topics (personal use)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: feature delivered as `.claude/skills/watchlist/watchlist.md` | I | ✅ |
| Skill format: frontmatter + User Input + Outline present | I + II | ✅ |
| Script scope: scripts perform I/O only, no business logic | II | ✅ |
| Reference material in `resources/`, not inline | II | ✅ (N/A — no rubrics/templates required for orchestrator skill) |
| Evidence requirement: all insights include direct quote | III | ✅ (enforced by `daily-digest`; watchlist is orchestrator only) |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges | III | ✅ (enforced by `daily-digest`; watchlist delegates to it) |
| Partial failure returns digest with status, not error | IV | ✅ (FR-010: topic failure isolated; run summary reports per-topic outcome) |
| Preflight checks verify hard deps before discovery | IV | ✅ (check `digests/` writable and watchlist config readable before refresh loop) |
| Python stdlib only; no third-party packages | V | ✅ |

No violations. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/006-topic-watchlists/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── watchlist-command-schema.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
.claude/skills/watchlist/
├── watchlist.md                  # Orchestrator skill (subcommands: refresh, add, remove, list)
└── scripts/
    ├── read_watchlist.py         # Read .watchlist.json → JSON list of topic entries
    ├── write_watchlist.py        # Add / remove topic from .watchlist.json
    └── find_digest.py            # Check if a digest exists for a topic on a given date

.watchlist.json                   # Gitignored watchlist config (created on first add)
.gitignore                        # Updated to include .watchlist.json
```

**Structure Decision**: Single skill directory following the existing `daily-digest` pattern. Three thin I/O scripts handle all filesystem operations. No `agents/` or `resources/` subdirectories are needed — the watchlist skill is a pure orchestrator with no discovery logic of its own.
