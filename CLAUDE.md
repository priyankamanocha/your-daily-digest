# signalflow Development Guidelines

Auto-generated from MVP spec. Last updated: 2026-03-21

## MVP (Phase 1) Technologies

- **Runtime**: Claude Code Skill (single command)
- **Input**: Text snippets only (no URLs, no web fetching)
- **Processing**: Claude's native reasoning (no external APIs or ML models)
- **Output**: Markdown files (date-stamped)
- **Storage**: File system only (local files)
- **Testing**: Manual invocation + quality rubric validation

## Project Structure (MVP)

```text
.claude/commands/
  └── daily-digest.md          # Single skill (entire MVP implementation)

digests/
  └── {YYYY}/{MM}/             # Generated digest output

specs/main/                     # Documentation
  ├── spec.md                   # MVP requirements (source of truth)
  ├── plan.md                   # Implementation plan
  ├── research.md (Part A)      # MVP technical decisions
  ├── benchmark.md              # Sample inputs + expected outputs
  └── data-model.md             # MVP entities (simplified)
```

## MVP Command

```bash
/daily-digest "<topic>" "[text snippet 1]" "[text snippet 2]" "[text snippet 3]"
```

## Implementation Style

- **Single skill** in `.claude/commands/daily-digest.md` (all logic in one prompt)
- **No external code files** — everything in Claude Code
- **No build cycle** — edit prompt, save, test immediately
- **No dependencies** — no MCP, no subagents, no APIs in MVP
- **Output**: Markdown files in `digests/{YYYY}/{MM}/`

## Key Constraints (MVP)

- Text snippets only (user provides content directly)
- Exact counts: 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
- Quality rubric: novelty, evidence, specificity, actionability
- All insights must cite evidence from provided content
- No padding: output best available insights, don't force counts

## Future (Phase 2+)

- Phase 2: Autonomous discovery (MCP + subagents)
- Phase 3: Feedback & learning
- Phase 4+: Automation & scale

See `specs/main/research.md` Part B for future design.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
