# Quickstart: Topic Watchlists

**Branch**: `006-topic-watchlists` | **Date**: 2026-03-22

## What this feature adds

A `/watchlist` skill that lets you save topics you care about and refresh all their digests with one command.

## Files created by this feature

```
.claude/skills/watchlist/
├── watchlist.md                  # The skill
└── scripts/
    ├── read_watchlist.py         # Reads .watchlist.json
    ├── write_watchlist.py        # Adds/removes topics from .watchlist.json
    └── find_digest.py            # Checks if a digest for a topic exists today

.watchlist.json                   # Created automatically on first /watchlist add
.gitignore                        # Updated to include .watchlist.json
```

## Usage

### Build your watchlist

```
/watchlist add ai-agents
/watchlist add openai
/watchlist add claude-code
```

### See what's in it

```
/watchlist list
```

### Refresh everything at once

```
/watchlist refresh
```

Topics that already have a digest today are skipped automatically. A summary is shown at the end.

### Remove a topic

```
/watchlist remove openai
```

## How freshness detection works

When you run `/watchlist refresh`, for each topic the skill checks whether a file matching `digests/{YYYY}/{MM}/digest-{today}-{topic-slug}.md` already exists. If it does, that topic is skipped. If not, it invokes `/daily-digest <topic>` to generate a fresh one.

## Testing without live search

Use snippets mode to test the refresh pipeline without internet access:

```
/daily-digest "ai-agents" "Snippet about AI agents" "Another snippet"
```

The `/watchlist` management commands (`add`, `remove`, `list`) work regardless — they only read and write `.watchlist.json`.

## Opting in to git-tracking the watchlist

By default `.watchlist.json` is gitignored. To share your watchlist with your team, remove the ignore rule:

```bash
# In .gitignore, delete the line:
.watchlist.json
```

Then commit `.watchlist.json` normally.
