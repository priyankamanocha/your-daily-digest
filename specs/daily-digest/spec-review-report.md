# Spec–Implementation Alignment Report

**Generated**: 2026-03-21 14:00
**Reviewer**: /review-spec
**Spec**: `specs/daily-digest/`
**Implementation**: `.claude/skills/daily-digest/`

---

## Summary

| Dimension | Checks | PASS | GAP | MISSING |
|-----------|--------|------|-----|---------|
| Input Contract | 8 | 7 | 1 | 0 |
| Output Contract | 12 | 8 | 4 | 0 |
| Data Model | 8 | 7 | 1 | 0 |
| Architecture | 14 | 14 | 0 | 0 |
| Functional Requirements | 14 | 12 | 2 | 0 |
| **Total** | **56** | **48** | **8** | **0** |

**Overall Status**: GAPS FOUND

---

## Dimension 1: Input Contract

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Topic: required, non-empty | ✓ | `validate_input.py`: `if not topic or not topic.strip()` | PASS |
| Topic: max 100 chars | ✓ | `TOPIC_MAX_LEN = 100`, `if len(topic) > TOPIC_MAX_LEN` | PASS |
| Topic: alphanumeric + hyphens/underscores | ✓ | `r"^[a-zA-Z0-9\-_ ]+"` — regex also allows spaces | GAP |
| Hints: optional | ✓ | Optional in skill + script handles empty `hints_str` | PASS |
| Hints: max 10 items | ✓ | `HINTS_MAX_COUNT = 10` | PASS |
| Hints: each ≤ 50 chars | ✓ | `HINTS_MAX_LEN = 50` | PASS |
| Snippets: accepted for testing only | ✓ | Step 3: "manual/test mode only"; user input description explicit | PASS |
| Error output: JSON with `valid`, `error` fields | ✓ | Returns `{"valid": False, "error": "..."}` or `{"valid": True, ...}` | PASS |

---

## Dimension 2: Output Contract

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| File path: `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md` | ✓ | `output-schema.md` + `digest-template.md` both match | PASS |
| Header: `# Daily Digest — {Topic}` | ✓ | `digest-template.md` line 4: `# Daily Digest — {Topic}` | PASS |
| Header line 2: `Generated: {YYYY-MM-DD HH:MM}` | ✓ | `digest-template.md` line 6: `Generated: {YYYY-MM-DD HH:MM}` | PASS |
| Header line 3: `Discovery: {status}` | ✓ | `digest-template.md` line 7: `Discovery: {complete \| partial…}` | PASS |
| Section: `## Key Insights (1–3)` | ✓ | `output-schema.md` structure shows `### 🧠 Key Insights (1-3)`; example block shows `## 🧠 Key Insights (1-3)`; `digest-template.md` uses `## Key Insights (1–3)` (no emoji) | GAP |
| Section: `## Anti-patterns (2–4)` | ✓ | Both spec and template use `## Anti-patterns (2–4)` | PASS |
| Section: `## Actions to Try (1–3)` | ✓ | Both spec and template use `## Actions to Try (1–3)` | PASS |
| Section: `## Resources (3–5)` | ✓ | `output-schema.md` uses `### 🔗 Resources (3-5)`; `digest-template.md` uses `## Resources (3–5)` (no emoji) | GAP |
| Insight has `**Source**` and `**Evidence**: "..."` | ✓ | Both `output-schema.md` and `digest-template.md` have `**Source**` and `**Evidence**: "{Quote}"` | PASS |
| Action has Effort / Time / Steps / Expected outcome | ✓ | `output-schema.md`: `**Effort**`, `**Time**`, `**Steps**`, `**Outcome**` (bold labels); `digest-template.md`: `Effort:`, `Time:`, `Steps:`, `Expected outcome:` (plain labels; "Expected outcome" vs "Outcome") | GAP |
| Quality warning text matches spec exactly | ✓ | `spec.md` FR-011: `⚠️ Low-signal content — insights below represent the best available material`; `output-schema.md`: `⚠️ **Low-signal content** — Insights below...` (bold, capital I); `digest-template.md`: matches `spec.md` exactly | GAP |
| Failure fallback: no file created, message only | ✓ | `daily-digest.md` step 10: "Do not write a file" ✓; but `output-schema.md` fallback message says "Or switch to manual mode (optional fallback)" — contradicts spec policy that snippets are testing-only | GAP |

---

## Dimension 3: Data Model

| Check | Expected (spec) | Actual (impl) | Result |
|-------|----------------|---------------|--------|
| Credibility score 0–3, score < 2 excluded from insights | ✓ | `credibility-rules.md`: 0–3 table + "Sources scoring < 2 are excluded from Insights, Anti-patterns, and Actions" | PASS |
| Freshness: < 2 days = 3, 2–7 = 2, 8–30 = 1, > 30 = 0 | ✓ | `freshness-policy.md`: exact thresholds match `data-model.md` | PASS |
| Deduplication: rank by credibility, then freshness | ✓ | `data-model.md`: "rank by credibility score, then freshness score as tiebreaker"; `daily-digest.md` step 7: "keep the one with the strongest evidence from the most credible source" — freshness tiebreaker not mentioned | GAP |
| Quality rubric: 4 dimensions (Novelty, Evidence, Specificity, Actionability) | ✓ | `quality-rubric.md` table has exactly these 4 dimensions | PASS |
| Quality rubric: include if ≥ 2 on ≥ 3 dimensions | ✓ | `quality-rubric.md`: "Include only insights that score 2 on ≥ 3 dimensions. No padding." | PASS |
| Web agent SOURCE fields: title, url, author, date, credibility_signal, summary | ✓ | `web-discovery-agent.md` step 3 + SOURCE format: all 6 fields present | PASS |
| Video agent SOURCE fields: title, url, channel, date, verified/unverified, summary | ✓ | `video-discovery-agent.md` step 3 + SOURCE format: all 6 fields present | PASS |
| Social agent SOURCE fields: title, url, handle, date, verified/unverified, summary | ✓ | `social-discovery-agent.md` step 3 + SOURCE format: all 6 fields present | PASS |

---

## Dimension 4: Architecture

| Check | Expected path (spec) | Exists? | Result |
|-------|---------------------|---------|--------|
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
| Skill format: YAML frontmatter + User Input + Outline | ✓ | `daily-digest.md`: has `---name:…---`, `## User Input`, `## Outline` | PASS |
| Scripts: I/O only, no business logic | ✓ | Scripts handle I/O and light validation/path-generation; no discovery logic or AI reasoning in scripts | PASS |

---

## Dimension 5: Functional Requirements

| Requirement | Spec Definition | Implemented In | Result |
|-------------|----------------|----------------|--------|
| FR-001: Discover from web, video, social | 3 parallel agents | `daily-digest.md` step 4: "Start all three simultaneously" | PASS |
| FR-002: Synthesize into 1-3/2-4/1-3/3-5 format | quality-rubric.md counts | `daily-digest.md` step 8 + `quality-rubric.md` Final Content Counts | PASS |
| FR-003: Complete within 45 seconds | 45s timeout, proceed with partial | `daily-digest.md` step 4: "after **40 seconds**" | GAP |
| FR-004: Deduplicate near-duplicate insights | Semantic match, keep best-evidence | `daily-digest.md` step 7: semantic grouping, keep highest-credibility | PASS |
| FR-005: Classify sources as credible/non-credible | 0–3 scale | `credibility-rules.md`: 0–3 scoring table | PASS |
| FR-006: Exclude non-credible from insights/antipatterns/actions | Score < 2 excluded | `credibility-rules.md` + `daily-digest.md` step 7: "From credible sources only (score ≥ 2)" | PASS |
| FR-007: Allow non-credible in resources (ranked lower) | Resources section only | `credibility-rules.md` + `daily-digest.md` step 8: "credible sources first, supplementary after" | PASS |
| FR-008: Apply quality rubric to all insights | ≥2 on ≥3 dimensions | `daily-digest.md` step 8 + `quality-rubric.md` inclusion rule | PASS |
| FR-009: Attribute insight to highest-credibility source | `**Source**` field in output | `digest-template.md`: `**Source**: {Publication name}` | PASS |
| FR-010: Indicate discovery completeness | `Discovery:` line in header | `digest-template.md` + `daily-digest.md` step 5 status table | PASS |
| FR-011: Include quality warning when low-signal | `⚠️ Low-signal content…` | `daily-digest.md` step 8 + `quality-rubric.md` + `digest-template.md` | PASS |
| FR-012: Handle individual source failures gracefully | Partial status, continue with available | `daily-digest.md` step 5: 1–2 agents → `partial` status; step 4 continues with available results | PASS |
| FR-013: Timeout at 45s, use partial results | 45s timeout → digest with warning | `daily-digest.md` step 4: 40s timeout — same gap as FR-003 | GAP |
| FR-014: Fallback when all sources fail or 0 credible | No-content fallback message, no file | `daily-digest.md` step 10: fallback message + "Do not write a file" | PASS |

---

## Gaps & Recommended Actions

- **Input Contract / Topic character validation**: Spec says alphanumeric + hyphens/underscores only. `validate_input.py` regex `^[a-zA-Z0-9\-_ ]+$` also accepts spaces. Recommended: update implementation — either remove space from the regex or update spec and `input-schema.md` to explicitly allow spaces.

- **Output Contract / Key Insights section header**: `output-schema.md` structure section uses `### 🧠 Key Insights (1-3)` (level 3, emoji); example block uses `## 🧠 Key Insights (1-3)` (level 2, emoji); `digest-template.md` uses `## Key Insights (1–3)` (level 2, no emoji). Recommended: update `output-schema.md` — remove emoji and use `##` level to match implementation and spec intent.

- **Output Contract / Resources section header**: `output-schema.md` uses `### 🔗 Resources (3-5)` (level 3, emoji); `digest-template.md` uses `## Resources (3–5)` (level 2, no emoji). Recommended: update `output-schema.md` to `## Resources (3–5)`.

- **Output Contract / Action field labels**: `output-schema.md` uses bold labels (`**Effort**`, `**Time**`, `**Outcome**`); `digest-template.md` uses plain labels (`Effort:`, `Time:`, `Expected outcome:`). Label names also differ ("Outcome" vs "Expected outcome"). Recommended: update `output-schema.md` to use plain labels matching `digest-template.md`.

- **Output Contract / Quality warning text**: `output-schema.md` uses `⚠️ **Low-signal content** — Insights below represent the best available material.` (bold, capital I, trailing period); `spec.md` FR-011 and `digest-template.md` use `⚠️ Low-signal content — insights below represent the best available material` (no bold, lowercase i, no period). Recommended: update `output-schema.md` to match canonical text from `spec.md`.

- **Output Contract / Fallback message framing**: `output-schema.md` fallback message says "Or switch to manual mode (optional fallback):" suggesting snippets as a user fallback. `spec.md` states snippets are "for testing only — not a user-facing fallback". `daily-digest.md` step 10 correctly says "Try providing content manually (test mode):". Recommended: update `output-schema.md` fallback message to match the testing-only framing in `daily-digest.md` step 10.

- **Data Model / Deduplication tiebreaker**: `data-model.md` specifies "rank by credibility score, then freshness score as tiebreaker". `daily-digest.md` step 7 says "keep the one with the strongest evidence from the most credible source" — freshness as tiebreaker is not mentioned. Recommended: update `daily-digest.md` step 7 to add "use freshness score as a tiebreaker when credibility scores are equal".

- **FR-003 / FR-013 / Timeout value**: `spec.md` FR-003 and FR-013 specify the 45-second timeout. `daily-digest.md` step 4 says "Proceed with whatever results are available after **40 seconds**". Recommended: update `daily-digest.md` step 4 from "40 seconds" to "45 seconds" to match spec, or update spec if 40s is the intentional choice.

---

## Notes

- PASS: spec and implementation agree
- GAP: discrepancy found — one needs to be updated
- MISSING: defined in spec with no implementation counterpart, or vice versa
- This report is overwritten on each run
