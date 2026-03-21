# Phase 2 Implementation Guide

**Document Purpose**: Concrete, actionable guidance for implementing Phase 2 Autonomous Discovery
**Audience**: Engineer implementing the `/daily-digest` Phase 2 skill
**Prerequisite**: Read `research.md` for detailed rationale; use this guide for implementation details

---

## Overview

Extend `.claude/commands/daily-digest.md` to support autonomous discovery:

```
MVP (Phase 1):
  /daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"
           ↓ (user provides content)
        Insight extraction

Phase 2:
  /daily-digest claude-code
           ↓ (no snippets provided)
        Autonomous discovery (web search + fetch)
           ↓
        Insight extraction
```

**Key constraint**: Single skill file. No new code files, no external infrastructure.

---

## Architectural Changes to `.claude/commands/daily-digest.md`

### Current Flow (MVP)
```
1. Parse input (topic + 3-5 text snippets)
2. Validate snippets (100-500 words each)
3. Extract insights (MVP quality rubric)
4. Generate anti-patterns, actions, resources
5. Write markdown output
```

### New Flow (Phase 2)
```
1. Parse input (topic ± text snippets)
2. IF snippets provided:
     → Path A: MVP manual mode (existing logic)
   ELSE:
     → Path B: Autonomous discovery
        a. Interpret topic → keywords + subtopics
        b. Perform web search (3 queries)
        c. Fetch top 5-10 URLs, aggregate content
        d. Attempt MCP sources (Twitter, YouTube) if available
        e. Handle timeout at 45s; use partial results if needed
        f. Classify sources (credible vs. non-credible)
        g. Deduplicate candidate insights
        h. Filter low-credible sources from insights
        i. Path A: Extract insights (reuse MVP quality rubric)
3. Generate output (same format as MVP)
```

### Backward Compatibility
```
/daily-digest claude-code "[snippet1]" "[snippet2]" "[snippet3]"
         ↓
      MVP manual mode (Path A)

/daily-digest claude-code
         ↓
      Phase 2 autonomous mode (Path B)
```

Both paths produce identical output format.

---

## Implementation Sections

### Section 1: Input Parsing & Mode Detection

```
Current code:
  Extract args: topic, [snippet1, snippet2, ...]
  Validate: 3-5 snippets required, 100-500 words each

New code:
  Extract args: topic, [snippets (optional)]
  IF len(snippets) >= 3:
    → manual_mode = True (proceed with MVP logic)
  ELSE:
    → manual_mode = False (proceed with discovery)
    → Set up discovery phase
```

**Prompt guidance:**
```
Parse the command input:
- First argument is always the topic (e.g., "claude-code")
- Remaining arguments are optional text snippets in quotes

IF 3+ valid snippets provided:
  Use MVP manual mode (reuse existing insight extraction)

IF 0-2 snippets provided:
  Use Phase 2 autonomous discovery:
    1. Interpret topic to extract keywords/subtopics
    2. Perform web discovery
    3. Fetch and aggregate content
    4. Deduplicate and score insights
    5. Extract insights using MVP quality rubric
    6. Generate output
```

---

### Section 2: Topic Interpretation (Phase 2 Only)

**Purpose**: Convert user-provided topic into search queries and relevance filters

**For topic "claude-code", generate:**
```
Core Keywords:
  - Claude Code
  - Claude Code (exact)

Subtopics & Related Concepts:
  - Subagents (parallel execution, modularity)
  - Skills (reusable processing blocks)
  - MCP (Model Context Protocol, integrations)
  - Hooks (lifecycle automation)
  - Slash commands
  - Claude Code patterns & workflows
  - Comparisons: Cursor, Copilot, Windsurf
  - Claude Code advanced techniques

Search Query Templates:
  - "[topic] [subtopic]"
  - "[topic] patterns"
  - "[topic] advanced techniques"
  - "[subtopic] [topic]"

Exclude (topic drift protection):
  - Generic LLM discussions
  - AI news unrelated to [topic]
  - Competitor tools (unless directly compared to [topic])
```

**Prompt section:**
```
Topic Interpretation:

Input topic: [user-provided topic, e.g., "claude-code"]

Step 1: Extract Core Keywords
  - Exact matches (e.g., "Claude Code")
  - Acronyms and aliases (e.g., "CC")

Step 2: Identify Subtopics & Domains
  - What concepts frequently appear alongside [topic]?
  - What ecosystems are part of [topic]'s world?
  - Example for "Claude Code": subagents, skills, MCP, hooks, etc.

Step 3: Generate Search Queries
  - 3-5 specific queries combining topic + subtopics
  - Aim for: "[topic] [subtopic] [operator word]"
    Operators: "pattern", "advanced", "best practices", "tutorial", "example"

Step 4: Define Relevance Criteria
  - High relevance: Content explicitly about [topic] or its subtopics
  - Medium relevance: Applicable to [topic] practitioners but not directly about [topic]
  - Low relevance: Adjacent or tangential

Step 5: Identify Out-of-Scope Topics
  - Topics to exclude or deprioritize
  - Example for "Claude Code": Generic LLM discussions, unrelated AI news
```

---

### Section 3: Web Discovery (Phase 2 Only)

**Purpose**: Search for relevant content across the web

**Workflow:**

```
Input: topic, keywords, search_queries (from Section 2)
Output: URLs to fetch

Step 1: Perform Web Searches
  - Execute 3 searches in sequence
  - Each search: 10-20 results
  - Example searches for "claude-code":
    * "Claude Code subagents pattern"
    * "MCP integration Claude Code advanced"
    * "Claude Code best practices 2026"

Step 2: Filter & Rank Results
  - Remove duplicates (same URL appearing in multiple searches)
  - Prioritize:
    * Official domains (anthropic.com, official projects)
    * Recently published (<30 days old)
    * High engagement signals (if available)
  - Keep top 10-20 results total

Step 3: Select URLs to Fetch
  - Pick 5-10 URLs from filtered results
  - Diverse sources: official docs, tech blogs, community posts
  - Avoid fetching all from same domain

Inputs: Keywords + search queries
Outputs: List of URLs to fetch
```

**Prompt section:**
```
Web Discovery via Search:

You have: topic, keywords, search_queries

Step 1: Execute Web Search
  Use the web_search tool to search for:
  - Search Query 1: "[query from topic interpretation]"
    Expect: 10-20 results
  - Search Query 2: "[query]"
  - Search Query 3: "[query]"

Step 2: Collect & Dedup Results
  - Aggregate all results from 3 searches
  - Remove duplicate URLs
  - Estimate total unique URLs found

Step 3: Rank & Filter
  For each URL, assess:
    - Domain: official, established blog, community site, new site
    - Recency: How recent is this content? <7 days = high, 7-30 = medium, >30 = low
    - Relevance: Does URL title/description match topic?

  Keep: Top 5-10 URLs with best combination of recency + relevance + domain authority

Step 4: Output
  List of URLs ready for fetching
```

---

### Section 4: Content Fetching & Aggregation (Phase 2 Only)

**Purpose**: Fetch and parse content from URLs; aggregate into unified corpus

**Workflow:**

```
Input: URLs to fetch (from Section 3)
Output: Aggregated content corpus with metadata

Step 1: Fetch & Parse Each URL
  - Use fetch tool for each URL
  - Fetch tool returns: HTML → markdown (automatic)
  - Extract metadata: title, domain, publication date (if available)
  - Assess engagement (views, comments, shares) if available from page

Step 2: Aggregate Content
  - Combine all fetched content into structured format:
    {
      "source_id": "source_1",
      "url": "https://...",
      "domain": "example.com",
      "title": "[extracted]",
      "content": "[markdown]",
      "metadata": {
        "publication_date": "[extracted or null]",
        "engagement": { "views": X, "comments": Y, ...}
      }
    }

Step 3: Handle Failures Gracefully
  - If fetch fails (timeout, 404, unparseable): skip that URL, continue with others
  - If all fetches fail: abort discovery, return fallback message

Step 4: Summarize Content
  - For each source, extract key paragraphs/sections (don't store full text)
  - Target: 500-1000 words per source
  - Remove boilerplate (headers, footers, navigation)
```

**Prompt section:**
```
Content Fetching & Aggregation:

You have: List of 5-10 URLs to fetch

Step 1: Fetch Each URL
  For each URL in list:
    - Use the fetch tool to retrieve content
    - Result: HTML converted to markdown
    - Extract: title, domain, publication date (if visible)

  If fetch fails (timeout, 404):
    - Log failure for later reporting
    - Continue with next URL

Step 2: Aggregate into Corpus
  For each successfully fetched URL, create entry:
    {
      "source_id": "source_1",  # sequential ID
      "url": "https://...",
      "domain": "example.com",
      "title": "[extracted from page]",
      "content_summary": "[extract key sections, ~500-1000 words]",
      "metadata": {
        "publication_date": "[if available]",
        "source_type": "blog | official | community | video"
      }
    }

Step 3: Report Aggregation Status
  - Total URLs fetched: X out of Y
  - Failed fetches: [list if any]
  - Total content volume: Xk words

Proceed to next phase.
```

---

### Section 5: MCP Sources (Phase 2 Optional)

**Purpose**: Supplement web discovery with Twitter/YouTube if MCPs available

**Workflow:**

```
Input: Topic keywords
Output: Content from Twitter/YouTube (if MCPs available)

Step 1: Attempt Twitter Discovery (Optional)
  - IF Twitter MCP available:
    * Search for recent tweets matching topic keywords
    * Fetch top tweets (engagement-sorted)
    * Extract: tweet text, author, engagement counts
  - IF Twitter MCP unavailable:
    * Log: "Twitter MCP unavailable; using web content only"
    * Continue with aggregated content

Step 2: Attempt YouTube Discovery (Optional)
  - IF YouTube MCP available:
    * Search for recent videos on topic
    * Fetch top video descriptions, transcripts if available
    * Extract: title, channel, view count, transcript (first 500 words)
  - IF YouTube MCP unavailable:
    * Log: "YouTube MCP unavailable; using web content only"
    * Continue

Step 3: Aggregate New Sources
  - Combine Twitter/YouTube results with web sources in unified corpus
  - Mark source type: "twitter", "youtube", "blog", "official"

Note: This is optional. If MCPs unavailable, system continues with web content.
      No failures; graceful degradation.
```

**Prompt section:**
```
Supplemental Discovery (Twitter/YouTube):

After web discovery completes, attempt:

Step 1: Twitter Discovery (optional)
  IF Twitter MCP is available:
    - Search Twitter for topics matching keywords
    - Retrieve top 5-10 tweets by engagement
    - Extract: tweet text, author, likes, replies
  IF not available:
    - Log: "Twitter MCP unavailable; skipping"
    - Continue with web content only

Step 2: YouTube Discovery (optional)
  IF YouTube MCP is available:
    - Search YouTube for topic
    - Retrieve top 3-5 videos
    - Extract: title, channel, views, transcript (first 500 words if available)
  IF not available:
    - Log: "YouTube MCP unavailable; skipping"
    - Continue

Step 3: Combine with Web Corpus
  - Add Twitter/YouTube sources to existing source list
  - Mark each source with type: "twitter" | "youtube" | "blog" | "official"

Result: Final aggregated corpus, ready for deduplication.
```

---

### Section 6: Timeout Management (Phase 2)

**Purpose**: Ensure discovery completes within 45 seconds

**Workflow:**

```
Global Timeout: 45 seconds from start of Phase 2 discovery

Checkpoint Timing:
  - Section 2 (topic interpretation): 0-5 seconds
  - Section 3 (web search): 5-8 seconds
  - Section 4 (fetching): 8-28 seconds (timeout at 40 seconds)
  - Section 5 (MCP): 28-35 seconds (timeout at 40 seconds)
  - Section 6+ (dedup, scoring, extraction): 35-45 seconds

Timeout Logic:
  - If any section exceeds time budget: stop that section, use partial results
  - If web search takes >5 seconds: abort search, use top 20 results so far
  - If fetching takes >20 seconds: stop fetching, use fetched URLs so far
  - If aggregation at 40 seconds: skip MCP, proceed to deduplication
  - At 45 seconds: stop everything, use best-available content

Result Handling:
  - If ≥3 credible sources fetched: generate digest from available content
  - If 1-2 credible sources: generate digest + include quality warning
  - If 0 credible sources by timeout: fallback message (no digest)
```

**Prompt section:**
```
Timeout Management:

Track elapsed time throughout discovery phases.

Timeouts:
  - Web search: Stop at 5 seconds, use results so far
  - Content fetching: Stop at 20 seconds (28s total), use fetched URLs so far
  - MCP attempts: Stop at 7 seconds (35s total), skip if not done
  - Overall: Hard stop at 45 seconds

At any timeout:
  - Use results obtained so far
  - If <1 credible source: fallback message
  - If 1-2 credible sources: include quality warning in digest
  - If ≥3 credible sources: generate full digest

Report timeout status in digest metadata (hidden, for logging).
```

---

### Section 7: Source Classification & Credibility Scoring (Phase 2)

**Purpose**: Assess which sources are credible for insights

**Workflow:**

```
Input: Aggregated source corpus (Section 4 + 5)
Output: Each source classified as: HIGH | MEDIUM | LOW credibility

Classification Logic:

For each source, assess:

1. Domain/Authority
   - Official domain (anthropic.com, github.com/official): +3
   - Known tech publication (stripe.com, vercel.com): +2
   - Established blog (many followers, >1 year old): +1
   - New/unknown domain: +0

2. Author (if identifiable)
   - Official/verified account: +3
   - Well-known practitioner (1000+ followers, track record): +2
   - Community contributor: +1
   - Unverified/anonymous: +0

3. Content Type
   - Official documentation: +2
   - Concrete example/code/demo: +1
   - Abstract discussion: +0
   - Beginner tutorial: -1 (deprioritize)
   - Promotional/marketing: -2 (disqualify)

4. Engagement (if available)
   - >1000 views/impressions: +1
   - >100 comments/interactions: +1
   - Recent (<7 days): +0.5
   - Older (>30 days): -0.5

Final Score Calculation:
  credibility_score = (domain + author + content + engagement) / 4
  Normalize to HIGH (3), MEDIUM (2), LOW (1):
    - ≥2.5 → HIGH
    - 1.5-2.5 → MEDIUM
    - <1.5 → LOW

Decision:
  - HIGH, MEDIUM: May be used for Insights section
  - LOW: Excluded from Insights; may appear in Resources section only (ranked lower)
```

**Prompt section:**
```
Source Credibility Classification:

For each source in aggregated corpus, determine credibility:

Assessment Rubric:

  1. Domain Authority (0-3 scale)
     - 3: Official domain (anthropic.com) or verified official
     - 2: Known tech publication with editorial standards
     - 1: Established independent blog
     - 0: New domain or low-reputation site

  2. Author Credibility (0-3 scale)
     - 3: Official or verified identity (CEO, research lead, etc.)
     - 2: Well-known practitioner in ecosystem
     - 1: Active community contributor
     - 0: Unverified or unknown

  3. Content Quality (0-3 scale, can be negative)
     - 3: Concrete example + code/demo + steps
     - 2: Clear explanation + example
     - 1: General discussion
     - 0: Beginner tutorial
     - -1: Promotional/marketing (disqualify)

  4. Engagement & Recency (0-2 scale)
     - 2: >1000 views AND >100 interactions AND <7 days old
     - 1: Moderate engagement OR recent
     - 0: Low engagement or old

Final Classification:
  avg_score = (domain + author + content + engagement) / 4

  if avg_score ≥ 2.5:
    credibility = "HIGH"
  elif avg_score ≥ 1.5:
    credibility = "MEDIUM"
  else:
    credibility = "LOW"

Output: source_id → credibility mapping
```

---

### Section 8: Engagement Signal Detection (Phase 2)

**Purpose**: Extract engagement signals where available for scoring

**Workflow:**

```
For sources with available engagement data (tweets, YouTube videos, blog comments):

Engagement Scoring (0-2 scale):

1. Views/Impressions
   - >1000: score = 2
   - 100-1000: score = 1
   - <100: score = 0

2. Interactions (comments, shares, likes, replies)
   - >100: score = 2
   - 10-100: score = 1
   - <10: score = 0

3. Recency
   - <7 days old: score = 2
   - 7-30 days old: score = 1
   - >30 days old: score = 0

Final Engagement Score: (views + interactions + recency) / 3
  Range: 0-2
  Use for: Tie-breaker in deduplication (Section 9)

Note: Engagement data often unavailable (e.g., blog articles don't expose view counts).
      If unavailable, treat engagement score as 0 (credibility + specificity alone used).
```

**Prompt section:**
```
Engagement Signal Extraction:

For sources where engagement data is publicly available (tweets, YouTube, blog comments):

Extract and Score:

  Views/Impressions: [number if available, else "unknown"]
    - >1000 views: high engagement
    - 100-1000 views: moderate
    - <100 views: low

  Interactions (likes, replies, comments, shares): [number if available]
    - >100: high engagement
    - 10-100: moderate
    - <10: low

  Recency (publication date): [date]
    - <7 days old: high recency
    - 7-30 days: moderate
    - >30 days: low recency

Use engagement signals as:
  - Secondary signal for credibility (boost credibility if high engagement + credible source)
  - Tie-breaker in deduplication (when two insights similar, prefer higher engagement)
  - Priority ranking (display higher-engagement insights first)

Note: Many sources (blogs, docs) don't expose engagement. Use credibility + specificity alone for those.
```

---

### Section 9: Deduplication & Insight Grouping (Phase 2)

**Purpose**: Identify semantically identical insights; retain best-evidence version

**Workflow:**

```
Input: Aggregated sources + classification from Sections 7-8
Output: Deduplicated list of unique insights with best-evidence version + supporting sources

Step 1: Extract Candidate Insights
  - For each source, extract 2-4 candidate insights
  - Total candidates: 8-10 sources × 2-4 = 16-40 candidates

Step 2: Semantic Grouping
  - Read all candidates
  - Ask: "Which insights are describing the same underlying practice?"
  - Group similar insights together
  - Expected groupings: 3-7 groups from 16-40 candidates

Step 3: Score Each Insight Version
  - For each group, score each insight version:
    score = credibility (0-3) + specificity (0-3) + engagement (0-2)
  - Range: 0-8
  - Select highest-scoring version for each group

Step 4: Attribution & Source Tracking
  - For each retained insight, track:
    * Best-evidence source (highest score)
    * Supporting sources (other sources in same group)
    * Credibility of each supporting source
  - Example:
    Insight: "Use subagents for parallel execution"
    Best source: Anthropic blog (score 8)
    Supporting: [Tech blog (score 6), Twitter thread (score 4)]

Step 5: Output
  - 3-7 unique, deduplicated insights
  - Each with best-evidence source + supporting sources
  - Ready for quality rubric evaluation
```

**Prompt section:**
```
Deduplication & Insight Grouping:

Step 1: Extract Candidate Insights
  Review all fetched sources and extract 2-4 candidate insights from each.
  Target: 2-4 insights per source × 8-10 sources = 16-40 candidates total

Step 2: Group Similar Insights
  Read all candidates.
  For each pair of insights, ask:
    "Are these describing the same underlying practice, even if phrased differently?"

  Examples of duplicates:
    - "Use subagents for parallel execution" vs. "Subagents enable concurrent processing"
    - "MCP abstracts auth" vs. "MCP handles authentication"

  Build groups. Expected: 3-7 groups from 16-40 candidates.

Step 3: Score Insight Versions
  For each group, score each version:

    score = credibility (0-3) + specificity (0-3) + engagement (0-2)

    credibility: Source classification from Section 7 (HIGH=3, MEDIUM=2, LOW=1)
    specificity: How concrete is this version?
      3 = concrete example + code/steps
      2 = clear explanation + example
      1 = general statement
      0 = vague
    engagement: From Section 8 (0-2)

  Select highest-scoring version per group.

Step 4: Track Supporting Sources
  For each retained insight:
    best_source: [source_id with highest score]
    supporting_sources: [other sources in group, ranked by score]

  Example:
    Insight: "Use subagents for parallel execution"
    best_source: source_5 (Anthropic blog, score 8)
    supporting: [source_1 (Tech blog, score 6), source_3 (Twitter, score 3)]

Step 5: Output Deduplicated Insights
  - List of unique insights with source attribution
  - Ready for MVP quality rubric evaluation
```

---

### Section 10: Topic Relevance Filtering (Phase 2)

**Purpose**: Ensure discovered content is truly about the topic

**Workflow:**

```
Input: Deduplicated insights (from Section 9)
Output: Filtered insights marked as relevant/irrelevant

Relevance Scoring (0-7 scale):

For each insight, assess:

1. Explicit Mention (0-3)
   - Does content explicitly mention the topic or its subtopics?
   - 3: Yes, extensively
   - 1: Yes, but briefly
   - 0: No

2. Applicability (0-2)
   - Is insight actionable for practitioners in this topic?
   - 2: Yes, directly applicable
   - 1: Tangentially applicable
   - 0: Not applicable

3. Focus (0-2)
   - Is topic the focus of content, or mentioned in passing?
   - 2: Main focus, dedicated section
   - 1: Mentioned, but not main focus
   - 0: Mentioned only in passing

Final Relevance Score: Sum of above (0-7)

Decision:
  - ≥6: Keep (on-topic)
  - 3-5: Marginal; apply quality rubric strictly (require score ≥6/8)
  - <3: Exclude (off-topic)
```

**Prompt section:**
```
Topic Relevance Filtering:

For each deduplicated insight from Section 9, assess relevance to the topic.

Relevance Rubric:

  1. Explicit Mention of Topic (0-3)
     - 3: Content explicitly discusses topic extensively
     - 1: Topic mentioned but not central
     - 0: Topic not mentioned

  2. Applicability to Topic Practitioners (0-2)
     - 2: Insight directly applicable to [topic] work
     - 1: Tangentially applicable
     - 0: Not applicable to [topic]

  3. Content Focus (0-2)
     - 2: [Topic] is main focus of content
     - 1: [Topic] mentioned but not main focus
     - 0: [Topic] mentioned only in passing

Score Calculation:
  relevance_score = mention + applicability + focus
  Range: 0-7

Decision:
  if relevance_score ≥ 6:
    → Keep insight (on-topic)
  elif relevance_score 3-5:
    → Marginal; apply quality rubric strictly (require ≥6/8 on rubric)
  else (relevance_score < 3):
    → Exclude insight (off-topic)

Output: Filtered insights with relevance scores
```

---

### Section 11: Apply MVP Quality Rubric (Phase 2 + MVP)

**Purpose**: Filter insights against 4-dimensional quality rubric (same as MVP)

**Workflow:**

```
Input: Filtered insights from Section 10
Output: Insights passing MVP quality rubric

Quality Rubric (4 dimensions, each 0-2):

1. Novelty
   - 0: Known/obvious information
   - 1: Somewhat new
   - 2: New + non-obvious

2. Evidence
   - 0: No evidence
   - 1: Mentioned in content
   - 2: Direct quote or code example

3. Specificity
   - 0: Generic, vague
   - 1: Somewhat specific
   - 2: Concrete + actionable

4. Actionability
   - 0: Observation only
   - 1: Implies a next step
   - 2: Clear next step

Inclusion Rule:
  - Score ≥2 on ≥3 dimensions → INCLUDE
  - Score <2 on ≥2 dimensions → EXCLUDE (low signal)

Special Case - Topic Relevance:
  - If relevance_score ≥6 (on-topic): Standard inclusion rule applies
  - If relevance_score 3-5 (marginal): Require ≥2 on all 4 dimensions (stricter)
  - If relevance_score <3: Already excluded

Output:
  - 1-3 insights passing rubric
  - No padding; output best available even if <3 total
```

**Prompt section:**
```
Apply MVP Quality Rubric:

For each filtered insight (from Section 10), score on 4 dimensions:

Rubric:

  Novelty (0-2):
    2: New + non-obvious pattern
    1: Somewhat new
    0: Known/obvious

  Evidence (0-2):
    2: Direct quote or code example
    1: Mentioned in content
    0: No evidence

  Specificity (0-2):
    2: Concrete + actionable
    1: Somewhat specific
    0: Generic/vague

  Actionability (0-2):
    2: Clear next step
    1: Implies action
    0: Observation only

Inclusion Rule:
  if relevance_score ≥ 6:
    → Include if score ≥2 on ≥3 dimensions
  elif relevance_score 3-5:
    → Include only if score ≥2 on all 4 dimensions (stricter)
  else:
    → Already excluded (relevance <3)

Output: 1-3 insights passing rubric
  No padding: output best available even if <3 total
```

---

### Section 12: Anti-patterns & Actions (Phase 2)

**Purpose**: Extract anti-patterns and generate actions (same as MVP)

**Reuse MVP Logic**: Sections in `.claude/commands/daily-digest.md` for:
- Anti-pattern extraction (2-4 items)
- Action generation (1-3 items per insight)
- Resource selection (3-5 items)

**Phase 2 Variation**: Apply to discovered sources instead of user-provided snippets.

**Prompt section:**
```
Extract Anti-patterns & Generate Actions:

Use the same MVP logic, but applied to discovered sources:

Anti-patterns (2-4):
  - From aggregated source corpus, identify 2-4 practices to avoid
  - Each with evidence quote from sources
  - Same rubric as MVP

Actions to Try (1-3):
  - For each insight, generate concrete experiments
  - Same rubric as MVP: effort, time, steps, outcome
  - Ensure actions are executable in 30 minutes to 3 hours

Resources (3-5):
  - Select top supporting sources/references
  - Use direct quotes or literal phrases from discovered content
  - Rank credible sources first, non-credible second

(Reuse MVP prompt sections for these; no Phase 2 changes needed.)
```

---

### Section 13: Quality Signal: Detect Low-Signal Content (Phase 2)

**Purpose**: Warn user if discovery yields low-quality insights

**Workflow:**

```
After insight extraction (Section 11), assess overall signal quality:

Count check:
  - Insights: <1 (should be 1-3)
  - Anti-patterns: <2 (should be 2-4)
  - Actions: <1 (should be 1-3)
  - Resources: <3 (should be 3-5)

If any count below minimum:
  - Generate quality warning: "⚠️ Low-signal content — insights below represent the best available material"
  - Include discovery status message:
    * If discovery timed out: "Discovery incomplete: operation timed out"
    * If some sources failed: "Discovery incomplete: [source] unavailable"
  - Output available content (no fallback to manual mode; digest is still generated)

If all counts met:
  - No warning; discovery successful
```

**Prompt section:**
```
Quality Signal Assessment:

After extracting insights, anti-patterns, actions, and resources, count totals:

Minimum Thresholds:
  - Insights: 1 (target 1-3)
  - Anti-patterns: 2 (target 2-4)
  - Actions: 1 (target 1-3)
  - Resources: 3 (target 3-5)

If any below minimum:
  Prepare warning message:
    "⚠️ Low-signal content — insights below represent the best available material"

  Include discovery status:
    - If timeout reached: "Discovery incomplete: operation timed out"
    - If sources failed: "Discovery incomplete: [source names] unavailable"

  Output best-available content (do not fall back; digest is still generated)

If all thresholds met:
  No warning. Digest is high-signal.
```

---

### Section 14: Fallback to Manual Mode (Phase 2)

**Purpose**: If autonomous discovery fails, guide user to manual mode

**Trigger conditions:**

```
Fallback to manual mode if:
  - No credible sources found (all sources classified as LOW)
  - All discovery sources failed/timed out before fetching any content
  - 0 insights extracted after quality rubric filtering

Fallback Message:
  "No relevant content discovered for topic '[topic]'.
   Try providing text snippets manually:
     /daily-digest [topic] \"[snippet1]\" \"[snippet2]\" \"[snippet3]\"

   Or try a different topic."

User Actions:
  - Provide text snippets to trigger MVP manual mode
  - Or re-run with different topic
```

**Prompt section:**
```
Fallback to Manual Mode:

If discovery results in:
  - 0 credible sources found, OR
  - Discovery timed out before any content fetched, OR
  - 0 insights pass quality rubric

Display fallback message (no digest file created):

  "No relevant content discovered for topic '[topic]'.

   Try providing text snippets manually:
     /daily-digest [topic] \"[snippet1]\" \"[snippet2]\" \"[snippet3]\"

   Or try a different topic."

(Do not generate empty digest file. Return user-visible message only.)
```

---

### Section 15: Markdown Output & File Write (Phase 2)

**Purpose**: Generate digest markdown (same as MVP)

**Reuse MVP Output Format:**

```markdown
# Daily Digest — {Topic}

Generated: {YYYY-MM-DD HH:MM}

## Key Insights (1-3)

### {Title}
{Description}

Evidence: "{Quote}"

*Source: {Source Name} (credibility: HIGH/MEDIUM)*
*Supporting sources: [list other sources if applicable]*

## Anti-patterns (2-4)

- **{Name}**: {Quote from source}.

## Actions to Try (1-3)

### {Title}
- Effort: {low|medium|high}
- Time: {duration}
- Steps: [numbered list]
- Expected outcome: {result}

## Resources (3-5)

- **{Quote from source}**: {Why it matters}
  *Source: {Name} (credibility: HIGH/MEDIUM/LOW)*

---

[If low-signal:]
⚠️ Low-signal content — insights below represent the best available material
[If discovery incomplete:]
Discovery incomplete: {status message}
```

**Phase 2 additions:**
- Attribution to source: "Source: [Name] (credibility: HIGH/MEDIUM)"
- Supporting sources: "[Other sources supporting this insight]"
- Discovery status warnings if applicable

---

## Testing Checklist

Before Phase 2 release, verify:

- [ ] **Input parsing**: `/daily-digest topic` (no snippets) triggers Phase 2 mode
- [ ] **Input parsing**: `/daily-digest topic "[snippet1]"` (snippets) triggers MVP manual mode
- [ ] **Web discovery**: Web search executes, returns results
- [ ] **Content fetching**: 5-10 URLs fetched successfully, markdown conversion works
- [ ] **Source classification**: Each source assigned credibility (HIGH/MEDIUM/LOW)
- [ ] **Deduplication**: Similar insights merged, best-evidence version retained
- [ ] **Quality rubric**: Insights filtered to 1-3, all passing ≥3/4 dimensions
- [ ] **Attribution**: Each insight credited to source with credibility level
- [ ] **Latency**: End-to-end <45 seconds (measure 5 runs, avg <40s)
- [ ] **Low-signal handling**: If <3 insights, quality warning appears
- [ ] **Fallback**: If 0 credible sources, fallback message appears (no digest file)
- [ ] **Backward compatibility**: MVP manual mode still works
- [ ] **Output format**: Markdown matches MVP format
- [ ] **File creation**: Digest file created at `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic}.md`

---

## Implementation Order (Recommended)

1. **Phase 2.1**: Input parsing + mode detection (Section 1)
2. **Phase 2.2**: Topic interpretation (Section 2)
3. **Phase 2.3**: Web discovery (Section 3)
4. **Phase 2.4**: Content fetching (Section 4)
5. **Phase 2.5**: MCP sources (Section 5, optional but nice-to-have)
6. **Phase 2.6**: Timeout management (Section 6, integrate throughout)
7. **Phase 2.7**: Source classification (Section 7)
8. **Phase 2.8**: Engagement signals (Section 8)
9. **Phase 2.9**: Deduplication (Section 9)
10. **Phase 2.10**: Topic relevance (Section 10)
11. **Phase 2.11**: Apply quality rubric (Section 11)
12. **Phase 2.12**: Anti-patterns & actions (Section 12, reuse MVP)
13. **Phase 2.13**: Quality signal detection (Section 13)
14. **Phase 2.14**: Fallback handling (Section 14)
15. **Phase 2.15**: Output & file write (Section 15, reuse MVP)
16. **Testing**: Run checklist (Testing Checklist, above)

---

## Known Limitations & Future Work

### Phase 2 Limitations
- No autonomous scheduling (runs on-demand)
- No user feedback loop (Phase 3 adds `/rate-digest`)
- Sequential fetching (not parallelized)
- Web search may miss emerging content
- Heuristic-based deduplication (not ML-based embeddings)

### Phase 3+ Enhancements
- Autonomous scheduling (daily at specified time)
- User feedback loop (`/rate-digest` command)
- Persistent source tracking (followed accounts across runs)
- Subagent-based parallelization for faster discovery
- ML-based deduplication (embeddings) if heuristics insufficient

---

**Implementation Guide Complete. Ready to code.**
