# Plan — 0012 Token budget guards

## Scope

Adds a new OPTIONAL token-budget extension. Touches Failure Classes (Section 14.1, new category),
Concurrency Control and Retry/Backoff (Sections 8.3, 8.4), the orchestration state machine (Section 7,
park/blocked state), and the durable counter source (Section 13.5 plus decisions 0010/0011). Config
keys live under the extension's namespace (`budget.*`). Depends on 0010 (class D) and 0011 (ledger
re-seed).

## Steps

1. Ensure a token-budget extension is specified as OPTIONAL with token as the unit of account. Done
   when the extension exists, is marked OPTIONAL, and the unit is stated.
2. Ensure three budget scopes with distinct exhaustion semantics: per-session and per-issue caps abort
   the run and requeue that single issue; a global cap pauses new dispatch while in-flight runs
   continue. Done when both semantics and their scopes are specified.
3. Ensure budget exhaustion is its own failure category `token_budget_exceeded` (added to "Failure
   Classes", Section 14.1) routed to a park/blocked state and kept OUT of the exponential
   retry/backoff path ("Retry and Backoff", Section 8.4). Done when the category is listed and the
   state machine routes it to a non-retry park.
4. Ensure each cap has an OPTIONAL soft warning threshold `*_warning_pct` (Default: `80`) that emits a
   one-shot warning signal. Done when the soft threshold and its default are specified.
5. Ensure budget counters are class D (decision 0010): durable, re-seeded from durable spend (or the
   0011 ledger) before any enforcement decision, idempotent under restart, keyed by absolute snapshot.
   Done when the durability and idempotent-resume requirement is stated and cross-referenced.
6. Ensure the global pause is expressed as a dispatch gate composing with Concurrency Control (Section
   8.3): a paused scope yields zero new slots and running agents are not terminated. Done when the gate
   is specified alongside concurrency control.
7. Ensure an OPTIONAL constrained recovery is specified: on a cap breach, retry once through a narrow
   handoff iff fresh local progress exists, else park; a second breach without new progress parks
   terminally. Done when the handoff path is specified as OPTIONAL.
8. Ensure the tripwire nature is documented: caps are evaluated against observed cumulative usage and
   may overshoot by one report; estimate-based pre-authorization is a separate advisory OPTIONAL not
   required here. Done when the boundary note exists.
9. Ensure a cost/currency overlay is recorded as explicitly deferred: a note states dollars-as-unit
   and a per-model pricing table (input/output rate, currency) as an Implementation-defined future
   layer over token counts, with the missing-pricing policy (fail-open vs fail-closed) called out.
   Done when the deferral note exists.
10. Ensure config keys are specified under `budget.*` with defaults (caps default unlimited/disabled;
    `*_warning_pct` default `80`). Done when the keys and defaults are present.

## Cross-cutting sync

- Config cheat sheet (6.4): note the budget extension owns `budget.*`; document the keys in the
  extension subsection.
- Failure classes (14.1): add `token_budget_exceeded`.
- Test matrix (17): add `Extension Conformance` rows under 17.4 — per-issue cap aborts+requeues; global
  cap pauses dispatch; a budget abort is not retried via backoff; the durable counter is re-seeded
  idempotently on restart; the soft warning fires once.
- Checklist (18): add the token-budget-guards extension to 18.2.

## Anchor changes

- New anchors: failure category `token_budget_exceeded`; the budget park/blocked state; config keys
  `budget.*` and `*_warning_pct`.
- Depends on anchors introduced by 0010 (class D) and 0011 (the usage ledger).

## Status

Not started. Decision drafted; not yet applied to `SPEC.md`.
