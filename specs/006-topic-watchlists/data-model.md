# Data Model: Topic Watchlists

**Branch**: `006-topic-watchlists` | **Date**: 2026-03-22

## Entities

### WatchlistConfig

The root object persisted to `.watchlist.json` in the project root.

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | string | yes | Schema version. Currently `"1"`. |
| `topics` | TopicEntry[] | yes | Ordered list of saved topics. May be empty. |

**Constraints**:
- `topics` is ordered by insertion time (append-only for add, filter for remove).
- The file is created on first `add` call if it does not exist.
- If the file is absent, the watchlist is treated as empty (not an error).
- If the file is present but unparseable JSON, the skill reports a clear error and stops.

---

### TopicEntry

A single saved topic in the watchlist.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The topic identifier passed to `daily-digest`. Lowercase, hyphens allowed (e.g., `ai-agents`). |
| `label` | string | no | Optional human-readable display label (e.g., `"AI Agents"`). Defaults to `name` if absent. |
| `added_at` | string (ISO 8601 date) | yes | Date the topic was added, `YYYY-MM-DD`. |

**Constraints**:
- `name` is the identity key — no two entries may share the same `name` (case-insensitive comparison).
- `name` is validated against `[a-z0-9][a-z0-9 \-]*` (same constraints as `daily-digest` topic input).
- Topic names are normalized to lowercase before storage and comparison.

**Identity rule**: Two topics are considered duplicates if `name.lower()` is equal after normalization.

---

### DigestReference (derived, not stored)

Not persisted — derived at runtime by scanning the filesystem.

| Field | Type | Description |
|---|---|---|
| `topic_name` | string | The topic name from the watchlist entry. |
| `date` | string (YYYY-MM-DD) | Date of the digest. |
| `file_path` | string | Absolute or repo-relative path to the digest file. |
| `slug` | string | URL-safe slug derived from topic name using `build_path.py` slug logic. |

**Derivation**:
```
slug = re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:50]
file_path = f"digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md"
```

**Freshness check**: A topic is "fresh today" if the file at `file_path` (using today's date) exists.

**History lookup**: All files matching `digest-*-{slug}.md` across all `digests/{YYYY}/{MM}/` directories, sorted descending by date.

---

## `.watchlist.json` Example

```json
{
  "version": "1",
  "topics": [
    {
      "name": "ai-agents",
      "label": "AI Agents",
      "added_at": "2026-03-22"
    },
    {
      "name": "openai",
      "added_at": "2026-03-22"
    },
    {
      "name": "claude-code",
      "label": "Claude Code",
      "added_at": "2026-03-20"
    }
  ]
}
```

---

## State Transitions

### Topic lifecycle

```
[absent] --add--> [in watchlist] --remove--> [absent]
```

- `add` with existing name → stays `[in watchlist]`, notice displayed, no state change.
- `remove` with unknown name → stays `[absent]`, notice displayed, no state change.

### Refresh run outcomes per topic

```
[in watchlist] --> [skipped: fresh today]   (digest already exists for today)
              --> [refreshed]               (daily-digest succeeded)
              --> [failed: <reason>]         (daily-digest failed or error)
```
