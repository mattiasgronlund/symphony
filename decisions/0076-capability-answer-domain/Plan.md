# Plan — 0076 A capability that cannot determine its answer says so

## Scope

`VCSX-SPEC.md`: Section 9 "Plugin API" (preamble), 9.1 "VCS Backend Plugin", 9.2 "Forge Backend
Plugin", 4.1 "Operation Set" (`status`, `push`), 8.6 "Invocation Preconditions", 11 "Security and
Trust Model", 12.2 "`ship` Sequence", 13.1 "Test Matrix", 13.2 "Implementation Checklist", 13.3
"Conformance Statement".

`conformance/vcsx/vocabulary.json`: one `precondition_reasons` entry, `checkout_unreadable`.
`conformance/vcsx/README.md`: the normalization count and a deferred-coverage entry.

No section is added, removed, or renumbered: the invariant lands in Section 9's existing preamble, so
no cross-reference in either engine document moves.

No `VCSX-CONTRACT.md` edit. Section 14 requires every *shared* token to be spelled identically; the
contract surface names no Section 9 capability, defers the reason registry, and carries no precondition
registry of its own.

No `SPEC.md` edit. Symphony references the engine's operations, classes and reason vocabulary, not its
plugin API; `checkout_unreadable` arrives under the `usage_or_config` status Symphony already handles.

No `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit beyond what Section 13.3 already obliges — an engine
records precondition reasons it adds *beyond* the registry, and this one is now in it. Step 10 verifies.

## Steps

1. **Section 9's preamble states the invariant.** Ensure the "Plugin API" preamble states that each
   capability answers in one of two shapes, fixed by its entry in Sections 9.1 and 9.2 — the
   operation's typed result `<op>:<reason>`, or a value the engine composes an operation from — and
   that a value-answering capability MUST be able to answer that it could not determine one, which
   MUST NOT be spelled as the value's absent or negative case. Ensure it states that every such
   non-answer maps to a Section 4.3 reason where an operation has been dispatched or a Section 8.6
   precondition reason where none has, the first dispatch being the boundary, and that the
   capability's own entry MUST state which. Ensure a second paragraph records why the rule is stated
   over the list rather than per capability: the failure it prevents raises nothing anywhere, so what
   follows is a benign result for a run that did nothing. Done when a capability added later has a
   rule to be read against.

2. **`pr_state` answers four ways.** Ensure Section 9.2's `pr_state(work_branch)` bullet answers the
   work branch's pull request — its number, its state and the head it currently carries — none where
   the forge carries no pull request for it, or that the state could not be determined; that the last
   two are distinct answers and an undetermined state MUST NOT be answered as an absent pull request;
   and that the mapping is `push:failed`, `create_pr:failed`, and a `pr_state_unavailable` output for
   `status`. Ensure the bullet fixes the lookup's key: on the work branch as head whatever base the
   pull request targets, because `create_pr:base_mismatch` exists to find one opened against a
   different base, so a caller's own base MUST NOT be substituted. Ensure it states that a search the
   backend could not complete — including an enumeration that reached a bound it imposes, which it
   MUST document — is a state it could not determine and not an absent pull request. Done when each
   of the five states the readers act on has an answer of its own.

3. **`create_or_update_pr` refuses rather than duplicates.** Ensure Section 9.2's
   `create_or_update_pr` bullet states that maintaining one pull request per work branch requires
   finding the one that exists, so a backend that could not determine whether the work branch already
   has one MUST NOT create one, and reports `create_pr:failed`. Done when the duplicate-pull-request
   outcome is forbidden in the capability that would produce it.

4. **The Section 9.1 audit.** Ensure each value-answering VCS capability states what an answer it
   could not determine maps to: `detect_mode()` and `current_branch()` to `checkout_unreadable`;
   `is_dirty()` to a dispatched `commit` reporting `commit:failed`, with the guard stated as
   dispatching rather than skipping; `is_conflicted()` and `ahead_behind()` to a `status` output
   reported undetermined; `resolve_base_ref()` to `diff:base_unavailable` with `status` distinguishing
   an undetermined resolution from `base_absent`. Ensure `accepts_branch_name()` and
   `accepts_identity()` state that they answer yes or no with no third answer, a backend that cannot
   judge answering no, and that this is a choice rather than an omission. Done when no capability's
   failure has to be inferred from the registry alone.

5. **`checkout_unreadable` joins the precondition registry.** Ensure Section 8.6's table carries a row
   for a VCS backend capability consulted before the first dispatch that could not answer, and that
   the prose states such a capability establishes no precondition either way and is
   `checkout_unreadable` rather than the refusal its negative answer would have produced. Done when a
   backend that cannot read the checkout has a reason that is not `no_current_branch`.

6. **`status` reports what it could not determine.** Ensure Section 4.1's `status` bullet states that
   an output the operation could not determine is null with a `<field>_unavailable` output reporting
   it — `pr_state_unavailable` where a configured forge could not be asked — and that `base_absent`
   states what the checkout holds while `<field>_unavailable` states that the read did not establish
   it, which is Section 4.3's absent/unavailable distinction. Ensure the existing `base_absent`
   material is unchanged. Done when a read reports no determinate value it did not establish.

7. **`push`'s pull-request guard is in the operation's own text.** Ensure Section 4.1's `push` bullet
   states that where a forge is configured the operation first reads `pr_state` and refuses a push
   over a CLOSED/MERGED pull request, and that a state it could not determine is not the absence of
   one: the operation does not push and reports `push:failed`. Done when the guard and its
   fail-closed disposition are readable from Section 4.1 rather than only from Section 9.2's gloss.

8. **`ship`'s guard does not read undetermined as clean.** Ensure Section 12.2's pseudocode guard
   admits an undetermined predicate (`if worktree_dirty() is not clean`) and that the prose states
   why: the guard exists to skip a `commit` that would report `nothing_to_commit`, not to decide
   whether a commit is owed, so an undetermined predicate dispatches rather than skips, a guard that
   read it as clean producing a `ship` that reports success with the work still uncommitted. Done when
   the branch on the predicate is fail-closed.

9. **Section 11 names the forge half.** Ensure Section 11's network bullet cites Sections 9.1 and 9.2
   and states the list as three of the VCS backend's capabilities and every required capability of the
   forge backend. Ensure Section 9.2 states that every capability of that section reaches the code
   host, needs a credential, and realizes an operation Section 3.2 places host-side, so the forge
   plugin has no local half to separate. Done when a consumer mediating "the capabilities that touch
   the network" mediates the forge.

10. **The registries and the matrix.** Ensure `vocabulary.json` carries `checkout_unreadable` under
    `precondition_reasons` and that no other entry changes; ensure Section 13.1 asks for the
    `pr_state`-undetermined behavior of `push`, `create_pr` and `status`, the `is_dirty()`-undetermined
    behavior of `ship`, `checkout_unreadable` over `no_current_branch`, the widened network
    enumeration, and the invariant itself; ensure Section 13.2's plugin item names the invariant and
    Section 13.3's capability item names the forge search bound. Done when an engine cannot pass the
    matrix while spelling a failure as an absent answer.

## Cross-cutting sync

`CLAUDE.md` names the `SPEC.md` cross-cutting sections; this decision changes `VCSX-SPEC.md`, whose
counterparts are Sections 13.1 (Step 10), 13.2 (Step 10) and 13.3 (Step 10, the forge search bound).

`conformance/vcsx/README.md`: the `reasons` normalization count moves 32/50 → 33/51 (that row is
0077's token, corrected here because both land in one change), and "Deferred to later slices" gains an
entry for the conditions no vector can supply.

No configuration key, default, or base-resolution behavior changes, so Section 6.4's config material is
untouched.

## Anchor changes

None renamed or removed. Added: the precondition reason `checkout_unreadable` (Section 8.6), the
`status` output `pr_state_unavailable` and the `<field>_unavailable` output form (Section 4.1).
`pr_state`'s answer domain widens from three answers to four and its value gains the pull request's
number and head; the capability keeps its name and its argument.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 8.6, 9, 9.1, 9.2, 11, 12.2, 13.1, 13.2, 13.3),
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.
