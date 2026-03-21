# Research: Post-Write Digest Validator

**Branch**: `004-post-write-validator` | **Date**: 2026-03-21 | **Phase**: 0

## Decision Log

### 1. Delivery Vehicle: Script vs Skill

**Decision**: Python script at `.claude/skills/daily-digest/scripts/validate_digest.py`

**Rationale**: The validator performs deterministic, mechanical file parsing — not AI reasoning. It needs to produce consistent, repeatable results independent of model behaviour. A Python script guarantees determinism and is unit-testable against fixture files. The existing `validate_input.py` script sets the precedent for rule-checking logic in scripts. The user-facing entry point remains the existing `/validate-digest` slash command (a skill), which can call this script.

**Alternatives considered**:
- Pure skill (inline Claude reasoning): rejected — non-deterministic; same digest might pass/fail across runs.
- New top-level skill: rejected — this is a utility sub-component of the daily-digest skill, not a standalone intelligence feature.

---

### 2. Item Counting Conventions

**Decision**: Section items identified by structural marker, not line-by-line content.

| Section | Heading | Item Marker |
|---------|---------|-------------|
| Key Insights | `## Key Insights (1–3)` | `### ` (level-3 sub-heading) |
| Anti-patterns | `## Anti-patterns (2–4)` | `- **` (bold list item) |
| Actions to Try | `## Actions to Try (1–3)` | `### ` (level-3 sub-heading) |
| Resources | `## Resources (3–5)` | `- **` (bold list item) |

**Rationale**: These markers directly mirror the digest template's structure and are unambiguous. Using structural markers (not content heuristics) avoids false positives from body text that happens to start with `###`.

**Alternatives considered**:
- Count any `###` heading in the file: rejected — headings appear in the header block too, causing false positives.
- Count lines matching a content pattern: rejected — fragile; template structure is the authoritative source.

---

### 3. Section Heading Matching

**Decision**: Exact string prefix match against the four required headings.

Exact strings (from `digest-template.md`):
- `## Key Insights (1–3)`
- `## Anti-patterns (2–4)`
- `## Actions to Try (1–3)`
- `## Resources (3–5)`

**Rationale**: The digest template defines these as fixed strings. Exact matching is simple and ensures the validator fails loudly if the template changes — a useful early warning of template drift.

**Alternatives considered**:
- Fuzzy/partial match: rejected — would mask template drift and accept malformed headings silently.

---

### 4. Evidence Field Parsing

**Decision**: Regex match `\*\*Evidence\*\*:\s*"[^"]+"` within each Insight block.

**Rationale**: The template's field rules specify `"double quotes"` around the quote text. A regex anchored to the `**Evidence**:` label and requiring non-empty content in double quotes covers both the presence check and the format check in one pass.

**Alternatives considered**:
- Check only for the `**Evidence**:` label (not the quotes): rejected — too lenient; an empty or unquoted value would pass.

---

### 5. Low-Signal Trigger Detection

**Decision**: Parse the `Discovery:` metadata line in the header block. Trigger low-signal check if the value contains `partial` or `timeout` (case-insensitive substring match).

**Rationale**: The template specifies exactly three non-standard `Discovery:` values: `partial — X unavailable` and `timeout — partial results used`. Both contain the trigger words. The `manual` value does not trigger low-signal (manual/test mode is not low-signal by definition).

**Alternatives considered**:
- Check if any count is at minimum: rejected per clarification Q5 — Discovery line is the authoritative signal.

---

### 6. Integration with daily-digest.md

**Decision**: Insert validator call immediately after `write_digest.py` in Step 9 of `daily-digest.md`.

```
python .claude/skills/daily-digest/scripts/validate_digest.py "$FILE_PATH"
```

If exit code is non-zero: stop and display the validation report. The digest file remains on disk (for debugging) but the run is marked failed.

**Rationale**: The validator should run on the freshly written file while the path is already in scope. Stopping on failure preserves the file for inspection — deleting it would remove debugging context.

**Alternatives considered**:
- Run validator before write: rejected — nothing to validate yet.
- Run validator as a separate preflight in Step 1: rejected — validation depends on the written output, not inputs.

---

### 7. Performance Target

**Decision**: Validator MUST complete within 2 seconds for any single digest file.

**Rationale**: A typical digest file is 2–5 KB. Python stdlib file I/O + a single regex scan of the content completes in ~10–50 ms on any modern machine. The 2-second bound is a conservative ceiling that accommodates slow network-mounted file systems or heavily loaded machines. This resolves the "no perceptible delay" language from SC-001.

---

### 8. Report Output Format

**Decision**: Plain-text structured report, human-readable. Written to stdout and to `<digest-filename>.validation.txt` in the same directory.

**Rationale**: Human-readable text is parseable by Claude (for the orchestrator to read) and directly inspectable in a terminal. JSON would require an extra parsing step in the skill; markdown would introduce rendering complexity in a terminal context. The `.validation.txt` extension signals the file is a metadata artefact alongside the digest.

Example report structure:
```
Validation Report: digest-2026-03-21-claude-code.md
Generated: 2026-03-21 14:32:00

CHECKS
------
[PASS] Structure: all 4 required headings present
[FAIL] Count — Key Insights: found 0, expected 1–3
[PASS] Count — Anti-patterns: found 3, expected 2–4
[PASS] Count — Actions to Try: found 2, expected 1–3
[PASS] Count — Resources: found 4, expected 3–5
[FAIL] Evidence — "Insight Title Here": Evidence field missing
[PASS] Formatting: no unclosed code blocks detected
[SKIP] Low-signal warning: Discovery status is 'complete' — check not applicable

SUMMARY
-------
Status: FAIL
Total checks: 7 (run) + 1 (skipped)
Passed: 5  Failed: 2  Skipped: 1
```
