# Data Model: SignalFlow MVP

**Phase**: Phase 1 (MVP)
**Date**: 2026-03-21
**Scope**: MVP only (no future entities)

---

## Core Entities

### Insight

**Purpose**: Non-obvious pattern or technique extracted from provided text snippets.

```typescript
interface Insight {
  id: string
  title: string                 // 5-10 words
  description: string           // 2-3 sentences, answers what/why/how
  evidence: string              // Direct quote from provided content
  novelty_score: number         // 0-2 (0=low, 1=medium, 2=high)
  evidence_score: number        // 0-2 (0=none, 1=partial, 2=direct quote)
  specificity_score: number     // 0-2 (0=generic, 1=somewhat specific, 2=concrete)
  actionability_score: number   // 0-2 (0=observation only, 1=implies action, 2=clear next step)
  topic: string
  created_at: string            // ISO 8601
}
```

**Validation**:
- `title`: non-empty, 5-10 words
- `description`: non-empty, 2-3 sentences, must answer all three: what/why/how
- `evidence`: direct quote from provided content (required)
- All scores: range [0, 2] (0=low quality, 1=medium, 2=high quality)
- **Inclusion rule**: Score must be 2 on at least 3 of 4 dimensions

---

### Anti-pattern

**Purpose**: Inefficient or incorrect practice to avoid.

```typescript
interface AntiPattern {
  id: string
  name: string                  // Descriptive title
  description: string           // Why to avoid (1-2 sentences)
  evidence: string              // Quote or attribution from content
  topic: string
  created_at: string
}
```

**Validation**:
- `name`: non-empty, descriptive
- `description`: non-empty, explains consequences
- `evidence`: source attribution required

---

### Action

**Purpose**: Concrete, testable experiment derived from insights.

```typescript
interface Action {
  id: string
  title: string                 // Imperative verb, concrete
  effort: 'low' | 'medium' | 'high'
  time_required: string         // Specific: "45 minutes", "2 hours"
  steps: string[]               // Numbered, concrete, independent
  expected_outcome: string      // Measurable result
  related_insights: string[]    // IDs of insights this action stems from
  topic: string
  created_at: string
}
```

**Validation**:
- `title`: non-empty, action-oriented
- `effort`: one of enum values
- `time_required`: specific (not range), parseable
- `steps`: non-empty array, each step concrete
- `expected_outcome`: measurable, non-empty

---

### Resource

**Purpose**: Supporting reference from provided content.

```typescript
interface Resource {
  id: string
  title: string                 // Source name or content snippet
  why_it_matters: string        // 1-2 sentences, specific to content
  topic: string
  created_at: string
}
```

**Validation**:
- `title`: non-empty
- `why_it_matters`: non-empty, specific to why it's relevant

---

### DigestRun

**Purpose**: Metadata for one digest execution.

```typescript
interface DigestRun {
  id: string                    // e.g., "2026-03-21-claude-code"
  topic: string
  start_time: string            // ISO 8601
  end_time: string              // ISO 8601
  status: 'completed' | 'failed'
  insights: Insight[]           // Exactly 1-3
  anti_patterns: AntiPattern[]  // Exactly 2-4
  actions: Action[]             // Exactly 1-3
  resources: Resource[]         // Exactly 3-5
  quality_warning?: string      // Only if low-signal
  output_file: string           // Path to generated digest
}
```

**Validation**:
- Exact counts: 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
- If counts not met: output best available with quality warning

---

## State Flow

```
DigestRun starts
  |
  v
Parse user input (topic + text snippets)
  |
  v
Filter: evaluate each candidate insight against quality rubric
  |
  v
{ Insight passes: add to output, Insight fails: discard }
  |
  v
Extract anti-patterns, actions, resources
  |
  v
Assemble markdown file
  |
  v
DigestRun completes (write to digests/{YYYY}/{MM}/)
```

---

## Storage Model (MVP)

**Input**: Text snippets passed via command (not persisted)
**Output**: Markdown file in `digests/{YYYY}/{MM}/`
**State**: None persisted between runs
**Database**: None

---

## Key Business Rules (MVP)

1. **Exact counts**: 1-3 insights (not "up to 5")
2. **No padding**: Better to output 1 strong insight than 3 weak ones
3. **Evidence required**: All insights must cite provided content
4. **Quality rubric**: Use 4-dimension rubric (novelty, evidence, specificity, actionability)
5. **Clear quality gate**: Low-signal digests include warning, don't pad output
6. **No cross-digest deduplication**: Each run is independent
7. **No persistence**: All input is ephemeral

---

## What's NOT in MVP

- **Content entity**: No multi-source content modeling, deduplication, or metadata
- **YouTube Channel**: No channel management
- **Feedback entity**: No feedback capture
- **Source weighting**: No learning from feedback
- **Retrieval stats**: No metadata about content discovery
- **Broken URL handling**: No URL handling at all
- **Cross-source synthesis**: Single-run context only

These are all Phase 2+ features.

---

## Validation at Output

Before writing digest file, validate:
- [ ] Insight count: exactly 1-3
- [ ] Anti-pattern count: exactly 2-4
- [ ] Action count: exactly 1-3
- [ ] Resource count: exactly 3-5
- [ ] All insights have evidence
- [ ] All actions have effort, time, steps, outcome
- [ ] Markdown is valid and readable

If any validation fails: output what qualifies + quality warning.

---

## Example: Valid MVP Digest Run

```
DigestRun {
  id: "2026-03-21-claude-code"
  topic: "Claude Code"
  insights: [
    Insight { title: "...", evidence: "[quote]", ...scores... },
    Insight { title: "...", evidence: "[quote]", ...scores... },
    Insight { title: "...", evidence: "[quote]", ...scores... }
  ]
  anti_patterns: [
    AntiPattern { name: "...", evidence: "[quote]" },
    AntiPattern { name: "...", evidence: "[quote]" },
    AntiPattern { name: "...", evidence: "[quote]" },
    AntiPattern { name: "...", evidence: "[quote]" }
  ]
  actions: [
    Action { title: "...", effort: "medium", time_required: "1 hour", steps: [...], outcome: "..." },
    Action { title: "...", effort: "low", time_required: "30 minutes", steps: [...], outcome: "..." }
  ]
  resources: [
    Resource { title: "...", why_it_matters: "..." },
    Resource { title: "...", why_it_matters: "..." },
    Resource { title: "...", why_it_matters: "..." },
    Resource { title: "...", why_it_matters: "..." },
    Resource { title: "...", why_it_matters: "..." }
  ]
  output_file: "digests/2026/03/digest-2026-03-21-claude-code.md"
}
```

All counts are exact, all required fields present, no padding.
