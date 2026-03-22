<!--
SYNC IMPACT REPORT
==================
Version change:     n/a → 1.0.0 (initial ratification)
Modified principles: none (new document)
Added sections:
  - Core Principles (I–V)
  - Runtime Requirements
  - Development Workflow
  - Governance
Removed sections:    none

Templates reviewed:
  ✅ .specify/templates/plan-template.md — Constitution Check section documents specific gates below
  ✅ .specify/templates/spec-template.md — aligns with quality/evidence requirements; no change needed
  ✅ .specify/templates/tasks-template.md — aligns with simplicity and skill-first principles; no change needed
  ✅ .specify/templates/agent-file-template.md — reviewed; no changes required

Deferred items:      none
-->

# your-daily-digest Constitution

## Core Principles

### I. Skill-First Delivery

All intelligence features MUST be delivered as Claude Code skills located in
`.claude/skills/<skill-name>/`. Each skill lives in its own named subdirectory.

- Skills MUST follow the canonical format: YAML frontmatter (`name:`, `description:`),
  `## User Input` with `$ARGUMENTS`, and `## Outline` execution steps.
- Discovery agents MUST be separate skill files under `agents/`, not inline prompts.
- Python utility scripts MAY exist alongside a skill under `scripts/` for I/O operations only.
- No standalone applications, servers, or external APIs are permitted as delivery vehicles.

**Rationale**: Skills are the unit of deployment in this project. A consistent structure
makes skills discoverable, testable, and composable without tooling.

### II. Prompt-as-Code

Skill files (`.md`) are source code and MUST be treated with the same discipline as code.

- Reference material (rubrics, templates, policies) MUST be extracted to `resources/` files
  and referenced by path — not embedded inline in the skill file.
- Business logic (scoring, selection, routing) MUST live in the skill `## Outline`, not in
  Python scripts. Scripts are thin I/O helpers only (file read/write, path generation,
  input validation).
- Skill files have no build cycle: edit, save, invoke — no compilation step.

**Rationale**: Keeping skills focused on execution flow and externalising reference material
makes skills readable at a glance and reference material independently auditable.

### III. Quality Over Completeness

Output MUST meet the quality rubric before being written to a digest file.

- The four-dimension rubric (Novelty, Evidence, Specificity, Actionability) MUST be applied.
  Include only insights scoring 2 on ≥ 3 dimensions.
- Count ranges MUST be enforced: 1–3 insights, 2–4 anti-patterns, 1–3 actions, 3–5 resources.
- When available content falls below a section's minimum, the quality warning MUST appear.
- Padding is forbidden. Output the best available material; never fill counts with weak content.
- All insights and anti-patterns MUST include a direct quote as evidence. Paraphrasing
  evidence is a FAIL condition.

**Rationale**: A digest that pads weak content destroys user trust faster than a short
digest with a quality warning. The rubric is the contract with the user.

### IV. Graceful Degradation

The system MUST produce a useful result even when discovery partially or fully fails.

- Discovery agents MUST be spawned in parallel; the skill MUST proceed with whatever
  results are available after the timeout (40 seconds).
- Partial agent failure (1–2 of 3 agents) MUST produce a digest with a `partial` discovery
  status, not an error.
- Total agent failure or zero credible sources MUST produce the no-content fallback message
  (not a partial or empty digest file).
- Preflight checks MUST run before discovery; unmet hard dependencies (Python, MCP tools,
  write access) MUST stop execution with a clear, actionable error message.

**Rationale**: Users who invoke the skill must always receive either a digest or a clear
message explaining what to do next. Silent failure or partial output without status is
unacceptable.

### V. Simplicity

Every feature MUST use the minimum complexity required to satisfy its acceptance criteria.

- No package managers, build tools, or external runtime dependencies beyond Python stdlib
  and MCP tools available in the Claude Code environment.
- Python MUST be 3.8+ stdlib only. Third-party packages are not permitted.
- New scripts or agent files MUST NOT be added unless an existing file cannot satisfy the
  need without becoming overloaded.
- YAGNI applies: do not design for hypothetical future requirements.

**Rationale**: The project has no build cycle by design. Adding dependencies reintroduces
the complexity that the skill-first model eliminates. Simplicity is a feature.

## Runtime Requirements

The following dependencies MUST be present for the skill to run. The preflight step in
`daily-digest.md` verifies these before discovery begins.

| Dependency | Requirement | Used By |
|---|---|---|
| Python | ≥ 3.8, stdlib only | All utility scripts |
| `web_search` MCP tool | Must be available in Claude Code session | Web, video, social agents |
| `fetch` MCP tool | Must be available in Claude Code session | Web, video, social agents |
| `digests/` directory | Must be writable (created if absent) | `write_digest.py` |

If `web_search` or `fetch` is unavailable, the skill MUST suggest manual/test mode using
snippets as the fallback.

## Development Workflow

- **Edit**: Modify skill `.md` files or `resources/` reference files directly.
- **Test (autonomous)**: Invoke `/daily-digest <topic>` — requires MCP tools in session.
- **Test (manual/snippets)**: Invoke `/daily-digest <topic> "snippet1" "snippet2"` — no
  MCP tools required; validates the synthesis pipeline independently.
- **Validate**: Run `/validate-digest` to verify output against MVP benchmark.
- **No build step**: Changes take effect immediately on next invocation.

When adding a new skill:
1. Create `.claude/skills/<skill-name>/` directory.
2. Add `<skill-name>.md` with YAML frontmatter, `## User Input`, `## Outline`.
3. Add `scripts/` for I/O helpers and `resources/` for reference material as needed.
4. Update `CLAUDE.md` skill table.

## Governance

This constitution supersedes `CLAUDE.md` and all feature specs in cases of conflict.
`CLAUDE.md` is a runtime development guide derived from the constitution; update it when
the constitution changes.

- Amendments require: (a) documenting the rationale, (b) incrementing the version, and
  (c) propagating changes to affected templates and `CLAUDE.md`.
- Version follows semantic versioning:
  - MAJOR: Principle removed, renamed, or redefined in a backward-incompatible way.
  - MINOR: New principle or section added, or materially expanded guidance.
  - PATCH: Clarification, wording improvement, or typo fix.
- All feature plans MUST include a Constitution Check section listing which principles
  apply and confirming no violations before implementation begins.
- Compliance is verified during plan review (before Phase 0 research) and after design
  (before Phase 1 implementation).

**Constitution Check Gates** (for use in plan-template Constitution Check section):

| Gate | Principle | Pass Condition |
|---|---|---|
| Delivery vehicle | I. Skill-First | Feature delivered as `.claude/skills/<name>/<name>.md` |
| Skill format | I + II | Frontmatter + User Input + Outline present |
| Script scope | II | Scripts perform I/O only; no business logic |
| Reference material | II | Rubrics/templates in `resources/`, not inline |
| Evidence requirement | III | All insights include direct quote |
| Count enforcement | III | Counts within 1–3/2–4/1–3/3–5 ranges |
| Degradation handling | IV | Partial failure returns digest with status, not error |
| Preflight checks | IV | Hard deps verified before discovery starts |
| Dependencies | V | Python stdlib only; no third-party packages |

**Version**: 1.0.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-21
