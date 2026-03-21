# Digest Output Template

```markdown
# Daily Digest — {Topic}

Generated: {YYYY-MM-DD HH:MM}
Discovery: {complete | partial — X unavailable | timeout — partial results used | manual}

## Key Insights (1–3)

### {Title}
{Description}

**Source**: {Publication name}
**Evidence**: "{Quote}"

## Anti-patterns (2–4)

- **{Name}**: {Evidence quote}. ({Source})

## Actions to Try (1–3)

### {Title}
- Effort: {low | medium | high}
- Time: {specific duration}
- Steps: [numbered]
- Expected outcome: {measurable result}

## Resources (3–5)

- **{Title}**: {URL} — {Why it matters}

---
⚠️ Low-signal content — insights below represent the best available material
[include only when a section falls below its minimum]
```

## Field Rules

- **Title** (Insights, Actions): 5–10 words
- **Description** (Insights): 2–3 sentences covering what / why / how
- **Evidence**: Direct quote from source content — must appear in `"double quotes"`
- **Anti-pattern evidence**: Full sentence quote from provided content
- **Resource title**: Direct quote or literal phrase from source content (not paraphrased)
- **Action Steps**: Numbered list
- **Discovery line**: Use `manual` when snippets were provided; otherwise use completion status from agents
