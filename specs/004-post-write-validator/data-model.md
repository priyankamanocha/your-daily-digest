# Data Model: Post-Write Digest Validator

**Branch**: `004-post-write-validator` | **Date**: 2026-03-21

## Entities

### CheckResult

A single validation check outcome.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable check name (e.g., `"Count — Key Insights"`) |
| `status` | enum: `PASS \| FAIL \| SKIP` | Outcome of this check |
| `detail` | string \| None | Specific failure or skip reason; None on PASS |

**Rules**:
- `status = SKIP` when the check is not applicable (e.g., low-signal check when Discovery is `complete`)
- `detail` MUST be populated when `status = FAIL`; SHOULD be populated when `status = SKIP` (reason for skip)
- `detail` MUST name the affected item (insight title, section name, or line number) when applicable

---

### ValidationReport

The aggregate result of a single validator run.

| Field | Type | Description |
|-------|------|-------------|
| `digest_path` | string | Absolute path to the validated digest file |
| `generated_at` | string | ISO-8601 timestamp of the validation run |
| `checks` | list[CheckResult] | Ordered list of all check results |
| `overall_status` | enum: `PASS \| FAIL` | PASS only if zero FAIL results; FAIL otherwise |
| `pass_count` | int | Number of checks with status PASS |
| `fail_count` | int | Number of checks with status FAIL |
| `skip_count` | int | Number of checks with status SKIP |

**Rules**:
- `overall_status = FAIL` if `fail_count > 0`, regardless of skip count
- `overall_status = PASS` if `fail_count = 0` (skipped checks do not count as failures)
- Check order in the report follows the check execution order: Structure → Counts → Evidence → Formatting → Low-signal

---

### DigestSection

An in-memory representation of a parsed section from the digest file. Used internally during validation; not persisted.

| Field | Type | Description |
|-------|------|-------------|
| `heading` | string | Exact heading text matched (e.g., `"## Key Insights (1–3)"`) |
| `item_count` | int | Number of items found using the section's item marker |
| `raw_content` | string | Raw text content of the section (between this heading and the next) |
| `item_texts` | list[string] | Extracted text of each item (title or list entry) |

---

### SectionRule

A configuration record defining the validation rules for one section. Statically defined; not loaded from files.

| Field | Type | Description |
|-------|------|-------------|
| `heading` | string | Exact heading string to match |
| `item_marker` | enum: `heading3 \| bold_list` | How to count items: `heading3` = `### `, `bold_list` = `- **` |
| `min_count` | int | Minimum allowed item count (inclusive) |
| `max_count` | int | Maximum allowed item count (inclusive) |
| `check_evidence` | bool | Whether to validate `**Evidence**: "..."` fields in items |

**Static SectionRules**:

| Section | Marker | Min | Max | Evidence |
|---------|--------|-----|-----|----------|
| `## Key Insights (1–3)` | `heading3` | 1 | 3 | true |
| `## Anti-patterns (2–4)` | `bold_list` | 2 | 4 | false |
| `## Actions to Try (1–3)` | `heading3` | 1 | 3 | false |
| `## Resources (3–5)` | `bold_list` | 3 | 5 | false |

---

## Parsing Strategy

### File Structure

A valid digest file has this top-to-bottom structure:

```
# Daily Digest — {Topic}               ← H1 title (line 1)
                                        ← blank line
Generated: {YYYY-MM-DD HH:MM}          ← metadata field
Discovery: {status}                     ← metadata field
                                        ← blank line
## Key Insights (1–3)                  ← section heading
[insight content]

## Anti-patterns (2–4)                 ← section heading
[anti-pattern content]

## Actions to Try (1–3)               ← section heading
[action content]

## Resources (3–5)                     ← section heading
[resource content]

---                                    ← optional separator
⚠️ Low-signal content ...              ← optional footer
```

### Parsing Order

1. Read entire file as UTF-8 text
2. Extract `Discovery:` line value from header block (first 10 lines)
3. Split file into sections by `## ` headings
4. For each SectionRule, locate the matching section
5. Count items using the section's `item_marker`
6. If `check_evidence = true`, scan each item block for `**Evidence**: "..."`
7. Scan entire file for unclosed fenced code blocks (count ` ``` ` occurrences)
8. If Discovery status triggers low-signal check, look for `⚠️ Low-signal content` footer

### Evidence Pattern

```
\*\*Evidence\*\*:\s*"[^"]+"
```

Matches: `**Evidence**: "some quoted text here"`
Does NOT match: `**Evidence**: unquoted text` or `**Evidence**:` (empty)

### Low-Signal Trigger Pattern

```
Discovery:\s*(partial|timeout)
```

Case-insensitive. Matches: `partial — X unavailable`, `timeout — partial results used`.
Does NOT match: `complete`, `manual`.

---

## Output Files

### Report File

- **Path**: `<digest_dir>/<digest_filename>.validation.txt`
- **Format**: Plain text (UTF-8)
- **Created**: After every validator run (overwritten if already exists)
- **Encoding**: UTF-8, Unix line endings

### Digest File

- **Not modified by the validator** — read-only access only
- Remains on disk even when validation fails (for debugging)
