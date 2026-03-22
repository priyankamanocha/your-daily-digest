# Feature Specification: Source Allowlist / Blocklist

**Feature Branch**: `008-source-allowlist-blocklist`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "source allowlist/blocklist. Let users pin trusted domains/handles and exclude noisy sources per topic"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Block a Noisy Source (Priority: P1)

A user runs a daily digest on "AI safety" and keeps seeing results from a low-quality blog that dominates search results. They add the domain to their blocklist for that topic. On the next run, no results from that domain appear in the digest.

**Why this priority**: Blocklisting is the highest-value action — users reach for it the moment a source degrades their digest quality. It delivers immediate, verifiable relief and requires no change to how the skill is invoked.

**Independent Test**: Configure a blocklist entry for a domain and run the digest. Verify the blocked domain does not appear in any resource, insight, anti-pattern, or action in the output. Delivers full value as a standalone capability.

**Acceptance Scenarios**:

1. **Given** a blocklist entry for `noisyblog.com` under topic `"AI safety"`, **When** the web discovery agent finds an article from `noisyblog.com`, **Then** that source is excluded before scoring and does not appear in the digest or manifest.
2. **Given** a blocklist entry for `noisyblog.com` under topic `"AI safety"`, **When** the digest for a *different* topic (e.g., `"climate"`) is run, **Then** `noisyblog.com` results are not filtered and may appear normally.
3. **Given** a blocklist entry for `@noisehandle` (a social handle), **When** the social discovery agent returns a post from `@noisehandle`, **Then** that post is excluded from the digest.

---

### User Story 2 - Pin a Trusted Source (Priority: P2)

A user follows a specific research lab's blog and always wants it represented in their digest. They add the domain to their allowlist for the topic. On subsequent runs, if the domain produces content within the freshness window, it is prioritised for inclusion even if its raw quality score would otherwise deprioritise it.

**Why this priority**: Pinning trusted sources gives users a personalized signal boost without having to retype `--hints` on every invocation. It builds on the blocklist infrastructure and adds positive curation.

**Independent Test**: Configure an allowlist entry for a domain and run the digest. Verify the pinned domain's content, if discovered and fresh, is included in the digest even when competing candidates would normally rank higher.

**Acceptance Scenarios**:

1. **Given** an allowlist entry for `trusteddomain.org` under topic `"machine learning"`, **When** the web discovery agent returns an article from `trusteddomain.org` within the freshness window, **Then** that source is guaranteed inclusion in the digest provided it scores 2 on at least 1 quality dimension, regardless of how other candidates rank.
2. **Given** an allowlist entry for `trusteddomain.org`, **When** no fresh content from `trusteddomain.org` is found during discovery, **Then** the digest proceeds normally without error — allowlisting is best-effort, not a guarantee.
3. **Given** an allowlist entry for `@researchlab` (a social handle), **When** the social agent finds a post from `@researchlab`, **Then** it is guaranteed inclusion in the digest provided it scores 2 on at least 1 quality dimension.

---

### User Story 3 - Manage Filters via Config File (Priority: P3)

A user wants to maintain their source preferences across sessions without retyping flags. They edit a single config file to add, remove, or update allowlist and blocklist entries per topic. The file is version-controllable and human-readable.

**Why this priority**: The config file is the persistence layer. Without it, rules only exist per-invocation. It unlocks the primary value of both allowlist and blocklist across sessions, but comes after the filtering logic is working.

**Independent Test**: Create a config file with allowlist and blocklist entries, invoke the digest, and verify the entries take effect without passing any extra flags at runtime.

**Acceptance Scenarios**:

1. **Given** a config file with valid entries, **When** the daily-digest skill starts, **Then** the config is loaded automatically with no extra flags required.
2. **Given** a config file with a syntax error, **When** the daily-digest skill starts, **Then** the skill halts with a clear error message identifying the file and the problem line, before any discovery runs.
3. **Given** no config file exists, **When** the daily-digest skill runs, **Then** it proceeds with no filtering applied (same behavior as today).

---

### User Story 4 - Apply Global (Topic-Agnostic) Rules (Priority: P4)

A user wants to block a spam aggregator across all topics without repeating the entry. They add it to a global section of the config. It applies to every digest run regardless of topic.

**Why this priority**: Reduces repetition for sources that are universally unwanted or trusted. Adds polish after per-topic filtering is stable.

**Independent Test**: Add a global blocklist entry. Run digests for two different topics and verify the blocked source is absent from both.

**Acceptance Scenarios**:

1. **Given** a global blocklist entry for `spamsite.com`, **When** any digest is run regardless of topic, **Then** `spamsite.com` results are excluded.
2. **Given** a topic-level allowlist entry that conflicts with a global blocklist entry, **When** the digest runs for that topic, **Then** the topic-level rule takes precedence.

---

### Edge Cases

- If a domain appears in both the allowlist and blocklist for the same topic, the block rule wins and the source is excluded.
- A bare domain entry (`example.com`) matches `example.com` and `www.example.com` only. To block a specific subdomain, users must list it explicitly (e.g., `blog.example.com`). No wildcard matching is supported.
- What if the config file is present but empty?
- What if an allowlisted source has no fresh content within the time window?
- What if a URL from discovery matches a blocked handle pattern but is from a different platform?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to define a list of trusted sources (allowlist) per topic in a persistent config file.
- **FR-002**: Users MUST be able to define a list of excluded sources (blocklist) per topic in a persistent config file.
- **FR-003**: Users MUST be able to define global allowlist and blocklist entries that apply across all topics.
- **FR-004**: The system MUST exclude any source whose domain or handle matches a blocklist entry before scoring or inclusion in the digest.
- **FR-005**: The system MUST guarantee inclusion of sources whose domain or handle matches an allowlist entry, provided the source has content within the freshness window and scores 2 on at least 1 quality dimension (minimum quality floor). Allowlisted sources meeting this floor are included regardless of how other candidates rank.
- **FR-006**: Topic-level rules MUST take precedence over global rules when a conflict exists for the same source.
- **FR-006a**: When a source appears in both the allowlist and blocklist for the same topic, the block rule MUST take precedence and the source MUST be excluded.
- **FR-007**: The system MUST load the config file automatically on each digest run, requiring no additional flags from the user.
- **FR-008**: If the config file contains a syntax error, the system MUST halt before discovery begins and report a clear error identifying the file and the problem.
- **FR-009**: If no config file exists, the system MUST proceed normally with no filtering applied.
- **FR-010**: Source matching MUST support both domain names (e.g., `example.com`) and social handles (e.g., `@username`). Matching is exact host-level only — no wildcards or glob patterns are supported. A bare domain entry (e.g., `example.com`) matches both `example.com` and `www.example.com` but not other subdomains such as `blog.example.com`.
- **FR-011**: The config file format MUST be human-readable and version-controllable.
- **FR-012**: Blocklist and allowlist application MUST be recorded in the sidecar manifest so users can audit which sources were filtered or boosted.

### Key Entities

- **SourceFilter**: A single allowlist or blocklist rule containing a source identifier (domain or handle), the list type (allow/block), and an optional topic scope.
- **FilterConfig**: The full collection of SourceFilter rules, organised into per-topic sections and a global section, loaded from the config file at run time.
- **FilteredSourceRecord**: An extension of the existing SourceRecord that includes a `filter_action` field indicating whether the source was `blocked`, `boosted`, or `unaffected`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add or remove a source rule and see the change reflected in the next digest run without modifying any other file or flag.
- **SC-002**: 100% of sources matching a blocklist entry are absent from the digest output and marked as `blocked` in the manifest.
- **SC-003**: When an allowlisted source has fresh content and scores 2 on at least 1 quality dimension, it is always included in the digest — inclusion rate is 100% when the quality floor is met.
- **SC-004**: A config file with a syntax error causes the skill to halt with an actionable error message before any discovery work runs, avoiding wasted compute.
- **SC-005**: The feature adds no new required inputs to the existing invocation contract — existing invocations continue to work identically.

## Clarifications

### Session 2026-03-22

- Q: When a domain appears in both the allowlist and blocklist for the same topic, which rule wins? → A: Block wins — the source is always excluded.
- Q: How strong is the allowlist boost — tiebreaker only, or guaranteed inclusion? → A: Guaranteed inclusion — if fresh and scores 2 on ≥1 quality dimension, the source is always included regardless of other candidates' ranking.
- Q: Should source entries support wildcard/pattern matching (e.g., `*.reuters.com`)? → A: No wildcards — exact host-level matching only. A bare domain matches itself and its `www.` prefix only.

## Assumptions

- The config file is a JSON file (`sources.json`) located at the project root. YAML was considered but requires a third-party package (`pyyaml`), which violates the Python stdlib-only constraint (Constitution Principle V). JSON is stdlib-native and satisfies FR-011 (human-readable, version-controllable).
- Domain matching is exact host-level with no wildcard support (fully specified in FR-010).
- Handle matching is case-insensitive and platform-agnostic (e.g., `@researcher` matches that handle on any social platform).
- Allowlisting is a best-effort boost, not a guarantee of inclusion — if an allowlisted source produces no fresh content, no error or warning is raised.
- The config file is optional; its absence is a normal condition, not an error.
- The `--hints` flag in the existing invocation contract remains separate from the allowlist. Hints are one-off per-invocation overrides; the allowlist is a persistent preference.
