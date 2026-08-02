---
name: phase-planner
description: Create, expand, or update an implementation-ready ExecPlan for a named phase or the next ready roadmap phase. Use before behavior, test, or code work when a full phase plan does not yet exist. Do not implement product code.
---

# Phase Planner

Resolve the named phase. For "next", select the earliest incomplete phase whose dependencies are satisfied and blockers resolved.

Read applicable repository instructions, `.agent/PLANS.md`, relevant SPEC sections, roadmap, traceability, prior phase outcomes, existing phase document, relevant source/tests/configuration, and Git status.

Create or update `docs/implementation/phases/phase-NN-<name>.md` from the phase template.

The plan must:

- Define an observable outcome and included/excluded requirement IDs.
- Identify dependencies, current behavior, target behavior, repository paths, interfaces, risks, and blockers.
- Include the staged workflow: optional discovery, behavior contract, verification design, implementation, and closure.
- Use scenario IDs and a verification matrix.
- Define a thin end-to-end walking skeleton.
- Include security, authorization, data, migration, rollout, rollback, recovery, and observability where relevant.
- Include exact commands discovered from the repository.
- Define stage gates and evidence requirements.
- Update roadmap/traceability only when planning reveals allocation, dependency, blocker, or status changes.

Do not guess missing product decisions and do not implement code.
