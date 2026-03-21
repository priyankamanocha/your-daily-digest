# Feature Specification: Source Manifest Output

**Feature Branch**: `003-source-manifest`
**Created**: 2026-03-21
**Status**: Draft

## Overview

Every `/daily-digest` run produces a sidecar manifest file alongside the digest. The manifest records every source discovered, its credibility and freshness scores, deduplication decisions, quality rubric scores for each candidate insight, and the final section selections. This makes the digest fully auditable and dramatically easier to debug when output quality is unexpected.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect Why an Insight Was Included or Excluded (Priority: P1)

As a developer or power user, I want to open the manifest file after running `/daily-digest` and immediately understand why any specific insight appeared in the digest — or why it didn't — without re-running discovery.

**Why this priority**: The manifest's core value is traceability. Without knowing why something was selected or rejected, debugging a poor-quality digest requires re-running the skill and guessing. This story delivers that value on its own.

**Independent Test**:
- Run `/daily-digest <topic>` autonomously
- Open the sidecar manifest file
- Verify every source has a credibility score and every candidate insight has quality rubric scores and a pass/fail result

**Acceptance Scenarios**:

1. **Given** a digest was successfully generated, **When** the user opens the manifest, **Then** every source discovered by all agents is listed with its credibility score, freshness score, and the signal used to assign credibility
2. **Given** a source was excluded from insights but appears in resources, **When** the user reads the manifest, **Then** the source entry shows `credibility_score < 2` and the section it was relegated to
3. **Given** a candidate insight failed the quality rubric, **When** the user reads the manifest, **Then** the candidate entry shows per-dimension scores and `quality_pass: false` with the dimensions that failed

---

### User Story 2 - Trace Deduplication Decisions (Priority: P2)

As a developer, I want to see which sources were grouped as near-duplicates and which version was retained, so I can verify the deduplication logic is working correctly.

**Why this priority**: Deduplication is silent — the user only sees the winning insight. When the wrong version is retained (e.g. a lower-credibility source wins), there is no way to diagnose it without the manifest.

**Independent Test**:
- Run `/daily-digest` on a topic with overlapping content across sources
- Verify the manifest lists deduplication groups showing grouped candidates and the kept version

**Acceptance Scenarios**:

1. **Given** two or more sources covered the same insight, **When** the user reads the manifest, **Then** a deduplication group entry lists all grouped source URLs, identifies the winner, and states the reason (highest credibility; freshness as tiebreaker)
2. **Given** a source was deduplicated away, **When** the user reads the manifest, **Then** the source appears in the deduplication group as a rejected entry — not silently absent from the output

---

### User Story 3 - Confirm Final Section Selections (Priority: P3)

As a developer reviewing digest quality, I want to see the complete mapping of what made it into each digest section and from which source, so I can verify section counts and attribution are correct.

**Why this priority**: Validates the final output without parsing the markdown digest — useful for automated quality checks and regression testing.

**Independent Test**:
- Compare the manifest's `section_selections` against the rendered digest
- Verify every item in the digest maps to exactly one entry in the manifest

**Acceptance Scenarios**:

1. **Given** a digest with 2 insights, **When** the user reads the manifest section_selections, **Then** exactly 2 insight entries are listed with their source URL and quality scores
2. **Given** the digest was generated with a quality warning (partial sources), **When** the user reads the manifest, **Then** `discovery_status` reflects the partial state and `agents_failed` lists which agents did not complete

---

### Edge Cases

- **No digest created (fallback)**: Manifest is NOT written — no manifest file when no digest file is created
- **Partial discovery (timeout or agent failure)**: Manifest is written with results from available agents only; missing agents listed under `agents_failed`
- **Zero candidates after quality filter**: Manifest records all candidates with their failing scores; `section_selections.key_insights` is an empty list
- **Snippets mode (test mode)**: Manifest is written with `discovery_status: manual`; `sources` lists each snippet as a synthetic source entry with no credibility scoring

---

## Requirements *(mandatory)*

### Functional Requirements

**Manifest File**:
- **FR-001**: System MUST write a manifest file alongside every successfully created digest file; if no digest file is created, no manifest is written
- **FR-002**: Manifest file path MUST mirror the digest path, replacing `.md` with `.manifest.json` (e.g. `digests/2026/03/digest-2026-03-21-claude-code.manifest.json`)
- **FR-003**: Manifest MUST be valid JSON and include a `schema_version` field

**Source Records**:
- **FR-004**: Manifest MUST include every source returned by all discovery agents with: `url`, `title`, `source_type` (web/video/social/snippet), `agent`, `author_or_handle`, `date`, `days_old`, `credibility_score` (0–3 or null for snippets), `credibility_signal`, `freshness_score` (0–3), `summary`

**Deduplication Records**:
- **FR-005**: Manifest MUST include one deduplication group entry for every set of semantically equivalent candidates; each group MUST list all grouped source URLs, identify the winner URL, and state the reason (credibility score; freshness as tiebreaker)

**Candidate Records**:
- **FR-006**: Manifest MUST include one candidate record per deduplicated insight candidate with: `title`, `primary_source_url`, `credibility_score`, `freshness_score`, quality rubric scores for all four dimensions (`novelty`, `evidence`, `specificity`, `actionability` — each 0–2), `quality_pass` (boolean), and `rejection_reason` if `quality_pass` is false

**Section Selections**:
- **FR-007**: Manifest MUST record the final items selected for each digest section (`key_insights`, `antipatterns`, `actions`, `resources`), each entry with `title` and `primary_source_url`
- **FR-008**: Manifest MUST record `discovery_status`, `agents_succeeded`, `agents_failed`, and `quality_warning` (boolean)

### Key Entities

- **SourceRecord**: One per discovered source — url, title, source_type, agent, author_or_handle, date, days_old, credibility_score, credibility_signal, freshness_score, summary
- **DeduplicationGroup**: Grouping of semantically equivalent candidates — group_id, candidate_urls[], winner_url, reason
- **CandidateRecord**: One per post-dedup candidate — title, primary_source_url, credibility_score, freshness_score, quality_scores {novelty, evidence, specificity, actionability}, quality_pass, rejection_reason
- **SectionSelections**: Final selected items by section — key_insights[], antipatterns[], actions[], resources[] (each item: title, primary_source_url)
- **ManifestFile**: Top-level container — schema_version, topic, generated_at, discovery_status, agents_succeeded[], agents_failed[], quality_warning, sources[], deduplication_groups[], candidates[], section_selections

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A manifest file is present alongside every successfully generated digest; zero digests are written without a corresponding manifest
- **SC-002**: Every source in the manifest is traceable to a specific discovery agent and has a credibility score (or explicit null for snippets)
- **SC-003**: Every item appearing in the digest can be found in `section_selections` in the manifest — no digest content is unaccounted for
- **SC-004**: Every candidate insight that did not make the digest has a `quality_pass: false` entry with per-dimension scores showing where it failed
- **SC-005**: Every source URL involved in deduplication appears in a deduplication group — no source is silently merged without a record

---

## Assumptions

1. **Format**: JSON is the output format; YAML is not required. JSON is universally parseable and consistent with the existing Python scripts.
2. **Write timing**: Manifest is written immediately after the digest in the same step. If digest writing fails, no manifest is written.
3. **Snippets mode**: Snippets are recorded as synthetic source entries with `source_type: snippet` and `credibility_score: null` (not scored).
4. **Manifest size**: No size limit imposed. For typical topics (30–40 sources, 10–20 candidates), manifests will be under 100 KB.
5. **Privacy**: Manifests contain only publicly discoverable URLs and metadata — no user data.
6. **Schema stability**: The manifest schema is versioned via `schema_version`. Breaking changes increment the version.

---

## Dependencies & Constraints

- **Depends on**: `daily-digest` skill — manifest is a side-effect of a successful digest run
- **Output location**: Same `digests/` directory as the digest — same writability requirement
- **Python stdlib only**: Manifest serialisation uses the `json` stdlib module; no third-party packages
- **Constraint**: `schema_version` field is mandatory to support future schema evolution without breaking existing readers
