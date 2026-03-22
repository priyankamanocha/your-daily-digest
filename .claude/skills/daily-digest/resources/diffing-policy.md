# Diffing Policy

Rules governing digest-to-digest comparison for the daily-digest skill.

## Staleness Window

| Parameter | Value | Description |
|---|---|---|
| `staleness_window_days` | 7 | Maximum age (inclusive) of a previous digest eligible as a comparison baseline. A digest dated exactly 7 days ago is still in-window; one dated 8+ days ago is ignored. |

## Repeat Detection Threshold

| Parameter | Value | Description |
|---|---|---|
| `jaccard_threshold` | 0.5 | Minimum Jaccard similarity between title token sets to classify an item as a repeat. Both source match AND Jaccard ≥ 0.5 must hold. |

## Stopwords

Excluded from title token comparison before Jaccard is computed. Lowercase, strip punctuation, then remove these tokens:

```
the, a, an, is, are, was, were, in, on, at, of, and, or, but, to, for,
with, it, its, this, that, by, from
```

## Section Comparison Rules

All four digest sections are compared independently. An item is only suppressed if it matches a prior item in the **same section** (no cross-section suppression).

| Section | Title extraction pattern |
|---|---|
| Key Insights | `### ` heading text |
| Anti-patterns | `**Name**:` bold prefix at bullet start |
| Actions to Try | `### ` heading text |
| Resources | `**Title**:` bold prefix at bullet start |

## Fallback Behaviour

| Condition | Result |
|---|---|
| No previous digest found for topic | All items pass through; no footer note |
| Previous digest older than staleness window | All items pass through; no footer note |
| Previous digest file unreadable or malformed | All items pass through; no footer note |
| Script exits with code 1 | Treat as no baseline; all items pass through |
