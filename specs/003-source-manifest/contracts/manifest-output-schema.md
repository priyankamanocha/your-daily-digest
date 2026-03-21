# Output Contract: Source Manifest

**Output**: Sidecar JSON file written alongside each digest (success case only)

---

## File Path

```
digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{topic-slug}.manifest.json
```

Derived by replacing `.md` with `.manifest.json` in the digest path. Always co-located with its digest.

---

## Script Interface

```bash
python .claude/skills/daily-digest/scripts/write_manifest.py <digest_path> <manifest_json>
```

| Argument | Description |
|----------|-------------|
| `digest_path` | Path to the digest file just written (used to derive manifest path) |
| `manifest_json` | Complete manifest payload as a compact JSON string |

**Exit codes**: `0` = success, `1` = error (message printed to stderr)
**stdout**: `✅ Manifest created: {manifest_path}` on success

---

## When Written

| Condition | Manifest written? |
|-----------|-----------------|
| Digest written successfully | ✅ Yes |
| No digest (all sources failed) | ❌ No |
| No digest (zero credible sources) | ❌ No |
| Snippets mode (digest written) | ✅ Yes (`discovery_status: manual`) |

---

## Top-Level Fields

| Field | Type | Example |
|-------|------|---------|
| `schema_version` | `"1.0"` | `"1.0"` |
| `topic` | string | `"claude-code"` |
| `generated_at` | ISO8601 datetime | `"2026-03-21T14:30:00"` |
| `discovery_status` | `complete\|partial\|timeout\|manual` | `"complete"` |
| `agents_succeeded` | string[] | `["web", "video", "social"]` |
| `agents_failed` | string[] | `[]` |
| `quality_warning` | boolean | `false` |
| `sources` | SourceRecord[] | see data-model.md |
| `deduplication_groups` | DeduplicationGroup[] | see data-model.md |
| `candidates` | CandidateRecord[] | see data-model.md |
| `section_selections` | SectionSelections | see data-model.md |

Full field definitions: [`data-model.md`](../data-model.md)

---

## Format Guarantees

| Aspect | Guarantee |
|--------|-----------|
| Encoding | UTF-8 |
| JSON validity | Always valid JSON (verified by `json.dumps` in write_manifest.py) |
| Indentation | 2-space indent for readability |
| Path coupling | Manifest path always matches digest path (same directory, same stem) |
| Atomicity | Written in a single `write()` call; no partial writes |
