# Automated Validation Report

**Generated**: 2026-03-22 00:05
**Skill**: `/daily-digest`
**Specification**: `specs/daily-digest/`
**Validator**: /validate-digest

---

## Sample Input Set 1: Subagents Pattern

**Input**:
- Topic: `claude-code`
- Snippets: 3 from `specs/daily-digest/benchmark.md` Sample Input Set 1
- Expected Signal: High-signal (no quality warning)

**Output File**: `digests/2026/03/digest-2026-03-22-claude-code.md`

### Automated Validation Results

| Check | Result | Details |
|-------|--------|---------|
| Structure | PASS | Header + all 5 sections present in correct order; no extras |
| Count Rules | PASS | 2 insights (1–3 ✓), 2 anti-patterns (2–4 ✓), 1 action (1–3 ✓), 3 resources (3–5 ✓) |
| Insight Evidence | PASS | Both insights contain `Evidence: "..."` with direct quotes from snippets |
| Anti-pattern Evidence | FAIL | Anti-pattern bullets use `(Snippet N)` attribution but lack an `Evidence: "..."` quoted line; output-schema does not require Evidence for anti-patterns — spec conflict (see Notes) |
| Resource Grounding | FAIL | Resource titles are descriptive summaries, not verbatim quotes from snippet text; output-schema specifies `{Title}` with no direct-quote requirement — spec conflict (see Notes) |
| Insight Titles | PASS | "Parallel Subagents Cut Multi-Source Retrieval Latency by 60%" (9 words ≤10 ✓); "Subagent Batching Sweet Spot: 3–5 Agents, 10–20 Items Each" (9 words ≤10 ✓) |
| Benchmark Expectations | PASS | 60% latency claim ✓, batching guidance (3-5 agents, 10-20 items) ✓, one-per-item anti-pattern ✓, shared-state blocking anti-pattern ✓, parallelization action ✓ |
| Quality Warning | PASS | Not present — correct for high-signal run (2 insights selected, both rubric-pass) |

### Manual Review Required

- [ ] Novelty: Are insights truly non-obvious to an experienced Claude Code user?
- [ ] Actionability: Do the 4 steps in the action lead to a measurable outcome?
- [ ] Rubric Scoring: Do both insights score ≥2 on ≥3 dimensions? (automated scoring applied: both scored 2/2/2/2)

**Reviewed By**: _[human reviewer name and date]_

---

## Sample Input Set 2: MCP Tools Pattern

**Input**:
- Topic: `mcp-tools`
- Snippets: 3 from `specs/daily-digest/benchmark.md` Sample Input Set 2
- Expected Signal: High-signal (no quality warning)

**Output File**: `digests/2026/03/digest-2026-03-22-mcp-tools.md`

### Automated Validation Results

| Check | Result | Details |
|-------|--------|---------|
| Structure | PASS | Header + all 5 sections present in correct order; no extras |
| Count Rules | PASS | 2 insights (1–3 ✓), 2 anti-patterns (2–4 ✓), 1 action (1–3 ✓), 3 resources (3–5 ✓) |
| Insight Evidence | PASS | Both insights contain `Evidence: "..."` with direct quotes from snippets |
| Anti-pattern Evidence | FAIL | Anti-pattern bullets use `(Snippet N)` attribution but lack an `Evidence: "..."` quoted line — same spec conflict as Set 1 (see Notes) |
| Resource Grounding | FAIL | Resource titles are descriptive summaries, not verbatim quotes — same spec conflict as Set 1 (see Notes) |
| Insight Titles | FAIL | Insight 2 title "MCP Adoption Is Gated by Server Availability — Custom APIs Still Need Fallback Auth" = 13 words; exceeds 10-word limit |
| Benchmark Expectations | PASS | Auth elimination claim ✓, availability caveat ✓, dependency version conflicts anti-pattern ✓, assuming-all-APIs-have-MCP anti-pattern ✓, audit-integrations action ✓ |
| Quality Warning | PASS | Not present — correct for high-signal run |

### Manual Review Required

- [ ] Novelty: Is the MCP availability caveat non-obvious to an experienced builder?
- [ ] Actionability: Does the audit action provide enough specificity for immediate execution?
- [ ] Rubric Scoring: Do both insights score ≥2 on ≥3 dimensions? (automated scoring: both scored 2/2/2/2)

**Reviewed By**: _[human reviewer name and date]_

---

## Overall Validation Result

### Automated Checks

| Dimension | Set 1 | Set 2 |
|-----------|-------|-------|
| Structure | PASS | PASS |
| Count Rules | PASS | PASS |
| Insight Evidence | PASS | PASS |
| Anti-pattern Evidence | FAIL | FAIL |
| Resource Grounding | FAIL | FAIL |
| Insight Titles | PASS | FAIL |
| Benchmark Expectations | PASS | PASS |
| Quality Warning | PASS | PASS |

- **Total Checks**: 16 (8 per input set)
- **Passed**: 11/16
- **Failed**: 5/16
- **Status**: FAIL

### Manual Review Checks

- **Total Manual Checks**: 6 (3 per input set)
- **Status**: PENDING HUMAN REVIEW

---

## Interpretation

**Status: FAIL** — 5 automated checks failed. However, 3 of the 5 failures are attributable to
spec conflicts between `/validate-digest` and `output-schema.md` rather than actual skill defects:

**Genuine failure (1):**
- Insight title length: Set 2 Insight 2 title is 13 words. The skill must produce titles ≤ 10 words.

**Spec conflicts requiring resolution (2 check types × 2 sets = 4 failures):**
- Anti-pattern Evidence: `/validate-digest` requires `Evidence: "..."` quotes in anti-pattern bullets, but `output-schema.md` formats anti-patterns as `- {Name}: {Why to avoid} ({Source})` with no Evidence field.
- Resource Grounding: `/validate-digest` requires titles to be direct quotes; `output-schema.md` specifies `{Title}` with no quote requirement. The digest-template.md and example output in output-schema both use descriptive titles.

---

## Recommended Actions

1. **Fix Set 2 Insight 2 title** — shorten to ≤10 words (e.g. "MCP Adoption Depends on Server Availability — Plan Fallback Auth" → still 10 words if counting without em-dash: "MCP Adoption Depends on Server Availability" = 6 words)
2. **Resolve spec conflict — Anti-pattern Evidence** — decide: either update output-schema to add `Evidence:` field to anti-pattern format, or update `/validate-digest` check to align with the existing format
3. **Resolve spec conflict — Resource Grounding** — decide: either require direct-quote titles (stricter, harder to satisfy in snippets mode) or update check to require only source attribution

---

## Notes

- PASS: spec and implementation agree
- FAIL: discrepancy found
- Spec conflicts: two validate-digest checks contradict output-schema.md — the underlying skill behavior is correct per output-schema; the validator is stricter than the spec it validates against
- This report is overwritten on each run
- Anti-pattern and Resource FAIL results in both sets trace to the same two spec conflicts, not independent defects

---

## Rerun Instructions

1. Fix Insight title length in skill logic (Step 8 — enforce ≤10 word limit on all titles before output)
2. Resolve spec conflicts (update either validate-digest or output-schema)
3. Run: `/validate-digest`
4. Check: `specs/daily-digest/automated-validation-report.md`
