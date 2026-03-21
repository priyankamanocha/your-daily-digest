# Feature Specification: SignalFlow Daily Intelligence Digest

**Feature Branch**: `main`
**Created**: 2026-03-21
**Status**: Draft
**Input**: SignalFlow system requirements from `/spec/requirements.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Digest from Manual Content Input (Priority: P1)

User manually gathers content snippets (text excerpts from articles, tweets, code examples, documentation) on a topic, pastes them into `/daily-digest <topic>`, and receives a digest with high-signal insights extracted from that content.

**Why this priority**: Core MVP functionality. Focuses on the hardest part: insight extraction and synthesis from raw content. Without a working digest engine, everything else is waste.

**Independent Test**: Can be fully tested by providing 3-5 text content snippets (100-500 words each), running the command, and receiving a markdown digest with 1-3 high-quality insights, anti-patterns, and actions. This alone validates the core value.

**Acceptance Scenarios**:

1. **Given** user pastes text content snippets and runs `/daily-digest claude-code "snippet1" "snippet2" "snippet3"`, **When** system completes processing, **Then** a markdown file is created with insights extracted from provided content
2. **Given** user provides the same content in different formats (bullet points, paragraphs, code), **When** system completes processing, **Then** digest handles varied input formats gracefully
3. **Given** insufficient high-signal content provided, **When** system completes processing, **Then** output includes quality warning and best-available insights

---

### User Story 2 - Extract High-Quality Insights & Actions (Priority: P1)

System extracts non-obvious insights from provided content (novel techniques with concrete evidence, non-obvious patterns) and generates 1-3 actionable experiments users can try in 30 minutes to 3 hours.

**Why this priority**: This is the core value. Without quality insights and actions, the output is not useful. MVP must nail this before adding automation.

**Independent Test**: Can be fully tested by verifying that insights are: not restatements of content, not obvious/commonly known, backed by evidence, and answer "what are advanced users doing?" / "why does it matter?" / "how to apply it?". Actions are concrete, executable independently, and produce measurable outcomes.

**Acceptance Scenarios**:

1. **Given** user-provided content, **When** insight extraction runs, **Then** system produces 1-3 high-quality insights that reflect real-world usage patterns and are actionable
2. **Given** content doesn't meet quality bar, **When** output is assembled, **Then** system outputs best available and flags low confidence rather than padding
3. **Given** insights are extracted, **When** action generation runs, **Then** system produces 1-3 concrete actions with effort levels, time estimates, and expected outcomes

---

### Edge Cases (MVP)

- What happens when no high-signal content is available? → System outputs best available content with visible quality warning (`⚠️ Low-signal content`)
- What happens when an insight doesn't answer all three required questions (what/why/how)? → System rejects it and continues evaluating other content
- What happens when provided content is too short/sparse? → System outputs best-available insights and flags reduced signal in output

## Requirements *(mandatory)*

### Functional Requirements (MVP)

**Input**
- **FR-001**: System MUST accept user-specified topic (string, no special format)
- **FR-002**: System MUST accept 3-5 text content snippets (user-provided, no web fetching)
- **FR-003**: System MUST NOT fetch content from URLs, APIs, or external sources (user must provide text directly)

**Processing**
- **FR-004**: System MUST filter provided content using high-signal criteria: concrete technique, non-obvious insight, evidence provided
- **FR-005**: System MUST extract insights that qualify as: novel techniques with evidence OR non-obvious patterns
- **FR-006**: System MUST extract 2-4 anti-patterns and explain why to avoid
- **FR-007**: System MUST generate 1-3 actionable experiments: executable, 30 min-3 hours, measurable outcomes
- **FR-008**: System MUST identify 3-5 supporting resources/citations from provided content

**Output**
- **FR-009**: System MUST produce markdown file with: Key Insights (1-3), Anti-patterns (2-4), Actions (1-3), Resources (3-5)
- **FR-010**: System MUST date-stamp output and write to `digests/{YYYY}/{MM}/` directory
- **FR-011**: System MUST use Claude Code skill primitives only (no external code, no build step)
- **FR-012**: System MUST clearly flag low-signal digests with quality warnings instead of padding

### Post-MVP Requirements (Phase 2+)

- **FR-P2-001**: System MUST autonomously discover content from YouTube, Twitter/X, blogs, and web
- **FR-P2-002**: System MUST deduplicate content across sources (semantic merging)
- **FR-P2-003**: System MUST use subagents for parallel content retrieval
- **FR-P2-004**: System MUST accept feedback via `/rate-digest` and adapt source prioritization
- **FR-P2-005**: System MUST persist state across runs (channels, feedback, source weights)
- **FR-P2-006**: System MUST suggest and manage YouTube channel discovery

### Interpretation of Topic Scope

The system MUST interpret the user-provided topic to include:
- Core keywords directly associated with the topic
- Related subtopics and concepts that frequently co-occur with it
- Relevant domains (tools, frameworks, ecosystems that are part of the topic's world)

For example, topic "Claude Code" includes: subagents, skills, hooks, MCP, slash commands, usage patterns, agent-based development, direct tool comparisons (Cursor, Copilot, Windsurf). It explicitly excludes: generic LLM discussions, unrelated AI tooling, broad AI news with no practical relevance.

### Key Entities (MVP Only)

- **Insight**: Non-obvious pattern or technique with evidence from provided content; answers what/why/how
- **Anti-pattern**: Inefficient or incorrect practice with explanation of why to avoid
- **Action**: Concrete, testable experiment; effort level (low/medium/high); time estimate (30 min - 3 hours); produces measurable outcome
- **Resource**: Supporting reference from provided content (quoted text or source attribution) with justification for inclusion

## Success Criteria *(mandatory)*

### MVP Measurable Outcomes

**Target Counts** (for high-signal digests):
- **SC-001**: System produces 1-3 insights per run
- **SC-002**: Each insight: non-obvious, backed by evidence from provided content, answers ALL THREE of "what/why/how"
- **SC-003**: System produces 2-4 anti-patterns per run
- **SC-004**: System produces 1-3 actions per run
- **SC-005**: System produces 3-5 supporting resources per run

**Low-Signal Handling** (explicit rule):
- **SC-006**: For high-signal content: aim for exact target counts above
- **SC-007**: For low-signal content: output best-available insights (may be fewer than minimums) with visible quality warning; **do not pad with weak content**
- **SC-008**: Digest generation completes in < 3 minutes per run (text processing only, no I/O)

**Quality Gate**:
- **SC-009**: Output meets quality benchmark (see `benchmark.md`): extracts high-quality insights, rejects padding, generates concrete actions

### Post-MVP Success Criteria (Phase 2+)

- **SC-P2-001**: Autonomous content discovery retrieves 10-20 high-signal items per source
- **SC-P2-002**: Semantic deduplication merges duplicate insights (no redundancy in final digest)
- **SC-P2-003**: Feedback signals influence source prioritization (observed improvement in subsequent digests)
- **SC-P2-004**: YouTube channel suggestions are accurate and relevant
