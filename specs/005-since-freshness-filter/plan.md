# Implementation Plan: Since Freshness Filter

**Branch**: `005-since-freshness-filter` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-since-freshness-filter/spec.md`

## Summary

Add a `--since` flag to `/daily-digest` that controls how far back discovery agents look for content. Defaults to 24 hours (since=1) — matching the daily-brief intent. Supports numeric (days), `yesterday`, `last month`, and `<month> <year>` expressions. Invalid input halts with a clear error. The active window is displayed in the digest header. Changes are confined to the existing skill and its supporting files — no new scripts or agent files are needed.

## Technical Context

**Language/Version**: Python 3.8+ stdlib only (utility scripts); Claude Code skill (Markdown)
**Primary Dependencies**: Claude Code built-in tools (`WebSearch`, `WebFetch`); Python stdlib `datetime` for date validation in `validate_input.py`
**Storage**: File system (digest output, manifest output — unchanged)
**Testing**: Manual invocation (`/daily-digest <topic> --since <value>`) + `/validate-digest`
**Target Platform**: Claude Code IDE session
**Project Type**: Claude Code skill
**Performance Goals**: `--since` parsing adds no perceptible latency (LLM reasoning, no network calls)
**Constraints**: Python stdlib only; no new scripts unless existing files cannot handle the need
**Scale/Scope**: Single-user skill; all changes are additive to existing files

## Constitution Check

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: feature delivered as `.claude/skills/<name>/<name>.md` | I | ✅ |
| Skill format: frontmatter + User Input + Outline present | I + II | ✅ |
| Script scope: scripts perform I/O only, no business logic | II | ✅ |
| Reference material in `resources/`, not inline | II | ✅ |
| Evidence requirement: all insights include direct quote | III | ✅ |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges | III | ✅ |
| Partial failure returns digest with status, not error | IV | ✅ |
| Preflight checks verify hard deps before discovery | IV | ✅ |
| Python stdlib only; no third-party packages | V | ✅ |

All gates pass. No violations.

**Notes**:
- Date resolution ("feb 2026" → date range) lives in `SKILL.md` Step 0 (LLM reasoning), not in Python — satisfies Principle II.
- `validate_input.py` only validates the already-resolved `since_window` object (sanity check at I/O boundary) — satisfies Principle II.
- No new scripts or agent files are created — satisfies Principle V (YAGNI).

## Project Structure

### Documentation (this feature)

```text
specs/005-since-freshness-filter/
├── plan.md                          # This file
├── research.md                      # Phase 0 output
├── data-model.md                    # Phase 1 output
├── contracts/
│   └── invocation-contract-diff.md  # Phase 1 output
└── tasks.md                         # Phase 2 output (/speckit.tasks)
```

### Source Code Changes

All changes are modifications to existing files. No new files are created.

```text
.claude/skills/daily-digest/
├── SKILL.md                         # MODIFY — Steps 0, 2, 4, 9, 10
├── scripts/
│   └── validate_input.py            # MODIFY — add since_window validation
├── resources/
│   ├── invocation-contract.md       # MODIFY — add since / since_window fields
│   └── digest-template.md           # MODIFY — add Sources: line to header
└── agents/
    ├── web-discovery-agent.md       # MODIFY — add --since-start arg and date filter
    ├── video-discovery-agent.md     # MODIFY — add --since-start arg and date filter
    └── social-discovery-agent.md    # MODIFY — add --since-start arg and date filter
```

**Structure Decision**: Single skill, no new files. All changes are additive modifications to existing files. Consistent with the project's no-build-cycle, skill-first architecture.

## Phase 0: Research

See [research.md](research.md) — all design decisions resolved.

Key decisions:
- **D-001**: Two payload fields: `since` (raw) + `since_window` (resolved) — clean separation of parsing and downstream consumption
- **D-002**: Window passed to agents as `--since-start <YYYY-MM-DD>` flag — consistent with existing `--hints` pattern
- **D-003**: `--since` is orthogonal to `freshness-policy.md` — filter vs. scorer; no change to `freshness-policy.md`
- **D-004**: Date resolution in `SKILL.md` Step 0 (LLM reasoning) — no Python needed, Principle II compliant
- **D-005**: `validate_input.py` validates resolved `since_window` (boundary check only) — Principle II compliant
- **D-006**: No-content fallback message includes window label and a `--since` widening hint
- **D-007**: `Sources: {label}` line added to digest header below `Discovery:`

## Phase 1: Design

See [data-model.md](data-model.md) and [contracts/invocation-contract-diff.md](contracts/invocation-contract-diff.md).

### Change Specifications

#### SKILL.md — Step 0 (Parse Invocation)

Add `--since` parsing before existing flag parsing:

1. If `--since <value>` is present, extract value → `since_raw`. Remove flag and value from argument string. If absent, `since_raw = "1"`.
2. Resolve `since_raw` to a `since_window`:
   - Numeric string N (positive integer): `start_date = today − N days`, `label = "last 24 hours"` (N=1) or `"last N days"` (N>1)
   - `"yesterday"`: `start_date = today − 1 day`, `label = "yesterday (YYYY-MM-DD)"`
   - `"last month"`: `start_date = today − 30 days`, `label = "last 30 days"`
   - `"<month> <year>"` (e.g. `"feb 2026"`): `start_date = first day of month`, `end_date = last day of month`, `label = "1 Feb – 28 Feb 2026"`
   - `""` or unrecognised: halt immediately with error — do not fall back to default
3. `end_date` is always today's date (run date) for all cases except `<month> <year>`, where it is the last day of that month.
4. Add to payload JSON: `"since": "<since_raw>", "since_window": {"start_date": "...", "end_date": "...", "label": "..."}`

Updated `PAYLOAD_JSON` shape:
```json
{
  "topic": "<topic>",
  "hints": [<hints>],
  "snippets": [<snippets>],
  "since": "<since_raw>",
  "since_window": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "label": "<label>"}
}
```

#### SKILL.md — Step 2 (Validate Input)

`validate_input.py` now receives the full extended payload (including `since_window`). No change to the call itself — the script handles new fields.

#### SKILL.md — Step 4 (Spawn Discovery Agents)

Append `--since-start {since_window.start_date}` to each agent's argument string:

```
{topic} [--hints {hints}] --since-start {since_window.start_date}
```

#### SKILL.md — Step 9 (Build Output Path and Write Digest)

Pass `since_window.label` when assembling digest content. The digest header gains a `Sources:` line (see digest-template.md change below).

#### SKILL.md — Step 10 (No-Content Fallback)

Update fallback message to:
```
No relevant content discovered for '{topic}' in the {since_window.label}.

Try widening the time window: /daily-digest "{topic}" --since 7
Or provide content manually: /daily-digest "{topic}" "[snippet 1]"
```

#### validate_input.py

Add `since_window` validation block (using `datetime.date.fromisoformat` — stdlib only):
- `start_date` parseable as ISO date
- `end_date` parseable as ISO date
- `start_date` ≤ `end_date`
- `start_date` ≤ today

#### invocation-contract.md

Add `since` and `since_window` field definitions, constraints, and resolution rules table. See [contracts/invocation-contract-diff.md](contracts/invocation-contract-diff.md) for the full diff.

#### digest-template.md

Add `Sources: {label}` line to header block:
```
Generated: {YYYY-MM-DD HH:MM}
Discovery: {status}
Sources: {since_window.label}
```

#### Discovery Agents (web, video, social)

Each agent's `## User Input` arguments line gains `--since-start <YYYY-MM-DD>`. The `## Outline` gains a filter instruction: exclude any source whose publication date is known to be before `--since-start`. Include undated sources with an `[undated]` note in the summary field.

## Complexity Tracking

> No Constitution Check violations — this table is empty.
