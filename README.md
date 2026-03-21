# signalflow

A Claude Code skill that autonomously discovers and synthesises high-quality intelligence digests on any topic. Parallel agents search the web, video, and social sources — then score, deduplicate, and assemble insights, anti-patterns, actions, and resources that meet a strict quality rubric.

## Usage

```
/daily-digest <topic>
/daily-digest <topic> --hints <channel1,@handle2>
/daily-digest <topic> "snippet 1" "snippet 2"   # test mode — no MCP tools required
```

**Examples**:
```
/daily-digest claude-code
/daily-digest ai-agents --hints 3blue1brown,@karpathy
/daily-digest "prompt engineering" "Structured outputs reduce hallucination by 40%..."
```

Output is written to `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic}.md`.

## Output Format

Each digest contains:

| Section | Count | Rules |
|---------|-------|-------|
| Key Insights | 1–3 | Each must include a direct quote as evidence |
| Anti-patterns | 2–4 | Practices to avoid, evidenced from credible sources |
| Actions to Try | 1–3 | Concrete experiments derived from insights |
| Resources | 3–5 | Credible sources first |

If any section falls below its minimum, a `⚠️ Low-signal content` warning is appended. Padding is never used.

## Requirements

| Dependency | Requirement |
|---|---|
| Python | ≥ 3.8, stdlib only |
| `web_search` MCP | Must be active in Claude Code session |
| `fetch` MCP | Must be active in Claude Code session |
| `digests/` | Must be writable (created automatically) |

## Validation

```
/validate-digest
```

Runs the skill against benchmark inputs and checks the output against the format contract and quality rubric. Produces a structured report at `specs/daily-digest/automated-validation-report.md`.

## Project Structure

```text
.claude/
└── skills/
    └── daily-digest/
        ├── daily-digest.md          # Orchestrator skill
        ├── agents/                  # Parallel discovery agents
        │   ├── web-discovery-agent.md
        │   ├── video-discovery-agent.md
        │   └── social-discovery-agent.md
        ├── scripts/                 # Python I/O utilities (stdlib only)
        │   ├── check_runtime.py
        │   ├── validate_input.py
        │   ├── build_path.py
        │   └── write_digest.py
        └── resources/               # Rubrics, policies, templates
            ├── credibility-rules.md
            ├── freshness-policy.md
            ├── quality-rubric.md
            └── digest-template.md

digests/                             # Generated output (gitignored)
└── {YYYY}/{MM}/

specs/                               # Feature specifications and plans
```

## Development

No build step. Edit a skill file, save, invoke — changes take effect immediately.

- **Edit skill**: modify `.claude/skills/daily-digest/daily-digest.md` or files in `resources/`
- **Test (autonomous)**: `/daily-digest <topic>` — requires MCP tools
- **Test (manual)**: `/daily-digest <topic> "snippet1" "snippet2"` — no MCP tools needed
- **Validate**: `/validate-digest`
