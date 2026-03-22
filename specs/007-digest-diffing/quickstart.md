# Quickstart: Digest Diffing

**Branch**: `007-digest-diffing` | **Date**: 2026-03-22

## What This Feature Does

After this feature lands, the daily-digest skill automatically compares today's discovered content against the most recent previous digest for the same topic. Items already covered in the previous run are suppressed. A footer note reports how many items were filtered and from which baseline date.

## Usage

No change to the existing invocation syntax. Diffing is on by default.

```
/daily-digest claude-cowork
```

If today's digest for "claude-cowork" finds insights already in yesterday's digest, those are silently excluded. The footer note at the bottom of the digest will show:

```
3 items suppressed as already covered in digest from 2026-03-21
```

### Opt out (force full run)

```
/daily-digest claude-cowork --no-diff
```

Produces the same output as if the diffing feature did not exist.

## How It Works (High Level)

1. **Baseline lookup** (Step 3.5): `diff_digest.py` searches `digests/` for the most recent file matching the same topic slug. If found and within 7 days, it parses all four sections and returns a list of prior item titles per section.

2. **Repeat detection** (Step 8): For each quality-passing candidate, compute Jaccard similarity between its title tokens and each baseline title in the same section. If Jaccard ≥ 0.5 **and** the source matches, the item is classified as a repeat and excluded.

3. **Footer note** (Step 9): If any items were suppressed, the digest footer notes the count and the baseline date.

## Edge Behaviours

| Scenario | Result |
|---|---|
| No previous digest for topic | All items pass through; no footer note |
| Previous digest > 7 days old | All items pass through; no footer note |
| Previous digest malformed/empty | All items pass through; no footer note |
| All candidates are repeats | Low-signal warning + empty sections; footer note with count |
| `--no-diff` flag present | Diffing skipped; output identical to pre-feature behaviour |

## Files Changed

| File | Change |
|---|---|
| `.claude/skills/daily-digest/daily-digest.md` | Add Step 3.5 (diff lookup), modify Step 8 (filter repeats), modify Step 9 (footer note) |
| `.claude/skills/daily-digest/scripts/diff_digest.py` | New script: topic slug → baseline lookup + section parse → JSON |
| `.claude/skills/daily-digest/resources/diffing-policy.md` | New resource: staleness window, Jaccard threshold, stopword list |
| `.claude/skills/daily-digest/resources/invocation-contract.md` | Add `--no-diff` flag documentation |
| `.claude/skills/daily-digest/scripts/validate_input.py` | Parse and pass through `--no-diff` flag |

## Testing

**Scenario 1 — Repeat suppression** (manual snippets mode):

```
# First run
/daily-digest test-topic "Anthropic released feature X. Quote: 'we built X for users'"

# Second run (same source + overlapping title expected)
/daily-digest test-topic "Anthropic released feature X. Quote: 'we built X for users'"
```

Expected: Second run's insight is suppressed; footer note shows "1 item suppressed."

**Scenario 2 — First run**:

```
/daily-digest brand-new-topic "Some content"
```

Expected: No filtering, no footer note.

**Scenario 3 — Opt-out**:

```
/daily-digest test-topic --no-diff "Anthropic released feature X. Quote: 'we built X for users'"
```

Expected: Insight is NOT suppressed even if a baseline exists.
