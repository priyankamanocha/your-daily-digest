# Quickstart: Source Allowlist / Blocklist

How to control which sources appear in your daily digests.

---

## Setup

Create `sources.json` at the repository root (same folder as `CLAUDE.md`):

```json
{
  "global": {
    "block": ["contentfarm.io"]
  },
  "topics": {
    "AI safety": {
      "allow": ["alignmentforum.org"],
      "block": ["hypesite.ai"]
    }
  }
}
```

That's it. No flags, no restarts — the next `/daily-digest` invocation picks it up automatically.

---

## Block a source

Add it to a `block` list:

```json
{
  "topics": {
    "machine learning": {
      "block": ["noisyblog.com", "@spamaccount"]
    }
  }
}
```

The source is excluded from the digest and marked `blocked` in the manifest.

**Topic name must match exactly** (case-insensitive) what you pass to `/daily-digest`:
```
/daily-digest machine learning
```

---

## Pin a trusted source

Add it to an `allow` list:

```json
{
  "topics": {
    "machine learning": {
      "allow": ["paperswithcode.com", "@karpathy"]
    }
  }
}
```

When the source has fresh content and meets the minimum quality threshold, it is guaranteed to appear in the digest regardless of how other sources rank.

---

## Apply rules to all topics

Use the `global` section:

```json
{
  "global": {
    "block": ["spam-aggregator.com"],
    "allow": ["mylab.org"]
  }
}
```

Global rules apply to every topic. Topic-level rules take precedence over global rules for the same source.

---

## Source entry formats

| Type | Format | Matches |
|------|--------|---------|
| Domain | `"example.com"` | `example.com` and `www.example.com` |
| Subdomain | `"blog.example.com"` | `blog.example.com` only |
| Handle | `"@username"` | that handle on any social platform (case-insensitive) |

No wildcards — entries are exact matches.

---

## If something goes wrong

**Bad JSON** — the skill halts before discovery with an error identifying the problem:
```
Error loading sources.json: invalid JSON at line 7
```
Fix the syntax in `sources.json` and re-run.

**No sources.json** — the skill runs normally with no filtering applied. This is the default state.

---

## Audit trail

Every source in the manifest now includes a `filter_action` field:
- `"blocked"` — excluded by a block rule
- `"boosted"` — guaranteed inclusion via allow rule
- `"unaffected"` — no rule applied

Check `digests/{YYYY}/{MM}/digest-{date}-{slug}.manifest.json` to see which sources were filtered.
