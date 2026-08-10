# Plan — 0074 The commit-identity precondition is scoped to the entry point

## Scope

`VCSX-SPEC.md`: Section 4.3 "Reason-Token Registry" (three rows and a boundary paragraph),
Section 8.4 "Escalation Payload" (one `need` token), Section 8.6 "Invocation Preconditions" (the
scope clause, a new paragraph, and the closing rule), and Section 13.1 "Test Matrix".

`conformance/vcsx/vocabulary.json` (`reasons`, `needs`, `precondition_reasons`),
`conformance/vcsx/vectors/identity-precondition.json` (new), and `conformance/vcsx/README.md`.

No edit to `VCSX-CONTRACT.md`: it defers the per-operation reason registry and names no `need` token
(its Sections 5.5, 6, 11), so `identity_missing` and `supply_identity` add nothing it spells. Under
Section 14 the tokens would have to match if it spelled them; it does not.

No edit to `SPEC.md`: Symphony supplies the commit identity from operator configuration (`vcs.author`,
Section 6.4) on every invocation, so it never reaches `identity_missing`, and a `needs_caller` result
it did reach is absorbed by the `#class` fallback it already documents.

No edit to `VCSX-SPEC.md` Section 9.1: `accepts_identity` is still asked only before the policy runs,
because a supplied identity is judged at entry whatever the entry and only *absence* reaches a
dispatch. Its "asked before any operation is dispatched" clause stays true.

No edit to Sections 12.2 or 12.3: `ship` already takes `identity` and `land` already takes none, which
is the scope this decision states.

No edit to Section 13.2: the checklist's "operation set and the reason-token registry" and "invocation
contract … invocation preconditions" bullets already cover both halves.

No edit to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: its tables record reasons and `need`s an engine
adds *beyond* the registries, and this decision adds to the registries themselves.

## Steps

1. **`identity_missing` is a reason of the three commit-writing operations.** Ensure the Section 4.3
   registry table carries a row for each of `commit`, `integrate` and `pull` with reason
   `identity_missing`, class `needs_caller`, each in its own operation's group, the `integrate` and
   `pull` meanings naming the merge commit. Done when a reader of the table alone finds a reason for
   an absent identity under every operation that writes a commit and under no other.

2. **The boundary between `identity_missing` and `identity_invalid` is stated once.** Ensure Section
   4.3 carries a paragraph, after the one distinguishing `base_unresolved` from `base_unavailable`,
   stating that the two name one condition at two points with the first dispatch as the boundary; that
   an entry the precondition covers never reaches `identity_missing`; that an entry it does not cover
   MAY reach a commit-writing operation through a `run_op` edge and that the result routes like any
   other; and that only absence reaches a dispatch, because a supplied identity is judged for shape
   before the policy runs whatever the entry. Done when a consumer can predict which of the two tokens
   an invocation yields from the entry point alone.

3. **`supply_identity` is in the `need` vocabulary.** Ensure Section 8.4's example `need` list carries
   `supply_identity` among the resolvable needs, before `intervention` and `flow_exhausted`. Done when
   a front-end binding resolvers by `need` token has one to bind for this condition.

4. **A supplied commit identity is judged whatever the entry.** Ensure Section 8.6's first paragraph
   states that where the caller supplied a commit identity the engine accepts it with
   `accepts_identity`, that the shape is judged whatever the entry so no invocation carries a
   malformed identity into the policy, and — separately — that for an entry that can write a commit
   an identity is REQUIRED and its absence is refused there. Done when "absent" and "malformed" are
   two clauses with different scopes rather than one clause covering both.

5. **The scope is the entry point.** Ensure Section 8.6 carries a paragraph stating that a front-end
   sequence that dispatches one means the sequence's own dispatches (Sections 12.2, 12.3), so `ship`
   requires an identity and `land` does not and a policy's `run_op` edges do not widen the set; that
   an entry outside the set MAY still reach a commit-writing operation because a policy is a graph;
   that this is not judged from the invocation's arguments and the checkout but from a path the policy
   might take; and that the dispatched operation reports `identity_missing` instead, which is the
   disposition Section 9.3 already gives an unsupported capability. Done when the question issue #23
   asks is answered by the text rather than by inference from it.

6. **The closing rule names a reason rather than a counterfactual.** Ensure Section 8.6's rule reads
   that an engine MUST NOT report a precondition reason for a condition an operation *has a reason
   that names*, with the first dispatch as the boundary, followed by the note that the universal
   `failed` reason does not satisfy that test because it names no condition — reading it as one would
   make every precondition reportable as `<op>:failed` and leave the registry nothing to name. Done
   when the rule no longer argues against the registry it closes.

7. **The test matrix carries both halves.** Ensure Section 13.1's invocation-contract bullet, after
   the `accepts_branch_name` / `accepts_identity` clause, states that an entry the identity
   precondition does not cover — a `status` whose policy routes `status:ok` to `run_op` `commit` —
   runs the policy and reports `commit:identity_missing`, class `needs_caller`, rather than a
   precondition reason, and that a malformed identity supplied to that same entry is refused before
   the policy runs. Done when the two dispositions are separately testable.

8. **The vocabulary carries the new tokens.** Ensure `conformance/vcsx/vocabulary.json` holds
   `commit:identity_missing`, `integrate:identity_missing` and `pull:identity_missing` in `reasons`
   with class `needs_caller`; `supply_identity` in `needs` with `raised_by: "escalate"` and
   `resolvable: true`; and a `precondition_reasons` meaning for `identity_invalid` that states the
   scope of "absent", the entry-independence of "malformed", and where an uncovered entry's absence
   lands instead. Done when the registry and Sections 4.3, 8.4 and 8.6 agree token for token.

9. **A vector file pins the scope.** Ensure `conformance/vcsx/vectors/identity-precondition.json`
   exists with `function: "requires_commit_identity"`, `given` an entry point and the policy the
   invocation would run, and `expect` whether an identity is required: `true` for `commit`,
   `integrate`, `pull` and `ship`; `false` for `status`, `diff`, `push`, `create_pr`, `merge` and
   `land`; and two vectors asserting that a `run_op` edge to `commit` from `status:ok` and to
   `integrate` from `push:non_fast_forward` leave the answer `false`. Its notes MUST record that a
   `false` answer does not mean no commit is written, and that whether a supplied identity is well
   formed is a backend judgement deferred with the rest of plugin behavior. Done when the reading
   issue #23 asks about is a pass/fail rather than a sentence.

10. **The corpus README describes what it now holds.** Ensure `conformance/vcsx/README.md` lists the
    new file in its coverage table, states the corrected vector total and reason-entry normalization
    counts, and narrows its "Invocation preconditions" deferral to the half a vector cannot supply.
    Done when the README's counts match the files and no deferral claims coverage that now exists.

## Cross-cutting sync

Section 13.1's invocation-contract bullet (step 7). Section 13.2 needs no edit; Section 6.4 is
`VCSX-SPEC.md`'s `[base]` section and is untouched — the config cheat sheet this repository's working
agreements name is `SPEC.md`'s, and no `SPEC.md` configuration key changes.

`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md` (steps 8, 10). The README's
normalization sentence and vector total were both stale by decision 0073's two reason rows before this
change; they are corrected to the counts after it — 32 table rows yielding 50 entries, and 75 vectors.

## Anchor changes

Added: `identity_missing` (Section 4.3 reason, for `commit`, `integrate` and `pull`),
`supply_identity` (Section 8.4 `need`), `requires_commit_identity`
(`conformance/vcsx/vectors/identity-precondition.json` function).

No token renamed or removed. `identity_invalid` keeps its spelling, its class-free status and its
Section 8.6 row; only the scope of "absent where the entry requires one" is made explicit.

## Status

Applied to `VCSX-SPEC.md`, `conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`, and
`conformance/vcsx/vectors/identity-precondition.json`.
