# /daily-digest: Generate Daily Intelligence Digest

## Command

`/daily-digest <topic> "[text snippet 1]" "[text snippet 2]" "[text snippet 3...]"`

---

## Runtime Execution

### 1. Parse and Validate Input

- Extract topic (first argument): non-empty, alphanumeric + spaces, max 100 chars
- Extract snippets (quoted arguments): 3-5 required, each 100-500 words
- Return error if validation fails with usage instructions

### 2. Extract Insights (1-3)

For each snippet, identify candidates and score on 4 dimensions:
- **Novelty**: 0=known, 1=somewhat new, 2=new+non-obvious
- **Evidence**: 0=none, 1=mentioned, 2=direct quote
- **Specificity**: 0=generic, 1=somewhat, 2=concrete+actionable
- **Actionability**: 0=observation, 1=implies action, 2=clear next step

**Rule**: Include insight ONLY if scores 2 on ≥3 dimensions.

For each kept insight:
- Title (5-10 words, enforced)
- Description (2-3 sentences: what/why/how)
- Evidence (direct quote from content)

### 3. Extract Anti-patterns (2-4)

Identify 2-4 practices to avoid:
- Name: descriptive title
- Evidence: FULL SENTENCE QUOTE from provided content (not fragments)

### 4. Generate Actions (1-3)

For each insight, create concrete experiments:
- Title: imperative verb
- Effort: low / medium / high
- Time: specific duration (e.g., "45 minutes", not "1-2 hours")
- Steps: numbered, concrete, independent
- Expected outcome: measurable result

### 5. Select Resources (3-5)

Extract supporting references directly from provided content:
- **Title**: DIRECT QUOTE OR LITERAL PHRASE from snippets (5-20 words)
- **Why it matters**: 1-2 sentences explaining relevance to extracted insights

**Rule**: Every resource title must be directly traceable to provided text. No synthesis or thematic summaries.

### 6. Check Signal Quality

Count final items:
- Insights: 1-3?
- Anti-patterns: 2-4?
- Actions: 1-3?
- Resources: 3-5?

If any below minimum → prepare quality warning: `⚠️ Low-signal content — insights below represent the best available material`

### 7. Generate Markdown Output

Build file path: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md`

Output format:
```markdown
# Daily Digest — {Topic}

Generated: {YYYY-MM-DD HH:MM}

## Key Insights (1-3)

### {Title}
{Description}

Evidence: "{Quote}"

## Anti-patterns (2-4)

- **{Name}**: {Evidence quote}.

## Actions to Try (1-3)

### {Title}
- Effort: {level}
- Time: {duration}
- Steps: [numbered]
- Expected outcome: {result}

## Resources (3-5)

- **{Direct quote or literal phrase from content}**: {Why it matters}

---

[If low-signal: ⚠️ Low-signal content — insights below represent the best available material]
```

Timestamp: Generated current time at execution.

### 8. Write to Disk

Create directories if needed, write markdown file, return success or error.

---

## Reference: Quality Rubric

**Insight Inclusion Rule**: Must score 2 (high) on ≥3 of 4 dimensions:

| Dimension | 0 (Reject) | 1 (Weak) | 2 (Include) |
|-----------|-----------|---------|-----------|
| Novelty | Known/obvious | Somewhat new | New + non-obvious |
| Evidence | None | Mentioned | Direct quote |
| Specificity | Generic | Somewhat | Concrete |
| Actionability | Observation | Implies action | Clear next step |

**Resource Anchoring**: Each resource title must be a direct quote or literal phrase from provided snippets. No paraphrasing or synthesis.

**Anti-pattern Evidence**: Use full-sentence quotes from provided content, not fragments.

**Low-Signal Rule**: If any section below minimum, output best-available + quality warning (not a failure).

---

## Example Output

**Input**:
```
/daily-digest claude-code "[snippet about subagents...]" "[snippet about batching...]" "[snippet about independent scopes...]"
```

**Output**:
```
✅ Digest created: digests/2026/03/digest-2026-03-21-claude-code.md
```

**Digest Contents** (see `digests/2026/03/digest-2026-03-21-claude-code.md`):
- 2 insights with evidence quotes
- 2 anti-patterns with full-quote evidence
- 2 actions with effort/time/steps/outcome
- 5 resources with direct-quote titles

All content grounded in provided snippets.
