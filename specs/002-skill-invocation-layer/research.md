# Research: Skill Invocation Layer

**Feature**: 002-skill-invocation-layer
**Date**: 2026-03-21

## Overview

This feature is an internal refactor of an existing skill. No new external technologies are introduced. Research focuses on design decisions rather than technology evaluation.

## Decision Log

### D-001: Where does argument parsing live?

**Decision**: In the skill Outline prose (Step 0), not in a Python script.

**Rationale**: The your-daily-brief constitution (Principle II) states business logic belongs in the skill Outline; scripts are thin I/O helpers. Argument parsing is an LLM-executable step: Claude reads `$ARGUMENTS`, identifies the topic (first quoted/unquoted token), extracts `--hints` values if present, and collects remaining quoted strings as snippets. No Python required.

**Alternatives considered**:
- New `parse_payload.py` — rejected; adds a file for logic Claude can do inline, violates Principle V
- Absorb into `validate_input.py` — rejected; conflates parsing with validation, reduces independent testability

---

### D-002: Payload transport mechanism

**Decision**: JSON-serialized string passed as a single positional argument to affected scripts.

**Rationale**: Keeps scripts stateless and self-contained. Matches the existing invocation pattern (`python script.py "$ARG"`). No temp file lifecycle to manage. JSON is natively supported by Python stdlib (`json` module).

**Alternatives considered**:
- Temp JSON file — rejected; adds cleanup burden for a within-session ephemeral value
- Environment variable — rejected; less explicit, harder to trace in skill prose
- stdin pipe — rejected; requires shell pipe syntax in Outline, adds complexity for no benefit

---

### D-003: Which scripts are in scope?

**Decision**: `validate_input.py` and `build_path.py` only.

**Rationale**: These are the only two scripts that currently accept topic or hints as separate positional arguments. `check_runtime.py` takes no arguments; `write_digest.py` takes file path and content — neither has a topic/hints dependency.

---

### D-004: `validate_input.py` disposition

**Decision**: Repurposed — updated to accept a JSON payload string, parse it, validate all three fields, and return the validated payload or a structured error.

**Rationale**: Preserves the separation between Outline prose (execution flow) and Python (I/O + validation). The script remains the single authority on field constraints. The Outline delegates validation entirely to the script rather than duplicating constraint logic in prose.

**Alternatives considered**:
- Retire script, validate inline in Outline — rejected; harder to test, harder to read, duplicates constraint definitions across skill versions
- Keep old interface, add new interface — rejected; two interfaces for one purpose violates Principle V

---

### D-005: Zero new files introduced

**Decision**: This feature adds exactly one new file (`resources/invocation-contract.md`) and modifies three existing files (`daily-digest.md`, `validate_input.py`, `build_path.py`).

**Rationale**: Principle V (Simplicity) — new scripts/files only when an existing file cannot satisfy the need without becoming overloaded. No file reaches that threshold here.

---

### D-006: Payload contract document

**Decision**: New file at `.claude/skills/daily-digest/resources/invocation-contract.md`.

**Rationale**: Consistent with the existing `resources/` convention for reference material (credibility-rules.md, freshness-policy.md, quality-rubric.md). Co-locating with the skill makes it directly reachable by a relative path from the skill file and scripts.

---

## Summary: No NEEDS CLARIFICATION items remain

All four clarification questions from `/speckit.clarify` are resolved:
1. Transport: JSON string argument ✅
2. Script scope: validate_input.py + build_path.py only ✅
3. Contract location: `resources/invocation-contract.md` ✅
4. validate_input.py disposition: repurposed, not retired ✅
