# Automated Validation

## Purpose

This document records the automated validation approach and latest results for the SignalFlow MVP.

## Validation Scope

The automated validation must verify `/daily-digest` output against:

- `specs/000-mvp-manual-digest/benchmark.md`
- `specs/000-mvp-manual-digest/contracts/digest-output-schema.md`

## Validation Criteria

- Structure
- Count rules
- Evidence presence
- Low-signal handling
- Benchmark expectations

## Latest Results

Status: Pending

Validation run has not yet been recorded in this document.

## Expected Artifacts

- Automated validation harness
- Generated digest outputs from benchmark runs
- Pass/fail summary by validation criterion

## Rerun Instructions

Run:

```bash
/validate-digest
```

## Notes

- Validation should be automated, not manual.
- Any rule that cannot be checked automatically should be called out explicitly in the results.

