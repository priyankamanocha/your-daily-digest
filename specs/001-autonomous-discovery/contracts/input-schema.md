# Input Contract: Phase 2 Autonomous Discovery Skill

**Endpoint**: `/daily-digest` command (Claude Code skill)

---

## Command Format

```bash
/daily-digest <topic> [--hints <hints>]
```

---

## Parameters

### topic (required)
- **Type**: string
- **Description**: Topic for autonomous discovery
- **Constraints**:
  - Non-empty
  - Max 100 characters
  - Alphanumeric, hyphens, underscores allowed
  - Examples: "claude-code", "subagents", "prompt-engineering"
- **Examples**:
  - `/daily-digest claude-code`
  - `/daily-digest autonomous-agents`
  - `/daily-digest agentic-workflows`

### hints (optional)
- **Type**: comma-separated list of strings
- **Description**: Curated sources to prioritize during discovery
- **Constraints**:
  - Max 10 items total
  - Each item max 50 characters
  - YouTube channel names or X/Twitter usernames
  - If provided, discovery agents will prioritize results from specified sources
- **Format**:
  - YouTube: channel name or @handle (e.g., "Anthropic", "@anthropic")
  - X/Twitter: username (e.g., "@dmarx", "@jackieon2wheels")
- **Examples**:
  - `/daily-digest claude-code --hints Anthropic,@dmarx`
  - `/daily-digest agentic-workflows --hints @anthropic,@karpathy`
  - `/daily-digest subagents --hints Anthropic`

---

## Validation Rules

| Rule | Behavior |
|------|----------|
| Missing topic | ERROR: "topic is required" |
| Empty topic | ERROR: "topic cannot be empty" |
| topic > 100 chars | ERROR: "topic exceeds 100 characters" |
| Invalid topic chars | ERROR: "topic contains invalid characters (use alphanumeric, hyphens, underscores)" |
| hints > 10 items | ERROR: "hints exceeds 10 items" |
| hint item > 50 chars | ERROR: "[hint] exceeds 50 characters" |
| All validation passes | Proceed to Phase 2 autonomous discovery |

---

## Input Processing

1. **Parse command** → Extract topic + hints
2. **Validate topic** → Check format, length, characters
3. **Validate hints** → Check count and individual lengths
4. **Normalize hints** → Remove duplicates, trim whitespace
5. **Pass to orchestrator** → Begin parallel discovery

---

## Examples

### Example 1: Topic only
```bash
/daily-digest claude-code
```
**Parsed Input**:
```json
{
  "topic": "claude-code",
  "hints": null
}
```

### Example 2: Topic + hints
```bash
/daily-digest agentic-workflows --hints Anthropic,@dmarx,@jackieon2wheels
```
**Parsed Input**:
```json
{
  "topic": "agentic-workflows",
  "hints": [
    "Anthropic",
    "@dmarx",
    "@jackieon2wheels"
  ]
}
```

### Example 3: Invalid (error case)
```bash
/daily-digest "very long topic that exceeds one hundred characters and should trigger validation error"
```
**Error**: "topic exceeds 100 characters"

---

## Error Responses

All validation errors return to user with:
- Error message (human-readable)
- Suggestion (how to fix)
- Example of correct usage

Example:
```
Error: topic exceeds 100 characters
Suggestion: Keep topic under 100 characters
Example: /daily-digest claude-code
```
