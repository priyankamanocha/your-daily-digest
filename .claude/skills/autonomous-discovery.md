# Autonomous Content Discovery Skill

**Name**: `autonomous-discovery`
**Version**: 2.0.0 (Phase 2)
**Purpose**: Multi-agent autonomous discovery of relevant content from web, video, and social sources
**Input**: `/daily-digest <topic> [--hints <hints>]`
**Output**: Markdown digest file or fallback message
**Status**: Phase 2 Implementation (Foundational + MVP Ready)

---

## 📋 Table of Contents

1. [Configuration & Constants](#configuration--constants)
2. [Data Structures & Types](#data-structures--types)
3. [Input Validation Module](#input-validation-module)
4. [Agent Interface & Orchestrator](#agent-interface--orchestrator)
5. [Processing Pipeline](#processing-pipeline)
6. [Output Generation Module](#output-generation-module)
7. [Error Handling](#error-handling)
8. [Utility Functions](#utility-functions)
9. [Main Entrypoint](#main-entrypoint)

---

## Configuration & Constants

```javascript
/**
 * CONFIGURATION
 * Central place for all tunable parameters and limits
 */

const CONFIG = {
  // Input constraints
  CONSTRAINTS: {
    TOPIC_MAX_LENGTH: 100,
    TOPIC_MIN_LENGTH: 1,
    TOPIC_PATTERN: /^[a-zA-Z0-9\-_ ]+$/,
    HINTS_MAX_COUNT: 10,
    HINTS_MAX_LENGTH: 50,
  },

  // Execution
  TIMEOUT_MS: 45000, // 45-second deadline per spec
  EXECUTION: {
    AGENT_TIMEOUT_MS: 40000, // Reserve 5s for aggregation
    PARALLEL_AGENTS: ['web', 'video', 'social'],
  },

  // Quality thresholds
  QUALITY: {
    MIN_INSIGHTS: 1,
    MAX_INSIGHTS: 3,
    MIN_ANTIPATTERNS: 2,
    MAX_ANTIPATTERNS: 4,
    MIN_ACTIONS: 1,
    MAX_ACTIONS: 3,
    MIN_RESOURCES: 3,
    MAX_RESOURCES: 5,
    RUBRIC_PASS_THRESHOLD: 2, // ≥2 on ≥3 dimensions
    MIN_PASSING_DIMENSIONS: 3,
  },

  // Discovery
  DISCOVERY: {
    CANDIDATE_INSIGHTS_MIN: 20,
    CANDIDATE_INSIGHTS_MAX: 40,
    FRESHNESS_THRESHOLDS: {
      VERY_FRESH: { days: 2, score: 3 },      // <2 days
      FRESH: { days: 7, score: 2 },           // 2-7 days
      MODERATE: { days: 30, score: 1 },       // 8-30 days
      STALE: { days: Infinity, score: 0 },    // >30 days
    },
  },

  // Output paths
  OUTPUT: {
    BASE_DIR: 'digests',
    FILE_PATTERN: 'digest-{YYYY}-{MM}-{DD}-{topic-slug}.md',
  },
};

// Error codes for structured error handling
const ERROR_CODES = {
  TOPIC_MISSING: 'ERR_TOPIC_MISSING',
  TOPIC_EMPTY: 'ERR_TOPIC_EMPTY',
  TOPIC_TOO_LONG: 'ERR_TOPIC_TOO_LONG',
  TOPIC_INVALID_CHARS: 'ERR_TOPIC_INVALID_CHARS',
  HINTS_TOO_MANY: 'ERR_HINTS_TOO_MANY',
  HINT_TOO_LONG: 'ERR_HINT_TOO_LONG',
  DISCOVERY_FAILED: 'ERR_DISCOVERY_FAILED',
  TIMEOUT: 'ERR_TIMEOUT',
  NO_CONTENT: 'ERR_NO_CONTENT',
};
```

---

## Data Structures & Types

```javascript
/**
 * DATA STRUCTURES
 * Core types flowing through the system
 */

/**
 * UserInput: Parsed command-line input
 */
class UserInput {
  constructor(topic, hints = []) {
    this.topic = topic;
    this.hints = hints;
  }

  static fromArgs(args) {
    const topic = args[0];
    const hintsArg = args.includes('--hints')
      ? args[args.indexOf('--hints') + 1]
      : '';
    return new UserInput(topic, hintsArg ? hintsArg.split(',').map(h => h.trim()) : []);
  }
}

/**
 * DiscoveredSource: Raw content from a single discovery source
 * Output by each agent (web, video, social)
 */
class DiscoveredSource {
  constructor(data) {
    this.url = data.url;
    this.title = data.title;
    this.content = data.content; // Raw or parsed text
    this.source_type = data.source_type; // 'web' | 'video' | 'social'
    this.author = data.author; // Publisher/creator/channel
    this.published_date = data.published_date; // ISO8601 or null
    this.days_old = calculateDaysOld(data.published_date);
    this.freshness_score = calculateFreshnessScore(this.days_old);
    this.credibility_signal = data.credibility_signal; // Observable signals
  }
}

/**
 * CandidateInsight: Proposed insight extracted from sources
 * Pre-deduplication; includes all quality scores
 */
class CandidateInsight {
  constructor(data) {
    this.title = data.title; // 5-10 words
    this.description = data.description; // 2-3 sentences: what/why/how
    this.evidence = data.evidence; // Direct quote from source
    this.source_urls = data.source_urls || [];
    this.source_types = data.source_types || []; // ['web', 'video', 'social']
    this.published_date = data.published_date;
    this.days_old = data.days_old || 0;

    // Quality scores (filled by agents and US2 tasks)
    this.credibility_score = data.credibility_score || 0; // 0-3 (US2)
    this.freshness_score = data.freshness_score || 0; // 0-3 (by agent)
    this.specificity_score = data.specificity_score || 0; // 0-3 (US2)
    this.engagement_score = data.engagement_score || 0; // 0-2 (US2)

    // Combined score for ranking
    this.combined_score = this.calculateCombinedScore();
  }

  calculateCombinedScore() {
    return (
      this.credibility_score +
      this.freshness_score +
      this.specificity_score +
      this.engagement_score
    );
  }
}

/**
 * DeduplicatedInsight: Post-deduplication insight
 * One entry per unique insight after merging
 */
class DeduplicatedInsight extends CandidateInsight {
  constructor(data) {
    super(data);
    this.primary_source_url = data.primary_source_url;
    this.contributing_sources = data.contributing_sources || [];
    this.quality_scores = data.quality_scores || {
      novelty: 0,
      evidence: 0,
      specificity: 0,
      actionability: 0,
    };
    this.quality_pass = data.quality_pass || false;
  }
}

/**
 * DiscoveryResult: Aggregated results from all agents
 * Before deduplication and quality filtering
 */
class DiscoveryResult {
  constructor(topic, hints) {
    this.topic = topic;
    this.hints = hints;
    this.raw_sources = []; // DiscoveredSource[]
    this.candidate_insights = []; // CandidateInsight[]
    this.execution_time_ms = 0;
    this.agents_succeeded = []; // ['web', 'video', 'social']
    this.agents_failed = [];
    this.completion_status = 'pending'; // 'complete' | 'partial' | 'timeout' | 'failed'
    this.success = false;
  }
}

/**
 * FinalDigest: Output digest matching MVP format
 * Ready to be written to markdown file
 */
class FinalDigest {
  constructor(topic) {
    this.topic = topic;
    this.generated_at = new Date().toISOString();
    this.insights = []; // DeduplicatedInsight[]
    this.antipatterns = [];
    this.actions = [];
    this.resources = [];
    this.discovery_status = '';
    this.quality_warning = null;
    this.file_path = '';
  }
}
```

---

## Input Validation Module

```javascript
/**
 * INPUT VALIDATION MODULE
 * Validates and parses user input
 * Tasks: T004-T006
 */

/**
 * Validates topic against constraints
 * @param {string} topic - User-provided topic
 * @returns {ValidationResult}
 */
function validateTopic(topic) {
  if (!topic) {
    return createValidationError(
      ERROR_CODES.TOPIC_MISSING,
      'topic is required'
    );
  }

  const trimmed = String(topic).trim();

  if (!trimmed) {
    return createValidationError(
      ERROR_CODES.TOPIC_EMPTY,
      'topic cannot be empty'
    );
  }

  if (trimmed.length > CONFIG.CONSTRAINTS.TOPIC_MAX_LENGTH) {
    return createValidationError(
      ERROR_CODES.TOPIC_TOO_LONG,
      `topic exceeds ${CONFIG.CONSTRAINTS.TOPIC_MAX_LENGTH} characters`
    );
  }

  if (!CONFIG.CONSTRAINTS.TOPIC_PATTERN.test(trimmed)) {
    return createValidationError(
      ERROR_CODES.TOPIC_INVALID_CHARS,
      'topic contains invalid characters (use alphanumeric, hyphens, underscores)'
    );
  }

  return { valid: true, topic: trimmed };
}

/**
 * Parses and normalizes hints
 * @param {string|string[]} hints - Comma-separated or array of hints
 * @returns {ValidationResult}
 */
function parseAndValidateHints(hints) {
  if (!hints || (Array.isArray(hints) && hints.length === 0)) {
    return { valid: true, hints: [] };
  }

  const hintsArray = Array.isArray(hints)
    ? hints
    : String(hints)
        .split(',')
        .map(h => h.trim())
        .filter(h => h.length > 0);

  // Remove duplicates
  const uniqueHints = [...new Set(hintsArray)];

  // Validate count
  if (uniqueHints.length > CONFIG.CONSTRAINTS.HINTS_MAX_COUNT) {
    return createValidationError(
      ERROR_CODES.HINTS_TOO_MANY,
      `hints exceeds ${CONFIG.CONSTRAINTS.HINTS_MAX_COUNT} items`
    );
  }

  // Validate individual lengths
  for (const hint of uniqueHints) {
    if (hint.length > CONFIG.CONSTRAINTS.HINTS_MAX_LENGTH) {
      return createValidationError(
        ERROR_CODES.HINT_TOO_LONG,
        `hint "${hint.substring(0, 20)}..." exceeds ${CONFIG.CONSTRAINTS.HINTS_MAX_LENGTH} characters`
      );
    }
  }

  return { valid: true, hints: uniqueHints };
}

/**
 * Main input parser
 * @param {string} topic - Topic to discover
 * @param {string} [hintsStr] - Optional hints
 * @returns {ParseResult}
 */
function parseUserInput(topic, hintsStr) {
  // Validate topic
  const topicResult = validateTopic(topic);
  if (!topicResult.valid) {
    return {
      success: false,
      error: topicResult.error,
      errorCode: topicResult.errorCode,
    };
  }

  // Parse hints
  const hintsResult = parseAndValidateHints(hintsStr);
  if (!hintsResult.valid) {
    return {
      success: false,
      error: hintsResult.error,
      errorCode: hintsResult.errorCode,
    };
  }

  return {
    success: true,
    userInput: new UserInput(topicResult.topic, hintsResult.hints),
  };
}
```

---

## Agent Interface & Orchestrator

```javascript
/**
 * AGENT INTERFACE & ORCHESTRATOR
 * Abstract agent definition and orchestrator logic
 * Tasks: T007-T009
 */

/**
 * Abstract Agent Interface
 * Implemented by: WebDiscoveryAgent, VideoDiscoveryAgent, SocialDiscoveryAgent
 */
class DiscoveryAgent {
  constructor(agentType) {
    this.agentType = agentType; // 'web', 'video', 'social'
    this.startTime = null;
    this.executionTime = 0;
  }

  /**
   * Execute discovery for topic
   * @param {string} topic
   * @param {string[]} hints
   * @returns {Promise<DiscoveredSource[]>}
   */
  async discover(topic, hints) {
    throw new Error('Must implement discover()');
  }

  /**
   * Get execution time in milliseconds
   */
  getExecutionTime() {
    return this.executionTime;
  }

  /**
   * Format results as DiscoveredSource[]
   * @param {*} rawResults
   * @returns {DiscoveredSource[]}
   */
  formatResults(rawResults) {
    throw new Error('Must implement formatResults()');
  }
}

/**
 * ORCHESTRATOR: Coordinates parallel agent execution
 * Main entry point for discovery process
 */
class DiscoveryOrchestrator {
  constructor(userInput) {
    this.userInput = userInput;
    this.startTime = Date.now();
    this.agents = this.initializeAgents();
    this.result = new DiscoveryResult(userInput.topic, userInput.hints);
  }

  /**
   * Initialize discovery agents
   * @private
   */
  initializeAgents() {
    // Placeholder: Agents will be implemented in Phase 3 (T016-T024)
    return {
      web: null,    // WebDiscoveryAgent (T016-T018)
      video: null,  // VideoDiscoveryAgent (T019-T021)
      social: null, // SocialDiscoveryAgent (T022-T024)
    };
  }

  /**
   * Check if execution timeout exceeded
   */
  isTimedOut() {
    return Date.now() - this.startTime > CONFIG.TIMEOUT_MS;
  }

  /**
   * Get remaining time in milliseconds
   */
  getTimeRemaining() {
    return Math.max(
      0,
      CONFIG.TIMEOUT_MS - (Date.now() - this.startTime)
    );
  }

  /**
   * Main orchestration: Spawn agents, collect results, merge
   * @returns {Promise<DiscoveryResult>}
   */
  async orchestrate() {
    try {
      // Spawn all agents in parallel
      const agentPromises = CONFIG.EXECUTION.PARALLEL_AGENTS.map(agentType =>
        this.executeAgentWithTimeout(agentType)
      );

      // Wait for all agents OR timeout
      const settledResults = await Promise.allSettled(agentPromises);

      // Merge results
      await this.mergeResults(settledResults);

      // Update completion status
      this.updateCompletionStatus();

      return this.result;
    } catch (error) {
      this.result.success = false;
      this.result.completion_status = 'error';
      return this.result;
    }
  }

  /**
   * Execute single agent with timeout
   * @private
   */
  async executeAgentWithTimeout(agentType) {
    const agent = this.agents[agentType];
    if (!agent) {
      throw new Error(`Agent ${agentType} not initialized`);
    }

    return Promise.race([
      agent.discover(this.userInput.topic, this.userInput.hints),
      new Promise((_, reject) =>
        setTimeout(
          () => reject(new Error(`${agentType} agent timed out`)),
          this.getTimeRemaining()
        )
      ),
    ]);
  }

  /**
   * Merge results from all agents
   * @private
   */
  async mergeResults(settledResults) {
    const agentTypes = CONFIG.EXECUTION.PARALLEL_AGENTS;

    for (let i = 0; i < settledResults.length; i++) {
      const agentType = agentTypes[i];
      const result = settledResults[i];

      if (result.status === 'fulfilled' && result.value) {
        // Add sources to result
        if (Array.isArray(result.value)) {
          this.result.raw_sources.push(...result.value);
        }
        this.result.agents_succeeded.push(agentType);
      } else {
        this.result.agents_failed.push(agentType);
      }
    }
  }

  /**
   * Determine completion status based on agent results
   * @private
   */
  updateCompletionStatus() {
    const successCount = this.result.agents_succeeded.length;
    this.result.execution_time_ms = Date.now() - this.startTime;

    if (this.isTimedOut()) {
      this.result.completion_status = 'timeout';
    } else if (successCount === 3) {
      this.result.completion_status = 'complete';
    } else if (successCount > 0) {
      this.result.completion_status = 'partial';
    } else {
      this.result.completion_status = 'failed';
    }

    this.result.success = successCount > 0;
  }
}
```

---

## Processing Pipeline

```javascript
/**
 * PROCESSING PIPELINE
 * Extract insights, deduplicate, filter by quality
 * Tasks: T013-T015 (scaffolding), T031-T033 (implementation)
 */

/**
 * Extract candidate insights from discovered sources
 * Task T031: Generate 20-40 insight proposals
 */
function extractCandidateInsights(discoveryResult) {
  const insights = [];

  for (const source of discoveryResult.raw_sources) {
    // Extract key insights from each source
    const sourceInsights = extractInsightsFromSource(source);
    insights.push(...sourceInsights);
  }

  return insights.slice(0, CONFIG.DISCOVERY.CANDIDATE_INSIGHTS_MAX);
}

/**
 * Extract insights from a single source
 * @private
 */
function extractInsightsFromSource(source) {
  // Placeholder: Will be filled with actual extraction logic
  // For now, create a simple insight from source content
  return [
    new CandidateInsight({
      title: source.title,
      description: source.content.substring(0, 200),
      evidence: source.content,
      source_urls: [source.url],
      source_types: [source.source_type],
      published_date: source.published_date,
      days_old: source.days_old,
      freshness_score: source.freshness_score,
    }),
  ];
}

/**
 * Task T014: Semantic deduplication (placeholder)
 * Will be filled in Phase 4 User Story 2 (T053-T056)
 */
function deduplicateInsights(candidateInsights) {
  // Placeholder: Group by semantic equivalence, retain highest-scoring
  return candidateInsights.map(
    insight =>
      new DeduplicatedInsight({
        ...insight,
        quality_pass: insight.combined_score >= CONFIG.QUALITY.RUBRIC_PASS_THRESHOLD,
      })
  );
}

/**
 * Task T015: Quality filtering (placeholder)
 * Apply MVP quality rubric (≥2 on ≥3 dimensions)
 */
function filterByQuality(deduplicatedInsights) {
  // Placeholder: Credibility filtering will be added in US2
  return deduplicatedInsights.filter(
    insight => insight.quality_pass
  );
}
```

---

## Output Generation Module

```javascript
/**
 * OUTPUT GENERATION MODULE
 * Generate markdown digest and write to file
 * Tasks: T011-T012, T037-T039
 */

/**
 * Task T011: Generate FinalDigest
 */
function generateFinalDigest(topic, discoveryResult, filteredInsights) {
  const digest = new FinalDigest(topic);

  // Select insights (1-3)
  digest.insights = filteredInsights.slice(0, CONFIG.QUALITY.MAX_INSIGHTS);

  // Extract antipatterns from insights
  digest.antipatterns = extractAntipatterns(filteredInsights).slice(
    0,
    CONFIG.QUALITY.MAX_ANTIPATTERNS
  );

  // Extract actions from insights
  digest.actions = extractActions(filteredInsights).slice(
    0,
    CONFIG.QUALITY.MAX_ACTIONS
  );

  // Extract resources from sources
  digest.resources = extractResources(discoveryResult.raw_sources).slice(
    0,
    CONFIG.QUALITY.MAX_RESOURCES
  );

  // Set discovery status and warnings
  digest.discovery_status = formatDiscoveryStatus(discoveryResult);
  if (digest.insights.length < CONFIG.QUALITY.MIN_INSIGHTS + 1) {
    digest.quality_warning =
      '⚠️ Low-signal content — insights below represent the best available material';
  }

  // Task T039: Generate file path
  digest.file_path = generateFilePath(topic);

  return digest;
}

/**
 * Extract antipatterns from insights
 * @private
 */
function extractAntipatterns(insights) {
  return insights
    .slice(0, CONFIG.QUALITY.MAX_ANTIPATTERNS)
    .map((insight, idx) => ({
      title: `Anti-pattern ${idx + 1}: ${insight.title}`,
      description: `Avoid because: ${insight.description.split('.')[0]}`,
      source: insight.primary_source_url,
    }));
}

/**
 * Extract actionable steps from insights
 * @private
 */
function extractActions(insights) {
  return insights
    .slice(0, CONFIG.QUALITY.MAX_ACTIONS)
    .map((insight, idx) => ({
      title: `Action ${idx + 1}: ${insight.title}`,
      effort: 'medium',
      time_minutes: 15,
      steps: [
        `Understand: ${insight.description.split('.')[0]}`,
        'Apply: Use this insight in your context',
        'Measure: Track the outcome',
      ],
      outcome: 'Improved understanding and applied knowledge',
    }));
}

/**
 * Extract resources from sources
 * @private
 */
function extractResources(sources) {
  return sources
    .slice(0, CONFIG.QUALITY.MAX_RESOURCES)
    .map(source => ({
      title: source.title,
      url: source.url,
      source_type: source.source_type,
      reason: `See the original ${source.source_type} source`,
    }));
}

/**
 * Format discovery status string
 * @private
 */
function formatDiscoveryStatus(discoveryResult) {
  const status = discoveryResult.completion_status;

  switch (status) {
    case 'complete':
      return `Complete (${discoveryResult.agents_succeeded.length}/3 agents successful)`;
    case 'partial':
      return `Incomplete: ${discoveryResult.agents_failed.join(', ')} unavailable`;
    case 'timeout':
      return 'Timeout: partial results used';
    default:
      return 'Failed to discover content';
  }
}

/**
 * Task T039: Generate output file path
 */
function generateFilePath(topic) {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');

  // Convert topic to slug
  const topicSlug = topic
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .substring(0, 50);

  return `${CONFIG.OUTPUT.BASE_DIR}/${year}/${month}/digest-${year}-${month}-${day}-${topicSlug}.md`;
}

/**
 * Task T012: Write digest to markdown file
 */
async function writeDigestFile(digest) {
  const markdown = formatDigestMarkdown(digest);

  return {
    file_path: digest.file_path,
    content: markdown,
    size_bytes: markdown.length,
    insight_count: digest.insights.length,
    antipattern_count: digest.antipatterns.length,
    action_count: digest.actions.length,
    resource_count: digest.resources.length,
  };
}

/**
 * Format digest as markdown
 * @private
 */
function formatDigestMarkdown(digest) {
  const lines = [
    `# Daily Digest — ${digest.topic}`,
    '',
    `**Generated**: ${new Date(digest.generated_at).toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })} UTC`,
    `**Discovery Status**: ${digest.discovery_status}`,
    '',
  ];

  // Insights
  if (digest.insights.length > 0) {
    lines.push(`## 🧠 Key Insights (${digest.insights.length})`);
    lines.push('');
    for (const insight of digest.insights) {
      lines.push(`### ${insight.title}`);
      lines.push('');
      lines.push(insight.description);
      lines.push('');
      lines.push(`**Source**: ${insight.primary_source_url}`);
      lines.push(`**Evidence**: "${insight.evidence}"`);
      lines.push('');
    }
  }

  // Antipatterns
  if (digest.antipatterns.length > 0) {
    lines.push(`## ⚠️ Anti-patterns (${digest.antipatterns.length})`);
    lines.push('');
    for (const ap of digest.antipatterns) {
      lines.push(`- **${ap.title}**: ${ap.description} (${ap.source})`);
    }
    lines.push('');
  }

  // Actions
  if (digest.actions.length > 0) {
    lines.push(`## ⚡ Actions to Try (${digest.actions.length})`);
    lines.push('');
    for (const action of digest.actions) {
      lines.push(`### ${action.title}`);
      lines.push('');
      lines.push(`- **Effort**: ${action.effort}`);
      lines.push(`- **Time**: ${action.time_minutes} minutes`);
      lines.push('- **Steps**:');
      for (let i = 0; i < action.steps.length; i++) {
        lines.push(`  ${i + 1}. ${action.steps[i]}`);
      }
      lines.push(`- **Outcome**: ${action.outcome}`);
      lines.push('');
    }
  }

  // Resources
  if (digest.resources.length > 0) {
    lines.push(`## 🔗 Resources (${digest.resources.length})`);
    lines.push('');
    for (const resource of digest.resources) {
      lines.push(`- [${resource.title}](${resource.url}) — ${resource.reason}`);
    }
    lines.push('');
  }

  // Quality warning
  if (digest.quality_warning) {
    lines.push('---');
    lines.push('');
    lines.push(digest.quality_warning);
    lines.push('');
  }

  return lines.join('\n');
}
```

---

## Error Handling

```javascript
/**
 * ERROR HANDLING
 * Centralized error creation and management
 */

/**
 * Create validation error
 * @private
 */
function createValidationError(errorCode, message) {
  return {
    valid: false,
    errorCode,
    error: message,
  };
}

/**
 * Fallback messages for various failure modes
 */
const FALLBACK_MESSAGES = {
  NO_CONTENT: `No relevant content discovered for topic '{topic}'.

Try providing text snippets manually:

/daily-digest "{topic}" "[snippet1]" "[snippet2]" "[snippet3]"

This will trigger Phase 1 (MVP) manual mode.`,

  TIMEOUT: `⚠️ **Discovery incomplete: operation timed out**

System exceeded the 45-second deadline. Digest generated from best-available partial results.`,

  PARTIAL: `⚠️ **Low-signal content** — Insights below represent the best available material.

Discovery incomplete: {failed_sources} unavailable`,

  ERROR: `Error during discovery: {error}

Try again or provide text snippets manually:

/daily-digest "{topic}" "[snippet1]" "[snippet2]"`,
};

/**
 * Create fallback message
 */
function createFallbackMessage(type, context = {}) {
  let message = FALLBACK_MESSAGES[type] || FALLBACK_MESSAGES.ERROR;

  // Template string replacement
  for (const [key, value] of Object.entries(context)) {
    message = message.replace(`{${key}}`, value);
  }

  return message;
}
```

---

## Utility Functions

```javascript
/**
 * UTILITY FUNCTIONS
 * Helper functions for common operations
 */

/**
 * Calculate days since publication date
 */
function calculateDaysOld(dateString) {
  if (!dateString) return null;
  const publishedDate = new Date(dateString);
  const today = new Date();
  return Math.floor((today - publishedDate) / (1000 * 60 * 60 * 24));
}

/**
 * Calculate freshness score based on days old
 */
function calculateFreshnessScore(daysOld) {
  if (daysOld === null || daysOld === undefined) return 1;

  const thresholds = CONFIG.DISCOVERY.FRESHNESS_THRESHOLDS;

  if (daysOld < thresholds.VERY_FRESH.days) return thresholds.VERY_FRESH.score;
  if (daysOld < thresholds.FRESH.days) return thresholds.FRESH.score;
  if (daysOld < thresholds.MODERATE.days) return thresholds.MODERATE.score;
  return thresholds.STALE.score;
}

/**
 * Format timestamp for display
 */
function formatTimestamp(date = new Date()) {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * Create topic slug for file naming
 */
function createTopicSlug(topic) {
  return topic
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .substring(0, 50);
}

/**
 * Log with timestamp
 */
function log(level, message, data = {}) {
  const timestamp = formatTimestamp();
  console.log(`[${timestamp}] [${level}] ${message}`, data);
}
```

---

## Main Entrypoint

```javascript
/**
 * MAIN ENTRYPOINT
 * Skill invocation: /autonomous-discovery <topic> [--hints <hints>]
 */

async function autonomousDiscovery(topic, hintsArg) {
  try {
    log('INFO', 'Starting autonomous discovery', { topic, hintsArg });

    // 1. Parse and validate input
    const parseResult = parseUserInput(topic, hintsArg);
    if (!parseResult.success) {
      log('ERROR', 'Input validation failed', parseResult);
      return {
        success: false,
        error: parseResult.error,
        errorCode: parseResult.errorCode,
      };
    }

    const userInput = parseResult.userInput;
    log('INFO', 'Input validated', {
      topic: userInput.topic,
      hints: userInput.hints,
    });

    // 2. Orchestrate parallel discovery
    const orchestrator = new DiscoveryOrchestrator(userInput);
    const discoveryResult = await orchestrator.orchestrate();
    log('INFO', 'Discovery complete', {
      status: discoveryResult.completion_status,
      sources: discoveryResult.raw_sources.length,
      execution_time: discoveryResult.execution_time_ms,
    });

    // 3. Extract and process insights
    const candidateInsights = extractCandidateInsights(discoveryResult);
    const deduplicatedInsights = deduplicateInsights(candidateInsights);
    const filteredInsights = filterByQuality(deduplicatedInsights);

    // 4. Handle failure cases
    if (filteredInsights.length === 0) {
      const fallbackMsg = createFallbackMessage('NO_CONTENT', {
        topic: userInput.topic,
      });
      log('WARN', 'No credible content found', { topic: userInput.topic });
      return {
        success: false,
        message: fallbackMsg,
        discovery_status: discoveryResult.completion_status,
      };
    }

    // 5. Generate digest
    const digest = generateFinalDigest(
      userInput.topic,
      discoveryResult,
      filteredInsights
    );
    log('INFO', 'Digest generated', {
      insights: digest.insights.length,
      antipatterns: digest.antipatterns.length,
      actions: digest.actions.length,
      resources: digest.resources.length,
    });

    // 6. Write output file
    const writeResult = await writeDigestFile(digest);
    log('INFO', 'Digest written', {
      file_path: writeResult.file_path,
      size_bytes: writeResult.size_bytes,
    });

    return {
      success: true,
      file_path: writeResult.file_path,
      digest_summary: {
        insights: writeResult.insight_count,
        antipatterns: writeResult.antipattern_count,
        actions: writeResult.action_count,
        resources: writeResult.resource_count,
      },
      discovery_status: discoveryResult.completion_status,
      execution_time_ms: discoveryResult.execution_time_ms,
    };
  } catch (error) {
    log('ERROR', 'Skill execution failed', { error: error.message });
    return {
      success: false,
      error: error.message,
      fallback: createFallbackMessage('ERROR', { error: error.message }),
    };
  }
}

// Export for testing and integration
module.exports = {
  autonomousDiscovery,
  CONFIG,
  // Classes
  UserInput,
  DiscoveredSource,
  CandidateInsight,
  DeduplicatedInsight,
  DiscoveryResult,
  FinalDigest,
  DiscoveryOrchestrator,
  // Functions
  parseUserInput,
  validateTopic,
  parseAndValidateHints,
  extractCandidateInsights,
  deduplicateInsights,
  filterByQuality,
  generateFinalDigest,
  writeDigestFile,
  // Utilities
  calculateDaysOld,
  calculateFreshnessScore,
  formatTimestamp,
  createTopicSlug,
};
```

---

## Implementation Status

### ✅ Completed
- **Configuration & Constants**: All tunable parameters centralized
- **Data Structures**: Type definitions for all entities (UserInput, DiscoveredSource, CandidateInsight, etc.)
- **Input Validation**: Topic and hints validation (T004-T006)
- **Agent Interface**: Abstract agent definition for extensibility
- **Orchestrator**: Parallel execution, timeout handling, result merging (T007-T009)
- **Processing Pipeline**: Deduplication and quality filtering scaffolding (T013-T015)
- **Output Generation**: Markdown formatting and file path generation (T011-T012, T037-T039)
- **Error Handling**: Centralized error codes and fallback messages
- **Utilities**: Helper functions for dates, slugs, logging
- **Main Entrypoint**: Skill invocation with full error handling

### ⏳ Placeholder (To be implemented in Phase 3 & 4)
- **WebDiscoveryAgent**: Implement in T016-T018
- **VideoDiscoveryAgent**: Implement in T019-T021
- **SocialDiscoveryAgent**: Implement in T022-T024
- **Credibility Scoring**: Implement in T040-T044 (US2)
- **Deduplication Logic**: Implement in T053-T056 (US2)
- **Quality Enforcement**: Implement with credibility rules (US2)

---

## Best Practices Applied

✅ **Separation of Concerns**: Each module has a single responsibility
✅ **Configuration Centralization**: All constants in one place for easy tuning
✅ **Type Safety**: Structured classes for all data types
✅ **Error Handling**: Centralized error codes and fallback messages
✅ **Extensibility**: Abstract agent interface for future agent types
✅ **Testability**: Pure functions with clear inputs/outputs
✅ **Logging**: Structured logging for debugging and monitoring
✅ **Documentation**: Clear comments and docstrings
✅ **Backwards Compatibility**: Fallback to MVP manual mode
✅ **Modularity**: Pluggable components for future enhancements

---

**Next Phase**: Implement Phase 3 User Story 1 - Autonomous Discovery Agents (T016-T039)
