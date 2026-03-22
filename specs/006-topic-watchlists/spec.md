# Feature Specification: Topic Watchlists

**Feature Branch**: `006-topic-watchlists`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "Topic watchlists: Support recurring digests for saved topics like ai-agents, openai, claude-code with one command refresh all of them"

## Clarifications

### Session 2026-03-22

- Q: How is the watchlist feature surfaced as a command? → A: New standalone skill `/watchlist` with subcommands (`refresh`, `add`, `remove`, `list`)
- Q: How does the system associate a digest file with a specific topic name? → A: Topic name embedded in filename: `{YYYY-MM-DD}-{topic-name}.md` (e.g., `2026-03-22-ai-agents.md`)
- Q: What happens when the user adds a topic already in the watchlist? → A: No-op with a notice — display "topic already in watchlist" and continue normally
- Q: Should the watchlist config file be committed to git by default or gitignored? → A: Gitignored by default — watchlist is a personal local preference
- Q: What happens when `/watchlist refresh` is run on an empty watchlist? → A: Display a friendly notice ("watchlist is empty, add topics with `/watchlist add <topic>`") and exit cleanly

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Refresh All Watchlist Topics at Once (Priority: P1)

A user has previously saved a set of topics they care about (e.g., `ai-agents`, `openai`, `claude-code`). With a single command, they refresh all of them, receiving a fresh digest for each topic without having to invoke the skill multiple times.

**Why this priority**: This is the core value proposition — batch refresh eliminates repetitive manual invocations and makes the feature feel like a real subscription system.

**Independent Test**: Can be fully tested by defining a watchlist with 2–3 topics and running the refresh command, then verifying that a new digest file exists for each topic.

**Acceptance Scenarios**:

1. **Given** a watchlist contains `ai-agents`, `openai`, and `claude-code`, **When** the user runs the refresh command, **Then** a new digest is generated for each topic and saved to `digests/{YYYY}/{MM}/`.
2. **Given** one topic in the watchlist has a digest from earlier today, **When** the user refreshes, **Then** that topic is skipped and a skip notice appears in the run summary.
3. **Given** the refresh command completes, **When** the user reviews output, **Then** a summary lists which topics were refreshed, which were skipped, and any that failed.

---

### User Story 2 - Manage the Watchlist (Priority: P2)

A user can add or remove topics from their watchlist without editing raw files — using simple commands to maintain the list over time.

**Why this priority**: Watchlists are only useful if they stay current. Without easy management, users accumulate stale topics or abandon the feature.

**Independent Test**: Can be fully tested by adding a new topic, listing the watchlist to confirm it appears, then removing it and confirming it is gone.

**Acceptance Scenarios**:

1. **Given** no watchlist exists, **When** the user adds the first topic `claude-code`, **Then** the watchlist is created with that topic.
2. **Given** a watchlist has three topics, **When** the user removes one, **Then** the watchlist has two topics and the removed one no longer appears in refresh runs.
3. **Given** the user lists watchlist topics, **When** the command runs, **Then** all saved topics are displayed with their names and the date of their last generated digest.

---

### User Story 3 - View Watchlist Digest History (Priority: P3)

A user can quickly see, per saved topic, when the last digest was generated and navigate to it.

**Why this priority**: Gives users confidence their watchlist is active and helps them find recent output without browsing the digests folder manually.

**Independent Test**: Can be fully tested by generating a digest for one watchlist topic, then running the history view and verifying the entry appears with the correct date and file path.

**Acceptance Scenarios**:

1. **Given** a topic has had three digests generated, **When** the user views history for that topic, **Then** they see the three most recent digests with dates and file paths.
2. **Given** a topic has never been refreshed, **When** the user views history, **Then** the output indicates no digests exist yet for that topic.

---

### Edge Cases

- What happens when a watchlist topic name contains spaces or special characters?
- How does the system handle a refresh when content discovery fails mid-run for one topic?
- What happens when the `digests/` directory is not writable during a batch refresh?
- If the watchlist file is empty or contains no topics, `/watchlist refresh` displays a friendly notice ("watchlist is empty, add topics with `/watchlist add <topic>`") and exits cleanly.
- How does the system behave if the watchlist file is malformed (unparseable)?
- What if the user runs refresh while a previous refresh is still in progress?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to define a persistent watchlist of named topics that survives between sessions.
- **FR-002**: The `/watchlist refresh` subcommand MUST generate a fresh digest for every topic in the watchlist in a single invocation.
- **FR-003**: System MUST skip a topic during batch refresh if a digest for that topic already exists for today's date, and report the skip in the run summary.
- **FR-004**: System MUST produce a per-run summary listing: topics refreshed, topics skipped (already fresh today), and topics that failed with a reason.
- **FR-005**: The `/watchlist add <topic>` subcommand MUST add the named topic to the watchlist; if the topic already exists, it MUST display a "topic already in watchlist" notice and take no further action.
- **FR-006**: The `/watchlist remove <topic>` subcommand MUST remove the named topic from the watchlist.
- **FR-007**: The `/watchlist list` subcommand MUST display all topics currently in the watchlist along with the date of the last generated digest for each.
- **FR-008**: Each per-topic digest generated during a batch refresh MUST follow the same output format and quality standards as a manually invoked single-topic digest.
- **FR-009**: System MUST store watchlist configuration as a file in the project directory; the file MUST be gitignored by default (personal local preference), with users able to opt in to version-controlling it by removing the ignore rule.
- **FR-010**: System MUST process watchlist topics independently so that a failure on one topic does not prevent the remaining topics from being processed.

### Key Entities

- **Watchlist**: A persistent, ordered collection of topic entries the user wants to track. There is one default watchlist per project.
- **Topic Entry**: A single saved topic. Has a name (e.g., `ai-agents`), an optional display label, and a reference to the most recently generated digest for that topic.
- **Batch Refresh Run**: A single execution of the refresh-all command. Records start time, per-topic outcomes (refreshed / skipped / failed), and an overall summary.
- **Digest**: An existing concept — a date-stamped Markdown file in `digests/{YYYY}/{MM}/`. In the watchlist context, digest filenames follow the pattern `{YYYY-MM-DD}-{topic-name}.md` (e.g., `2026-03-22-ai-agents.md`), enabling the system to locate and check freshness by scanning the filesystem.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user with 5 topics in their watchlist can refresh all of them with a single command invocation (no repeated manual steps required).
- **SC-002**: The refresh command produces a clear summary within the same session, listing each topic's outcome (refreshed, skipped, or failed).
- **SC-003**: Topics that already have a digest for today are consistently skipped — no duplicate digest files are created for the same topic on the same date.
- **SC-004**: A failure on any single topic during batch refresh does not prevent remaining topics from being processed.
- **SC-005**: Adding, removing, and listing watchlist topics each complete in a single command with no additional prompts required.

## Assumptions

- The watchlist is stored as a simple file in the project root or a designated config directory, consistent with the project's file-system-only storage model.
- Topic names are short identifiers (e.g., `ai-agents`, `claude-code`) — the same strings a user would pass to the existing single-topic digest command.
- A "fresh" digest for today means a file matching `{today's date}-{topic-name}.md` already exists in `digests/{YYYY}/{MM}/` — staleness is determined by date only, not time of day.
- The initial implementation targets a single default watchlist; named or multiple watchlists are out of scope.
- No scheduling or background automation is in scope — all refreshes are user-initiated.
- Topics are processed sequentially to avoid overloading discovery; parallel processing is a future enhancement.
