# Data Model: Digest Diffing

**Branch**: `007-digest-diffing` | **Date**: 2026-03-22

## Entities

---

### DiffBaseline

Represents the previous digest used as the comparison baseline for today's run.

| Field | Type | Description |
|---|---|---|
| `found` | bool | Whether a qualifying previous digest exists |
| `baseline_date` | str (YYYY-MM-DD) | Date extracted from the baseline filename |
| `baseline_path` | str | Relative path to the baseline digest file |
| `sections` | DiffBaselineSections | Parsed item titles per section |

**Validation rules**:
- `baseline_date` must be within the staleness window (≤ 7 days before today) for `found = true`
- If the file is malformed or empty, treat as `found = false`
- `baseline_path` must not equal today's digest path (exclude same-day files)

**Lifecycle**: Created at Step 3.5 (diff lookup), consumed at Step 8 (item filtering), and referenced in the Step 9 footer note. Not persisted — lives only for the duration of the skill run.

---

### DiffBaselineSections

The parsed item titles from each of the four digest sections in the baseline.

| Field | Type | Description |
|---|---|---|
| `key_insights` | list[str] | Titles of Key Insights in the baseline |
| `anti_patterns` | list[str] | Names of Anti-patterns in the baseline |
| `actions` | list[str] | Titles of Actions to Try in the baseline |
| `resources` | list[str] | Titles of Resources in the baseline |

**Extraction rules** (per `research.md` Decision 3):

| Section | Pattern |
|---|---|
| Key Insights | `### (.+)` headings under the `## Key Insights` block |
| Anti-patterns | `\*\*(.+?)\*\*:` at bullet line start under `## Anti-patterns` |
| Actions to Try | `### (.+)` headings under `## Actions to Try` |
| Resources | `\*\*(.+?)\*\*:` at bullet line start under `## Resources` |

---

### InsightFingerprint

Computed in-memory for each candidate item during Step 8 comparison. Not a stored entity.

| Field | Type | Description |
|---|---|---|
| `title` | str | The item's title as selected after quality rubric |
| `title_tokens` | set[str] | Lowercased, punctuation-stripped, stopword-removed tokens from `title` |
| `section` | str | One of: `key_insights`, `anti_patterns`, `actions`, `resources` |

**Repeat condition**: An item is a repeat if there exists a baseline item in the same section where:
1. **Source matches**: The source attribution of the candidate matches the source of the baseline item (case-insensitive, trimmed).
2. **Jaccard ≥ 0.5**: `|intersection(tokens_A, tokens_B)| / |union(tokens_A, tokens_B)| ≥ 0.5` on the title token sets.

Both conditions must hold. Source-only or title-only match is not sufficient.

---

### DiffResult

Aggregates the outcome of the repeat-detection pass for all four sections.

| Field | Type | Description |
|---|---|---|
| `baseline_date` | str (YYYY-MM-DD) | Date of the baseline digest used |
| `suppressed_count` | int | Total number of items suppressed across all sections |
| `suppressed_by_section` | dict[str, list[str]] | Titles suppressed per section key |
| `passed_by_section` | dict[str, list[Any]] | Selected items that passed (new material) per section |

**Usage**:
- `suppressed_count == 0` → no footer note appended
- `suppressed_count > 0` → footer note: `"N items suppressed as already covered in digest from YYYY-MM-DD"`
- If `passed_by_section[section]` length falls below section minimum → apply low-signal warning per quality policy

---

### DiffPolicy

Configuration constants governing the diffing behaviour. Defined in `resources/diffing-policy.md`, read by `diff_digest.py` and referenced in the skill outline.

| Field | Value | Description |
|---|---|---|
| `staleness_window_days` | 7 | Maximum age of a previous digest eligible for comparison |
| `jaccard_threshold` | 0.5 | Minimum Jaccard similarity to classify a title as a match |
| `stopwords` | (list) | Common English tokens excluded from Jaccard comparison |

---

## State Transitions

```
Skill invocation
      │
      ▼
Step 3.5: Diff Lookup
      ├── No qualifying baseline → DiffBaseline{found: false}
      │         │
      │         ▼
      │   Step 8: All candidates pass through → DiffResult{suppressed_count: 0}
      │
      └── Baseline found → DiffBaseline{found: true, sections: {...}}
                │
                ▼
          Step 8: Per-item Jaccard check
                ├── Item is repeat → suppressed
                └── Item is new   → passed
                │
                ▼
          DiffResult assembled
                │
                ├── suppressed_count == 0 → no footer note
                └── suppressed_count > 0  → footer note appended at Step 9
```

## Invocation Contract Extension

The `--no-diff` flag is added to the existing invocation payload:

| Field | Type | Default | Description |
|---|---|---|---|
| `no_diff` | bool | `false` | When `true`, skip Step 3.5 entirely; all candidates pass through |

Parsed at Step 0 alongside `--hints`. Presence of `--no-diff` in `$ARGUMENTS` sets `no_diff = true`.
