# Manifest Schema Reference

The sidecar manifest (`digest-{date}-{slug}.manifest.json`) is written alongside every digest by `scripts/write_manifest.py`. It records every source, deduplication decision, candidate quality score, and final section selection for a single digest run.

---

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `"1.0"` | Schema version — always `"1.0"` for this release |
| `topic` | string | Topic passed to the skill (from validated payload) |
| `generated_at` | string (ISO8601) | Timestamp matching the `Generated:` line in the digest |
| `discovery_status` | enum | `complete` \| `partial — {agents} unavailable` \| `timeout — partial results used` \| `manual` |
| `agents_succeeded` | string[] | Agents that returned results — subset of `["web", "video", "social"]` |
| `agents_failed` | string[] | Agents that failed or timed out — empty if all succeeded |
| `quality_warning` | boolean | `true` if the quality warning line was added to the digest |
| `sources` | SourceRecord[] | All sources from all agents (see below) |
| `deduplication_groups` | DeduplicationGroup[] | Merge decisions (empty if no duplicates found) |
| `candidates` | CandidateRecord[] | All deduplicated candidates before quality filter |
| `section_selections` | SectionSelections | Final items per digest section |

---

## SourceRecord

Collected in Step 4 from each agent's `SOURCE:` lines; scores added in Steps 5–6.

```json
{
  "url": "https://example.com/article",
  "title": "Page or video title",
  "source_type": "web",
  "agent": "web",
  "author_or_handle": "Author Name or @handle",
  "date": "2026-03-20",
  "days_old": 2,
  "credibility_score": 3,
  "credibility_signal": "Major publication",
  "freshness_score": 2,
  "summary": "2-3 sentence summary from the agent."
}
```

| Field | Type | Notes |
|-------|------|-------|
| `source_type` | enum | `web` \| `video` \| `social` \| `snippet` |
| `agent` | enum | `web` \| `video` \| `social` \| `manual` |
| `date` | string or null | ISO8601 date; `null` if not available |
| `days_old` | integer or null | Days since publication; `null` if date unavailable |
| `credibility_score` | 0–3 or null | Per `credibility-rules.md`; `null` for snippets |
| `credibility_signal` | string or null | Observable trust indicator; `null` for snippets |
| `freshness_score` | 0–3 or null | Per `freshness-policy.md`; `null` if date unavailable |
| `filter_action` | enum or null | `"blocked"` \| `"boosted"` \| `"unaffected"`; `null` for legacy manifests. Blocked sources remain in `sources` but are absent from `candidates`. |

---

## DeduplicationGroup

Recorded in Step 7 for each set of semantically equivalent candidates that were merged.

```json
{
  "group_id": "g001",
  "candidate_urls": ["https://source-a.com", "https://source-b.com"],
  "winner_url": "https://source-a.com",
  "reason": "Higher credibility (3 vs 2)"
}
```

Only sources involved in a merge appear here. Unique candidates are absent from this array.

---

## CandidateRecord

Recorded in Step 7–8 for each deduplicated candidate, including those that failed the quality rubric.

```json
{
  "title": "Candidate insight title (5-20 words)",
  "primary_source_url": "https://highest-credibility-source.com",
  "credibility_score": 3,
  "freshness_score": 2,
  "quality_scores": {
    "novelty": 2,
    "evidence": 2,
    "specificity": 1,
    "actionability": 2
  },
  "quality_pass": true,
  "rejection_reason": null
}
```

| Field | Notes |
|-------|-------|
| `quality_scores.*` | Each dimension: 0, 1, or 2 per quality-rubric.md |
| `quality_pass` | `true` if score is 2 on ≥3 dimensions |
| `rejection_reason` | Which dimensions scored below 2; `null` if `quality_pass` is `true` |

---

## SectionSelections

Recorded in Step 8 as final content is selected. Lists may be empty if a section fell below its minimum.

```json
{
  "key_insights": [
    {"title": "Insight title", "primary_source_url": "https://source.com"}
  ],
  "antipatterns": [
    {"title": "Anti-pattern name", "primary_source_url": "https://source.com"}
  ],
  "actions": [
    {"title": "Action title", "primary_source_url": "https://source.com"}
  ],
  "resources": [
    {"title": "Resource title", "primary_source_url": "https://source.com"}
  ]
}
```

---

## Snippets Mode

When snippets are provided (manual/test mode), each snippet becomes a synthetic SourceRecord:

```json
{
  "url": null,
  "title": "Snippet 1",
  "source_type": "snippet",
  "agent": "manual",
  "author_or_handle": null,
  "date": null,
  "days_old": 0,
  "credibility_score": null,
  "credibility_signal": null,
  "freshness_score": null,
  "summary": "<snippet text>"
}
```

`discovery_status` is `"manual"`. `deduplication_groups` is `[]`.

---

## File Path Contract

```
digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.manifest.json
```

Always co-located with its digest. Derived by `write_manifest.py` replacing `.md` with `.manifest.json`.
