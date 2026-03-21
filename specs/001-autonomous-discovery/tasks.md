---
description: "Task list for Phase 2 Autonomous Content Discovery implementation"
---

# Tasks: Phase 2 — Autonomous Content Discovery

**Input**: Design documents from `/specs/001-autonomous-discovery/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Tests**: Not explicitly requested in feature specification - validation via manual invocation and quality rubric testing

**Organization**: Tasks grouped by user story (US1: Autonomous Discovery [P1], US2: Source Quality [P2]) to enable independent implementation and testing.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize skill file structure and foundation

- [x] T001 Create `.claude/skills/autonomous-discovery.md` with header, input parsing section, and orchestrator placeholder
- [x] T002 Set up project structure: Create `digests/{2026}/{01-12}/` directory structure for date-stamped output
- [ ] T003 [P] Create `.specify/` configuration and test helper scripts for skill validation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before user story implementation can begin

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Input Validation & Parsing

- [x] T004 Implement input validation in `.claude/skills/autonomous-discovery.md`: topic length (max 100 chars), hint count (max 10), valid characters (alphanumeric, hyphens, underscores)
- [x] T005 [P] Implement hint normalization: parse comma-separated hints, remove duplicates, trim whitespace
- [x] T006 [P] Implement error handling for invalid inputs: return structured error messages per input-schema.md contract

### Orchestrator Foundation

- [x] T007 Implement orchestrator main loop in `.claude/skills/autonomous-discovery.md`: spawn 3 agents in parallel, collect results, measure execution time
- [x] T008 [P] Implement timeout handler: 45-second deadline with graceful degradation to partial results
- [x] T009 [P] Implement result collection: merge DiscoveredSource[], DiscoveryResult container, track completion_status (complete/partial/timeout)

### MVP Integration

- [x] T010 Integrate MVP quality rubric application: reuse existing insight extraction logic from MVP daily-digest.md
- [x] T011 [P] Implement FinalDigest generation: match MVP output format (insights, antipatterns, actions, resources, quality warnings)
- [x] T012 [P] Implement output file writing: create digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md files with proper metadata

### Deduplication & Quality Scoring (Scaffolding)

- [x] T013 Implement CandidateInsight structure: extract insights from discovered sources with fields (title, description, evidence, source_urls, credibility_score, freshness_score, specificity_score, engagement_score)
- [x] T014 [P] Implement deduplication placeholder: semantic matching logic skeleton (will be filled by US2)
- [x] T015 [P] Implement quality filtering placeholder: MVP rubric enforcement skeleton (will be filled by US2)

**Checkpoint**: ✅ Foundation complete - User Story 1 implementation can begin

**Skill Structure** (`.claude/skills/autonomous-discovery.md`):
- Configuration & Constants (all tunable parameters)
- Data Structures (UserInput, DiscoveredSource, CandidateInsight, DiscoveryResult, FinalDigest)
- Input Validation Module (parseUserInput, validateTopic, parseAndValidateHints)
- Agent Interface & Orchestrator (DiscoveryAgent, DiscoveryOrchestrator)
- Processing Pipeline (extractCandidateInsights, deduplicateInsights, filterByQuality)
- Output Generation (generateFinalDigest, writeDigestFile, formatDigestMarkdown)
- Error Handling (createValidationError, FALLBACK_MESSAGES)
- Utility Functions (calculateDaysOld, calculateFreshnessScore, createTopicSlug)
- Main Entrypoint (autonomousDiscovery skill invocation)

---

## Phase 3: User Story 1 - Autonomous Topic Discovery (Priority: P1) 🎯 MVP

**Goal**: Implement autonomous discovery from web, video, and social media sources without manual text input

**Independent Test**:
- User invokes `/daily-digest <topic>` with no text snippets
- System discovers relevant content from web, YouTube, Twitter
- System generates digest with 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
- Output created at `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic}.md`
- All insights cite credible sources

### Web Discovery Agent

- [ ] T016 [P] [US1] Implement web discovery agent prompt in `.claude/commands/skills.md`: interpret topic into search keywords, execute 3-5 web searches, fetch top URLs, extract content
- [ ] T017 [P] [US1] Implement web agent result formatting: return DiscoveredSource[] with (url, title, content, source_type="web", author, published_date, freshness_score, credibility_signal)
- [ ] T018 [P] [US1] Add web agent latency tracking: measure execution time (target 8-12s per research.md)

### Video Discovery Agent

- [ ] T019 [P] [US1] Implement video discovery agent prompt: search YouTube, fetch video metadata and transcripts, extract relevant content
- [ ] T020 [P] [US1] Implement video agent result formatting: return DiscoveredSource[] with source_type="video", channel/creator information, transcripts as content
- [ ] T021 [P] [US1] Add video agent latency tracking: measure execution time (target 6-10s per research.md)

### Social Media Discovery Agent

- [ ] T022 [P] [US1] Implement social media discovery agent prompt: search Twitter/X for relevant discussions, fetch threads and replies, prioritize verified accounts
- [ ] T023 [P] [US1] Implement social agent result formatting: return DiscoveredSource[] with source_type="social", author/handle, tweet/post content, engagement signals (likes, retweets)
- [ ] T024 [P] [US1] Add social agent latency tracking: measure execution time (target 5-8s per research.md)

### Hint-Based Discovery Enhancement

- [ ] T025 [US1] Implement hint prioritization in discovery agents: if hints provided, boost results from specified YouTube channels and X/Twitter users
- [ ] T026 [P] [US1] Add hint validation: map hints to actual channels/accounts, skip invalid hints gracefully
- [ ] T027 [P] [US1] Log hint usage: track which hints matched results for transparency

### Orchestration & Aggregation

- [ ] T028 [US1] Implement parallel agent orchestration: spawn web, video, social agents simultaneously, wait for all with timeout
- [ ] T029 [P] [US1] Implement result merging: aggregate DiscoveredSource[] from all 3 agents into single DiscoveryResult, track which agents succeeded
- [ ] T030 [P] [US1] Implement discovery status tracking: mark completion_status as "complete" (≥3 agents succeeded), "partial" (1-2 agents succeeded), or "timeout" (45s exceeded)

### MVP Integration for US1

- [ ] T031 [US1] Extract CandidateInsight[] from discovered sources: generate 20-40 insight proposals with all quality scores
- [ ] T032 [P] [US1] Apply MVP quality rubric: retain insights passing ≥2 on 3/4 dimensions (novelty, evidence, specificity, actionability)
- [ ] T033 [P] [US1] Generate final digest output: select 1-3 insights, 2-4 antipatterns, 1-3 actions, 3-5 resources matching MVP format

### Fallback Handling for US1

- [ ] T034 [US1] Implement no-credible-content fallback: when zero credible sources found, display message "No relevant content discovered for topic '[topic]'. Try providing text snippets manually: `/daily-digest [topic] "[snippet1]" "[snippet2]"...`"
- [ ] T035 [P] [US1] Implement timeout warning message: when 45-second deadline exceeded, include "Discovery incomplete: operation timed out" in output
- [ ] T036 [P] [US1] Implement partial results handling: when 1-2 credible sources available, generate digest with quality warning "⚠️ Low-signal content — insights below represent the best available material"

### Output Generation for US1

- [ ] T037 [US1] Implement markdown digest generation per output-schema.md: header with topic, generated timestamp, discovery status
- [ ] T038 [P] [US1] Implement source attribution: each insight/action includes **Source** field with publication name
- [ ] T039 [P] [US1] Implement file path generation: create digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md with proper date/topic formatting

**Checkpoint**: User Story 1 (Autonomous Discovery) fully functional and independently testable

---

## Phase 4: User Story 2 - Source Quality & Filtering (Priority: P2)

**Goal**: Ensure discovered content prioritizes credible sources and enforces quality standards

**Independent Test**:
- Provide digest for topic with mixed source credibility (reputable + questionable sources)
- Verify digest insights prioritize credible sources
- Verify digest maintains 1-3 insights and 2-4 antipatterns (no padding from weak sources)
- Verify non-credible sources excluded from insights but may appear in Resources section (ranked lower)

### Credibility Classification

- [ ] T040 [P] [US2] Implement credibility scoring: classify sources on 0-3 scale based on (publisher authority, account verification, primary vs secondary, domain reputation)
- [ ] T041 [P] [US2] Implement observable signals: detect verified accounts (blue checkmarks), official publications, primary sources, known spam domains
- [ ] T042 [P] [US2] Add web credibility rules: prioritize established outlets (.edu, .org, verified domains), deprioritize unverified blogs and promotional content
- [ ] T043 [P] [US2] Add video credibility rules: prioritize verified YouTube channels, official creators, published content; deprioritize random channels without verification
- [ ] T044 [P] [US2] Add social credibility rules: prioritize verified X/Twitter accounts, official announcements, established tech influencers; deprioritize unverified accounts, promotional spam

### Quality Enforcement

- [ ] T045 [US2] Implement credible-source-only requirement for insights: exclude non-credible sources from insight extraction (credibility_score < 2)
- [ ] T046 [P] [US2] Implement antipattern credibility filtering: retain only antipatterns sourced from credible sources
- [ ] T047 [P] [US2] Implement action credibility filtering: retain only actions sourced from credible sources

### Resource Ranking

- [ ] T048 [US2] Implement resource ranking: credible resources listed first, non-credible resources (credibility_score < 2) listed second and marked as supplementary
- [ ] T049 [P] [US2] Add resource quality metadata: mark credible vs supplementary in resource output for transparency

### Low-Signal Handling

- [ ] T050 [US2] Implement low-signal detection: when <3 credible sources available, set quality_warning flag
- [ ] T051 [P] [US2] Implement quality warning generation: include "⚠️ Low-signal content — insights below represent the best available material" when appropriate
- [ ] T052 [P] [US2] Implement discovery status transparency: list which sources failed/timed out (e.g., "Discovery incomplete: Twitter unavailable")

### Deduplication with Quality Priority

- [ ] T053 [US2] Implement semantic deduplication: identify near-duplicate insights across sources
- [ ] T054 [P] [US2] Implement credibility-based deduplication: when duplicates found, retain version from highest-credibility source
- [ ] T055 [P] [US2] Implement freshness scoring in deduplication: break ties using freshness_score (0-3: very fresh <2 days = 3, fresh 2-7 days = 2, moderate 8-30 days = 1, stale >30 days = 0)
- [ ] T056 [P] [US2] Implement engagement scoring: factor author authority and community validation into deduplication ranking

### No-Credible-Content Fallback

- [ ] T057 [US2] Implement zero-credible-sources fallback: when no credible sources found for topic, display fallback message and skip digest generation
- [ ] T058 [P] [US2] Implement manual mode trigger: fallback message includes instruction to provide text snippets: `/daily-digest <topic> "<snippet1>" "<snippet2>"`

**Checkpoint**: User Stories 1 AND 2 both functional; autonomous discovery prioritizes credible sources and maintains quality standards

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and quality assurance

### Benchmark & Quality Validation

- [ ] T059 [P] Run benchmark test: validate skill against sample topics from benchmark.md
- [ ] T060 [P] Verify output quality: confirm generated digests pass MVP quality rubric on 3/4 dimensions (novelty, evidence, specificity, actionability)
- [ ] T061 [P] Validate latency: measure end-to-end execution time, confirm <45 seconds

### Backward Compatibility

- [ ] T062 Verify MVP manual mode still works: test `/daily-digest <topic> "<snippet1>" "<snippet2>"` (original text-based mode)
- [ ] T063 [P] Test fallback integration: when autonomous discovery fails, manual mode can be triggered as fallback

### Error Handling & Edge Cases

- [ ] T064 [P] Test ultra-niche topics: verify graceful fallback when no discovery sources available
- [ ] T065 [P] Test paywalled content: verify system skips paywalled resources, continues with public content
- [ ] T066 [P] Test non-English content: verify system prioritizes English, includes non-English only if directly relevant
- [ ] T067 [P] Test breaking news: verify system includes recent sources with quality warning if few results available

### Documentation & Reference

- [ ] T068 Create IMPLEMENTATION_CHECKLIST.md: step-by-step verification of feature completion per spec.md requirements
- [ ] T069 [P] Create QUICK_REFERENCE.md: user guide for Phase 2 command syntax, examples, fallback behavior
- [ ] T070 [P] Update README.md: describe Phase 2 autonomous discovery mode, link to documentation

### Logging & Transparency

- [ ] T071 [P] Implement discovery logging: log agent invocations, result counts, deduplication steps (for debugging)
- [ ] T072 [P] Implement quality metadata logging: track credibility scores, freshness scores, quality warnings generated

### Final Validation

- [ ] T073 Run validation script: execute IMPLEMENTATION_CHECKLIST.md against feature requirements
- [ ] T074 [P] Verify all user scenarios from spec.md: test acceptance criteria for US1 (autonomous discovery) and US2 (quality filtering)
- [ ] T075 [P] Confirm spec.md success criteria met: SC-001 through SC-008 all passing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS** all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Can run in parallel with US2 once foundational is done
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Can run in parallel with US1 (credibility scoring overlays US1 agents)
- **Polish (Phase 5)**: Depends on US1 + US2 completion

### User Story Dependencies

- **User Story 1 (P1 - Autonomous Discovery)**: Core value - no dependencies beyond Foundational
  - Can be independently tested: user invokes `/daily-digest <topic>`, receives digest
  - Models: DiscoveredSource, CandidateInsight, DiscoveryResult
  - Agents: Web, Video, Social (parallel)

- **User Story 2 (P2 - Source Quality)**: Enhancement to US1 - can run in parallel
  - Can be independently tested: digest prioritizes credible sources, enforces quality
  - Overlays credibility scoring onto US1 agent results
  - Depends conceptually on US1 agents but can be implemented simultaneously

### Within Each User Story

- **US1 Execution Order**:
  1. Foundational tasks (input validation, orchestrator, MVP integration)
  2. Agent implementation in parallel (web, video, social)
  3. Hint-based enhancement
  4. Output generation

- **US2 Execution Order**:
  1. Credibility classification (rules for web, video, social)
  2. Quality enforcement (filter insights, antipatterns, actions)
  3. Deduplication with quality priority
  4. Fallback handling

### Parallel Opportunities

- **Setup (Phase 1)**: All tasks marked [P] can run in parallel
- **Foundational (Phase 2)**: All tasks marked [P] (validation, timeout, result collection, deduplication, quality filtering) can run in parallel
- **User Story 1 (Phase 3)**:
  - All 3 agents (T016-T024) marked [P] can be implemented in parallel (different source types)
  - Latency tracking tasks marked [P] can run in parallel
  - Hint-based enhancement (T026-T027) marked [P] can run in parallel
- **User Story 2 (Phase 4)**: All credibility rules (T042-T044) marked [P] can run in parallel
- **Polish (Phase 5)**: All validation and testing tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Parallel: Implement all 3 discovery agents simultaneously (different files/logic)
Task: "Implement web discovery agent prompt in .claude/commands/skills.md"
Task: "Implement video discovery agent prompt in .claude/commands/skills.md"
Task: "Implement social media discovery agent prompt in .claude/commands/skills.md"

# Parallel: Implement result formatting for all agents
Task: "Implement web agent result formatting: return DiscoveredSource[]"
Task: "Implement video agent result formatting: return DiscoveredSource[]"
Task: "Implement social agent result formatting: return DiscoveredSource[]"

# Parallel: Implement latency tracking for all agents
Task: "Add web agent latency tracking"
Task: "Add video agent latency tracking"
Task: "Add social agent latency tracking"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (T001-T003)
2. ✅ Complete Phase 2: Foundational (T004-T015) - **CRITICAL**
3. ✅ Complete Phase 3: User Story 1 (T016-T039)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - User invokes `/daily-digest claude-code`, receives digest
   - Verify all 3 agents returning results
   - Confirm output matches MVP format
5. Deploy/demo Phase 1 MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP complete!)
3. Add User Story 2 → Test independently → Deploy/Demo (Enhanced with quality filtering)
4. Run Polish tasks → Final validation
5. Each user story adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. **Developer A**: Foundational phase (input validation, orchestrator, MVP integration)
2. Once Foundational ready:
   - **Developer A**: Web discovery agent (US1)
   - **Developer B**: Video discovery agent (US1)
   - **Developer C**: Social discovery agent (US1)
3. Once US1 agents complete, parallel work on US2:
   - **Developer A**: Credibility classification (US2)
   - **Developer B**: Quality enforcement (US2)
   - **Developer C**: Deduplication + resource ranking (US2)
4. Final: Polish + validation in parallel

---

## Notes

- [P] tasks = different files/agents/logic, no dependencies
- [Story] label maps task to specific user story (US1, US2) for traceability
- Each user story independently completable and testable
- Single file structure: all implementation in `.claude/commands/skills.md`
- Latency budget: 45 seconds total (research.md estimates ~27s with 18s safety margin)
- Quality rubric: MVP novelty/evidence/specificity/actionability applied to all discovered insights
- No external code files: all logic prompt-based in skills.md
- Backward compatibility: MVP manual mode continues to work
- Commit after each task or logical group (suggest: after foundational, after US1, after US2, after polish)
- Stop at any checkpoint to validate story independently before proceeding

---

## Success Criteria Mapping

**spec.md requirements → Task coverage**:

| Requirement | Tasks |
|-------------|-------|
| FR-001: Discover from multiple sources | T016-T024 (3 agents) |
| FR-002: Synthesize into digest format | T031-T033, T037-T039 |
| FR-003: Complete within 45 seconds | T008, T018, T021, T024, T061 |
| FR-004: Merge duplicate insights | T053-T056 |
| FR-005: Classify credibility | T040-T044 |
| FR-006: Exclude non-credible from insights | T045-T047 |
| FR-007: Allow non-credible in resources | T048-T049 |
| FR-008: Apply quality rubric | T032, T060 |
| FR-009: Attribute insights | T037-T038 |
| FR-010: Indicate completeness | T030, T035-T036, T052 |
| FR-011: Include quality warning | T050-T052 |
| FR-012: Handle source failures gracefully | T029-T030, T057-T058 |
| FR-013: Timeout & partial results | T008, T030, T034-T036 |
| FR-014: Fallback to manual mode | T034, T057-T058 |

