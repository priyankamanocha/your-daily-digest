# Research: Source Manifest Output

**Branch**: `003-source-manifest` | **Date**: 2026-03-21

---

## Decision 1: Manifest Format — JSON vs YAML

**Decision**: JSON

**Rationale**: Python's `json` stdlib module serialises/deserialises without any third-party dependency. JSON is unambiguously machine-readable, diff-friendly in git, and parseable by any tool without a YAML library. YAML's human-readability advantage is marginal for a file primarily read by tools and developers inspecting structured data.

**Alternatives considered**:
- YAML: More readable but requires PyYAML (not stdlib); ruled out by Principle V.
- Markdown table: Human-readable but not machine-parseable; ruled out.

---

## Decision 2: How to Collect Manifest Data Through a Prompt-Based Skill

**Decision**: The orchestrator (`daily-digest.md`) accumulates manifest data in a structured scratch block at each step, then passes the assembled JSON to `write_manifest.py` at Step 9.

**Rationale**: The skill is prompt-driven; there is no in-memory state between steps. Each step already produces structured output (SOURCE: lines from agents, deduplication group descriptions, quality score tables). The skill can format these intermediate outputs as a JSON manifest payload during the synthesis steps and pass it to the write script at the end — consistent with how the digest content itself is assembled and passed to `write_digest.py`.

**Alternatives considered**:
- Append to a temp file at each step: Requires multiple Bash calls and temp file management; adds complexity without benefit.
- Combine with `write_digest.py`: Script would need to parse both markdown and JSON; violates single-responsibility and makes the script harder to test.

---

## Decision 3: Manifest Path Derivation

**Decision**: `write_manifest.py` accepts the digest file path and derives the manifest path by replacing `.md` with `.manifest.json`. The orchestrator does not need to call `build_path.py` a second time.

**Rationale**: Coupling the manifest path to the digest path in the script guarantees they always co-locate. If the path derivation logic ever changes, it changes in one place.

**Example**: `digests/2026/03/digest-2026-03-21-claude-code.md` → `digests/2026/03/digest-2026-03-21-claude-code.manifest.json`

---

## Decision 4: New Script vs Extending write_digest.py

**Decision**: New script `write_manifest.py`.

**Rationale**: `write_digest.py` writes a markdown string to a path. `write_manifest.py` serialises a JSON payload and writes it to a derived path. Different inputs, different outputs, different concerns. Combining them would bloat `write_digest.py` and break its single-purpose design.

**Alternatives considered**:
- Extend `write_digest.py` with an optional `--manifest` flag: More complex interface, harder to test independently; ruled out.

---

## Decision 5: Manifest Schema Version Field

**Decision**: Include `schema_version: "1.0"` as the first field in every manifest.

**Rationale**: The manifest schema will evolve as the skill adds features. A version field lets readers detect breaking changes without inspecting content. Starting at `"1.0"` signals a stable, intentional initial schema.

---

## Decision 6: Snippets Mode Handling

**Decision**: In snippets (manual/test) mode, each snippet is recorded as a synthetic source entry with `source_type: "snippet"`, `agent: "manual"`, `credibility_score: null`, `freshness_score: null`. No deduplication groups are generated. `discovery_status` is `"manual"`.

**Rationale**: The manifest must always be complete regardless of mode. Null scores make it obvious the snippet was not credibility-assessed, preventing misinterpretation.

---

## Summary of New Files

| File | Purpose |
|------|---------|
| `.claude/skills/daily-digest/scripts/write_manifest.py` | I/O script: accepts digest path + JSON payload, derives manifest path, writes file |
| `.claude/skills/daily-digest/resources/manifest-schema.md` | Reference: manifest JSON schema documentation for use by the orchestrator |
