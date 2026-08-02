---
name: phase-workflow
description: Coordinate the repository's phased delivery skills with short commands such as prepare, plan, behavior, verify, implement, close, resume, status, or run-next-stage for a named or next phase.
---

# Phase Workflow Coordinator

Route the user's short command to the narrow skill that owns the work.

## Commands

- `prepare` or `audit roadmap` → follow `$spec-roadmap`.
- `plan <phase>` or `plan next` → follow `$phase-planner`.
- `behavior <phase>` → follow `$phase-behavior-contract`.
- `verify <phase>` → follow `$phase-verification`.
- `implement <phase>` or `resume` → follow `$phase-implementer`.
- `close <phase>` → follow `$phase-closeout`.
- `status <phase>` → inspect roadmap, traceability, and ExecPlan; report stage/gate status without edits unless needed for consistency.
- `run-next-stage <phase>` → inspect the ExecPlan and run only the earliest stage whose prerequisites are satisfied.

Never skip a gate silently. If the user explicitly requests a skip, record the exception, rationale, risk, and compensating validation in the ExecPlan.

For multi-phase requests, process phases sequentially unless the work is demonstrably independent and read-only. Do not parallelize overlapping code edits.
