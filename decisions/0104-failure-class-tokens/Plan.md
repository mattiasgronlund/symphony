# Plan — 0104 The failure classes get a token

## Scope

`SPEC.md`: Section 14.1 "Failure Classes" (each class gains an identifier-shaped token and the set's
openness is stated), Section 14.2 "Recovery Behavior", Sections 17.2, 17.4 and 18.1.4 (the
conformance checks that name a class), Section 19 "Conformance Statement", and Section 17's registry
paragraph.

`conformance/vocabulary.json`: one new group, `failure_classes`.

`conformance/README.md`: the coverage table, the closed-set paragraph, the "Deferred to later
slices" entry for Section 14.1 (which decision 0103 recorded as pending this decision), and
"Surfaced findings".

`CONFORMANCE-STATEMENT-TEMPLATE.md`: the two `MUST document` rows named by class, and any
recovery-disposition table keyed by class.

## Steps

1. **`Failure Classes` — each class gains a token.** Ensure each of the nine carries an
   identifier-shaped token beside its Title Case prose name, in the shape Section 14.1 already uses
   for `token_budget_exceeded`. Done-condition: Section 14.1 spells failure categories one way, and
   for each of the nine a reader can tell what a consumer branches on.

2. **`Failure Classes` — the set's openness is stated.** Ensure the closing note's permission for an
   OPTIONAL extension to define additional categories is stated as the set being open, so the
   registry records `exhaustive: false` from the prose rather than by inference from
   `token_budget_exceeded`'s existence. Done-condition: a reader can tell whether a generated type
   may close the enum without consulting Section 8.8.

3. **`Recovery Behavior` — every bullet names the classes it disposes of.** Section 14.2's bullets
   carry their own descriptive headings rather than Section 14.1's names, and the mapping is not
   one-to-one, so ensure each bullet names its class token(s) and that a preamble states the two
   places it is not 1:1 — `workspace_failures` and `agent_session_failures` share the worker
   disposition, `tracker_failures` takes two. Done-condition: every one of the nine is reachable
   from Section 14.2, and no bullet's classes have to be inferred.

4. **The conformance checks name the token.** Ensure Sections 17.2, 17.4 and 18.1.4 name the token
   where they currently name only the prose title, so a check asserts something spelled identically
   in every implementation. Done-condition: `grep -n 'Engine Invocation Failures\|Repository
   Provisioning Failures' SPEC.md` shows no occurrence in Sections 17 or 18 that lacks its token.

5. **`Conformance Statement` — the class-keyed rows.** Ensure Section 19 and
   `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1's two park-vs-retry rows are keyed by token, so a
   statement author transcribes a token rather than a title. Done-condition: no row in the template
   names a failure class only by its prose title.

6. **`Test and Validation Matrix` — the registry paragraph.** Ensure the sentence listing the
   published token sets names the failure classes (Section 14.1). Done-condition: every group in
   `vocabulary.json` is traceable to a set this paragraph names.

7. **`vocabulary.json` — `failure_classes`.** Ensure the group exists with `spec_refs` citing
   Sections 14.1 and 14.2, `requirement_level: "REQUIRED"`, `exhaustive: false` (step 2), and each
   entry carrying its `token`, its prose `name`, and `core` (`false` for `Node Provisioning
   Failures` and `Executor Bring-up Failures`, which the OPTIONAL node-scheduler extension owns).
   The Section 14.2 recovery disposition is **not** carried: with step 3 done it would restate prose,
   and the mapping is not one-to-one.
   Ensure the `note` records that an OPTIONAL extension MAY define further categories —
   `token_budget_exceeded` being the specification's own example — and that openness is a property
   of the set rather than of the names, so an implementation shipping no such extension may close
   its own enum at nine. Done-condition: a Conformance Statement author can fill the
   recovery-disposition rows from this group alone.

8. **`conformance/README.md` — coverage, closedness, and the deferral entry.** Ensure the coverage
   table carries a `failure_classes` row, the closed-set paragraph accounts for it, and the
   "Deferred to later slices" entry decision 0103 wrote for Section 14.1 is removed as published.
   Done-condition: no bullet in that list names a set the registry now carries.

9. **`conformance/README.md` — the surfaced finding.** Ensure "Surfaced findings" records that
   Section 14.1 spelled failure categories two ways — nine Title Case titles and one snake_case
   category, the latter asserted by a Section 17.4 check — as resolved by step 1. Done-condition:
   the finding is readable without reference to this decision folder.

## Cross-cutting sync

Section 6.4's config cheat sheet gains nothing: no configuration key changes. Section 17 is covered
by steps 4 and 6; Section 18 by step 4; Section 19 by step 5.

## Anchor changes

Each of Section 14.1's nine failure classes gains an identifier-shaped token as a new anchor:
`workflow_config_failures`, `repository_provisioning_failures`, `workspace_failures`,
`agent_session_failures`, `tracker_failures`, `observability_failures`, `engine_invocation_failures`,
`node_provisioning_failures`, `executor_bring_up_failures`. The Title Case names are retained as
prose names, so **no anchor is renamed or removed** and no existing reference breaks. One registry
group name is added: `failure_classes`.

## Status

Applied to `SPEC.md`, `conformance/vocabulary.json`, `conformance/README.md` and
`CONFORMANCE-STATEMENT-TEMPLATE.md`.
