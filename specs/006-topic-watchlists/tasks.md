# Tasks: Topic Watchlists

**Input**: Design documents from `/specs/006-topic-watchlists/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the skill directory skeleton and update project-level config.

- [x] T001 [P] Create `.claude/skills/watchlist/` and `.claude/skills/watchlist/scripts/` directories
- [x] T002 [P] Add `.watchlist.json` to `.gitignore` (project root)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: I/O scripts that ALL user stories depend on. Must complete before any skill logic is written.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Implement `read_watchlist.py` in `.claude/skills/watchlist/scripts/read_watchlist.py` — reads `.watchlist.json` from CWD; if absent returns `{"ok": true, "topics": []}`; if unparseable returns `{"ok": false, "error": "..."}`. Output always to stdout as JSON. Exit code always 0.
- [x] T004 [P] Implement `find_digest.py` in `.claude/skills/watchlist/scripts/find_digest.py` — accepts `<topic_name> <YYYY-MM-DD>` as CLI args; derives slug using `re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:50]`; checks if `digests/{YYYY}/{MM}/digest-{date}-{slug}.md` exists; outputs `{"exists": true/false, "path": "..."/null}` to stdout as JSON. Exit code always 0. Python stdlib only.

**Checkpoint**: Foundation ready — skill implementation can begin.

---

## Phase 3: User Story 1 — Refresh All Watchlist Topics at Once (Priority: P1) 🎯 MVP

**Goal**: Single `/watchlist refresh` command generates fresh digests for all saved topics, skipping those already fresh today, and prints a per-topic run summary.

**Independent Test**: Manually create `.watchlist.json` with 2–3 topics. Run `/watchlist refresh`. Verify a new `digest-{today}-{slug}.md` file exists for each topic in `digests/{YYYY}/{MM}/`. Run again — verify all topics are skipped with "already fresh today" in the summary.

### Implementation for User Story 1

- [x] T005 [US1] Create `.claude/skills/watchlist/watchlist.md` — YAML frontmatter (`name: watchlist`, `description: Manage and refresh a personal topic watchlist`), `## User Input` section (`$ARGUMENTS`, format: `<subcommand> [<argument>]`), and `## Outline` with:
  - Step 0: Parse `$ARGUMENTS` — extract first whitespace-delimited token as `subcommand`, remainder as `argument`
  - Step 1: Route `refresh` → Step 2; `add` → Step 3; `remove` → Step 4; `list` → Step 5; `history` → Step 6; unknown → Step 7. **Stub Steps 6 and 7 with a comment only — do NOT implement them here** (Step 6 is implemented in T010, Step 7 in T011).
  - Step 2 (`refresh`): (a) **Preflight**: verify `digests/` directory exists and is writable — if not, print `Error: digests/ directory is not writable. Please create it or check permissions.` and stop. (b) Run `python .claude/skills/watchlist/scripts/read_watchlist.py`; parse JSON; if `ok=false` print error and stop; if `topics` is empty print "Your watchlist is empty. Add topics with: /watchlist add \<topic\>" and stop. (c) For each topic in order: run `python .claude/skills/watchlist/scripts/find_digest.py "{topic.name}" "{today}"` (today = `YYYY-MM-DD` format); if `exists=true` mark topic as `SKIPPED`; else invoke `daily-digest` skill for `{topic.name}` via Agent tool, capture file path from output, mark `REFRESHED` or `FAILED`. (d) After all topics print run summary: `✓ Refreshed: {name} → {path}` / `⟳ Skipped: {name} (already fresh today)` / `✗ Failed: {name} → {reason}`

**Checkpoint**: User Story 1 fully functional. Running `/watchlist refresh` (with a manually created `.watchlist.json`) generates and skips digests correctly.

---

## Phase 4: User Story 2 — Manage the Watchlist (Priority: P2)

**Goal**: Users can add, remove, and list watchlist topics via commands, without editing `.watchlist.json` directly.

**Independent Test**: Run `/watchlist add claude-code`. Run `/watchlist list` — verify `claude-code` appears. Run `/watchlist add claude-code` again — verify "already in your watchlist" notice, no duplicate. Run `/watchlist remove claude-code`. Run `/watchlist list` — verify it no longer appears.

### Implementation for User Story 2

- [x] T006 [US2] Implement `write_watchlist.py` in `.claude/skills/watchlist/scripts/write_watchlist.py` — accepts `<action> <topic_json>` CLI args where `action` is `"add"` or `"remove"` and `topic_json` is a JSON string `{"name": "...", "label": "...", "added_at": "..."}`. For `add`: read `.watchlist.json` (create if absent with `{"version": "1", "topics": []}`); check if topic already exists (case-insensitive `name` match); if exists output `{"ok": true, "action": "already_exists", "total": N}`; else append and write back, output `{"ok": true, "action": "added", "total": N}`. For `remove`: filter out matching topic; output `{"ok": true, "action": "removed"/"not_found", "total": N}`. On I/O error output `{"ok": false, "error": "..."}` and exit 1. Python stdlib only.
- [x] T007 [US2] Add Step 3 (`add`) to `watchlist.md` Outline — parse `argument` as topic name; if empty print `Usage: /watchlist add \<topic\>` and stop; normalize: `argument.lower().strip()`; validate name matches `[a-z0-9][a-z0-9 \-]*` (same constraints as `daily-digest` topic input) — if invalid print `Error: topic name may only contain letters, numbers, spaces, and hyphens.` and stop; build topic JSON `{"name": normalized_name, "label": argument.strip(), "added_at": "{today}"}` and run `python .claude/skills/watchlist/scripts/write_watchlist.py "add" "{topic_json}"`; parse result; if `action=added` print `Added "{name}" to your watchlist ({total} topics total).`; if `action=already_exists` print `"{name}" is already in your watchlist.`; if `ok=false` print error.
- [x] T008 [US2] Add Step 4 (`remove`) to `watchlist.md` Outline — parse `argument` as topic name; if empty print `Usage: /watchlist remove \<topic\>` and stop; run `python .claude/skills/watchlist/scripts/write_watchlist.py "remove" '{"name": "{argument.lower().strip()}"}'`; parse result; if `action=removed` print `Removed "{name}" from your watchlist ({total} topics remaining).`; if `action=not_found` print `"{name}" was not found in your watchlist.`; if `ok=false` print error.
- [x] T009 [US2] Add Step 5 (`list`) to `watchlist.md` Outline — run `read_watchlist.py`; if empty/absent print empty-watchlist notice; else for each topic: derive slug (`re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:50]`); use Glob tool to find all files matching `digests/*/*/digest-*-{slug}.md` across all year/month directories; sort results descending by filename; the first result is the most recent digest — extract its date from the filename (4th hyphen-delimited segment: `YYYY-MM-DD`); if no files found, last-digest = `(never)`; if date matches today append `(today)`; print table with columns `Topic`, `Label`, `Last digest`; header: `Your watchlist ({N} topics):`.

**Checkpoint**: User Stories 1 and 2 both independently functional.

---

## Phase 5: User Story 3 — View Watchlist Digest History (Priority: P3)

**Goal**: Users can see the 3 most recent digests for any watchlist topic, with dates and file paths.

**Independent Test**: Generate 2+ digests for one watchlist topic on different days (or manually create the files). Run `/watchlist history {topic}`. Verify the output lists up to 3 past digests with correct dates and paths. Run `/watchlist history {unknown-topic}` — verify a clear "no digests found" message.

### Implementation for User Story 3

- [x] T010 [US3] Add Step 6 (`history`) to `watchlist.md` Outline — parse `argument` as topic name; if empty print `Usage: /watchlist history \<topic\>` and stop; derive slug using same logic as `find_digest.py`; use Glob tool to find all files matching `digests/*/*/digest-*-{slug}.md`; sort results descending by filename (ISO date prefix ensures lexicographic = chronological); take first 3; if none found print `No digests found for "{name}".`; else print:
  ```
  Digest history for "{name}" (last {N}):

  1. {YYYY-MM-DD} → {file_path}
  2. {YYYY-MM-DD} → {file_path}
  3. {YYYY-MM-DD} → {file_path}
  ```

**Checkpoint**: All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Robustness, discoverability, and validation across all stories.

- [x] T011 [P] Add Step 7 (unknown subcommand handler) to `watchlist.md` Outline — if `subcommand` does not match any known value, print: `Unknown subcommand: "{subcommand}"` followed by the full usage block listing all 5 subcommands (`refresh`, `add`, `remove`, `list`, `history`) with one-line descriptions.
- [x] T012 [P] Update `CLAUDE.md` skill table to add a row for `watchlist`: location `.claude/skills/watchlist/watchlist.md`, description "Manage a personal topic watchlist and batch-refresh all saved topics with one command."
- [ ] T013 End-to-end verification using `specs/006-topic-watchlists/quickstart.md` — manually walk through the quickstart scenarios: add 3 topics, list them, run refresh, verify digest files exist, run refresh again and verify all skipped, remove one topic, verify list updated, run history for a refreshed topic.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately. T001 and T002 are fully parallel.
- **Foundational (Phase 2)**: Depends on Phase 1 completion. T003 and T004 are fully parallel.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion (T003, T004 must exist before T005 references them).
- **User Story 2 (Phase 4)**: Depends on Phase 2. T006 must precede T007 and T008. T007, T008, T009 must be sequential (all edit `watchlist.md`).
- **User Story 3 (Phase 5)**: Depends on Phase 2 and Phase 3 (T010 adds to `watchlist.md` created in T005).
- **Polish (Phase 6)**: Depends on all story phases. T011 and T012 are parallel. T013 runs last.

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (T003, T004). No dependency on US2 or US3.
- **US2 (P2)**: Depends on Foundational (T003, T004). T006 independent of US1. T007–T009 depend on T005 (add to skill created in US1).
- **US3 (P3)**: Depends on T005 (adds to `watchlist.md`). Independent of US2.

### Within Each User Story

- T003 and T004: fully parallel (different files, no shared state)
- T007, T008, T009: sequential (all append to `watchlist.md`)
- T011 and T012: parallel (different files)

---

## Parallel Opportunities

```
Phase 1:  T001 ‖ T002
Phase 2:  T003 ‖ T004
Phase 3:  T005 (sequential — depends on T003, T004)
Phase 4:  T006 → T007 → T008 → T009 (sequential — same file edits)
Phase 5:  T010 (sequential — extends T005's file)
Phase 6:  T011 ‖ T012 → T013
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T004)
3. Complete Phase 3: User Story 1 (T005)
4. **STOP and VALIDATE**: Use quickstart.md — create `.watchlist.json` manually, run `/watchlist refresh`, verify digest files
5. US1 is fully functional as a standalone feature

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 → Batch refresh works (MVP)
3. Phase 4 → Full watchlist management (no more manual JSON editing)
4. Phase 5 → History view
5. Phase 6 → Polish and CLAUDE.md update

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [Story] label maps each task to a specific user story for traceability
- `watchlist.md` is extended incrementally across Phases 3–5: T005 creates it, T007–T010 add to it, T011 adds the final fallback handler
- All scripts must be Python 3.8+ stdlib only (no third-party packages per Constitution Principle V)
- Commit after each phase checkpoint for clean rollback points
- US1 is fully testable before US2 is built — create `.watchlist.json` manually for initial testing
