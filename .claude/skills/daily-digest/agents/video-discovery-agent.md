---
name: video-discovery-agent
description: Discover recent YouTube video content on a topic, extracting key claims from transcripts and descriptions.
---

## User Input

```text
$ARGUMENTS
```

Arguments: `<topic> [--hints <channel1,channel2>]`

---

## Outline

### 1. Build Search Queries

Generate 2–3 YouTube search queries for the topic:
- Direct topic search
- Tutorial or walkthrough angle
- Recent or news angle (append "2025" or "2026" to surface fresh content)

If hint channels were provided, prefix queries with `site:youtube.com/{channel}` or search those channels directly.

### 2. Search YouTube

Run each query with `WebSearch`. Collect the top 3 video results per query (up to 10 URLs total).

### 3. Fetch and Extract

For each video URL, use `WebFetch` to retrieve the page. Extract:
- **title** — video title
- **url** — YouTube URL
- **channel** — channel name
- **date** — upload date (ISO 8601 where possible)
- **verified** — `verified` if the channel has a verified badge, otherwise `unverified`
- **summary** — 2–3 sentences drawn from transcript snippets, description, or chapter titles covering what is most relevant to the topic

Skip videos with no transcript, description, or retrievable content.

### 4. Return Sources

Output each source on its own line in this exact format:

```
SOURCE: <title> | <url> | <channel> | <date> | <verified/unverified> | <summary>
```

Return up to 10 sources. If fewer than 2 are found, include a note:

```
VIDEO_STATUS: low-signal — only {n} sources found
```

Otherwise:

```
VIDEO_STATUS: ok — {n} sources returned
```
