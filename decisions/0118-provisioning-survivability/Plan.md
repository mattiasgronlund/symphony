# Plan — 0118 A tool that is not there yet is a tool the workspace cannot use

## Scope

`SPEC.md`: Section 9.7 "Repository Provisioning and the VCS Engine" (the workspace-content
guarantee, the ordering, and disk-full), Section 16.5 `ensure_object_store` (the ordering note),
Sections 17.2, 18.1.

## Steps

1. **`Repository Provisioning` — the guarantee.** Ensure the section states that a tool the workspace
   depends on MUST be usable from a workspace Symphony provisioned, with no step the agent takes
   first. Ensure it is stated over what the workspace contains rather than over clone depth,
   submodule recursion, or store sharing — all of which are the engine's determinations (Section
   9.7, `VCSX-CONTRACT.md`). Done-condition: a repository author can check the guarantee by
   provisioning a workspace and running the tool.

2. **`Repository Provisioning` — the submodule consequence.** Ensure the text states that a tool
   distributed as a submodule does not satisfy the guarantee, because whether provisioning populates
   one is the engine's determination rather than something a repository can rely on, and that a
   deployment needing such a tool distributes it as a pinned release the workspace resolves or
   vendors it into the tree. Done-condition: the recommendation reads as a consequence of step 1
   rather than as a distribution preference.

3. **`Repository Provisioning` — the ordering Symphony owns.** Ensure the text states that an
   implementation MUST NOT start an agent session against a workspace whose tree derivation has not
   completed — the store half and the tree half being distinct (Section 16.5), and a repository's own
   tools being present only after the second. Done-condition: the one thing the engine cannot state
   is stated here.

4. **`Repository Provisioning` — disk-full.** Ensure `ENOSPC` is stated to be a
   `repository_provisioning_failures` condition taking that class's existing disposition (Sections
   14.1, 14.2), that a partially written store or tree MUST NOT be presented as usable, and that the
   retry is the repo-scoped one rather than a per-worker backoff. Done-condition: no new failure
   class or disposition is introduced.

5. **Section 16.5 — the ordering in the algorithm.** Ensure the prose under `ensure_object_store`
   notes that the store half alone does not make a repository's own tools present. Done-condition:
   the algorithm's two halves are distinguishable in what they guarantee, not only in what they do.

6. **Sections 17.2, 18.1.** Ensure the test matrix checks that a workspace-dependency tool is usable
   from a freshly provisioned workspace with no additional step; that no agent session starts against
   a workspace whose tree derivation did not complete; and that a provisioning run interrupted by a
   full disk leaves no partially written store presented as usable. Ensure the checklist carries the
   guarantee. Done-condition: steps 1, 3 and 4 each have a check.

## Cross-cutting sync

Section 6.4 gains nothing: no configuration key. Sections 17 and 18 are covered by step 6. Section 19
gains nothing — no new `Implementation-defined` choice; the object-store path obligation already
exists.

## Anchor changes

None.

## Status

Applied to `SPEC.md` (Sections 9.7, 16.5, 17.2, 18.1).
