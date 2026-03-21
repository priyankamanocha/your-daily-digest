# Tasks: Skill Invocation Layer

**Input**: Design documents from `/specs/002-skill-invocation-layer/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks grouped by user story for independent implementation and testing.
**Tests**: Not requested — no test tasks included.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: No new infrastructure required. Project structure exists. Single setup task: establish the shared contract reference that all subsequent tasks point to.

- [x] T001 Create payload schema reference at `.claude/skills/daily-digest/resources/invocation-contract.md` — document field names (`topic`, `hints`, `snippets`), types, constraints (topic: ≤100 chars, alphanumeric/hyphens/underscores/spaces; hints: ≤10 items each ≤50 chars; snippets: no constraint), wire format (compact JSON), and note that validation is delegated to `validate_input.py`

**Checkpoint**: Contract reference exists and is the single source of truth for all field definitions.

---

## Phase 2: Foundational

No additional foundational phase required. T001 is the only prerequisite and is covered in Phase 1. All user story phases may begin after T001 completes.

---

## Phase 3: User Story 1 — Invoke Skill with a Single Canonical Command (Priority: P1) 🎯 MVP

**Goal**: A topic-only (or topic + hints) invocation produces a canonical JSON payload at the entrypoint; the orchestrator and all affected scripts read exclusively from that payload.

**Independent Test**: Invoke `/daily-digest "AI agents"` — confirm Step 0 produces `{"topic":"AI agents","hints":[],"snippets":[]}`, `validate_input.py` is called with that JSON string, `build_path.py` is called with that JSON string, and no step re-parses `$ARGUMENTS`.

### Implementation for User Story 1

- [x] T002 [US1] Add Step 0 (Entrypoint) to `.claude/skills/daily-digest/daily-digest.md` — insert as the first step in `## Outline`; describes how to parse `$ARGUMENTS` into `PAYLOAD_JSON`: extract `--hints <value>` (comma-split → hints list); treat all remaining non-flag tokens (everything except the `--hints` flag and its value) as a single space-joined topic string; set snippets to `[]`; serialize result as compact JSON string stored as `PAYLOAD_JSON`
- [x] T003 [P] [US1] Update `.claude/skills/daily-digest/scripts/validate_input.py` — change `__main__` to accept a single JSON string argument (`sys.argv[1]`); wrap `json.loads` in try/except — on `json.JSONDecodeError` return `{"valid": false, "error": "invalid payload format"}` with exit code 1; extract `topic`, `hints`, `snippets` fields; run existing topic and hints validation logic; pass `snippets` through without validation; on success return `{"valid": true, "topic": ..., "hints": ..., "snippets": ...}`; on field violation return `{"valid": false, "error": "..."}` with exit code 1
- [x] T004 [P] [US1] Update `.claude/skills/daily-digest/scripts/build_path.py` — change `__main__` to accept a single JSON string argument (`sys.argv[1]`); parse it with `json.loads`; extract `topic` field; pass to existing `build_path()` function unchanged
- [x] T005 [US1] Update Step 2 in `.claude/skills/daily-digest/daily-digest.md` — replace `python validate_input.py "$TOPIC" "$HINTS"` with `python validate_input.py "$PAYLOAD_JSON"` (depends on T002, T003)
- [x] T006 [US1] Update Step 9 in `.claude/skills/daily-digest/daily-digest.md` — replace `python build_path.py "$TOPIC"` with `python build_path.py "$PAYLOAD_JSON"` (depends on T002, T004)
- [x] T007 [US1] Update Steps 4–7 and Step 10 in `.claude/skills/daily-digest/daily-digest.md` — replace all references to raw `$TOPIC` and `$HINTS` variables with `payload.topic` and `payload.hints` extracted from the validated payload returned by Step 2; update the Step 10 no-content fallback message to reference `payload.topic` instead of the raw `{topic}` variable (depends on T002, T005)

**Checkpoint**: Topic-only and topic+hints invocations produce a canonical payload. Orchestrator reads all invocation data from the payload. `validate_input.py` and `build_path.py` accept JSON. No raw argument variables remain downstream of Step 0.

---

## Phase 4: User Story 2 — Invoke Skill with Optional Snippets for Test Mode (Priority: P2)

**Goal**: Snippet strings are parsed into the payload at the entrypoint; mode selection reads `payload.snippets` rather than scanning raw arguments.

**Independent Test**: Invoke `/daily-digest "AI agents" "Snippet one" "Snippet two"` — confirm payload contains `snippets: ["Snippet one", "Snippet two"]` and orchestrator routes to test/manual mode via `payload.snippets`, not by re-parsing `$ARGUMENTS`.

### Implementation for User Story 2

- [x] T008 [US2] Extend Step 0 in `.claude/skills/daily-digest/daily-digest.md` — add snippets parsing: after extracting topic and hints, collect all remaining quoted strings from `$ARGUMENTS` as the `snippets` list in `PAYLOAD_JSON`; discard any empty-string or whitespace-only entries before serializing (depends on T002)
- [x] T009 [US2] Update Step 3 in `.claude/skills/daily-digest/daily-digest.md` — replace raw-argument snippet detection with `payload.snippets` check: if `payload.snippets` is non-empty → test/manual mode; else → autonomous discovery (depends on T008)

**Checkpoint**: Snippets are a first-class field in the payload. Mode routing is driven entirely by `payload.snippets`. No argument scanning occurs after Step 0.

---

## Phase 5: User Story 3 — Invalid Invocation Produces a Clear Error at the Entrypoint (Priority: P3)

**Goal**: Any constraint violation (missing topic, topic too long, too many hints) is caught by `validate_input.py` at Step 2 and surfaces as a clear error message before any downstream step executes.

**Independent Test**: Invoke `/daily-digest` with no arguments — confirm error is returned immediately with a descriptive message; no discovery, file I/O, or script execution occurs beyond Step 2.

### Implementation for User Story 3

- [x] T010 [US3] Update Step 2 in `.claude/skills/daily-digest/daily-digest.md` — add explicit error-stop: after calling `validate_input.py "$PAYLOAD_JSON"`, check exit code; if non-zero, read the `error` field from the JSON output and stop execution with the message `Error: {error}` — do not proceed to Step 3 or any subsequent step (depends on T003, T005)

**Checkpoint**: All three invalid-input scenarios (missing topic, topic too long, too many hints) are caught at Step 2 and abort before any discovery or I/O step runs.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T011 [P] Update the `## User Input` section and argument format comment in `.claude/skills/daily-digest/daily-digest.md` — revise the format description to reflect that `$ARGUMENTS` is now parsed into a canonical payload at Step 0; update any inline documentation that references old variable names (`$TOPIC`, `$HINTS`) (depends on T002–T010)
- [x] T012 End-to-end smoke validation in `.claude/skills/daily-digest/daily-digest.md` snippets mode — invoke the skill with each scenario: (1) topic only, (2) topic + hints, (3) topic + snippets, (4) no topic; confirm correct payload, routing, and error behaviour for each (depends on T011)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 3 (US1)**: Depends on T001 — BLOCKS phases 4 and 5
- **Phase 4 (US2)**: Depends on T002 (T008 extends Step 0) — can start after T002 completes
- **Phase 5 (US3)**: Depends on T003 + T005 — can start after those complete
- **Phase 6 (Polish)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1)**: Starts after T001 — foundational payload; no dependency on US2 or US3
- **US2 (P2)**: T008 depends on T002 (extends same Step 0); T009 depends on T008
- **US3 (P3)**: T010 depends on T003 and T005 — can overlap with US2 work

### Within Each User Story

- T003 and T004 are parallelizable (different files, no shared dependency)
- T005 depends on T002 + T003; T006 depends on T002 + T004; T007 depends on T005
- T008 depends on T002; T009 depends on T008
- T010 depends on T003 + T005

### Parallel Opportunities

- T003 and T004 can run in parallel (validate_input.py and build_path.py are independent files)
- T008 and T010 can run in parallel once their prerequisites (T002/T005) are complete

---

## Parallel Example: User Story 1

```
# Once T001 and T002 are complete, launch T003 and T004 in parallel:
Task: "Update validate_input.py to accept JSON payload — scripts/validate_input.py"
Task: "Update build_path.py to accept JSON payload — scripts/build_path.py"

# Then T005 and T006 (which depend on T002+T003 and T002+T004 respectively):
Task: "Update Step 2 in daily-digest.md to call validate_input.py with $PAYLOAD_JSON"
Task: "Update Step 9 in daily-digest.md to call build_path.py with $PAYLOAD_JSON"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 (contract reference file)
2. Complete T002–T007 (US1: canonical payload + script migration)
3. **STOP and VALIDATE**: Invoke `/daily-digest "AI agents"` with snippets for testing; confirm payload produced, validate called with JSON, build_path called with JSON
4. Proceed to US2 and US3 once US1 is confirmed

### Incremental Delivery

1. T001 → contract established
2. T002–T007 (US1) → canonical payload, orchestrator unified, scripts migrated (MVP)
3. T008–T009 (US2) → snippets as first-class field, mode routing via payload
4. T010 (US3) → error handling centralised at entrypoint
5. T011–T012 (Polish) → documentation and smoke validation

---

## Notes

- No new Python files are introduced by this feature (Principle V)
- `check_runtime.py` and `write_digest.py` are not touched
- All parsing logic stays in the skill Outline prose (Principle II)
- Commit after each checkpoint (end of US1, US2, US3 phases)
