# Plan — 0075 A failed counterpart acquisition is `pull:failed`

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set", 4.3 "Reason-Token Registry", 9.1 "VCS Backend Plugin",
and 13.1 "Test Matrix".

`conformance/vcsx/README.md`: the deferred-coverage entry for the acquire/use split extends to the
counterpart half.

No `conformance/vcsx/vocabulary.json` edit. No reason token is added, no class changes, and the
registry's `pull` entries — `ok`, `conflict`, `identity_missing`, and the universal `failed`,
`unsupported` — are already the complete set this decision leaves in place. Step 6 verifies rather than
assumes it.

No section is added, removed, or renumbered: every change lands inside an existing subsection, so no
cross-reference in either engine document moves.

No `VCSX-CONTRACT.md` edit. Section 14 requires every *shared* token to be spelled identically, and this
decision spells no new token; the contract surface names no Section 9.1 capability.

No `SPEC.md` edit. Symphony references the engine's operations, classes and reason vocabulary, not its
plugin API, and a `pull:failed` that is now reachable is another `error`-class result its `#class`
fallback already absorbs.

No `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit. Section 13.3 obliges an engine to record the reason
tokens it adds beyond the registry and the capability descriptors its plugins advertise; neither
changes here. Step 7 verifies this.

## Steps

1. **`fetch_counterpart` answers three ways.** Ensure Section 9.1's `fetch_counterpart(remote,
   work_branch)` bullet states three answers rather than two: the ref of the work branch's remote
   counterpart; none where the remote carries none (Section 6.2); or that the acquisition failed, which
   the engine reports as `pull:failed` (Section 4.3). Ensure the bullet states that the last two are
   distinct answers — an acquisition that failed MUST NOT be answered as an absent counterpart. Done
   when each of the three conditions the operation has a result for has an answer of its own, and when
   Section 6.2's "surfaces at first use as the operation's `failed` reason" is satisfiable for `pull`.

2. **`fetch_base` keeps its two answers, with the reason named.** Ensure Section 9.1's `fetch_base(remote,
   branch)` bullet states that a base it cannot acquire is `integrate:base_unavailable` (Section 4.3),
   so the two acquiring capabilities are read side by side and the asymmetry between them is visible at
   the point it exists. Ensure nothing else about the capability changes: it still answers the base ref
   and takes the same arguments. Done when neither acquiring capability's failure has to be inferred
   from the registry alone.

3. **`pull`'s three outcomes are in the operation's own text.** Ensure Section 4.1's `pull` bullet states
   that where the remote carries no counterpart the operation is a benign no-op reported as `pull:ok` —
   the ordinary state before the first push, the work branch being engine-derived (Sections 6.2, 6.3) —
   and that an acquisition the engine could not complete is `pull:failed` rather than that no-op.
   Ensure the existing history-preservation material is unchanged: the counterpart is merged in, no
   commit is rewritten, dropped or re-parented, and `pull:conflict` is a merge conflict the caller
   resolves and `commit` finalizes. Done when the pre-first-push state and the failure are
   distinguishable from the operation's own description rather than only from the plugin API.

4. **Section 4.3 states why `pull` carries no counterpart token.** Ensure the prose following the
   registry table — the paragraph distinguishing `base_unresolved` from `base_unavailable` — states that
   both of `fetch_base`'s non-ref answers are failures, so one reason covers them, while
   `fetch_counterpart`'s are a benign absence and a failure, which no single reason can carry because a
   reason carries one proto class (Sections 4.2, 8.5); the acquiring capability therefore distinguishes
   them (Section 9.1) and the failure is the universal `failed`. Done when a reader who finds
   `integrate:base_unavailable` and no `pull` counterpart row finds the reason in the document rather
   than reading the omission as an oversight.

5. **The test matrix asks for the check.** Ensure Section 13.1's "Operations and reasons" bullet states
   that a `pull` whose acquisition fails yields `pull:failed` rather than `ok`, while a `pull` against a
   remote carrying no counterpart still yields `ok` — placed beside the existing "an `integrate` whose
   acquisition fails yields `base_unavailable` rather than retrying to the flow bound". Done when the
   matrix distinguishes the two counterpart conditions, so an engine cannot pass it while reporting a
   failed fetch as success.

6. **The token registry is unchanged and verified.** Ensure `conformance/vcsx/vocabulary.json` still
   carries exactly `pull:ok`, `pull:conflict`, `pull:identity_missing`, `pull:failed` and
   `pull:unsupported`, with `failed` and `unsupported` marked `universal: true` and `pull` carrying no
   `blocked` entry (it is gated at no lifecycle position). Done when the registry and Section 4.3 agree
   after the edit, with no entry added.

7. **The conformance corpus records the gap.** Ensure `conformance/vcsx/README.md`'s "Base-ref
   resolution and the acquire/use split" entry under "Deferred to later slices" covers the counterpart
   half: whether a `fetch_counterpart` failed is a property of a real checkout with a real remote, as a
   failed `fetch_base` is, so `pull:failed` from a failed acquisition has no vector and stays deferred.
   Ensure no "Surfaced findings" entry is added: this decision resolves an issue from an implementation
   rather than a gap found while authoring vectors. Done when the corpus states why the new matrix check
   has no vector instead of appearing to have overlooked it.

## Cross-cutting sync

`CLAUDE.md` names the `SPEC.md` cross-cutting sections; this decision changes `VCSX-SPEC.md`, whose
counterparts are Sections 13.1 (Step 5) and 13.2 (verified, no edit — the checklist item "the VCS
backend separating the capabilities that acquire from the local ones that use what they acquired"
already covers the split, and no new surface is added for it to list).

Section 6.4's config material is untouched: no configuration key, default, or base-resolution behavior
changes.

## Anchor changes

None. No section is retitled, no capability renamed, no reason token added or removed.
`fetch_counterpart`'s answer domain widens from two answers to three; the capability keeps its name and
its arguments.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.1, 13.1) and `conformance/vcsx/README.md`.
`conformance/vcsx/vocabulary.json` verified unchanged.
