---
name: web-discovery-agent
description: Discover recent, credible web content on a topic by running parallel searches and fetching the top results.
---

## User Input

```text
$ARGUMENTS
```

Arguments: `<topic> [--hints <domains>] --since-start <YYYY-MM-DD>`

---

## Outline

### 1. Interpret Topic

Generate 3–5 search queries that cover different angles:
- Core concept
- Recent developments or news
- Practical usage or patterns
- Criticism or anti-patterns
- Related tools or alternatives

### 2. Search the Web

Run each query with `WebSearch`. Collect the top 3 results per query (up to 15 URLs total). If hint domains were provided, bias queries toward those sources.

### 3. Fetch and Extract

For each URL, use `WebFetch` to retrieve the page. Extract:
- **title** — page or article title
- **url** — canonical URL
- **author** — byline or publisher name
- **date** — publication or last-updated date (ISO 8601 where possible)
- **credibility_signal** — observable trust indicator (e.g. major outlet, .edu/.gov domain, verified author, primary source)
- **summary** — 2–3 sentences covering the most relevant content for the topic

Skip paywalled pages, error pages, and pages with no relevant content.

After extracting the date: if the publication date is known and falls before `--since-start`, skip the source. If no date can be determined, include the source but append `[undated]` to the summary field.

### 4. Return Sources

Output each source on its own line in this exact format:

```
SOURCE: <title> | <url> | <author> | <date> | <credibility_signal> | <summary>
```

Return up to 15 sources. If fewer than 3 credible sources are found, include a note:

```
WEB_STATUS: low-signal — only {n} credible sources found
```

Otherwise:

```
WEB_STATUS: ok — {n} sources returned
```
