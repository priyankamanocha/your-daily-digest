# Data Model: Phase 2 Autonomous Discovery

**Purpose**: Define entities flowing through parallel discovery agents and orchestrator

---

## Core Entities

### InputRequest
User invocation of Phase 2 autonomous discovery

**Fields**:
- `topic` (string, required): Topic for discovery (e.g., "claude-code", "subagents")
- `hints` (list[string], optional): Curated sources to prioritize
  - YouTube channel names (e.g., "Anthropic", "@user_channel")
  - X/Twitter usernames (e.g., "@anthropic", "@author")

**Validation**:
- topic: non-empty, max 100 characters
- hints: max 10 items, each max 50 characters

---

### DiscoveredSource
Raw content discovered by individual agent

**Fields**:
- `url` (string): Source URL
- `title` (string): Content title
- `content` (string): Raw or parsed content text
- `source_type` (enum): "web" | "video" | "social"
- `author` (string): Author/publisher/channel name
- `published_date` (string, ISO8601): Publication date if available
- `days_old` (number): Days since publication (calculated as today - published_date)
- `freshness_score` (number): 0-3 based on days_old (see Freshness Policy below)
- `credibility_signal` (string): Observable signal (verified account, official publication, etc.)

**Agent Responsibility**:
- Web agent returns: articles, blog posts, documentation
- Video agent returns: video transcripts, descriptions
- Social agent returns: tweets, posts, thread content

---

### CandidateInsight
Proposed insight extracted from discovered source(s)

**Fields**:
- `title` (string): Insight title (5-10 words)
- `description` (string): What/why/how (2-3 sentences)
- `evidence` (string): Direct quote from source
- `source_urls` (list[string]): URLs supporting this insight
- `source_types` (list[enum]): ["web", "video", "social"] — which sources contributed
- `published_date` (string, ISO8601): Most recent publication date among sources
- `days_old` (number): Days since most recent source was published
- `credibility_score` (number): 0-3 (observable signals from sources)
- `freshness_score` (number): 0-3 (0=stale >30 days, 1=moderate 8-30 days, 2=fresh 2-7 days, 3=very fresh <2 days)
- `specificity_score` (number): 0-3 (concrete vs generic)
- `engagement_score` (number): 0-2 (author authority, community validation)
- `combined_score` (number): credibility + freshness + specificity + engagement (max 11)

**Deduplication**: Group by semantic equivalence; retain highest-scoring version

---

### DeduplicatedInsight
Post-deduplication insight (one entry per unique insight)

**Fields**:
- `title` (string)
- `description` (string)
- `evidence` (string)
- `primary_source_url` (string): Highest-credibility source
- `contributing_sources` (list): All sources that mentioned this insight
- `quality_scores` (object): {novelty, evidence, specificity, actionability} → 0-2 each
- `quality_pass` (boolean): Passes MVP rubric (≥2 on ≥3 dimensions)

---

### DiscoveryResult
Aggregated results from all 3 agents (before deduplication)

**Fields**:
- `topic` (string)
- `hints` (list[string]): Original input hints
- `raw_sources` (list[DiscoveredSource]): All sources from 3 agents
- `candidate_insights` (list[CandidateInsight]): All proposed insights
- `execution_time_ms` (number): Total discovery time
- `agents_succeeded` (list[string]): ["web", "video", "social"] or subset if failures
- `completion_status` (enum): "complete" | "partial" | "timeout"

---

### FinalDigest
Output digest matching MVP format

**Fields**:
- `topic` (string)
- `generated_at` (string, ISO8601): Generation timestamp
- `insights` (list): 1-3 insights (from DeduplicatedInsight, MVP quality rubric enforced)
- `antipatterns` (list): 2-4 anti-patterns (why to avoid + evidence)
- `actions` (list): 1-3 actions (effort level, time estimate, steps, outcome)
- `resources` (list): 3-5 resources (credible first, then supplementary)
- `discovery_status` (string): "Complete" | "Incomplete: [source] unavailable" | "Timeout: partial results"
- `quality_warning` (string, optional): "⚠️ Low-signal content..." if <3 credible sources
- `file_path` (string): Output path (digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic}.md)

**MVP Integration**: FinalDigest structure identical to MVP output; reuses MVP quality rubric and insight extraction

---

## Data Flow

```
InputRequest
  ↓
Web Agent → DiscoveredSource[] (8-15 sources)
Video Agent → DiscoveredSource[] (6-12 sources)
Social Agent → DiscoveredSource[] (5-10 sources)
  ↓
Orchestrator merges → DiscoveryResult (all raw sources)
  ↓
Extract CandidateInsight[] (20-40 proposals)
  ↓
Deduplication → DeduplicatedInsight[] (8-12 unique)
  ↓
Quality Filter (MVP rubric) → Selected insights
  ↓
MVP Insight Extraction → FinalDigest
  ↓
Output: Markdown file (digests/{YYYY}/{MM}/...)
```

---

## Freshness Policy

**Requirement**: System must prefer sources from last N days to ensure discovery captures recent, relevant content.

### Freshness Scoring

**Freshness Score** (0-3) based on publication recency:

| Days Old | Score | Category | Handling |
|----------|-------|----------|----------|
| **< 2 days** | 3 | Very Fresh | Prioritize (breaking news, latest developments) |
| **2-7 days** | 2 | Fresh | Standard priority (recent but not bleeding-edge) |
| **8-30 days** | 1 | Moderate | Lower priority (older but potentially still relevant) |
| **> 30 days** | 0 | Stale | Deprioritize (likely outdated, archived) |

### Application in Deduplication & Selection

**During deduplication**:
1. Group semantically identical insights
2. Within each group, rank by `combined_score` (credibility + **freshness** + specificity + engagement)
3. Retain highest-scoring version (prefer fresh over stale duplicates)

**During quality filtering**:
- Freshness is part of candidate ranking
- Multiple insights on same topic? Prefer fresher sources
- Stale insights (>30 days) only included if no fresh alternatives available

### Discovery Agent Behavior

**Web Agent**:
- Prioritize results from last 7 days (filter by publication date)
- Include older sources (8-30 days) if high relevance
- Exclude sources >30 days old unless topic-specific

**Video Agent**:
- Prioritize videos published in last 30 days (shorter window for video content)
- Include archived content only if no recent equivalents

**Social Agent**:
- Prioritize posts from last 7 days (fast-moving platform)
- Retweets/quotes count as "fresh" if recent, even if original is older

### Edge Cases

| Scenario | Handling |
|----------|----------|
| **All sources >30 days old** | Include best-available with quality warning |
| **Mix of fresh + stale for same insight** | Use fresh source, note in evidence |
| **Breaking news (<2 days old)** | Prioritize, include in digest even if limited corroboration |
| **Date unavailable** | Treat as moderate (score=1) to avoid bias |

---

## Constraints & Validation Rules

| Entity | Constraint |
|--------|-----------|
| **InputRequest.topic** | Non-empty, max 100 chars, alphanumeric + hyphens |
| **InputRequest.hints** | Max 10 items, each max 50 chars |
| **DiscoveredSource.content** | Max 5000 chars (truncate if needed) |
| **CandidateInsight** | Evidence must be direct quote from source |
| **DeduplicatedInsight.quality_pass** | ≥2 score on ≥3 dimensions (novelty, evidence, specificity, actionability) |
| **FinalDigest.insights** | 1-3 items (or 0 if all fail rubric) |
| **FinalDigest.file_path** | digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.md |

---

## Notes

- All timestamps are ISO8601 format
- All text fields are UTF-8
- URLs are absolute (http/https)
- Deduplication happens **before** MVP quality rubric (dedup groups raw candidates, then rubric selects from groups)
- If <3 credible sources discovered, FinalDigest includes quality_warning
- If 0 credible sources, return fallback message (no digest file created)
