# Research: SignalFlow Technical Decisions

**Date**: 2026-03-21
**Purpose**: Document MVP decisions and future architecture (clearly separated)

---

# PART A: MVP DECISIONS (Phase 1)

## 1. MVP Input Model: Manual Text Content Only

### Decision
**MVP accepts ONLY user-pasted text content**. No URL fetching, no web access, no external integrations.

Users manually gather 3-5 text snippets (100-500 words each) from any source and paste directly:
```
/daily-digest claude-code "snippet1..." "snippet2..." "snippet3..."
```

### Rationale
1. **Zero infrastructure**: No MCP, no APIs, no external dependencies
2. **Fast iteration**: Can build and validate in 1-2 weeks
3. **Core value first**: Proves insight extraction works before adding complexity
4. **User in control**: User decides what content is relevant, not a search algorithm
5. **No ambiguity**: Clear input/output, no fetching failures or timeouts

### What This Means
- `/daily-digest <topic> <text_snippet_1> <text_snippet_2> ... <text_snippet_5>`
- System reads provided text → filters → synthesizes → outputs markdown
- No network calls, no MCP, no subagents, no APIs
- User responsible for content curation

### Alternatives Considered & Rejected for MVP
- **URLs with web fetching**: Requires MCP integration; deferred to Phase 2
- **URLs with user-provided content**: Confusing; text only is clearer
- **Autonomous discovery**: Infrastructure overhead; defer to Phase 2
- **Real-time streaming**: Scope creep; not MVP

---

## 2. Insight Extraction: Prompt-Based Synthesis (No Padding)

### Decision
**Claude reads text snippets and extracts insights** using a strict, non-padded prompt:

Each insight MUST:
- Have a title (5-10 words)
- Include description answering: what/why/how (2-3 sentences)
- Cite evidence directly from provided content
- Be non-obvious (not widely known)

**EXACT COUNTS** (not targets, not ranges):
- **1-3 insights per digest** (minimum 1, maximum 3 — enforce strictly)
- **2-4 anti-patterns per digest** (minimum 2, maximum 4)
- **1-3 actions per digest** (minimum 1, maximum 3)
- **3-5 resources per digest** (minimum 3, maximum 5)

If fewer insights meet the quality bar → output what qualifies, don't pad.

### Rationale
1. **Exact counts force quality discipline**: "1-3" is not the same as "up to 5"; prevents padding
2. **Evidence requirement prevents hallucination**: All insights grounded in provided content
3. **Claude's strength**: Pattern recognition + reasoning work well
4. **Simple + transparent**: No ML models; users can verify output
5. **Non-obvious requirement**: Distinguishes insights from summaries

### Alternatives Considered
- Automatic keyword extraction: Too shallow (rejected)
- ML models: Over-engineered, slow to validate (rejected)
- Summarization: Restatement not insight (rejected)

---

## 3. MVP Output Format (Simplified)

### Decision
**Markdown file**, date-stamped, minimal schema:

```
# Daily Digest — {TOPIC}
Generated: {YYYY-MM-DD HH:MM}

## 🧠 Key Insights (1-3)
### Insight Title
[Description: what / why / how]
**Evidence**: "[direct quote from provided content]"

## ⚠️ Anti-patterns (2-4)
- [Name]: [Why to avoid] (cite if from content)

## ⚡ Actions to Try (1-3)
### Action Title
- Effort: low/medium/high
- Time: X minutes
- Steps: [numbered]

## 🔗 Resources (3-5)
- [Source/reference]: [Why it matters]

---
[Quality note if low-signal]
```

### MVP Constraints (Enforce)
- NO metadata beyond generation timestamp
- NO scheduling info, no "next digest" messages, no deadlines
- NO feedback fields (Phase 2+)
- NO complex nested structures
- Just: insights + anti-patterns + actions + resources

### Rationale
1. **Markdown**: Portable, version-controllable, plain text readable
2. **Date-stamped**: Enables archival in `digests/{YYYY}/{MM}/`
3. **Minimal schema**: MVP output is clean, focused, fast to parse/validate
4. **Evidence inline**: Users verify insights immediately

---

## 4. Quality Rubric for MVP (Measurable)

### Decision
Evaluate each candidate insight on this rubric:

| Dimension | Score 0 (reject) | Score 1 | Score 2 (include) |
|-----------|---|---|---|
| **Novelty** | Known/obvious | Somewhat new | New + non-obvious pattern |
| **Evidence** | None | Mentioned but not cited | Direct quote from content |
| **Specificity** | Generic/broad | Somewhat specific | Concrete + actionable |
| **Actionability** | Observation only | Implies action | Clear next step |

**Inclusion rule**: Insight must score "2" on AT LEAST 3 of 4 dimensions.

**No padding rule**: If only 1 strong insight available → output 1, not 3.

Quality warning if low-signal:
```
⚠️ Low-signal content — insights below represent the best available material
```

### Rationale
1. **Measurable**: Team can test consistency against rubric
2. **Prevents padding**: Objective criteria, not subjective
3. **Users trust it**: Transparent scoring, can review quality
4. **Implementable**: Skill can evaluate using the rubric

---

## 5. Technology Stack (MVP)

| Component | Technology | Note |
|-----------|-----------|------|
| Runtime | Claude Code skill | Native, no setup needed |
| Input | Text snippets only (no URLs, no web fetching) | User pastes 3-5 snippets directly |
| Processing | Claude's reasoning (pattern recognition, synthesis) | No external APIs or ML models |
| Output | Markdown files, date-stamped | `digests/{YYYY}/{MM}/digest-...md` |
| Storage | File system (local files) | No database, no external storage |
| Testing | Manual invocation + output validation | Rapid iteration cycle |

**What's NOT in MVP**: MCP, subagents, APIs, persistence, databases, scheduling, external integrations

---

## 6. Known Risks & Mitigations (MVP)

| Risk | Mitigation |
|------|-----------|
| Low-quality insights from weak input | User responsible for content curation; quality rubric filters weak insights |
| Insights lack evidence | Require direct quotes from content; reject unsourced claims |
| Generic/obvious output | Rubric requires "non-obvious"; test with sample content + quality scoring |
| User dissatisfaction | Focus on quality over quantity; get real feedback from beta users |
| Token limits on long content | Limit input to 3-5 snippets of 100-500 words each; clear guidance in docs |

---

## 7. Summary: MVP Decisions

| Decision | MVP | Rationale |
|----------|-----|-----------|
| Input source | Manual text snippets only | Prove quality first, no infrastructure needed |
| Infrastructure | None (single Claude Code skill) | Minimum viable, fast iteration |
| Persistence | No state files | Simplify MVP scope |
| Feedback | No `/rate-digest` command | Defer to Phase 3 after MVP validation |
| Output schema | Minimal (insights, anti-patterns, actions, resources) | Clean, focused MVP |
| Tech stack | Claude Code skill only | No MCP, APIs, or external dependencies |
| Counts | Exact (1-3, 2-4, 1-3, 3-5) or best-available with warning | Prevent padding, maintain quality |

---

## Final Notes (MVP Only)

1. **Text-only input** — resolves the URL/fetching contradiction
2. **Exact counts** — prevent padding; low-signal runs output best-available with warning
3. **Quality rubric** — enables measurable testing via benchmark
4. **Single skill** — no subagents, no external APIs
5. **Fast timeline** — 1-2 weeks to working MVP

---

# PART B: FUTURE ARCHITECTURE (Phase 2+)

**Note**: This section is for reference only. MVP implementation should ignore everything in Part B.

## 1. Phased Roadmap (Phase 2+)

### Phase 2 — Autonomous Discovery
**Adds**: Web search + YouTube + Twitter API (via MCP)
**Uses**: Subagents for parallel retrieval, semantic deduplication
**Removes**: Manual content curation requirement
**Timeline**: 2-3 weeks after Phase 1 validation
**Success**: Autonomous digests match MVP quality

### Phase 3 — Learning & Personalization
**Adds**: `/rate-digest` feedback, persistent state (channels, feedback, source weights)
**Behavior**: Source prioritization adapts to user preferences
**Timeline**: 2 weeks after Phase 2
**Success**: User's digests improve over time based on feedback

### Phase 4+ — Automation & Scale
**Adds**: Scheduled daily execution, Notion export, multi-topic digests, team sharing, historical trends
**Timeline**: After Phase 3 stability
**Success**: Fully automated daily intelligence delivery

---

**Implementers**: Focus on Part A only. Part B exists for future planning, not MVP.