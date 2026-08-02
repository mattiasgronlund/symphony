# Codex Execution Plans for Phased Delivery

An ExecPlan is a self-contained, living implementation document. It must let a contributor unfamiliar with prior conversations resume the work using only the repository and the plan.

## Core principles

Every ExecPlan must:

- Deliver observable user or operator behavior, not merely files or scaffolding.
- Name concrete repository paths, commands, interfaces, and expected results.
- Remain current as work progresses.
- Separate canonical product requirements from implementation decisions.
- Preserve a runnable repository at meaningful checkpoints where practical.
- Include negative, authorization, failure, migration, recovery, and observability behavior where applicable.
- Be explicit about assumptions, uncertainty, and blocked product decisions.

Compilation, file existence, or tests being added are supporting evidence; they are not sufficient completion criteria.

## Mandatory phase stages

A substantial phase normally proceeds through these stages:

0. **Discovery** — optional; resolve uncertainty that could invalidate behavior or architecture.
1. **Behavior Contract** — define target user/admin documentation and scenario catalogue.
2. **Verification Design** — map scenarios to evidence; prepare harnesses, contracts, and high-value failing tests.
3. **Implementation** — build incrementally, beginning with a thin end-to-end walking skeleton.
4. **Conformance and Closure** — verify documentation against the implementation, run full validation, and close the phase.

A stage may be skipped only when the ExecPlan records why it provides no material value.

## Required ExecPlan sections

1. Title and status
2. Purpose and observable outcome
3. Requirements covered
4. Requirements explicitly excluded or deferred
5. Dependencies and prerequisites
6. Context and repository orientation
7. Current-state analysis
8. Proposed end state
9. Open product decisions and blockers
10. Stage 0 — Discovery, when needed
11. Stage 1 — Behavior Contract
12. Stage 2 — Verification Design
13. Stage 3 — Implementation
14. Stage 4 — Conformance and Closure
15. Interfaces, schemas, and dependencies
16. Security, privacy, authorization, and data handling
17. Migration, rollout, rollback, and recovery
18. Progress
19. Surprises & Discoveries
20. Decision Log
21. Outcomes & Retrospective

## Living sections

Continuously maintain:

- `Progress`
- `Surprises & Discoveries`
- `Decision Log`
- `Outcomes & Retrospective`

Use timestamps for meaningful progress entries. Record evidence, not only conclusions.

## Stage gates

Each stage ends with a concise checkpoint containing:

- Status: `Draft`, `Ready for review`, `Approved`, `Approved with changes`, `Blocked`, or `Complete`.
- Review date and reviewer, when known.
- Material discoveries.
- Decisions made.
- Changes required in later stages.
- Evidence reviewed.

Do not duplicate full discovery or decision details in every checkpoint. Put authoritative detail in the phase-wide logs and summarize only the stage impact.

## Stage 0 — Discovery

Use bounded spikes when technical or operational uncertainty could materially alter the target behavior or implementation.

For each spike record:

- Question
- Minimal experiment
- Evidence to collect
- Decision criteria
- Findings
- Recommended decision
- Effect on requirements, scenarios, tests, and phase scope
- Remaining uncertainty

A spike must not quietly become production implementation.

## Stage 1 — Behavior Contract

Treat documentation as a proposed behavior contract, not as proof of implemented behavior.

Produce or update:

- User documentation
- Administrator/operator documentation
- Scenario catalogue
- Permission and role matrix
- Error and recovery behavior
- Audit, privacy, and data-lifecycle effects
- Important examples and edge cases

Every scenario should include:

- Stable scenario ID
- Related requirement IDs
- Actors
- Preconditions
- Action
- Expected observable result
- Negative/authorization cases
- Recovery or reversal
- Audit/telemetry effects where relevant

Clearly distinguish existing behavior, approved target behavior, open decisions, and implementation assumptions.

## Stage 2 — Verification Design

Create a verification matrix mapping scenarios to evidence.

Implement before product code when valuable:

- Acceptance and contract test skeletons
- Authorization matrix tests
- Critical integration tests
- End-to-end test skeletons
- Test harness and fixtures required to exercise target behavior
- Migration and rollback checks

Implementation-specific unit tests may be written alongside code to avoid coupling tests to speculative internals.

Expected failing tests must fail for the intended missing behavior, not because the harness is broken. Record the expected failure evidence.

## Stage 3 — Implementation

Implement milestone by milestone:

1. Stable contracts and schemas
2. Thin end-to-end walking skeleton
3. Main successful workflow
4. Authorization and validation
5. Failure and recovery behavior
6. Operational controls and observability
7. Edge cases
8. Documentation verification preparation

For each milestone, record affected paths, commands, expected observations, retry/recovery behavior, and validation evidence.

## Stage 4 — Conformance and Closure

Verify the original behavior contract against the implemented system:

- Exercise documented examples.
- Correct commands, labels, messages, and screenshots or mark them for capture.
- Verify permissions and failure behavior.
- Verify administrator recovery procedures.
- Run complete automated and manual validation.
- Complete migration, rollout, rollback, and recovery guidance.
- Update roadmap and traceability statuses.
- Complete final outcomes and retrospective.

## Acceptance evidence

For each material behavior specify:

- Initial state
- User/operator/system action
- Expected observable result
- Negative and authorization behavior
- Automated test evidence
- Manual validation, when necessary
- Evidence location or command output summary

## Completion rule

A phase is complete only when:

- Included requirements are implemented or have an explicit disposition.
- Approved behavior scenarios match the implementation.
- Acceptance criteria have evidence.
- Required tests and checks pass.
- Documentation is verified and current.
- Migration, rollout, rollback, and recovery instructions are usable.
- No unresolved blocker remains in phase scope.
- Roadmap, traceability, and ExecPlan statuses agree.
