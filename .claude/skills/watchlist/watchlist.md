---
name: watchlist
description: Manage a personal topic watchlist and batch-refresh all saved topics with one command.
---

## User Input

```text
$ARGUMENTS
```

Format: `<subcommand> [<argument>]`

Subcommands:
- `refresh` — generate fresh digests for all watchlist topics
- `add <topic>` — add a topic to your watchlist
- `remove <topic>` — remove a topic from your watchlist
- `list` — show all watchlist topics and their last digest date
- `history <topic>` — show the 3 most recent digests for a topic

---

## Outline

### 0. Parse Arguments

Extract the first whitespace-delimited token from `$ARGUMENTS` → `subcommand` (lowercase).
Everything after the first token → `argument` (trimmed).

If `$ARGUMENTS` is empty or whitespace-only, go to Step 7 (unknown subcommand).

---

### 1. Route Subcommand

| Subcommand | Go to |
|------------|-------|
| `refresh` | Step 2 |
| `add` | Step 3 |
| `remove` | Step 4 |
| `list` | Step 5 |
| `history` | Step 6 |
| anything else | Step 7 |

---

### 2. Refresh — Generate Digests for All Watchlist Topics

**a. Preflight**

Check that the `digests/` directory exists and is writable. If not:
```
Error: digests/ directory is not writable. Please create it or check permissions.
```
Stop.

**b. Load watchlist**

```bash
python .claude/skills/watchlist/scripts/read_watchlist.py
```

Parse JSON output.

- If `ok = false`: print `Error: {error}` and stop.
- If `topics` is empty: print the following and stop:
  ```
  Your watchlist is empty. Add topics with: /watchlist add <topic>
  ```

**c. Process each topic**

For each topic in the `topics` list (in order):

1. Determine today's date as `YYYY-MM-DD`.

2. Run:
   ```bash
   python .claude/skills/watchlist/scripts/find_digest.py "{topic.name}" "{today}"
   ```
   Parse JSON output.

3. If `exists = true`: mark topic as `SKIPPED`.

4. If `exists = false`: invoke the `daily-digest` skill via the Agent tool with the topic name as the argument. Capture the file path from the output (`Digest created: {path}`). Mark as `REFRESHED` with that path, or `FAILED` with the error reason if the skill does not return a digest path.

**d. Print run summary**

After all topics are processed, print one line per topic:

```
✓ Refreshed: {name} → {path}
⟳ Skipped: {name} (already fresh today)
✗ Failed: {name} → {reason}
```

---

### 3. Add — Add a Topic to the Watchlist

Parse `argument` as the topic name. If empty:
```
Usage: /watchlist add <topic>
```
Stop.

Normalize: `argument.lower().strip()`.

Validate: name must match `^[a-z0-9][a-z0-9 \-]*$`. If invalid:
```
Error: topic name may only contain letters, numbers, spaces, and hyphens.
```
Stop.

Build topic JSON: `{"name": "<normalized_name>", "label": "<argument.strip()>", "added_at": "<today YYYY-MM-DD>"}`.

Run:
```bash
python .claude/skills/watchlist/scripts/write_watchlist.py "add" '<topic_json>'
```

Parse JSON output:

- If `action = added`: print `Added "{name}" to your watchlist ({total} topics total).`
- If `action = already_exists`: print `"{name}" is already in your watchlist.`
- If `ok = false`: print `Error: {error}`

---

### 4. Remove — Remove a Topic from the Watchlist

Parse `argument` as the topic name. If empty:
```
Usage: /watchlist remove <topic>
```
Stop.

Run:
```bash
python .claude/skills/watchlist/scripts/write_watchlist.py "remove" '{"name": "<argument.lower().strip()>"}'
```

Parse JSON output:

- If `action = removed`: print `Removed "{name}" from your watchlist ({total} topics remaining).`
- If `action = not_found`: print `"{name}" was not found in your watchlist.`
- If `ok = false`: print `Error: {error}`

---

### 5. List — Show All Watchlist Topics

Run:
```bash
python .claude/skills/watchlist/scripts/read_watchlist.py
```

Parse JSON output.

- If `ok = false`: print `Error: {error}` and stop.
- If `topics` is empty: print `Your watchlist is empty. Add topics with: /watchlist add <topic>` and stop.

For each topic, find its most recent digest:

1. Derive slug: `re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))[:50]`
2. Use Glob tool to find all files matching `digests/*/*/digest-*-{slug}.md` across all year/month directories.
3. Sort results descending by filename (ISO date prefix makes lexicographic = chronological).
4. The first result is the most recent digest — extract its date from the filename (4th hyphen-delimited segment after `digest-`, i.e. `YYYY-MM-DD`).
5. If no files found: last digest = `(never)`.
6. If the date matches today, append ` (today)`.

Print:
```
Your watchlist ({N} topics):

Topic              Label              Last digest
claude-code        claude-code        2026-03-22 (today)
agentic-workflows  agentic-workflows  2026-03-20
llm-evals          LLM Evals          (never)
```

---

### 6. History — Show Recent Digests for a Topic

Parse `argument` as the topic name. If empty:
```
Usage: /watchlist history <topic>
```
Stop.

Derive slug: `re.sub(r"[^a-z0-9-]", "", argument.lower().strip().replace(" ", "-"))[:50]`

Use Glob tool to find all files matching `digests/*/*/digest-*-{slug}.md`.

Sort results descending by filename. Take the first 3.

If none found:
```
No digests found for "{argument}".
```

Otherwise print:
```
Digest history for "{argument}" (last {N}):

1. {YYYY-MM-DD} → {file_path}
2. {YYYY-MM-DD} → {file_path}
3. {YYYY-MM-DD} → {file_path}
```

---

### 7. Unknown Subcommand

If `subcommand` does not match any known value (or `$ARGUMENTS` was empty), print:

```
Unknown subcommand: "{subcommand}"

Usage: /watchlist <subcommand> [<argument>]

Subcommands:
  refresh           Generate fresh digests for all watchlist topics
  add <topic>       Add a topic to your watchlist
  remove <topic>    Remove a topic from your watchlist
  list              Show all watchlist topics and their last digest date
  history <topic>   Show the 3 most recent digests for a topic
```
