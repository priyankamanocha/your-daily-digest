---
name: daily-digest
description: Generate a Daily Intelligence Digest by autonomously discovering, scoring, and synthesising insights on any topic from web, video, and social sources.
---

## User Input

```text
$ARGUMENTS
```

Arguments format: `<topic> [--hints <hint1,hint2>] ["snippet1" "snippet2" ...]`

- **topic** — required; the subject to research (max 100 chars, alphanumeric / hyphens / underscores / spaces)
- **--hints** — optional; comma-separated YouTube channels or @handles to prioritise (max 10, each ≤50 chars)
- **snippets** — optional quoted strings for manual/test mode only; when present, discovery is skipped

`$ARGUMENTS` is parsed into a canonical payload at Step 0. All subsequent steps read exclusively from that payload. See `.claude/skills/daily-digest/resources/invocation-contract.md` for the full schema and constraints.

---

## Outline

### 0. Parse Invocation (Entrypoint)

Parse `$ARGUMENTS` into the canonical invocation payload:

1. If `--hints <value>` is present, extract the comma-separated value and split into a list → `hints`. Remove the `--hints` flag and its value from the argument string. If absent, `hints = []`.
2. Extract any remaining quoted strings → `snippets`. Discard entries that are empty or contain only whitespace. If none remain, `snippets = []`.
3. Treat all remaining non-flag tokens as a single space-joined string → `topic`.
4. Serialize to compact JSON and store as `PAYLOAD_JSON`:

```
PAYLOAD_JSON = {"topic": "<topic>", "hints": [<hints>], "snippets": [<snippets>]}
```

Example — `/daily-digest "AI agents" --hints "channel1,channel2"`:
```
PAYLOAD_JSON = {"topic": "AI agents", "hints": ["channel1", "channel2"], "snippets": []}
```

Example — `/daily-digest "AI agents" "Snippet A" "Snippet B"`:
```
PAYLOAD_JSON = {"topic": "AI agents", "hints": [], "snippets": ["Snippet A", "Snippet B"]}
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

If valid, the output contains `{"valid": true, "topic": ..., "hints": ..., "snippets": ...}`. Use this validated payload for all subsequent steps.

---

### 3. Choose Mode

- `payload.snippets` non-empty → **Snippets mode**: build synthetic source records for each snippet (see Step 4 snippets section), set `manifest_discovery_status = "manual"`, `manifest_agents_succeeded = []`, `manifest_agents_failed = []`, then skip to Step 8
- `payload.snippets` empty → run Steps 4–7 (autonomous discovery)

---

### 4. Spawn Three Discovery Agents in Parallel

Start all three simultaneously — do not wait for one before launching the next.

- **Web agent**: `.claude/skills/daily-digest/agents/web-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`
- **Video agent**: `.claude/skills/daily-digest/agents/video-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`
- **Social agent**: `.claude/skills/daily-digest/agents/social-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`

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

If any section falls below its minimum, add the quality warning.

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
No relevant content discovered for '{payload.topic}'.

Try providing content manually (test mode):
/daily-digest "{payload.topic}" "[snippet 1]" "[snippet 2]"
```

Do not write a file. Do not call `write_manifest.py` — no manifest is written in the fallback case.
