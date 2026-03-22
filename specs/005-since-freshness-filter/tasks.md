# Tasks: Since Freshness Filter

**Input**: Design documents from `/specs/005-since-freshness-filter/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. No new files are created — all tasks modify existing files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Confirm change scope — no new files or project structure needed for this feature.

- [x] T001 Read and confirm understanding of all 7 files to be modified: `.claude/skills/daily-digest/SKILL.md`, `scripts/validate_input.py`, `resources/invocation-contract.md`, `resources/digest-template.md`, `agents/web-discovery-agent.md`, `agents/video-discovery-agent.md`, `agents/social-discovery-agent.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update the contract definition, output template, and validation script — required before any user story is testable.

**⚠️ CRITICAL**: All three user stories depend on these changes being complete.

- [x] T002 Update `.claude/skills/daily-digest/resources/invocation-contract.md` — add `since` (string, optional, default `"1"`) and `since_window` (object with `start_date`, `end_date`, `label`) to the Payload Schema, Field Definitions table, Field Constraints table, and Parsing Rules section; add `--since <value>` to the Arguments format line; document that `--since` is parsed before `--hints`
- [x] T003 [P] Update `.claude/skills/daily-digest/resources/digest-template.md` — add `Sources: {since_window.label}` line to the header block immediately below the `Discovery:` line; update Field Rules section to document the new `Sources:` field
- [x] T004 [P] Update `.claude/skills/daily-digest/scripts/validate_input.py` — add `since_window` validation: (1) check `start_date` is a valid `YYYY-MM-DD` string using `datetime.date.fromisoformat` (stdlib); (2) check `end_date` is a valid `YYYY-MM-DD` string; (3) check `start_date` ≤ `end_date`; (4) check `start_date` ≤ today; return appropriate error strings for each failure; default `since_window` to `{"start_date": today-1, "end_date": today, "label": "last 24 hours"}` if field is absent from payload

**Checkpoint**: Contract, template, and validator updated — user story implementation can begin.

---

## Phase 3: User Story 1 — Default daily freshness (Priority: P1) 🎯 MVP

**Goal**: `/daily-digest claude-code` with no `--since` flag automatically applies a 24-hour discovery window. Agents filter sources; digest header shows `Sources: last 24 hours`.

**Independent Test**: Run `/daily-digest claude-code` (no flags). Verify: (1) digest header contains `Sources: last 24 hours`; (2) discovered sources are all dated within the last 24 hours or marked `[undated]`; (3) no error is raised.

- [x] T005 [US1] Update `SKILL.md` Step 0 (Parse Invocation) — add `--since` extraction: if `--since <value>` is present, extract value as `since_raw` and remove flag+value from argument string; if absent, set `since_raw = "1"`; resolve `since_raw = "1"` to `since_window = {"start_date": today-1day, "end_date": today, "label": "last 24 hours"}`; add `"since": since_raw` and `"since_window": {...}` to `PAYLOAD_JSON`; update the example payload blocks in the step to include the new fields
- [x] T006 [P] [US1] Update `.claude/skills/daily-digest/agents/web-discovery-agent.md` — add `--since-start <YYYY-MM-DD>` to the `## User Input` arguments line; add a filter step in `## Outline` after Step 3 (Fetch and Extract): exclude any source whose publication date is known to be before `--since-start`; include sources with no detectable date with `[undated]` appended to the summary field
- [x] T007 [P] [US1] Update `.claude/skills/daily-digest/agents/video-discovery-agent.md` — same changes as T006: add `--since-start` to User Input, add date filter step, include undated sources with `[undated]` flag
- [x] T008 [P] [US1] Update `.claude/skills/daily-digest/agents/social-discovery-agent.md` — same changes as T006: add `--since-start` to User Input, add date filter step, include undated sources with `[undated]` flag
- [x] T009 [US1] Update `SKILL.md` Step 4 (Spawn Discovery Agents) — append `--since-start {since_window.start_date}` to each agent's argument string; update all three agent invocation lines to include the new flag (depends on T005, T006, T007, T008)
- [x] T010 [US1] Update `SKILL.md` Step 9 (Build Output Path and Write Digest) — include `since_window.label` when assembling the digest header; the header must now include a `Sources: {since_window.label}` line below `Discovery:` per the updated `digest-template.md` (depends on T005)
- [x] T011 [US1] Update `SKILL.md` Step 10 (No-Content Fallback) — replace current fallback message with: `No relevant content discovered for '{payload.topic}' in the {since_window.label}.\n\nTry widening the time window: /daily-digest "{payload.topic}" --since 7\nOr provide content manually: /daily-digest "{payload.topic}" "[snippet 1]"` (depends on T005)

**Checkpoint**: User Story 1 fully functional. `/daily-digest <topic>` applies 24h window end-to-end.

---

## Phase 4: User Story 2 — Numeric day override (Priority: P2)

**Goal**: `--since 7` (or any positive integer N) expands discovery to the last N days. Invalid numeric inputs (`--since 0`, `--since -3`, empty `--since`) halt with a clear error — no silent fallback.

**Independent Test**: (1) Run `/daily-digest claude-code --since 7` — verify `Sources: last 7 days` in header and sources ≤ 7 days old; (2) Run `/daily-digest claude-code --since 0` — verify error message and no discovery run.

- [x] T012 [US2] Extend `SKILL.md` Step 0 — add numeric N resolution: if `since_raw` is a string of digits, parse as integer; if N = 1, window is already handled (24 hours); if N > 1, set `start_date = today - N days`, `label = "last N days"`; if `since_raw` is `""` (empty string), halt immediately with: `"--since requires a value. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."` and stop — do not fall back to default (depends on T005)
- [x] T013 [US2] Extend `SKILL.md` Step 0 — add numeric guard: if numeric `since_raw` parses to 0 or a negative number, halt with: `"since={N} is not valid — minimum value is 1."` and stop; if `since_raw` looks like a number but fails to parse as integer, treat as unrecognised expression and halt with the unrecognised-expression error (depends on T012)

**Checkpoint**: User Stories 1 and 2 both work. Numeric `--since` fully functional with correct error handling.

---

## Phase 5: User Story 3 — Natural language date expressions (Priority: P3)

**Goal**: `--since yesterday`, `--since "last month"`, and `--since "feb 2026"` resolve to the correct date windows. Unrecognised expressions halt with a clear error including examples of valid formats.

**Independent Test**: (1) `--since yesterday` → `Sources: yesterday (YYYY-MM-DD)`; (2) `--since "last month"` → `Sources: last 30 days`; (3) `--since "feb 2026"` → `Sources: 1 Feb – 28 Feb 2026`; (4) `--since "next tuesday"` → error with examples shown.

- [x] T014 [US3] Extend `SKILL.md` Step 0 — add natural language resolution for all three supported expressions: (1) `"yesterday"` → `start_date = today - 1 day`, `end_date = today - 1 day`, `label = "yesterday (YYYY-MM-DD)"`; (2) `"last month"` → `start_date = today - 30 days`, `end_date = today`, `label = "last 30 days"`; (3) `"<month> <year>"` (e.g. `"feb 2026"`, case-insensitive) → `start_date = first day of that month`, `end_date = last day of that month`, `label = "1 Feb – 28 Feb 2026"`; (4) any other non-numeric, non-empty value → halt with: `"Could not interpret '--since {value}'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."` (depends on T012, T013)

**Checkpoint**: All three user stories fully functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification and documentation consistency.

- [x] T015 [P] Update `SKILL.md` User Input section — add `--since` to the Arguments format line: `<topic> [--hints <hint1,hint2>] [--since <value>] ["snippet1" "snippet2" ...]`; add a `--since` row to the argument description list with: `optional; number of days or date expression (default: 1 = last 24 hours)`
- [x] T016 Verify end-to-end consistency — confirm that `invocation-contract.md`, `SKILL.md` User Input, `SKILL.md` Step 0, the three agent files, `validate_input.py`, and `digest-template.md` are mutually consistent: same field names, same default, same error messages match spec FR-003/FR-007; run `/daily-digest claude-code` and `/daily-digest claude-code --since 3` to confirm `Sources:` line appears correctly in both outputs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — can start once foundational complete
- **US2 (Phase 4)**: Depends on Phase 3 (T005) — extends Step 0 already added in US1
- **US3 (Phase 5)**: Depends on Phase 4 (T012, T013) — extends Step 0 further
- **Polish (Phase 6)**: Depends on Phase 5

### User Story Dependencies

- **US1**: Establishes the core Step 0 parsing structure and agent pass-through — all other stories build on this
- **US2**: Extends Step 0 for numeric N; depends on US1 (shared SKILL.md Step 0)
- **US3**: Extends Step 0 for natural language; depends on US2 (shares the same Step 0 branching logic)

### Within Each Story

- Agent tasks (T006, T007, T008) are fully parallel — different files, no shared state
- SKILL.md tasks within a story must be sequential (single file, ordered steps)
- T009 (Step 4 update) depends on T005 (Step 0 adds `since_window`) and T006–T008 (agents updated to accept `--since-start`)

---

## Parallel Opportunities

```
Phase 2 — run in parallel:
  T002  Update invocation-contract.md
  T003  Update digest-template.md
  T004  Update validate_input.py

Phase 3 — run T006, T007, T008 in parallel (different agent files):
  T006  Update web-discovery-agent.md
  T007  Update video-discovery-agent.md
  T008  Update social-discovery-agent.md
  → then T009 (SKILL.md Step 4) once all three agents are updated
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002–T004)
3. Complete Phase 3: User Story 1 (T005–T011)
4. **STOP and VALIDATE**: Run `/daily-digest claude-code` — confirm `Sources: last 24 hours` in output
5. Proceed to US2 only if MVP is validated

### Incremental Delivery

1. Phases 1–3 → 24-hour default works end-to-end (MVP)
2. Phase 4 → numeric `--since N` works with error handling
3. Phase 5 → natural language expressions work
4. Phase 6 → polish and consistency verification

---

## Notes

- All tasks modify existing files — no `mkdir`, no new file creation
- SKILL.md Step 0 is touched by T005 (US1), T012–T013 (US2), and T014 (US3) — implement in order to avoid conflicts
- The three agent files (T006–T008) are identical in change pattern — implement in parallel
- `validate_input.py` change (T004) is foundational — it validates the resolved `since_window`, which depends on Step 0 being correct; test them together after Phase 3
