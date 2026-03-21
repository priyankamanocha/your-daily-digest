# Tasks: Source Manifest Output

**Feature**: `003-source-manifest`
**Input**: Design documents from `specs/003-source-manifest/`
**Status**: Ready for implementation

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: New script and resource file — no dependencies, can start immediately.

- [ ] T001 [P] Create `write_manifest.py` in `.claude/skills/daily-digest/scripts/write_manifest.py` — accepts two CLI args: `<digest_path>` and `<manifest_json>`; derives manifest path by replacing `.md` with `.manifest.json`; creates directories as needed; writes JSON with 2-space indent; prints `✅ Manifest created: {manifest_path}` on success; exits 0/1
- [ ] T002 [P] Create `manifest-schema.md` in `.claude/skills/daily-digest/resources/manifest-schema.md` — document the full manifest JSON schema: top-level fields (schema_version, topic, generated_at, discovery_status, agents_succeeded, agents_failed, quality_warning), and the structure of sources[], deduplication_groups[], candidates[], and section_selections; include field types, allowed values, and a minimal example

**Checkpoint**: `write_manifest.py` runs standalone; `manifest-schema.md` is readable reference for orchestrator steps

---

## Phase 2: Foundational

**Purpose**: Permission entry that allows the skill to run `write_manifest.py` without interruption.

- [ ] T003 Add `"Bash(python .claude/skills/daily-digest/scripts/write_manifest.py *)"` to the `permissions.allow` list in `.claude/settings.json`

**Checkpoint**: `write_manifest.py` can be invoked by the skill without a user permission prompt

---

## Phase 3: User Story 1 — Inspect Source Credibility and Candidate Quality (Priority: P1) 🎯 MVP

**Goal**: Manifest contains every discovered source with its credibility score and every candidate insight with per-dimension quality scores and pass/fail result. Opening the manifest explains exactly why any insight was included or excluded.

**Independent Test**: Run `/daily-digest <topic>` autonomously → open the sidecar `.manifest.json` → verify sources have credibility_score and credibility_signal; candidates have quality_scores for all 4 dimensions and quality_pass boolean.

- [ ] T004 [US1] Modify `daily-digest.md` Step 4 — after receiving SOURCE: lines from each agent, build a source record for each line (fields: url, title, source_type, agent, author_or_handle, date, days_old, credibility_signal, summary) using the schema in `resources/manifest-schema.md`; accumulate as `manifest_sources`
- [ ] T005 [US1] Modify `daily-digest.md` Step 6 — for each source in `manifest_sources`, add `credibility_score` (0–3) and `freshness_score` (0–3) using `resources/credibility-rules.md` and `resources/freshness-policy.md`
- [ ] T006 [US1] Modify `daily-digest.md` Step 7 — for each deduplicated candidate, record a candidate entry (fields: title, primary_source_url, credibility_score, freshness_score, quality_scores {novelty, evidence, specificity, actionability each 0–2}, quality_pass, rejection_reason); accumulate as `manifest_candidates`
- [ ] T007 [US1] Modify `daily-digest.md` Step 9 — after calling `write_digest.py`, assemble the manifest payload from `manifest_sources`, `manifest_candidates`, and top-level fields (schema_version: "1.0", topic, generated_at matching digest timestamp, discovery_status, agents_succeeded, agents_failed, quality_warning); call `write_manifest.py "$FILE_PATH" "$MANIFEST_JSON"`

**Checkpoint**: Every `/daily-digest` run produces `digest-*.manifest.json` alongside `digest-*.md`; manifest lists all sources with scores and all candidates with quality pass/fail

---

## Phase 4: User Story 2 — Trace Deduplication Decisions (Priority: P2)

**Goal**: Manifest records every deduplication group — which sources were merged, which won, and why — so no source is silently dropped.

**Independent Test**: Run `/daily-digest` on a broad topic → read manifest `deduplication_groups` → verify merged sources appear in groups with winner and reason; verify rejected sources are not silently absent.

- [ ] T008 [US2] Modify `daily-digest.md` Step 7 — while deduplicating, record deduplication groups: for each semantic group of ≥2 equivalent candidates, create a group entry (fields: group_id e.g. "g001", candidate_urls[], winner_url, reason e.g. "credibility score 3 > 2" or "equal credibility; fresher source preferred"); accumulate as `manifest_dedup_groups`; add `manifest_dedup_groups` to the manifest payload assembled in T007

**Checkpoint**: Manifest `deduplication_groups` array accounts for every source URL involved in a merge; sources not merged are absent from this array (by design)

---

## Phase 5: User Story 3 — Confirm Final Section Selections (Priority: P3)

**Goal**: Manifest records exactly which items appear in each digest section and their source, plus the top-level discovery metadata. Every digest item is traceable in the manifest.

**Independent Test**: Compare manifest `section_selections` against digest markdown → every insight, anti-pattern, action, and resource in the digest has an exact counterpart in the manifest; `discovery_status` and `agents_failed` match the `Discovery:` header line in the digest.

- [ ] T009 [US3] Modify `daily-digest.md` Step 8 — as final content is selected for each section, record section_selections: key_insights, antipatterns, actions, and resources as lists of `{title, primary_source_url}`; add `section_selections` to manifest payload in T007; set `quality_warning: true` in payload if the quality warning was triggered
- [ ] T010 [US3] Modify `daily-digest.md` Step 5 — record `agents_succeeded`, `agents_failed`, and `discovery_status` from the assessment table; store for inclusion in manifest payload assembled in T007

**Checkpoint**: Manifest `section_selections` exactly mirrors digest content; `discovery_status` in manifest matches `Discovery:` line in digest header

---

## Phase 6: Polish & Edge Cases

**Purpose**: Ensure correct manifest behaviour in fallback and snippets modes.

- [ ] T011 Review `daily-digest.md` Step 10 (No-Content Fallback) — confirm `write_manifest.py` is NOT called in this step; add explicit comment in Step 10 noting "no manifest written in fallback case" to prevent accidental future addition
- [ ] T012 Update `daily-digest.md` Step 3 (Choose Mode) and Step 4 — in snippets mode, build synthetic source entries for each snippet (source_type: "snippet", agent: "manual", credibility_score: null, freshness_score: null, days_old: 0); set discovery_status: "manual" in manifest payload; no deduplication_groups needed (set to empty array)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — T001 and T002 can start in parallel immediately
- **Phase 2 (Foundational)**: Depends on T001 (file must exist before adding permission)
- **Phase 3 (US1)**: Depends on T001, T002, T003 — needs script, schema reference, and permission
- **Phase 4 (US2)**: Depends on Phase 3 completion — extends the manifest payload built in T007
- **Phase 5 (US3)**: Depends on Phase 3 completion — adds more fields to the same payload
- **Phase 6 (Polish)**: Depends on Phases 3–5 — verifies edge cases after core manifest is working

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 1+2; delivers core manifest
- **US2 (P2)**: Depends on US1 completion (adds to existing payload assembly in T007)
- **US3 (P3)**: Depends on US1 completion (adds to existing payload assembly in T007)
- US2 and US3 both modify `daily-digest.md` → implement sequentially, not in parallel

### Within Phase 3 (US1)

- T004 → T005 → T006 → T007 (sequential: each step feeds the next)
- T007 is the integration point — must be last in US1

### Parallel Opportunities

- **T001 + T002** (Phase 1): Different files — run in parallel
- **T008 and T009**: Both modify `daily-digest.md` — sequential only

---

## Parallel Example: Phase 1

```
# Launch both simultaneously:
Task T001: Create write_manifest.py in .claude/skills/daily-digest/scripts/write_manifest.py
Task T002: Create manifest-schema.md in .claude/skills/daily-digest/resources/manifest-schema.md
```

---

## Implementation Strategy

### MVP (Phase 1 + 2 + US1 only)

1. Complete Phase 1: Create `write_manifest.py` + `manifest-schema.md` (T001, T002 in parallel)
2. Complete Phase 2: Add permission (T003)
3. Complete Phase 3 (US1): Orchestrator collects sources + candidates + writes manifest (T004→T007)
4. **STOP and VALIDATE**: Run `/daily-digest <topic>` → verify manifest file created alongside digest with sources and candidates

### Full Delivery

5. Phase 4 (US2): Add deduplication groups (T008)
6. Phase 5 (US3): Add section selections + discovery metadata (T009, T010)
7. Phase 6 (Polish): Edge case handling for fallback and snippets (T011, T012)

---

## Notes

- All orchestrator changes (T004–T012) modify `.claude/skills/daily-digest/daily-digest.md` — implement sequentially
- `write_manifest.py` follows the same pattern as `write_digest.py`: thin I/O only, no business logic
- `manifest-schema.md` is the reference the orchestrator reads in Steps 4–9 to format records correctly
- The manifest payload is assembled incrementally across steps 4–9; T007 is the integration point where it is serialised and written
- No test tasks — spec does not request TDD; validation is by manual inspection of generated manifest files
