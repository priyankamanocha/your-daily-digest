# Feature Specification: Digest Diffing

**Feature Branch**: `007-digest-diffing`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "digest diffing. compare today's digest with the previous one and add whats changed since last run to reduce repeated insights"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Suppress Repeated Insights on Re-run (Priority: P1)

A user runs the daily digest on the same topic two days in a row. Yesterday's digest covered events A, B, and C. Today's discovery finds A (still trending), B (still mentioned), and D (brand new). With digest diffing, today's output surfaces only D as a new insight, while A and B are silently omitted or flagged as already covered — so the user reads only what is genuinely new.

**Why this priority**: This is the core value proposition. Without it, users re-read the same insights daily, eroding trust and making the digest feel stale.

**Independent Test**: Run `/daily-digest` on any topic twice on consecutive days. Confirm that insight titles or evidence quotes that appeared in the previous digest are absent (or explicitly marked "previously covered") in today's output.

**Acceptance Scenarios**:

1. **Given** a previous digest exists for topic "Claude Cowork", **When** today's discovery finds 2 insights already present in yesterday's digest and 1 new one, **Then** today's digest contains only the 1 new insight (not the 2 repeats).
2. **Given** a previous digest exists, **When** an insight has the same source and overlapping evidence quote as a prior insight, **Then** it is classified as a repeat and excluded from the final output.
3. **Given** today's discovery finds only insights already covered in the previous digest, **Then** the digest is generated with a low-signal warning noting that no new material was found, rather than an empty or failed output.

---

### User Story 2 — Graceful First Run (No Previous Digest) (Priority: P1)

A user runs the digest for a topic that has no prior digest on disk. Digest diffing must not block or error; it simply runs as today without filtering anything.

**Why this priority**: Without graceful handling of the first-run case, the feature would break all new topics and new users.

**Independent Test**: Delete or rename any existing digest file and run `/daily-digest` on that topic. Confirm the digest generates normally with no diff-related errors or warnings.

**Acceptance Scenarios**:

1. **Given** no previous digest exists for the requested topic, **When** the digest is generated, **Then** all discovered insights are included without filtering and no diff-related warnings appear.
2. **Given** no previous digest exists, **When** the digest is generated, **Then** the output is identical to what would be produced without the diffing feature.

---

### User Story 3 — Stale Previous Digest Treated as Fresh (Priority: P2)

A user runs a digest today but the most recent prior digest for that topic is more than 7 days old. Since the news cycle has moved on, the previous digest is considered too stale to diff against, and today's run includes all discovered insights without filtering.

**Why this priority**: Stale digests would cause legitimate new coverage of recurring topics to be incorrectly suppressed.

**Independent Test**: Place a digest file dated 10+ days ago and run today's digest on the same topic. Confirm all discovered insights appear in today's output unfiltered.

**Acceptance Scenarios**:

1. **Given** the most recent previous digest is older than 7 days, **When** today's digest runs, **Then** no insights are filtered and a note appears indicating the previous digest was too old to diff against.
2. **Given** the most recent previous digest is exactly 7 days old, **Then** it is treated as within the staleness window and insights are still compared (boundary inclusive).

---

### Edge Cases

- What happens when the previous digest is malformed or empty? System skips diffing and runs as a first-run (no filtering).
- What happens when a resource URL repeats but the insight text is new? Only insight-level content (title + evidence) is compared — URL-only matches are not filtered.
- What if today's run finds fewer than the minimum insight count after filtering? The digest is generated with available new material plus a low-signal warning, consistent with existing quality policy.
- What if multiple previous digests exist for the same topic? Only the most recent qualifying digest (within 7 days) is used for comparison.
- What happens when the user opts out of diffing? The full unfiltered run proceeds, identical to pre-feature behaviour.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST locate the most recent previous digest for the same topic before finalising today's output.
- **FR-002**: The system MUST compare each discovered item against corresponding items in the previous digest across all four sections (Key Insights, Anti-patterns, Actions to Try, Resources). A repeat is declared when both conditions hold: (1) the source attribution matches, and (2) the title or headline shares ≥50% of its words with a prior item's title.
- **FR-003**: The system MUST exclude items classified as repeats from the final digest output across all four sections.
- **FR-004**: The system MUST proceed without filtering when no qualifying previous digest exists (first run or prior digest older than 7 days).
- **FR-005**: The system MUST generate a valid digest even when all discovered insights are repeats, applying the existing low-signal warning rather than producing an empty or failed output.
- **FR-006**: The system MUST determine the previous digest by topic name and date, using the existing `digests/{YYYY}/{MM}/` directory structure.
- **FR-007**: The system MUST NOT modify or delete the previous digest file; comparison is read-only.
- **FR-008**: Users MUST be able to bypass diffing to force a full unfiltered run when needed.
- **FR-009**: When one or more items are suppressed, the digest MUST include a footer note stating the count and the date of the previous digest used as baseline (e.g., "3 items suppressed as already covered in digest from 2026-03-21"). When nothing is suppressed, no note appears.

### Key Entities

- **Previous Digest**: The most recent digest file on disk for the same topic, used as the comparison baseline. Key attributes: topic name, generation date, list of insight titles and evidence quotes.
- **Insight Fingerprint**: A lightweight representation of an insight used for comparison — derived from its title and evidence quote — without requiring identical wording.
- **Diff Result**: The outcome of comparing today's discovered insights against the previous digest: a set of new insights (pass through) and a set of repeats (suppressed).
- **Staleness Window**: The maximum age (7 days) of a previous digest for it to be eligible as a comparison baseline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Insights that appeared in the previous digest are absent from today's output in 100% of cases where a qualifying previous digest exists.
- **SC-002**: First-run and stale-baseline scenarios complete without errors or diff-related warnings.
- **SC-003**: When all discovered insights are repeats, the digest still generates a valid file with a low-signal warning rather than failing or producing an empty document.
- **SC-004**: Opt-out produces output identical to pre-feature behaviour, verifiable by comparing two runs with and without bypass on a topic with no prior digest.
- **SC-005**: Digest generation time does not increase by more than 5 seconds due to the diffing step.
- **SC-006**: When items are suppressed, a footer note appears stating the exact suppression count and the baseline digest date. When nothing is suppressed, no note appears.

## Clarifications

### Session 2026-03-22

- Q: Which digest sections should be diffed and deduplicated? → A: All four sections (Key Insights, Anti-patterns, Actions to Try, Resources)
- Q: What constitutes a "repeat" match? → A: Same source + significant title/headline overlap (≥50% shared words)
- Q: Should the digest surface a summary of what was filtered/skipped? → A: Brief footer note with count only: "X items suppressed as already covered in [previous digest date]"

## Assumptions

- Topic identity is determined by the topic slug in the digest filename, consistent with the existing naming convention (`digest-{YYYY-MM-DD}-{topic-slug}.md`).
- The 7-day staleness window is a reasonable default based on news-cycle cadence; this can be revisited based on user feedback.
- Similarity matching uses same-source + ≥50% title word overlap within the Python stdlib-only constraint — no external NLP library required.
- Opt-out is achieved via an invocation flag, consistent with how other digest parameters are passed.
- The feature does not retroactively update or annotate the previous digest to mark items as "already sent."
