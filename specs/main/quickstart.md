# QuickStart: SignalFlow MVP

**Date**: 2026-03-21
**Scope**: MVP Phase 1 (text input only, no URLs, no web fetching)

---

## For Users: Generate Your First Digest

### Step 1: Gather Text Content

Manually collect 3-5 text snippets (100-500 words each) from any source about a topic you want to explore.

Sources can be:
- Blog post excerpts
- Twitter threads (copy full text)
- Code examples with descriptions
- Documentation sections
- Technical articles

**Important**: You provide the TEXT directly. System does NOT fetch URLs.

### Step 2: Run the Digest Command

Open Claude Code and run:

```bash
/daily-digest "topic-name" "Snippet 1: [paste text here]" "Snippet 2: [paste text here]" "Snippet 3: [paste text here]"
```

Example:

```bash
/daily-digest claude-code "Subagents enable parallel execution of independent tasks..." "I used subagents for parallel content retrieval..." "Subagents with shared state cause bottlenecks..."
```

### Step 3: Wait for Results

System processes your text and outputs a markdown file in < 3 minutes.

### Step 4: Read Your Digest

File location:
```
digests/2026/03/digest-2026-03-21-claude-code.md
```

Contents:
- **Key Insights (1-3)**: Non-obvious patterns backed by evidence from your content
- **Anti-patterns (2-4)**: Mistakes to avoid with explanations
- **Actions to Try (1-3)**: Concrete, testable experiments
- **Resources (3-5)**: Supporting materials from your content

### Step 5: Iterate

Try with different content and topics. Observe which insights are most useful.

---

## For Developers: MVP Overview

### Project Structure

```
signalflow/
├── .claude/commands/
│   └── daily-digest.md               # Single MVP skill
├── digests/                          # Generated output (created by skill)
│   └── {YYYY}/{MM}/
│       └── digest-{date}-{topic}.md
└── specs/main/                       # Documentation
    ├── spec.md                       # MVP requirements (source of truth)
    ├── plan.md                       # Implementation plan
    ├── research.md                   # Technical decisions
    ├── benchmark.md                  # Sample inputs + expected outputs
    ├── data-model.md                 # MVP entities (simplified)
    └── contracts/
        ├── digest-output-schema.md   # MVP output format
        └── feedback-input-schema.md  # Phase 3 feature (not MVP)
```

### MVP Scope (EXACT)

**Input**: Text snippets only (3-5 snippets, 100-500 words each, pasted directly)
**Output**: Markdown file with 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
**No external dependencies**: No MCP, APIs, web fetching, subagents, persistence
**Timeline**: 1-2 weeks

### Core MVP Workflow

```
User pastes text snippets
      |
      v
/daily-digest skill reads text
      |
      v
Filter: remove low-signal content
      |
      v
Synthesize: extract insights using quality rubric
      |
      v
Generate: anti-patterns, actions, resources
      |
      v
Assemble: markdown file
      |
      v
Output: digests/{YYYY}/{MM}/digest-{date}-{topic}.md
```

### Quality Rubric (MVP)

Evaluate each candidate insight on 4 dimensions:

| Dimension | Low (reject) | High (include) |
|-----------|---|---|
| Novelty | Known/obvious | New + non-obvious |
| Evidence | None | Direct quote from content |
| Specificity | Generic | Concrete + actionable |
| Actionability | Observation only | Clear next step |

**Inclusion rule**: Score "High" on at least 3 of 4 to include.

### Testing MVP Quality

1. Run `/daily-digest` with sample inputs from `benchmark.md`
2. Compare output against expected quality in `benchmark.md`
3. Evaluate using the quality rubric
4. If output doesn't match: refine skill prompt and retry

### MVP Files to Edit

- `.claude/commands/daily-digest.md` — The skill implementation (all logic lives here)
- `specs/main/spec.md` — Source of truth for MVP requirements
- `specs/main/research.md` (Part A only) — MVP technical decisions

**Do NOT edit during implementation**:
- `specs/main/contracts/feedback-input-schema.md` (Phase 3 only)
- Any Phase 2+ content in `research.md` Part B
- Post-MVP features in `plan.md`

### Iteration Cycle

1. **Edit** `.claude/commands/daily-digest.md`
2. **Run** `/daily-digest <topic> [text snippets...]`
3. **Evaluate** output against quality rubric
4. **Refine** prompt if needed
5. **Repeat**

No build step, no deployment — changes are live immediately.

---

## Key Implementation Constraints

- Text input only (user provides content directly)
- No external APIs or MCP calls
- Output exact counts (1-3 insights, NOT "up to 5")
- All insights must cite evidence from provided content
- No `/rate-digest` command in MVP
- No persistence or state files
- No scheduling or metadata

---

## Testing Against Benchmark

See `benchmark.md` for:
- Sample input sets (realistic technical content)
- Expected quality outputs
- How to evaluate consistency

Use this to validate MVP implementation.

---

## Questions?

- **MVP requirements**: See `spec.md`
- **Technical decisions**: See `research.md` Part A
- **Quality standards**: See `benchmark.md`
- **Output format**: See `contracts/digest-output-schema.md`

**All docs describe MVP only. Phase 2+ content is clearly marked as future.**
