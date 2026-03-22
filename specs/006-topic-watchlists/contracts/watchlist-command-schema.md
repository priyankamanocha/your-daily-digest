# Contract: `/watchlist` Skill Command Schema

**Branch**: `006-topic-watchlists` | **Date**: 2026-03-22

This document defines the invocation contract for the `/watchlist` skill — the accepted subcommands, argument shapes, and expected outputs.

---

## Invocation Format

```
/watchlist <subcommand> [<argument>]
```

`$ARGUMENTS` is a single string received by the skill. The first whitespace-delimited token is the subcommand. Remaining tokens are the argument.

---

## Subcommands

### `refresh`

Generates a fresh digest for every topic in the watchlist.

**Syntax**: `/watchlist refresh`

**Arguments**: none

**Behaviour**:
1. If watchlist is empty or absent: display notice and exit cleanly.
   ```
   Your watchlist is empty. Add topics with: /watchlist add <topic>
   ```
2. For each topic in order:
   - If a digest for today already exists (`digest-{today}-{slug}.md`): skip and mark `SKIPPED`.
   - Otherwise: invoke `daily-digest` skill for the topic and mark `REFRESHED` or `FAILED`.
3. After all topics are processed, display a run summary (see Run Summary below).

**Output — Run Summary**:
```
Watchlist refresh complete (YYYY-MM-DD)

✓ Refreshed:  ai-agents      → digests/2026/03/digest-2026-03-22-ai-agents.md
⟳ Skipped:    openai         (already fresh today)
✗ Failed:     claude-code    → No content discovered
```

---

### `add`

Adds a topic to the watchlist.

**Syntax**: `/watchlist add <topic>`

**Arguments**: `<topic>` — required; the topic name (same format accepted by `/daily-digest`)

**Behaviour**:
- If topic is absent: add to watchlist and confirm.
  ```
  Added "ai-agents" to your watchlist (3 topics total).
  ```
- If topic already exists (case-insensitive match): display notice, no change.
  ```
  "ai-agents" is already in your watchlist.
  ```
- If no argument provided: display usage error.
  ```
  Usage: /watchlist add <topic>
  ```

---

### `remove`

Removes a topic from the watchlist.

**Syntax**: `/watchlist remove <topic>`

**Arguments**: `<topic>` — required; the topic name to remove

**Behaviour**:
- If topic exists: remove and confirm.
  ```
  Removed "ai-agents" from your watchlist (2 topics remaining).
  ```
- If topic not found (case-insensitive match): display notice, no change.
  ```
  "ai-agents" was not found in your watchlist.
  ```
- If no argument provided: display usage error.
  ```
  Usage: /watchlist remove <topic>
  ```

---

### `list`

Displays all topics in the watchlist.

**Syntax**: `/watchlist list`

**Arguments**: none

**Behaviour**:
- If watchlist has topics: display table.
  ```
  Your watchlist (3 topics):

  Topic         Label          Last digest
  -----------   ------------   ---------------------
  ai-agents     AI Agents      2026-03-22 (today)
  openai        openai         2026-03-20
  claude-code   Claude Code    (never)
  ```
- If watchlist is empty or absent:
  ```
  Your watchlist is empty. Add topics with: /watchlist add <topic>
  ```

---

### `history`

Shows the 3 most recent digests for a specific watchlist topic.

**Syntax**: `/watchlist history <topic>`

**Arguments**: `<topic>` — required; the topic name to look up history for

**Behaviour**:
- If no argument provided: display usage error.
  ```
  Usage: /watchlist history <topic>
  ```
- If digests exist for the topic: display up to 3 most recent, sorted newest first.
  ```
  Digest history for "ai-agents" (last 3):

  1. 2026-03-22 → digests/2026/03/digest-2026-03-22-ai-agents.md
  2. 2026-03-21 → digests/2026/03/digest-2026-03-21-ai-agents.md
  3. 2026-03-19 → digests/2026/03/digest-2026-03-19-ai-agents.md
  ```
- If no digests found for the topic:
  ```
  No digests found for "ai-agents".
  ```

**Note**: `history` scans all `digests/{YYYY}/{MM}/` directories across all dates using the topic's slug pattern. The topic does not need to currently be in the watchlist — any slug match is returned.

---

## Unknown subcommand

If the first token does not match `refresh`, `add`, `remove`, `list`, or `history`:

```
Unknown subcommand: "<token>"

Usage:
  /watchlist refresh           — refresh all topics
  /watchlist add <topic>       — add a topic
  /watchlist remove <topic>    — remove a topic
  /watchlist list              — show all topics
  /watchlist history <topic>   — show recent digest history for a topic
```

---

## Script I/O Contracts

### `read_watchlist.py`

**Input**: no arguments (reads `.watchlist.json` from CWD)

**Output (stdout, JSON)**:
```json
{"ok": true, "topics": [{"name": "ai-agents", "label": "AI Agents", "added_at": "2026-03-22"}, ...]}
```
or on missing file:
```json
{"ok": true, "topics": []}
```
or on parse error:
```json
{"ok": false, "error": "Invalid JSON in .watchlist.json: <detail>"}
```

**Exit code**: 0 always (caller inspects `ok` field).

---

### `write_watchlist.py`

**Input**: `<action> <topic_json>`
- `action`: `"add"` or `"remove"`
- `topic_json`: JSON string `{"name": "...", "label": "...", "added_at": "..."}`

**Output (stdout, JSON)**:
```json
{"ok": true, "action": "added", "total": 3}
{"ok": true, "action": "already_exists", "total": 3}
{"ok": true, "action": "removed", "total": 2}
{"ok": true, "action": "not_found", "total": 2}
{"ok": false, "error": "<reason>"}
```

**Exit code**: 0 on success; 1 on unrecoverable error (e.g., unwritable file).

---

### `find_digest.py`

**Input**: `<topic_name> <date_YYYY-MM-DD>`

**Output (stdout, JSON)**:
```json
{"exists": true, "path": "digests/2026/03/digest-2026-03-22-ai-agents.md"}
{"exists": false, "path": null}
```

**Exit code**: 0 always.
