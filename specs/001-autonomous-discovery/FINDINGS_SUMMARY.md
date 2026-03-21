# Phase 2 Research Findings Summary

**Date**: 2026-03-21
**Document**: Quick reference for Phase 2 Autonomous Discovery decisions
**Full Research**: See `research.md`

---

## Quick Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **1. Discovery Sources** | Web search (primary) + fetch + MCP (secondary) | No external code, native tools, graceful degradation |
| **2. Content Access** | Sequential fetch, 5-10 URLs, 45s timeout | Latency: 27-48s total (under 45s), simple orchestration |
| **3. Deduplication** | Prompt-based semantic matching + heuristic scoring | No ML models, transparent, scalable to 8-10 sources |
| **4. Quality Signals** | Source classification + engagement heuristics + MVP rubric | Observable heuristics, reuses MVP logic, no external models |

---

## Architecture: Single Skill Pattern

**All logic in `.claude/commands/daily-digest.md`:**

```
Input: /daily-digest claude-code
  ↓
1. Topic Interpretation [Prompt-based]
2. Web Search (native tool) + Fetch (native tool)
3. Source Classification & Engagement Scoring [Prompt-based]
4. Deduplication via Semantic Matching [Prompt-based]
5. Quality Rubric Application [Reuse MVP]
6. Markdown Generation & File Write [Reuse MVP]
```

**No external code files. No infrastructure. No dependencies.**

---

## Latency Budget ✅

```
Web search (3 queries):        2-3 seconds
Content fetch (5-10 URLs):     10-20 seconds
Deduplication + scoring:       10-15 seconds
Insight generation (MVP):      5-10 seconds
---
Total:                         27-48 seconds (Target: <45s)
```

Margin available: 2-18 seconds. Safe.

---

## Reliability Model

### Success Path (≥3 credible sources)
- Generate digest from discovered content
- Same format as MVP (1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources)
- No quality warning needed

### Partial Success (1-2 credible sources or some sources failed)
- Generate digest from available content
- May have fewer insights/resources than targets
- Include quality warning: "⚠️ Low-signal content — insights represent best available"
- Include status: "Discovery incomplete: [source name] unavailable"

### Fallback (0 credible sources or all sources failed/timed out)
- No digest generated
- Display message: "No relevant content discovered. Try manual mode: `/daily-digest topic "[snippet1]" "[snippet2]"`"
- User can trigger MVP manual mode as fallback

---

## Source Credibility Classification

### Credible (use for insights)
- Official/verified: Anthropic blog, official docs, verified authors
- Established outlets: Tech publications, well-known blogs, verified experts
- High engagement proxy: 1000+ views OR 100+ comments

### Non-Credible (exclude from insights; may use in Resources section only, ranked lower)
- Promotional/marketing content
- Unverified sources, very new domains, high spam signals
- Beginner-level content (tutorials, install guides)

---

## Deduplication Scoring

When multiple sources have similar insights, retain **best-evidence version** using heuristics:

```
Score = Credibility (0-3) + Specificity (0-3) + Engagement (0-2)
Range: 0-8
Threshold: Keep version with highest score
```

Example:
- Insight from Twitter (unverified author, 2 likes) = 0+1+0 = 1 → **DISCARD**
- Same insight from Anthropic blog (1200 views, code example) = 3+3+2 = 8 → **KEEP**

Result: One insight, attributed to highest-credibility source. Other sources listed as supporting evidence.

---

## MVP Quality Rubric (Applied to All Insights)

Every insight must score ≥3/4 dimensions:

| Dimension | Score 0 | Score 1 | Score 2 |
|-----------|---------|---------|---------|
| Novelty | Known/obvious | Somewhat new | New + non-obvious |
| Evidence | None | Mentioned | Direct quote |
| Specificity | Generic | Somewhat | Concrete |
| Actionability | Observation | Implies action | Clear action |

**No padding**: Output best-available insights, even if <3 total. Don't force counts.

---

## Implementation Implications

### Must-Haves
1. ✅ Web search tool available (native in Claude Code)
2. ✅ Fetch tool available (native in Claude Code)
3. ✅ 45-second execution window (hard constraint)
4. ✅ MCP availability is optional (graceful fallback to web search)

### Challenges & Mitigations
| Challenge | Mitigation |
|-----------|-----------|
| Web search result quality varies | Use specific queries (keywords + operator words like "pattern", "advanced") |
| HTML parsing from diverse sources | Fetch tool normalizes to markdown automatically |
| Rate limiting | Limit to 10 fetches per run; 45s timeout naturally bounds aggressiveness |
| Deduplication ambiguity | Prompt guidance: "Identical if same underlying practice, even if phrased differently" |
| Engagement data not always available | Use credibility + specificity alone; engagement is optional booster |
| Source classification is heuristic | Transparent rubric; post-MVP could add ML classifier if needed |

---

## Post-Research Decision Gates

Before Phase 2 implementation, verify:

1. ✅ **Web search + fetch tools** are available in Claude Code (assumed: yes)
2. ✅ **45-second latency** is achievable with actual discovery (test: benchmark 3-5 topics)
3. ✅ **Deduplication accuracy** with 20-40 candidate insights (test: manual validation)
4. ✅ **Credibility heuristics** are reliable (test: user feedback during Phase 2 beta)

---

## What This Enables

- Phase 2 as single skill (no external code files)
- Autonomous discovery without manual content curation
- MVP quality maintained via quality rubric + source classification
- Graceful degradation for partial failures, low-signal content, timeouts
- Backward compatibility: MVP manual mode still works (`/daily-digest topic "[snippet1]"...`)

---

## What's Not Solved (Future Phases)

- **Autonomous scheduling** (Phase 3: daily at scheduled time)
- **Personalization** (Phase 3: user feedback loop via `/rate-digest`)
- **Persistent source management** (Phase 3: maintain followed accounts across runs)
- **Parallelization** (Phase 4: subagents for faster discovery if latency becomes issue)

---

## Test Plan (Post-Implementation)

1. **Latency test**: Run 5 digests, measure end-to-end time. Verify <45s.
2. **Quality test**: 10 digests, verify each insight scores ≥3/4 dimensions (MVP rubric).
3. **Deduplication test**: Hand-label duplicate insights in discovered content, verify system deduplication accuracy >90%.
4. **Source attribution test**: Verify each insight is credited to a credible source; no low-credibility sources in Insights section.
5. **Fallback test**: Attempt discovery on ultra-niche topic, verify graceful fallback to manual mode message.

---

**Next**: Implement Phase 2 skill using this research as specification.
