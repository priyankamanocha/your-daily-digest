---
name: daily-digest
description: Generate a Daily Intelligence Digest by autonomously discovering, scoring, and synthesising insights on any topic from web, video, and social sources.
---

TRIGGER when the user:
- Says "research <topic>", "deep dive <topic>", or "investigate <topic>"
- Says "what's new in X", "what's happening with X", or "latest on X"
- Asks for a "briefing", "roundup", "digest", or "summary" on a topic
- Says "catch me up on X" or "summarize latest X"
- Explicitly invokes "daily digest" or "generate digest"

DO NOT TRIGGER when:
- The user asks about a specific file, codebase, or local code (use Explore agent instead)
- The user asks a factual question answerable from training data without web search
- The user wants to summarize a specific document or snippet they have already provided

## User Input

```text
$ARGUMENTS
```

Arguments format: `<topic> [--hints <hint1,hint2>] [--since <value>] [--no-diff] ["snippet1" "snippet2" ...]`

- **topic** — required; the subject to research (max 100 chars, alphanumeric / hyphens / underscores / spaces)
- **--hints** — optional; comma-separated YouTube channels or @handles to prioritise (max 10, each ≤50 chars)
- **--since** — optional; number of days or date expression to limit discovery (default: `1` = last 24 hours). Examples: `7`, `yesterday`, `last month`, `feb 2026`
- **--no-diff** — optional flag; skips digest diffing and returns all discovered items unfiltered
- **snippets** — optional quoted strings for manual/test mode only; when present, discovery is skipped

`$ARGUMENTS` is parsed into a canonical payload at Step 0. All subsequent steps read exclusively from that payload. See `.claude/skills/daily-digest/resources/invocation-contract.md` for the full schema and constraints.

---

## Outline

### 0. Parse Invocation (Entrypoint)

Parse `$ARGUMENTS` into the canonical invocation payload:

1. If `--since <value>` is present, extract the value → `since_raw`. Remove the `--since` flag and its value from the argument string. If absent, `since_raw = "1"`.
2. If `--hints <value>` is present, extract the comma-separated value and split into a list → `hints`. Remove the `--hints` flag and its value from the argument string. If absent, `hints = []`.
3. If `--no-diff` is present as a standalone flag, set `no_diff = true` and remove it from the argument string. If absent, `no_diff = false`.
4. Extract any remaining quoted strings → `snippets`. Discard entries that are empty or contain only whitespace. If none remain, `snippets = []`.
5. Treat all remaining non-flag tokens as a single space-joined string → `topic`.
6. Resolve `since_raw` into `since_window` using these rules (today = run date):
   - `since_raw` is empty string → **halt immediately**: `"--since requires a value. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."`
   - `since_raw` is a positive integer string (e.g. `"1"`, `"7"`):
     - Parse N; if N < 1 → **halt**: `"since={N} is not valid — minimum value is 1."`
     - N = 1: `since_window = {start_date: today−1day, end_date: today, label: "last 24 hours"}`
     - N > 1: `since_window = {start_date: today−Ndays, end_date: today, label: "last N days"}`
   - `since_raw = "yesterday"` (case-insensitive): `since_window = {start_date: today−1day, end_date: today−1day, label: "yesterday (YYYY-MM-DD)"}`
   - `since_raw = "last month"` (case-insensitive): `since_window = {start_date: today−30days, end_date: today, label: "last 30 days"}`
   - `since_raw` matches `"<month> <year>"` pattern (e.g. `"feb 2026"`, case-insensitive): `since_window = {start_date: first day of that month, end_date: last day of that month, label: "1 Feb – 28 Feb 2026"}`
   - Any other value → **halt immediately**: `"Could not interpret '--since {since_raw}'. Use a number (days) or a phrase like 'yesterday', 'last month', or 'jan 2026'."`
7. Serialize to compact JSON and store as `PAYLOAD_JSON`:

```
PAYLOAD_JSON = {
  "topic": "<topic>",
  "hints": [<hints>],
  "snippets": [<snippets>],
  "since": "<since_raw>",
  "since_window": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "label": "<label>"},
  "no_diff": <no_diff>
}
```

Example — `/daily-digest "AI agents" --hints "channel1,channel2"` (no `--since`):
```
PAYLOAD_JSON = {"topic": "AI agents", "hints": ["channel1", "channel2"], "snippets": [], "since": "1", "since_window": {"start_date": "2026-03-21", "end_date": "2026-03-22", "label": "last 24 hours"}, "no_diff": false}
```

Example — `/daily-digest "AI agents" --since 7`:
```
PAYLOAD_JSON = {"topic": "AI agents", "hints": [], "snippets": [], "since": "7", "since_window": {"start_date": "2026-03-15", "end_date": "2026-03-22", "label": "last 7 days"}, "no_diff": false}
```

Example — `/daily-digest "AI agents" "Snippet A" "Snippet B"`:
```
PAYLOAD_JSON = {"topic": "AI agents", "hints": [], "snippets": ["Snippet A", "Snippet B"], "since": "1", "since_window": {"start_date": "2026-03-21", "end_date": "2026-03-22", "label": "last 24 hours"}, "no_diff": false}
```

---

### 1. Preflight Checks

```bash
python .claude/skills/daily-digest/scripts/check_runtime.py
```

If exit code is non-zero, stop and report each failed check from the JSON output.

Also verify Claude Code's built-in tools are available before proceeding:
- `WebSearch` — required by all three discovery agents
- `WebFetch` — required by all three discovery agents

These are built into Claude Code and require no MCP configuration. If either is unavailable in the current session, warn the user and suggest using manual/test mode with snippets instead.

---

### 2. Validate Input

```bash
python .claude/skills/daily-digest/scripts/validate_input.py "$PAYLOAD_JSON"
```

Parse the JSON output. If exit code is non-zero, stop immediately and report:

```
Error: {error}
```

Do not proceed to Step 3.

If valid, the output contains `{"valid": true, "topic": ..., "hints": ..., "snippets": ..., "since": ..., "since_window": {...}, "no_diff": ...}`. Use this validated payload for all subsequent steps.

---

### 3. Choose Mode

- `payload.snippets` non-empty → **Snippets mode**: build synthetic source records for each snippet (see Step 4 snippets section), set `manifest_discovery_status = "manual"`, `manifest_agents_succeeded = []`, `manifest_agents_failed = []`, then skip to Step 8
- `payload.snippets` empty → run Steps 4–7 (autonomous discovery)

---

### 1.5. Load Source Filters

```bash
python .claude/skills/daily-digest/scripts/load_source_filters.py
```

| Exit code | Action |
|-----------|--------|
| `0` | Parse stdout JSON → store `FILTER_CONFIG = result.filter_config` |
| `1` | Halt immediately: print `Error: {result.error}` and stop |
| `2` | Set `FILTER_CONFIG = null` and continue (no filtering) |

---

### 3.5. Diff Lookup

If `payload.no_diff == true`, set `diff_baseline = {"found": false}` and proceed to Step 4.

Otherwise:

1. Derive the topic slug from `payload.topic` using the same logic as `build_path.py`:
   - Lowercase the topic
   - Replace spaces with hyphens
   - Strip any character that is not alphanumeric or a hyphen
   - Truncate to 50 characters
   - Store as `<derived_slug>`

2. Run:
   ```bash
   python .claude/skills/daily-digest/scripts/diff_digest.py <derived_slug>
   ```

3. Parse the JSON output into `diff_baseline`.
   - If the script exits with code 1, or the output cannot be parsed, set `diff_baseline = {"found": false}` and continue.
   - If `diff_baseline.found == false` (no qualifying baseline), proceed normally — all items will pass through unfiltered.

---

### 4. Spawn Three Discovery Agents in Parallel

Start all three simultaneously — do not wait for one before launching the next.

- **Web agent**: `.claude/skills/daily-digest/agents/web-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}] --since-start {payload.since_window.start_date}`
- **Video agent**: `.claude/skills/daily-digest/agents/video-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}] --since-start {payload.since_window.start_date}`
- **Social agent**: `.claude/skills/daily-digest/agents/social-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}] --since-start {payload.since_window.start_date}`

Proceed with whatever results are available after 45 seconds.

**Manifest data — autonomous mode**: For each `SOURCE:` line returned by an agent, parse the pipe-separated fields and build a source record per the schema in `.claude/skills/daily-digest/resources/manifest-schema.md`. Set `source_type` and `agent` from the originating agent (`web`, `video`, or `social`). Leave `credibility_score`, `credibility_signal`, and `freshness_score` as `null` — they are filled in Step 6. Accumulate all records as `manifest_sources`.

**Manifest data — snippets mode**: For each snippet in `payload.snippets`, build a synthetic source record:
```json
{
  "url": null, "title": "Snippet {n}", "source_type": "snippet", "agent": "manual",
  "author_or_handle": null, "date": null, "days_old": 0,
  "credibility_score": null, "credibility_signal": null, "freshness_score": null,
  "summary": "<snippet text>"
}
```
Accumulate as `manifest_sources`. Set `manifest_dedup_groups = []`.

---

### 4.5. Apply Source Filters

If `FILTER_CONFIG` is null (no `sources.json`): set `filter_action = "unaffected"` on all records in `manifest_sources` and proceed to Step 5.

Otherwise, resolve each source in `manifest_sources` against the filter config using this 4-tier precedence (first match wins):

**Matching logic**:
- Each entry in an `allow` or `block` array is either a domain (e.g. `"reuters.com"`) or a handle (e.g. `"@handle"`).
- **Domain match**: extract the host from `source.url` (strip `https://`, `http://`, `www.` prefix, stop at first `/`). Match if host equals the entry exactly OR if host equals `www.{entry}` (so `"reuters.com"` matches both `reuters.com` and `www.reuters.com`). Match is case-insensitive.
- **Handle match**: compare the entry (case-insensitive) against `source.author_or_handle`. Match if equal.
- If `source.url` is null and the entry is a domain, skip — cannot match.

**Topic lookup**: match `payload.topic` to a key in `FILTER_CONFIG.topics` using case-insensitive exact string comparison.

**Precedence (apply in order; first match wins)**:

1. Topic-level `block` — if the source matches any entry in `FILTER_CONFIG.topics[payload.topic].block` → `filter_action = "blocked"`
2. Topic-level `allow` — if the source matches any entry in `FILTER_CONFIG.topics[payload.topic].allow` → `filter_action = "boosted"`
3. Global `block` — if the source matches any entry in `FILTER_CONFIG.global.block` → `filter_action = "blocked"`
4. Global `allow` — if the source matches any entry in `FILTER_CONFIG.global.allow` → `filter_action = "boosted"`
5. No match → `filter_action = "unaffected"`

Set `source.filter_action` on every record. Remove all records where `filter_action = "blocked"` from the active candidate pool (they remain in `manifest_sources` for auditability).

---

### 5. Assess Discovery Status

Merge all sources and record:

| Agents succeeded | Discovery status |
|---|---|
| 3/3 | `complete` |
| 1–2 | `partial — {failed_agents} unavailable` |
| 0 | go to step 10 |
| Timeout | `timeout — partial results used` |

**Manifest data**: Store `manifest_discovery_status` (the status string above), `manifest_agents_succeeded` (list of agent names that returned results), and `manifest_agents_failed` (list of agent names that failed or timed out).

---

### 6. Score Source Credibility

Apply scoring rules from `.claude/skills/daily-digest/resources/credibility-rules.md`.

**Manifest data**: For each record in `manifest_sources`, set `credibility_score` (0–3) and `credibility_signal` (the observable trust indicator used). Also apply freshness scoring per `.claude/skills/daily-digest/resources/freshness-policy.md` and set `freshness_score` (0–3, or `null` if date unavailable).

---

### 7. Extract and Deduplicate Candidate Insights

From credible sources only (score ≥ 2), extract 10–20 candidates. For each:

- **Title**: 5–10 words
- **Description**: 2–3 sentences (what / why / how)
- **Evidence**: a direct quote from the source
- **Source**: URL + publication name
- **Freshness**: apply scoring from `.claude/skills/daily-digest/resources/freshness-policy.md`

Then deduplicate: group semantically equivalent candidates, keep the one with the strongest evidence from the most credible source. When credibility scores are equal, prefer the fresher source.

**Manifest data — deduplication groups**: For each semantic group of ≥2 equivalent candidates that were merged, record a deduplication group entry per the schema in `manifest-schema.md` (fields: `group_id`, `candidate_urls`, `winner_url`, `reason`). Accumulate as `manifest_dedup_groups`. If no merges occurred, `manifest_dedup_groups = []`.

**Manifest data — candidates**: For each deduplicated candidate, score it on the four quality rubric dimensions (novelty, evidence, specificity, actionability — each 0–2) and compute `quality_pass` (true if score is 2 on ≥3 dimensions). Record a candidate entry per the schema in `manifest-schema.md`. Accumulate as `manifest_candidates`.

---

### 8. Apply Quality Rubric and Select Final Content

Apply the rubric and counts from `.claude/skills/daily-digest/resources/quality-rubric.md`.

Select final content:
- **Key Insights**: 1–3
- **Anti-patterns**: 2–4 (practices to avoid, evidenced from credible sources)
- **Actions**: 1–3 (concrete experiments derived from insights)
- **Resources**: 3–5 (credible sources first, supplementary sources after)

**Boosted source guarantee** (applied after normal quality scoring, before repeat filter):

For each section, after ranking candidates by quality score:
1. Identify all candidates with `filter_action = "boosted"` that have a date within `payload.since_window` (or within 30 days if no window) and score ≥ 2 on at least 1 quality dimension.
2. For any boosted candidate not already selected: insert it into the section, ordered by quality score descending among boosted entries.
3. If inserting a boosted candidate would exceed the section maximum: drop the lowest-ranking non-boosted candidate to make room.
4. Edge case — all candidates in the section are boosted and total exceeds maximum: cap at the section maximum in boost-insertion order (do not drop any boosted candidates).

**Repeat filter** (applied after boosted guarantee, before count enforcement):

If `diff_baseline.found == true`, filter each section using the rules in `.claude/skills/daily-digest/resources/diffing-policy.md`:

For each selected item, compute its **title token set**: lowercase the title, strip punctuation, remove stopwords listed in diffing-policy.md. Then for each item in the same section of `diff_baseline.sections`:
- Check if the item's **`**Source**:` attribution** (case-insensitive, trimmed) matches the baseline item's source.
- Compute Jaccard similarity: `|intersection(title_tokens_A, title_tokens_B)| / |union(title_tokens_A, title_tokens_B)|`.
- If **both** conditions hold (source matches AND Jaccard ≥ 0.5), classify the item as a repeat and remove it from the section.

After filtering, accumulate:
- `suppressed_count` — total items removed across all four sections (integer, starts at 0)
- `suppressed_baseline_date` — `diff_baseline.baseline_date` (used in the footer note at Step 9)

If `diff_baseline.found == false`, skip the repeat filter entirely: `suppressed_count = 0`.

If any section falls below its minimum after filtering, add the quality warning.

**Manifest data**: As each section's content is finalised, record a `SelectionItem` (`title`, `primary_source_url`) for each selected item. Accumulate as `manifest_section_selections` with keys `key_insights`, `antipatterns`, `actions`, `resources`. Set `manifest_quality_warning = true` if the quality warning was triggered, otherwise `false`.

---

### 9. Build Output Path and Write Digest

```bash
python .claude/skills/daily-digest/scripts/build_path.py "$PAYLOAD_JSON"
```

Assemble the markdown then write:

```bash
python .claude/skills/daily-digest/scripts/write_digest.py "$FILE_PATH" "$CONTENT"
```

**Digest format**: see `.claude/skills/daily-digest/resources/digest-template.md`

The digest header must include the `Sources:` line populated with `payload.since_window.label`. In snippets mode, use `"manual"` for the Sources value.

**Write manifest**: After writing the digest, assemble the manifest payload from all accumulated manifest data:

```json
{
  "schema_version": "1.0",
  "topic": "<payload.topic>",
  "generated_at": "<timestamp matching digest Generated: line>",
  "discovery_status": "<manifest_discovery_status>",
  "agents_succeeded": "<manifest_agents_succeeded>",
  "agents_failed": "<manifest_agents_failed>",
  "quality_warning": "<manifest_quality_warning>",
  "sources": "<manifest_sources>",
  "deduplication_groups": "<manifest_dedup_groups>",
  "candidates": "<manifest_candidates>",
  "section_selections": "<manifest_section_selections>"
}
```

Serialise to compact JSON, then call:

```bash
python .claude/skills/daily-digest/scripts/write_manifest.py "$FILE_PATH" "$MANIFEST_JSON"
```

The schema for all manifest records is in `.claude/skills/daily-digest/resources/manifest-schema.md`.

Return: `Digest created: {file_path}` and `Manifest created: {manifest_path}`

---

### 10. No-Content Fallback

If all agents failed or zero credible sources were found, output:

```
No relevant content discovered for '{payload.topic}' in the {payload.since_window.label}.

Try widening the time window: /daily-digest "{payload.topic}" --since 7
Or provide content manually: /daily-digest "{payload.topic}" "[snippet 1]" "[snippet 2]"
```

Do not write a file. Do not call `write_manifest.py` — no manifest is written in the fallback case.
