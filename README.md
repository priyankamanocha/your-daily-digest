# your-daily-digest

A Claude Code skill that autonomously discovers and synthesises high-quality intelligence digests on any topic. Parallel agents search the web, video, and social sources — then score, deduplicate, and assemble insights, anti-patterns, actions, and resources that meet a strict quality rubric.

## Skills

| Skill | Invoke | Description |
|-------|--------|-------------|
| `daily-digest` | `/daily-digest <topic>` | Discover and synthesise a digest on any topic |
| `watchlist` | `/watchlist <subcommand>` | Manage a saved topic list and batch-refresh all topics |

## Usage

### daily-digest

```
/daily-digest <topic>
/daily-digest <topic> --hints <channel1,@handle2>
/daily-digest <topic> --since <window>
/daily-digest <topic> --no-diff
/daily-digest <topic> "snippet 1" "snippet 2"   # snippets mode — no MCP tools required
```

**Flags**:

| Flag | Default | Description |
|------|---------|-------------|
| `--hints` | — | Comma-separated YouTube channels or @handles to prioritise |
| `--since` | `1` | Freshness window: number of days, `yesterday`, `last month`, or `feb 2026` |
| `--no-diff` | off | Skip repeat-filtering against the previous digest |

**Examples**:
```
/daily-digest claude-code
/daily-digest ai-agents --hints 3blue1brown,@karpathy
/daily-digest "prompt engineering" --since 7
/daily-digest "machine learning" --since "last month"
/daily-digest "prompt engineering" "Structured outputs reduce hallucination by 40%..."
```

Output is written to `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic}.md`.

### watchlist

```
/watchlist add <topic>       # save a topic
/watchlist remove <topic>    # remove a topic
/watchlist list              # show all saved topics with last digest date
/watchlist refresh           # regenerate digests for all saved topics
/watchlist history <topic>   # show last 3 digests for a topic
```

Watchlist is stored in `.watchlist.json` at repo root (gitignored, user-managed).

### Source filtering (optional)

Create `sources.json` at repo root to allowlist or blocklist domains and handles:

```json
{
  "global": {
    "block": ["spamsite.com", "@noisybot"]
  },
  "topics": {
    "AI safety": {
      "allow": ["alignmentforum.org", "@paulchristiano"],
      "block": ["hypesite.ai"]
    }
  }
}
```

See `sources.json.example` for the full schema. Topic-level rules take precedence over global rules. `sources.json` is gitignored — manage it locally per environment.

## Output Format

Each digest contains:

| Section | Count | Rules |
|---------|-------|-------|
| Key Insights | 1–3 | Each must include a direct quote as evidence |
| Anti-patterns | 2–4 | Practices to avoid, evidenced from credible sources |
| Actions to Try | 1–3 | Concrete experiments derived from insights |
| Resources | 3–5 | Credible sources first |

If any section falls below its minimum, a `⚠️ Low-signal content` warning is appended. Padding is never used. Repeat insights from the previous digest are filtered out automatically (disable with `--no-diff`).

## Requirements

| Dependency | Requirement |
|---|---|
| Python | ≥ 3.8, stdlib only |
| `WebSearch` | Built into Claude Code — no MCP config needed |
| `WebFetch` | Built into Claude Code — no MCP config needed |
| `digests/` | Must be writable (created automatically) |

## Testing & Validation

```bash
# Run automated evals (no MCP tools needed)
PYTHONIOENCODING=utf-8 python .claude/skills/daily-digest/evals/run_evals.py

# Run script unit tests
python -m pytest tests/ -v

# Run full skill validation against benchmark inputs
/validate-digest
```

| Command | What it checks |
|---------|---------------|
| `run_evals.py` | Payload parsing, since_window resolution, error cases, digest structure on existing files |
| `pytest tests/` | Python script I/O (validate_input, build_path, write_digest, etc.) |
| `/validate-digest` | Full skill run against benchmark snippets — structure, counts, evidence, rubric |

Validation report: `specs/daily-digest/automated-validation-report.md`

## Project Structure

```text
.claude/
└── skills/
    ├── daily-digest/
    │   ├── SKILL.md                 # Orchestrator skill
    │   ├── agents/                  # Parallel discovery agents
    │   │   ├── web-discovery-agent.md
    │   │   ├── video-discovery-agent.md
    │   │   └── social-discovery-agent.md
    │   ├── scripts/                 # Python I/O utilities (stdlib only)
    │   │   ├── check_runtime.py
    │   │   ├── validate_input.py
    │   │   ├── build_path.py
    │   │   ├── write_digest.py
    │   │   ├── write_manifest.py
    │   │   ├── diff_digest.py
    │   │   └── load_source_filters.py
    │   ├── resources/               # Rubrics, policies, templates
    │   │   ├── credibility-rules.md
    │   │   ├── freshness-policy.md
    │   │   ├── quality-rubric.md
    │   │   ├── digest-template.md
    │   │   ├── diffing-policy.md
    │   │   ├── invocation-contract.md
    │   │   └── manifest-schema.md
    │   └── evals/                   # Eval sets and runner
    │       ├── run_evals.py
    │       └── sets/
    └── watchlist/
        ├── watchlist.md             # Watchlist skill
        └── scripts/
            ├── read_watchlist.py
            ├── write_watchlist.py
            └── find_digest.py

sources.json                         # Optional: allowlist/blocklist (gitignored)
sources.json.example                 # Example config
digests/                             # Generated output (gitignored)
└── {YYYY}/{MM}/
specs/                               # Feature specifications
tests/                               # Python script unit tests
```

## Development

No build step. Edit a skill file, save, invoke — changes take effect immediately.

- **Edit skill**: modify `.claude/skills/daily-digest/SKILL.md` or files in `resources/`
- **Test (autonomous)**: `/daily-digest <topic>` — requires Claude Code with WebSearch/WebFetch
- **Test (snippets)**: `/daily-digest <topic> "snippet1" "snippet2"` — no tools needed
- **Validate**: `/validate-digest`
- **Evals**: `PYTHONIOENCODING=utf-8 python .claude/skills/daily-digest/evals/run_evals.py`
