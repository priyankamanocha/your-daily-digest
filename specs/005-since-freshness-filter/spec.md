# Feature Specification: Since Freshness Filter

**Feature Branch**: `005-since-freshness-filter`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "support --since freshness filter. default value if user doesnt specify anything should be one. since=1 means find all blogs, youtube video etc published since last 24 hours, true to the intent of project since it is your-daily-brief. but it should be possible for user to override it by saying since yesterday or give a time window like last month or feb 2026."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Default daily freshness (Priority: P1)

A user invokes `/daily-digest claude-code` without any `--since` flag. The skill automatically limits discovery to content published in the last 24 hours, matching the "daily" intent of the project.

**Why this priority**: This is the core behaviour — the default must work correctly without any user input, and it must reflect the project's daily-brief intent.

**Independent Test**: Run `/daily-digest claude-code` with no flags. Verify all discovered sources have a publication date within the last 24 hours (or are flagged as undated).

**Acceptance Scenarios**:

1. **Given** no `--since` flag is provided, **When** discovery agents run, **Then** only sources published within the last 24 hours are considered, equivalent to `--since 1`.
2. **Given** a source has no detectable publication date, **When** the agent encounters it, **Then** it is included with a note that the date could not be verified — not silently excluded.

---

### User Story 2 - Numeric day override (Priority: P2)

A user wants a broader window and runs `/daily-digest claude-code --since 7`. The skill expands discovery to content published in the last 7 days.

**Why this priority**: The most common override — users catching up after a few days away, or researching a topic with sparse daily coverage.

**Independent Test**: Run `/daily-digest claude-code --since 7`. Verify the digest includes sources up to 7 days old and that sources older than 7 days are excluded.

**Acceptance Scenarios**:

1. **Given** `--since 7` is provided, **When** discovery runs, **Then** sources published within the last 7 days are eligible and sources older than 7 days are excluded.
2. **Given** `--since 0` is provided, **When** the skill parses the argument, **Then** an error is shown: "since=0 is not valid — minimum value is 1."
3. **Given** `--since 365` is provided, **When** discovery runs, **Then** the skill accepts the value and applies the 365-day window without capping it.

---

### User Story 3 - Natural language date expressions (Priority: P3)

A user runs `/daily-digest claude-code --since "last month"` or `/daily-digest claude-code --since "feb 2026"`. The skill interprets the expression and applies the correct date window.

**Why this priority**: Reduces friction for users who think in calendar terms rather than day counts. Lower priority because the numeric form already covers the use case functionally.

**Independent Test**: Run with `--since "yesterday"`, `--since "last month"`, and `--since "feb 2026"`. Verify each resolves to the correct date window relative to the run date.

**Acceptance Scenarios**:

1. **Given** `--since yesterday`, **When** discovery runs, **Then** only content from the previous calendar day is eligible.
2. **Given** `--since "last month"`, **When** discovery runs, **Then** content from the last 30 days is eligible.
3. **Given** `--since "feb 2026"`, **When** discovery runs, **Then** content published between 2026-02-01 and 2026-02-28 is eligible.
4. **Given** an unrecognisable expression like `--since "next tuesday"`, **When** the skill parses it, **Then** a clear error is shown: `Could not interpret '--since next tuesday'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'.`

---

### Edge Cases

- What happens when `--since` is provided but empty (`--since ""`)? → Treat as invalid; halt with a clear error message. Never silently fall back to the default — the user provided the flag intentionally.
- What if a source's publication date is in the future (data error)? → Exclude it and log as an anomaly.
- What if `--since` is used with snippet mode? → `--since` applies to autonomous discovery only; user-supplied snippets are always processed regardless of date.
- What if discovery returns zero sources within the window? → Produce the no-content fallback message with the active window clearly stated (e.g., "No sources found in the last 3 days").

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The skill MUST default to a 24-hour freshness window (`since=1`) when no `--since` flag is provided.
- **FR-002**: The skill MUST accept `--since <N>` where N is a positive integer representing the number of days to look back.
- **FR-003**: The skill MUST reject `since=0` or negative values with a clear, actionable error message and halt discovery.
- **FR-004**: The skill MUST accept `--since yesterday` and resolve it to the previous calendar day relative to the run date.
- **FR-005**: The skill MUST accept `--since "last month"` and resolve it to the trailing 30 days relative to the run date.
- **FR-006**: The skill MUST accept `--since "<month> <year>"` (e.g., `"feb 2026"`) and resolve it to the first and last day of that calendar month.
- **FR-007**: The skill MUST show a clear error for unrecognisable `--since` expressions, including examples of valid formats.
- **FR-008**: Discovery agents MUST receive the resolved freshness window (a start date and end date) and filter candidate sources accordingly.
- **FR-009**: Sources with no detectable publication date MUST be included in discovery results but flagged as undated, not silently excluded.
- **FR-010**: The active freshness window MUST be visible in the digest output (e.g., `Sources: last 24 hours` or `Sources: 1 Feb – 28 Feb 2026`).
- **FR-011**: The `--since` filter MUST apply to all autonomous discovery, including hint-guided discovery via `--hints`. User-supplied snippets are always processed regardless of date.

### Key Entities

- **Freshness Window**: A resolved date range (start date, end date) derived from the `--since` argument. End date is always the run date.
- **Dated Source**: A discovered source with a verifiable publication date that can be compared against the freshness window.
- **Undated Source**: A discovered source where no publication date can be determined. Included with a visible flag; never filtered out.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When no `--since` flag is given, 100% of digest runs apply the 24-hour window with no user intervention required.
- **SC-002**: All supported `--since` expressions (numeric, `yesterday`, `last month`, `<month> <year>`) resolve to the correct date window in all test cases.
- **SC-003**: Invalid `--since` inputs produce a readable error without running discovery — fast failure with no wasted work.
- **SC-004**: The active freshness window is visible in every digest output, making results auditable without re-running the skill.
- **SC-005**: Zero sources are silently excluded due to missing dates — undated sources are always surfaced with a visible flag.

## Clarifications

### Session 2026-03-22

- Q: For invalid `--since` inputs (empty, zero, unrecognisable), should the skill halt with an error or fall back silently to the 24-hour default? → A: Always halt with a clear error. Silently falling back masks misconfiguration.
- Q: Does `--since` apply to sources found via `--hints`, or do hint-guided sources bypass the freshness filter? → A: `--since` applies to all autonomous discovery including hint-guided sources. `--hints` narrows where agents look; `--since` governs what they return.

## Assumptions

- "Last month" means the trailing 30 days from the run date, not the previous calendar month. Users needing calendar-month precision should use the `<month> <year>` form.
- The run date is the date on which the skill is invoked (today's date as known to Claude Code).
- Natural language date parsing is performed by the skill's LLM reasoning step, keeping Python stdlib-only compliance — no date-parsing library is introduced.
- `--since` interacts only with the discovery phase. Scoring, deduplication, and synthesis are unaffected.
- The feature number 004 was skipped by the branching system; this feature is correctly numbered 005.
