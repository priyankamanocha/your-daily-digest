# Tasks Feedback

The task list is broadly aligned to the finalized MVP, but a few execution details should be tightened before implementation starts.

## Findings

- The plan marks several tasks as parallelizable even though they all edit the same file: `.claude/commands/daily-digest.md`. In particular, T012-T015 are marked `[P]`, and the parallel section says they can run in parallel. For a single-file implementation, that is likely to create merge/conflict risk rather than real acceleration.
- T009 underspecifies its dependencies. The markdown writer does not just depend on T012. It also depends on anti-pattern extraction, action generation, resource selection, evidence handling, and low-signal handling. The dependency graph should reflect that.
- T003 looks unnecessary. Copying benchmark cases from `specs/000-mvp-manual-digest/benchmark.md` into a separate local reference file creates duplication and weakens the benchmark as a single source of truth.
- The final validation wording still contains stale count language: "5 high-quality insights extracted." That no longer matches the MVP schema, which is 1-3 insights per run.
- T024 is questionable as a required delivery task. Creating sample digests in a hard-coded dated output directory risks checking in stale generated artifacts and mixing runtime output with documentation.

## Recommended Changes

- Remove the `[P]` parallel marker from tasks that all modify `.claude/commands/daily-digest.md`, or group them into one implementation task with sub-checks.
- Update T009 so it depends on the full content-generation set, not only T012.
- Remove T003 and point all testing directly to `specs/000-mvp-manual-digest/benchmark.md`.
- Rewrite the final validation line so it says all expected high-quality insights across benchmark runs are extracted, rather than "5 high-quality insights."
- Make T024 optional, or replace it with a lighter task such as capturing one verified example digest only if documentation needs it.

## Overall Assessment

This is close to a workable MVP execution plan. The main improvements are about sequencing and reducing unnecessary task noise, not changing scope.

## Round 2 Feedback

The task plan is now much closer to executable. Most of the earlier concerns were fixed. Only a few cleanup issues remain.

## Remaining Findings

- The "Sequential Implementation Path" section has an internal inconsistency in task numbering. The narrative there no longer matches the actual task list for T017-T019, and it says T019 was consolidated into T018 even though T019 still exists in the task list.
- The implementation strategy still says to move benchmark digests into `digests/2026/03/` for reference. That reintroduces the earlier concern about mixing generated runtime artifacts into the delivery path.
- The phase dependency section still says User Stories 1 and 2 can proceed in parallel, while the later guidance correctly says the single-file implementation should be sequential to avoid merge conflicts. The wording should be tightened so the plan does not imply conflicting execution models.

## Recommended Changes For Round 2

- Update the "Sequential Implementation Path" section so T017-T019 exactly match the current task list.
- Remove or make optional the step about moving benchmark digests into a dated output directory.
- Reword the dependency section to say the stories may overlap conceptually, but implementation in `.claude/commands/daily-digest.md` should proceed sequentially.

