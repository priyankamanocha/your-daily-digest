# GitHub Issues to Create

Create these issues in: https://github.com/priyankamanocha/signalflow/issues

All tasks are marked as **COMPLETED** ✅

---

## Phase 1: Setup (Shared Infrastructure)

### Issue 1: T001 - Create digests output directory structure
**Status**: ✅ Completed
**Description**: Create `digests/{YYYY}/{MM}/` directory structure in project root for storing generated digest files.

### Issue 2: T002 - Initialize .claude/commands/ directory
**Status**: ✅ Completed
**Description**: Initialize `.claude/commands/` directory if not present, ready for skill files.

---

## Phase 2: Foundational (Blocking Prerequisites)

### Issue 3: T003 - Design skill interface specification
**Status**: ✅ Completed
**Description**: Design `/daily-digest` skill interface specification including:
- Input parsing (topic + text snippets)
- Output file paths
- Error handling

**Files**: `.claude/commands/daily-digest.md`

### Issue 4: T004 - Define quality rubric validation logic
**Status**: ✅ Completed
**Description**: Define quality rubric for insight extraction:
- 4 dimensions: novelty, evidence, specificity, actionability
- Scoring: 0-2 per dimension
- Inclusion rule: ≥2 on ≥3 dimensions

**Files**: `specs/main/data-model.md`

### Issue 5: T005 - Create markdown output generator template
**Status**: ✅ Completed
**Description**: Create markdown output template structure for:
- Key Insights (1-3)
- Anti-patterns (2-4)
- Actions to Try (1-3)
- Resources (3-5)

**Files**: `specs/main/contracts/digest-output-schema.md`

---

## Phase 3: User Story 1 - Generate Digest from Manual Content Input

### Issue 6: T006 [US1] - Implement command input parsing
**Status**: ✅ Completed
**Description**: Extract topic string and 3-5 text snippet arguments for `/daily-digest` command

**Files**: `.claude/commands/daily-digest.md`

### Issue 7: T007 [US1] - Implement output file path generation
**Status**: ✅ Completed
**Description**: Build file path: `digests/{YYYY}/{MM}/digest-{YYYY}-{MM}-{DD}-{topic-slug}.md`

**Files**: `.claude/commands/daily-digest.md`

### Issue 8: T008 [US1] - Implement markdown file writer
**Status**: ✅ Completed
**Description**: Generate and save digest file to computed path with all required sections

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011-T015

### Issue 9: T009 [US1] - Add error handling
**Status**: ✅ Completed
**Description**: Handle missing arguments, invalid topic names, file system errors with clear messages

**Files**: `.claude/commands/daily-digest.md`

### Issue 10: T010 [US1] - Test with benchmark inputs (Sample Input Set 1)
**Status**: ✅ Completed
**Description**: Run `/daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"` with Subagents pattern from `specs/main/benchmark.md`

**Verification**: File created at `digests/{YYYY}/{MM}/digest-{YYYY}-{MM}-{DD}-claude-code.md` with correct structure

---

## Phase 4: User Story 2 - Extract High-Quality Insights & Actions

### Issue 11: T011 [US2] - Implement insight extraction prompt
**Status**: ✅ Completed
**Description**: Design prompt that evaluates each snippet against 4 dimensions and applies inclusion rule (≥2 on 3/4)

**Files**: `.claude/commands/daily-digest.md`

### Issue 12: T012 [US2] - Implement anti-pattern extraction
**Status**: ✅ Completed
**Description**: Generate 2-4 anti-patterns with "why to avoid" explanation and evidence attribution

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011

### Issue 13: T013 [US2] - Implement action generation
**Status**: ✅ Completed
**Description**: Create 1-3 concrete, testable actions with effort, time, steps, expected outcome

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011

### Issue 14: T014 [US2] - Implement resource selection
**Status**: ✅ Completed
**Description**: Extract 3-5 supporting references with "why it matters" justification from provided content

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011

### Issue 15: T015 [US2] - Implement low-signal handling
**Status**: ✅ Completed
**Description**: Output best-available content with quality warning if below target counts

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011-T014

### Issue 16: T016 [US2] - Implement evidence citation
**Status**: ✅ Completed
**Description**: Ensure all insights have direct quotes, anti-patterns cite sources, resources reference content

**Files**: `.claude/commands/daily-digest.md`
**Depends on**: T011-T015

### Issue 17: T017 [US2] - Test with Sample Input Set 1 (Subagents)
**Status**: ✅ Completed
**Description**: Verify high-quality insights extracted (latency reduction, batching guidance), low-quality items rejected

**Verification**: Output validates against `specs/main/benchmark.md` expected outputs

### Issue 18: T018 [US2] - Test with Sample Input Set 2 (MCP Tools)
**Status**: ✅ Completed
**Description**: Verify insights about authentication elimination, tool availability, and anti-patterns accurately extracted

**Verification**: Output validates against `specs/main/benchmark.md` expected outputs

### Issue 19: T019 [US2] - Validate quality rubric consistency
**Status**: ✅ Completed
**Description**: Ensure all extracted insights score ≥2 on at least 3 of 4 dimensions per `specs/main/data-model.md`

---

## Phase 5: Polish & Cross-Cutting Concerns

### Issue 20: T020 - Update daily-digest.md with documentation
**Status**: ✅ Completed
**Description**: Add complete inline documentation and usage examples to `.claude/commands/daily-digest.md`

**Files**: `.claude/commands/daily-digest.md`

### Issue 21: T021 - Run quickstart.md validation
**Status**: ✅ Completed
**Description**: Follow developer and user guides in `specs/main/quickstart.md` end-to-end to verify all documented workflows

**Files**: `specs/main/quickstart.md`

### Issue 22: T022 - Final output validation
**Status**: ✅ Completed
**Description**: Run digest generation against all benchmark samples and verify output format matches contract exactly

**Verification**: 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources for high-signal; best-available with quality warning for low-signal

**Files**: `specs/main/contracts/digest-output-schema.md`, `specs/main/benchmark.md`

---

## Summary

- **Total Issues**: 22
- **Status**: All ✅ Completed
- **MVP Scope**: User Stories 1 & 2 (Phases 1-5)
- **Repository**: https://github.com/priyankamanocha/signalflow

You can manually create these issues on GitHub, or use this script with the GitHub CLI:

```bash
# Example (if gh CLI is installed)
gh issue create --title "T001 - Create digests output directory structure" \
  --body "Create \`digests/{YYYY}/{MM}/\` directory structure in project root for storing generated digest files." \
  --label "phase-1" --state open
```
