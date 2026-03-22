# Research: Topic Watchlists

**Branch**: `006-topic-watchlists` | **Date**: 2026-03-22

## Decision Log

### 1. Watchlist config file format

**Decision**: JSON file (`.watchlist.json`) in project root

**Rationale**: JSON is human-readable, trivially parseable with Python stdlib `json` module, and supports structured entries (name, optional label, last-digest-path). Plain text (one topic per line) would be simpler but can't carry per-topic metadata (display label, last digest reference) without a custom format. TOML/YAML require third-party packages (prohibited by Principle V). JSON hits the sweet spot of structure + stdlib.

**Alternatives considered**:
- Plain text (one topic per line) — rejected: no room for per-topic metadata without inventing a custom format
- Python pickle / shelve — rejected: binary, non-human-readable, brittle across Python versions
- SQLite — rejected: overkill for a personal list of ~20 topics; no querying benefit

---

### 2. Freshness check mechanism

**Decision**: Filesystem scan using the existing `digest-{YYYY-MM-DD}-{topic-slug}.md` pattern produced by `build_path.py`

**Rationale**: `build_path.py` already generates `digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md`. The watchlist skill can derive the expected path for today's date using the same slug logic (`topic.lower().replace(" ", "-")` then strip non-alphanumeric/hyphen) and check for file existence — zero additional state, no index file.

**Slug derivation rule** (mirrors `build_path.py`):
```
slug = re.sub(r"[^a-z0-9-]", "", topic.lower().replace(" ", "-"))[:50]
expected_path = f"digests/{YYYY}/{MM}/digest-{YYYY-MM-DD}-{slug}.md"
```

**Alternatives considered**:
- Separate index file mapping topic → last digest path — rejected: extra state to keep in sync; filesystem is the source of truth
- Storing last-digest path in `.watchlist.json` — rejected: same sync problem; stale if user manually moves/renames files

---

### 3. How `/watchlist refresh` invokes `daily-digest`

**Decision**: The watchlist skill's `## Outline` iterates each topic and invokes the `daily-digest` skill via the Agent tool for each, passing `topic` as the argument.

**Rationale**: Skills in this project are invoked via the Agent tool (Claude spawning a sub-agent with a skill file). The `daily-digest` skill already handles all discovery, scoring, and writing. The watchlist is a pure orchestrator — it should not re-implement any digest logic. Calling the skill by path is the correct composition pattern per Principle I and II.

**Alternatives considered**:
- Inlining the digest logic in `watchlist.md` — rejected: violates Principle II (no duplication of business logic), creates maintenance divergence
- Calling `build_path.py` + `write_digest.py` directly — rejected: bypasses the discovery and quality pipeline entirely

---

### 4. Subcommand dispatch

**Decision**: String prefix matching on `$ARGUMENTS` within the skill `## Outline`

**Rationale**: The watchlist skill receives raw text in `$ARGUMENTS`. The Outline reads the first token to determine the subcommand (`refresh`, `add`, `remove`, `list`) and routes accordingly. This is the same pattern the existing skill uses for `--hints` flag detection. No external parser script needed — the dispatch is trivial (4 cases) and is business logic that belongs in the skill file per Principle II.

**Alternatives considered**:
- Separate skill file per subcommand — rejected: overkill for 4 simple subcommands; increases file count without benefit
- Python argparse script for dispatch — rejected: dispatch is 4-case routing, not complex enough to warrant a script; scripts are for I/O only

---

### 5. Gitignore strategy

**Decision**: Add `.watchlist.json` to the project `.gitignore` as part of the implementation task

**Rationale**: The watchlist is a personal preference (clarification Q4). Adding to `.gitignore` at implementation time is the standard pattern. Users who want to share it can remove the ignore rule manually.

**Alternatives considered**:
- Creating a separate `.watchlist.gitignore` — rejected: non-standard, adds friction
- Not adding to `.gitignore` at all — rejected: contradicts FR-009 and clarification Q4

---

### 6. Sequential vs parallel topic processing during refresh

**Decision**: Sequential processing (one topic at a time)

**Rationale**: Each `daily-digest` invocation spawns 3 parallel discovery agents internally. Running multiple watchlist topics in parallel would launch up to N×3 agents simultaneously, risking rate limiting on `WebSearch`/`WebFetch`. Sequential processing keeps resource usage predictable. This is documented as a future enhancement in the spec's Assumptions.

**Alternatives considered**:
- Parallel refresh (all topics simultaneously) — deferred to future: valid enhancement once rate-limit behaviour is characterised
