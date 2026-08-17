# Plan — 0124 One token for two resources is a conditional read against the wrong thing

## Scope

`VCSX-SPEC.md`: Section 8.1 "Entry Points and Arguments" (the second validator), Section 8.2 "Result
Envelope" (the second returned value), Section 9.1 "VCS Backend Plugin" (the which-reads-carry-a-validator
paragraph), Section 9.2 "Forge Backend Plugin" (the prohibition), Sections 13.1, 13.2.

## Steps

1. **`checks_state_validator`.** Ensure Section 8.1 defines an OPTIONAL argument carrying the
   validator a previous invocation's `checks_state` read returned, presented on each `await_checks`
   read, with `Default: unset — an unconditional first read`. Done-condition: the argument exists and
   names its resource.

2. **`pr_state_validator` is scoped to its own resource.** Ensure its entry states that it is
   presented on the `status` read alone, and no longer on each `await_checks` read. Done-condition: no
   argument is presented to a capability that did not issue it.

3. **The second returned value.** Ensure Section 8.2 returns the `checks_state` validator alongside
   the pull-request one, each attached to the data it describes, so the round trip closes for both
   from Sections 8.1 and 8.2 alone. Done-condition: every validator an invocation can present has a
   stated place it came from.

4. **The engine carries the obligation.** Ensure Section 9.2's `unchanged` prohibition gains the
   clause that the engine MUST NOT present a validator issued for another resource, and states why
   the obligation is the engine's: which resource issued a token is what the engine knows and the
   backend cannot check, holding an opaque value it was handed. Done-condition: the obligation sits on
   the party that can meet it.

5. **The which-reads-carry-a-validator paragraph.** Ensure Section 9.1's paragraph covers
   `checks_state` rather than deriving the rule from `pr_state`'s readers alone: `checks_state` has one
   reader, conditions no write, and carries its own validator. Done-condition: both capabilities are
   settled by the sentence that decides the question.

6. **Sections 13.1, 13.2.** Ensure the test matrix checks that an `await_checks` presents the
   `checks_state` validator and not the pull-request one; that the validator an `await_checks`
   returned is the value a later invocation presents, so a parked-and-resumed wait stays cheap across
   invocations; and that a `status` and an `await_checks` in one consumer loop each carry their own.
   Ensure the checklist's conditional-read bullet names both. Done-condition: steps 1, 2 and 3 each
   have a check, and the cross-invocation saving is asserted rather than only the within-invocation
   one.

## Cross-cutting sync

Section 13.3's conditional-read row is the one issue #67 asks for (decision 0128); ensure it is worded
to cover the mechanism for **both** validators rather than `pr_state`'s alone, so the two decisions
do not each add a row for half the obligation.

Section 8.5: additive, so a `MINOR`.

`SPEC.md`: Section 9.10's awaiting-required-checks bullet says the engine "already reads conditionally
where the forge supports it"; ensure nothing there implies one validator, and that a parked issue's
next `await_checks` presents what the previous one returned.

## Anchor changes

New anchor: the `checks_state_validator` argument, and the `outputs` value it round-trips through.
`pr_state_validator` is unchanged in spelling and in meaning, and narrowed in where it is presented.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.1, 8.2, 9.1, 9.2, 13.1, 13.2, 13.3).
