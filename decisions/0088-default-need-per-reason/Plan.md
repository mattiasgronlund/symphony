# Plan — 0088 An outcome no action disposed of takes the default, and the registry carries each need

## Scope

`VCSX-SPEC.md`: Sections 4.3 "Reason-Token Registry", 5.2 "Actions", 5.4 "Unmatched Policy and
Determinism", 8.4 "Escalation Payload", 12.3 "`land` Sequence", 13.1 "Test Matrix", 13.2
"Implementation Checklist". `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/compose-envelope.json` and `conformance/vcsx/README.md`.

`VCSX-CONTRACT.md`: Section 5.4 "Unmatched Policy", whose fail-safe clause is the contract's spelling
of the rule this decision widens (Section 14's alignment rule).

## Steps

1. **`Default need` column (Section 4.3)** — ensure the registry table carries a `Default need` column
   giving each `needs_caller` reason the need an escalation carries where nothing named one:
   `blocked` → `human_review`; `commit:worktree_moved` → `reread_then_retry`;
   `commit:identity_missing` → `supply_identity`; `integrate:merge_conflicts` → `resolve_conflicts`;
   `integrate:identity_missing` → `supply_identity`; `push:non_fast_forward` → `integrate_then_retry`;
   `push:pr_closed` → `human_review`; `create_pr:conflict` → `human_review`; `merge:not_open` →
   `human_review`; `merge:checks_pending` → `await_checks`; `merge:conflict` → `resolve_conflicts`;
   `merge:head_moved` → `reread_then_retry`; `pull:conflict` → `resolve_conflicts`;
   `pull:identity_missing` → `supply_identity`. Ensure every `done` and `error` row carries `—`.
   *Done when* the column exists, the fourteen `needs_caller` rows carry a need each, and the mappings
   agree with Section 12.2's routing where that routing fixes one.

2. **What the column is (Section 4.3)** — ensure prose after the table states that the column names the
   need an escalation on that result carries where nothing in the policy named one, that the built-in
   default for the class (Section 5.4) has no `escalate(reason)` to take a need from, and that a
   front-end binds its resolvers by the `need` token (Sections 5.5, 8.4) — so a need each engine
   derived independently would offer one driver a different resolver key on every engine. Ensure the
   prose states that a policy edge naming its own `escalate(reason)` supplies the need instead, so the
   column is a default rather than a constraint on what a repository may raise.
   *Done when* the column's meaning, its scope and its overridability are stated.

3. **`reread_then_retry` (Sections 4.3, 8.4)** — ensure the need vocabulary in Section 8.4 carries
   `reread_then_retry`, and Section 4.3 states why the two moved-state reasons take it rather than
   `human_review`: the state moved between the read and the write and the repair is to read it again,
   which is the re-entry a resume already performs (Section 5.5). Ensure Section 8.4's closing sentence
   still holds over the widened vocabulary — every need other than the two holds names something a
   caller can supply **or an action it can take**.
   *Done when* the token is in Section 8.4's enumeration, Section 4.3 carries the rationale, and
   Section 8.4's "every other need" sentence admits a need met by acting rather than supplying.

4. **The disposition rule (Section 5.4)** — ensure the fail-safe bullet is stated over an operation
   outcome **no action disposed of** rather than over an unmatched one, keeping the existing MUST and
   its reason. Ensure the bullet states what disposes of an outcome: an action that ends the flow —
   `escalate`, `park`, `fail` (Section 5.6) — or a `run_op` whose own result takes its place in the
   machine. Ensure it states that the remaining actions emit an intent or run a hook and return, so an
   outcome that matched one of them reaches the same built-in default an unmatched outcome reaches.
   Ensure the built-in default for `needs_caller` names the reason's default need (Section 4.3).
   *Done when* the bullet quantifies over disposition, enumerates what disposes, and cites the registry
   for the need.

5. **An `escalate` with no `reason` (Section 5.2)** — ensure the `escalate` bullet states that an edge
   naming no `reason` raises the trigger's default need where the trigger is a `needs_caller` result
   (Section 4.3), and `human_review` otherwise, because an `error` or `done` result a policy chose to
   escalate names no remedy of its own and a lifecycle position has no outcome to take one from.
   *Done when* the fallback is stated and covers all three trigger kinds.

6. **Section 12.3's observation is scoped** — ensure the sentence stating that `merge:head_moved` adds
   a reason token and no `need` token is corrected: it reaches a caller through a bare `merge` entry
   point as well as through a repository's edge, and it now carries `reread_then_retry`
   (Sections 4.3, 8.4). *Done when* Section 12.3 no longer asserts the condition adds no `need` token.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Unmatched policy" — rename the group's first check to cover
  disposition: an operation outcome whose matched edge neither ends the flow nor dispatches an
  operation reaches the same built-in default an unmatched outcome reaches, so a
  `push:non_fast_forward → notify` edge under a single-operation entry point yields `needs_caller`
  with the reason's default need and the decisive result reported, rather than an `ok` envelope, a
  dropped result or a park; an escalation the built-in default raised carries the Section 4.3 default
  need for its reason; a `merge:head_moved` reached through a bare `merge` entry point escalates
  `reread_then_retry` rather than `human_review`.
- **Implementation checklist (Section 13.2)** — extend the action-policy-machine line so fail-safe is
  stated over an undisposed outcome, and the reason-registry line so it carries the default needs.
- **Conformance Statement (Section 13.3)** — no new row: the mapping is fixed rather than
  `Implementation-defined`. The `need` vocabulary an engine emits is already recorded there
  (Section 8.4), and an engine that adds a reason beyond Section 4.3's registry now records its default
  need with it, which the existing "any reason token the engine adds beyond a registry" row covers.
- **`conformance/vcsx/vocabulary.json`** — add `reread_then_retry` to `needs` with
  `raised_by: "escalate"` and `resolvable: true`; add a `default_need` field to each `needs_caller`
  entry in `reasons`, and `null` on the rest.
- **`VCSX-CONTRACT.md` Section 5.4** — restate the fail-safe bullet over an operation outcome no action
  disposed of, matching the spec's spelling (Section 14).
- **`conformance/vcsx/vectors/compose-envelope.json`** — contribute the undisposed-outcome rows to the
  vector file decision 0089 introduces: a `needs_caller` result no action disposed of reports the
  result and escalates its default need, a `merge:head_moved` reached through a bare entry point takes
  `reread_then_retry`, and an `error` result in the same position fails. The default need is read from
  the registry by the implementation rather than supplied by the vector, as `match_edge` derives a
  proto class rather than being told one.

## Anchor changes

New code token: `reread_then_retry` (a `need`). No existing anchor is renamed or removed. Section
12.3's sentence asserting that `merge:head_moved` adds no `need` token is removed as an assertion; the
reason token itself is unchanged.

## Status

Applied to `VCSX-SPEC.md`.
