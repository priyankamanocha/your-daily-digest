# Data Model: Source Manifest

**Branch**: `003-source-manifest` | **Spec**: [spec.md](spec.md)

---

## ManifestFile

Top-level container written to `digest-{date}-{slug}.manifest.json`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | ✅ | Schema version, e.g. `"1.0"` |
| `topic` | string | ✅ | Topic passed to the skill |
| `generated_at` | string (ISO8601) | ✅ | Timestamp matching the digest |
| `discovery_status` | enum | ✅ | `complete` \| `partial` \| `timeout` \| `manual` |
| `agents_succeeded` | string[] | ✅ | Subset of `["web", "video", "social"]` |
| `agents_failed` | string[] | ✅ | Agents that did not return results (empty if all succeeded) |
| `quality_warning` | boolean | ✅ | `true` if the quality warning appeared in the digest |
| `sources` | SourceRecord[] | ✅ | All sources discovered by all agents |
| `deduplication_groups` | DeduplicationGroup[] | ✅ | All dedup groups (empty if no merges occurred) |
| `candidates` | CandidateRecord[] | ✅ | All deduplicated insight candidates before quality filter |
| `section_selections` | SectionSelections | ✅ | Final items selected for each digest section |

---

## SourceRecord

One entry per source returned by a discovery agent (or per snippet in manual mode).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | ✅ | Canonical URL |
| `title` | string | ✅ | Page/video/post title |
| `source_type` | enum | ✅ | `web` \| `video` \| `social` \| `snippet` |
| `agent` | enum | ✅ | `web` \| `video` \| `social` \| `manual` |
| `author_or_handle` | string | ✅ | Byline, channel name, or @handle |
| `date` | string (ISO8601) | ✅ | Publication date; `null` if unavailable |
| `days_old` | integer | ✅ | Days since publication; `null` if date unavailable |
| `credibility_score` | integer (0–3) or null | ✅ | Credibility score per `credibility-rules.md`; `null` for snippets |
| `credibility_signal` | string | ✅ | Observable signal used to assign score; `null` for snippets |
| `freshness_score` | integer (0–3) or null | ✅ | Freshness score per `freshness-policy.md`; `null` if date unavailable |
| `summary` | string | ✅ | 2–3 sentence summary from the agent |

---

## DeduplicationGroup

One entry per set of semantically equivalent candidates that were merged.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `group_id` | string | ✅ | Unique identifier, e.g. `"g001"` |
| `candidate_urls` | string[] | ✅ | All source URLs in the group |
| `winner_url` | string | ✅ | URL of the retained candidate |
| `reason` | string | ✅ | Human-readable explanation, e.g. `"Higher credibility (3 vs 2)"` |

**Constraint**: Only sources involved in at least one merge appear here. Unique candidates are not listed.

---

## CandidateRecord

One entry per candidate insight after deduplication, before the quality rubric filter.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ | Candidate insight title (5–10 words) |
| `primary_source_url` | string | ✅ | Highest-credibility source URL |
| `credibility_score` | integer (0–3) | ✅ | Score of primary source |
| `freshness_score` | integer (0–3) | ✅ | Freshness score of primary source |
| `quality_scores` | QualityScores | ✅ | Per-dimension rubric scores |
| `quality_pass` | boolean | ✅ | `true` if ≥2 on ≥3 dimensions |
| `rejection_reason` | string or null | ✅ | Which dimensions failed; `null` if `quality_pass` is `true` |

### QualityScores (nested object)

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `novelty` | integer | 0–2 | Rubric dimension score |
| `evidence` | integer | 0–2 | Rubric dimension score |
| `specificity` | integer | 0–2 | Rubric dimension score |
| `actionability` | integer | 0–2 | Rubric dimension score |

---

## SectionSelections

Final items written to each digest section.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key_insights` | SelectionItem[] | ✅ | 1–3 items (empty list if none passed rubric) |
| `antipatterns` | SelectionItem[] | ✅ | 2–4 items |
| `actions` | SelectionItem[] | ✅ | 1–3 items |
| `resources` | SelectionItem[] | ✅ | 3–5 items |

### SelectionItem (nested object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ | Title as it appears in the digest |
| `primary_source_url` | string | ✅ | Source URL supporting this item |

---

## Validation Rules

| Field | Constraint |
|-------|-----------|
| `schema_version` | Non-empty string; currently `"1.0"` |
| `discovery_status` | Must be one of `complete`, `partial`, `timeout`, `manual` |
| `credibility_score` | 0, 1, 2, or 3 — or `null` (snippets only) |
| `freshness_score` | 0, 1, 2, or 3 — or `null` (date unavailable) |
| `quality_scores.*` | 0, 1, or 2 |
| `section_selections.*` | Lists may be empty; no upper-bound enforcement in the manifest itself |
| File path | `{digest_path_without_extension}.manifest.json` |

---

## Example Manifest (abbreviated)

```json
{
  "schema_version": "1.0",
  "topic": "claude-code",
  "generated_at": "2026-03-21T14:30:00",
  "discovery_status": "complete",
  "agents_succeeded": ["web", "video", "social"],
  "agents_failed": [],
  "quality_warning": false,
  "sources": [
    {
      "url": "https://docs.anthropic.com/claude-code",
      "title": "Claude Code Documentation",
      "source_type": "web",
      "agent": "web",
      "author_or_handle": "Anthropic",
      "date": "2026-03-20",
      "days_old": 1,
      "credibility_score": 3,
      "credibility_signal": "Official primary source",
      "freshness_score": 3,
      "summary": "Official documentation for Claude Code..."
    }
  ],
  "deduplication_groups": [
    {
      "group_id": "g001",
      "candidate_urls": ["https://source-a.com", "https://source-b.com"],
      "winner_url": "https://source-a.com",
      "reason": "Higher credibility (3 vs 2)"
    }
  ],
  "candidates": [
    {
      "title": "Subagents Enable Parallel Task Execution",
      "primary_source_url": "https://docs.anthropic.com/claude-code",
      "credibility_score": 3,
      "freshness_score": 3,
      "quality_scores": {"novelty": 2, "evidence": 2, "specificity": 2, "actionability": 1},
      "quality_pass": true,
      "rejection_reason": null
    }
  ],
  "section_selections": {
    "key_insights": [{"title": "Subagents Enable Parallel Task Execution", "primary_source_url": "https://docs.anthropic.com/claude-code"}],
    "antipatterns": [{"title": "Sequential Discovery", "primary_source_url": "https://source-c.com"}],
    "actions": [{"title": "Implement Parallel Discovery in Your Skill", "primary_source_url": "https://docs.anthropic.com/claude-code"}],
    "resources": [{"title": "Claude Code Documentation", "primary_source_url": "https://docs.anthropic.com/claude-code"}]
  }
}
```
