# Plan — 0108 A throttle is not a failure, and retryable is a property of the need

## Scope

`VCSX-SPEC.md`: Section 4.3 "Reason-Token Registry" (two reasons, their class and default need, and
the prose that separates them), Section 8.2 "Result Envelope" (the diagnostic output), Section 8.4
"Escalation Payload" (the `retry_after` need and the `retryable` property), Section 8.5 "Versioning
and the Version Grammar" (the major-stable surface), Section 9.2 "Forge Backend Plugin" (which
capability answers them), Sections 13.1, 13.2, 13.3.

`VCSX-CONTRACT.md`: no change. Section 11 defers the concrete reason registry and the escalation
payload to the full spec, and the three proto classes it does fix are unchanged.

`conformance/vcsx/vocabulary.json`: the two reasons with their proto class and default need, and the
`retry_after` need with its `retryable` property — the registry already carries the reason and
`need` vocabularies.

## Steps

1. **Section 4.3 — the two reasons.** Ensure the registry carries `rate_limited` and
   `forge_unavailable`, each class `needs_caller` with default need `retry_after`, scoped to the
   operations whose forge call the condition prevented — `push` (through its `pr_state` read),
   `create_pr` and `merge`. Done-condition: a throttled `create_pr` has a reason that is not
   `failed`, and `grep` shows both tokens with class `needs_caller`.

2. **Section 4.3 — why the class is not `error`.** Ensure prose states that an `error`-class result
   no edge disposes of reaches the built-in default and **fails the flow** (Section 5.4), so
   carrying a throttle under `failed` ends a unit of work for a condition that clears on its own;
   and that `needs_caller` is the class Section 4.2 defines for an operation awaiting a caller
   action, waiting being one. Done-condition: the class is argued from the disposition it produces,
   not from taxonomy.

3. **Section 4.3 — why two reasons and not four.** Ensure prose states the split is by repair:
   `rate_limited` has an informed repair, its bucket and `resets_at` already in
   `outputs.forge_budget` (Section 8.2, decision 0107), and `forge_unavailable` an uninformed one.
   Ensure it states that the conditions inside `forge_unavailable` — a server error, an expired
   bound, a transport failure — carry one repair and are therefore diagnosis rather than routing,
   citing the same arrangement Section 4.3 already makes for `hook_unanswered`. Done-condition: a
   reader can tell why a 503 and a TLS failure share a token and a 429 does not join them.

4. **Section 4.3 — the version-control scope limit.** Ensure prose states that the version-control
   transport gains no transient reason here, that a git remote publishes no budget or reset time,
   and that `provision:unreachable` already routes the caller-repairable git-side condition away
   from `failed`. Done-condition: a reader does not expect `integrate:forge_unavailable` and can
   tell the omission was decided.

5. **Section 8.4 — the `retry_after` need.** Ensure `retry_after` joins the `need` vocabulary,
   named as the need a transient forge condition raises, with the reset time — where one is known —
   in `outputs.forge_budget` rather than in the need. Done-condition: the need list includes it and
   nothing duplicates `resets_at` into the escalation payload.

6. **Section 8.4 — `retryable` as a property of the need.** Ensure the section defines `retryable`
   as *re-invoking the same entry point with the same arguments, after a delay and with no further
   action by the caller, MAY succeed*; states it is a property of the `need` and therefore follows
   from a reason's default need (Section 4.3) so the two cannot disagree; carries it in the
   escalation payload; and fixes the value for every need in the vocabulary — `reread_then_retry`,
   `await_checks` and `retry_after` retryable, `integrate_then_retry`, `resolve_conflicts`,
   `supply_identity`, `human_review` and both holds not. Done-condition: for every need Section 8.4
   names, a reader can state the value without consulting another section.

7. **Section 8.4 — why the field exists.** Ensure prose states that a consumer deriving retryability
   from the need is correct until a `MINOR` adds one (Section 8.5), so carrying the bit is what
   makes a new need absorbable — the job the `#class` fallback does for new reasons. Done-condition:
   the field is justified by something a derivation cannot do.

8. **Section 8.5 — the major-stable surface.** Ensure the `retryable` value of a need is named in
   the major-stable list beside the class of every listed reason. Done-condition: the list accounts
   for every field a consumer branches on.

9. **Section 8.2 — the diagnostic output.** Ensure `outputs` carries the condition behind a
   `forge_unavailable` result as a token — a server error, an expired bound (Section 8.1, decision
   0109), or a transport failure — absent for any other reason, in the shape `unanswered_gates`
   already uses for its three conditions. Done-condition: routing and diagnosis spell the condition
   the same way and one consumer branch reads both.

10. **Section 9.2 — which capability answers them.** Ensure the section states that any capability
    may answer either reason, since every one of them reaches the code host, and that a backend MUST
    NOT report a permanent refusal under either. Done-condition: the obligation sits beside the
    budget-snapshot obligation and covers capabilities added later.

11. **Sections 13.1, 13.2, 13.3.** Ensure the test matrix checks that a throttled forge call yields
    `rate_limited` and not `failed`, that the run escalates rather than failing, that a 422-shaped
    permanent refusal still yields an `error`-class result, that `retryable` is present on every
    `needs_caller` escalation and matches the need, and that `forge_unavailable`'s condition is
    reported in `outputs`. Ensure the checklist and the Conformance Statement account for the two
    reasons and the `retryable` property. Done-condition: each of steps 1, 2, 6 and 9 has a check
    that would fail if the step were reverted.

12. **`conformance/vcsx/vocabulary.json`.** Ensure the reason group carries both tokens with class
    `needs_caller` and default need `retry_after`, and the `need` group carries `retry_after` and a
    `retryable` property on every need. Done-condition: a consumer can generate its retry predicate
    from the registry without reading prose.

## Cross-cutting sync

No `repo.policy.toml` key changes. Section 5.3's `#class` ladder is untouched: both reasons are
`needs_caller`, so an existing `#needs_caller` edge already catches them, which is the compatibility
property Section 4.3 claims for new reasons.

## Anchor changes

New anchors: reason tokens `rate_limited` and `forge_unavailable`; `need` token `retry_after`; the
escalation field `retryable`; the `outputs` key reporting a `forge_unavailable` condition and its
three condition tokens. No anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.3, 8.2, 8.4, 8.5, 9.2, 13.1, 13.2),
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.
