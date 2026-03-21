# Feature Specification: Post-Write Digest Validator

**Feature Branch**: `004-post-write-validator`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "Digest validation: add a post write validator that checks section counts, required evidence, broken formatting, and low signal warnings"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch Missing Evidence Before Reading (Priority: P1)

After a digest is written, the validator runs automatically and immediately tells the user whether required evidence (direct quotes) is present for every insight. If any insight is missing a quote, the validator reports which insight is affected.

**Why this priority**: Missing evidence is the most critical quality failure — an insight without a source quote cannot be verified and undermines the digest's credibility. Catching this early prevents a user from acting on unsubstantiated claims.

**Independent Test**: Run the validator against a digest where one insight has no `**Evidence**:` field. The validator should report exactly which insight is missing evidence and exit with a non-zero status.

**Acceptance Scenarios**:

1. **Given** a written digest where all insights include a `**Evidence**: "..."` field, **When** the validator runs, **Then** it reports evidence checks as passed with no failures.
2. **Given** a written digest where one insight is missing the `**Evidence**:` field, **When** the validator runs, **Then** it reports that insight by title as failing the evidence requirement.
3. **Given** a written digest where an insight has an `**Evidence**:` label but the value is not wrapped in double quotes, **When** the validator runs, **Then** it flags the insight as having malformed evidence.

---

### User Story 2 - Detect Section Count Violations (Priority: P2)

The validator counts items in each section and reports any section that falls outside its allowed range. A user running validation knows immediately whether the digest is structurally compliant or needs remediation.

**Why this priority**: Section count rules define the digest's format contract. Producing a digest with zero actions or six resources breaks downstream expectations and indicates a generation failure.

**Independent Test**: Run the validator against a digest with five resources (above the 3–5 ceiling) and zero actions (below the 1–3 floor). The validator should flag both violations independently.

**Acceptance Scenarios**:

1. **Given** a digest with 2 insights, 3 anti-patterns, 2 actions, and 4 resources (all within range), **When** the validator runs, **Then** it reports all section counts as compliant.
2. **Given** a digest with 0 insights, **When** the validator runs, **Then** it reports the Insights section as below minimum (minimum: 1).
3. **Given** a digest with 5 anti-patterns, **When** the validator runs, **Then** it reports the Anti-patterns section as exceeding maximum (maximum: 4).
4. **Given** a digest with 6 resources, **When** the validator runs, **Then** it reports the Resources section as exceeding maximum (maximum: 5).

---

### User Story 3 - Surface Broken Formatting (Priority: P3)

The validator scans the digest for structural formatting problems — missing required headings, unclosed code blocks, and malformed list items — and reports each problem with its location (line or section name).

**Why this priority**: Broken formatting prevents the digest from rendering correctly and makes sections unreadable. Evidence and count checks are meaningless if the structure is corrupt.

**Independent Test**: Run the validator against a digest with a missing `## Anti-patterns` heading. The validator should report the missing heading by name.

**Acceptance Scenarios**:

1. **Given** a well-formed digest, **When** the validator runs, **Then** no formatting errors are reported.
2. **Given** a digest missing the `## Resources` heading, **When** the validator runs, **Then** the validator reports that heading as absent.
3. **Given** a digest with an unclosed fenced code block, **When** the validator runs, **Then** the validator reports an unclosed code block error with the approximate line number.

---

### User Story 4 - Attach Low-Signal Warnings (Priority: P3)

When a section meets minimum count but the content is flagged as low-signal (per the digest template's quality warning mechanism), the validator confirms the warning is present in the output and surfaces it in the validation report.

**Why this priority**: Low-signal warnings are an explicit contract in the digest format. Validating their presence ensures the author has not silently omitted the warning when content quality was poor.

**Independent Test**: Run the validator against a digest that has only 1 resource but no low-signal warning footer. The validator should flag the missing warning.

**Acceptance Scenarios**:

1. **Given** a digest where a section meets minimum count and no low-signal warning is present, **When** the validator runs, **Then** no low-signal warning is required and none is reported missing.
2. **Given** a digest with a `⚠️ Low-signal content` footer present, **When** the validator runs, **Then** the validator confirms the warning is present in the report.
3. **Given** a digest where the author indicated low-signal intent in the `Discovery:` line but no warning footer appears, **When** the validator runs, **Then** the validator flags the inconsistency.

---

### Edge Cases

- What happens when the digest file does not exist at the given path?
- How does the validator handle a completely empty file?
- What happens when the digest has the right number of section headings but the content beneath them is empty?
- How does the validator behave when insight titles contain special characters or markdown formatting?
- What happens when the `**Evidence**:` value spans multiple lines?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The validator MUST accept a path to a written digest file as its sole input.
- **FR-002**: The validator MUST check that each of the four required sections (Key Insights, Anti-patterns, Actions to Try, Resources) is present by its exact heading text.
- **FR-003**: The validator MUST count items in each section and report any that fall outside the allowed range: Insights 1–3, Anti-patterns 2–4, Actions 1–3, Resources 3–5.
- **FR-004**: The validator MUST verify that every item in the Key Insights section includes an `**Evidence**:` field containing a value wrapped in double quotes.
- **FR-005**: The validator MUST detect unclosed fenced code blocks and report them with an approximate line reference.
- **FR-006**: The validator MUST check for the presence of the `⚠️ Low-signal content` footer when the `Discovery:` line indicates partial or timeout results.
- **FR-007**: The validator MUST produce a structured summary listing: pass/fail status per check, count of failures, and specific failure details (section name, line reference, or item title as applicable).
- **FR-008**: The validator MUST exit with a non-zero status code when any check fails, and exit with zero when all checks pass.
- **FR-009**: The validator MUST be invokable as a standalone script using only Python standard library.
- **FR-010**: The validator MUST handle missing files, empty files, and permission errors gracefully, reporting a clear error and exiting with a non-zero status.

### Key Entities

- **Digest File**: A written Markdown file conforming to the digest template. Contains a header block, four content sections, and an optional low-signal footer.
- **Validation Report**: The structured output produced by the validator. Includes a per-check result, overall pass/fail status, and actionable failure details.
- **Section**: A named block within the digest delimited by a level-2 heading (e.g., `## Key Insights`). Each section has a defined minimum and maximum item count.
- **Evidence Field**: A labeled field within an Insight item, formatted as `**Evidence**: "quote text"`. Required for every insight.
- **Low-Signal Warning**: The `⚠️ Low-signal content` footer line appended to digests when any section falls below its quality threshold.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four required section count checks complete and report results within the same run as the write operation, adding no perceptible delay to digest generation.
- **SC-002**: Every insight missing an evidence quote is identified and named in the report — zero false negatives for the evidence check across a suite of 20 representative digest fixtures.
- **SC-003**: Broken formatting (missing headings, unclosed blocks) is detected and reported with enough location detail that a reviewer can find the issue without scanning the full file manually.
- **SC-004**: The validator never exits with status zero when a required check has failed — false pass rate is 0%.
- **SC-005**: A developer unfamiliar with the digest format can interpret the validation report and understand what failed and where without consulting documentation.

## Assumptions

- The validator runs after `write_digest.py` has completed successfully; it does not perform the write itself.
- The digest template's section headings use the exact strings defined in `digest-template.md` (`## Key Insights (1–3)`, `## Anti-patterns (2–4)`, `## Actions to Try (1–3)`, `## Resources (3–5)`). The validator matches against these exact strings.
- "Low-signal" detection is triggered by the `Discovery:` metadata line containing the keywords `partial` or `timeout`, consistent with the template's field rules.
- Item counting logic uses the structural marker for each section type: `###` sub-headings for Insights and Actions, leading `- **` list items for Anti-patterns and Resources.
- The validator is invoked by the daily-digest orchestrator skill after each successful write; it is not a background or scheduled job.
