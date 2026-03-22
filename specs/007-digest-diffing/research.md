# Research: Digest Diffing

**Branch**: `007-digest-diffing` | **Date**: 2026-03-22

## Decision Log

---

### Decision 1: Similarity Algorithm

**Decision**: Jaccard word-set overlap (≥ 50% shared non-stopword tokens) for title comparison.

**Rationale**: The spec defines "same source + ≥50% title word overlap" as the repeat criterion. Jaccard is the natural stdlib implementation: `intersection(set_a, set_b) / union(set_a, set_b)`. It is interpretable, deterministic, and requires no dependencies. Python's `difflib.SequenceMatcher` is sequence-order-sensitive (good for prose, bad for shuffled titles) and harder to tune to a percentage threshold. Jaccard on lowercased, punctuation-stripped tokens maps directly to "shared words."

**Alternatives considered**:
- `difflib.SequenceMatcher`: Order-sensitive, harder to map to "50% word overlap" intuitively. Rejected.
- Edit distance (Levenshtein): Char-level, not word-level; stopword noise. Rejected.
- Embedding-based similarity: Requires third-party packages. Rejected (constitution Principle V).

**Stopword handling**: Strip common English stopwords (the, a, an, is, are, was, were, in, on, at, of, and, or, but, to, for, with) before computing overlap. This prevents stopword-heavy titles from inflating similarity artificially.

---

### Decision 2: Previous Digest Lookup Strategy

**Decision**: Scan `digests/` recursively for files matching `digest-*-{slug}.md`, sort by embedded date descending, skip today's date, take the first result within the 7-day staleness window.

**Rationale**: The slug is deterministic from `build_path.py`: `re.sub(r"[^a-z0-9-]", "", topic.lower().replace(" ", "-"))[:50]`. The same slug derivation in `diff_digest.py` produces an exact match to any prior file for the same topic. Directory scan with `os.walk` (stdlib) is straightforward and handles the `digests/{YYYY}/{MM}/` hierarchy naturally.

**Alternatives considered**:
- Manifest-based lookup (read manifest JSON for topic metadata): More robust but adds a dependency on manifest file existing. Previous digests may predate the manifest feature. Rejected in favour of filename-based approach.
- Index file: YAGNI — a single glob over the digests directory is fast enough for local file counts. Rejected.

---

### Decision 3: Markdown Section Parsing

**Decision**: Split the previous digest on `## ` heading boundaries. Extract section names and their content blocks. Compare per-section items by parsing the template-defined structure (bold titles for insights/actions, bullet-starting bold names for anti-patterns/resources).

**Rationale**: The digest template format is stable and owned by this project. A simple `re.split(r'\n## ', content)` gives reliable section blocks without a full markdown parser. Per-section item extraction uses lightweight regex on the known patterns from `digest-template.md`.

**Section-to-pattern mapping**:

| Section header | Item title extraction |
|---|---|
| `Key Insights` | `### (.+)` headings |
| `Anti-patterns` | `\*\*(.+?)\*\*:` at line start |
| `Actions to Try` | `### (.+)` headings |
| `Resources` | `\*\*(.+?)\*\*:` at line start |

**Alternatives considered**:
- Full markdown parser (e.g., `markdown` package): Third-party, violates Principle V. Rejected.
- Line-by-line state machine: More fragile, harder to maintain. Rejected in favour of regex on known patterns.

---

### Decision 4: Invocation Opt-Out Mechanism

**Decision**: `--no-diff` flag added to `$ARGUMENTS` parsing in Step 0 of the skill. When present, sets `diff_enabled = false` and the diff step is skipped entirely.

**Rationale**: Consistent with the existing `--hints` flag pattern in the invocation contract. Parsed at Step 0 alongside other flags, requiring minimal change to the skill outline.

**Alternatives considered**:
- Environment variable or settings file: More complex; skill-level flags are the established pattern. Rejected.
- Separate opt-in flag (default off): Defeats the purpose — diffing should be on by default so users get the benefit without remembering to add a flag. Rejected.

---

### Decision 5: Insertion Point in Skill Outline

**Decision**: New **Step 3.5** added between Step 3 (Choose Mode) and Step 4 (Spawn Agents). In snippets mode and autonomous mode, the previous digest is located and parsed before discovery begins, so that the diff result is available when candidates are selected in Step 8.

**Rationale**: Running the lookup before discovery is cheap (one file read) and means the diff result is ready at selection time. An alternative of running it after Step 8 would work functionally but is less clean — the diff check would need to be woven into Step 8's selection logic rather than being a discrete step.

**Step 8 modification**: After quality rubric selection, apply `diff_result` filter: remove any selected item whose title matches a previous item (same section). Reduces final counts; if a section falls below minimum, apply low-signal warning per existing policy.

**Step 9 modification**: Append footer note if `diff_result.suppressed_count > 0`: `"N items suppressed as already covered in digest from YYYY-MM-DD"`.

---

### Decision 6: Script Scope

**Decision**: `diff_digest.py` is a pure I/O + data-extraction script. It accepts a topic slug and returns a JSON payload listing prior items per section. The business logic (which items are repeats) stays in the skill `## Outline` (Step 8), consistent with Principle II.

**`diff_digest.py` interface**:
```
python diff_digest.py <topic_slug> [--window-days 7]
```
Output (stdout, JSON):
```json
{
  "found": true,
  "baseline_date": "2026-03-21",
  "baseline_path": "digests/2026/03/digest-2026-03-21-claude-cowork.md",
  "sections": {
    "key_insights": ["Title A", "Title B"],
    "anti_patterns": ["Pattern X"],
    "actions": ["Action 1"],
    "resources": ["Resource Name 1"]
  }
}
```
When no qualifying baseline exists: `{"found": false}`.

The skill outline performs Jaccard comparison using the returned titles.
