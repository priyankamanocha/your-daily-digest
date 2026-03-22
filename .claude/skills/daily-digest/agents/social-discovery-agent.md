---
name: social-discovery-agent
description: Discover quality X/Twitter discussions on a topic, prioritising verified accounts and substantive threads.
---

## User Input

```text
$ARGUMENTS
```

Arguments: `<topic> [--hints <@handle1,@handle2>] --since-start <YYYY-MM-DD>`

---

## Outline

### 1. Build Search Queries

Generate 2–3 X/Twitter search queries:
- Core topic with recent filter
- Topic + "thread" or "lessons learned"
- Topic + prominent practitioner terms (e.g. "tip", "mistake", "pattern")

If hint handles were provided, search those accounts first (e.g. `from:@handle {topic}`).

### 2. Search X/Twitter

Run each query with `WebSearch`. Collect the top results (up to 10 posts or threads total). Prioritise:
1. Verified accounts
2. Accounts with established followings in the relevant field
3. Posts with visible engagement signals (replies, reposts)

### 3. Fetch and Extract

For each post or thread URL, use `WebFetch` to retrieve the content. Extract:
- **title** — first sentence or main claim of the post
- **url** — direct link to the post or thread
- **handle** — @username of the author
- **date** — post date (ISO 8601 where possible)
- **verified** — `verified` if the account has a verified badge, otherwise `unverified`
- **summary** — 2–3 sentences capturing the main claim, insight, or discussion from the post or thread

Skip posts that are purely promotional, spam, or have no substantive content.

After extracting the date: if the post date is known and falls before `--since-start`, skip the post. If no date can be determined, include the source but append `[undated]` to the summary field.

### 4. Return Sources

Output each source on its own line in this exact format:

```
SOURCE: <title> | <url> | <handle> | <date> | <verified/unverified> | <summary>
```

Return up to 10 sources. If fewer than 2 are found, include a note:

```
SOCIAL_STATUS: low-signal — only {n} sources found
```

Otherwise:

```
SOCIAL_STATUS: ok — {n} sources returned
```
