# Plan — 0063 `commit` captures the working tree, and `is_dirty()` is its predicate

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set" (the `commit` bullet), 9.1 "VCS Backend Plugin" (the
`is_dirty()` capability), 12.2 "`ship` Sequence" (the prose under the algorithm), and 13.1 "Test
Matrix".

No new section, no renumbering, no new token: the reason registry, the proto classes, the invocation
statuses and the `need` vocabulary are all unchanged, so nothing in the major-stable surface
(Section 8.5) moves and `conformance/vcsx/vocabulary.json` needs no edit.

No `VCSX-CONTRACT.md` edit: its Section 6 lists `commit` as a named operation with no gloss and defers
the per-operation registry and the plugin API to `VCSX-SPEC.md` (its Section 11). What `commit` captures
is operation semantics on the deferred side of that line, and no shared name changes.

No `SPEC.md` edit: Symphony's Section 9.8 says "the agent uses local git in the worktree, including
`git commit`" and makes the commit *message* the agent's; it states nothing about which content a
`commit` operation captures, so it stays correct as written.

No vector change: what a commit captures needs a real worktree, which `conformance/vcsx/README.md`
already defers under "Front-end sequences" and "Plugin behavior".

## Steps

1. **`commit` states what it captures.** Ensure Section 4.1's `commit` bullet states that the operation
   captures the working tree in full — every change the VCS does not ignore, including content the VCS
   has not yet recorded — and that the engine defines no staging operation and no way to commit a
   subset, so nothing selects the commit's content out of band. Done when an implementer reading only
   Section 4.1 cannot conclude that `commit` commits an index someone else populated.
2. **`is_dirty()` is named as `commit`'s predicate.** Ensure Section 9.1's `is_dirty()` capability
   states that it reports the working tree dirty exactly when a `commit` would capture something, so
   content the VCS has not yet recorded counts and ignored content does not (Section 4.1). Done when a
   backend author reading Section 9.1 alone implements the same predicate the guard needs.
3. **Section 12.2's guard is tied to the capability.** Ensure the prose under the `ship` algorithm
   states that `worktree_dirty()` is the `is_dirty()` capability (Section 9.1) and that guard and
   operation therefore share one predicate — so a change made only of content the VCS has not yet
   recorded is committed rather than reported clean and pushed as an empty branch. Done when the
   failure the issue names is refuted at the algorithm that would have produced it.
4. **The test matrix covers the empty-branch failure.** Ensure Section 13.1's `Operations and reasons`
   check states that a working tree whose only change is content the VCS has not recorded is dirty and
   is committed, rather than reported `commit:nothing_to_commit` or skipped. Done when the silent
   failure has a testable line.

## Cross-cutting sync

None beyond Section 13.1 (Step 4). Section 13.2's checklist already covers the operation set at the
altitude it uses and gains nothing from restating one operation's content rule; Section 13.3 gains no
row because nothing here is `Implementation-defined`, which is the point of the decision.

`conformance/vcsx/vocabulary.json` is unchanged: no token is added, removed, or reclassed —
`commit:nothing_to_commit` keeps its `done` class.

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` are untouched; this decision changes
`VCSX-SPEC.md`, whose counterparts are Sections 13.1 and 13.2.

## Anchor changes

None. No code-token is renamed or removed and no section is retitled; `commit`, `is_dirty()`,
`worktree_dirty()` and `commit:nothing_to_commit` all keep their spellings.

## Out of scope

- **A `stage` operation and a `before:stage` position.** Recorded as Option B in `Background.md`: the
  engine has no way to decide what a partial selection would contain, and the argument would have to
  come from the caller, which Section 6.3 declines for branches on the same reasoning.
- **A partial-commit or selection argument to `commit`.** The reconsideration trigger, not this
  decision.
- **What the `scan-content` hook inspects.** Section 10.4 already names "a commit diff"; that the diff
  now demonstrably includes new files follows from Step 1 and needs no separate rule.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 9.1, 12.2, 13.1).
