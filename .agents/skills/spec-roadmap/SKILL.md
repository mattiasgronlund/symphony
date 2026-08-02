---
name: spec-roadmap
description: Prepare, audit, or update planning documentation from a large SPEC, including requirement IDs, ROADMAP.md, TRACEABILITY.md, AGENTS.md, .agent/PLANS.md, vertical phases, and discovery spikes. Use for planning governance, not product implementation.
---

# Specification Roadmap

Prepare or reconcile the repository's phased implementation system.

## Required reading

Read `SPEC.md`, all applicable `AGENTS.md`/`AGENTS.override.md`, `.agent/PLANS.md` if present, existing architecture/testing/deployment/planning documents, representative code, and Git status.

## Workflow

1. Preserve canonical product meaning and add stable requirement IDs where missing.
2. Identify behavior already implemented, ambiguity, contradiction, duplication, hidden dependencies, and untestable requirements.
3. Divide work into vertical product/operator phases with independently observable outcomes.
4. Create bounded discovery spikes for uncertainty that could invalidate behavior or architecture.
5. Update `docs/implementation/ROADMAP.md`.
6. Update `docs/implementation/TRACEABILITY.md`; every normative requirement must have a disposition and unassigned count should be zero.
7. Reconcile root `AGENTS.md` and `.agent/PLANS.md` without discarding valid existing instructions.
8. Detail only the next sufficiently understood phase; leave later phases at roadmap level when discoveries may change them.
9. Validate IDs, links, phase references, commands, and Git diff.

Use `references/review-checklist.md` before finishing.

Do not implement product code.
