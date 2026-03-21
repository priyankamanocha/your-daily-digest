# Implementation Plan: Skill Invocation Layer

**Branch**: `002-skill-invocation-layer` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-skill-invocation-layer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a unified invocation layer to the `daily-digest` skill: a new entrypoint section in the skill Outline that parses `$ARGUMENTS` into a canonical JSON payload (`topic`, `hints`, `snippets`). The payload is passed as a single JSON-serialized string argument to all affected helper scripts. `validate_input.py` and `build_path.py` are updated to accept the payload; a new `resources/invocation-contract.md` documents the schema. No new scripts are introduced.

## Technical Context

**Language/Version**: Python 3.8+, stdlib only (existing)
**Primary Dependencies**: `json`, `re`, `sys`, `datetime` — all stdlib (existing)
**Storage**: File system only (existing)
**Testing**: Manual invocation via snippets mode; `/validate-digest` for output validation
**Target Platform**: Claude Code session (cross-platform)
**Project Type**: Claude Code Skill (`.claude/skills/daily-digest/`)
**Performance Goals**: Entrypoint parsing adds negligible overhead; no latency targets
**Constraints**: Python stdlib only; backward-compatible argument syntax for callers; no new third-party packages
**Scale/Scope**: Single skill, 2 scripts in scope (`validate_input.py`, `build_path.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: feature delivered as `.claude/skills/<name>/<name>.md` | I | ✅ |
| Skill format: frontmatter + User Input + Outline present | I + II | ✅ |
| Script scope: scripts perform I/O only, no business logic | II | ✅ |
| Reference material in `resources/`, not inline | II | ✅ |
| Evidence requirement: all insights include direct quote | III | ✅ (not affected by this feature) |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges | III | ✅ (not affected by this feature) |
| Partial failure returns digest with status, not error | IV | ✅ (not affected by this feature) |
| Preflight checks verify hard deps before discovery | IV | ✅ (unchanged; still Step 1) |
| Python stdlib only; no third-party packages | V | ✅ |

No violations. No entries required in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/002-skill-invocation-layer/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── invocation-payload.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
.claude/skills/daily-digest/
├── daily-digest.md                      # Modified: new entrypoint section (Step 0)
│                                        #   all downstream steps reference payload fields
├── resources/
│   └── invocation-contract.md           # New: payload schema reference
└── scripts/
    ├── validate_input.py                # Modified: accept JSON payload string
    ├── build_path.py                    # Modified: extract topic from JSON payload
    ├── check_runtime.py                 # Unchanged (no topic/hints dependency)
    └── write_digest.py                  # Unchanged (no topic/hints dependency)
```

**Structure Decision**: Single-skill layout. All changes are contained within the existing `.claude/skills/daily-digest/` directory. No new directories are required.

## Phase 0: Research

### Decisions

**Decision 1: Entrypoint parsing mechanism**
- **Decision**: Parsing `$ARGUMENTS` into the payload is described as prose in the skill Outline (Step 0), not in a Python script
- **Rationale**: Claude Code executes Outline steps natively. Argument parsing is business logic per the constitution (Principle II) and belongs in the Outline, not in scripts. Adding a `parse_payload.py` would violate Principle V (new scripts only when an existing file cannot satisfy the need).
- **Alternatives considered**: New `parse_payload.py` script — rejected because it adds a file for logic that Claude can execute inline; `validate_input.py` absorbing parse + validate — rejected because conflating parsing with validation reduces testability and violates single-responsibility.

**Decision 2: JSON payload transport**
- **Decision**: Payload passed as a single JSON-serialized string argument: `python script.py "$PAYLOAD_JSON"`
- **Rationale**: Keeps scripts stateless; no temp files to clean up; works naturally with the existing bash-one-liner invocation pattern in the Outline.
- **Alternatives considered**: Temp file on disk — rejected (cleanup burden, not needed for in-session use); stdin pipe — rejected (more complex orchestrator syntax, no benefit here).

**Decision 3: No new parse script**
- **Decision**: Zero new Python files introduced by this feature
- **Rationale**: Principle V — minimum complexity. Two existing scripts need signature updates; a new script is not warranted.
- **Alternatives considered**: `parse_payload.py` — rejected (see Decision 1 rationale).

**Decision 4: `validate_input.py` repurposed, not retired**
- **Decision**: `validate_input.py` is updated to accept a JSON payload string, validate all three fields, and return a validated payload or error
- **Rationale**: Preserves the clean separation between skill prose (execution flow) and Python (I/O + validation). The script remains the single validation authority.
- **Alternatives considered**: Retire script, move validation inline to Outline — rejected because inline validation in prose is harder to test independently and harder to read.

## Phase 1: Design & Contracts

See `data-model.md` and `contracts/invocation-payload.md` for the canonical payload schema.

### Invocation Flow (post-change)

```
User types: /daily-digest "AI agents" --hints "channel1,channel2" "Snippet A"

Step 0 (Entrypoint — Outline prose):
  Parse $ARGUMENTS →
    payload = {
      "topic": "AI agents",
      "hints": ["channel1", "channel2"],
      "snippets": ["Snippet A"]
    }
  Serialize to JSON string: PAYLOAD_JSON

Step 1 (Preflight):
  python check_runtime.py          ← unchanged

Step 2 (Validate):
  python validate_input.py "$PAYLOAD_JSON"
  ← accepts JSON payload, validates fields, returns {valid, topic, hints, snippets} or error

Step 3 (Mode select):
  payload.snippets non-empty → test mode (skip to Step 8)
  payload.snippets empty     → autonomous discovery (Steps 4–7)

Steps 4–7 (Discovery):
  Agents receive topic and hints extracted from payload
  ← orchestrator extracts payload.topic, payload.hints from validated payload

Step 9 (Build path):
  python build_path.py "$PAYLOAD_JSON"
  ← extracts payload.topic, builds digest path
```

### Script Interface Changes

| Script | Before | After |
|---|---|---|
| `validate_input.py` | `python validate_input.py "$TOPIC" "$HINTS"` | `python validate_input.py "$PAYLOAD_JSON"` |
| `build_path.py` | `python build_path.py "$TOPIC"` | `python build_path.py "$PAYLOAD_JSON"` |
| `check_runtime.py` | `python check_runtime.py` | unchanged |
| `write_digest.py` | `python write_digest.py "$PATH" "$CONTENT"` | unchanged |

### Agent Context Update

Run after plan is complete:
```
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```
