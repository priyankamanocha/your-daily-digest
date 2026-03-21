# /validate-digest: Automated MVP Validation

## Purpose

Automatically validate `/daily-digest` skill output against MVP specifications:
- `specs/000-mvp-manual-digest/benchmark.md` (expected outputs)
- `specs/000-mvp-manual-digest/contracts/digest-output-schema.md` (output format)
- `specs/000-mvp-manual-digest/data-model.md` (quality rubric)

Generate a structured validation report with pass/fail criteria.

---

## Execution Flow

### Step 1: Load Specification Files

Read:
- `specs/000-mvp-manual-digest/benchmark.md` (expected outputs for Sample Input Sets 1 & 2)
- `specs/000-mvp-manual-digest/contracts/digest-output-schema.md` (output schema and validation rules)
- `specs/000-mvp-manual-digest/data-model.md` (quality rubric: 4 dimensions, ≥3 score rule)
- `.claude/commands/daily-digest.md` (skill implementation)

Stop if any file is missing.

### Step 2: Run /daily-digest Against Benchmark Inputs

**Sample Input Set 1 (Subagents Pattern)**:
```
Topic: "claude-code"
Snippet 1: [from benchmark.md - "Subagents in Claude Code enable parallel execution..."]
Snippet 2: [from benchmark.md - "I used subagents to parallelize a content retrieval task..."]
Snippet 3: [from benchmark.md - "Subagents are powerful but easy to misuse..."]
```

**Sample Input Set 2 (MCP Tools Pattern)**:
```
Topic: "mcp-tools"
Snippet 1: [from benchmark.md - "MCP (Model Context Protocol) tools abstract away authentication..."]
Snippet 2: [from benchmark.md - "I tried using three different Python HTTP libraries..."]
Snippet 3: [from benchmark.md - "Not all APIs have MCP servers yet..."]
```

For each run:
- Capture generated digest file path
- Capture generation timestamp
- Note any errors or failures

### Step 3: Validate Structure

**PASS Criteria** (automated check):
- File exists at expected path: `digests/{YYYY}/{MM}/digest-{YYYY}-{MM}-{DD}-{topic-slug}.md`
- Markdown contains exactly these sections (in order):
  1. `# Daily Digest — {Topic}`
  2. `Generated: {YYYY-MM-DD HH:MM}`
  3. `## Key Insights (1-3)`
  4. `## Anti-patterns (2-4)`
  5. `## Actions to Try (1-3)`
  6. `## Resources (3-5)`
- No extra metadata or scheduling fields

**FAIL Criteria**:
- File missing or at wrong path
- Any required section missing
- Extra sections present (except quality warning)

### Step 4: Validate Count Rules

**High-Signal Run** (normal case - no quality warning):

**PASS Criteria**:
- Insights: Count = 1, 2, or 3 (not 0, not >3)
- Anti-patterns: Count = 2, 3, or 4 (not 0-1, not >4)
- Actions: Count = 1, 2, or 3 (not 0, not >3)
- Resources: Count = 3, 4, or 5 (not 0-2, not >5)
- Quality warning: NOT present

**FAIL Criteria**:
- Any count outside required range
- Quality warning present when no low-signal content

**Low-Signal Run** (exception case - has quality warning):

**PASS Criteria**:
- Quality warning present: `⚠️ Low-signal content — insights below represent the best available material`
- Insights: Count ≥ 1 (may be < 3)
- Anti-patterns: Count ≥ 2 (may be < 4)
- Actions: Count ≥ 1 (may be < 3)
- Resources: Count ≥ 3 (may be < 5)
- All content is best-available (no padding)

**FAIL Criteria**:
- Quality warning missing when counts below minimums
- Any padding detected (weak insights forced into output)

**Manual Review Required**:
- Detect if low-signal via count checks, but determining "no padding" requires human judgment

### Step 5: Validate Evidence

**PASS Criteria** (automated check):
- All insights: Contain `Evidence: "..."` with quoted text from provided snippets
- All anti-patterns: Contain `Evidence: "..."` with full-sentence quote from provided content
- All resources: Title is direct quote or literal phrase from provided content
- All actions: Linked to insights logically (can verify "Effort:", "Time:", "Steps:", "Expected outcome:" present)

**FAIL Criteria**:
- Any insight missing Evidence
- Any anti-pattern missing full-sentence quote
- Any resource title that is paraphrased or synthesized
- Any action missing effort/time/steps/outcome

**Manual Review Required**:
- Whether quotes actually support the claim (semantic accuracy)

### Step 6: Validate Titles

**PASS Criteria** (automated check):
- Insight titles: Count words in each title, verify all ≤ 10 words
- Format: Title is within `### [title]` markers

**FAIL Criteria**:
- Any insight title > 10 words
- Title format incorrect

### Step 7: Validate Against Benchmark Expectations

**Sample Input Set 1 Expected Outputs** (from benchmark.md):

Insights should include:
- ✓ Latency reduction claim (60% for parallel vs sequential)
- ✓ Batching guidance (3-5 subagents, 10-20 items)

Anti-patterns should include:
- ✓ One-subagent-per-item overhead
- ✓ Shared-state blocking

Actions should include:
- ✓ Parallelization strategy
- ✓ Batching optimization

Resources should reference:
- ✓ Subagent parallelism for multi-source
- ✓ Independent scopes requirement
- ✓ Batching strategy

**Sample Input Set 2 Expected Outputs** (from benchmark.md):

Insights should include:
- ✓ Authentication elimination claim
- ✓ Tool availability caveat

Anti-patterns should include:
- ✓ Dependency version conflicts
- ✓ Assuming all APIs have MCP servers

Actions should include:
- ✓ Audit API integrations
- ✓ Plan fallback auth

Resources should reference:
- ✓ MCP eliminating auth complexity
- ✓ Tool availability dependency

**PASS Criteria**:
- For high-signal content, benchmark expectations matched (✓ marks above present in output)

**FAIL Criteria**:
- Key insights from benchmark missing
- Expected anti-patterns not identified

**Manual Review Required**:
- Whether extracted insights are truly non-obvious (vs obvious from content)
- Whether insights answer what/why/how (rubric scoring)

### Step 8: Create Validation Report

Generate `specs/000-mvp-manual-digest/automated-validation-report.md`:

```markdown
# Automated Validation Report

**Generated**: {current timestamp}
**MVP Component**: `/daily-digest` skill
**Specification Version**: 2026-03-21
**Validator**: /validate-digest

---

## Sample Input Set 1: Subagents Pattern

**Input**:
- Topic: `claude-code`
- Snippets: 3 from `specs/000-mvp-manual-digest/benchmark.md` Sample Input Set 1
- Expected Signal: High-signal (no quality warning)

**Output File**: `digests/2026/03/digest-2026-03-21-claude-code.md`

### Automated Validation Results

| Check | Result | Details |
|-------|--------|---------|
| Structure | PASS/FAIL | All 5 sections present in correct order |
| Count Rules | PASS/FAIL | 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources |
| Insight Evidence | PASS/FAIL | All insights have quoted evidence |
| Anti-pattern Evidence | PASS/FAIL | All anti-patterns have full-sentence quotes |
| Resource Grounding | PASS/FAIL | All resource titles are direct quotes from content |
| Insight Titles | PASS/FAIL | All insight titles ≤ 10 words |
| Benchmark Expectations | PASS/FAIL | Key insights/anti-patterns/resources match benchmark |
| Quality Warning | PASS/FAIL | Not present (high-signal) |

### Manual Review Required

- [ ] Novelty: Are insights truly non-obvious?
- [ ] Actionability: Do actions have clear next steps?
- [ ] Rubric Scoring: Do insights score ≥2 on ≥3 dimensions?

**Reviewed By**: [human reviewer name and date]

---

## Sample Input Set 2: MCP Tools Pattern

**Input**:
- Topic: `mcp-tools`
- Snippets: 3 from `specs/000-mvp-manual-digest/benchmark.md` Sample Input Set 2
- Expected Signal: High-signal (no quality warning)

**Output File**: `digests/2026/03/digest-2026-03-21-mcp-tools.md`

### Automated Validation Results

| Check | Result | Details |
|-------|--------|---------|
| Structure | PASS/FAIL | All 5 sections present in correct order |
| Count Rules | PASS/FAIL | 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources |
| Insight Evidence | PASS/FAIL | All insights have quoted evidence |
| Anti-pattern Evidence | PASS/FAIL | All anti-patterns have full-sentence quotes |
| Resource Grounding | PASS/FAIL | All resource titles are direct quotes from content |
| Insight Titles | PASS/FAIL | All insight titles ≤ 10 words |
| Benchmark Expectations | PASS/FAIL | Key insights/anti-patterns/resources match benchmark |
| Quality Warning | PASS/FAIL | Not present (high-signal) |

### Manual Review Required

- [ ] Novelty: Are insights truly non-obvious?
- [ ] Actionability: Do actions have clear next steps?
- [ ] Rubric Scoring: Do insights score ≥2 on ≥3 dimensions?

**Reviewed By**: [human reviewer name and date]

---

## Overall Validation Result

### Automated Checks
- **Total Checks**: 16 (8 per Sample Input Set)
- **Passed**: X/16
- **Failed**: Y/16
- **Status**: PASS / FAIL

### Manual Review Checks
- **Total Manual Checks**: 6 (3 per Sample Input Set)
- **Status**: PENDING HUMAN REVIEW

---

## Interpretation

**PASS**: All automated checks passed AND manual review approved
**FAIL**: One or more automated checks failed (fix daily-digest.md and rerun)
**PENDING**: Automated checks passed, awaiting manual review

---

## Rerun Instructions

To validate again:

1. Update `/daily-digest` logic if needed (fix in `.claude/commands/daily-digest.md`)
2. Run: `/validate-digest`
3. Check: `specs/000-mvp-manual-digest/automated-validation-report.md`
4. If FAIL on automated checks: Iterate on skill and rerun
5. If PENDING: Complete manual review checklist

---

## Notes

- Automated checks are fully repeatable and deterministic
- Manual review checks require human judgment and cannot be fully automated
- This report is generated automatically; updates with each run
- Do not modify this file manually (it is overwritten by /validate-digest)
```

### Step 9: Summary and Status

Output to user:
```
✅ Validation Complete

Sample Input Set 1 (Subagents): PASS / FAIL
Sample Input Set 2 (MCP Tools): PASS / FAIL

Full Report: specs/000-mvp-manual-digest/automated-validation-report.md

Automated Checks: X/16 PASS
Manual Review: PENDING / APPROVED / FAILED

Next: [If PASS] MVP is validated. If FAIL, address issues in daily-digest.md and rerun.
```

---

## Error Handling

**If `/daily-digest` fails to run**:
- Stop execution
- Report error: "Cannot run /daily-digest. Check: topic format, snippet word counts, file permissions"
- Suggest: "Verify .claude/commands/daily-digest.md is executable"

**If benchmark.md is missing**:
- Stop execution
- Report error: "Cannot load specs/000-mvp-manual-digest/benchmark.md. File missing."

**If output file path is wrong**:
- Stop execution
- Report error: "Generated file not at expected path. Check daily-digest.md timestamp and slug generation logic"

**If a check cannot be automated**:
- Mark as "Manual Review Required" in report
- List specific criteria that need human judgment
- Do not skip the check or force an automated result

---

## Output Requirements

- ✅ Repeatable and deterministic (same inputs → same results)
- ✅ Fully automated for structural/count/evidence checks
- ✅ Explicit escape hatch for non-automatable rules ("Manual Review Required")
- ✅ Structured report format (table-based, easy to scan)
- ✅ No scope changes (only validate, do not fix)
- ✅ Timestamp every run
- ✅ Clear PASS/FAIL/PENDING status

