# Plan — 0010 State recovery model and class taxonomy

## Scope

Adds a cross-cutting state-recovery taxonomy and a per-field classification obligation. Touches the
Orchestrator Runtime State (Section 4.1.6/4.1.8 fields), Idempotency and Recovery Rules (Section 7.4),
Partial State Recovery (Section 14.3), Service Startup (Section 16.1), and the rate-limit tracking in
Session Metrics and Token Accounting (Section 13.5). No new core config keys: classes C and D are
exercised by the extensions that own them (0013, 0012). Prerequisite for decisions 0011, 0012, 0013.

## Steps

1. Ensure a state-recovery taxonomy is defined with exactly four classes — `Reconstructable` (R),
   `Ephemeral` (E), `Cached external signal` (C), `Durable` (D) — each with its restart and
   unknown-value contract, as a cross-cutting subsection (Section 7 or 14). Done when the four class
   names and their contracts are specified in one place and referenced from the recovery sections.
2. Ensure every field of the Orchestrator Runtime State ("Orchestrator Runtime State", Section 4.1.8)
   is assigned exactly one class and the assignment is documented. Done when each of
   `poll_interval_ms`, `max_concurrent_agents`, `running`, `claimed`, `retry_attempts`, `completed`,
   `codex_totals`, `codex_rate_limits` carries a class.
3. Ensure class R states that the external source of truth is authoritative and R fields MUST NOT be
   primary-persisted (reconstruct by reconciliation). Done when the rule is stated and `running` /
   `claimed` are marked R.
4. Ensure class E requires documenting the reset-at-startup consequence, and that `retry_attempts`
   (timers restart) and runtime/observability counters are marked E with their consequence. Done when
   stated.
5. Ensure class C requires: last-known-good carried across restart and across failed refresh; a
   staleness age that promotes a value to an explicit `UNKNOWN`; `UNKNOWN` represented distinctly from
   any in-band value (the spec states it MUST NOT be modeled as `0`); a configured policy on `UNKNOWN`
   (fail-open proceed vs fail-closed pause new dispatch); and MAY distinguish *unsupported* (permanent
   UNKNOWN) from *blocked* (transient UNKNOWN). Done when these are specified and `codex_rate_limits`
   is reclassified C.
6. Ensure class D requires durable, idempotent, re-seedable accounting restored before any enforcement
   read, keyed by absolute snapshot (not additive), with documented degradation when no store is
   configured. Done when stated.
7. Ensure Section 7.4 "Idempotency and Recovery Rules" and Section 14.3 "Partial State Recovery
   (Restart)" are reconciled with the taxonomy: the unqualified "without a durable orchestrator DB" /
   "intentionally in-memory" assertions become "R and E are the default; the durable class D is the
   narrow, OPTIONAL exception for accounting that cannot be reconstructed or safely lost". Done when
   both sections reference the taxonomy and no longer assert an unqualified no-durable-state rule.
8. Ensure Service Startup (Section 16.1) notes that class C and D fields are restored from their store
   when one is configured, rather than unconditionally zeroed. Done when the startup prose/pseudocode
   reflects restore-or-default for C/D fields.

## Cross-cutting sync

- Config cheat sheet (6.4): no core keys added; C/D config is owned by extensions 0012/0013.
- Test matrix (17): add a `Core Conformance` row under 17.4 that every Orchestrator Runtime State
  field has a documented recovery class; add `Extension Conformance` rows (where C/D are used) that
  `UNKNOWN` is never represented as `0` and that last-known-good survives restart.
- Checklist (18): reframe the Section 18.2 TODO "Persist retry queue and session metadata across
  process restarts" — the retry queue is class E by decision; session accounting is class D only under
  an enforcement extension. Add a class-taxonomy line to 18.1.

## Anchor changes

- `codex_rate_limits` (Section 4.1.8) reclassified from implicit-ephemeral to class `Cached external
  signal`; an absent value denotes `UNKNOWN`, not 0% utilization.
- Section 7.4 "Idempotency and Recovery Rules" — the "without a durable orchestrator DB" bullet
  qualified (not removed): R/E default, `Durable` the narrow OPTIONAL exception.
- New Section 14.3 "State Recovery Classes" inserted. The former 14.3 "Partial State Recovery
  (Restart)" renumbered to 14.4 (its "intentionally in-memory" wording qualified), and the former
  14.4 "Operator Intervention Points" renumbered to 14.5.
- New anchors: the recovery class names `Reconstructable` (R) / `Ephemeral` (E) / `Cached external
  signal` (C) / `Durable` (D); the `UNKNOWN` sentinel; the startup pseudocode function
  `restore_cached_and_durable_state` (Section 16.1).

## Status

Applied to `SPEC.md` (working tree on branch `main`; not yet committed).
