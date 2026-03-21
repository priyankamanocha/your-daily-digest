# Contract: Feedback System (Phase 2+, Not MVP)

**Status**: Future Feature (Phase 3)
**Version**: 1.0 (Design)
**Date**: 2026-03-21

---

## Overview

This contract describes the feedback system that will be implemented in Phase 3 (after autonomous discovery in Phase 2 is stable).

**MVP (Phase 1) does NOT include**:
- `/rate-digest` command
- Feedback capture
- Persistent state
- Learning/personalization

---

## When Feedback is Added (Phase 3)

### Input Interface: `/rate-digest` Command

Users run after reading a digest:

```bash
/rate-digest
```

System presents interactive prompts:
- Which insights were useful?
- Which insights were NOT useful?
- Rate overall digest quality (1-5 stars)
- Which content sources were most valuable?

---

## Data Schema (Phase 3+)

```yaml
feedback_id: "fb-2026-03-21-001"
digest_run_id: "2026-03-21-claude-code"
topic: "Claude Code"
feedback_timestamp: "2026-03-21T15:45:00Z"

useful_insights:
  - insight_id: "insight-1"
    title: "..."

not_useful_insights:
  - insight_id: "insight-3"
    title: "..."

overall_rating: 4  # 1-5 scale
comments: "..."
```

---

## Learning Algorithm (Phase 3+)

Source weighting formula:
```
weight = (useful_count - not_useful_count) / total_appearances
```

Used to prioritize sources in Phase 2+ autonomous discovery.

---

## Important Note for MVP

**MVP has NO feedback mechanism**. All feedback-related work is deferred to Phase 3, after:
1. Phase 1 (MVP) proves core insight quality works
2. Phase 2 adds autonomous discovery via MCP

This contract is documented here for future reference only.

See `specs/main/research.md` Part B for the complete Phase 3 design.
