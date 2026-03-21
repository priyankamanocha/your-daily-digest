# Feature Specification: Skill Invocation Layer

**Feature Branch**: `002-skill-invocation-layer`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "invocation layer for the skill. add clear entrypoint and optional snippets into a single payload orchestrator and helper scripts both use"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Invoke Skill with a Single Canonical Command (Priority: P1)

A user invokes the daily-digest skill by typing a single command. Behind the scenes, the entrypoint parses the full argument string into a structured payload (topic, optional hints, optional snippets) and that same payload is available to both the orchestrator logic and all helper scripts without any additional parsing or re-interpretation.

**Why this priority**: The entrypoint is the foundation all other invocation paths build on. Without a canonical payload, each consumer (orchestrator, script) parses arguments differently, creating inconsistency and fragility.

**Independent Test**: Invoke the skill with a topic only — confirm that one canonical payload object is produced and that subsequent orchestrator steps and scripts consume it without any additional argument parsing.

**Acceptance Scenarios**:

1. **Given** a user types `/daily-digest "AI agents"`, **When** the skill entrypoint processes the input, **Then** a single structured payload is produced containing `topic = "AI agents"`, `hints = []`, and `snippets = []`
2. **Given** a valid payload is produced at the entrypoint, **When** the orchestrator proceeds to any step (preflight, validate, discover), **Then** it reads topic, hints, and snippets from the shared payload — not by re-parsing the raw argument string
3. **Given** any helper script is called during skill execution, **When** it needs invocation data, **Then** it reads from the shared payload rather than accepting topic/hints as separate positional arguments

---

### User Story 2 - Invoke Skill with Optional Snippets for Test Mode (Priority: P2)

A user invokes the skill with one or more quoted snippet strings appended to the command. The entrypoint detects snippets and includes them in the payload; the orchestrator then routes to manual/test mode using the same payload structure without any special-case argument handling.

**Why this priority**: Snippets enable testing without live MCP discovery. The current invocation mixes argument-parsing logic across the orchestrator and scripts, making it hard to add snippets without breaking normal mode. A unified payload makes snippets a first-class field rather than a special case.

**Independent Test**: Invoke the skill with a topic and two snippet strings — confirm the payload includes `snippets = ["...", "..."]` and that the orchestrator skips discovery and proceeds directly to content processing using those snippets.

**Acceptance Scenarios**:

1. **Given** a user types `/daily-digest "AI agents" "Snippet one" "Snippet two"`, **When** the entrypoint processes the input, **Then** the payload contains `topic = "AI agents"` and `snippets = ["Snippet one", "Snippet two"]`
2. **Given** a payload with non-empty snippets, **When** the orchestrator evaluates mode selection, **Then** it routes to test/manual mode by checking `payload.snippets` — not by scanning the raw argument string for quoted values
3. **Given** a payload with empty snippets, **When** the orchestrator evaluates mode selection, **Then** it routes to autonomous discovery mode

---

### User Story 3 - Invalid Invocation Produces a Clear Error at the Entrypoint (Priority: P3)

A user invokes the skill with a missing topic or malformed arguments. The entrypoint validates the payload before handing control to the orchestrator, and returns a clear error message describing what was wrong without executing any downstream steps.

**Why this priority**: Centralising validation at the entrypoint prevents partial execution and inconsistent error messages from different scripts.

**Independent Test**: Invoke the skill with no topic — confirm a single descriptive error is returned immediately and no discovery, file I/O, or script execution occurs.

**Acceptance Scenarios**:

1. **Given** a user invokes the skill with no arguments, **When** the entrypoint processes the input, **Then** it returns an error identifying the missing topic and does not proceed
2. **Given** a user invokes the skill with a topic that exceeds the allowed length, **When** the entrypoint validates the payload, **Then** it returns an error naming the violated constraint
3. **Given** a user invokes the skill with more than the allowed number of hints, **When** the entrypoint validates the payload, **Then** it returns an error before any discovery begins

---

### Edge Cases

- What happens when the topic is provided but contains only whitespace?
- How does the entrypoint handle snippet strings that are empty (`""`) or contain only whitespace?
- What happens when the `--hints` flag is present but no values follow it?
- How does the system behave if the payload JSON string passed to a script is malformed or unparseable?
- What happens when the same snippet is provided more than once?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The skill MUST expose a single, documented entrypoint that accepts the full raw invocation string and produces a canonical payload
- **FR-002**: The payload MUST contain exactly three fields: `topic` (required string), `hints` (optional list, default empty), and `snippets` (optional list, default empty)
- **FR-003**: The entrypoint MUST validate the payload by invoking `validate_input.py` with the JSON payload string; `validate_input.py` MUST be updated to accept the payload (replacing its current raw-argument interface) and return a descriptive error if any field violates defined constraints
- **FR-004**: The orchestrator MUST read `topic`, `hints`, and `snippets` exclusively from the canonical payload — not by re-parsing the raw argument string
- **FR-005**: Helper scripts that currently receive topic or hints as separate positional arguments MUST be updated to accept the canonical payload as a single JSON-serialized string argument; scripts that do not consume topic or hints are out of scope for this migration
- **FR-006**: The entrypoint MUST be the only place where raw argument parsing occurs; no other skill file or script may parse the raw invocation string
- **FR-007**: The presence of one or more non-empty values in `payload.snippets` MUST trigger test/manual mode; absence or all-empty snippets MUST trigger autonomous discovery mode
- **FR-008**: The payload contract (field names, types, constraints) MUST be documented in a new file under `.claude/skills/daily-digest/resources/` that both the skill file and all affected scripts reference

### Key Entities

- **Invocation Payload**: The canonical structured object produced by the entrypoint; contains `topic`, `hints`, and `snippets`; is the single source of truth for invocation data throughout a skill run
- **Entrypoint**: The input-handling section of the skill that parses the raw argument string and produces the payload; also performs all validation before handing off to the orchestrator
- **Orchestrator**: The skill's main execution logic; consumes the payload but never re-parses raw input
- **Helper Script**: Any Python utility script called during skill execution that previously accepted topic or hints as separate positional arguments

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of orchestrator steps that currently reference raw argument variables reference payload fields instead after this change
- **SC-002**: 100% of helper scripts that currently accept topic or hints as separate positional arguments are migrated to accept the canonical payload; scripts with no topic/hints dependency are unchanged
- **SC-003**: All three invocation modes (topic only, topic + hints, topic + snippets) produce a correct payload and route to the expected execution path with no additional argument parsing downstream
- **SC-004**: Any invalid invocation (missing topic, constraint violation) is caught at the entrypoint and returns an error before any downstream step executes, in 100% of invalid-input test cases
- **SC-005**: A developer can determine the complete invocation contract by reading a single reference document without consulting multiple skill files or scripts

## Assumptions

- The existing argument syntax (`<topic> [--hints <h1,h2>] ["snippet1" "snippet2"]`) is preserved as-is; only the internal parsing and propagation mechanism changes
- Helper scripts currently accept topic and hints as separate positional arguments (based on `validate_input.py "$TOPIC" "$HINTS"` pattern in daily-digest.md)
- Backward compatibility for users typing the same commands is required; only the internal structure changes

## Clarifications

### Session 2026-03-21

- Q: How is the canonical payload passed from the orchestrator to Python helper scripts? → A: As a single JSON-serialized string argument on the command line
- Q: Which helper scripts are in scope for migration to the canonical payload? → A: Only scripts that currently accept topic or hints as separate arguments
- Q: Where should the payload contract reference document live? → A: New file under `.claude/skills/daily-digest/resources/`
- Q: What happens to `validate_input.py` after migration? → A: Repurposed — updated to accept the JSON payload and validate its fields, replacing the raw-args version
