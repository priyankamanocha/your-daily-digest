# Phase 2 Implementation Checklist

**Document Purpose**: Actionable checklist for implementing multi-agent parallel discovery based on PHASE2-MULTI_AGENT_ARCHITECTURE.md

**Status**: Ready for implementation
**Target Timeline**: 2-3 weeks
**Team Size**: 1-2 engineers

---

## Pre-Implementation (Week 0)

### Architecture Review
- [ ] Team reviews `PHASE2-MULTI_AGENT_ARCHITECTURE.md` (main research document)
- [ ] Confirm understanding of orchestrator + 3 subagent model
- [ ] Validate 45-second budget is acceptable
- [ ] Confirm input/output contracts (JSON schemas) with team
- [ ] Review parallel vs sequential latency comparison
- [ ] Identify any blockers or questions

### Tool Availability Verification
- [ ] Confirm `web_search` tool available in Claude Code
- [ ] Confirm `fetch` tool available in Claude Code
- [ ] Check MCP availability (Twitter, YouTube servers)
- [ ] Identify fallback if MCP unavailable
- [ ] Test basic web_search + fetch latency (measure P50/P95)

### Dependency Check
- [ ] Verify Python/subagent framework available (if using Python subagents)
- [ ] Confirm Claude Code supports skill-to-skill invocation (for spawning subagents)
- [ ] Test non-blocking async patterns in Claude Code
- [ ] Verify file I/O for markdown output works

---

## Week 1: Orchestrator & Input/Output Contracts

### Orchestrator Skeleton (Phase 2 Discovery)
- [ ] Create `skills/phase2-discovery.md` file
- [ ] Add header section with description
- [ ] Copy input/output contract definitions (JSON schemas) from research doc
- [ ] Add Section 1: Input validation
  - [ ] Parse topic from command arguments
  - [ ] Validate topic (non-empty, <100 chars)
  - [ ] Determine if topic-only (Phase 2) vs topic + snippets (MVP manual mode)
  - [ ] Extract keywords from topic
  - [ ] Validate timeout budget (40-45 seconds)

### Subagent Input/Output Contract Definitions
- [ ] Create `schemas/discovery-agent-input.json` (unified contract)
- [ ] Create `schemas/discovery-agent-output.json` (unified contract)
- [ ] Document contract expectations in orchestrator prompt
- [ ] Add examples (web, video, social) showing what each agent returns

### Orchestrator Function Signatures (Pseudo-code Section)
- [ ] Define `parallelize_discovery(topic, keywords, timeout_budget)`
- [ ] Define `wait_for_agents(agents, timeout_budget)` (non-blocking wait)
- [ ] Define `merge_results(results)` (takes 3 agent outputs)
- [ ] Define `deduplicate_candidates(merged_pool)` (semantic dedup)
- [ ] Define `apply_quality_rubric(candidates)` (MVP filter)
- [ ] Add detailed pseudo-code for timeout handling

### Error Handling
- [ ] Document timeout scenarios (per-agent, orchestrator-level)
- [ ] Document fallback if 0 agents complete (manual mode message)
- [ ] Document partial-results handling (1-2 agents complete)
- [ ] Add error logging instrumentation

---

## Week 2: Subagent Implementation

### Web Discovery Subagent
- [ ] Create `skills/web-discovery.md`
- [ ] Add input validation section (parse web agent input contract)
- [ ] Add topic interpretation:
  - [ ] Extract 3-5 search queries from topic + keywords
  - [ ] Example: "claude-code" → ["claude code subagents", "MCP integration", "patterns advanced"]
- [ ] Add web search execution (native web_search tool)
  - [ ] Execute 3 searches in sequence
  - [ ] Limit results to 20 total
  - [ ] Extract top URLs
- [ ] Add content fetching (native fetch tool)
  - [ ] Fetch 8 URLs (configurable limit)
  - [ ] Parse HTML → Markdown automatically
  - [ ] Aggregate content snippets
  - [ ] Handle rate limiting (if hit, return partial)
- [ ] Add result structuring (output contract)
  - [ ] Create candidates[] array (JSON)
  - [ ] Include source credibility heuristic per URL
  - [ ] Include engagement metadata (inbound links, mentions)
  - [ ] Include query execution metadata
- [ ] Add timeout handling (respect 12-second soft limit)
- [ ] Test latency (target: 12s P95)

### Video Discovery Subagent
- [ ] Create `skills/video-discovery.md`
- [ ] Add input validation
- [ ] Add video search (YouTube via MCP or web search)
  - [ ] Search for 2-3 queries
  - [ ] Extract video URLs
- [ ] Add transcript extraction
  - [ ] Extract transcripts from 3-5 videos (parallel if possible)
  - [ ] Handle videos without transcripts (skip gracefully)
- [ ] Add result structuring (output contract)
  - [ ] Include video metadata (title, channel, engagement)
  - [ ] Segment transcript by topic
  - [ ] Assign source credibility (verified channel vs unverified)
- [ ] Add timeout handling (respect 10-second limit)
- [ ] Test latency (target: 10s P95)

### Social Media Discovery Subagent
- [ ] Create `skills/social-discovery.md`
- [ ] Add input validation
- [ ] Add Twitter/X search (MCP or native if available)
  - [ ] Search for 2-3 queries
  - [ ] Limit to recent posts (last 30 days)
  - [ ] Extract 7-10 tweets
- [ ] Add result structuring (output contract)
  - [ ] Include tweet metadata (author, verification, engagement)
  - [ ] Assign source credibility (verified account vs unverified)
  - [ ] Include engagement signals (likes, retweets, replies)
- [ ] Add graceful fallback if Twitter API unavailable
- [ ] Add timeout handling (respect 8-second limit)
- [ ] Test latency (target: 8s P95)

### Subagent Testing
- [ ] Unit test each subagent independently
  - [ ] Provide mock input, verify output structure
  - [ ] Verify input/output contracts (JSON schema validation)
  - [ ] Test error paths (API failures, timeouts)
- [ ] Integration test: Invoke all 3 subagents in parallel
  - [ ] Measure actual latency for real topic
  - [ ] Verify results from all 3 arrive at orchestrator
  - [ ] Verify output contracts matched

---

## Week 3: Deduplication & Quality Filtering

### Semantic Deduplication (Prompt-Based)
- [ ] Add deduplication logic to orchestrator
- [ ] Implement grouping algorithm:
  - [ ] Merge output from 3 agents (combine candidates[] arrays)
  - [ ] Prompt guidance: "Identify semantically identical insights"
  - [ ] Output: Groups of equivalent insights
- [ ] Implement scoring per group (heuristic):
  - [ ] Credibility (0-3): Source authority
  - [ ] Specificity (0-3): Concrete vs generic
  - [ ] Engagement (0-2): Views/likes/reactions
  - [ ] Score = Credibility + Specificity + Engagement (0-8 range)
- [ ] Select winner per group (highest score)
- [ ] Retain supporting evidence (alternative sources)
- [ ] Output: Deduplicated candidates (~8-12 from 24-45 raw)

### Quality Filtering (MVP Rubric)
- [ ] Apply MVP 4-dimension rubric (reuse from daily-digest.md)
  - [ ] Novelty (0-2): New + non-obvious?
  - [ ] Evidence (0-2): Cited + direct quote?
  - [ ] Specificity (0-2): Concrete + actionable?
  - [ ] Actionability (0-2): Clear next step?
- [ ] Inclusion rule: ≥2 on ≥3 dimensions
- [ ] Output: Final insights (1-3 expected)
- [ ] Track which candidates rejected (audit trail)

### Source Classification (Anti-patterns & Actions)
- [ ] Identify 2-4 anti-patterns from final insights
  - [ ] Use same candidates pool
  - [ ] Apply same deduplication (avoid duplicate anti-patterns)
- [ ] Generate 1-3 actions per insight
  - [ ] Reuse MVP action generation logic
  - [ ] Effort, time, steps, expected outcome

### Resources Extraction
- [ ] Extract 3-5 supporting resources
  - [ ] Pull from merged candidate pool
  - [ ] Include credible sources first
  - [ ] Format as direct quotes or titles from content

### Deduplication Testing
- [ ] Manual validation test (small dataset)
  - [ ] Create 10-15 candidate insights (mix of duplicates + unique)
  - [ ] Run deduplication prompt
  - [ ] Manually verify grouping (hand-label duplicates)
  - [ ] Measure accuracy >90%?
- [ ] Edge case testing
  - [ ] All identical insights (expect 1 group, select highest-credibility)
  - [ ] All unique insights (expect N groups, no merges)
  - [ ] Mixed confidence (test low-confidence merges handled conservatively)

---

## Week 3 (Continued): Integration & Polish

### Orchestrator Completion
- [ ] Add main execution flow:
  1. Validate input (topic-only vs MVP mode)
  2. Extract keywords from topic
  3. Spawn 3 subagents in parallel
  4. Wait for results (non-blocking, timeout at 40s)
  5. Merge results from available agents
  6. Deduplicate semantically
  7. Apply quality rubric
  8. Generate anti-patterns, actions, resources
  9. Output markdown file
- [ ] Add timeout handling at orchestrator level:
  - [ ] Hard stop at 40s (5s margin for final steps)
  - [ ] Log which agents completed
  - [ ] Log warnings if <3 agents completed
- [ ] Add fallback handling:
  - [ ] If 0 agents complete: "No content discovered. Use manual mode: /daily-digest topic [snippet1]..."
  - [ ] If 1-2 agents complete: Add quality warning to digest
  - [ ] If all 3 complete: No warning needed

### Backward Compatibility
- [ ] Verify MVP manual mode still works (`/daily-digest topic [snippet1] [snippet2] [snippet3]`)
- [ ] Route topic-only to Phase 2; topic + snippets to MVP
- [ ] Output format identical between MVP and Phase 2

### Markdown Output
- [ ] Reuse MVP output format
- [ ] Include generated timestamp
- [ ] Include quality warnings if applicable
- [ ] Include discovery metadata (which agents succeeded, duration)

### Error Recovery
- [ ] Handle individual agent failures gracefully
- [ ] Implement retries (optional: 1 retry if timeout)
- [ ] Log all errors for debugging

---

## Testing Phase (All Weeks)

### Unit Testing (Per Subagent)
- [ ] Web discovery: test search + fetch with mock URLs
- [ ] Video discovery: test transcript extraction
- [ ] Social discovery: test Twitter search + aggregation
- [ ] Each subagent validates against output contract

### Integration Testing
- [ ] Orchestrator + all 3 subagents together
- [ ] Test parallel execution (confirm non-blocking)
- [ ] Test timeout handling (simulate slow agent)
- [ ] Test partial failures (1 or 2 agents fail)

### Benchmark Testing (Sample Topics)
- [ ] Test 5-10 diverse topics:
  - [ ] "claude-code" (tech, well-documented)
  - [ ] "quantum computing" (emerging, less coverage)
  - [ ] "machine learning trends 2026" (hot topic, lots of content)
  - [ ] "ultra-niche-topic-xyz" (verify graceful fallback)
- [ ] For each topic, measure:
  - [ ] End-to-end latency
  - [ ] Number of candidates (raw + deduplicated)
  - [ ] Number of final insights (vs target 1-3)
  - [ ] Insight quality (manual rubric check)
  - [ ] Which agents succeeded

### Latency Validation
- [ ] Measure P50, P95, P99 latencies
- [ ] Target: P95 < 30s (target spec: <30s)
- [ ] Log detailed timing per phase:
  - [ ] Agent runtimes (web, video, social)
  - [ ] Merge + deduplicate time
  - [ ] Quality filter time
  - [ ] Insight extraction time
- [ ] Identify any bottlenecks

### Quality Assurance
- [ ] Deduplication accuracy: hand-validate >90% of merges
- [ ] Insight quality: Verify ≥2 on 3/4 rubric dimensions
- [ ] Anti-patterns: Verify 2-4 present + high quality
- [ ] Actions: Verify 1-3 present, effort/time/steps filled
- [ ] Resources: Verify 3-5 present, direct quotes or titles

---

## Documentation (Parallel)

### Updated CLAUDE.md
- [ ] Document Phase 2 command: `/daily-digest <topic>`
- [ ] Document input validation (topic-only vs topic + snippets)
- [ ] Document output format (unchanged from MVP)
- [ ] Document quality warnings (if partial discovery)
- [ ] Document timeout behavior

### Subagent Documentation
- [ ] Document web-discovery contract + usage
- [ ] Document video-discovery contract + usage
- [ ] Document social-discovery contract + usage
- [ ] Include example inputs/outputs

### Latency Documentation
- [ ] Update specs with measured P95 latencies
- [ ] Document timing breakdown (parallelism benefit)
- [ ] Document safety margin explanation

### Migration Guide (Plugin-Ready)
- [ ] Document input/output contracts (ready for Phase 3 extraction)
- [ ] Document how Phase 2 maps to cowork plugin (conceptual)
- [ ] Note: Formal plugin migration happens in Phase 3

---

## Deployment Checklist

### Pre-Launch Validation
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Benchmark tests run for 5+ topics
- [ ] Latency targets met (P95 < 30s, P99 < 35s)
- [ ] Edge cases handled (0 agents, 1 agent, partial results)
- [ ] Documentation complete and reviewed

### Rollout Plan
- [ ] Merge `001-autonomous-discovery` branch to main
- [ ] Update `.claude/commands/daily-digest.md` to route topic-only → Phase 2
- [ ] Create digest output directory: `digests/{YYYY}/{MM}/`
- [ ] Announce Phase 2 ready for testing

### Post-Launch Monitoring
- [ ] Log metrics: latency, success rate, agent completion rate
- [ ] Monitor for failures: which subagents timeout?
- [ ] Collect feedback: digest quality, user satisfaction
- [ ] Track issues for Phase 2.1 (refinements)

---

## Sign-Off Criteria (Definition of Done)

### Functional Requirements
- ✅ `/daily-digest <topic>` (no snippets) invokes Phase 2 autonomous discovery
- ✅ System discovers content from web, video, social in parallel
- ✅ System merges + deduplicates 24-45 candidates into 8-12 unique insights
- ✅ System extracts 1-3 final insights using MVP quality rubric
- ✅ System generates 2-4 anti-patterns, 1-3 actions, 3-5 resources
- ✅ Output is identical markdown format as MVP
- ✅ Execution completes within 45 seconds (P95 < 30s)

### Quality Requirements
- ✅ Deduplication accuracy >90% (spot-check >50% of merges)
- ✅ Insight quality: ≥2 on 3/4 MVP rubric dimensions
- ✅ Source credibility: Insights from credible sources only (credibility ≥2)
- ✅ Evidence: Every insight has direct quote or clear attribution
- ✅ Anti-patterns: Practical, evidence-backed, 2-4 per digest
- ✅ Actions: Concrete, effort/time/steps specified, 1-3 per digest
- ✅ Resources: 3-5, direct quotes or titles, sorted by credibility

### Non-Functional Requirements
- ✅ Backward compatible: MVP manual mode still works
- ✅ Graceful degradation: Partial results handled with warnings
- ✅ Error handling: No crashes on edge cases (0 agents, timeout, API errors)
- ✅ Logging: Audit trail of which agents succeeded, merge decisions
- ✅ Plugin-ready: Input/output contracts formalized, future extraction clear

### Documentation Requirements
- ✅ Research document (PHASE2-MULTI_AGENT_ARCHITECTURE.md)
- ✅ Implementation guide (IMPLEMENTATION_GUIDE.md updated)
- ✅ API documentation (subagent contracts)
- ✅ Latency analysis (measured P50/P95/P99)
- ✅ Test results (5+ benchmark topics)

---

## Risk Mitigation During Implementation

| Risk | Mitigation |
|------|-----------|
| **Agents timeout frequently** | Start with conservative timeout limits (web: 15s, video: 12s, social: 10s); tighten based on real measurements |
| **Deduplication creates false merges** | Conservative approach: only merge high-confidence (0.9+); manually review low-confidence |
| **Insight quality drops below MVP** | Use MVP quality rubric as hard filter; require ≥2 on 3/4 dimensions; don't pad with weak insights |
| **Web fetch rate limiting** | Limit fetch to 5-8 URLs per run instead of 10; use web search relevance ranking to pick best |
| **MCP sources unavailable** | Test without MCP first; use web search as primary; add MCP as optional optimization later |
| **Latency exceeds 45s on real topics** | Reduce fetch_limit, reduce search query count; profile to identify bottleneck |
| **Plugin conversion complexity** | Document contracts NOW (Phase 2); minimal refactoring needed in Phase 3 |

---

## Estimated Effort

| Phase | Task | Hours | Notes |
|-------|------|-------|-------|
| **Week 0** | Pre-implementation review + tool verification | 4h | Lightweight; identify blockers early |
| **Week 1** | Orchestrator skeleton + input/output contracts | 12h | Foundation work |
| **Week 2** | 3 subagents (web, video, social) | 18h | Parallel development possible (1 engineer per agent) |
| **Week 3** | Deduplication + quality filtering + integration | 16h | 1 engineer; test heavily |
| **Week 3** | Testing + benchmarking + documentation | 12h | Can overlap with development |
| **Deployment** | Review + rollout + monitoring setup | 4h | Lightweight; mainly process |
| | **Total** | **~66h** | **2-3 weeks at 20-30 hours/week** |

---

## Success Metrics (Post-Launch)

**Phase 2 is successful when:**

1. **Performance**: P95 latency < 30s on 10 benchmark topics
2. **Quality**: ≥2 on 3/4 MVP rubric dimensions for 90%+ of insights
3. **Reliability**: Agent success rate >85% (2-3 agents complete)
4. **Coverage**: Deduplication accuracy >90% (semantic matching correct)
5. **User Experience**: Graceful handling of edge cases (partial results, timeouts)
6. **Maintainability**: Clear input/output contracts for Phase 3 plugin extraction

---

## Post-Phase 2 (Phase 3+ Planning)

### Feedback Loop (Phase 3)
- [ ] Add `/rate-digest` command for user feedback
- [ ] Track source quality over time
- [ ] Learn user preferences (which sources matter most)

### Scheduling (Phase 3)
- [ ] Add scheduled daily digest generation
- [ ] Support multiple topics per digest
- [ ] Export to Notion, email, etc.

### Plugin Conversion (Phase 3+)
- [ ] Extract orchestrator to cowork plugin
- [ ] Extract subagents to cowork plugin tasks
- [ ] Use JSON schemas defined in Phase 2 (minimal changes)
- [ ] Maintain same deduplication + quality logic

---

**Document Version**: 1.0
**Status**: Ready for Engineering Handoff
**Last Updated**: 2026-03-21
