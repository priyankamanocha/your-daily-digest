# Spec–Implementation Alignment Report

**Generated**: 2026-03-22
**Reviewer**: /review-spec
**Spec**: `specs/daily-digest/`
**Implementation**: `.claude/skills/daily-digest/`

---

## Summary

| Dimension | Checks | PASS | GAP | MISSING |
|-----------|--------|------|-----|---------|
| Input Contract | 8 | 6 | 2 | 0 |
| Output Contract | 12 | 11 | 1 | 0 |
| Data Model | 8 | 8 | 0 | 0 |
| Architecture | 14 | 13 | 1 | 0 |
| Functional Requirements | 14 | 14 | 0 | 0 |
| **Total** | **56** | **52** | **4** | **0** |

**Overall Status**: GAPS FOUND — 4 minor gaps. All functional requirements and data model checks pass. Gaps are confined to spec documentation (input-schema.md predates the invocation layer, one output fallback message variant) and a filename convention difference in architecture.

---

## Dimension 1: Input Contract

_Compared `contracts/input-schema.md` against `scripts/validate_input.py` and `SKILL.md` (Step 0)._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Topic: required, non-empty | Two distinct errors: "topic is required" (absent/empty) / "topic cannot be empty" (whitespace-only) | `validate_input.py`: `not topic` → "topic is required"; `not topic.strip()` → "topic cannot be empty" — both messages match | PASS |
| Topic: max 100 chars | ERROR: "topic exceeds 100 characters" | `TOPIC_MAX_LEN = 100`; returns exact error string | PASS |
| Topic: alphanumeric + hyphens/underscores/spaces | `^[a-zA-Z0-9\-_ ]+$`; error: "use alphanumeric, hyphens, underscores, spaces" | Pattern matches; error string: "use alphanumeric, hyphens, underscores, spaces" — exact match | PASS |
| Hints: optional, default `[]` | Default `[]` when absent | `payload.get("hints", [])` — correct default | PASS |
| Hints: max 10 items | ERROR: "hints exceeds 10 items" | `HINTS_MAX_COUNT = 10`; returns exact string | PASS |
| Hints: each ≤ 50 chars | ERROR: `"[hint] exceeds 50 characters"` | Returns `hint "<preview>..." exceeds 50 characters` (truncated preview format differs slightly from spec) | GAP |
| Snippets: accepted for testing | Not documented in input-schema.md | Snippets are a first-class payload field with full mode-routing support; `input-schema.md` has no mention | GAP |
| Error output: single-line `Error: {error}` | `input-schema.md` says "single-line message: `Error: {error}`" | `validate_input.py` outputs JSON; `SKILL.md` Step 2 prints `Error: {error}` — matches spec | PASS |

---

## Dimension 2: Output Contract

_Compared `contracts/output-schema.md` against `resources/digest-template.md`, `scripts/build_path.py`, and `SKILL.md` Step 10._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| File path: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md` | Exact format | `build_path.py`: `f"digests/{now:%Y}/{now:%m}/digest-{now:%Y-%m-%d}-{slug}.md"` | PASS |
| Header: `# Daily Digest — {Topic}` | Exact heading | `digest-template.md`: `# Daily Digest — {Topic}` | PASS |
| Header line 2: `Generated: {YYYY-MM-DD HH:MM}` | Exact field | `digest-template.md`: `Generated: {YYYY-MM-DD HH:MM}` | PASS |
| Header line 3: `Discovery: {status}` | Exact field | `digest-template.md`: `Discovery: {complete \| partial — X unavailable \| ...}` | PASS |
| Section: `## Key Insights (1–3)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Anti-patterns (2–4)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Actions to Try (1–3)` | Exact heading | `digest-template.md`: matches | PASS |
| Section: `## Resources (3–5)` | Exact heading | `digest-template.md`: matches | PASS |
| Insight has `**Source**` and `**Evidence**: "..."` | Both fields per insight | `digest-template.md`: `**Source**: {Publication name}` + `**Evidence**: "{Quote}"` | PASS |
| Action has Effort / Time / Steps / Expected outcome | All four sub-fields | `digest-template.md`: `- Effort:`, `- Time:`, `- Steps:`, `- Expected outcome:` | PASS |
| Quality warning text matches spec exactly | `⚠️ Low-signal content — insights below represent the best available material` | `digest-template.md`: identical text | PASS |
| Failure fallback: no file + correct message | `output-schema.md`: "zero credible sources" case should include hints recovery suggestion, then snippets | `SKILL.md` Step 10 uses single message (snippets only) for all fallback cases — no hints recovery suggestion | GAP |

---

## Dimension 3: Data Model

_Compared `data-model.md` against `resources/credibility-rules.md`, `resources/freshness-policy.md`, `resources/quality-rubric.md`, and agent SOURCE formats._

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Credibility score 0–3; score < 2 excluded from insights | 0–3 scale; `< 2` excluded from Insights/Anti-patterns/Actions | `credibility-rules.md`: exact scale + exclusion rule; `SKILL.md` Step 7: "From credible sources only (score ≥ 2)" | PASS |
| Freshness: < 2 days = 3, 2–7 = 2, 8–30 = 1, > 30 = 0 | 4-band scoring table | `freshness-policy.md`: exact thresholds | PASS |
| Deduplication: rank by credibility, then freshness | Credibility first; freshness as tiebreaker | `SKILL.md` Step 7: "keep the one with the strongest evidence from the most credible source. When credibility scores are equal, prefer the fresher source." | PASS |
| Quality rubric: 4 dimensions (Novelty, Evidence, Specificity, Actionability) | 4 named dimensions, each scored 0–2 | `quality-rubric.md`: 4-column table with exact dimension names and 0/1/2 definitions | PASS |
| Quality rubric: include if ≥ 2 on ≥ 3 dimensions | Inclusion threshold | `quality-rubric.md`: "Include only insights that score 2 on ≥ 3 dimensions. No padding." | PASS |
| Web agent SOURCE: title, url, author, date, credibility_signal, summary | 6 fields, pipe-delimited | `web-discovery-agent.md`: `SOURCE: <title> \| <url> \| <author> \| <date> \| <credibility_signal> \| <summary>` | PASS |
| Video agent SOURCE: title, url, channel, date, verified/unverified, summary | 6 fields | `video-discovery-agent.md`: `SOURCE: <title> \| <url> \| <channel> \| <date> \| <verified/unverified> \| <summary>` | PASS |
| Social agent SOURCE: title, url, handle, date, verified/unverified, summary | 6 fields | `social-discovery-agent.md`: `SOURCE: <title> \| <url> \| <handle> \| <date> \| <verified/unverified> \| <summary>` | PASS |

---

## Dimension 4: Architecture

_Compared `plan.md` directory structure against actual files on disk._

| Check | Expected path (spec) | Exists? | Result |
|-------|---------------------|---------|--------|
| Orchestrator | `.claude/skills/daily-digest/daily-digest.md` | **No — actual file is `SKILL.md`** | GAP |
| Web agent | `.claude/skills/daily-digest/agents/web-discovery-agent.md` | Yes | PASS |
| Video agent | `.claude/skills/daily-digest/agents/video-discovery-agent.md` | Yes | PASS |
| Social agent | `.claude/skills/daily-digest/agents/social-discovery-agent.md` | Yes | PASS |
| check_runtime.py | `.claude/skills/daily-digest/scripts/check_runtime.py` | Yes | PASS |
| validate_input.py | `.claude/skills/daily-digest/scripts/validate_input.py` | Yes | PASS |
| build_path.py | `.claude/skills/daily-digest/scripts/build_path.py` | Yes | PASS |
| write_digest.py | `.claude/skills/daily-digest/scripts/write_digest.py` | Yes | PASS |
| credibility-rules.md | `.claude/skills/daily-digest/resources/credibility-rules.md` | Yes | PASS |
| freshness-policy.md | `.claude/skills/daily-digest/resources/freshness-policy.md` | Yes | PASS |
| quality-rubric.md | `.claude/skills/daily-digest/resources/quality-rubric.md` | Yes | PASS |
| digest-template.md | `.claude/skills/daily-digest/resources/digest-template.md` | Yes | PASS |
| Skill format: YAML frontmatter + User Input + Outline | All three required sections | `SKILL.md` has `---` YAML frontmatter (`name`, `description`), `## User Input` with `$ARGUMENTS`, `## Outline` with numbered steps | PASS |
| Scripts: I/O only, no business logic | Thin I/O wrappers | All 4 scripts contain only file/path/JSON I/O; no credibility, freshness, or rubric logic inline | PASS |

---

## Dimension 5: Functional Requirements

_Compared each FR from `spec.md` against `SKILL.md` and agent implementations._

| Requirement | Spec Definition | Implemented In | Result |
|-------------|----------------|----------------|--------|
| FR-001: Discover from web, video, social | 3 parallel agents | `SKILL.md` Step 4: "Start all three simultaneously — do not wait for one before launching the next" | PASS |
| FR-002: Synthesize into 1-3/2-4/1-3/3-5 format | Count ranges enforced | `quality-rubric.md` Final Content Counts table + `SKILL.md` Step 8 | PASS |
| FR-003: Complete within 45 seconds | 45s hard timeout | `SKILL.md` Step 4: "Proceed with whatever results are available after 45 seconds" | PASS |
| FR-004: Deduplicate near-duplicate insights | Semantic match, retain best-evidence | `SKILL.md` Step 7: "group semantically equivalent candidates, keep the one with the strongest evidence from the most credible source" | PASS |
| FR-005: Classify sources as credible/non-credible | 0–3 scale | `SKILL.md` Step 6 + `credibility-rules.md` | PASS |
| FR-006: Exclude non-credible from Insights/Anti-patterns/Actions | Score < 2 excluded | `SKILL.md` Step 7: "From credible sources only (score ≥ 2)"; `credibility-rules.md` exclusion rule | PASS |
| FR-007: May include non-credible in Resources, ranked lower | Resources exception; credible first | `SKILL.md` Step 8: "credible sources first, supplementary sources after"; `credibility-rules.md`: "Resources only, ranked below credible sources" | PASS |
| FR-008: Apply quality rubric to all insights | ≥2 on ≥3 dimensions | `SKILL.md` Step 8 references `quality-rubric.md`; rubric enforced before selection | PASS |
| FR-009: Attribute insight to highest-credibility source | `**Source**` field visible | `digest-template.md`: `**Source**: {Publication name}` per insight; Step 7 retains highest-credibility source | PASS |
| FR-010: Indicate discovery completeness | `Discovery:` line in header | `digest-template.md` header; `SKILL.md` Step 5 sets `manifest_discovery_status` string | PASS |
| FR-011: Include quality warning when low-signal | Exact `⚠️ Low-signal content...` text | `quality-rubric.md`: "add the quality warning"; `digest-template.md`: exact text | PASS |
| FR-012: Handle individual source failures gracefully | Partial status, continue with available | `SKILL.md` Step 5: `partial — {failed_agents} unavailable` status string | PASS |
| FR-013: Timeout at 45s, use partial results | Timeout → digest with warning | Step 4 proceeds at 45s; Step 5 `timeout — partial results used` | PASS |
| FR-014: Fallback when all sources fail or 0 credible | No-content fallback, no file | `SKILL.md` Step 10: message only, "Do not write a file" | PASS |

---

## Gaps & Recommended Actions

- **[D1 / Hints error message format]**: Spec says `ERROR: "[hint] exceeds 50 characters"`. Implementation returns `hint "<preview>..." exceeds 50 characters` (with a 20-char truncated preview). The message is informative but the format differs from spec. Recommended: update `input-schema.md` to document the actual format with truncated preview.

- **[D1 / Snippets undocumented]**: `contracts/input-schema.md` has no mention of the `snippets` parameter — it predates the invocation layer feature. Snippets are fully implemented with their own mode-routing path. Recommended: add a `snippets` parameter section to `input-schema.md` referencing `resources/invocation-contract.md` for the full schema.

- **[D2 / Fallback message variant]**: `output-schema.md` specifies that the "zero credible sources" fallback should include a hints recovery suggestion before the snippets suggestion. `SKILL.md` Step 10 uses a single snippets-only message for all fallback cases. Recommended: update `output-schema.md` to remove the hints suggestion from the fallback (consistent with simpler single-message approach), OR differentiate the two cases in Step 10.

- **[D4 / Orchestrator filename]**: `plan.md`, `CLAUDE.md`, and the spec's architecture section reference `.claude/skills/daily-digest/daily-digest.md` as the orchestrator. The actual file is `.claude/skills/daily-digest/SKILL.md` (speckit convention). Content is fully correct — this is a naming discrepancy only. Recommended: update `plan.md` and `CLAUDE.md` project structure to reference `SKILL.md`.

---

## Notes

- All 4 gaps are LOW severity — none affect core discovery, quality, or output functionality
- Architecture: 13/14 checks pass — all content and behaviour is correct; only filename differs from spec
- Functional Requirements: 14/14 pass — every FR is implemented
- Data Model: 8/8 pass — credibility, freshness, rubric, and agent SOURCE formats all aligned
- This report is overwritten on each run of `/review-spec`
