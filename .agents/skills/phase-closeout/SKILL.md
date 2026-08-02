---
name: phase-closeout
description: Perform Stage 4 conformance and closure for an implemented phase: verify documentation against real behavior, run full validation, finalize rollout/recovery guidance, traceability, roadmap status, and retrospective.
---

# Phase Conformance and Closure

Use after Stage 3 implementation is complete or when validating whether a phase can close.

## Workflow

1. Exercise every important documented user and administrator example.
2. Correct documentation to match approved behavior and actual implementation; flag intentional deviations as decisions rather than silently rewriting requirements.
3. Verify labels, commands, messages, permissions, errors, recovery, audit, privacy, and operational procedures.
4. Run the complete test, lint, type-check, build, migration/rollback, and manual validation set applicable to the phase.
5. Record evidence and unresolved failures.
6. Finalize rollout, monitoring, rollback, and recovery instructions.
7. Update traceability evidence/status and roadmap status.
8. Complete phase outcomes and retrospective.
9. Review Git diff and preserve unrelated changes.

A phase closes only when `.agent/PLANS.md` completion rules are met. Otherwise leave it `Validating` or `Blocked` and state exact reasons.
