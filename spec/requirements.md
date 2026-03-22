# Requirements: your-daily-brief — Daily Intelligence Digest

## 1. Overview

**your-daily-brief** generates a **daily digest of high-signal insights** about any topic specified by the user at invocation time.
It transforms raw content (tweets, videos, blogs) into:

* Actionable insights
* Anti-patterns to avoid
* Concrete actions to try

The system is designed for **continuous learning and improvement**, not just summarization.

---

## 2. Goals

### Primary Goals

* Identify **patterns used by advanced users** on the specified topic
* Surface **non-obvious insights (not summaries)**
* Provide **1–3 actionable experiments per day**

### Secondary Goals

* Reduce noise from low-quality content
* Improve relevance over time using feedback

---

## 3. Non-Goals

* Not a generic news aggregator
* Not a link dump
* Not focused on beginner tutorials
* Not real-time (batch daily is sufficient for MVP)

---

## 4. Inputs

### 4.1 Data Sources

* **YouTube** — user-specified seed channels, expanded over time with your-daily-brief suggestions
* **Twitter/X** — accounts identified and monitored autonomously by your-daily-brief based on the topic
* **Blogs & web** — autonomous search across the web, supplemented by user-provided URLs

### 4.2 Input Method

The user invokes `/daily-digest <topic>` from within Claude Code (e.g. `/daily-digest Claude Code`). The default topic is **Claude Code**.

your-daily-brief handles its own research autonomously — the user does not need to supply URLs for each run. The user MAY provide additional URLs manually to supplement what your-daily-brief finds. Both are processed together.

### 4.3 YouTube Source Management

* The user provides an initial seed list of YouTube channels
* After each run, your-daily-brief MAY suggest additional channels it discovered that are relevant to the topic
* Suggested channels are added to the monitored list only after explicit user approval
* The approved channel list persists across runs

### 4.4 Twitter/X Source Management

* your-daily-brief autonomously identifies accounts relevant to the specified topic (engineers, builders, researchers, practitioners)
* your-daily-brief monitors these accounts for high-signal content without requiring user input
* your-daily-brief MAY surface new accounts it discovers and flag them for the user's awareness
* The user does not need to provide or maintain a Twitter/X account list

**Known constraint:** Autonomous account discovery involves ranking, graph traversal, and noise filtering — this is non-trivial. SpecKit should account for this complexity when phasing the implementation.

### 4.5 Input Schema (Normalized)

```json
{
  "source": "twitter | youtube | blog",
  "content": "text or transcript snippet",
  "author": "string",
  "url": "string",
  "engagement": "string or number",
  "timestamp": "ISO-8601 string"
}
```

### 4.6 Definition of High-Signal Content

The system MUST use the following criteria to score and filter content before processing.

**High-signal content — include and prioritise if it meets one or more of these:**

* Posted or shared by a known advanced practitioner, researcher, or official representative in the topic's ecosystem (e.g. for Claude Code: an Anthropic engineer or prolific Claude Code builder)
* Contains a concrete technique, workflow, or code pattern (not pure opinion)
* Covers a non-obvious, undocumented, or emerging aspect of the topic (e.g. for Claude Code: an undocumented capability or edge case)
* Has measurable engagement (likes, views, comments, upvotes)

Engagement is a **primary ranking signal** — among items that pass the quality bar, higher engagement = higher priority in the digest.

**Low-signal content — filter out if it matches any of these:**

* Beginner-level content (install guides, basic prompting, "getting started")
* Duplicate of content already present in the current digest run
* Marketing or promotional content from vendors or tool builders
* Low-effort summaries that restate widely known information without adding new insight

Content that is pure opinion with no concrete technique shown should be deprioritised but not hard-excluded — it may be retained if it comes from a high-credibility author with strong engagement.

---

### 4.7 Topic Interpretation

The system MUST interpret the user-provided topic into:

* Core keywords directly associated with the topic
* Related subtopics and concepts that frequently co-occur with it
* Relevant domains — tools, frameworks, ecosystems that are part of the topic's world

The system SHOULD:

* Expand the topic to include closely related concepts that advanced practitioners would consider part of the same space
* Avoid drifting into loosely related or adjacent domains that dilute signal

Example — Topic: "Claude Code"

Include:
* Subagents, skills, hooks, MCP, slash commands
* Real-world usage patterns and workflows
* Agent-based development approaches
* Direct comparisons with competing tools (Cursor, Copilot, Windsurf)

Exclude:
* Generic LLM discussions not specific to Claude Code
* Unrelated AI tooling unless directly comparable to Claude Code
* Broad AI news with no practical relevance to the topic

The topic interpretation MUST be re-evaluated if the user changes the topic between runs.

---

### 4.8 Content Retrieval Constraints

Content retrieval MUST use the following tools:

* MCP web access for autonomous search and page fetching
* Direct URL ingestion when the user provides URLs manually

Autonomous discovery SHOULD:

* Limit to the top 10–20 results per source per run to avoid signal dilution
* Prioritise recent content (see section 4.9 for time window definition)

The system MUST:

* Prefer depth from fewer high-quality sources over wide shallow scraping
* Avoid excessive retrieval breadth that introduces noise and slows processing

---

### 4.9 Time Window

The system SHOULD prioritise content published within the last 24–48 hours.

The system MAY include older content if:

* It introduces a genuinely novel or non-obvious technique not previously surfaced
* It is highly relevant to the topic and has not appeared in a prior digest run

The system MUST:

* Prefer recency when multiple items have similar signal quality
* Not surface the same older item across multiple digest runs

---

## 5. Core Functional Requirements

### 5.1 Insight Extraction

The system MUST extract insights according to the definition in 5.1.1 and produce output conforming to the schema below.

#### 5.1.1 Definition of an Insight

An insight MUST qualify as one of the following:

* A **pattern** observed across multiple inputs — something multiple advanced users are independently doing or reporting
* A **novel technique** from a single source — a specific, non-obvious approach that a credible author demonstrates with evidence (code, demo, repo, screenshot)

The insight MUST be scoped to the topic specified by the user at invocation time.

An insight MUST NOT be:

* A restatement of a single source with no synthesis
* Obvious or commonly known information
* Generic advice (e.g. "use subagents for modularity", "write clear prompts")

Each insight MUST implicitly answer all three of these questions:

* What are advanced users doing differently?
* Why does it matter?
* How can it be applied?

If an insight cannot answer all three, it does not qualify.

#### Output Schema

```yaml
insights:
  - title: string
    description: string
    evidence: [string]
    relevance: high | medium | low
```

---

### 5.2 Anti-pattern Detection

The system MUST:

* Identify incorrect or inefficient practices
* Explain why they should be avoided

#### Output Schema

```yaml
anti_patterns:
  - description: string
    why_to_avoid: string
```

---

### 5.3 Action Generation

The system MUST:

* Generate **practical, testable actions**
* Align actions with identified insights

#### 5.3.1 Action Quality Bar

Each action MUST:

* Be executable in isolation — no missing context or prerequisites
* Be completable within 30 minutes to 3 hours
* Produce a measurable outcome (a learning, an artifact, or a visible result)

Each action SHOULD (but is not required to):

* Map to at least one insight in the same digest — standalone actions are permitted if they are high-value and concrete

The system MUST NOT generate:

* Vague actions (e.g. "explore subagents", "try using hooks")
* Actions with undefined or multi-day scope
* Actions that duplicate each other across the same digest run

#### Output Schema

```yaml
actions:
  - title: string
    effort: low | medium | high
    time_required: string
    steps: [string]
    expected_outcome: string
```

---

### 5.4 Resource Selection

The system MUST:

* Select the most valuable supporting resources
* Justify why each resource matters

#### Output Schema

```yaml
top_resources:
  - title: string
    type: tweet | video | blog
    url: string
    why_it_matters: string
```

---

### 5.5 Deduplication and Cross-Source Synthesis

The system MUST:

* Detect duplicate content across sources — the same idea reported by multiple sources counts as one insight, not many
* Merge similar items into a single insight with all sources listed as supporting evidence

The system SHOULD:

* Treat multi-source validation as a positive signal — an idea appearing across Twitter, YouTube, and a blog is stronger than one appearing in only one place
* Use multiple sources as corroborating evidence within a single insight rather than generating separate insights per source

The system MUST NOT:

* Produce multiple insights that represent the same underlying idea phrased differently
* Count the same piece of content twice because it was shared across platforms

---

## 6. Output Format (User-Facing)

The system MUST produce a structured digest:

```markdown
# 🧠 your-daily-brief Daily Digest — <topic>

## 🧠 Key Insights
1. ...
2. ...

## ⚠️ Anti-patterns
- ...
- ...

## ⚡ Actions to Try
1. ...
2. ...

## 🔗 Top Resources
- [title](url) — why it matters
```

---

## 7. Constraints

* Maximum 5 insights
* Maximum 3 actions
* No duplicate information across sections
* Avoid generic or obvious statements
* Prioritize **signal over completeness**

---

## 8. Quality Requirements

Each output MUST satisfy:

* Insight is **actionable or thought-provoking**
* Insight reflects **real-world usage patterns**
* Content is **non-trivial and non-obvious**
* Actions are **feasible within 30 min – 3 hours**

### 8.1 Internal Quality Scoring

Before producing output, the system SHOULD internally evaluate each candidate insight against three dimensions:

* **Novelty** — is this new information, or something already widely known?
* **Actionability** — does it lead to a clear next step, or is it observation only?
* **Signal strength** — is it backed by evidence (code, demo, repo, multiple sources)?

Based on this evaluation the system MUST:

* Prefer fewer, higher-quality outputs over a full-but-diluted digest — if only 2 insights meet the bar, output 2, not 5
* Never pad the digest to hit the maximum counts in section 7

If no content meets the quality bar on a given day, the system MUST:

* Output the best available content regardless
* Prepend a visible quality warning to the digest, e.g.: `⚠️ Low-signal day — content below usual quality threshold`

---

### 8.2 Failure Mode Handling

If insufficient high-signal content is available for a given run, the system MUST:

* Output the best available content rather than producing nothing
* Clearly indicate reduced confidence or signal quality inline (e.g. `⚠️ Limited signal — fewer sources than usual`)

The system SHOULD fall back gracefully by:

* Reducing the number of insights rather than padding with weak ones
* Producing more conservative action suggestions tied only to well-evidenced content

The system MUST NOT:

* Invent patterns or insights without evidence from actual sources
* Fill the digest with generic or obvious content to meet output count targets
* Present low-confidence content without flagging it as such

---

## 9. Feedback & Learning

### 9.1 Feedback Input Schema

```yaml
feedback:
  useful: [string]
  not_useful: [string]
```

### 9.2 System Behavior

The system SHOULD:

* Increase weight of useful topics/sources
* Deprioritize irrelevant content
* Adapt future digests accordingly

---

## 10. System Components

The implementation MUST use the following Claude Code primitives:

* **Skills** — for reusable, composable processing steps
* **Subagents** — for parallel content collection and processing
* **Hooks** — for lifecycle automation within the workflow
* **Commands** — `/daily-digest` (MVP), `/rate-digest` (post-MVP)
* **MCP** — for external tool access (web fetching, filesystem, and any other integrations the implementation requires)

---

## 11. Execution Environment

* **Runtime:** Claude Code (IDE)
* **Trigger:** slash command invoked by the user inside the IDE
* **Output destination:** a markdown file written to the project directory, date-stamped

---

## 12. Execution Flow

1. Collect content
2. Normalize inputs
3. Filter low-signal items
4. Extract insights
5. Detect anti-patterns
6. Generate actions
7. Select top resources
8. Assemble digest
9. Capture feedback (optional)

---

## 13. Full System Vision

The following capabilities describe the complete system. SpecKit should determine appropriate phasing.

* Accept a user-specified topic at invocation time; default topic is Claude Code
* Conduct autonomous research across YouTube, Twitter/X, blogs, and the web for the specified topic
* Accept optional user-provided URLs to supplement autonomous research
* Support automated data ingestion via APIs or scraping
* Single command trigger: `/daily-digest <topic>`
* Rating command: `/rate-digest` for feedback capture
* Insight and action generation in a single workflow
* Personalization engine that adapts to user feedback over time
* Historical trend tracking across digest runs
* Integration with Notion for personal knowledge management

---

## 14. Acceptance Criteria

The system is considered successful if:

* Produces at least **1 high-quality insight per run**
* Produces at least **1 actionable suggestion per run**
* Output is **useful to a senior engineer**
* User would **apply at least one action within a week**