# your-daily-brief Development Guidelines

Last updated: 2026-03-21

## Technologies

- **Runtime**: Claude Code Skill
- **Discovery**: Parallel subagents via MCP tools (`web_search`, `fetch`)
- **Processing**: Claude's native reasoning
- **Output**: Markdown files (date-stamped, `digests/{YYYY}/{MM}/`)
- **Storage**: File system only (local files)
- **Testing**: Manual invocation (snippets mode) + `/validate-digest`

## Project Structure

```text
.claude/
  ├── commands/                        # Slash commands (/validate-digest, /speckit.*)
  └── skills/
      └── daily-digest/
          ├── daily-digest.md          # Orchestrator skill
          ├── agents/
          │   ├── web-discovery-agent.md
          │   ├── video-discovery-agent.md
          │   └── social-discovery-agent.md
          ├── scripts/
          │   ├── check_runtime.py     # Preflight checks
          │   ├── validate_input.py    # Input validation
          │   ├── build_path.py        # Output path generation
          │   └── write_digest.py      # File writing
          └── resources/
              ├── credibility-rules.md
              ├── freshness-policy.md
              ├── quality-rubric.md
              └── digest-template.md

digests/
  └── {YYYY}/{MM}/                     # Generated digest output

specs/
  └── daily-digest/        # Specification, contracts, benchmark
```

## Skill

| Skill | Location | Description |
|-------|----------|-------------|
| `daily-digest` | `.claude/skills/daily-digest/daily-digest.md` | Autonomous discovery via parallel agents. Snippets accepted for testing only. |

## Implementation Style

- **Single skill** — all execution logic in `daily-digest.md`
- **Agents as skills** — each discovery agent is a separate skill file under `agents/`
- **Reference material** — rubrics, templates, policies live in `resources/`, not inline
- **Python utility scripts** — I/O only (`scripts/`); no business logic
- **No build cycle** — edit prompt, save, test immediately

## Key Constraints

- Autonomous discovery by default; snippets mode for testing only
- Exact counts: 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
- Quality rubric: novelty, evidence, specificity, actionability (score 2 on ≥3 dimensions)
- All insights must include a direct quote as evidence
- No padding: output best available material, add quality warning if below minimum
- Python stdlib only — no third-party packages

## Runtime Requirements

| Dependency | Requirement |
|---|---|
| Python | ≥ 3.8, stdlib only |
| `web_search` MCP | Must be active in Claude Code session |
| `fetch` MCP | Must be active in Claude Code session |
| `digests/` | Must be writable |

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
