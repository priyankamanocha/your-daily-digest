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

Also verify MCP tools are available before proceeding:
- `web_search` — required by all three discovery agents
- `fetch` — required by all three discovery agents

If either MCP tool is unavailable, warn the user and stop. Autonomous discovery cannot run without them. Suggest using manual/test mode with snippets instead.

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

- `payload.snippets` non-empty → skip to Step 8 (manual/test mode)
- `payload.snippets` empty → run Steps 4–7 (autonomous discovery)

---

### 4. Spawn Three Discovery Agents in Parallel

Start all three simultaneously — do not wait for one before launching the next.

- **Web agent**: `.claude/skills/daily-digest/agents/web-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`
- **Video agent**: `.claude/skills/daily-digest/agents/video-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`
- **Social agent**: `.claude/skills/daily-digest/agents/social-discovery-agent.md` — pass `{payload.topic} [--hints {payload.hints joined by comma}]`

Proceed with whatever results are available after 45 seconds.

---

### 5. Assess Discovery Status

Merge all sources and record:

| Agents succeeded | Discovery status |
|---|---|
| 3/3 | `complete` |
| 1–2 | `partial — {failed_agents} unavailable` |
| 0 | go to step 10 |
| Timeout | `timeout — partial results used` |

---

### 6. Score Source Credibility

Apply scoring rules from `.claude/skills/daily-digest/resources/credibility-rules.md`.

---

### 7. Extract and Deduplicate Candidate Insights

From credible sources only (score ≥ 2), extract 10–20 candidates. For each:

- **Title**: 5–10 words
- **Description**: 2–3 sentences (what / why / how)
- **Evidence**: a direct quote from the source
- **Source**: URL + publication name
- **Freshness**: apply scoring from `.claude/skills/daily-digest/resources/freshness-policy.md`

Then deduplicate: group semantically equivalent candidates, keep the one with the strongest evidence from the most credible source. When credibility scores are equal, prefer the fresher source.

---

### 8. Apply Quality Rubric and Select Final Content

Apply the rubric and counts from `.claude/skills/daily-digest/resources/quality-rubric.md`.

Select final content:
- **Key Insights**: 1–3
- **Anti-patterns**: 2–4 (practices to avoid, evidenced from credible sources)
- **Actions**: 1–3 (concrete experiments derived from insights)
- **Resources**: 3–5 (credible sources first, supplementary sources after)

If any section falls below its minimum, add the quality warning.

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

Return: `✅ Digest created: {file_path}`

---

### 10. No-Content Fallback

If all agents failed or zero credible sources were found, output:

```
No relevant content discovered for '{payload.topic}'.

Try providing content manually (test mode):
/daily-digest "{payload.topic}" "[snippet 1]" "[snippet 2]"
```

Do not write a file.
