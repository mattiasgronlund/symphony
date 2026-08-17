# Plan — 0128 A table that is complete against itself is where a missing obligation hides

## Scope

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: Section 3 "`Implementation-defined` and `MUST document`
Resolutions".

`CLAUDE.md`: the working agreements' cross-cutting sync list.

`VCSX-SPEC.md`: Section 13.3 "Conformance Statement", where the validator obligation is worded for one
validator and now covers two.

## Steps

1. **The network bound row.** Ensure Section 3 carries a row for the default `network_bound_ms` and
   any per-capability values the engine applies, citing Sections 8.1 and 9, with a resolution
   placeholder naming the duration, any per-capability values, and whether a deployment may configure
   it. Done-condition: the row matches Section 13.3's bullet in scope.

2. **The validator mechanism row, over both validators.** Ensure Section 3 carries a row for the
   mechanism a forge backend declaring conditional-read support realizes the `pr_state` and
   `checks_state` validators with (Sections 9.2, and decision 0124), with a resolution placeholder
   admitting `not supported` for a backend that declares none. Done-condition: the row covers both
   validators, so decision 0124 adds no second row.

3. **The budget bucket row.** Ensure Section 3 carries a row for which budget buckets each forge
   backend observes and where it reads them from, citing Section 9.2, per backend. Done-condition:
   the row is per-backend, as the `forge_parameters` row already is.

4. **The resume token row.** Ensure Section 3 carries a row for the form of the `resume_token` and
   how the engine establishes that one it is handed is its own and current (Sections 8.1, 8.2, 8.6,
   and decision 0123). Done-condition: the row exists and this batch adds no Section 13.3 obligation
   without one.

5. **The condition stays in the resolution.** Ensure no column is added for a conditional row; a
   backend declaring no conditional-read support answers `not supported`. State nothing about this in
   the template itself beyond the placeholder — the table's shape is what a generator parses.
   Done-condition: Section 3's columns are unchanged.

6. **`VCSX-SPEC.md` Section 13.3.** Ensure the capability-descriptor bullet's validator clause names
   both validators rather than `pr_state`'s alone. Done-condition: the bullet and the template row
   describe the same obligation.

7. **`CLAUDE.md` — the sync list.** Ensure the working agreements name the artifacts a substantive
   change must keep in sync beyond `SPEC.md`'s three: `VCSX-SPEC.md` Sections 13.1, 13.2 and 13.3, and
   the two Conformance Statement templates. Done-condition: a decision that adds an
   `Implementation-defined` answer has a stated obligation to add its row, in the file an agent reads
   at the start of a session.

## Cross-cutting sync

`CONFORMANCE-STATEMENT-TEMPLATE.md` (Symphony's own) is checked in the same pass for obligations
`SPEC.md` added without a row; where none is missing, nothing changes and the check is recorded here
rather than repeated.

`scripts/validate_workflow_bundle.py` is unchanged: it validates the workflow bundle's structure, not
the spec, and this decision adds no bundle scaffolding.

## Anchor changes

None. Five template rows are added; no obligation is renamed or removed, and Section 13.3's validator
clause is widened rather than respelled.

## Status

Applied to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 3), `VCSX-SPEC.md` (Section 13.3) and
`CLAUDE.md`.
