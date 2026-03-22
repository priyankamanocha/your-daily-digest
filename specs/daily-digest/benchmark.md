# your-daily-brief Benchmark

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

---

## Sample Input Sets 3–7: Since Freshness Filter

These sets test `--since` flag parsing, `since_window` resolution, and error handling. Content quality is not the focus — checks are on payload correctness and digest header output.

**Reusable snippets** (used for all happy-path sets):

```
Snippet A: Parallel subagents reduce latency by 60% compared to sequential execution for multi-source research tasks. Each subagent runs independently with its own context window, and results are merged in the parent skill.
Snippet B: Subagent batching is critical: 3-5 subagents per source type, 10-20 items each. One subagent per item causes excessive overhead and should be avoided.
Snippet C: Make sure subagents have independent scopes. Shared state between subagents causes blocking and eliminates the parallelism benefit entirely.
```

---

### Sample Input Set 3: Default Window (no --since flag)

**Invocation**:
```
/daily-digest freshness-test "Snippet A" "Snippet B" "Snippet C"
```

**Expected payload** (from `validate_input.py`):
```json
{"since": "1", "since_window": {"start_date": "{today-1}", "end_date": "{today}", "label": "last 24 hours"}}
```

**Expected digest header**:
```
Sources: manual
```
*(snippets mode always uses "manual" for Sources, regardless of since_window)*

**PASS Criteria**:
- `validate_input.py` exits 0, `since = "1"`, `since_window.label = "last 24 hours"`
- Digest file created at expected path
- `Sources: manual` present in header

**FAIL Criteria**:
- Skill halts with error
- `since_window` missing or incorrect
- Digest file not created

---

### Sample Input Set 4: Numeric Override (--since 7)

**Invocation**:
```
/daily-digest freshness-test --since 7 "Snippet A" "Snippet B" "Snippet C"
```

**Expected payload**:
```json
{"since": "7", "since_window": {"start_date": "{today-7}", "end_date": "{today}", "label": "last 7 days"}}
```

**Expected digest header**:
```
Sources: manual
```

**PASS Criteria**:
- `since = "7"`, `since_window.label = "last 7 days"`
- Digest file created; structure valid

**FAIL Criteria**:
- Skill halts with error
- `since_window.label` says "last 24 hours" (default incorrectly applied)

---

### Sample Input Set 5: Natural Language — "last month"

**Invocation**:
```
/daily-digest freshness-test --since "last month" "Snippet A" "Snippet B" "Snippet C"
```

**Expected payload**:
```json
{"since": "last month", "since_window": {"start_date": "{today-30}", "end_date": "{today}", "label": "last 30 days"}}
```

**PASS Criteria**:
- `since_window.label = "last 30 days"`
- Digest file created; structure valid

**FAIL Criteria**:
- Skill halts with parse error
- `since_window` resolves to wrong dates

---

### Sample Input Set 6: Calendar Month — "feb 2026"

**Invocation**:
```
/daily-digest freshness-test --since "feb 2026" "Snippet A" "Snippet B" "Snippet C"
```

**Expected payload**:
```json
{"since": "feb 2026", "since_window": {"start_date": "2026-02-01", "end_date": "2026-02-28", "label": "1 Feb – 28 Feb 2026"}}
```

**PASS Criteria**:
- `since_window.start_date = "2026-02-01"`, `since_window.end_date = "2026-02-28"`
- `since_window.label = "1 Feb – 28 Feb 2026"`
- Digest file created; structure valid

**FAIL Criteria**:
- Skill halts with parse error
- Wrong start/end dates (e.g. wrong month length)

---

### Sample Input Set 7: Invalid --since Inputs (Error Cases)

Each invocation below MUST halt before creating any digest file. No file should exist at the expected output path.

| Invocation | Expected error message |
|------------|----------------------|
| `/daily-digest freshness-test --since 0 "Snippet A"` | `since=0 is not valid — minimum value is 1.` |
| `/daily-digest freshness-test --since "" "Snippet A"` | `--since requires a value. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'.` |
| `/daily-digest freshness-test --since "next tuesday" "Snippet A"` | `Could not interpret '--since next tuesday'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'.` |

**PASS Criteria** (for each error case):
- No digest file created
- Output contains the expected error string

**FAIL Criteria**:
- Digest file is created despite invalid input
- Skill silently falls back to default instead of halting
- Error message does not match expected text

---

### Freshness Scoring Reference

When running in autonomous mode (no snippets), sources are scored by publication age:

| Score | Age | Example |
|-------|-----|---------|
| 3 | < 2 days | Published yesterday |
| 2 | 2–7 days | Published last week |
| 1 | 8–30 days | Published 3 weeks ago |
| 0 | > 30 days | Published last month |
| null | No date | Undated source — included, not scored |

Freshness score influences candidate ranking but does not gate inclusion on its own (quality rubric determines inclusion). Undated sources must never be silently excluded.

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
