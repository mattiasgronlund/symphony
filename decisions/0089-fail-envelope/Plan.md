# Plan — 0089 `fail` gets the envelope `park` has, and `fail(reason)` is the repository's token

## Scope

`VCSX-SPEC.md`: Sections 5.2 "Actions", 6.5 "`[policy]` Edges", 8.2 "Result Envelope", 13.1 "Test
Matrix", 13.2 "Implementation Checklist". `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/compose-envelope.json` and `conformance/vcsx/README.md`.

No `VCSX-CONTRACT.md` change: `VCSX-CONTRACT.md` Section 5.2 spells `fail` identically and describes
no envelope, which is deferred to this document (`VCSX-CONTRACT.md` Section 11).

## Steps

1. **The fourth null case (Section 8.2)** — ensure the null list carries a flow the policy failed with
   `fail` (Section 5.2) alongside the clean `ok`, the parked flow and the flow stopped at its bound.
   Ensure the rule is stated over the class: a `fail` reports the decisive result where the run has one
   whose class is `error`, and nulls all three otherwise — a `needs_caller` or `done` result, or a
   lifecycle position, which has no outcome at all (Section 5.1). Ensure the prose states why the split
   is where it is: the classes agree in the first case so the invariant above holds unchanged, and an
   explicit `#error → fail` edge then reports what the built-in `error` default reports for the same
   flow, which is itself a `fail` (Section 5.4).
   *Done when* the fourth case exists, is scoped by class, and the existing sentence about the middle
   two cases ("In neither of the last two did an operation ask the caller for anything") still names
   the cases it was written for.

2. **`fail(reason)`'s argument (Section 5.2)** — ensure the `fail` bullet states that the invocation
   ends at `error` and that the edge's `reason` is a repository-authored token, reported in `message`
   and in `outputs` (Section 8.2) rather than in the envelope's `reason` field.
   *Done when* the bullet names where the argument goes and where it does not.

3. **`failed_by_policy` (Section 8.2)** — ensure `outputs` carries `failed_by_policy` where the policy
   ended the flow with `fail`: the `trigger` the edge fired on and the `reason` the edge wrote; absent
   where no `fail` ran. Ensure the prose states why the token is not in `reason`: that field carries an
   operation reason (Section 4.3), a configuration reason (Section 6.10) or a precondition reason
   (Section 8.6), each from a registry a consumer branches on, and a repository-authored value there
   would be indistinguishable from an engine one.
   *Done when* the key exists with its two fields, its absent rule, and the namespace argument.

4. **`reason` is OPTIONAL on a `fail` edge (Section 6.5)** — ensure the section states that a `fail`
   edge MAY carry a `reason` and that an edge omitting it is well formed, so the existing
   argument-completeness rule — `op` for `run_op`, `hook` for `run` — is not read as requiring one.
   Ensure `failed_by_policy` is stated to carry the trigger regardless and the reason where the edge
   wrote one. *Done when* Section 6.5 says the key is OPTIONAL and Section 8.2's key tolerates its
   absence.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Invocation contract" — a `fail` on an `error`-class result
  reports that result with `status` `error`; a `fail` on a `needs_caller` result, on a `done` result,
  and at a lifecycle position each yield `status` `error` with null `op`/`reason`/`class` and report
  the edge's trigger and reason in `failed_by_policy`, rather than an `ok` envelope for a failed flow;
  a `fail` edge carrying no `reason` is well formed and reports the trigger alone.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line so the envelope
  covers a policy-failed flow.
- **Conformance Statement (Section 13.3)** — no new row: the envelope shape and the key are fixed
  rather than `Implementation-defined`.
- **`conformance/vcsx/vocabulary.json`** — add `failed_by_policy` to the `output_keys` group decision
  0086 introduces, with its two fields; annotate the `fail` action entry so `reason` is recorded as
  OPTIONAL and repository-authored rather than a registry token.
- **`conformance/vcsx/vectors/compose-envelope.json`** — a new vector file over `compose_envelope`,
  carrying the five `fail` rows the report enumerated plus the `park` and flow-bound rows they are
  argued against, so the three shapes that broke stay asserted. Shared with decisions 0088 and 0090,
  which contribute the undisposed-outcome and `entry`-nullability rows; record it in
  `conformance/vcsx/README.md`'s coverage table and vector count.

## Anchor changes

New code token: `failed_by_policy` (an `outputs` key). No existing anchor is renamed or removed;
`fail` keeps its name and its argument.

## Status

Applied to `VCSX-SPEC.md`.
