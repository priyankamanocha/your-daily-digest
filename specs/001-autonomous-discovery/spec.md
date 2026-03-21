# Feature Specification: Phase 2 — Autonomous Content Discovery

**Feature Branch**: `001-autonomous-discovery`
**Created**: 2026-03-21
**Status**: Draft
**Phase**: 2 (Post-MVP)
**Timeline**: 2-3 weeks after Phase 1 MVP validation

## Overview

Extend SignalFlow from manual text curation (MVP) to autonomous discovery of relevant content from web, video, and social media sources. Users provide a topic; the system discovers, deduplicates, and synthesizes insights without manual content gathering.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autonomous Topic Discovery (Priority: P1)

As a knowledge worker, I want to run `/daily-digest <topic>` (topic only, no text snippets) and receive a digest synthesized from autonomous discovery, without manually gathering content.

**Why this priority**: This is the core Phase 2 value — removes manual content curation entirely. Without autonomous discovery, Phase 2 adds no user value.

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
- System displays message: "No relevant content discovered for topic '[topic]'. Try providing text snippets manually: `/daily-digest [topic] "[snippet1]" "[snippet2]"...`"
- User can provide text snippets to trigger MVP manual mode as fallback

**Timeout Behavior**:
- If discovery takes >45 seconds, system stops waiting and generates digest from results received so far
- If results received are low-signal, digest includes timeout warning: "Discovery incomplete: operation timed out"
- User-visible message clarifies that partial results were used

### Edge Cases

- Very new breaking news (content exists but not yet published widely): Include recent sources with quality warning if few results available
- Non-English content: System prioritizes English; can include non-English if directly relevant and translated
- Content behind paywalls: Skip, continue with publicly accessible results only
- Ultra-niche topics with no public discovery: Fall back to manual mode request

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
- **SC-006**: When zero credible sources found or all discovery sources fail, system displays fallback message (no digest) guiding user to provide text snippets manually
- **SC-007**: Duplicate insights from multiple sources are merged; user sees single insight attributed to highest-credibility source
- **SC-008**: User can invoke `/daily-digest <topic> <text_snippet>` to trigger MVP manual mode as fallback when autonomous discovery is insufficient

---

## Assumptions

1. **Discovery source availability**: Public sources available for most typical topics. If sources unavailable, system degrades gracefully (returns partial results or falls back to manual mode).
2. **User expectations for quality**: Users expect Phase 2 autonomous digests to match MVP manually-curated quality (insights pass quality rubric, no artificial padding).
3. **Latency budget**: Discovery and digest generation must complete within 45 seconds. If timeout reached, system uses best-available partial results rather than waiting longer.
4. **Content duplication**: Multiple discovery sources return overlapping insights; system deduplicates and retains highest-credibility version.
5. **Backward compatibility**: MVP manual mode (`/daily-digest <topic> <text_snippet>`) continues to work alongside Phase 2 autonomous mode.
6. **English-first content**: System prioritizes English-language content; non-English included only if directly relevant and high quality.

---

## Dependencies & Constraints

**Dependencies on Phase 1 (MVP)**:
- Phase 2 reuses entire MVP insight extraction engine, quality rubric, and output format
- Phase 2 adds discovery + deduplication layer on top of MVP (no changes to MVP core)
- Phase 2 must maintain backward compatibility: `/daily-digest <topic> <text_snippet1>` (manual mode) still works

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

These are important implementation concerns that enable Phase 2 but are not independent user-facing features:

- **Parallel discovery**: Discovery from multiple sources should execute efficiently (not sequentially) to provide fast user experience
- **Graceful degradation**: System should continue functioning when individual discovery sources fail, generate digests from available sources, and provide transparency about incomplete discovery

## Notes

- Phase 2 validates that autonomous discovery can match MVP manual quality
- Post-Phase 2 decision: If autonomous quality is validated, Phase 3 could default to autonomous; if not, MVP manual mode remains primary
- User-facing output emphasizes source attribution: each insight indicates which source(s) support it
- Excluded low-credibility sources are handled internally; users see quality warnings if discovery is incomplete, but not lists of rejected sources
