# SignalFlow Benchmark

**Purpose**: Sample inputs and expected-quality outputs for testing digest quality consistently.

**How to use**: Run `/daily-digest claude-code "snippet1" "snippet2" "snippet3"` with the
provided snippets, then evaluate the output against the expected quality levels.

---

## Sample Input Set 1: Claude Code Subagents Pattern

### Input Snippets

**Snippet 1** (from Anthropic documentation):
```
Subagents in Claude Code enable parallel execution of independent tasks.
Each subagent runs as a separate Claude instance with its own context window.
Subagents are particularly effective for multi-source research, where you need to fetch from
YouTube, Twitter, and web simultaneously without blocking. Returns are merged and synthesized
in the parent skill, reducing latency by 60% compared to sequential execution.
```

**Snippet 2** (from user experience):
```
I used subagents to parallelize a content retrieval task. I had 3 sources: YouTube for videos,
Twitter for commentary, and blogs for long-form analysis. Running these sequentially took 6 minutes.
With 3 parallel subagents, it dropped to 2 minutes. The key insight: make sure subagents have
independent scopes so they don't block on shared state.
```

**Snippet 3** (from another builder):
```
Subagents are powerful but easy to misuse. I initially created one subagent per item to fetch
(50 items = 50 subagents). That was a mistake—too much overhead. Instead, I create 3-5 subagents
per source type. Each subagent batches 10-20 items. That's the sweet spot for our use case.
```

### Expected Output Quality

**Insights Extracted** (should be 1-3 high-quality):
1. ✅ **HIGH QUALITY** — "Parallel subagents reduce latency by 60% compared to sequential for multi-source retrieval"
   - Non-obvious? Yes (quantified performance claim)
   - Evidence? Multiple sources cite this pattern
   - Answers what/why/how? Yes
   - Qualifies on rubric? Yes (scores 2 on novelty, evidence, specificity, actionability)

2. ✅ **HIGH QUALITY** — "Subagent batching matters: 3-5 subagents per source type, 10-20 items per subagent, prevents overhead"
   - Non-obvious? Yes (specific tuning guidance)
   - Evidence? Direct from experienced user
   - Concrete? Yes, gives specific numbers
   - Actionable? Yes, users can apply immediately

3. ❌ **SHOULD BE REJECTED** — "Subagents are useful for parallel tasks"
   - Why rejected? Generic/obvious statement; doesn't answer what/why/how; no actionable guidance
   - Would score 0-1 on novelty and actionability — below rubric threshold

**Anti-patterns** (should be 2-4):
- ✅ "Creating one subagent per item (e.g., 50 items = 50 subagents) causes overhead; instead batch into 3-5 subagents"
- ✅ "Subagents with shared state blocking causes bottlenecks; keep subagent scopes independent"

**Actions** (should be 1-3):
- ✅ "Parallelize a multi-source research task: implement 3 subagents (one per source type), merge results, measure latency before/after"
  - Effort: medium
  - Time: 1-2 hours
  - Measurable outcome? Yes (latency reduction)

---

## Sample Input Set 2: MCP Tools for Extensibility

### Input Snippets

**Snippet 1**:
```
MCP (Model Context Protocol) tools abstract away authentication complexity. Instead of
managing API keys, auth tokens, rate limits, and SDKs, you call an MCP server. The MCP
handles the infrastructure. For web access, just call WebFetch MCP and get HTML parsed
into markdown. No SDK dependency management.
```

**Snippet 2**:
```
I tried using three different Python HTTP libraries in the same project. Dependency hell.
Version conflicts, auth token storage all different. Switched to MCP tools for web access.
Single interface, no dependency versioning. Deployment simplified.
```

**Snippet 3**:
```
Not all APIs have MCP servers yet. Twitter does (via community MCPs). Web search does.
But if you need a custom API, you either build an MCP for it or handle auth yourself.
The value of MCP is clear: fewer moving parts.
```

### Expected Output Quality

**Insights** (1-3):
1. ✅ **HIGH QUALITY** — "MCP tools eliminate authentication complexity and dependency management by providing a single interface to external services"
   - Concrete? Yes (lists specific benefits)
   - Actionable? Yes (users can prefer MCP over direct API calls)
   - Answers what/why/how? Yes

2. ✅ **HIGH QUALITY** — "MCP adoption depends on tool availability; not all APIs have MCP servers yet, requiring fallback to direct API handling"
   - Non-obvious? Yes (limitation not obvious from MCP marketing)
   - Evidence? From real user experience
   - Actionable? Yes (plan MCP availability check before architecture decisions)

**Anti-patterns** (2-4):
- ✅ "Using multiple HTTP libraries in the same codebase for different APIs causes dependency version conflicts and deployment complexity"
- ✅ "Assuming all APIs have MCP servers available; requires fallback plans for custom/niche APIs"

**Actions** (1-3):
- ✅ "Audit your current API integrations and identify which have MCP servers available; plan fallback auth handling for those without MCP support"

---

## Quality Rubric Application Guide

### ✅ Insight PASSES If:
- [x] Non-obvious (not something widely known in the field)
- [x] Backed by evidence from provided content (direct quote or paraphrase with source attribution)
- [x] Specific (not generic; provides concrete numbers, patterns, or technical details)
- [x] Answers ALL THREE: what/why/how (not just one)

### ❌ Insight FAILS If:
- [x] Generic ("APIs are useful", "testing is important")
- [x] Obvious to the target audience (senior engineers)
- [x] No evidence provided or cited
- [x] Vague or abstract (no actionable guidance)

---

## Testing Digest Quality

1. **Run with Sample Input Set 1** above (snippets mode — no MCP tools needed)
2. **Compare output**:
   - Are the high-quality insights listed?
   - Are low-quality insights rejected (not padded)?
   - Are anti-patterns accurate?
   - Are actions concrete and testable?
3. **Score using rubric**:
   - Each insight: Novelty, Evidence, Specificity, Actionability (0-2 each)
   - Pass threshold: Score 2 on at least 3 of 4 dimensions
4. **Repeat with Sample Input Set 2**

## Benchmark Success Criteria

Digest quality is validated when:
- ✅ All high-quality insights in this benchmark are extracted
- ✅ All low-quality items are rejected (not padded)
- ✅ All anti-patterns are accurate
- ✅ All actions are concrete and testable
- ✅ Output matches expected schema (1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources)
