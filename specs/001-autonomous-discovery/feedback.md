# Phase 2 Spec Feedback

The Phase 2 autonomous discovery spec has the right overall direction, but it still needs cleanup before it becomes a strong planning input.

## Findings

- The spec still contains substantial implementation detail. It names MCP as the integration mechanism, specific external services, cosine similarity, embeddings, retry strategy, and even a weighted quality formula. Those are design decisions and should move to planning or research documents, not remain in the feature spec.
- Several success criteria are not realistic as Phase 2 acceptance gates. Examples include A/B comparison against manually curated MVP digests, 95% precision verified by manual review, and measurements across 100 diverse topics. Those are good longer-term KPIs, but too heavy and subjective for a planning-ready feature spec.
- The story decomposition is weaker than it appears. User Story 2 (parallel discovery) and User Story 4 (graceful degradation) are important, but they are more like architectural or reliability slices layered on top of the main discovery story than independently deployable user-facing increments.
- Quality filtering and attribution are still underspecified in product terms. The spec says to prefer authoritative sources and document excluded sources, but it does not clearly define where excluded-source information appears or what "authority" means from a user-visible behavior standpoint.
- The spec still contains template remnants and the checklist overstates spec quality. Placeholder comments remain in the requirements/success criteria sections, and the checklist says there are no implementation details even though there clearly are.

## Recommended Changes

- Move implementation choices out of `spec.md` into a later planning/research document:
  - MCP choice
  - cosine similarity / embeddings
  - retry algorithms
  - exact scoring formulas
- Reduce success criteria to planning-stage acceptance gates that are measurable without requiring production-scale datasets or manual review campaigns.
- Reframe User Story 2 and User Story 4 as supporting requirements or implementation concerns if they are not truly independent user-facing slices.
- Clarify user-facing filtering and attribution behavior:
  - what users will see in the digest
  - what is internal metadata only
  - whether excluded-source details belong in logs, diagnostics, or output
- Remove leftover template comments and update the checklist so it accurately reflects the spec’s current state.

## Overall Assessment

This is a solid draft with the right Phase 2 problem framing, but it is not yet as clean as the finalized MVP spec. It should go through one more requirements-hygiene pass before `/speckit.plan`.

## Round 2 Feedback

The first cleanup pass improved the spec substantially, but a few issues still need to be resolved before planning.

### Findings

- Failure-mode behavior is still contradictory. The spec says ultra-niche topics should fall back to a manual input request, timeout scenarios should still generate a digest from partial results, and all-source failures should fall back to manual mode. Those are different user experiences, and the spec does not define the boundary between "no content found," "all sources failed," and "partial low-signal results."
- Source credibility is still underspecified in product terms. The spec requires filtering to credible sources and citing the most credible or authoritative source, but it does not define the user-visible rules for those judgments. That makes the requirement hard to implement consistently and hard to test.
- Latency expectations are inconsistent. One acceptance scenario uses a 30-second timeout threshold, one functional requirement says completion should stay under 1 minute, and the assumptions section broadens this to seconds to low minutes. Planning needs one explicit budget and one definition of timeout behavior.
- The checklist overstates readiness. The spec still contains template placeholder comments in mandatory sections, while the checklist says all required content is complete and the spec is ready for planning.

### Recommended Changes

- Define a single failure-state decision tree covering:
  - no relevant content discovered
  - some sources fail but enough content remains
  - all discovery sources fail
  - timeouts with partial results
- Replace vague credibility language with product-level rules that QA can verify. For example, specify whether credibility is a hard inclusion threshold, a ranking signal, or both, and clarify whether weaker sources can appear in resources even if they cannot support insights.
- Normalize the performance requirement to one explicit target for:
  - when discovery is considered timed out
  - how long the full command is allowed to run
  - what user-visible warning appears when the target is missed
- Remove the remaining template comments and update the checklist so its pass/fail status matches the actual state of `spec.md`.

### Overall Assessment

This version is close, but I would still hold it out of `/speckit.plan` until the failure-state UX, credibility rules, and latency budget are made explicit.

## Round 3 Feedback

The spec package is close, but there are still a couple of consistency issues between the spec and its own readiness checklist.

### Findings

- The credibility rules are internally contradictory. One requirement says non-credible sources are excluded entirely, while the next says the resources section may include non-credible sources if they contain useful supporting information. The spec needs one rule for whether non-credible sources are ever user-visible.
- The checklist says placeholder comments were removed, but `spec.md` still contains template comments in the requirements and success criteria sections. That makes the checklist's "passed" status inaccurate.
- The checklist summary is out of sync with the current document. The spec now contains 13 functional requirements and 7 success criteria, while the checklist still reports 12 and 6.

### Recommended Changes

- Resolve the credibility contradiction by choosing one of these approaches:
  - exclude non-credible sources from both insights and resources
  - exclude them from insights but allow them in resources with explicit wording that this is an exception
- Remove the remaining template comments from `spec.md`, or update the checklist to stop claiming they are gone.
- Reconcile the checklist summary counts with the current spec so the readiness signal is trustworthy.

### Overall Assessment

This draft is materially improved, but it still needs one more consistency pass before the spec package can be considered fully clean.

## Round 4 Feedback

The spec is now close to planning-ready, but there are still two remaining consistency issues that should be fixed before treating the package as fully clean.

### Findings

- The latency requirement is still inconsistent across the spec. User Story 1 still describes timeout as greater than 30 seconds, one functional requirement still says completion should be under 1 minute total, and later sections use a 45-second timeout budget. The checklist says latency was normalized, but the actual spec still contains three different thresholds.
- The success criteria do not fully align with the failure-mode UX. One success criterion says that when discovery fails, the digest includes a quality warning, but the failure-mode section says that when there are zero credible sources or all sources fail, the system should show a manual fallback message instead of generating a digest.

### Recommended Changes

- Normalize all latency references in `spec.md` to one explicit target and use the same threshold in:
  - acceptance scenarios
  - functional requirements
  - success criteria
  - assumptions and constraints
- Tighten the wording of the success criteria so it distinguishes:
  - partial failure or low-signal discovery, which still produces a digest with warnings
  - total failure or zero credible content, which produces the manual fallback message instead of a digest

### Overall Assessment

This version is materially improved, but the timeout budget and failure/success criteria still need one final consistency pass before the spec package can be considered fully clean.

## Round 5 Feedback

The spec package is very close, but there is still one product-level contradiction and a small amount of checklist drift.

### Findings

- User Story 2 still conflicts with the later failure-mode definition. Its acceptance scenario says that when no credible sources are available, the system generates a digest with a quality warning. Later sections now define zero credible sources as a fallback case that shows a manual input message and does not generate a digest.
- The checklist still has stale wording in one readiness item. It says the feature meets measurable outcomes defined in "6 success criteria," but the spec and the checklist summary now both show 8 success criteria.
- The checklist status line is also stale. It still says "PASSED (after Round 2 feedback incorporation)" even though it now documents rounds 3-4 fixes and claims all feedback rounds are resolved.

### Recommended Changes

- Reconcile User Story 2 acceptance scenario 2 with the rest of the spec by choosing one behavior for the zero-credible-source case:
  - generate a low-signal digest with warning
  - show fallback message only, with no digest
- Update the checklist wording so every mention of success-criteria counts matches the current total of 8.
- Refresh the checklist status text so it reflects the latest review state rather than Round 2.

### Overall Assessment

This is now close to fully clean, but I would still fix the zero-credible-source contradiction and the remaining checklist drift before treating the spec package as fully aligned.
