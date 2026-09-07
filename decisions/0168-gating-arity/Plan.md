# Plan — 0168 A published property with one value left

## Scope

`conformance/vocabulary.json`, `conformance/README.md` and `CONFORMANCE-STATEMENT-TEMPLATE.md`.

No change to `SPEC.md`: Section 5.5 (Workflow Validation and Error Surface) is the authority here and
is already correct — decision 0160 made it so, and this decision brings the three artifacts that
publish it into line.

## Steps

1. **`error_classes` entries carry no `gating`.** Ensure the five entries in
   `conformance/vocabulary.json`'s `error_classes` group — `missing_workflow_file`,
   `workflow_parse_error`, `workflow_front_matter_not_a_map`, `template_parse_error`,
   `template_render_error` — each carry `token` and `condition` and no `gating` key.
   Done when no entry object in the group has a `gating` key: loading the registry and testing
   whether any member of `error_classes.entries` carries that key answers false.

2. **The group's `note` states the one behavior and where it comes from.** Ensure the
   `error_classes` group's `note` says that Section 5.5 assigns every class in the group the same
   dispatch gating behavior — the affected run attempt fails and no new dispatches are blocked for
   the instance — rather than describing a two-valued per-entry property, and that it records why
   the value is not carried per entry.
   Done when the note names the single behavior and no longer names `blocks_dispatch`.

3. **The note's extension sentence stops asking an implementation to assign a behavior.** Ensure the
   sentence about Section 5.5's open set says an implementation MUST document any class it defines
   and that the gating behavior is assigned by Section 5.5 rather than chosen by the implementation,
   an implementation-defined class taking the same one.
   Done when the note no longer says an implementation assigns a gating behavior.

4. **`conformance/README.md`'s entry-field documentation drops the `gating` clause.** Ensure the
   paragraph describing `condition` in the error groups and in `transition_triggers` no longer says
   `error_classes` additionally carries `gating`.
   Done when `grep -c gating conformance/README.md` is `0`.

5. **The Conformance Statement template asks for the condition, not a behavior.** Ensure the Section
   4.1 Core row for workflow/template error classes defined beyond Section 5.5's five reads
   `<token + condition for each, or none>`, matching its two neighbouring rows for the tracker and
   agent-runner error categories.
   Done when the row no longer names a dispatch gating behavior.

## Cross-cutting sync

- **`SPEC.md` Sections 6.4, 17 and 18** — unaffected. No configuration key, no check and no
  checklist item changes; Section 5.5's prose already states what this decision publishes.
- **`VCSX-SPEC.md` Sections 13.1–13.3** — unaffected. Nothing here is the engine's.
- **Conformance Statement templates** — step 5 corrects a row rather than adding one. No new
  `Implementation-defined` value and no new MUST-document obligation is introduced; the obligation
  the row exists for, documenting an implementation-defined error class (Section 5.5), is unchanged
  and keeps its row.
- **Conformance corpus vectors** — unaffected. `vectors/prompt-rendering.json` asserts error class
  *spellings* and never a gating behavior, so no vector changes and no README table row moves.

## Anchor changes

- `error_classes[].gating` — **removed** from `conformance/vocabulary.json`, together with the two
  values it took, `blocks_dispatch` and `fails_attempt`. Recorded here rather than treated as no
  change, because decision 0102's `Plan.md` states the field and its five values as a
  done-condition, and a reader chasing that step needs to arrive at this decision rather than at a
  file that no longer matches it. The values were spellings the registry introduced; `SPEC.md` never
  states either.

None in `SPEC.md`: no code-token identifier it names is renamed or removed, and no section is
retitled.

## Status

Applied to `conformance/vocabulary.json` (the five entries and the group note),
`conformance/README.md` (the entry-field documentation) and `CONFORMANCE-STATEMENT-TEMPLATE.md`
(the Section 4.1 Core row). All five steps.
