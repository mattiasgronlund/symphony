# Plan — 0182 The engine reads the commit subjects, through a capability that did not exist

## Scope

`VCSX-SPEC.md` Section 9.1 (VCS Backend Plugin), Section 10.2 (Pull-Request Composition), Section 12.5
(Compose the Pull-Request Body), Section 13.1 (Test Matrix) and Section 13.2 (Implementation
Checklist). `VCSX-CONTRACT.md`'s pull-request message bullet. `SPEC.md` Section 9.10 (Forge Operations,
Pull Requests, and Review Writes)'s message-composition bullet.

## Steps

1. **Section 9.1 gains `commit_subjects`.** Ensure a capability `commit_subjects(base_ref)` follows
   `diff(base_ref)`. It answers the subject (first message line) of each commit on the current branch
   not reachable from `base_ref`, oldest first, or that it could not determine them. It reads the
   checkout and acquires nothing, and is resolved against the same base `diff` uses (Section 6.4).
   Done when Section 9.1 lists it.

2. **Section 10.2 names who supplies each input.** Ensure the `body_source = "auto"` bullet says that
   the consumer supplies the work item and, where it runs the task model, the closed task list, and
   that the engine reads the commit subjects itself through `commit_subjects` (Section 9.1). Ensure it
   says that where that read could not determine them, the composed body carries the fixed token
   `commit_subjects_undetermined` in their place, and a `template` unit is told they are
   undetermined. Done when "inputs the consumer supplies" no longer covers the commit subjects.

3. **Section 12.5 reads them from the engine.** Ensure `compose_pr_body` takes the subjects from
   `commit_subjects(base_ref)`, not from `inputs`, and substitutes `commit_subjects_undetermined` for
   an undetermined read. Done when `inputs.commit_subjects` no longer occurs.

4. **Section 13.1 and Section 13.2 check it.** Ensure the Message formulation row in Section 13.1
   says the `auto` body's subjects come from the engine's own read, and an undetermined read yields
   `commit_subjects_undetermined` rather than an empty section. Ensure Section 13.2 lists
   `commit_subjects` with the VCS backend's capabilities, or in the message formulation item. Done
   when both mention it.

5. **The other documents follow.** Ensure `VCSX-CONTRACT.md`'s **Pull-request message — composed**
   bullet and `SPEC.md` Section 9.10's message-composition bullet attribute the commit subjects to
   the engine's read and the ticket and task list to the consumer. Done when neither describes all
   three as consumer-supplied.

6. **The vector that quotes Section 10.2 follows.** Ensure the description of
   `auto_body_source_without_a_bound_unit_is_valid` in `conformance/vcsx/vectors/policy-validation.json`
   no longer says `auto` composes from "durable inputs the consumer supplies". Done when that phrase no
   longer occurs in `conformance/`.

## Cross-cutting sync

- `SPEC.md` Section 6.4, 17, 18: unaffected; Symphony's obligations don't change (it supplies less).
- `VCSX-SPEC.md` Sections 13.1 and 13.2: step 4. Section 13.3: no obligation added.
- Conformance Statement templates: no row owed.
- `conformance/vcsx/`: step 6 corrects one description; no vector is added. A host-independent
  vector for the marker would need a checkout fixture whose log is unreadable, which the corpus does
  not model.

## Anchor changes

- Added: `commit_subjects` (`VCSX-SPEC.md` Section 9.1) and `commit_subjects_undetermined`
  (Section 10.2).
- Removed: `inputs.commit_subjects` from Section 12.5's pseudocode.

## Status

Applied, all steps, in the same pull request as decisions 0177–0182 (issues #173–#178).
