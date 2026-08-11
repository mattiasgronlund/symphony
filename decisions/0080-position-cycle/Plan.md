# Plan — 0080 A cycle of lifecycle positions is refused at validation

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set", 5.6 "Flow Bound and Termination", 6.10 "Validation",
13.1 "Test Matrix", 13.2 "Implementation Checklist".

`conformance/vcsx/vocabulary.json`: one `config_reasons` entry, `position_cycle`.

`conformance/vcsx/vectors/policy-validation.json`: four vectors, two refused and two accepted, and
Sections 4.1 and 5.6 added to the file's `spec_refs`.

`conformance/vcsx/README.md`: the vector count, the slice's growth history, and the sections
`policy-validation.json` is derived from.

No section is added, removed, or renumbered.

One configuration reason, no operation reason and no `need` token. Section 8.5 admits a new
configuration reason in a `MINOR` and Section 6.10 states that it is absorbed by the
`usage_or_config` status without an existing class edge, so no consumer changes to receive it. Step 6
verifies that Sections 4.3 and 8.4 are unchanged.

No `VCSX-CONTRACT.md` edit. Section 14 requires shared tokens to be spelled identically; the contract
carries no configuration-reason registry, so the token is not shared surface. Step 6 verifies.

No `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit. Its Section 2 mirrors Section 13.2 at a coarser
grain and enumerates no configuration reason. Step 6 verifies.

No `SPEC.md` edit. Symphony reads the engine's `usage_or_config` status and its reason; a new reason
under a status that does not change reaches it without a consumer change.

## Steps

1. **Section 6.10 carries the reason.** Ensure the validation table has a row reading a cycle of
   lifecycle positions, each position's `run_op` edge dispatching the operation the next position
   gates, so no operation on the cycle can run (Sections 4.1, 5.6) → `position_cycle`, placed among
   the consistency failures beside `duplicate_transition` rather than among the first three
   well-formedness rows. Done when the table names the condition and the surrounding prose's
   "first three conditions are well-formedness failures" sentence still reads true.

2. **Section 6.10 states the boundary against the bound.** Ensure the prose after the table states
   that `position_cycle` names a policy that cannot run rather than one that might not converge; that
   a position is matched exactly, has no class fallback and binds at most one edge, so a `run_op`
   edge bound to a position is taken whenever the position runs and such a cycle reaches no operation
   on any traversal; that a cycle passing through a typed operation result is not this condition and
   is not refused, because a result reports state outside the engine and the next traversal may
   differ; and that the check is over the `before:<op>` positions the engine defines and the `run_op`
   edges bound to them, a policy being refused where any from-context yields such a cycle, with a
   scoped edge selected over an unscoped one for the same trigger (Section 5.4). Done when a reader
   who has just read Section 5.6's cycle paragraph finds the two rules reconciled rather than in
   tension.

3. **Section 5.6 states the one shape it does not bound.** Ensure the paragraph that introduces the
   bound no longer says that a `run_op` edge at `before:<op>` naming that same operation is a loop the
   bound ends as it ends any other, and states instead that a cycle of lifecycle positions is refused
   before it runs as a configuration error (`position_cycle`, Section 6.10) while the bound holds
   every loop that runs operations. Ensure the "not a cycle detector" paragraph keeps its three
   defended routings and gains the sentence that makes its own measure the reason for the boundary:
   a cycle made only of positions takes no operations, so the count measures nothing that could
   converge, where each defended pair takes one per turn and ends when the state it reports settles.
   Done when Section 5.6 defends the same routings it defends today and no longer claims this shape.

4. **Section 4.1 names the corollary where the dispatch rule is stated.** Ensure the paragraph
   stating that a gated operation's position runs as part of dispatching it closes by noting that a
   `[policy]` edge binding a position to a `run_op` of an operation the cycle of positions returns to
   therefore names a dispatch that reaches no operation, and that Section 6.10 refuses the policy
   carrying it. Done when a reader who learns the dispatch rule learns its one refused consequence in
   the same place, in one sentence.

5. **The corpus asserts both sides of the boundary.** Ensure
   `conformance/vcsx/vectors/policy-validation.json` carries: a one-position cycle refused with
   `position_cycle`; a two-position cycle, where no edge names the operation its own position gates,
   refused with the same reason; a position edge to an operation that position does not gate accepted
   as valid; and a cycle through a typed operation result — `before:push` → `run_op integrate`,
   `integrate:ok` → `run_op push` — accepted as valid. Ensure the file's `spec_refs` names Sections
   4.1 and 5.6. Done when an engine that derived the narrow "its own position" predicate fails a
   vector, and an engine that refuses cycles generally fails a different one.

6. **Cross-cutting sync.** Ensure Section 13.1's termination check covers the refusal at validation
   and the accepted cycle through a typed result alongside the existing bound checks; ensure Section
   13.2's validation bullet names the refusal; add `position_cycle` to
   `conformance/vcsx/vocabulary.json` under `config_reasons`; update
   `conformance/vcsx/README.md`'s vector count, its parenthetical history of the slice's growth, and
   the sections `policy-validation.json` is derived from; and verify that Sections 4.3 and 8.4,
   `VCSX-CONTRACT.md` and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` are unchanged. Done when the
   matrix, the checklist, the vocabulary and the corpus README agree with Sections 5.6 and 6.10.

7. **Decision 0078 records the revisit.** Ensure `decisions/0078-dispatch-runs-the-position/`
   `Background.md` carries an append-only note that its incidental refusal of static detection is
   revisited by 0080, with the reason the refusal does not reach this shape, and that 0078's chosen
   option is untouched. Done when a reader of 0078 is not left with a conclusion the specification no
   longer holds.

## Cross-cutting sync

- Section 13.1 test matrix — Step 6.
- Section 13.2 implementation checklist — Step 6.
- `conformance/vcsx/vocabulary.json` — Step 6, one `config_reasons` entry added.
- `conformance/vcsx/vectors/policy-validation.json` — Step 5, four vectors added.
- `conformance/vcsx/README.md` — Step 6.
- Sections 4.3 and 8.4, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — verified
  unchanged, Step 6.

## Anchor changes

- **Added:** `position_cycle` — the Section 6.10 configuration reason for a cycle of lifecycle
  positions dispatching one another.
- **Removed:** the Section 5.6 sentence stating that a `run_op` edge at `before:<op>` naming that same
  operation is a loop the bound ends as it ends any other (added by decision 0078). The claim is
  replaced rather than the anchor renamed; no code-token identifier is removed.
- No anchor is renamed.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 5.6, 6.10, 13.1, 13.2),
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/policy-validation.json`,
`conformance/vcsx/README.md`, and `decisions/0078-dispatch-runs-the-position/Background.md`.
