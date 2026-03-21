# Contract: Daily Digest Output (MVP)

**Type**: User-Facing Output
**Version**: 1.0 (MVP)
**Date**: 2026-03-21

---

## Overview

The daily digest is output as a **date-stamped markdown file** with a minimal, clean structure. User runs `/daily-digest <topic> [text snippets...]` and receives a markdown file with extracted insights, anti-patterns, actions, and supporting references.

---

## File Format

**Filename Pattern**: `digest-{YYYY-MM-DD}-{topic-slug}.md`

**Location**: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md`

Example: `digests/2026/03/digest-2026-03-21-claude-code.md`

---

## Markdown Schema (MVP)

```markdown
# Daily Digest — {Topic}

Generated: {YYYY-MM-DD HH:MM}

## Key Insights (1-3)

### Insight 1: [Title]
[Description answering: what/why/how]

Evidence: "[Direct quote from provided content]"

### Insight 2: [Title]
[Description]

Evidence: "[Direct quote]"

## Anti-patterns (2-4)

- **[Name]**: [Why to avoid]. Evidence: [quote or attribution].

- **[Name]**: [Why to avoid]. Evidence: [quote or attribution].

## Actions to Try (1-3)

### 1. [Action Title]
Effort: low/medium/high
Time: [X minutes]
Steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected outcome: [Measurable result]

### 2. [Action Title]
...

## Resources (3-5)

- **[Resource title or source]**: [Why it matters from the content]

---

[Quality notes if applicable: "Low-signal content — insights below represent the best available material"]
```

---

## Count Rules (Explicit)

**For high-signal content (typical)**:
- Insights: exactly 1-3 (1 minimum, 3 maximum)
- Anti-patterns: exactly 2-4 (2 minimum, 4 maximum)
- Actions: exactly 1-3 (1 minimum, 3 maximum)
- Resources: exactly 3-5 (3 minimum, 5 maximum)

**For low-signal content (exception)**:
- Output best-available insights (may be fewer than 1-3 minimum)
- Include visible quality warning: "Low-signal content — insights below represent the best available material"
- **This is NOT a failure** — it's the correct behavior (honesty over padding)

---

## Field Definitions

### Key Insights Section
- **Count**: 1-3 (target for high-signal; best-available for low-signal)
- **Title**: 5-10 words, descriptive
- **Description**: 2-3 sentences, must answer ALL THREE of: what/why/how
- **Evidence**: Direct quote from provided content (required)

### Anti-patterns Section
- **Count**: 2-4 (target for high-signal; best-available for low-signal)
- **Name**: Descriptive title of the anti-pattern
- **Why to avoid**: 1-2 sentences explaining consequences
- **Evidence**: Direct reference or quote from provided content

### Actions to Try Section
- **Count**: 1-3 (target for high-signal; best-available for low-signal)
- **Title**: Concrete action title (imperative verb)
- **Effort**: low / medium / high (required)
- **Time**: Specific (e.g., "45 minutes", "2 hours"), not range
- **Steps**: Numbered, concrete, executable independently
- **Expected outcome**: Measurable, specific result

### Resources Section
- **Count**: 3-5 (target for high-signal; best-available for low-signal)
- **Title**: Source name or content snippet from provided content
- **Why it matters**: 1-2 sentences explaining relevance to the insight

### Quality Notes Section
- **When included**: If digest contains low-signal content or best-available is below target counts
- **Format**: Single line, prefixed with warning emoji
- **Example**: "⚠️ Low-signal content — insights below represent the best available material"
- **Effect**: Alerts user that this digest is lower quality; does NOT prevent publication

---

## MVP Constraints

- **NO metadata**: No "retrieval stats", "content sources", "next digest", "feedback deadline"
- **NO scheduling info**: No timestamps other than generation time
- **NO feedback fields**: No "useful" / "not useful" markers
- **NO complex structure**: Simple sections, flat hierarchy, no nesting

---

## Validation Rules

### Content Validation (All Runs)

- All insights must have evidence (direct quote or attribution)
- All anti-patterns must cite why to avoid
- All actions must have effort level and time estimate
- All resources must explain why they matter
- All content must be non-obvious, specific, and actionable (no generic statements)

### Count Validation

**For Normal/High-Signal Runs**:
- Insight counts MUST be exactly 1-3
- Anti-pattern counts MUST be exactly 2-4
- Action counts MUST be exactly 1-3
- Resource counts MUST be exactly 3-5

**For Low-Signal Exception Runs**:
- Best-available content in ALL sections (may be fewer than normal minimums)
- Insights may be 0-3 (not required to meet 1-3 minimum)
- Anti-patterns may be 0-4 (not required to meet 2-4 minimum)
- Actions may be 0-3 (not required to meet 1-3 minimum)
- Resources may be 0-5 (not required to meet 3-5 minimum)
- **Quality warning REQUIRED**: `⚠️ Low-signal content — insights below represent the best available material`

---

## Quality Gate

**Normal/High-Signal Run** — Output is valid MVP if:
- [ ] Exactly 1-3 insights present
- [ ] Exactly 2-4 anti-patterns present
- [ ] Exactly 1-3 actions present
- [ ] Exactly 3-5 resources present
- [ ] All insights have evidence
- [ ] All actions have effort, time, steps, outcome
- [ ] No metadata, scheduling, or feedback fields
- [ ] Markdown is clean and readable
- [ ] NO quality warning (content meets quality bar)

**Low-Signal Exception Run** — Output is valid MVP if:
- [ ] Best-available content present in each section (no minimums enforced)
- [ ] May have 0-3 insights (no 1-3 minimum required)
- [ ] May have 0-4 anti-patterns (no 2-4 minimum required)
- [ ] May have 0-3 actions (no 1-3 minimum required)
- [ ] May have 0-5 resources (no 3-5 minimum required)
- [ ] All present insights have evidence
- [ ] All present actions have effort, time, steps, outcome
- [ ] No metadata, scheduling, or feedback fields
- [ ] Markdown is clean and readable
- [ ] Quality warning PRESENT and visible: `⚠️ Low-signal content — insights below represent the best available material`
- [ ] **NOTE: This is NOT a failure** — honesty over padding is the correct behavior

---

## Examples

See `benchmark.md` for sample inputs and expected outputs.
