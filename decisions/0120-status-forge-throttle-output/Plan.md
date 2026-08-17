# Plan — 0120 A read that always completes still has to say which repair it needs

## Scope

`VCSX-SPEC.md`: Section 4.1 "Operation Set" (the `status` entry), Section 4.3 "Reason-Token
Registry" (the `(any forge)` clause), Section 9.2 "Forge Backend Plugin" (what a capability's
transient answer reaches the caller as), Sections 13.1, 13.2.

`conformance/vcsx/`: the conditional-read and transient-condition vectors assert the new output.

No change to `VCSX-CONTRACT.md`: it fixes the proto classes and the named results, and this decision
adds neither a reason nor a class.

## Steps

1. **`status` — the fourth pull-request output.** Ensure the `status` entry in `Operation Set`
   defines `pr_state_throttled`: where the forge refused the `pr_state` read because a budget was
   exhausted, the pull-request fields are null, that output reports it, and the operation still
   completes. State the distinction against its three neighbours in the terms the entry already uses
   for them — `pr_state_unavailable` is a read that established nothing, `pr_state_unchanged` a read
   that established the caller's copy is current, `pr_state_throttled` a read the forge refused for
   budget, and a reported state a read that established a new one. Done-condition: the entry names
   four distinguishable pull-request conditions and `status` still completes in all of them.

2. **`status` — where the reset time is read.** Ensure the entry states that the exhausted bucket and
   its `resets_at` are in `outputs.forge_budget` (Sections 8.2, 9.2), so the output names the
   condition and the snapshot carries the figure, with the figure in one place. Done-condition: no
   duplicate reset time in the output.

3. **`Reason-Token Registry` — the `(any forge)` clause matches its enumeration.** Ensure the
   sentence introducing `rate_limited` and `forge_unavailable` scopes them to the operations that
   **act** on a forge call — `push`, `create_pr`, `merge`, `await_checks` — rather than to "every
   operation whose forge call the condition prevented", and states why `status` is not among them:
   it reports rather than acts, it completes whatever the forge answered, and it carries the
   condition as an output. Done-condition: the clause and the enumeration describe one set, and a
   reader looking for `status` finds it named rather than absent.

4. **`Reason-Token Registry` — the boundary paragraph.** Ensure a paragraph states the division in
   the registry's own idiom, alongside the existing ones for `base_unresolved` / `base_unavailable`
   and for `blocked` / `failed` / `hook_unanswered`: an operation a forge refusal stops reports a
   reason, and an operation a forge refusal leaves one field short of complete reports an output.
   Done-condition: the paragraph names which operations are on each side and why the split falls
   there.

5. **`Forge Backend Plugin` — what a capability's transient answer becomes.** Ensure the paragraph
   permitting any capability to answer `rate_limited` or `forge_unavailable` states what each answer
   reaches the caller as, keyed by the reader rather than by the capability: the reading operation's
   own reason where the operation acts on the answer, and a `status` output where it reports it.
   This is Section 9.1's `pr_state`-has-three-readers split applied to the transient answers.
   Done-condition: no capability answer is permitted that no operation has a spelling for.

6. **Sections 13.1, 13.2.** Ensure the test matrix checks that a throttled `pr_state` reached through
   `status` yields `ok` with null pull-request fields and a `pr_state_throttled` output — not
   `status:failed`, not `pr_state_unavailable`, and not an escalation — and that the same throttle
   reached through `push` or `merge` still yields `rate_limited`; and that a `forge_unavailable` on a
   `status` read remains `pr_state_unavailable`, so the two conditions stay distinguishable at the
   operation that reports both. Ensure the checklist's conditional-read bullet names the fourth
   output. Done-condition: steps 1 and 5 each have a check, and the throttle/outage pair is asserted
   as distinguishable.

## Cross-cutting sync

Section 13.3 gains nothing: the output is fully specified and delegates no choice. Section 8.2 needs
no new key — `forge_budget` already carries the snapshot and its entry already states that its
absence is not evidence.

`SPEC.md` gains nothing normative. Symphony reads `status` outputs through the engine contract and
Section 8.11's recording requirement already covers the snapshot; a deployment that wants to act on
the new output does so through the OPTIONAL forge budget guard it already has.

## Anchor changes

New anchor: the `pr_state_throttled` output token. No anchor is renamed or removed. The `(any forge)`
clause is rewritten and its enumeration is unchanged, so no reason token moves.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.2, 13.1, 13.2) and
`conformance/vcsx/vocabulary.json`.
