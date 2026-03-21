# Phase 2 Autonomous Content Discovery — Complete Research Package

**Date**: 2026-03-21
**Phase**: 2 (Post-MVP)
**Status**: Research Complete ✅

This directory contains complete technical research and implementation guidance for Phase 2 Autonomous Content Discovery in SignalFlow.

---

## Document Overview

### Core Research Documents

1. **[research.md](research.md)** — *Full Technical Research Report*
   - Detailed analysis of all four discovery areas
   - Design decisions with rationale
   - Alternatives considered and rejected
   - Latency analysis and reliability profiles
   - Example discovery flow with numbers

   **When to read**: Deep-dive into technical decisions; understanding tradeoffs

2. **[FINDINGS_SUMMARY.md](FINDINGS_SUMMARY.md)** — *Quick Reference*
   - One-page summary of all key decisions
   - Decision table showing area, decision, and rationale
   - Architecture overview
   - Latency budget and reliability model
   - Test plan

   **When to read**: Quick check on decisions; brief overview for stakeholders

3. **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** — *Step-by-Step Implementation*
   - 15 detailed sections for implementing Phase 2 skill
   - Pseudo-code and prompt guidance for each section
   - Testing checklist
   - Implementation order (recommended)
   - Known limitations and future work

   **When to read**: Ready to implement Phase 2; need concrete instructions

### Reference Documents

4. **[spec.md](spec.md)** — *Feature Specification*
   - User stories and acceptance criteria
   - Functional requirements (FR-001 through FR-014)
   - Success criteria
   - Edge cases and failure modes

   **When to read**: Understanding what Phase 2 should deliver

5. **[plan.md](plan.md)** — *Implementation Plan*
   - High-level scope and timeline
   - Constitution check (design validation)
   - Complexity tracking
   - Project structure

   **When to read**: Project oversight; tracking progress

---

## The Four Core Research Areas

### 1. Discovery Source Integration
**Question**: How to access content from web, video, and social media?

**Decision**: Layered MCP + WebSearch + Fallback Pattern
- **Primary**: Claude's native `web_search` tool
- **Secondary**: Direct URL fetching via `fetch` tool
- **Tertiary**: Community MCP servers (Twitter, YouTube) if available
- **Fallback**: Graceful degradation to manual mode

**Why it works for MVP**:
- No external code files (all native tools)
- No infrastructure (tools already available)
- Single skill implementation
- 45-second latency budget: achievable in 27-48 seconds

**Reference**: See `research.md`, Section 1

### 2. Content Access
**Question**: How to efficiently fetch multi-source content within 45-second budget?

**Decision**: Sequential Fetch with Timeout Guard
- Execute 5-10 fetches in rapid succession (not strict parallelism)
- Aggregate content into unified corpus
- Hard timeout at 45 seconds; use best-available content if cutoff reached
- Automatic markdown parsing (fetch tool handles HTML → markdown)

**Latency breakdown**:
- Web search: 2-3 seconds
- Content fetch: 10-20 seconds
- Deduplication + scoring: 10-15 seconds
- Insight generation: 5-10 seconds
- **Total: 27-48 seconds** ✅

**Reference**: See `research.md`, Section 2

### 3. Deduplication Strategy
**Question**: How to identify semantically identical insights without embeddings?

**Decision**: Prompt-Based Semantic Matching + Heuristic Scoring
- Claude's reasoning identifies semantically identical insights
- Heuristic scoring selects "best-evidence version"
- Maintains source attribution trails
- No external embeddings or ML models

**Heuristic scoring formula**:
```
score = credibility (0-3) + specificity (0-3) + engagement (0-2)
Range: 0-8
Threshold: Retain highest-scoring version per insight group
```

**Expected efficiency**: 8-10 sources → 20-40 candidate insights → 3-7 unique after deduplication

**Reference**: See `research.md`, Section 3

### 4. Quality Signal Detection
**Question**: How to score source credibility and content relevance without ML?

**Decision**: Observable Heuristics + Topic Relevance + MVP Quality Rubric
- Source classification: HIGH | MEDIUM | LOW credibility
- Engagement signals: views, comments, recency (when available)
- Topic relevance scoring: ensures content is about specified topic
- MVP quality rubric application: 4 dimensions, ≥2 on ≥3 required

**Source credibility assessment**:
```
credibility_score = (domain + author + content + engagement) / 4
Normalize to: HIGH (≥2.5) | MEDIUM (1.5-2.5) | LOW (<1.5)
```

**Quality rubric** (4 dimensions):
- Novelty (0-2): Known → Somewhat new → New + non-obvious
- Evidence (0-2): None → Mentioned → Direct quote
- Specificity (0-2): Generic → Somewhat → Concrete
- Actionability (0-2): Observation → Implies action → Clear action

**Inclusion rule**: Score ≥2 on ≥3 dimensions

**Reference**: See `research.md`, Section 4

---

## Architecture

All Phase 2 logic implements as **single skill file**: `.claude/commands/daily-digest.md`

```
Current MVP:
  /daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"
           ↓ (user provides content)
        Insight extraction

Phase 2:
  /daily-digest claude-code
           ↓ (no snippets provided)
        Autonomous discovery
           ↓ (web search + fetch + dedup)
        Insight extraction (same as MVP)

Backward compatible:
  /daily-digest claude-code "[snippet1]"
           ↓ (snippets provided)
        MVP manual mode (existing logic)
```

**No external code files. No infrastructure. Everything in prompt.**

---

## Key Decisions at a Glance

| Decision | Why | Risk Mitigation |
|----------|-----|-----------------|
| **Web search primary, MCP secondary** | Web always available; MCP optional enhancement | Falls back to web-only if MCP unavailable |
| **Sequential fetch, not parallel** | Simpler orchestration in prompt; latency still <45s | Timeout guard at 40s ensures <45s total |
| **Prompt-based deduplication** | No embeddings/ML; transparent; auditable | Heuristic scoring; manual validation possible |
| **Heuristic credibility scoring** | Observable signals; no external models | Post-MVP could add ML classifier if needed |
| **Reuse MVP quality rubric** | Consistent signal quality across MVP + Phase 2 | No new evaluation logic; proven methodology |
| **Single skill implementation** | Maintains MVP architecture constraint | Prompt will be larger but still manageable |

---

## Success Criteria (Phase 2)

From spec.md:

- ✅ **SC-001**: Digest from autonomous discovery without text snippets
- ✅ **SC-002**: Structure/format matches MVP output
- ✅ **SC-003**: Each insight attributed to credible source
- ✅ **SC-004**: Discovery + digest within 45 seconds
- ✅ **SC-005**: Partial discovery with quality warning
- ✅ **SC-006**: Fallback message if 0 credible sources found
- ✅ **SC-007**: Duplicate insights merged; single attributed to best source
- ✅ **SC-008**: MVP manual mode still works alongside Phase 2

---

## Testing Strategy

### Pre-Implementation
1. Verify web_search and fetch tools available in Claude Code
2. Benchmark tool latency (expect 2-3s per operation)

### Post-Implementation
1. **Latency test**: 5 digests, all <45 seconds
2. **Quality test**: 10 digests, verify insights score ≥3/4 dimensions
3. **Deduplication test**: Manual validation of merging accuracy >90%
4. **Source attribution**: Verify no low-credibility sources in Insights section
5. **Fallback test**: Ultra-niche topic triggers manual mode fallback
6. **Backward compatibility**: MVP manual mode still works

---

## Implementation Roadmap

**Estimated effort**: 2-3 weeks post-MVP validation

**Phase 2 Milestone**: All 15 sections implemented
1. Input parsing + mode detection
2. Topic interpretation
3. Web discovery
4. Content fetching
5. MCP sources (optional)
6. Timeout management
7. Source classification
8. Engagement signals
9. Deduplication
10. Topic relevance filtering
11. Quality rubric application
12. Anti-patterns & actions (reuse MVP)
13. Quality signal detection
14. Fallback handling
15. Output & file write (reuse MVP)

**See IMPLEMENTATION_GUIDE.md for detailed breakdown.**

---

## Known Unknowns (Post-Research Validation)

1. **MCP server availability**: Assume Twitter/YouTube MCPs available or optional. *Action: Test before Phase 2 coding.*
2. **Web search quality for niche topics**: Assume "Claude Code" etc. are well-served. *Action: Benchmark 3-5 representative topics.*
3. **Engagement data availability**: Some sources may not expose views/comments. *Action: Audit top 20 sources for engagement data.*
4. **Heuristic deduplication accuracy**: Assumes Claude can group ~40 insights accurately. *Action: Benchmark with real discovery output.*

---

## Future Phases (Out of Scope)

**Phase 3: Personalization & Learning**
- `/rate-digest` command for user feedback
- Adapt future digests based on feedback
- Persistent source management (followed accounts)

**Phase 4+: Automation & Scale**
- Autonomous scheduling (daily at 9am)
- Subagent-based parallelization
- Historical trend tracking
- Notion integration for knowledge management

---

## Document Navigation

**For decision makers**: Start with [FINDINGS_SUMMARY.md](FINDINGS_SUMMARY.md)
**For implementers**: Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) + [research.md](research.md) Section by Section
**For auditors/reviewers**: Start with [spec.md](spec.md), reference [research.md](research.md) for tradeoffs
**For project managers**: [plan.md](plan.md) for scope, [FINDINGS_SUMMARY.md](FINDINGS_SUMMARY.md) for risk/mitigation

---

## Questions?

Each document includes:
- Rationale section explaining "why"
- Alternatives considered explaining "why not"
- Implementation implications highlighting challenges + mitigations

Refer to appropriate section in [research.md](research.md) for deep-dive on any decision.

---

**Research Package Complete. Ready for Phase 2 Implementation.**
