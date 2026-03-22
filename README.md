# your-daily-brief

A Claude Code skill that autonomously generates high-signal daily intelligence digests on any topic. Discovers content across web, YouTube, and Twitter/X, then synthesises non-obvious insights, anti-patterns, and actionable experiments — saving the output as a date-stamped markdown file.

## Usage

```
/daily-digest <topic>
```

Default topic: **Claude Code**

Runs autonomous discovery via parallel subagents. Optionally supply URLs to supplement what the skill finds on its own.

## Output

Each run produces a digest at `digests/{YYYY}/{MM}/{date}-{topic}.md` containing:

- **Key Insights** — non-obvious patterns observed across advanced practitioners (1–3)
- **Anti-patterns** — incorrect or inefficient practices to avoid (2–4)
- **Actions to Try** — concrete experiments completable in 30 min–3 hours (1–3)
- **Top Resources** — highest-signal sources with rationale (3–5)

## Requirements

| Dependency | Requirement |
|---|---|
| Python | ≥ 3.8, stdlib only |
| `web_search` MCP | Must be active in Claude Code session |
| `fetch` MCP | Must be active in Claude Code session |
| `digests/` directory | Must be writable |

## Project Structure

```
.claude/skills/daily-digest/
  ├── daily-digest.md          # Orchestrator skill
  ├── agents/                  # Parallel discovery subagents
  │   ├── web-discovery-agent.md
  │   ├── video-discovery-agent.md
  │   └── social-discovery-agent.md
  ├── scripts/                 # Python I/O utilities
  │   ├── check_runtime.py
  │   ├── validate_input.py
  │   ├── build_path.py
  │   └── write_digest.py
  └── resources/               # Rubrics, policies, templates
      ├── credibility-rules.md
      ├── freshness-policy.md
      ├── quality-rubric.md
      └── digest-template.md

digests/{YYYY}/{MM}/           # Generated digest output
specs/daily-digest/            # Specification and benchmark artifacts
```

## Quality Bar

Content is scored on novelty, evidence, specificity, and actionability. Items must score ≥ 2 on at least 3 dimensions to be included. All insights require a direct quote as evidence. Low-signal days surface the best available content with a visible warning rather than padding with weak material.

## Validation

```
/validate-digest
```
