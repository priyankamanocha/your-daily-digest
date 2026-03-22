# Tasks: Source Allowlist / Blocklist

**Branch**: `008-source-allowlist-blocklist`
**Input**: Design documents from `/specs/008-source-allowlist-blocklist/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Not requested — manual verification via snippets mode and `/validate-digest`.

**Organization**: Tasks grouped by user story. Each story is independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

**Purpose**: Documentation and schema updates that unblock all implementation work.

- [x] T001 [P] Add `filter_action` field to SourceRecord in `.claude/skills/daily-digest/resources/manifest-schema.md` — values `"blocked" | "boosted" | "unaffected"`, type `enum or null`, note `null` for legacy manifests; blocked sources remain in `manifest.sources` but are absent from `manifest.candidates`
- [x] T002 [P] Create `sources.json.example` at repository root with example entries covering global block, topic allow, topic block (mirror the example in `specs/008-source-allowlist-blocklist/contracts/filter-config-schema.md`)
- [x] T011 [P] Fix Assumptions section in `specs/008-source-allowlist-blocklist/spec.md` — update the first assumption from "YAML file (`sources.yml`)" to "JSON file (`sources.json`)" to reflect the decision in `research.md` Decision 1 *(applied during /speckit.analyze remediation)*

---

## Phase 2: Foundation

**Purpose**: Core infrastructure that MUST be complete before any user story can be implemented. Both blocklist (US1) and allowlist (US2) depend on this script.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Create `.claude/skills/daily-digest/scripts/load_source_filters.py` — **I/O and validation only** (no matching logic per Constitution Principle II). Reads `sources.json` from cwd; parses JSON using `json` module (stdlib); validates structure per `specs/008-source-allowlist-blocklist/contracts/filter-config-schema.md`; writes result to stdout; exit codes: 0 = `{"filter_config": {…}}`, 1 = `{"error": "sources.json: <message>"}`, 2 = `{"filter_config": null}` (file not found). Validation checks: (1) file read — IOError → exit 2; (2) JSON parse — invalid → exit 1 with line number; (3) root is object; (4) `global` is object if present; (5) `global.allow`/`global.block` are arrays of non-empty strings if present; (6) `topics` is object if present; (7) each topic value is object with optional `allow`/`block` arrays of non-empty strings; (8) unknown top-level keys are silently ignored. **Do NOT implement `extract_host()` or `matches_entry()` here** — those belong in the `daily-digest.md` Outline (see T005/T006/T010).

**Checkpoint**: `load_source_filters.py` is runnable. `python .claude/skills/daily-digest/scripts/load_source_filters.py` with no `sources.json` exits 2. With a valid file exits 0 with filter config JSON.

---

## Phase 3: User Story 1 — Block a Noisy Source (Priority: P1) 🎯 MVP

**Goal**: Sources matching a blocklist entry are excluded from the digest before scoring. Topic-scoped rules only (global rules come in US4).

**Independent Test**: *(Requires autonomous mode — MCP tools must be available. Snippets have `url: null` and cannot be matched by domain filters.)* Create `sources.json` with `{"topics": {"AI safety": {"block": ["noisyblog.com"]}}}`. Run `/daily-digest AI safety` in autonomous mode. Inspect the sidecar manifest: verify any source from `noisyblog.com` has `filter_action = "blocked"` and does not appear in `manifest.candidates` or digest output. Then run `/daily-digest climate` and verify `noisyblog.com` sources, if found, have `filter_action = "unaffected"`. *For environments without MCP tools, defer to T008 which tests Step 1.5 config loading in snippets mode.*

### Implementation for User Story 1

- [x] T004 [US1] Add Step 1.5 to `.claude/skills/daily-digest/daily-digest.md` immediately after Step 1 (Preflight Checks): call `python .claude/skills/daily-digest/scripts/load_source_filters.py`; on exit 0 parse stdout JSON → store as `FILTER_CONFIG`; on exit 1 halt immediately with the `error` value from stdout; on exit 2 set `FILTER_CONFIG = null` and continue normally
- [x] T005 [US1] Add filter application block to `.claude/skills/daily-digest/daily-digest.md` between Steps 4 and 5 (after agents return results, before discovery status assessment): when `FILTER_CONFIG` is not null, resolve each source in `manifest_sources` against topic-level block rules only — case-insensitive match of `payload.topic` to `FILTER_CONFIG.topics` keys; for each source, call `matches_entry()` logic against the topic's `block` list; set `source.filter_action = "blocked"` and remove from active candidate pool if matched; set `source.filter_action = "unaffected"` otherwise. When `FILTER_CONFIG` is null, set all sources to `filter_action = "unaffected"`.

**Checkpoint**: User Story 1 fully functional. Blocklist entries under a topic exclude sources from that topic's digest only.

---

## Phase 4: User Story 2 — Pin a Trusted Source (Priority: P2)

**Goal**: Sources matching an allowlist entry are guaranteed inclusion in the digest if they have fresh content and meet the minimum quality floor (score ≥ 2 on ≥ 1 quality dimension). Topic-scoped rules only.

**Independent Test**: *(Requires autonomous mode — MCP tools must be available. Snippets have `url: null` and cannot be matched by domain filters.)* Create `sources.json` with `{"topics": {"machine learning": {"allow": ["trusteddomain.org"]}}}`. Run `/daily-digest machine learning` in autonomous mode. Inspect the sidecar manifest: verify any source from `trusteddomain.org` has `filter_action = "boosted"` and appears in digest output even if its quality score would normally exclude it from ranking. If `trusteddomain.org` produces no content in the discovery window, the test is inconclusive — try a domain known to publish frequently on the topic.

### Implementation for User Story 2

- [x] T006 [US2] Extend the filter application block (added in T005) in `.claude/skills/daily-digest/daily-digest.md` to also resolve topic-level allow rules: for sources not already set to `"blocked"`, check `FILTER_CONFIG.topics[payload.topic].allow`; if matched, set `source.filter_action = "boosted"` (leave `"unaffected"` for non-matched sources)
- [x] T007 [US2] Modify `.claude/skills/daily-digest/daily-digest.md` Step 8 (Apply Quality Rubric and Select Final Content): after normal quality scoring, guarantee inclusion of any source with `filter_action = "boosted"` that has content within the freshness window and scores ≥ 2 on at least 1 quality dimension; if adding a boosted source would exceed a section's maximum count, drop the lowest-ranking non-boosted candidate to make room. **Edge case — all candidates boosted**: if every candidate in a section is boosted and total would exceed the section maximum, cap at the section maximum in boost-insertion order (first-matched boosted source takes priority) — this preserves Constitution III count enforcement (1–3 insights, 2–4 anti-patterns, 1–3 actions, 3–5 resources) even when all sources are allowlisted

**Checkpoint**: User Story 2 fully functional. Allowlisted sources with fresh, minimally-qualifying content always appear in the digest.

---

## Phase 5: User Story 3 — Manage Filters via Config File (Priority: P3)

**Goal**: The config file is the sole interface — no flags required. Valid config applies automatically; syntax errors halt before discovery; absent file is graceful.

**Independent Test**: (a) Place a valid `sources.json` at repo root, invoke `/daily-digest <topic>` — verify filtering applies with no extra flags. (b) Place a malformed `sources.json` (e.g., trailing comma), invoke the skill — verify it halts before discovery with an error message identifying `sources.json`. (c) Delete `sources.json`, invoke the skill — verify digest runs normally with no filtering.

### Implementation for User Story 3

- [ ] T008 [US3] Manually verify the three config states against Step 1.5 behaviour added in T004 using snippets mode: (a) valid `sources.json` → filter applied, (b) malformed JSON → skill halts with `"sources.json: …"` error before any agent is spawned, (c) no `sources.json` → skill runs with all sources `filter_action = "unaffected"`. Document any discrepancies found and fix in `load_source_filters.py` or `daily-digest.md` as needed.
- [x] T009 [P] [US3] Update `CLAUDE.md` project structure section — add `load_source_filters.py` under `scripts/` and add `sources.json` (optional, user-managed) at repo root level

**Checkpoint**: User Story 3 fully functional. Config file is the only required user action.

---

## Phase 6: User Story 4 — Apply Global (Topic-Agnostic) Rules (Priority: P4)

**Goal**: Global allow/block entries apply to every digest run. Topic-level rules take precedence over global rules for the same source.

**Independent Test**: *(Requires autonomous mode — MCP tools must be available. Snippets have `url: null` and cannot be matched by domain filters.)* Create `sources.json` with `{"global": {"block": ["spamsite.com"]}, "topics": {"AI safety": {"allow": ["spamsite.com"]}}}`. Run `/daily-digest climate` in autonomous mode — verify any `spamsite.com` source has `filter_action = "blocked"` in the manifest (global rule). Run `/daily-digest AI safety` — verify any `spamsite.com` source has `filter_action = "boosted"` (topic allow overrides global block). *For config loading validation without MCP tools, use T008.*

### Implementation for User Story 4

- [x] T010 [US4] **Replace** (do not extend) the filter application block added by T005/T006 in `.claude/skills/daily-digest/daily-digest.md` with a complete 4-tier conflict resolution algorithm: (1) topic-level block → `"blocked"`, (2) topic-level allow → `"boosted"`, (3) global block → `"blocked"`, (4) global allow → `"boosted"`, (5) no match → `"unaffected"`. Apply in this exact precedence order; first match wins. Reads from both `FILTER_CONFIG.topics[payload.topic]` (case-insensitive key lookup) and `FILTER_CONFIG.global`. *This supersedes the topic-only logic from T005/T006 entirely — verify no duplicate filter evaluation remains after the replacement.*

**Checkpoint**: User Story 4 fully functional. Global rules apply across all topics; topic-level rules override global rules.

---

## Final Phase: Polish & Cross-Cutting Concerns

- [ ] T012 Run `/validate-digest` on a topic with no `sources.json` present to confirm baseline digest behaviour (discovery, scoring, output) is unchanged by the new filter step — explicitly verify that output structure, section counts, and manifest format are identical to pre-feature behavior when `FILTER_CONFIG` is null

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately; T001, T002, and T011 run in parallel
- **Phase 2 (Foundation)**: Can start alongside Phase 1; T003 is a prerequisite for Phases 3–6
- **Phase 3 (US1)**: Requires T003 (load_source_filters.py) complete
- **Phase 4 (US2)**: Requires T005 (filter application block) complete — extends it
- **Phase 5 (US3)**: Requires T004 (Step 1.5) complete; T009 is parallel
- **Phase 6 (US4)**: Requires T006 (topic allow filtering) complete — extends it
- **Polish**: Requires all user story phases complete

### User Story Dependencies

- **US1 (P1)**: Requires Phase 2 only — no dependency on other stories
- **US2 (P2)**: Requires US1 complete (extends filter application block)
- **US3 (P3)**: Requires US1 complete (validates Step 1.5 behaviour)
- **US4 (P4)**: Requires US2 complete (extends filter application to global scope)

### Within Each Phase

- Foundation before stories (T003 before T004)
- Step 1.5 before filter application (T004 before T005)
- Topic block before topic allow (T005 before T006)
- Filter application before Step 8 guarantee (T006 before T007)

---

## Parallel Opportunities

### Phase 1 (can run together)
```
Task: T001 — Add filter_action to manifest-schema.md
Task: T002 — Create sources.json.example
Task: T011 — Fix spec.md YAML→JSON assumption
```

### Phase 5 (T009 can run alongside T008)
```
Task: T008 — Verify three config states (sequential verification)
Task: T009 — Update CLAUDE.md project structure (independent edit)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001, T002, T011)
2. Complete Phase 2 (T003) — CRITICAL
3. Complete Phase 3 (T004, T005) — User Story 1
4. **STOP and VALIDATE**: Blocklisting works end-to-end
5. Proceed to US2, US3, US4 incrementally

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 → Blocklist MVP: users can immediately exclude noisy sources
3. Phase 4 → Add allowlist guarantee: users can pin trusted sources
4. Phase 5 → Config file UX validated and documented
5. Phase 6 → Global rules: users can apply cross-topic rules
6. Polish → Spec cleanup + baseline validation

---

## Notes

- [P] tasks involve different files with no shared dependencies — safe to run in parallel
- No automated tests requested; manual verification via snippets mode is the validation method
- `load_source_filters.py` must be I/O only (Constitution Principle II) — matching algorithm lives in the Outline of `daily-digest.md`
- All filter decisions (blocked/boosted/unaffected) flow through `manifest_sources` → manifest JSON automatically without changes to `write_manifest.py`
- Blocked sources remain in `manifest.sources` for auditability; absent from `manifest.candidates`
- Commit after each task group (e.g., after T003, after T005, after T007) to keep rollback granular
