# Plan — 0130 The corpus names what an algorithm takes; the contract names what a caller sends

## Scope

`conformance/vcsx/vectors/policy-validation.json`, `conformance/vcsx/vectors/base-resolution.json`,
`conformance/vcsx/README.md`.

`VCSX-SPEC.md`: Section 12.4 "Resolve Base" only — one unbound name in the pseudocode. Section 8.1 is
already correct and is **not** edited.

## Steps

1. **`effectable_actions` in the vectors.** Ensure `conformance/vcsx/vectors/policy-validation.json`
   spells Section 8.1's `effectable_actions` rather than `consumer_capabilities` — in every vector's
   `given`, in the file-level `given` prose if it names the field, and in the two `notes` strings that
   gloss it (the one defining it, and the `bound_units` note that contrasts the two). Done-condition:
   `grep -c consumer_capabilities` over the file returns 0, and the vector count is unchanged at 38.

2. **`base_branch` in the vectors.** Ensure `conformance/vcsx/vectors/base-resolution.json` spells
   Section 8.1's `base_branch` rather than `supplied_base`, in the four vectors carrying it and in the
   `policy_source` note that names it. Done-condition: `grep -c supplied_base` over the file returns
   0, and the vector count is unchanged at 13.

3. **`resolve_base` binds the name it reads.** Ensure Section 12.4's `resolve_base` signature carries
   `base_branch` and its `target_branch` arm reads that parameter, rather than reading an unbound
   `supplied_base`. Keep the arm's behavior and its comment's substance unchanged — the comment states
   the value is the invocation's, else the consumer configuration's, which is what Section 8.1's
   `base_branch` is. Done-condition: no free name is read in Section 12.4, and the algorithm, Section
   8.1 and the corpus spell the value identically.

4. **The standing check.** Ensure `conformance/vcsx/README.md`'s vector-file schema description
   carries the rule as a constraint on authoring a `given` field: a field naming an invocation input
   MUST use Section 8.1's spelling, and a field naming something else — an entry point, a policy
   document, an engine-derived value — is not bound by it. Done-condition: a vector author reading the
   schema section meets the rule before writing a field name.

5. **Surfaced findings.** Ensure `conformance/vcsx/README.md`'s **Surfaced findings** section carries
   this sweep as an entry, with the three-instance count and the note that the specification needed no
   change here beyond the Section 12.4 name. Done-condition: the finding is recorded where the corpus
   records its findings, and does not rewrite the 0067 entry beside it.

## Cross-cutting sync

None. This decision adds no `Implementation-defined` obligation and no "MUST document" clause, so
`VCSX-SPEC.md` Section 13.3 and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 gain no row.
Sections 13.1 and 13.2 are unaffected: no behavior changes, and the renamed fields are corpus inputs
rather than conformance checks. `conformance/vcsx/vocabulary.json` carries no argument names, so it is
untouched.

## Anchor changes

Renamed anchors, in `conformance/vcsx/vectors/` only — neither was ever a `VCSX-SPEC.md` anchor:

- `consumer_capabilities` → `effectable_actions` (`policy-validation.json`). The target spelling is
  Section 8.1's, introduced by decision 0121.
- `supplied_base` → `base_branch` (`base-resolution.json`, and the free name in `VCSX-SPEC.md`
  Section 12.4's `resolve_base`). The target spelling is Section 8.1's.

One vector id moves with the field it names: `target_branch_resolves_from_the_supplied_base` →
`target_branch_resolves_from_the_base_branch` (`base-resolution.json`). No vector is added or removed,
and no section is renumbered.

## Status

Applied to `conformance/vcsx/vectors/policy-validation.json`,
`conformance/vcsx/vectors/base-resolution.json`, `conformance/vcsx/README.md`, and `VCSX-SPEC.md`
(Section 12.4).
