# /review-spec: Spec–Implementation Alignment Review

## Purpose

Review whether the `daily-digest` skill implementation matches its specification.
Produces a structured gap report across five dimensions:
input contract, output contract, data model, architecture, and functional requirements.

---

## Execution Flow

### Step 1: Load Spec Files

Read all of the following. Stop and report any missing file.

- `specs/daily-digest/spec.md` — functional requirements (FR-001–FR-014), success criteria (SC-001–SC-008)
- `specs/daily-digest/plan.md` — architecture decisions, directory structure
- `specs/daily-digest/data-model.md` — entities, field definitions, scoring rules
- `specs/daily-digest/contracts/input-schema.md` — input validation rules
- `specs/daily-digest/contracts/output-schema.md` — output format contract
- `specs/daily-digest/tasks.md` — implementation task completion status

---

### Step 2: Load Implementation Files

Read all of the following. Note any that are missing.

- `.claude/skills/daily-digest/daily-digest.md`
- `.claude/skills/daily-digest/agents/web-discovery-agent.md`
- `.claude/skills/daily-digest/agents/video-discovery-agent.md`
- `.claude/skills/daily-digest/agents/social-discovery-agent.md`
- `.claude/skills/daily-digest/scripts/validate_input.py`
- `.claude/skills/daily-digest/scripts/build_path.py`
- `.claude/skills/daily-digest/scripts/write_digest.py`
- `.claude/skills/daily-digest/scripts/check_runtime.py`
- `.claude/skills/daily-digest/resources/credibility-rules.md`
- `.claude/skills/daily-digest/resources/freshness-policy.md`
- `.claude/skills/daily-digest/resources/quality-rubric.md`
- `.claude/skills/daily-digest/resources/digest-template.md`

---

### Step 3: Run Alignment Checks

Work through each dimension below. For every check, assign one of:
- **PASS** — spec and implementation agree
- **GAP** — spec says X, implementation does Y (describe the difference)
- **MISSING** — spec defines something with no corresponding implementation, or vice versa

#### Dimension 1: Input Contract

Compare `contracts/input-schema.md` against `scripts/validate_input.py` and `daily-digest.md`.

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Topic: required, non-empty | ✓ | ? | ? |
| Topic: max 100 chars | ✓ | ? | ? |
| Topic: alphanumeric + hyphens/underscores | ✓ | ? | ? |
| Hints: optional | ✓ | ? | ? |
| Hints: max 10 items | ✓ | ? | ? |
| Hints: each ≤ 50 chars | ✓ | ? | ? |
| Snippets: accepted for testing only | ✓ | ? | ? |
| Error output: JSON with `valid`, `error` fields | ✓ | ? | ? |

#### Dimension 2: Output Contract

Compare `contracts/output-schema.md` against `resources/digest-template.md` and `scripts/write_digest.py`.

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| File path: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md` | ✓ | ? | ? |
| Header: `# Daily Digest — {Topic}` | ✓ | ? | ? |
| Header line 2: `Generated: {YYYY-MM-DD HH:MM}` | ✓ | ? | ? |
| Header line 3: `Discovery: {status}` | ✓ | ? | ? |
| Section: `## Key Insights (1–3)` | ✓ | ? | ? |
| Section: `## Anti-patterns (2–4)` | ✓ | ? | ? |
| Section: `## Actions to Try (1–3)` | ✓ | ? | ? |
| Section: `## Resources (3–5)` | ✓ | ? | ? |
| Insight has `**Source**` and `**Evidence**: "..."` | ✓ | ? | ? |
| Action has Effort / Time / Steps / Expected outcome | ✓ | ? | ? |
| Quality warning text matches spec exactly | ✓ | ? | ? |
| Failure fallback: no file created, message only | ✓ | ? | ? |

#### Dimension 3: Data Model

Compare `data-model.md` against `resources/credibility-rules.md`, `resources/freshness-policy.md`, `resources/quality-rubric.md`, and agent SOURCE: line formats.

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Credibility score 0–3, score < 2 excluded from insights | ✓ | ? | ? |
| Freshness: < 2 days = 3, 2–7 = 2, 8–30 = 1, > 30 = 0 | ✓ | ? | ? |
| Deduplication: rank by credibility, then freshness | ✓ | ? | ? |
| Quality rubric: 4 dimensions (Novelty, Evidence, Specificity, Actionability) | ✓ | ? | ? |
| Quality rubric: include if ≥ 2 on ≥ 3 dimensions | ✓ | ? | ? |
| Web agent SOURCE fields: title, url, author, date, credibility_signal, summary | ✓ | ? | ? |
| Video agent SOURCE fields: title, url, channel, date, verified/unverified, summary | ✓ | ? | ? |
| Social agent SOURCE fields: title, url, handle, date, verified/unverified, summary | ✓ | ? | ? |

#### Dimension 4: Architecture

Compare `plan.md` directory structure against actual files on disk.

| Check | Expected path (spec) | Exists? | Result |
|-------|---------------------|---------|--------|
| Orchestrator | `.claude/skills/daily-digest/daily-digest.md` | ? | ? |
| Web agent | `.claude/skills/daily-digest/agents/web-discovery-agent.md` | ? | ? |
| Video agent | `.claude/skills/daily-digest/agents/video-discovery-agent.md` | ? | ? |
| Social agent | `.claude/skills/daily-digest/agents/social-discovery-agent.md` | ? | ? |
| check_runtime.py | `.claude/skills/daily-digest/scripts/check_runtime.py` | ? | ? |
| validate_input.py | `.claude/skills/daily-digest/scripts/validate_input.py` | ? | ? |
| build_path.py | `.claude/skills/daily-digest/scripts/build_path.py` | ? | ? |
| write_digest.py | `.claude/skills/daily-digest/scripts/write_digest.py` | ? | ? |
| credibility-rules.md | `.claude/skills/daily-digest/resources/credibility-rules.md` | ? | ? |
| freshness-policy.md | `.claude/skills/daily-digest/resources/freshness-policy.md` | ? | ? |
| quality-rubric.md | `.claude/skills/daily-digest/resources/quality-rubric.md` | ? | ? |
| digest-template.md | `.claude/skills/daily-digest/resources/digest-template.md` | ? | ? |
| Skill format: YAML frontmatter + User Input + Outline | ✓ | ? | ? |
| Scripts: I/O only, no business logic | ✓ | ? | ? |

#### Dimension 5: Functional Requirements

Compare each FR from `spec.md` against the orchestrator skill and agent implementations.

| Requirement | Spec Definition | Implemented In | Result |
|-------------|----------------|----------------|--------|
| FR-001: Discover from web, video, social | 3 parallel agents | agents/ | ? |
| FR-002: Synthesize into 1-3/2-4/1-3/3-5 format | quality-rubric.md counts | quality-rubric.md + step 8 | ? |
| FR-003: Complete within 45 seconds | 40s timeout, proceed with partial | Step 4 in daily-digest.md | ? |
| FR-004: Deduplicate near-duplicate insights | Semantic match, keep best-evidence | Step 7 in daily-digest.md | ? |
| FR-005: Classify sources as credible/non-credible | 0–3 scale | credibility-rules.md | ? |
| FR-006: Exclude non-credible from insights/antipatterns/actions | Score < 2 excluded | Steps 6–8 | ? |
| FR-007: Allow non-credible in resources (ranked lower) | Resources section only | Step 8 | ? |
| FR-008: Apply quality rubric to all insights | ≥2 on ≥3 dimensions | quality-rubric.md | ? |
| FR-009: Attribute insight to highest-credibility source | `**Source**` field in output | digest-template.md | ? |
| FR-010: Indicate discovery completeness | `Discovery:` line in header | digest-template.md | ? |
| FR-011: Include quality warning when low-signal | `⚠️ Low-signal content...` | digest-template.md | ? |
| FR-012: Handle individual source failures gracefully | Partial status, continue with available | Steps 4–5 | ? |
| FR-013: Timeout at 45s, use partial results | Timeout → digest with warning | Steps 4–5 | ? |
| FR-014: Fallback when all sources fail or 0 credible | No-content fallback message | Step 10 | ? |

---

### Step 4: Write Gap Report

Write the completed report to `specs/daily-digest/spec-review-report.md`:

```markdown
# Spec–Implementation Alignment Report

**Generated**: {YYYY-MM-DD HH:MM}
**Reviewer**: /review-spec
**Spec**: `specs/daily-digest/`
**Implementation**: `.claude/skills/daily-digest/`

---

## Summary

| Dimension | Checks | PASS | GAP | MISSING |
|-----------|--------|------|-----|---------|
| Input Contract | 8 | ? | ? | ? |
| Output Contract | 12 | ? | ? | ? |
| Data Model | 8 | ? | ? | ? |
| Architecture | 14 | ? | ? | ? |
| Functional Requirements | 14 | ? | ? | ? |
| **Total** | **56** | **?** | **?** | **?** |

**Overall Status**: ALIGNED / GAPS FOUND / CRITICAL GAPS

---

## Dimension 1: Input Contract

{Filled table from Step 3}

---

## Dimension 2: Output Contract

{Filled table from Step 3}

---

## Dimension 3: Data Model

{Filled table from Step 3}

---

## Dimension 4: Architecture

{Filled table from Step 3}

---

## Dimension 5: Functional Requirements

{Filled table from Step 3}

---

## Gaps & Recommended Actions

{For each GAP or MISSING result, one bullet:}
- **[Dimension / Check]**: Spec says `{X}`. Implementation has `{Y}`. Recommended: {update spec | update implementation | investigate}.

---

## Notes

- PASS: spec and implementation agree
- GAP: discrepancy found — one needs to be updated
- MISSING: defined in spec with no implementation counterpart, or vice versa
- This report is overwritten on each run
```

---

### Step 5: Output Summary

Print to user:

```
✅ Review Complete

Input Contract:          ?/8  PASS
Output Contract:         ?/12 PASS
Data Model:              ?/8  PASS
Architecture:            ?/14 PASS
Functional Requirements: ?/14 PASS

Total: ?/56 checks passed

Status: ALIGNED / GAPS FOUND / CRITICAL GAPS

Full report: specs/daily-digest/spec-review-report.md
```

If any GAPs or MISSING results exist, also print:

```
Gaps found:
- {brief description of each gap}

Recommended next step: Address gaps in [spec | implementation], then rerun /review-spec.
```

---

## Error Handling

- **Missing spec file**: Stop, report which file is missing, suggest running `/speckit.plan` to regenerate
- **Missing implementation file**: Record as MISSING in architecture dimension, continue other checks
- **Cannot determine result for a check**: Mark as `NEEDS MANUAL REVIEW` with explanation; do not force PASS or GAP
