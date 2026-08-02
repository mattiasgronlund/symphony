---
name: phase-implementer
description: Implement Stage 3 of an approved phase against its behavior contract and verification matrix. Use to implement, continue, or resume a phase after planning and verification gates are satisfied.
---

# Phase Implementer

Resolve the named phase. For "resume", use the active `In progress` phase and first incomplete milestone.

Before code changes, read all applicable instructions, the ExecPlan, approved behavior contract, verification matrix, relevant SPEC requirements, prior phase outcomes, repository code, tests, and Git diff. Reconcile stale paths or assumptions in the plan before coding.

## Implementation order

1. Stable contracts and schemas.
2. Thin end-to-end walking skeleton through all necessary layers.
3. Main successful workflow.
4. Authorization and validation.
5. Failure and recovery behavior.
6. Operational controls and observability.
7. Edge cases.
8. Preparation for documentation conformance.

For each milestone:

- Timestamp progress.
- Keep changes within phase scope.
- Run relevant validation.
- Record failures, discoveries, decisions, and evidence.
- Mark complete only when the observable milestone outcome passes.

Write implementation-specific unit tests alongside code. Preserve expected external behavior defined by Stage 1 and prove it using Stage 2 evidence.

Do not invent unresolved product decisions. Record blockers and continue independent work only when safe. Do not silently absorb later-phase scope.

End with a Stage 3 checkpoint; do not mark the whole phase complete until `$phase-closeout` succeeds.
