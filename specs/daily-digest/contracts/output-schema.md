# Output Contract: Daily Digest Skill

**Output**: Markdown digest file (success case) OR fallback message (failure case)

---

## Success Case: Digest File Created

### File Path
```
digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md
```

**Components**:
- `{YYYY}`: Year (e.g., 2026)
- `{MM}`: Month zero-padded (e.g., 03)
- `{YYYY-MM-DD}`: ISO8601 date when digest was generated
- `{topic-slug}`: Topic converted to slug (lowercase, hyphens instead of spaces)

**Examples**:
- `digests/2026/03/digest-2026-03-21-claude-code.md`
- `digests/2026/03/digest-2026-03-21-agentic-workflows.md`
- `digests/2026/03/digest-2026-03-21-autonomous-agents.md`

---

## Markdown Structure (Success)

### Header
```markdown
# Daily Digest — {TOPIC}

Generated: {YYYY-MM-DD HH:MM}
Discovery: {status}
```

## Key Insights (1–3)
```markdown
### Insight Title

{Description: what / why / how}

**Source**: {Source name/publication}
**Evidence**: "{direct quote from source}"
```

## Anti-patterns (2–4)
```markdown
- {Pattern Name}: {Why to avoid} ({Source})
```

## Actions to Try (1–3)
```markdown
### Action Title

- Effort: low | medium | high
- Time: {specific duration}
- Steps: [numbered]
- Expected outcome: {measurable result}
```

## Resources (3–5)
```markdown
- **{Title}**: {URL} — {Why it matters}
```

### Quality Warning (if applicable)
```markdown
---
⚠️ Low-signal content — insights below represent the best available material
[include only when a section falls below its minimum]
```

---

## Failure Case: Fallback Message (No File Created)

### Scenario: Zero Credible Sources Found

**Output Message** (displayed to user, no file created):
```
No relevant content discovered for topic '{topic}'.

Try providing hints to guide discovery:
/daily-digest {topic} --hints [youtube_channels or @twitter_users]

Try providing content manually (test mode):
/daily-digest "{topic}" "[snippet1]" "[snippet2]"
```

### Scenario: All Discovery Sources Failed/Timeout

**Output Message**:
```
No relevant content discovered for '{topic}'.

Try providing content manually (test mode):
/daily-digest "{topic}" "[snippet1]" "[snippet2]"
```

---

## Validation Rules (Output)

| Condition | Output |
|-----------|--------|
| ≥3 credible sources found | Generate digest file (no warning) |
| 1-2 credible sources found | Generate digest file + quality warning |
| 0 credible sources found | Fallback message (no file) |
| Discovery timeout (>45s) | Use partial results + timeout warning in digest |
| All discovery agents failed | Fallback message (no file) |

---

## File Content Example (Success)

```markdown
# Daily Digest — claude-code

Generated: 2026-03-21 14:30
Discovery: complete

## Key Insights (1–3)

### Subagents Enable Parallel Task Execution

Claude Code can spawn multiple subagents to run discovery tasks in parallel, significantly reducing execution time compared to sequential processing. This approach is particularly effective for multi-source research (web, video, social media).

**Source**: Anthropic Documentation
**Evidence**: "Subagents allow parallelized execution of independent research tasks, reducing overall latency by ~50%"

### Parallel Discovery Improves Comprehensiveness

Running web, video, and social media discovery simultaneously ensures coverage across all relevant content types within a tight latency budget (27s end-to-end).

**Source**: @dmarx (Twitter)
**Evidence**: "Parallel agents beat sequential by breadth + speed"

## Anti-patterns (2–4)

- Sequential Discovery: Why to avoid: Exceeds latency budget, misses time-sensitive content (Twitter, breaking news)
- Ignoring Source Credibility: Why to avoid: Dilutes insight quality, amplifies spam/low-signal content

## Actions to Try (1–3)

### Implement Parallel Discovery in Your Skill

- Effort: medium
- Time: 4-6 hours
- Steps:
  1. Define agent spawn interface (topic + hints input)
  2. Implement 3 agents (web, video, social) as independent prompts
  3. Merge results with deduplication logic
  4. Apply quality rubric, output markdown
- Expected outcome: Discovery time reduced from 45s to 27s; improved insight comprehensiveness

## Resources (3–5)

- [Claude Code Subagents Guide](https://anthropic.com/docs/subagents) — How to spawn and coordinate parallel agents
- [Async Patterns in Prompts](https://anthropic.com/docs/async-patterns) — Best practices for parallel execution
- [@dmarx Research Threads](https://twitter.com/dmarx) — Practical examples of agent orchestration

---

⚠️ Low-signal content — insights below represent the best available material
Discovery: partial — social unavailable
```

---

## Output Format Guarantees

| Aspect | Guarantee |
|--------|-----------|
| **File encoding** | UTF-8 |
| **Line endings** | Unix (LF) |
| **Markdown standard** | GitHub Flavored Markdown (GFM) |
| **Frontmatter** | None (plain markdown only) |
| **Structure** | Header + Insights + Anti-patterns + Actions + Resources + optional warning |
| **Consistency** | Identical to MVP digest format |

---

## Notes

- All timestamps in UTC (ISO8601)
- Direct quotes are required in "Evidence" fields
- Source attribution is mandatory for all insights
- File path is deterministic based on topic + date (enables deduplication of repeated requests)
- Fallback message is user-friendly (no technical error codes, includes recovery suggestions)
