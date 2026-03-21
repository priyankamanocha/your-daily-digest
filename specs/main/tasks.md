---
description: "Task list for SignalFlow Daily Intelligence Digest MVP implementation"
---

# Tasks: SignalFlow Daily Intelligence Digest

**Input**: Design documents from `/specs/main/`
**Branch**: `main`
**MVP Scope**: User Stories 1 & 2 (P1) - Core digest generation and insight extraction
**Phase 2+**: Autonomous discovery, learning, and persistence (post-MVP)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Each user story produces a complete, independently testable increment.

## Format: `[ID] [P?] [Story?] Description`

- **[ID]**: Task identifier (T001, T002, etc.) in execution order
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- File paths are exact and testable

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [x] T001 Create digests output directory structure: `digests/{YYYY}/{MM}/` in project root
- [x] T002 Initialize `.claude/commands/` directory if not present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Design skill interface specification: Input parsing (topic + text snippets), output file paths, error handling in `.claude/commands/daily-digest.md` header
- [x] T004 Define quality rubric validation logic (4 dimensions: novelty, evidence, specificity, actionability; scores 0-2; inclusion rule ≥2 on 3+ dimensions)
- [x] T005 Create markdown output generator template (structure for insights, anti-patterns, actions, resources sections per schema)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Generate Digest from Manual Content Input (Priority: P1) 🎯 MVP

**Goal**: Implement the `/daily-digest <topic> "[text snippet 1]" "[text snippet 2]" "[text snippet 3]"` command that accepts user-provided text snippets and produces a date-stamped markdown digest.

**Independent Test**: Run `/daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"` with sample content from `specs/main/benchmark.md`, verify output file is created at `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-claude-code.md` with correct structure (sections present, no errors).

### Implementation for User Story 1

- [x] T006 [US1] Implement command input parsing: Extract topic string and 3-5 text snippet arguments in `.claude/commands/daily-digest.md`
- [x] T007 [US1] Implement output file path generation: Build `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md` path with current date and topic slugification
- [x] T008 [US1] Implement markdown file writer: Generate and save digest file to computed path with generated content (depends on T011-T015 for full content generation)
- [x] T009 [US1] Add error handling: Handle missing arguments, invalid topic names, file system errors with clear error messages
- [x] T010 [US1] Test with benchmark inputs: Run skill with Sample Input Set 1 (Subagents) from `specs/main/benchmark.md`, verify file creation and basic structure

**Checkpoint**: User Story 1 complete - `/daily-digest` command works end-to-end with file output

---

## Phase 4: User Story 2 - Extract High-Quality Insights & Actions (Priority: P1)

**Goal**: Implement the core insight extraction and synthesis engine that evaluates provided content against the quality rubric and produces 1-3 high-quality insights, 2-4 anti-patterns, 1-3 actions, and 3-5 resources (or best-available with quality warning if low-signal).

**Independent Test**: Provide Sample Input Sets 1 & 2 from `specs/main/benchmark.md` to the skill, verify output insights match expected quality levels (high-quality insights extracted, low-quality items rejected, no padding), anti-patterns are accurate, actions are concrete and testable, and count targets are met for high-signal content (or quality warning present for low-signal).

### Implementation for User Story 2

- [x] T011 [US2] Implement insight extraction prompt: Design prompt that evaluates each snippet against novelty/evidence/specificity/actionability criteria, applies inclusion rule (≥2 on 3/4 dimensions), rejects weak candidates in `.claude/commands/daily-digest.md`
- [x] T012 [US2] Implement anti-pattern extraction: Generate 2-4 patterns from provided content with "why to avoid" explanation and evidence attribution in `.claude/commands/daily-digest.md` (depends on T011)
- [x] T013 [US2] Implement action generation: Create 1-3 concrete, testable actions (effort level, time estimate, numbered steps, measurable outcome) derived from insights in `.claude/commands/daily-digest.md` (depends on T011)
- [x] T014 [US2] Implement resource selection: Extract 3-5 supporting references with "why it matters" justification from provided content in `.claude/commands/daily-digest.md` (depends on T011)
- [x] T015 [US2] Implement low-signal handling: If fewer than target counts achieved, output best-available content and include quality warning (`⚠️ Low-signal content — insights below represent the best available material`) without padding (depends on T011-T014)
- [x] T016 [US2] Implement evidence citation: Ensure all insights include direct quotes, all anti-patterns cite sources, all resources reference provided content (depends on T011-T015)
- [x] T017 [US2] Test with benchmark Sample Input Set 1 (Subagents): Verify high-quality insights extracted (latency reduction claim, batching guidance), low-quality generic statements rejected using `specs/main/benchmark.md`
- [x] T018 [US2] Test with benchmark Sample Input Set 2 (MCP Tools): Verify insights about authentication elimination and tool availability, anti-patterns about dependency management and tool availability assumptions are accurately extracted using `specs/main/benchmark.md`
- [x] T019 [US2] Validate quality rubric consistency: Ensure all extracted insights score ≥2 on at least 3 of 4 dimensions per data-model.md rules

**Checkpoint**: User Stories 1 & 2 complete - MVP digest generation is fully functional with high-quality insight extraction

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories or the overall system

- [x] T020 Update `.claude/commands/daily-digest.md` with complete inline documentation and usage examples
- [x] T021 Run quickstart.md validation: Follow developer and user guides in `specs/main/quickstart.md` end-to-end to verify all documented workflows function correctly
- [x] T022 Final output validation: Run digest generation against all benchmark samples and verify output format matches `specs/main/contracts/digest-output-schema.md` exactly (1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources for high-signal; best-available with quality warning for low-signal)

**Checkpoint**: MVP is complete, documented, and ready for delivery

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User Stories 1 & 2 are logically independent (both P1)
  - **Implementation constraint**: Must proceed sequentially in `.claude/commands/daily-digest.md` (single file, avoid merge conflicts)
- **Polish (Phase 5)**: Depends on User Stories 1 & 2 completion

### Within User Stories

- **User Story 1**: Straightforward implementation → end-to-end testing with benchmark
- **User Story 2**: Iterative prompt refinement → quality validation with rubric
- Both stories depend on T003-T005 (Foundational) being complete

### Parallel Opportunities

- T001-T002 (Setup) can run in parallel
- T003-T005 (Foundational) can run in parallel
- Within file-based implementation: Most tasks edit `.claude/commands/daily-digest.md`; sequential implementation with clear dependency tracking reduces merge conflicts
- Validation tasks (T010, T017-T019) can run once their respective implementation tasks complete

---

## Sequential Implementation Path (After Foundational Completion)

Once Phase 2 (Foundational) is complete, implement in sequence to avoid merge conflicts in the single skill file:

```bash
# User Story 1: Input & File I/O
T006: Implement command input parsing
T007: Implement output file path generation
T009: Add error handling

# User Story 2: Content Extraction (single-file sequential)
T011: Implement insight extraction prompt
T012: Implement anti-pattern extraction
T013: Implement action generation
T014: Implement resource selection
T015: Implement low-signal handling
T016: Implement evidence citation

# Writer depends on all extraction (T011-T016)
T008: Implement markdown file writer

# Validation (can run after implementation)
T010: Test US1 with benchmark Sample Input Set 1
T017: Test US2 with benchmark Sample Input Set 1 (Subagents)
T018: Test US2 with benchmark Sample Input Set 2 (MCP Tools)
T019: Validate quality rubric consistency

# Polish
T020: Update documentation
T021: Run quickstart validation
T022: Final output validation
```

---

## Implementation Strategy

### MVP Delivery (Phase 1 + 2 + 3 + 4)

1. Complete Phase 1: Setup (directory structure) — ~15 min
2. Complete Phase 2: Foundational (specification + rubric + template) — ~30 min
3. Complete Phase 3: User Story 1 (command + file I/O) — ~1-2 hours
4. Complete Phase 4: User Story 2 (extraction + quality) — ~2-3 hours
5. **STOP and VALIDATE**: Test both stories with benchmark inputs
6. Deploy MVP

**Total MVP time**: ~4-6 hours (single developer)

### Quality Validation at Each Checkpoint

- **After US1**: Can invoke `/daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"` and file is created at correct path
- **After US2**: Output file contains 1-3 high-quality insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources (for high-signal content); or best-available with quality warning (for low-signal)
- **Final**: All benchmark test cases pass (expected high-quality insights extracted across Sample Input Sets 1 & 2, weak candidates rejected, no padding)

### Phase 2+ (Post-MVP)

After MVP validation:
- Phase 2: Autonomous discovery (WebSearch MCP, Twitter MCP, YouTube integration)
- Phase 3: Learning & personalization (feedback capture, source weighting)
- Phase 4+: Automation (scheduling, Notion export, team features)

---

## Notes

- Single skill file: All logic in `.claude/commands/daily-digest.md` (no external code, no TypeScript)
- Quality rubric: Enforced via prompt design (each extraction step evaluates candidates before inclusion)
- No database: All input ephemeral; only output files persist
- Benchmark-driven: Validate against exact sample inputs and expected outputs
- Independent testing: Each user story can be validated in isolation
- Fast iteration: Modify prompt → test in <5 min → iterate
