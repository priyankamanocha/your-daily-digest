# Feature Specification: Daily Digest Skill

**Feature Branch**: `daily-digest`
**Created**: 2026-03-21
**Status**: Implemented

## Overview

Autonomous daily digest skill. Users provide a topic; the system discovers relevant content from web, video, and social media, deduplicates, applies the quality rubric, and synthesizes insights into a markdown digest. Snippets mode is available for testing without MCP tools.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autonomous Topic Discovery (Priority: P1)

As a knowledge worker, I want to run `/daily-digest <topic>` (topic only, no text snippets) and receive a digest synthesized from autonomous discovery, without manually gathering content.

**Why this priority**: This is the core skill value — users get a quality digest without manually gathering content.

**Independent Test**:
- User invokes `/daily-digest <topic>` with no text snippets
- System discovers relevant content from web, YouTube, Twitter
- System generates digest with 1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources
- Output matches MVP quality standards (quality rubric ≥2 on 3/4 dimensions)

**Acceptance Scenarios**:

1. **Given** user invokes `/daily-digest claude-code`, **When** system completes autonomous discovery, **Then** digest file created at `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-claude-code.md` with same structure as MVP output
2. **Given** system discovers 5+ sources, **When** extracting insights, **Then** system deduplicates semantically identical insights and retains best-evidence version only
3. **Given** low-signal discovery (<3 high-quality sources), **When** generating digest, **Then** output includes quality warning matching MVP low-signal handling
4. **Given** content discovery times out (>45 seconds), **When** partial results received, **Then** system uses best-available discovered content with timeout warning

---

### User Story 2 - Source Quality & Filtering (Priority: P2)

As a user, I want digests to prioritize insights from credible, relevant sources so that my digest reflects quality information, not spam or noise.

**Why this priority**: Ensures discovered content meets MVP quality standards. Without quality filtering, low-signal sources inflate insight counts and degrade digest value.

**Independent Test**:
- Provide digest for topic with mixed source credibility (reputable + questionable sources)
- Verify digest insights prioritize credible sources
- Verify digest maintains 1-3 insights and 2-4 anti-patterns (no padding from weak sources)

**Acceptance Scenarios**:

1. **Given** discovery includes both reputable and low-credibility sources, **When** digest is generated, **Then** insights are drawn from credible sources only
2. **Given** no credible sources available for topic, **When** discovery completes, **Then** digest includes quality warning(matching MVP low-signal handling)
3. **Given** multiple sources support same insight, **When** insight is cited, **Then** attribution names the most credible/authoritative source


### Failure Modes & User Experience

**When Discovery Has Relevant Content** (≥3 credible sources):
- System generates digest from discovered sources
- Digest includes insights, anti-patterns, actions, resources matching MVP counts
- No warning needed; discovery successful

**When Discovery Has Partial Content** (1-2 credible sources, some sources failed or timed out):
- System generates digest from available content
- Digest may have fewer insights/resources than MVP targets (e.g., 1 insight instead of 1-3, 1 resource instead of 3-5)
- Digest includes quality warning: "⚠️ Low-signal content — insights below represent the best available material" (matching MVP)
- Digest indicates discovery status: "Discovery incomplete: [source name] unavailable"

**When Discovery Has No Relevant Content** (0 credible sources, or all sources failed/timed out):
- System displays message: "No relevant content discovered for topic '[topic]'. Invoke again later, or use snippets mode for testing: `/daily-digest [topic] "[snippet1]" "[snippet2]"`"
- Snippets mode is for testing only — not a user-facing fallback

**Timeout Behavior**:
- If discovery takes >45 seconds, system stops waiting and generates digest from results received so far
- If results received are low-signal, digest includes timeout warning: "Discovery incomplete: operation timed out"
- User-visible message clarifies that partial results were used

### Edge Cases

- Very new breaking news (content exists but not yet published widely): Include recent sources with quality warning if few results available
- Non-English content: System prioritizes English; can include non-English if directly relevant and translated
- Content behind paywalls: Skip, continue with publicly accessible results only
- Ultra-niche topics with no public discovery: Display no-content fallback message

## Requirements *(mandatory)*

### Functional Requirements

**Core Discovery**:
- **FR-001**: System MUST discover relevant content on requested topic from multiple public sources (web, video, social media)
- **FR-002**: System MUST synthesize discovered content into digest format matching MVP output (1-3 insights, 2-4 anti-patterns, 1-3 actions, 3-5 resources)
- **FR-003**: System MUST complete discovery and digest generation within 45 seconds

**Deduplication & Quality**:
- **FR-004**: System MUST identify and merge duplicate or near-duplicate insights from multiple sources, retaining best-evidence version
- **FR-005**: System MUST classify sources as credible or non-credible: credible sources = published/established outlets, verified accounts, primary sources; non-credible sources = unverified accounts, promotional content, known spam domains
- **FR-006**: System MUST exclude non-credible sources entirely from the Insights, Anti-patterns, and Actions sections (only credible sources may support these)
- **FR-007**: System MAY include non-credible sources in the Resources section as an exception, only if they contain useful supplementary information; when included, non-credible resources MUST be ranked below credible resources (credible first)
- **FR-008**: System MUST apply MVP quality rubric to all discovered insights (≥2 on 3/4 dimensions: novelty, evidence, specificity, actionability)

**Attribution & Transparency**:
- **FR-009**: System MUST attribute each insight to the highest-credibility source supporting it (visible to user in digest)
- **FR-010**: System MUST indicate discovery completeness in digest (e.g., "Discovery incomplete: [source] unavailable" when sources fail or timeout)
- **FR-011**: System MUST include quality warning in digest when discovered content is low-signal or incomplete (matching MVP low-signal handling: "⚠️ Low-signal content — insights below represent the best available material")

**Reliability**:
- **FR-012**: System MUST handle individual discovery source failures gracefully: if some sources fail but credible content remains available, generate digest from available sources
- **FR-013**: System MUST timeout discovery at 45 seconds; if partial results received, generate digest from available content with timeout warning; if no credible content by timeout, display manual input fallback message
- **FR-014**: System MUST fall back to manual input mode if all discovery sources fail or no credible content is found

### Key Entities

- **DiscoveredSource**: Content from public sources (web, video, social media); includes text, URL, publication date, source credibility assessment
- **DiscoveryResult**: Digest generated from autonomous discovery; includes topic, insights with source attribution, discovery status (complete/partial/incomplete), quality warnings if applicable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System generates digest from autonomous discovery without requiring user to provide text snippets
- **SC-002**: Digest structure and format match MVP output (same sections: insights, anti-patterns, actions, resources)
- **SC-003**: Each insight in digest is attributed to a credible source (user sees source name/publication)
- **SC-004**: Discovery completes within 45 seconds; if timeout reached, system generates digest from best-available partial results with warning
- **SC-005**: When 1-2 credible sources available (partial discovery), digest is generated with quality warning ("⚠️ Low-signal content...") and discovery status message
- **SC-006**: When zero credible sources found or all discovery sources fail, system displays fallback message (no digest) guiding user to retry or use snippets mode for testing
- **SC-007**: Duplicate insights from multiple sources are merged; user sees single insight attributed to highest-credibility source
- **SC-008**: Snippets mode (`/daily-digest <topic> "[snippet1]"`) is available for testing; not a user-facing fallback

---

## Assumptions

1. **Discovery source availability**: Public sources available for most typical topics. If unavailable, system degrades gracefully (partial results or no-content fallback).
2. **User expectations for quality**: Users expect digests to meet the quality rubric (no padding, evidence required).
3. **Latency budget**: Discovery and digest generation must complete within 45 seconds. If timeout reached, system uses best-available partial results.
4. **Content duplication**: Multiple discovery sources return overlapping insights; system deduplicates and retains highest-credibility version.
5. **Snippets for testing**: Snippets mode is available for testing without MCP tools; not a user-facing fallback.
6. **English-first content**: System prioritizes English-language content; non-English included only if directly relevant and high quality.

---

## Dependencies & Constraints

**Core Dependencies**:
- `web_search` and `fetch` MCP tools — required for autonomous discovery
- Python 3.8+ stdlib — required for utility scripts
- `digests/` directory — must be writable

**External Dependencies**:
- Access to public web, video, and social media content for discovery
- Ability to fetch and parse content from multiple source types

**Constraints**:
- Discovery must complete within 45-second latency budget (timeout after 45 seconds, use best-available results)
- Output format must match MVP (same sections, counts, quality rubric application)
- Quality rubric must be applied to all discovered insights (≥2 on 3/4 dimensions; no padding)
- Insights must be drawn only from credible sources (no non-credible sources in insights; resources may include non-credible sources if lower-ranked)
- All insights must cite credible source in digest (no unsourced or hallucinated claims)

---

## Supporting Requirements (Non-User-Facing)

These are important implementation concerns that are not independent user-facing features:

- **Parallel discovery**: Discovery from multiple sources should execute efficiently (not sequentially) to provide fast user experience
- **Graceful degradation**: System should continue functioning when individual discovery sources fail, generate digests from available sources, and provide transparency about incomplete discovery

## Notes

- Autonomous discovery quality is validated via the quality rubric and /validate-digest
- Future: Phase 3 adds feedback and learning; Phase 4 adds automation and scale
- User-facing output emphasizes source attribution: each insight indicates which source(s) support it
- Excluded low-credibility sources are handled internally; users see quality warnings if discovery is incomplete, but not lists of rejected sources
