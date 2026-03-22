# Tasks: Digest Diffing

**Input**: Design documents from `/specs/007-digest-diffing/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[US1]**: Suppress Repeated Insights on Re-run
- **[US2]**: Graceful First Run (No Previous Digest)
- **[US3]**: Stale Previous Digest Treated as Fresh

---

## Phase 1: Setup

**Purpose**: Create policy resource — no other dependencies, can start immediately.

- [x] T001 Create `.claude/skills/daily-digest/resources/diffing-policy.md` with: staleness window (7 days), Jaccard threshold (0.5), and stopword list (`the, a, an, is, are, was, were, in, on, at, of, and, or, but, to, for, with, it, its, this, that, by, from`). Format as a readable markdown table matching the style of existing resource files (e.g., `freshness-policy.md`).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the diff script and extend the invocation layer. All user story phases depend on this.

**⚠️ CRITICAL**: No user story work can begin until T002 is complete.

- [x] T002 Create `.claude/skills/daily-digest/scripts/diff_digest.py`. Script accepts one CLI arg (`topic_slug`) and optional `--window-days N` (default 7). Logic: (1) derive slug from arg, (2) walk `digests/` recursively, collect files matching `digest-YYYY-MM-DD-{slug}.md`, (3) sort by embedded date descending, skip any file dated today, (4) take the first file within `window_days` of today (inclusive), (5) if none found, print `{"found": false}` and exit 0, (6) if found but file unreadable/empty, print `{"found": false}` and exit 0, (7) parse the four sections using `re.split(r'\n## ', content)` and extract titles per the patterns in `data-model.md` (### headings for Key Insights and Actions to Try; `**Title**:` bold pattern for Anti-patterns and Resources), (8) print JSON per the contract in `contracts/invocation-contract-delta.md` and exit 0. Any unexpected exception: print `{"found": false}` and exit 1.

- [x] T003 [P] Update `.claude/skills/daily-digest/scripts/validate_input.py` to detect and strip the `--no-diff` flag from the raw argument string before existing parsing. Add `"no_diff": true/false` to the validated output JSON. No validation error is raised for this flag — its presence sets `no_diff = true`, its absence sets `no_diff = false`.

- [x] T004 [P] Update `.claude/skills/daily-digest/resources/invocation-contract.md` to document: (1) `no_diff` field in the Payload Schema JSON block, (2) its row in the Field Definitions table (type: bool, required: No, default: false, description: skip diffing), (3) parsing rule step 4 in the Parsing Rules section (`--no-diff` → `no_diff = true`). Match the existing formatting style of the file.

**Checkpoint**: `diff_digest.py` is independently runnable. Running `python diff_digest.py some-slug` against the `digests/` directory returns well-formed JSON. `validate_input.py` passes `--no-diff` through correctly.

---

## Phase 3: User Stories 1 & 2 — Core Skill Integration (Priority: P1) 🎯 MVP

**Goal**: Wire `diff_digest.py` into the daily-digest skill so that (US1) repeat items are suppressed and a footer note appears, and (US2) the skill runs without error when no baseline exists.

**Independent Test (US1)**: Run `/daily-digest <topic> "Snippet A" "Snippet B"` twice with the same snippets and same source. Second run's insight should be suppressed; footer note shows "1 item suppressed as already covered in digest from YYYY-MM-DD".

**Independent Test (US2)**: Delete or rename any existing digest for the topic, then run `/daily-digest <topic> "Snippet A"`. Digest generates normally with no diff-related errors or warnings and no footer note.

- [x] T005 [US1] [US2] Patch `## Outline → Step 0` in `.claude/skills/daily-digest/daily-digest.md` to parse `--no-diff` alongside the existing `--hints` extraction. After hints extraction and before snippet extraction: if `--no-diff` is present as a standalone token, set `no_diff = true` and remove it from the argument string; otherwise `no_diff = false`. Add `"no_diff": <bool>` to `PAYLOAD_JSON`. Update the two `PAYLOAD_JSON` examples in Step 0 to include `"no_diff": false`.

- [x] T006 [US1] [US2] Add new `### 3.5. Diff Lookup` step to `.claude/skills/daily-digest/daily-digest.md` immediately after Step 3 (Choose Mode). Content: "If `payload.no_diff == true`, set `diff_baseline = {"found": false}` and skip to Step 4. Otherwise, derive the topic slug from `payload.topic` using the same logic as `build_path.py` (lowercase, replace spaces with hyphens, strip non-alphanumeric except hyphens, truncate to 50 chars) to produce `<derived_slug>`, then run: `python .claude/skills/daily-digest/scripts/diff_digest.py <derived_slug>`. Parse the JSON output into `diff_baseline`. If the script exits with code 1 or output is unparseable, set `diff_baseline = {"found": false}` and continue."

- [x] T007 [US1] Patch `### 8. Apply Quality Rubric and Select Final Content` in `.claude/skills/daily-digest/daily-digest.md`. After final content is selected for each of the four sections, apply the repeat filter: for each selected item, if `diff_baseline.found == true`, compute Jaccard similarity between the item's title tokens and each same-section title in `diff_baseline.sections` (tokenise: lowercase, strip punctuation, remove stopwords from `diffing-policy.md`). If Jaccard ≥ 0.5 AND the item's source attribution matches a baseline source (case-insensitive), classify item as a repeat and remove it from the section. Accumulate: `suppressed_count` (int), `suppressed_baseline_date` = `diff_baseline.baseline_date`. After filtering, if any section falls below its minimum count, apply the low-signal warning per the existing policy.

- [x] T008 [US1] Patch `### 9. Build Output Path and Write Digest` in `.claude/skills/daily-digest/daily-digest.md`. After assembling the digest markdown and before calling `write_digest.py`: if `suppressed_count > 0`, append a footer line to the markdown content: `\n_N item(s) suppressed as already covered in digest from YYYY-MM-DD._` where N = `suppressed_count` and YYYY-MM-DD = `suppressed_baseline_date`. If `suppressed_count == 0`, append nothing.

- [x] T009 [US2] Review and correct if needed the graceful first-run path in `.claude/skills/daily-digest/daily-digest.md` Steps 3.5, 8, and 9: (a) confirm that when `diff_baseline.found == false`, no Jaccard comparisons occur, `suppressed_count = 0`, and no footer note is appended; (b) confirm the digest output for a first-run is byte-for-byte identical to what would be produced with `--no-diff`. If any branch in the modified skill outline would produce a diff-related warning or altered output on first run, edit `daily-digest.md` to correct it.

**Checkpoint**: User Stories 1 and 2 are fully functional. A second run of the same snippet produces a suppressed digest with a footer note. A brand-new topic produces an unmodified digest.

---

## Phase 4: User Story 3 — Stale Digest Handling (Priority: P2)

**Goal**: Confirm that the 7-day staleness window in `diff_digest.py` (implemented in Phase 2) correctly makes stale baselines invisible to the diff lookup, so the skill behaves identically to a first run.

**Independent Test**: Temporarily rename an existing digest file to have a date 10 days ago (e.g., `digest-2026-03-12-<slug>.md`), run the skill, confirm all items pass through and no footer note appears.

- [x] T010 [US3] Trace the staleness boundary logic in `diff_digest.py` (T002): confirm the date comparison uses `(today - baseline_date).days <= window_days` (inclusive, so a 7-day-old file is still in-window). If the implementation uses strict `<` instead of `<=`, correct it to `<=` per the spec (boundary inclusive — FR from User Story 3 acceptance scenario 2).

- [x] T011 [US3] Verify the malformed-file edge case in `diff_digest.py` (T002): read the file-read/parse block and confirm that any exception during file open, `re.split`, or title extraction causes the function to return `{"found": false}` rather than propagating an error. If a bare `except` is missing or too narrow, extend it to cover `IOError`, `OSError`, and any regex/parsing failure.

**Checkpoint**: User Story 3 is validated. Stale baselines are silently ignored; today's run produces a full unfiltered digest with no footer note.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and documentation tidy-up.

- [x] T012 [P] Run the two-run snippets test from `quickstart.md` (Scenario 1): invoke `/daily-digest test-topic "Anthropic released feature X. Quote: 'we built X for users'"` twice. Verify the second run's digest: (a) the Key Insights section omits the repeated insight, (b) the footer note reads "1 item suppressed as already covered in digest from YYYY-MM-DD", (c) the digest file is valid markdown. Fix any discrepancy found.

- [x] T013 [P] Run the opt-out test from `quickstart.md` (Scenario 3): invoke `/daily-digest test-topic --no-diff "Anthropic released feature X. Quote: 'we built X for users'"` after a baseline exists. Verify the insight is NOT suppressed and no footer note appears. Fix any discrepancy found.

- [x] T014 Run `/validate-digest` on a digest produced by the modified skill. Confirm the digest passes all existing validation checks (format, counts, evidence quotes). If the footer note causes a format validation failure, update `.claude/skills/daily-digest/resources/digest-template.md` to document the optional footer line (after the existing `---` separator line), matching the existing template style.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 (T001 needed by T002 for policy constants).
  - T002 is the single blocking task: US1/US2/US3 integration cannot begin until it completes.
  - T003 and T004 can run in parallel with each other and with T002 (different files).
- **Phase 3 (US1+US2)**: Depends on T002 (diff_digest.py), T003 (validate_input.py), T004 (contract doc).
  - T005 → T006 → T007 → T008 must run in order (sequential patches to the same file).
  - T009 can run after T006–T008 are complete.
- **Phase 4 (US3)**: T010 and T011 can run in parallel after T002 is verified (they review T002 logic).
- **Phase 5 (Polish)**: Depends on all prior phases. T012 and T013 can run in parallel.

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 completion → T005 → T006 → T007 → T008
- **US2 (P1)**: Depends on Phase 2 completion → T005 → T006 → T009 (shares implementation with US1)
- **US3 (P2)**: Depends on T002 (Phase 2) → T010, T011 independently

### Parallel Opportunities

- T003 and T004 (Phase 2) can run in parallel — different files, no inter-dependency.
- T010 and T011 (Phase 4) can run in parallel — both review T002 in isolation.
- T012 and T013 (Phase 5) can run in parallel — independent invocation tests.

---

## Parallel Example: Phase 2

```
# These three tasks can overlap:
T002  diff_digest.py implementation        (.claude/skills/daily-digest/scripts/diff_digest.py)
T003  validate_input.py --no-diff patch    (.claude/skills/daily-digest/scripts/validate_input.py)
T004  invocation-contract.md update        (.claude/skills/daily-digest/resources/invocation-contract.md)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: T001
2. Complete Phase 2: T002 (blocking), T003 + T004 in parallel
3. Complete Phase 3: T005 → T006 → T007 → T008 → T009
4. **STOP and VALIDATE**: Run quickstart.md Scenario 1 and Scenario 2 manually
5. US1 and US2 are live — users get repeat suppression and graceful first-run handling

### Incremental Delivery

1. Phase 1 + Phase 2 → `diff_digest.py` works standalone (testable with `python diff_digest.py <slug>`)
2. Phase 3 → Skill produces filtered digests with footer notes (MVP complete)
3. Phase 4 → Staleness edge case confirmed; US3 validated
4. Phase 5 → End-to-end validated; format checked

---

## Notes

- [P] tasks touch different files — safe to run simultaneously
- T005–T008 are sequential patches to `daily-digest.md` — do not parallelize
- T009 and T010/T011 are verification tasks, not new code — they review and fix existing implementations
- Commit after T002 (standalone script complete) and again after T008 (skill integration complete) as natural checkpoints
- The `--no-diff` flag is the escape hatch for all testing — use it to verify baseline behaviour is unchanged
