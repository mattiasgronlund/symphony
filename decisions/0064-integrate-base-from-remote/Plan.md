# Plan — 0064 `integrate` resolves the base against the remote; the read-only operations do not

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set" (the `integrate` bullet and a `Note:` under the operation
list), 9.1 "VCS Backend Plugin", 12.2 "`ship` Sequence" (the prose under the algorithm), and 13.1 "Test
Matrix".

Depends on decision 0062, which puts the resolved remote in `[engine]` and supplies it to
`integrate(remote, base)`. This decision says what `integrate` does with it. Applied in the same change;
if they are ever separated, 0062 goes first.

No new section, no renumbering, no new token. Nothing in the major-stable surface (Section 8.5) moves —
no reason, class, status, `need` or envelope field changes — so `conformance/vcsx/vocabulary.json` needs
no edit.

No `VCSX-CONTRACT.md` edit: its Section 6 glosses `integrate` as "bring the base branch into the work
branch (back-merge / update-branch)", which stays true, and its Section 11 defers the plugin API, the
per-operation registry and "the engine's internal algorithms" to `VCSX-SPEC.md`. Where the two differ in
specificity rather than in a name, `VCSX-SPEC.md` governs (its Section 1.2), and no shared name changes.

No `SPEC.md` edit: Symphony's Section 9.8 already has Symphony perform "every operation that touches the
remote: fetch, branch, back-merge, and push", which is this decision's split stated from the consumer's
side and consistent with it.

No vector change: whether an operation acquires the base needs a repository and a network, which
`conformance/vcsx/README.md` already defers under "Plugin behavior".

## Steps

1. **`integrate` names its source.** Ensure Section 4.1's `integrate` bullet states that the base is the
   branch as the configured remote holds it (Sections 6.2, 6.4), acquired rather than read from the
   checkout's copy, while keeping the existing recorded-conflict-resolution clause and the "gated at no
   fixed position; typically run in response to `push:non_fast_forward`" clause. Done when an
   implementer reading the `integrate` bullet alone knows whether to reach the network.
2. **The read side is stated with it.** Ensure Section 4.1 carries a `Note:` under the operation list
   recording that the operations reaching the remote are exactly those Section 3.2 places host-side —
   among the version-control operations, `integrate`, `push` and `pull` — that `status` and `diff` are
   read-only and report against the base as the checkout already holds it, so their `ahead`/`behind`
   counts and delta MAY be stale where the remote has moved, and that the asymmetry follows from
   Section 3.2's trust split rather than being an omission: acquiring the base is a host-side act, and
   marking a read-only operation host-side would deny it to a consumer running the engine in-sandbox
   without credentials. Ensure the Note says a caller needing current figures runs `integrate` first.
   Done when both halves of the question are answered in the section that raises it.
3. **Section 9.1 states the same split over the capabilities.** Ensure Section 9.1 records that every
   capability not taking a `remote` is local to the checkout — it reads or writes the worktree and the
   history the checkout already holds, acquires nothing over the network, and needs no credential — so
   `ahead_behind(base)` and `diff(base)` compare against the checkout's copy of the base (Section 4.1).
   Done when a backend author implementing `ahead_behind` knows not to fetch.
4. **Section 12.2 records why the retry converges.** Ensure the prose under the `ship` algorithm states
   that the retry converges because `integrate` acquires the base from the configured remote
   (Section 4.1) rather than re-reading the checkout's copy, and that against a stale copy the push
   would stay non-fast-forward until the flow bound (Section 5.6) ended the invocation. Done when the
   loop's termination in the *good* case is stated, not just its bound in the bad one.
5. **The test matrix covers both halves.** Ensure Section 13.1's `Operations and reasons` check states
   that `integrate` brings in the base as the remote holds it, so a `push:non_fast_forward` retry
   converges against a base that moved, while `status` and `diff` report against the checkout's copy and
   acquire nothing. Done when an engine that never fetches and an engine that fetches on `status` both
   fail a named check.

## Cross-cutting sync

None beyond Section 13.1 (Step 5). Section 13.2's checklist covers the plugin API at the altitude it
uses; Section 13.3 gains no row because nothing here is `Implementation-defined`.

`conformance/vcsx/vocabulary.json` is unchanged: `integrate`'s entry carries its `lifecycle_position`
and its reasons, and neither moves.

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` are untouched; this decision changes
`VCSX-SPEC.md`, whose counterparts are Sections 13.1 and 13.2.

## Anchor changes

None of this decision's own. `integrate(base)` → `integrate(remote, base)` is recorded under decision
0062, which makes the parameter change; this decision only says what the parameter is used for.

## Out of scope

- **An OPTIONAL fetching variant of `status`.** The reconsideration trigger in `Background.md`, not this
  decision: it would be a new operation or a `status` argument, and no consumer has asked for one.
- **A fetch operation in the required set.** Recorded as the rescue Option B would need: it would put a
  step in every policy that the built-in routing exists to avoid.
- **`pull`'s source.** Section 4.1 already says "from its remote counterpart", and decision 0061
  constrains how it applies what it finds.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 9.1, 12.2, 13.1).
