# Implementation Plan: Daily Digest Skill

**Branch**: `daily-digest` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/daily-digest/spec.md`

## Summary

Autonomous-first daily digest skill. Users provide topic + optional hints (YouTube channels, X/Twitter handles). Three parallel discovery agents (web, video, social) spawn simultaneously; orchestrator merges results, scores credibility, deduplicates, applies quality rubric, and writes a markdown digest. Snippets accepted for testing only. Must execute within 45-second latency budget.

## Technical Context

**Language/Version**: Claude Code skill (prompt-based) + Python 3.8+ stdlib scripts
**Architecture**: Multi-agent parallel discovery
  - **Primary entry**: `/daily-digest <topic> [--hints channels,@handles]`
  - **Orchestrator**: `.claude/skills/daily-digest/daily-digest.md`
  - **Agents**: 3 separate skill files under `agents/` (web, video, social) — spawned in parallel
  - **Scripts**: Python I/O helpers in `scripts/` (validate_input, build_path, write_digest, check_runtime)
  - **Resources**: Reference material in `resources/` (credibility rules, freshness policy, quality rubric, digest template)

**Primary Dependencies**: `web_search` MCP tool, `fetch` MCP tool; Python 3.8+ stdlib only
**Deduplication Strategy**: Semantic matching; retain highest-credibility version per insight group
**Storage**: Markdown digests in `digests/{YYYY}/{MM}/`
**Testing**: Manual invocation (snippets mode) + `/validate-digest` benchmark validation
**Project Type**: Claude Code skill with parallel agent sub-skills
**Performance Goals**: Parallel discovery (3 agents simultaneous) + synthesis < 45 seconds
**Constraints**: Autonomous-first; Python stdlib only; quality rubric enforced (no padding); hints optional
**Scale/Scope**: Business/tech topics; graceful degradation for ultra-niche topics or unavailable sources

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Principle | Status |
|---|---|---|
| Delivery vehicle: `.claude/skills/daily-digest/daily-digest.md` | I | ✅ |
| Skill format: frontmatter + User Input + Outline | I + II | ✅ |
| Script scope: scripts perform I/O only | II | ✅ |
| Reference material in `resources/`, not inline | II | ✅ |
| Evidence requirement: all insights include direct quote | III | ✅ |
| Count enforcement within 1–3/2–4/1–3/3–5 ranges | III | ✅ |
| Partial failure returns digest with status, not error | IV | ✅ |
| Preflight checks verify hard deps before discovery | IV | ✅ |
| Python stdlib only; no third-party packages | V | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/daily-digest/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── benchmark.md
├── contracts/
│   ├── input-schema.md
│   └── output-schema.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude/skills/daily-digest/
├── daily-digest.md              # Orchestrator skill
├── agents/
│   ├── web-discovery-agent.md   # Web discovery (web_search + fetch)
│   ├── video-discovery-agent.md # YouTube discovery
│   └── social-discovery-agent.md# X/Twitter discovery
├── scripts/
│   ├── check_runtime.py         # Preflight: Python version + digests/ writable
│   ├── validate_input.py        # Input validation (topic + hints)
│   ├── build_path.py            # Output path: digests/{YYYY}/{MM}/digest-{date}-{slug}.md
│   └── write_digest.py          # Write digest file
└── resources/
    ├── credibility-rules.md     # 0-3 scoring table + exclusion rule
    ├── freshness-policy.md      # Age → score thresholds
    ├── quality-rubric.md        # 4-dimension table + min/max counts
    └── digest-template.md       # Output markdown template + field rules

digests/{YYYY}/{MM}/             # Generated output
```

**Orchestrator flow** (`daily-digest.md`):
1. Preflight checks (Python, MCP tools, digests/ writable)
2. Validate input (topic + hints)
3. Mode select (snippets → manual; none → autonomous)
4. Spawn 3 agents in parallel
5. Assess discovery status (complete/partial/timeout)
6. Score source credibility
7. Extract and deduplicate candidate insights
8. Apply quality rubric and select final content
9. Build path and write digest
10. No-content fallback

## Phase 0: Research

**Research Tasks** (complete):

1. ✅ **Parallel agent execution**: Spawn 3 agents simultaneously from orchestrator skill
2. ✅ **Hint-based discovery**: Pass YouTube channels + X/Twitter handles to agents
3. ✅ **Deduplication**: Semantic matching; retain highest-credibility version
4. ✅ **Latency analysis**: ~27s end-to-end with parallel execution, 18s safety margin under 45s budget

**Research Findings**:
- Web agent: 8-12s (search + fetch)
- Video agent: 6-10s (YouTube + transcripts)
- Social agent: 5-8s (Twitter/X + content)
- Orchestration: 2-4s
- Deduplication: 2-3s
- Insight extraction: 5-8s
- **Total: ~27s** (18s margin under 45s budget)

---

## Complexity Tracking

> No constitution violations. All gates pass (see Constitution Check above).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| 3 agent skill files (not 1) | Each source type needs distinct search strategy | One combined agent would conflate web/video/social logic and be harder to tune independently |
| `resources/` directory | Rubrics and templates are reference material, not execution logic | Embedding inline bloats the orchestrator and makes reference material harder to update |
