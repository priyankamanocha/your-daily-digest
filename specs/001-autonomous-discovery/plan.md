# Implementation Plan: Phase 2 — Autonomous Content Discovery

**Branch**: `001-autonomous-discovery` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-autonomous-discovery/spec.md`

## Summary

**Phase 2 is autonomous-first**: Users provide topic + optional hints (YouTube channels, X users). No text snippets expected. Implement as **skills.md with prompt-based parallel discovery agents** (web, video, social media). Orchestrator coordinates agents, deduplicates results, applies MVP quality rubric. Architecture designed for future extraction to cowork plugin. Must execute within 45-second latency budget.

## Technical Context

**Language/Version**: Claude Code skill (prompt-based)
**Architecture**: Multi-agent parallel discovery with prompt agents
  - **Primary Entry**: `/daily-digest <topic> [--hints youtube_channels,x_users]` (no snippets)
  - **Implementation**: skills.md file (separate from daily-digest.md)
  - **Subagents**: 3 prompt-based agents (web, video, social discovery) spawned in parallel
  - **Orchestration**: Orchestrator in skills.md coordinates agents, handles results, deduplicates

**Primary Dependencies**: Claude's native tools (web_search, fetch); MCP servers (Twitter, YouTube optional); hint parsing
**Subagent Design**: Each agent prompt independently researches source type, returns structured text results
**Deduplication Strategy**: Prompt-based semantic matching + heuristic scoring (Credibility + Specificity + Engagement)
**Storage**: Markdown digests in `digests/{YYYY}/{MM}/` via MVP integration
**Testing**: Manual invocation + benchmark validation; quality rubric verification; latency measurement
**Target Platform**: Claude Code skill (MVP-compatible); designed for future cowork plugin extraction
**Project Type**: Skill file with parallel prompt agents
**Performance Goals**: Parallel discovery (3 agents simultaneous) + deduplication + insight extraction <45 seconds
**Constraints**: Autonomous-first (no text snippets); single skill file; quality rubric enforcement (no padding); hint-based discovery optional (YouTube channels, X users)
**Scale/Scope**: Business/tech topics; handle optional hints; graceful degradation for ultra-niche topics

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Applicable Principles** (from MVP implementation):
- ✅ **Single Skill**: Phase 2 extends MVP as single skill file, no external code files
- ✅ **Prompt-Based**: All logic in Claude Code prompt, no dependencies or external APIs
- ✅ **Manual Testing + Quality Rubric**: Validation via benchmark samples and quality rubric (novelty, evidence, specificity, actionability)
- ✅ **Backward Compatibility**: MVP manual mode (`/daily-digest <topic> <text_snippet>`) continues to work
- ✅ **Output Format**: Markdown files in `digests/{YYYY}/{MM}/` (no new storage layers)

**Gates**:
- ✅ No external code files required (skill-based implementation)
- ✅ No new database or persistence layer
- ✅ Must maintain MVP quality standards (quality rubric enforcement, no padding)
- ✅ Must execute within 45-second latency budget
- ✅ Backward compatibility with MVP manual mode maintained

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
.claude/commands/
├── daily-digest.md           # MVP: Manual mode (backward compat, optional)
│
├── skills.md                 # PHASE 2: Orchestrator + parallel discovery agents
│   ├── Input parsing (topic + optional hints)
│   ├── Agent spawning (web, video, social parallel)
│   ├── Result collection & deduplication
│   ├── Quality filtering (MVP rubric)
│   ├── MVP insight extraction integration
│   └── Markdown output generation
```

**Skills.md Structure** (single file, prompt-based):

1. **Input Handler**
   - Parse topic + optional hints (YouTube channels, X users)
   - Validate inputs

2. **Orchestrator**
   - Spawn 3 discovery subagents in parallel
   - Wait for all results
   - Merge candidate insights

3. **Deduplication Logic**
   - Identify semantic duplicates
   - Score by credibility + specificity + engagement
   - Retain best-evidence versions

4. **Quality Filtering**
   - Apply MVP quality rubric
   - Select 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
   - Include warnings if low-signal

5. **Output Generation**
   - Markdown file in `digests/{YYYY}/{MM}/`
   - Source attribution
   - Discovery status messages

**Design Philosophy**: Single skills.md file, prompt-based agents (not code), easily extractable to cowork plugin later

## Phase 0: Research (Skills.md + Prompt Agents)

**Research Tasks** (from earlier research, applied to skills.md approach):

1. ✅ **Prompt Agent Execution Model**: How to spawn 3 discovery agents in parallel from skills.md prompt
2. ✅ **Hint-Based Discovery**: Parse and use YouTube channels + X/Twitter users as research hints
3. ✅ **Result Merging**: Prompt-based deduplication + heuristic scoring (Credibility + Specificity + Engagement)
4. ✅ **Latency Analysis**: 27s end-to-end with parallel execution, 18s safety margin (45s budget)
5. ✅ **Plugin Extractability**: Design skills.md structure for future cowork plugin conversion

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

> **Architectural Complexity**: Single skills.md file with prompt-based parallel agents balances:
> - ✅ Prompt-based agents (easier to understand, modify, test than code)
> - ✅ Parallel execution model (3 agents simultaneous, 27s latency)
> - ✅ Plugin extractability (organized structure ready for cowork conversion)
> - ✅ Minimal new files (skills.md only, separate from daily-digest.md)
> - ✅ Backward compatible (no changes to MVP daily-digest command)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
