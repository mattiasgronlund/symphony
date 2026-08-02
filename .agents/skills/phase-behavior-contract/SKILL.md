---
name: phase-behavior-contract
description: Produce and review Stage 1 behavior-contract documentation for a planned phase: user docs, administrator/operator docs, examples, scenarios, permissions, errors, recovery, audit, and data effects. Use before acceptance-test or product-code implementation.
---

# Phase Behavior Contract

Work only on Stage 1 of the named or active phase unless a bounded discovery spike is required first.

## Inputs

Read the active ExecPlan, relevant SPEC requirements, existing product documentation, current UI/API/operator conventions, prior decisions, relevant code, and `.agent/PLANS.md`.

## Outputs

Create or update target documentation in repository-appropriate locations and update the phase plan with:

- User workflows and important examples.
- Administrator/operator workflows and operational warnings.
- Stable scenario catalogue using the bundled scenario template.
- Roles and permission matrix.
- Success, error, authorization, recovery, reversal, audit, telemetry, privacy, and data-lifecycle behavior.
- Clear labels for existing behavior, approved target behavior, open decisions, and implementation assumptions.

Documentation at this stage is a proposed target-behavior contract; do not claim it is already implemented.

## Gate

End with a Stage 1 checkpoint: status, evidence reviewed, discoveries, decisions, and effects on verification/implementation. Put detailed discoveries and decisions in the phase-wide logs.

Do not implement test harnesses or product code. If a technical uncertainty could invalidate the contract, record or execute a minimal Stage 0 spike and stop affected scenarios until resolved.
