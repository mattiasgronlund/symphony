# Plan — 0077 A merge lands the head it read, or reports `merge:head_moved`

## Scope

`VCSX-SPEC.md`: Sections 4.3 "Reason-Token Registry", 5.6 "Flow Bound and Termination", 7.2 "`land`",
9.2 "Forge Backend Plugin", 12.3 "`land` Sequence", 13.1 "Test Matrix", 13.2 "Implementation
Checklist".

`conformance/vcsx/vocabulary.json`: one `reasons` entry, `merge:head_moved`, class `needs_caller`.

No section is added, removed, or renumbered.

No `need` token. The routing is built in (Step 4), so `merge:head_moved` ends an invocation only where
a repository binds it to an edge that does, and that edge names its own `escalate` reason. Section
8.4's vocabulary is unchanged; Step 7 verifies.

No `VCSX-CONTRACT.md` edit. Section 14 requires shared tokens to be spelled identically; the contract
defers the exhaustive per-operation reason registry (its Sections 5.5, 6, 11) and names no Section 9.2
capability, so neither the token nor the signature is shared surface.

No `SPEC.md` edit. Symphony branches on the engine's classes through the `#class` fallback, and a new
`needs_caller` reason lands on the edge it already has.

Depends on 0076, which lands first: `expected_head` is read from `pr_state`, whose answer 0076 widens.

## Steps

1. **The registry carries the reason.** Ensure Section 4.3's table has a `merge` / `head_moved` row,
   class `needs_caller`, glossed "The pull request's head advanced after it was read; re-read then
   retry", placed between `merge:conflict` and `merge:rejected`. Done when the condition has a token
   whose class is the one a caller acts on.

2. **Section 4.3 states why it is neither neighbour.** Ensure the prose following the table states
   that `merge:head_moved` and `push:non_fast_forward` name one condition on two operations — what was
   to be written to moved between the decision to write and the write — that neither is a conflict
   (the branches merge cleanly, and `merge:conflict` sends a caller to resolve what does not exist)
   nor a refusal (`merge:rejected` names branch protection, and reporting a moved head under it sends
   an operator to read a rule nobody wrote), that the two differ only in the recovery each gloss names
   and therefore in where each routes, and that the universal `failed` does not carry it because
   `failed` is class `error` and this is a state a caller acts on. Done when a reader who finds two
   near-miss reasons finds the reason they are not used.

3. **`request_merge` takes the head it must land.** Ensure Section 9.2's `request_merge` bullet reads
   `request_merge(pr, strategy, expected_head)`, that `expected_head` is the head `pr_state` answered
   when the pull request was read at `before:merge`, that the capability MUST NOT merge a pull request
   whose head is no longer `expected_head` and reports `merge:head_moved`, that the mechanism is the
   backend's and a backend whose forge offers no means of conditioning the merge does not declare the
   capability (Section 9.3), and that where `pr_state` could not determine the head there is no
   `expected_head` to supply and the operation reports `merge:failed` rather than merging blind.
   Done when the merge that succeeds is constrained, not only the merge that is refused.

4. **`land` loops.** Ensure Section 12.3's pseudocode re-runs `before:merge`, passes
   `expected_head`, continues on `merge:head_moved`, and checks the flow bound each turn, returning
   `flow_exhausted` when it is reached. Ensure the prose states that the routing is the built-in
   default a repository's edges override; that the retry re-enters the lifecycle position rather than
   the operation alone, because `before:merge` is where the pull request is read and where
   `pr_to_squash` runs, so a retry that re-merged without re-gating would merge a head no position
   inspected; and that because the routing is built in the condition adds a reason token and no `need`
   token. Done when `land` converges on the head it inspected or stops at the bound.

5. **`land`'s description matches its sequence.** Ensure Section 7.2 states that `land` merges the
   head it read, that nothing is merged where the head advances between the read and the merge, and
   that it re-reads and retries within the flow bound. Ensure the existing material — the configured
   strategy, `pr_to_squash`, transforms-never-authors, the refusal of a pull request that is not open
   or whose checks have not passed — is unchanged. Done when the front-end section and the reference
   algorithm agree.

6. **Section 5.6 names the second built-in loop.** Ensure the "count, not a cycle detector" paragraph
   names `merge:head_moved → before:merge → merge` beside `push:non_fast_forward → integrate → push`,
   so a repeated `(trigger, edge)` pair remains ordinary rather than pathological for both. Done when
   the bound's rationale covers both loops the engine ships.

7. **Registry and matrix.** Ensure `vocabulary.json` carries `merge:head_moved` under `reasons` with
   class `needs_caller` and that `needs` is unchanged; ensure Section 13.1 asks that a `merge` whose
   head advanced yields `head_moved` rather than `conflict`, `rejected` or `failed`, that a `pr_state`
   that could not determine the head yields `merge:failed` rather than an unconditioned merge, and
   that `land` re-reads, re-gates and retries so a squash message is transformed from the revision
   actually merged, with a head that moves between every attempt ending at the flow bound; ensure
   Section 13.2's checkout item names the conditional merge. Done when an engine cannot pass the
   matrix while merging a head no position inspected.

## Cross-cutting sync

`CLAUDE.md` names the `SPEC.md` cross-cutting sections; this decision changes `VCSX-SPEC.md`, whose
counterparts are Sections 13.1 and 13.2 (Step 7). Section 13.3 is unchanged: no `Implementation-defined`
site is added, and the token is in the registry rather than beyond it.

`conformance/vcsx/README.md`'s `reasons` normalization count moves to 33 rows / 51 entries, and its
deferred-coverage entry covers `merge:head_moved`; both are made in 0076's change, which lands with
this one.

## Anchor changes

- `request_merge(pr, strategy)` → `request_merge(pr, strategy, expected_head)` (Section 9.2). The
  capability keeps its name; a third argument is added.
- Added: the reason token `merge:head_moved` (Section 4.3).

## Status

Applied to `VCSX-SPEC.md` (Sections 4.3, 5.6, 7.2, 9.2, 12.3, 13.1, 13.2) and
`conformance/vcsx/vocabulary.json`.
