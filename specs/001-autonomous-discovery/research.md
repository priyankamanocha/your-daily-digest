# Phase 2 Research: Autonomous Content Discovery Implementation

**Date**: 2026-03-21
**Phase**: 2 (Post-MVP)
**Purpose**: Technical research findings for Phase 2 autonomous discovery design decisions.
**Status**: Research Complete

## Overview

This document provides technical findings and decisions for implementing Phase 2 Autonomous Content Discovery within Claude Code's single-skill constraint. Four core areas are addressed:

1. **Discovery Source Integration** — How to access web, video, and social media content
2. **Content Access** — Efficient multi-source fetching within 45-second latency budget
3. **Deduplication Strategy** — Identifying semantically identical insights without ML models
4. **Quality Signal Detection** — Scoring source credibility and content relevance via prompts

---

## 1. Discovery Source Integration

### Decision: Layered MCP + WebSearch + Fallback Pattern

**Recommended approach**: Implement a prioritized discovery layer that:
1. **Primary**: Use Claude's native `web_search` tool (available in Claude Code)
2. **Secondary**: Use `fetch` tool (MCP or built-in) for direct URL fetching when web search returns promising URLs
3. **Tertiary**: Leverage community-maintained MCP servers for specialized sources (Twitter, YouTube) if available
4. **Fallback**: Graceful degradation to manual mode when discovery unavailable

### Rationale

**Why this approach fits MVP constraints:**

- **No external code files**: All logic lives in the skill prompt. Discovery tool invocations are native Claude Code operations, not external dependencies.
- **No infrastructure**: Web search and fetch tools are already available within Claude Code; no new services to deploy or configure.
- **Single skill**: All discovery orchestration happens in one skill file (`daily-digest.md`), maintaining the MVP pattern.
- **Bounded complexity**: The skill's prompt handles discovery orchestration; the tools themselves (web_search, fetch) are blackboxes.
- **Latency-compatible**: Web search and fetch operations complete in <5 seconds typically, leaving 40 seconds for deduplication and insight generation within the 45-second budget.

**How discovery works in practice:**

```
Input: /daily-digest claude-code
  ↓
1. Topic Interpretation [Prompt-based]
   - Parse topic → extract keywords, subtopics, related domains
   - Example: "claude-code" → ["Claude Code", "subagents", "MCP", "skills", "hooks", "Claude Code usage patterns"]
  ↓
2. Web Search [Native tool]
   - Execute 3-5 parallel searches using interpreted keywords
   - Query examples: "Claude Code subagents pattern", "MCP integration Claude Code", "Claude Code skills advanced"
   - Limit to 10-20 results total (avoid noise)
  ↓
3. Content Fetch [Native fetch tool]
   - From search results, fetch top 5-10 URLs (in parallel or rapid sequence)
   - Parse HTML → markdown (Claude's fetch tool does this automatically)
   - Aggregate all fetched content for deduplication
  ↓
4. Social/Video Fallback [MCP if available, else skip]
   - Attempt to query Twitter/YouTube via MCP if available
   - These are optional; if unavailable, system continues with web content only
  ↓
5. Deduplication & Quality Scoring [Prompt-based]
   - Analyze aggregated content for duplicate insights
   - Score source credibility and content relevance
   - Apply MVP quality rubric
  ↓
6. Insight Extraction & Digest Generation [Reuse MVP engine]
   - Apply same insight extraction logic as MVP
   - Generate markdown output
```

### Alternatives Considered

**Alternative 1: Direct API integration (Twitter API, YouTube API)**
- ❌ **Rejected**: Requires API key management, SDK dependencies, and external authentication. Violates MVP constraint (no external code files, no dependency management). Phase 2 is still a single skill.
- **How we chose differently**: MCP abstraction removes API key management from the skill itself—the skill just calls MCP, and MCP handles auth.

**Alternative 2: MCP-only approach (all discovery via MCP servers)**
- ⚠️ **Partially viable**: Works if all required MCPs are available, but creates fragility around MCP availability. If Twitter MCP is down, entire discovery fails.
- **How we chose differently**: Layered approach uses web search as primary (always available), MCP as secondary (nice-to-have). Graceful degradation: if Twitter MCP unavailable, still get web + YouTube results.

**Alternative 3: Autonomous web scraping (direct HTML parsing)**
- ❌ **Rejected**: Violates terms of service for most sites, requires robust parsing logic (brittle across site layout changes), and doesn't scale. MVP constraint eliminates custom code.
- **How we chose differently**: Fetch tool handles parsing; no custom scraping code needed.

**Alternative 4: Federated model (multiple parallel discovery subagents)**
- ⚠️ **Future consideration**: Could parallelize discovery (subagent for web, subagent for Twitter, subagent for YouTube), but adds orchestration complexity. MVP constraint favors single skill.
- **How we chose differently**: Phase 2 keeps discovery single-skill; if latency becomes bottleneck (>45s), Phase 3 could introduce subagents for parallelization.

### Implementation Implications

**Key challenges & how to address them:**

1. **Web search result quality**: General web searches return mixed signal (tutorials, news, low-quality blogs).
   - **Mitigation**: Use specific search queries (keywords + operator words like "pattern", "advanced", "best practices"). Prioritize recent content (web_search tool returns sorted by relevance + recency).

2. **Content parsing from diverse sources**: HTML from blogs, Twitter threads, YouTube transcripts—all different formats.
   - **Mitigation**: Fetch tool normalizes to markdown. Prompt-based deduplication is format-agnostic (works on any text).

3. **Rate limiting**: Multiple fetches could hit rate limits.
   - **Mitigation**: Limit to 10 total fetches per discovery run, distributed across domains. 45-second timeout naturally bounds aggressive fetching.

4. **False positives in deduplication**: Similar-sounding insights may differ subtly.
   - **Mitigation**: Prompt-based semantic matching with explicit guidance: "Consider insights semantically identical if they describe the same underlying practice, even if phrased differently. Retain the version with strongest evidence."

---

## 2. Content Access

### Decision: Parallel Fetch with Timeout Guard

**Recommended approach:**
1. Execute 5-10 fetch operations in rapid succession (not strict parallelism, but non-blocking sequencing)
2. Aggregate fetched content into a unified corpus
3. Hard timeout at 45 seconds; use best-available content if cutoff reached
4. Content parsing handled automatically by fetch tool (HTML → markdown)

### Rationale

**Why this approach fits MVP constraints:**

- **Simple orchestration**: No complex async frameworks or threading. Single prompt can invoke multiple fetch operations in sequence, waiting for each result.
- **Bounded latency**: Web search typically completes in 2-3 seconds. Fetching 5-10 URLs at ~2 seconds each = 10-20 seconds total. Leaves 20-25 seconds for deduplication and insight generation. Well within 45-second budget.
- **Automatic parsing**: Fetch tool returns markdown, not raw HTML. No custom parsing logic needed.
- **Graceful degradation**: If a single fetch times out or fails, system continues with remaining results. No need for retry logic; MVP treats failures as "skip and move on."

**Latency analysis:**

```
Web search queries: 2-3 seconds total
├─ Query 1: "Claude Code subagents pattern"
├─ Query 2: "MCP integration Claude Code"
└─ Query 3: "Claude Code skills advanced"

Content fetch: 10-20 seconds (5-10 URLs at ~2s each)
├─ URL 1: Fetch & parse → markdown
├─ URL 2: Fetch & parse → markdown
├─ ...
└─ URL 10: Fetch & parse → markdown

Deduplication & scoring: 10-15 seconds
├─ Semantic analysis of all content
├─ Source credibility assessment
├─ Quality rubric application
└─ Insight extraction (reuse MVP engine)

Markdown generation & file write: 2-3 seconds

TOTAL: 24-41 seconds (well under 45s target)
```

### Content Aggregation Strategy

**How to structure the aggregated corpus for efficient deduplication:**

Instead of treating each fetched document as separate, normalize them into a unified "sources index":

```
AggregatedContent:
  - source_1:
      url: "https://..."
      title: "extracted from page"
      content: "[parsed markdown]"
      credibility: "high|medium|low"  # assessed by prompt
      publication_date: "extracted or inferred"
      domain: "extracted from URL"
  - source_2: ...
  - ...

Then, deduplication logic analyzes all sources together:
"Across all 8 sources, identify unique insights.
 If the same pattern appears in source_1 and source_5,
 report it once, attributed to the more credible source."
```

### Alternatives Considered

**Alternative 1: Strict parallel fetches (async/await or concurrent execution)**
- ⚠️ **Partially viable**: Faster (could complete in 5-8 seconds), but requires careful timeout handling and error aggregation.
- **How we chose differently**: Sequential fetch is simpler to implement in a prompt; 10-20 seconds total is acceptable within 45s budget. Simplicity is more valuable than 5-second improvement.

**Alternative 2: Paginated search results (fetch multiple pages)**
- ❌ **Rejected**: Web search results pages degrade in quality quickly. Top 10-20 results capture the high-signal content; pagination adds noise without benefit. 45s budget doesn't allow fetching 50+ results.
- **How we chose differently**: Limit to top 10-20 results per search, fetch top 5-10 of those. Depth over breadth.

**Alternative 3: Stream processing (process content as it arrives, not after all fetches complete)**
- ⚠️ **Future optimization**: Could improve latency by starting deduplication while fetches are in-flight, but adds state management complexity.
- **How we chose differently**: MVP approach: gather all content first, then process holistically. Simpler logic, good-enough latency.

**Alternative 4: Full-page traversal (follow links from landing pages to discover more content)**
- ❌ **Rejected**: Combinatorial explosion; 45s budget is insufficient. Violates "avoid excessive breadth" principle.
- **How we chose differently**: Single-hop fetching only (search results → fetch landing pages, not their outbound links).

### Implementation Implications

**Key challenges & how to address them:**

1. **Timeout handling**: Fetch operation hangs or exceeds timeout.
   - **Mitigation**: Use hard 45-second global timeout. If any fetch takes >5 seconds, skip and continue. After 40 seconds of elapsed time, stop fetching and move to deduplication phase.

2. **Content volume**: Aggregating 10 URLs worth of content could exceed Claude's context window.
   - **Mitigation**: Summarize fetched content within each source (extract key paragraphs/sections, not full text). Prompt can include guidance: "For each source, extract insights, quotes, and metadata. Omit boilerplate, headers, footers. Aim for 500-1000 words per source."

3. **Duplicated content across sources**: Different URLs pointing to same article (shared via multiple domains, cached versions, etc.).
   - **Mitigation**: Deduplication prompt includes: "If two sources contain identical or near-identical text blocks, treat as single source, attribute to original domain."

4. **Encoding/parsing errors**: Some pages may have encoding issues, missing content, or unstructured HTML.
   - **Mitigation**: Fetch tool's markdown conversion is robust for common cases. For failure cases, skip that source (no error). Prompt guidance: "If content is unreadable or empty, ignore that source and continue with others."

---

## 3. Deduplication Strategy

### Decision: Prompt-Based Semantic Matching with Heuristic Scoring

**Recommended approach:**
1. Use Claude's reasoning to identify semantically identical or near-identical insights across all discovered sources
2. Apply simple heuristics to select "best-evidence version" (credibility, specificity, engagement signals)
3. No embeddings, no ML models—pure prompt-based comparison
4. Maintain evidence trails (which sources support each insight) for attribution

### Rationale

**Why this approach fits MVP constraints:**

- **No external dependencies**: Deduplication is pure reasoning within the prompt. No vector databases, no embedding models, no external ML APIs.
- **Handles semantic similarity**: Claude understands that "using subagents for modularity" and "decompose work into parallel subagents" are the same insight despite different wording.
- **Simple to implement**: Prompt can explicitly list comparison rules: "Identify insights that describe the same underlying practice, even if phrased differently. When duplicates found, score each version on credibility and evidence; retain highest-scoring version."
- **Scalable to MVP data volumes**: 8-15 sources → 10-40 candidate insights → likely 3-7 unique insights after deduplication. Small enough for prompt-based analysis.
- **Auditable**: Unlike ML-based clustering, deduplication decisions are transparent in the prompt output ("Insights A and B are identical because...").

**Deduplication process:**

```
1. Content Aggregation
   ├─ 8-10 fetched sources (with metadata: URL, credibility, date)
   └─ 20-40 candidate insights extracted via initial analysis

2. Semantic Grouping [Prompt-based]
   ├─ Read all candidate insights
   ├─ For each pair, ask: "Are these describing the same practice?"
   ├─ Build groups of related insights
   └─ Example: Group A = {Insight_1, Insight_5, Insight_12} (all about "subagent modularity")

3. Best-Evidence Selection [Heuristic scoring]
   ├─ For each group, score each insight version:
   │  ├─ Credibility of source (domain reputation, author verification)
   │  ├─ Specificity of evidence (concrete example > abstract statement)
   │  ├─ Engagement signal (mentions, shares, comments if available)
   │  └─ Freshness (more recent = slightly higher score)
   ├─ Retain highest-scoring version
   └─ Example: In group A, Insight_5 (from Anthropic blog) scores highest → keep Insight_5, discard Insight_1 and Insight_12

4. Attribution Tracking
   ├─ For each retained insight, list all sources that support it
   ├─ Tag with credibility of each supporting source
   └─ Example: Insight_5 is supported by [source_5 (high), source_1 (medium), source_12 (medium)]

5. Output
   ├─ 3-7 unique insights (after deduplication) with best-evidence versions
   └─ User digest credits highest-credibility supporting source for each insight
```

### Heuristic Scoring for "Best-Evidence Version"

**Deduplication score** = Credibility + Specificity + Engagement (equal weight)

```
Credibility (0-3):
  3 = Official/verified source (Anthropic blog, author GitHub, published docs)
  2 = Established outlet (tech blog, research paper, verified expert)
  1 = Community source (Twitter verified, Medium, substack)
  0 = Unverified (anonymous forums, low-reputation blogs)

Specificity (0-3):
  3 = Concrete example + code/screenshot + clear steps
  2 = Concrete example + clear explanation
  1 = General technique or pattern
  0 = Abstract observation

Engagement (0-2):
  2 = High engagement (1000+ views, 100+ comments, multiple shares)
  1 = Moderate engagement (100-1000 views, 10-100 comments)
  0 = Low or unmeasured engagement

Final Score: Credibility + Specificity + Engagement
  Range: 0-8
  Threshold: Insights scoring ≥5 are included in digest
```

Example:
```
Insight "Subagents enable parallel task decomposition":

Version A (source_1 = Twitter, unknown author):
  Credibility: 0
  Specificity: 1 (mentions "parallel tasks" but no example)
  Engagement: 0 (2 likes)
  Score: 1 → DISCARD

Version B (source_5 = Anthropic blog, official Anthropic author):
  Credibility: 3
  Specificity: 3 (includes code example, architecture diagram, step-by-step guide)
  Engagement: 2 (1200 views, 50 comments)
  Score: 8 → KEEP (also apply MVP quality rubric)

Version C (source_12 = Tech blog, well-known blogger):
  Credibility: 2
  Specificity: 2 (clear explanation, no code)
  Engagement: 1 (200 views, 5 comments)
  Score: 5 → DISCARD (lower than B)

Result: Digest includes Version B, attributed to "Anthropic blog (official)"
        Supporting sources: Tech blog, Twitter user
```

### Alternatives Considered

**Alternative 1: Vector embeddings + cosine similarity**
- ❌ **Rejected**: Requires external embedding API (OpenAI, Hugging Face, or local model). Violates MVP constraint (no external APIs). Also requires vector database for storage/similarity search.
- **How we chose differently**: Prompt-based semantic matching is built-in; no external dependency.

**Alternative 2: Exact string matching (fuzzy string distance)**
- ❌ **Rejected**: Only catches nearly-identical text. Misses semantic duplicates ("use subagents for modularity" vs. "decompose into parallel subagents"). Too strict.
- **How we chose differently**: Claude's reasoning catches semantic equivalence; stricter but more accurate.

**Alternative 3: Keyword overlap heuristic (shared words = same insight)**
- ⚠️ **Partially viable**: Fast and simple, but many false positives. "MCP is useful" and "MCP is challenging" both contain "MCP" but are opposite insights.
- **How we chose differently**: Prompt-based reasoning understands semantic meaning, not just keyword overlap.

**Alternative 4: No deduplication (keep all insights, let user filter)**
- ❌ **Rejected**: Violates MVP quality bar. Digest would show same insight 3 times from different sources, breaking the "1-3 insights" contract and confusing users.
- **How we chose differently**: Deduplication is a must-have for digest quality.

**Alternative 5: Keep all versions, score them differently (don't merge)**
- ⚠️ **Considered briefly**: Show insight with multiple sources, different confidence levels. Too verbose; defeats purpose of digest (signal over noise).
- **How we chose differently**: Merge into single insight with highest-credibility source; mention other supporting sources in parentheses if space allows.

### Implementation Implications

**Key challenges & how to address them:**

1. **Pairwise comparison scaling**: With 40 candidate insights, comparing all pairs is O(n²) = 1600 comparisons.
   - **Mitigation**: Prompt can be efficient: ask Claude to "group similar insights, not compare all pairs exhaustively." Natural language grouping is faster than brute-force comparison. Expected 3-5 groups from 40 insights.

2. **Ambiguous similarity**: Some insights are partially related but not identical.
   - **Mitigation**: Define clear threshold: "Merge insights only if they describe the same underlying practice. Related practices (e.g., 'use subagents' and 'use skills') are separate insights."

3. **Evidence loss**: When merging insight A and B, evidence from both sources should be attributed.
   - **Mitigation**: After deduplication, prompt maintains a mapping: "Insight_merged supports [source_A, source_B, source_C]. Most credible source: source_A."

4. **Scoring subjectivity**: "Credibility" and "specificity" scores are heuristics, not objective.
   - **Mitigation**: Prompt includes explicit scoring rubric. Scores are reproducible (same insight + same sources = same score). Acceptable for MVP (post-MVP could train classifier if needed).

---

## 4. Quality Signal Detection

### Decision: Prompt-Based Source Classification + Engagement Heuristics

**Recommended approach:**
1. Classify sources as credible or non-credible using explicit URL/domain/author patterns
2. Apply engagement heuristics (recency, view counts, comments) when available
3. Apply MVP quality rubric (novelty, evidence, specificity, actionability) to every insight
4. Use prompt-based reasoning to assess relevance to topic

### Rationale

**Why this approach fits MVP constraints:**

- **No external ML models**: Credibility assessment uses simple heuristics (domain patterns, author verification) and prompt-based reasoning (topic relevance). No external classifiers.
- **Observable signals**: Source credibility is based on URL patterns, domain reputation, author attributes—all visible in the content. No hidden scores.
- **Reuses MVP quality rubric**: Phase 2 applies same 4-dimensional rubric as MVP (novelty, evidence, specificity, actionability). No new evaluation logic.
- **Transparent to users**: Digest can show which sources are credible and which are supporting. Users understand why certain insights are included/excluded.

### Source Credibility Classification

**Two-tier system: Credible vs. Non-Credible**

**Credible sources** (insights drawn only from these):
- Official/verified sources:
  - Anthropic blog, official documentation, GitHub repos (for Claude Code)
  - Official social accounts (Twitter/X verified, author bio matches known person)
  - Published research (arXiv, academic venues, conference papers)
- Established outlets:
  - Tech publications with editorial standards (TechCrunch, Wired, MIT Tech Review)
  - Well-known engineering blogs (Stripe blog, Vercel blog, etc.)
  - Prominent individual contributors with verified identity and track record
- Proxies for credibility:
  - High engagement (1000+ views, 100+ comments) = crowd validation
  - Longevity (content from established domains, not new)
  - Author reputation (author has >1000 followers, verified history)

**Non-credible sources** (excluded from insights; may appear in Resources section only, ranked below credible):
- Promotional/marketing content:
  - Vendor marketing blogs (tool company promoting its own tool)
  - Sponsored content, affiliate posts
- Unverified/low-reputation:
  - Anonymous blogs, pseudonymous forums
  - Very new domains (registered <1 year ago)
  - Sites with high spam signals (keyword stuffing, ad density)
- Beginner-level content:
  - "Getting started" guides, install tutorials, basic how-tos
  - Content with "beginner" or "intro" in title
  - Educational material (not practical patterns)

**Implementation in prompt:**

```
Assess each discovered source:

Source Classification Prompt:
---
For each source, determine credibility:

1. URL/Domain Analysis:
   - Is it an official domain? (e.g., anthropic.com)
   - Is it a known tech publication? (e.g., stripe.com/blog)
   - Is domain reputation high? (established since >1 year ago)
   Result: high | medium | low

2. Author Analysis (if available):
   - Author verified or well-known? (Twitter verified, GitHub contributor, etc.)
   - Author bio indicates relevant expertise?
   Result: high | medium | low

3. Engagement Signals (if available):
   - Views/impressions: >1000 = high, 100-1000 = medium, <100 = low
   - Comments/discussion: >100 = high, 10-100 = medium, <10 = low
   - Timestamp: <7 days old = high recency, <30 days = medium, >30 days = low
   Result: Combine signals → adjust credibility up/down

4. Content Type Check:
   - Is content beginner-level? (install, basic tutorial) → reduce credibility
   - Is content promotional/vendor marketing? → reduce credibility to low
   - Is content concrete/actionable with examples? → increase credibility

Final Classification:
  credibility = high | medium | low

Rule for Insights:
  - Use only high and medium credibility sources
  - If insight from low-credibility source, flag for user review or discard
  - Exception: If a low-credibility insight has high engagement + official source co-occurrence, escalate to medium

---
```

### Engagement Signal Detection

**When engagement data is available (tweets, YouTube comments, blog view counts):**

```
Engagement Scoring (0-2 scale):

Views/Impressions:
  2 = >1000 views
  1 = 100-1000 views
  0 = <100 views

Interaction (comments, shares, replies):
  2 = >100 interactions
  1 = 10-100 interactions
  0 = <10 interactions

Recency (for time-sensitive content):
  2 = <7 days old
  1 = 7-30 days old
  0 = >30 days old

Engagement Total = Views + Interactions + Recency
  Range: 0-6

Usage: High engagement (4-6) escalates source credibility if borderline.
       Example: Low-credibility source with 5000 views and 500 comments
               → treat as medium-credibility for this digest run.
```

### Topic Relevance Assessment

**Ensure discovered content is genuinely about the specified topic, not adjacent:**

```
Topic Relevance Rubric:

Input: topic = "Claude Code", source = [URL + extracted content]

Questions to assess:
1. Does content explicitly mention the core topic or its direct subtopics?
   - Example for "Claude Code": mentions "Claude Code", "subagents", "skills", "MCP"
   - YES = high relevance (3 points)
   - MAYBE = mentions related but distinct concepts (e.g., "LLM agents" without "Claude Code") (1 point)
   - NO = not about topic (0 points)

2. Is content actionable for practitioners in this topic area?
   - Example for "Claude Code": teaches a technique usable in Claude Code development
   - YES = high relevance (2 points)
   - MAYBE = tangentially relevant (1 point)
   - NO = irrelevant (0 points)

3. Is content focused (on-topic) or tangential (mentions as aside)?
   - Dedicated section to topic = 2 points
   - Mentioned in passing = 1 point
   - Not mentioned = 0 points

Total Relevance Score: 0-7
  6+ = Include in digest
  3-5 = Marginal; apply quality rubric strictly
  <3 = Exclude

Prompt Guidance:
"When relevance score <6, apply quality rubric strictly (require score ≥6 on rubric).
 When relevance score ≥6, standard quality rubric applies (≥5 out of 8)."
```

### Quality Rubric Application (Reuse from MVP)

**Each insight MUST be evaluated on 4 dimensions:**

```
Rubric (from MVP daily-digest.md):

Dimension | Score 0 (Reject) | Score 1 (Weak) | Score 2 (Include)
----------|------------------|----------------|------------------
Novelty | Known/obvious | Somewhat new | New + non-obvious
Evidence | None | Mentioned | Direct quote
Specificity | Generic | Somewhat | Concrete + actionable
Actionability | Observation | Implies action | Clear next step

Inclusion Rule: Include insight ONLY if:
  - Scores 2 on ≥3 dimensions, OR
  - Scores 1-2 on all 4 dimensions AND credible source AND high engagement

No padding: Output best available insights, even if <3 total.
```

### Alternatives Considered

**Alternative 1: ML-based credibility model (train classifier on labeled sources)**
- ❌ **Rejected**: Requires training data, labeled examples, and inference API. Violates MVP constraint (no external ML, no training infrastructure).
- **How we chose differently**: Heuristic-based classification is fast, observable, and no training required.

**Alternative 2: Whitelist/blacklist maintained by user**
- ⚠️ **Future consideration**: Could maintain a JSON file of trusted sources + banned sources, but adds state management and requires user curation.
- **How we chose differently**: MVP uses heuristics; Phase 3 could introduce user-maintained lists if needed.

**Alternative 3: Authority signals via link analysis (pagerank-style)**
- ⚠️ **Theoretically sound**: Inbound link count is a signal of authority, but requires crawling or external graph data. Complex to implement in prompt.
- **How we chose differently**: Domain reputation + author verification is sufficient proxy for MVP.

**Alternative 4: No source classification (all sources equal weight)**
- ❌ **Rejected**: Violates spec requirement (FR-005, FR-006): "System MUST classify sources as credible or non-credible." Would allow spam to inflate insight counts.
- **How we chose differently**: Classification is mandatory per spec.

### Implementation Implications

**Key challenges & how to address them:**

1. **Subjective credibility assessment**: "Credible" is a judgment call; different raters might disagree.
   - **Mitigation**: Prompt includes explicit heuristics (URL patterns, author verification). Decisions are reproducible and auditable. MVP quality bar is acceptable (not ML-precise, but good-enough for user value).

2. **Missing engagement data**: Some sources (blogs, niche forums) don't expose view counts or comment counts.
   - **Mitigation**: Engagement signals are optional. Credibility assessment proceeds on domain + author alone if engagement data unavailable.

3. **Gaming and spoofing**: Fraudulent sources can fake credibility signals (fake followers, purchased views).
   - **Mitigation**: This is a long-term problem; MVP assumes most sources are honest. Phase 3 could add fraud detection if needed.

4. **Topic drift**: Content is tangentially related but not on-topic (e.g., "AI ethics in Claude" is adjacent to "Claude Code," but not directly actionable).
   - **Mitigation**: Topic relevance rubric filters these out. Prompt includes clear examples of on-topic vs. off-topic content for the specified topic.

5. **Recency tradeoff**: Very recent content (breaking news) may have low engagement simply because it's new.
   - **Mitigation**: Recency is one factor; offset by credibility + topic relevance. Recent + credible source = worth including even if engagement low. Prompt guidance: "Recent content from high-credibility sources should be included; engagement signals take longer to accumulate."

---

## Integration Summary

### How These Four Areas Work Together

```
Phase 2 Discovery Flow:

Input: /daily-digest claude-code
  ↓
[1] Topic Interpretation (Prompt-based)
    → Keywords: ["Claude Code", "subagents", "skills", "MCP", ...]
  ↓
[2] Discovery (Web Search + Fetch)
    → 5-10 URLs fetched, content aggregated
  ↓
[4] Quality Signal Detection
    → Source classification (credible vs. non-credible)
    → Engagement scoring where available
    → Topic relevance assessment
    → Content credibility: HIGH, MEDIUM, LOW
  ↓
[3] Deduplication (Prompt-based semantic matching)
    → Group similar insights
    → Select best-evidence version per group
    → Maintain source attribution
  ↓
[Reuse MVP Engine]
    → Apply quality rubric (novelty, evidence, specificity, actionability)
    → Filter insights (score ≥5/8 for high-quality sources, ≥6/8 for medium/low)
    → Generate 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
  ↓
Output: Markdown digest file with source attribution
```

### Single-Skill Architecture

All four areas are implemented **within a single skill prompt** (`.claude/commands/daily-digest.md`):

1. **Topic interpretation** → Prompt section
2. **Discovery orchestration** → Skill invokes web_search + fetch tools
3. **Quality signal detection** → Prompt section (classifies sources)
4. **Deduplication** → Prompt section (groups + scores insights)
5. **Insight extraction** → Reuse MVP prompt (same quality rubric)

**No external code files, no infrastructure, no external models.** Everything is in the prompt and native Claude Code tools.

### Latency & Reliability Profile

- **Target latency**: <45 seconds
- **Breakdown**: Discovery (2-3s) + Fetch (10-20s) + Deduplication (10-15s) + Insight generation (5-10s) = **27-48s total** ✅
- **Reliability**: Graceful degradation at each stage (failed fetch → skip and continue; low engagement → use credibility alone; timeout → use partial results)
- **Fallback**: If <1 credible source found, user can provide text snippets manually (`/daily-digest claude-code "[snippet1]"...`), which triggers MVP manual mode.

---

## Decision Rationale Recap

| Area | Decision | Why | Constraint Met |
|------|----------|-----|-----------------|
| **Discovery** | Web search + fetch + MCP fallback | No external code, native tools, graceful degradation | ✅ Single skill, no deps |
| **Content Access** | Sequential fetching with 45s timeout | Simple orchestration, sufficient latency budget, bounded scope | ✅ No infrastructure |
| **Deduplication** | Prompt-based semantic matching + heuristic scoring | No embeddings/ML, transparent, scalable to MVP data volume | ✅ No external APIs |
| **Quality Signals** | Source classification + engagement heuristics + quality rubric | Observable signals, prompt-based reasoning, reuses MVP logic | ✅ No external models |

---

## Post-Research Implications

### What This Enables

1. **Phase 2 can be implemented as a single skill** — all discovery logic fits in `.claude/commands/daily-digest.md` alongside MVP code.
2. **Latency is acceptable** — 27-48 seconds comfortably within 45-second budget with margin.
3. **MVP quality can be maintained** — deduplication + quality rubric prevent signal dilution even with 8-10 sources.
4. **Graceful degradation** — system handles partial failures, timeouts, low-signal content without crashing.

### What This Doesn't Solve (Future Phases)

1. **Autonomous source discovery** — Currently requires user to invoke `/daily-digest <topic>`. Phase 3 could add autonomous scheduling ("daily at 9am for this topic").
2. **Personalization** — No user feedback loop yet. Phase 3 adds `/rate-digest` to capture user preferences.
3. **Source monitoring** — Phase 2 discovers sources per run; doesn't maintain a persistent "followed accounts" list. Phase 3 could add persistent source management.
4. **Parallelization** — Discovery is sequential; Phase 3 could introduce subagents for parallel web/Twitter/YouTube discovery if latency becomes problematic.

---

## Remaining Unknowns & Assumptions

### Known Unknowns

1. **MCP server availability**: Research assumes Twitter/YouTube MCPs are available or optional. If unavailable, system falls back to web search only. Post-research action: Test MCP availability before Phase 2 implementation.
2. **Web search quality for niche topics**: Research assumes "Claude Code" and similar tech topics are well-served by web search. Niche topics may have limited results. Post-research action: Benchmark web search quality across 3-5 representative topics.
3. **Engagement data availability**: Some sources may not expose engagement metrics. Heuristic scoring handles this, but real-world prevalence unknown. Post-research action: Audit top 20 sources for engagement data availability.

### Assumptions That Could Invalidate Findings

1. **Web search + fetch tools are always available** in Claude Code. (Assumption: Yes, they are core tools.)
2. **Prompt-based deduplication scales** to 20-40 candidate insights. (Assumption: Claude can group ~40 items with high accuracy. Real test: Benchmark with actual discovery output.)
3. **45-second latency is achievable**. (Assumption: Fetch operations complete in 2s each, search in 3s, analysis in 15s. Real test: Profile actual execution.)
4. **Users accept heuristic-based credibility classification** (no ML models). (Assumption: Observable signals + transparent rubric are sufficient. Real test: User feedback on source attribution in Phase 2 digests.)

---

## Next Steps (Implementation Phase)

1. **Implement Phase 2 skill** using recommendations from this research.
2. **Benchmark discovery latency** with 5+ representative topics.
3. **Test deduplication accuracy** against hand-labeled duplicate sets.
4. **Validate credibility classification** against user feedback (Phase 2 user testing).
5. **Measure quality rubric adherence** — confirm digests meet MVP bar (≥2 on 3/4 dimensions).
6. **Document edge cases** encountered during implementation (e.g., paywall content, encoding issues).

---

## Appendix: Example Discovery + Deduplication Flow

### Scenario: `/daily-digest claude-code`

**Discovery Phase (2-3s):**
```
Search 1: "Claude Code subagents pattern"
  → 10 results, fetch URLs [A, B, C]

Search 2: "MCP integration Claude Code"
  → 10 results, fetch URLs [D, E, F]

Search 3: "Claude Code advanced techniques"
  → 10 results, fetch URLs [G, H, I]

Fetched Content:
  A: Anthropic blog post on subagents (credibility: HIGH, 1200 views)
  B: Medium post on subagents (credibility: MEDIUM, 200 views)
  C: Twitter thread on subagents (credibility: MEDIUM, 50 engagement)
  D: Tech blog on MCP (credibility: MEDIUM, 400 views)
  E: HN discussion on MCP (credibility: MEDIUM, 300 votes)
  F: Startup blog on MCP (credibility: LOW, promotional)
  G: Dev doc on skills (credibility: HIGH, official)
  H: Blog on skills (credibility: MEDIUM, 150 views)
  I: Getting started guide (credibility: LOW, beginner content)
```

**Candidate Insights Extraction (5-10s):**
```
From A: "Use subagents for parallel task decomposition" (evidence: code example)
From B: "Subagents enable concurrent execution" (evidence: explanation)
From C: "Subagents let you split work into parallel jobs" (evidence: brief mention)
From D: "MCP is a protocol for tool integration" (evidence: definition)
From E: "MCP abstracts away auth complexity" (evidence: discussion)
From F: "[Skip, promotional content]"
From G: "Skills provide reusable, composable processing" (evidence: code)
From H: "Skills are building blocks for agents" (evidence: explanation)
From I: "[Skip, beginner-level]"

Total candidates: 7 insights
```

**Deduplication Phase (10-15s):**
```
Candidate Insights:
  1. "Use subagents for parallel task decomposition" (from A)
  2. "Subagents enable concurrent execution" (from B)
  3. "Subagents let you split work into parallel jobs" (from C)
  4. "MCP is a protocol for tool integration" (from D)
  5. "MCP abstracts away auth complexity" (from E)
  6. "Skills provide reusable, composable processing" (from G)
  7. "Skills are building blocks for agents" (from H)

Grouping:
  Group A (Subagent parallel execution): [1, 2, 3] → MERGE
  Group B (MCP integration): [4, 5] → SEPARATE (different aspects)
  Group C (Skills composition): [6, 7] → MERGE

Merged Insights:
  M1: "Use subagents for parallel task decomposition"
      Best version: 1 (from A)
      Credibility: HIGH (A), MEDIUM (B, C)
      Score: Credibility 3 + Specificity 3 + Engagement 1 = 7 → KEEP
      Supporting sources: [A (high), B (medium), C (medium)]

  M2: "MCP abstracts away authentication complexity"
      Best version: 5 (from E, more concrete than D)
      Credibility: MEDIUM (E), MEDIUM (D)
      Score: Credibility 2 + Specificity 2 + Engagement 1 = 5 → KEEP
      Supporting sources: [E (medium), D (medium)]

  M3: "Skills provide reusable, composable processing blocks"
      Best version: 6 (from G, official source)
      Credibility: HIGH (G), MEDIUM (H)
      Score: Credibility 3 + Specificity 2 + Engagement 0 = 5 → KEEP
      Supporting sources: [G (high), H (medium)]

Deduped Results: 3 insights
```

**Quality Rubric Application (5-10s):**
```
Apply MVP rubric to M1, M2, M3:

M1 "Use subagents for parallel task decomposition":
  Novelty: 2 (new + non-obvious pattern)
  Evidence: 2 (direct code example from A)
  Specificity: 2 (concrete technique + architecture)
  Actionability: 2 (clear how to apply in Claude Code)
  Score: 4/4 dimensions → INCLUDE

M2 "MCP abstracts away authentication complexity":
  Novelty: 1 (somewhat known pattern)
  Evidence: 1 (discussed but not deeply)
  Specificity: 2 (MCP specifically defined)
  Actionability: 2 (clear implication: use MCP)
  Score: 3/4 dimensions → INCLUDE

M3 "Skills provide reusable, composable processing blocks":
  Novelty: 0 (well-known from documentation)
  Evidence: 2 (official docs + explanation)
  Specificity: 2 (concrete structure)
  Actionability: 1 (general principle, not specific action)
  Score: 3/4 dimensions → INCLUDE (borderline; official source helps)

Final Insights for Digest: [M1, M2, M3] = 3 insights ✅
```

**Output (Markdown generation, 2-3s):**
```markdown
# Daily Digest — Claude Code

Generated: 2026-03-21 14:35

## Key Insights (1-3)

### Use subagents for parallel task decomposition
Subagents enable you to divide work into independent, parallel execution paths.
Instead of sequential processing, decompose your workflow into subagents that
execute concurrently, improving performance and modularity.

Evidence: "[code example from Anthropic blog]"

*Supported by: Anthropic blog (official), Medium post, Twitter discussion*

### MCP abstracts away authentication complexity
MCP (Model Context Protocol) provides a unified interface for tool integration,
eliminating the need to manage authentication, API keys, and SDKs for each
service individually.

Evidence: "MCP handles the infrastructure. For web access, just call WebFetch MCP and get HTML parsed into markdown."

*Supported by: HN discussion, Tech blog*

### Skills provide reusable, composable processing blocks
Skills are the fundamental building blocks in Claude Code. They are reusable,
independently testable units of functionality that compose into larger systems.

Evidence: "[official docs excerpt]"

*Supported by: Official Claude Code documentation, Technical blog*

## Anti-patterns (2-4)

[... anti-patterns extracted from sources, not shown here ...]

## Actions to Try (1-3)

[... actions generated from insights, not shown here ...]

## Resources (3-5)

[... resources from sources, not shown here ...]
```

---

**Research Complete. Ready for Implementation Phase.**
