# Spec–Implementation Alignment Report

**Generated**: 2026-03-21 (post invocation-layer implementation)
**Reviewer**: /review-spec
**Spec**: `specs/daily-digest/`
**Implementation**: `.claude/skills/daily-digest/`

---

## Summary

| Dimension | Checks | PASS | GAP | MISSING |
|-----------|--------|------|-----|---------|
| Input Contract | 8 | 3 | 5 | 0 |
| Output Contract | 12 | 11 | 1 | 0 |
| Data Model | 8 | 8 | 0 | 0 |
| Architecture | 14 | 14 | 0 | 0 |
| Functional Requirements | 14 | 14 | 0 | 0 |
| **Total** | **56** | **50** | **6** | **0** |

**Overall Status**: GAPS FOUND — all gaps are in `contracts/input-schema.md` (predates the invocation layer) and one output contract fallback message variant. Core discovery, quality, architecture, and all 14 functional requirements are fully aligned.

---

## Dimension 1: Input Contract

_Compared `contracts/input-schema.md` against `scripts/validate_input.py` and `daily-digest.md`._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Topic: required, non-empty | Two distinct messages: "topic is required" (missing) / "topic cannot be empty" (blank) | Single message: "topic is required" for both missing and blank | GAP |
| Topic: max 100 chars | ERROR: "topic exceeds 100 characters" | Returns "topic exceeds 100 characters" | PASS |
| Topic: alphanumeric + hyphens/underscores/spaces | Error message: "use alphanumeric, hyphens, underscores, spaces" | Error message omits "spaces": "use alphanumeric, hyphens, underscores" (pattern correctly allows spaces) | GAP |
| Hints: optional, default value | Example shows `"hints": null` for no hints | Defaults to `[]`; `invocation-contract.md` correctly uses `[]` | GAP (minor — functionally equivalent; `input-schema.md` example predates canonical payload) |
| Hints: max 10 items | ERROR: "hints exceeds 10 items" | Returns "hints exceeds 10 items" | PASS |
| Hints: each ≤ 50 chars | ERROR: "[hint] exceeds 50 characters" | Returns `hint "<preview>..." exceeds 50 characters` (truncated preview format) | GAP (minor — format differs; message remains informative) |
| Snippets: accepted for testing | Documented as accepted | Snippets are first-class payload field; snippets-mode routing implemented | GAP (`input-schema.md` does not document snippets at all — predates invocation layer) |
| Error output format | Multi-line: Error + Suggestion + Example lines | Single-line: `Error: {error}` only; no Suggestion or Example appended | GAP |

---

## Dimension 2: Output Contract

_Compared `contracts/output-schema.md` against `resources/digest-template.md` and `daily-digest.md` Step 10._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| File path: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md` | Exact format | `build_path.py` produces exact format | PASS |
| Header: `# Daily Digest — {Topic}` | Exact heading | `digest-template.md`: `# Daily Digest — {Topic}` | PASS |
| Header line 2: `Generated: {YYYY-MM-DD HH:MM}` | Exact field | `digest-template.md`: `Generated: {YYYY-MM-DD HH:MM}` | PASS |
| Header line 3: `Discovery: {status}` | Exact field | `digest-template.md`: `Discovery: {complete \| partial — X unavailable \| ...}` | PASS |
| Section: `## Key Insights (1–3)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Anti-patterns (2–4)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Actions to Try (1–3)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Resources (3–5)` | Exact heading | `digest-template.md`: matches | PASS |
| Insight has `**Source**` and `**Evidence**: "..."` | Both fields per insight | `digest-template.md`: both fields present | PASS |
| Action has Effort / Time / Steps / Expected outcome | All four fields | `digest-template.md`: all four fields present | PASS |
| Quality warning text matches spec exactly | `⚠️ Low-signal content — insights below represent the best available material` | `digest-template.md`: identical text | PASS |
| Failure fallback: no file + correct message | "Zero credible sources": hints suggestion + snippets suggestion. "All agents failed": snippets suggestion only. | Step 10 uses single message with snippets suggestion only for both cases | GAP |

---

## Dimension 3: Data Model

_Compared `data-model.md` against resource files and agent SOURCE formats._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Credibility score 0–3; score < 2 excluded from insights | 0–3 scale; exclusion rule | `credibility-rules.md`: exact scale + exclusion rule; Step 7: "score ≥ 2" | PASS |
| Freshness: < 2 days = 3, 2–7 = 2, 8–30 = 1, > 30 = 0 | Exact thresholds | `freshness-policy.md`: exact thresholds match | PASS |
| Deduplication: rank by credibility, then freshness | Credibility first, freshness tiebreaker | Step 7: "most credible source. When credibility scores are equal, prefer the fresher source." | PASS |
| Quality rubric: 4 dimensions (Novelty, Evidence, Specificity, Actionability) | 4 named dimensions | `quality-rubric.md`: 4-column table, exact dimension names | PASS |
| Quality rubric: include if ≥ 2 on ≥ 3 dimensions | Threshold rule | `quality-rubric.md`: "score 2 on ≥ 3 dimensions. No padding." | PASS |
| Web agent SOURCE: title, url, author, date, credibility_signal, summary | 6 fields, pipe-delimited | `web-discovery-agent.md`: `SOURCE: <title> \| <url> \| <author> \| <date> \| <credibility_signal> \| <summary>` | PASS |
| Video agent SOURCE: title, url, channel, date, verified/unverified, summary | 6 fields | `video-discovery-agent.md`: exact format | PASS |
| Social agent SOURCE: title, url, handle, date, verified/unverified, summary | 6 fields | `social-discovery-agent.md`: exact format | PASS |

---

## Dimension 4: Architecture

_Compared `plan.md` directory structure against actual files on disk._

| Check | Expected path | Exists? | Result |
|-------|--------------|---------|--------|
| Orchestrator | `.claude/skills/daily-digest/daily-digest.md` | ✅ | PASS |
| Web agent | `.claude/skills/daily-digest/agents/web-discovery-agent.md` | ✅ | PASS |
| Video agent | `.claude/skills/daily-digest/agents/video-discovery-agent.md` | ✅ | PASS |
| Social agent | `.claude/skills/daily-digest/agents/social-discovery-agent.md` | ✅ | PASS |
| check_runtime.py | `.claude/skills/daily-digest/scripts/check_runtime.py` | ✅ | PASS |
| validate_input.py | `.claude/skills/daily-digest/scripts/validate_input.py` | ✅ | PASS |
| build_path.py | `.claude/skills/daily-digest/scripts/build_path.py` | ✅ | PASS |
| write_digest.py | `.claude/skills/daily-digest/scripts/write_digest.py` | ✅ | PASS |
| credibility-rules.md | `.claude/skills/daily-digest/resources/credibility-rules.md` | ✅ | PASS |
| freshness-policy.md | `.claude/skills/daily-digest/resources/freshness-policy.md` | ✅ | PASS |
| quality-rubric.md | `.claude/skills/daily-digest/resources/quality-rubric.md` | ✅ | PASS |
| digest-template.md | `.claude/skills/daily-digest/resources/digest-template.md` | ✅ | PASS |
| Skill format: YAML frontmatter + User Input + Outline | All three required sections present | `daily-digest.md` has frontmatter (`name:`, `description:`), `## User Input` with `$ARGUMENTS`, `## Outline` with numbered steps | PASS |
| Scripts: I/O only, no business logic | Input validation, path generation, file write, runtime check | All four scripts: I/O or validation only; no discovery, scoring, or rubric logic | PASS |

---

## Dimension 5: Functional Requirements

_Compared each FR from `spec.md` against orchestrator skill and agent implementations._

| Requirement | Spec Definition | Implemented In | Result |
|-------------|----------------|----------------|--------|
| FR-001: Discover from web, video, social | 3 parallel agents | Step 4: three agents spawned simultaneously | PASS |
| FR-002: Synthesize into 1-3/2-4/1-3/3-5 format | Count ranges enforced | Step 8 + `quality-rubric.md` final counts table | PASS |
| FR-003: Complete within 45 seconds | 45s timeout | Step 4: "Proceed with whatever results are available after 45 seconds" | PASS |
| FR-004: Deduplicate near-duplicate insights | Semantic match, keep best-evidence | Step 7: group semantically equivalent, keep highest credibility then freshness | PASS |
| FR-005: Classify sources credible/non-credible | 0–3 scale | Step 6 + `credibility-rules.md` | PASS |
| FR-006: Exclude non-credible from Insights/Anti-patterns/Actions | Score < 2 excluded | Step 7: "From credible sources only (score ≥ 2)"; `credibility-rules.md` exclusion rule | PASS |
| FR-007: May include non-credible in Resources, ranked lower | Resources exception | Step 8: "credible sources first, supplementary after"; `credibility-rules.md`: "Resources only, ranked below credible" | PASS |
| FR-008: Apply quality rubric to all insights | ≥2 on ≥3 dimensions | Step 8 + `quality-rubric.md` inclusion rule | PASS |
| FR-009: Attribute insight to highest-credibility source | `**Source**` field visible | `digest-template.md`: `**Source**` per insight; Step 7 retains highest-credibility source | PASS |
| FR-010: Indicate discovery completeness | `Discovery:` line in header | `digest-template.md`: `Discovery: {status}` header field; Step 5 records status | PASS |
| FR-011: Include quality warning when low-signal | Exact warning text | Step 8: "add the quality warning"; `digest-template.md`: exact text present | PASS |
| FR-012: Handle individual source failures gracefully | Partial status, continue | Step 5: 1-2 agents → partial; Step 4: proceed with available results after timeout | PASS |
| FR-013: Timeout at 45s, use partial results | Timeout → digest with warning | Step 4 + Step 5: timeout row → "timeout — partial results used" | PASS |
| FR-014: Fallback when all sources fail or 0 credible | No-content fallback, no file | Step 10: message only, no file write | PASS |

---

## Gaps & Recommended Actions

1. **D1 / Topic empty vs missing error message** — `input-schema.md` specifies distinct messages: "topic is required" (missing) vs "topic cannot be empty" (blank). `validate_input.py` returns "topic is required" for both. **Recommended**: Update `validate_input.py` to return "topic cannot be empty" when topic is present but blank; OR update `input-schema.md` to accept a single message (simpler).

2. **D1 / Invalid-chars error omits "spaces"** — `validate_input.py` error says "use alphanumeric, hyphens, underscores" but the TOPIC_PATTERN allows spaces. **Recommended**: Update the error string to "use alphanumeric, hyphens, underscores, spaces" to match the spec and the actual pattern.

3. **D1 / `input-schema.md` does not document snippets** — `contracts/input-schema.md` predates the invocation layer feature and has no mention of snippets. **Recommended**: Add a `snippets` parameter section to `input-schema.md` (optional list of quoted strings; triggers test/manual mode; reference `resources/invocation-contract.md`).

4. **D1 / Hints default `null` vs `[]` in `input-schema.md` examples** — Example shows `"hints": null`; payload standard uses `[]`. **Recommended**: Update `input-schema.md` examples to use `"hints": []`.

5. **D1 / Error response format** — `input-schema.md` specifies multi-line error with Suggestion + Example. Orchestrator Step 2 outputs `Error: {error}` only. **Recommended**: Update `input-schema.md` to reflect the simpler single-line format (preferred for skill output).

6. **D2 / Fallback message missing hints recovery suggestion** — `output-schema.md` specifies that "zero credible sources" fallback shows a hints recovery suggestion first, then snippets. Step 10 shows only snippets for all fallback cases. **Recommended**: Either (a) update Step 10 to differentiate the two fallback cases and add the hints suggestion for "zero credible sources", OR (b) update `output-schema.md` to remove the hints suggestion from the fallback (simpler, consistent).

---

## Notes

- All 6 gaps are LOW severity — none block core discovery, quality, or output functionality
- Gaps 1–5 are all in `contracts/input-schema.md`, which predates feature 002 (invocation layer). Updating that file would bring the spec fully current with the implementation.
- Gap 6 can be resolved in either direction; the simpler single-message approach is likely preferable.
- Architecture: 14/14 checks pass — all expected files present, correct structure, scripts remain I/O-only
- Functional Requirements: 14/14 pass — all core discovery, quality, and reliability requirements are implemented
- This report is overwritten on each run of `/review-spec`
