---
name: phase-verification
description: Produce Stage 2 verification design for an approved behavior contract, including scenario-to-evidence mapping, acceptance/contract test skeletons, authorization checks, fixtures, and harness changes. Use before feature implementation.
---

# Phase Verification Design

Work only on Stage 2 for the named or active phase. Stage 1 must be approved or the plan must record an explicit exception.

## Workflow

1. Read the approved behavior contract, scenarios, ExecPlan, SPEC requirements, existing test architecture, commands, fixtures, and CI configuration.
2. Create/update a verification matrix mapping every material scenario to evidence.
3. Implement only test infrastructure needed to exercise the target behavior.
4. Add high-value acceptance, contract, integration, authorization, migration, and end-to-end test skeletons where appropriate.
5. Confirm expected failing tests fail for the intended absent behavior rather than broken setup.
6. Record exact commands and summarized expected-failure evidence.
7. Leave implementation-specific unit tests for Stage 3 when writing them now would couple tests to speculative internals.

## Gate

End with a Stage 2 checkpoint and update phase-wide discoveries/decisions. The gate should answer whether the tests would detect an incorrect implementation and whether the harness is credible.

Do not implement the product behavior, except for minimal non-feature harness support that is explicitly recorded.
