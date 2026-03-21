# Phase 2 Multi-Agent Architecture: Quick Reference

**Purpose**: One-page summary of key architectural decisions
**Audience**: Team leads, architects, implementation engineers
**Read Time**: 5 minutes

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Digest (Routing)                   │
│  /daily-digest <topic>          vs    /daily-digest topic [snippets]
│        ↓                                       ↓
│   Autonomous Mode (Phase 2)           Manual Mode (MVP, Phase 1)
└─────────────────────────────────────────────────────────────┘

Autonomous Mode (Phase 2):

    skills/phase2-discovery.md (Orchestrator)
              ↓
    ┌─────────────────────────────┐
    │  Spawn 3 Subagents (Parallel)│
    └─────────────────────────────┘
         ↙          ↓           ↖
    Web Agent    Video Agent    Social Agent
   (search +    (transcripts)   (Twitter/X)
    fetch)
         ↘          ↓           ↙
    ┌──────────────────────────────┐
    │ Collect Results (Non-Blocking)│
    │ Max Wait: 40s (hard deadline) │
    └──────────────────────────────┘
         ↓ (30 candidates from all agents)
    ┌──────────────────────────────┐
    │ Merge & Deduplicate          │
    │ (Prompt-based semantic match)│
    │ Output: 8-12 unique insights │
    └──────────────────────────────┘
         ↓
    ┌──────────────────────────────┐
    │ Quality Filter (MVP Rubric)  │
    │ Score ≥2 on ≥3 dimensions    │
    │ Output: 1-3 final insights   │
    └──────────────────────────────┘
         ↓
    ┌──────────────────────────────┐
    │ Extract Anti-patterns, Actions│
    │ Resources (Reuse MVP)        │
    └──────────────────────────────┘
         ↓
    ┌──────────────────────────────┐
    │ Generate Markdown Output     │
    │ Write to digests/{YYYY}/{MM}/│
    └──────────────────────────────┘
```

---

## Key Decisions (4 Areas)

### 1. Subagent Execution Model

**Decision**: Orchestrator + 3 parallel subagents (web, video, social)

| Aspect | Details |
|--------|---------|
| **Model** | Orchestrator spawns 3 agents in parallel, not sequential |
| **Agents** | Web (search+fetch), Video (YouTube transcripts), Social (Twitter/X posts) |
| **Parallelism** | All 3 run simultaneously; max latency = slowest agent |
| **Timeout** | Per-agent soft limit (web: 12s, video: 10s, social: 8s); orchestrator hard stop at 40s |
| **Fallback** | If agent times out, orchestrator continues with other agents (partial results OK) |
| **Latency Gain** | ~50% faster than sequential (27s parallel vs 40s sequential) |

**Input/Output Contracts** (JSON schemas):
- All subagents receive unified input: `{agent_type, topic, keywords, timeout_seconds, ...}`
- All subagents return unified output: `{agent_type, status, candidates[], ...}`
- Enables independent development and future plugin conversion

---

### 2. Result Merging Strategy

**Decision**: Prompt-based semantic deduplication + heuristic scoring (no ML)

| Aspect | Details |
|--------|---------|
| **Input** | 24-45 raw candidates from 3 agents |
| **Deduplication** | Prompt-based grouping (identify semantically identical insights) |
| **Scoring** | Heuristic: Credibility (0-3) + Specificity (0-3) + Engagement (0-2) = 0-8 |
| **Selection** | Keep highest-scoring candidate per group; track supporting evidence |
| **Confidence** | Track merge confidence (0.9-1.0 high, 0.5-0.7 low) |
| **Output** | 8-12 deduplicated candidates with merge metadata |
| **Quality Filter** | Apply MVP 4-dimension rubric; keep ≥2 on ≥3 dimensions |
| **Final** | 1-3 high-quality insights |

**No ML models needed**: Leverages Claude's native semantic reasoning + simple heuristics.

---

### 3. Plugin Extraction Patterns

**Decision**: Contract-first design for seamless Phase 3 cowork conversion

| Aspect | Details |
|--------|---------|
| **Phase 2 (Claude Code)** | All logic in `skills/phase2-discovery.md` + `skills/{web,video,social}-discovery.md` |
| **Phase 3 (Cowork Plugin)** | Extract to `src/orchestrator.ts` + `src/agents/*.ts` (minimal refactoring) |
| **What Transfers** | Input/output schemas, deduplication algorithm, quality rubric, merge heuristics |
| **What Changes** | Orchestrator logic (prompt → TypeScript), subagent invocation (skill refs → task API) |
| **Key Pattern** | Define formal JSON schemas NOW (Phase 2); reuse in Phase 3 plugin.json |
| **Migration Effort** | ~30-40% refactoring effort; most logic portable |

**Key Insight**: By formalizing contracts now, Phase 3 plugin conversion requires minimal work.

---

### 4. Parallel Latency Analysis

**Decision**: Full parallel execution (all 3 agents simultaneously)

**Timeline**:
```
0-12s    Phase 1: Web + Video + Social agents (parallel)
         Bottleneck: Web agent (12s)

12-15s   Phase 2: Merge + Deduplicate (serial, 3s)

15-23s   Phase 3: Quality Filter (serial, 8s)

23-26s   Phase 4: Insight Extraction (serial, 3s)

26-27s   Phase 5: Output Writing (serial, 1s)

─────────────────────────────────────────
27s TOTAL ✅  (vs 40s sequential, vs 45s budget)
18s MARGIN (Safety cushion for network jitter, retries)
```

| Scenario | Latency | Notes |
|----------|---------|-------|
| **Full Parallel (all 3 agents)** | 27s | Optimal; 18s safety margin |
| **2+1 Sequential (one waits)** | 32s | Acceptable; 13s margin |
| **Full Sequential (one at a time)** | 40s | Risky; only 5s margin |

**Bottleneck**: Web agent (search + fetch = 12s is slowest)

---

## Implementation Checklist (3-Week Timeline)

### Week 1: Orchestrator & Contracts
- [ ] Create `skills/phase2-discovery.md` (orchestrator skeleton)
- [ ] Define input/output schemas (JSON)
- [ ] Add pseudo-code for orchestration logic
- [ ] Implement timeout handling

### Week 2: Subagents (Parallel Development Possible)
- [ ] `skills/web-discovery.md` – search (2-3s) + fetch (8-10s) = 12s
- [ ] `skills/video-discovery.md` – search (2-3s) + transcripts (5-8s) = 10s
- [ ] `skills/social-discovery.md` – search (2-3s) + posts (3-5s) = 8s
- [ ] Unit test each subagent against contract

### Week 3: Merge, Filter, Integrate, Test
- [ ] Implement deduplication (semantic grouping + scoring)
- [ ] Implement quality filtering (MVP rubric)
- [ ] Integrate all 3 subagents with orchestrator
- [ ] Benchmark on 5-10 sample topics
- [ ] Validate latency (P95 < 30s)
- [ ] Document everything

---

## Input/Output Contracts (Formal)

### Orchestrator Input
```json
{
  "topic": "claude-code",
  "keywords": ["Claude Code", "subagents", "MCP"],
  "timeout_seconds": 40
}
```

### Subagent Input (Unified)
```json
{
  "agent_type": "web|video|social",
  "task_id": "discovery_uuid",
  "topic": "claude-code",
  "keywords": ["Claude Code", "subagents"],
  "timeout_seconds": 12,
  "output_format": "structured"
}
```

### Subagent Output (Unified)
```json
{
  "agent_type": "web|video|social",
  "task_id": "discovery_uuid",
  "status": "success|partial|timeout|error",
  "items_found": 8,
  "candidates": [
    {
      "id": "web_001",
      "source_url": "https://...",
      "source_name": "Anthropic Docs",
      "source_credibility": 3,
      "content": "Subagents enable parallel execution...",
      "metadata": { "publication_date": "2026-03-20", ... }
    }
  ]
}
```

### Orchestrator Output (Merged + Deduplicated)
```json
{
  "status": "success|partial|failure",
  "agents_completed": ["web", "video", "social"],
  "merged_candidates": [
    {
      "candidate_id": "web_001",
      "insight_text": "Subagents enable parallel task execution...",
      "evidence_source": "https://docs.anthropic.com/claude-code",
      "merge_confidence": 0.95,
      "deduplicated_from": ["web_001", "video_003", "social_002"]
    }
  ],
  "final_insights": 2,
  "warnings": []
}
```

---

## Deduplication Scoring Heuristic

**Merge candidates with highest score per group:**

```
Score = Credibility (0-3) + Specificity (0-3) + Engagement (0-2)
Range: 0-8

Example 1 (Keep this):
  Source: Anthropic docs
  Credibility: 3 (official)
  Specificity: 3 (code examples + mechanism)
  Engagement: 2 (450 inbound links)
  Total: 8 ✅

Example 2 (Discard, duplicate):
  Source: Twitter @devuser123
  Credibility: 1 (unverified)
  Specificity: 1 (brief mention)
  Engagement: 0 (12 likes)
  Total: 2 ❌
```

**Merge Confidence**:
- High (0.9-1.0): Safe to merge
- Medium (0.7-0.9): Merge with traceability
- Low (<0.7): Keep separate (conservative)

---

## MVP Quality Rubric (Reused)

**Include insight if ≥2 on ≥3 dimensions:**

| Dimension | 0 (Reject) | 1 (Weak) | 2 (Include) |
|-----------|-----------|---------|-----------|
| Novelty | Known/obvious | Somewhat new | New + non-obvious |
| Evidence | None | Mentioned | Direct quote |
| Specificity | Generic | Somewhat | Concrete |
| Actionability | Observation | Implies action | Clear next step |

**No padding**: Output 1 insight if only 1 qualifies (don't force 3).

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Web agent bottleneck (12s) | Margin exists (18s). If >30s in Phase 4, reduce fetch_limit. |
| Dedup false merges | Prompt-based is transparent; confidence scores flag low-confidence. |
| MCP unavailable | Web search primary; MCP secondary; graceful fallback. |
| Agent timeout | Soft + hard limits; orchestrator proceeds with partial results. |
| Quality drops | MVP rubric as hard filter; don't pad. |
| Plugin conversion | Contracts defined NOW; minimal refactoring in Phase 3. |

---

## Success Criteria

**Phase 2 is done when:**

- ✅ P95 latency < 30s (target: 27s)
- ✅ Dedup accuracy > 90%
- ✅ Insight quality ≥2 on 3/4 rubric dimensions
- ✅ All edge cases handled (partial results, timeouts, 0 agents)
- ✅ Backward compatible (MVP manual mode works)
- ✅ Input/output contracts formalized (plugin-ready)

---

## Files to Create/Modify

### New Files
- `skills/phase2-discovery.md` – Orchestrator
- `skills/web-discovery.md` – Web subagent
- `skills/video-discovery.md` – Video subagent
- `skills/social-discovery.md` – Social subagent
- `schemas/discovery-agent-input.json` – Unified input contract
- `schemas/discovery-agent-output.json` – Unified output contract

### Modified Files
- `.claude/commands/daily-digest.md` – Add routing (topic-only → Phase 2)
- `CLAUDE.md` – Update with Phase 2 info

### Documentation (Already Created)
- `PHASE2-MULTI_AGENT_ARCHITECTURE.md` – Full research (detailed)
- `IMPLEMENTATION_CHECKLIST.md` – Week-by-week tasks
- `QUICK_REFERENCE.md` – This file (summary)

---

## Key Metrics to Track

**During Development:**
- Agent latency (P50, P95, P99) per agent type
- Deduplication accuracy (spot-check manual validation)
- Insight quality (rubric compliance)
- Error rates (timeout frequency, API failures)

**Post-Launch:**
- End-to-end latency distribution
- Agent success rate (% of runs where N agents complete)
- Digest quality (user feedback, rubric validation)
- Source credibility accuracy (manual spot-checks)

---

## Next Steps

1. **Review this document** with team (30 min)
2. **Read full architecture doc** (`PHASE2-MULTI_AGENT_ARCHITECTURE.md`) (2-3 hours)
3. **Verify tool availability** (web_search, fetch, MCP) (1 hour)
4. **Start Week 1 tasks** using `IMPLEMENTATION_CHECKLIST.md` as guide (12 hours)

---

**Document Version**: 1.0
**Last Updated**: 2026-03-21
**Owner**: Engineering
**Status**: Ready for Implementation
