# Plan — 0061 `pull` preserves the work branch's committed history

## Scope

`VCSX-SPEC.md`: the `pull` bullet in Section 4.1 "Operation Set", the `pull` / `conflict` row in
Section 4.3 "Reason-Token Registry", the `pull(work_branch)` capability in Section 9.1 "VCS Backend
Plugin", the never-force bullet in Section 11 "Security and Trust Model", and the cross-cutting
Sections 13.1 "Test Matrix" and 13.2 "Implementation Checklist". `conformance/vcsx/README.md` follows in
its deferred-coverage list.

No section is added, renamed or reordered, so no cross-reference renumbers.

No `conformance/vcsx/vocabulary.json` edit: the decision adds, removes and reclasses no token. `pull`
keeps `read_only: false` and `lifecycle_position: null`, and `pull:ok` / `pull:conflict` keep their
classes. The registry records the vocabulary, not each token's semantics.

No vector: the reconciliation strategy is backend behavior over a real repository, which is the "Plugin
behavior" bucket `conformance/vcsx/README.md` already defers — the same bucket that holds the pinned,
never-forced push refspec this decision extends.

No `VCSX-CONTRACT.md` edit: its Section 6 "Engine Operations and Typed Results" lists `commit`,
`integrate`, `push`, `create_pr` and `merge` as the operations it names, does not name `pull`, and
defers both the exhaustive reason registry and the plugin API to `VCSX-SPEC.md`. No shared token changes
spelling, so Section 14's alignment rule is satisfied without an edit.

No `SPEC.md` edit: Symphony references the engine's operations through `VCSX-CONTRACT.md` (its
Section 9.7) and its only occurrences of the word are "pull request". The decision adds no vocabulary
for it to mirror.

## Steps

1. **`pull` states how it reconciles.** Ensure the `pull` bullet in Section 4.1 "Operation Set" says the
   update preserves the commits already on the branch — the remote counterpart is merged in, and no
   commit on the branch is rewritten, dropped or re-parented — with a pointer to Section 11's invariant.
   Done when a reader cannot choose a rewriting update from the bullet alone.
2. **`pull:conflict`'s recovery path is stated where the reason is introduced.** Ensure the same bullet
   records that `pull:conflict` is therefore a merge conflict, which the caller resolves and `commit`
   finalizes, and that no operation resumes a sequential replay. Done when the reason's way back is
   readable without deriving it from Section 12.2.
3. **The registry row names the merge.** Ensure the `pull` / `conflict` row in Section 4.3
   "Reason-Token Registry" reads as the merge of the remote counterpart stopping on conflicts rather
   than an unqualified "update". Done when the table agrees with Section 4.1 on what stopped, at the
   table's existing one-line altitude and with no class change.
4. **The capability carries the requirement.** Ensure Section 9.1 "VCS Backend Plugin" states it on
   `pull(work_branch)` → `pull:*` — merging the remote counterpart into the local branch and rewriting
   none of its commits — in the shape the neighbouring `push(work_branch)` and `integrate(base)` entries
   already use. Done when a backend author reading only Section 9.1 implements the same update as one
   reading Section 4.1.
5. **The no-rewrite invariant sits beside never-force.** Ensure Section 11 "Security and Trust Model"
   states, in the bullet that pins the push refspec and forbids a force push, that no operation which
   updates the work branch rewrites, drops or re-parents a commit already on it, and that this is what
   keeps the branch publishable under that rule. Ensure the same bullet excludes a `rebase` or `squash`
   merge strategy (Section 6.8) explicitly, since that writes to the base branch and leaves the work
   branch's own history intact. Done when the never-force rule reads as one an engine can always keep
   rather than one it may have to bend; when an operation added later can be checked against a stated
   property instead of against `pull`'s bullet; and when the invariant cannot be misread as narrowing
   the configured merge strategies.
6. **The test matrix covers the reconciliation.** Ensure Section 13.1 "Test Matrix" states, in its
   `Operations and reasons` check, that a divergent `pull` merges rather than rewrites and that the
   `pull:conflict` it leaves is finalized by `commit`. Done when the behavior this decision fixes is a
   testable line in the matrix.
7. **The checklist names the invariant.** Ensure Section 13.2 "Implementation Checklist" lists a
   history-preserving work-branch update alongside the pinned, never-forced push refspec in its
   checkout-mode bullet. Done when the definition of done includes the property Section 11 now states.
8. **The corpus records why no vector covers it.** Ensure `conformance/vcsx/README.md`'s "Deferred to
   later slices" list names the history-preserving work-branch update beside the pinned never-forced
   push refspec in its `Plugin behavior` bullet. Done when a reader of the corpus can tell the omission
   is deliberate rather than an oversight.

## Cross-cutting sync

`VCSX-SPEC.md` Sections 13.1 and 13.2 (Steps 6 and 7) are this document's counterparts to the `SPEC.md`
test matrix and implementation checklist named in `CLAUDE.md`; `SPEC.md`'s own Sections 6.4, 17 and 18
are untouched because this decision changes `VCSX-SPEC.md` only. `conformance/vcsx/README.md` (Step 8)
follows the deferral.

Section 4.2 needs no edit: `pull:conflict` keeps its `needs_caller` class and the proto-class
definitions are unchanged. Section 8.4 needs no edit: `resolve_conflicts` already names the need and its
meaning is unchanged. Section 8.5 needs no edit: no token is added and no listed reason's class moves,
so nothing crosses the major-stable surface. Section 12.2 needs no edit: `ship` dispatches `integrate`
and never `pull`, so its routing is unaffected — recorded in `Background.md` as a deliberate
non-change.

## Anchor changes

None removed or renamed. No token added: this decision constrains the behavior behind `pull` and
`pull:conflict` without changing their spelling or class.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.1, 11, 13.1, 13.2) and `conformance/vcsx/README.md`.
