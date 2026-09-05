# Plan — 0166 A vector file registered in neither list

## Scope

`conformance/README.md` only — the harness contract's interpretation-note list, and the vector file
tables.

No change to `SPEC.md`, `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `conformance/vocabulary.json`, or any
vector file. `repository-inheritance.json` already carries the note this decision registers; nothing
about its content changes. No `Implementation-defined` or MUST-document obligation is added, so
neither Conformance Statement template is owed a row.

## Steps

1. **The interpretation-note list names `resolve_repository_config`.** Ensure the harness contract's
   list of functions carrying an interpretation note beyond plain equality has a fourth bullet for
   `resolve_repository_config`, stating that `expect` is `{ resolved, absent }`; that each dotted
   path in `resolved` MUST equal the resolved view at that path; that each path in `absent` MUST NOT
   be present in it; and that unlisted paths are unconstrained.
   Done when the list has four bullets and `resolve_repository_config` is one of them.

2. **The bullet says why `absent` is not optional to implement.** Ensure the bullet states that a
   harness asserting only `resolved` cannot distinguish an implementation that applies defaults
   before resolution, since that order produces a superset satisfying every path in `resolved`
   (Section 6.1).
   Done when the bullet names the superset consequence.

3. **`repository-inheritance.json` has a vector-table row.** Ensure `conformance/README.md` carries
   a slice table row for `vectors/repository-inheritance.json` → `resolve_repository_config`, with
   its profile and its derived-from sections, under a heading naming decision 0159.
   Done when every file in `conformance/vectors/` has a table row naming it — the row count from
   `grep -c` on the table-row prefix equals the file count from `ls -1 conformance/vectors/ | wc -l`,
   16 at `38b0581`.

4. **`config-defaults.json`'s duplication is left in place.** Ensure no edit removes its entry from
   the interpretation-note list; the list is a registry and restating an inline note is its intended
   shape (`Background.md`).
   Done when `resolve_config_defaults` still appears in the list.

## Cross-cutting sync

None. This decision touches no `SPEC.md` section, so Sections 6.4, 17 and 18 are unaffected, and no
Conformance Statement template row is owed.

## Anchor changes

None. No code-token identifier or section title is renamed or removed.

## Status

Applied to `conformance/README.md`: the harness contract's interpretation-note list gains the
`resolve_repository_config` bullet (steps 1 and 2), and a slice 4 table names
`vectors/repository-inheritance.json` (step 3). `config-defaults.json`'s entry is untouched (step 4).
At the applied revision `conformance/vectors/` holds 16 files and the tables hold 16 rows.
