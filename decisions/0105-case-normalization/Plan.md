# Plan — 0105 One lowercase, named once and cited everywhere

## Scope

`SPEC.md`: Section 4.2 "Stable Identifiers and Normalization Rules" (the rule is named and defined,
and `Normalized Issue State` cites it), Section 4.1.1's `labels` field, Section 5.3.1's
`required_labels`, Section 5.3.5's `max_concurrent_agents_by_state`, Section 8.2 "Candidate
Selection Rules", Section 8.3 "Concurrency Control", Section 11.3 "Normalization Rules", Section
16.3's `reconcile_running_issues`, and the Section 17 checks that name either normalization.

`conformance/vectors/state-normalization.json`: three vectors pinning the mapping, and a
`description` that states the operation.

`conformance/README.md`: the vector-file encoding convention, and a "Surfaced findings" entry.

`conformance/vectors/workspace-key.json`: its two non-ASCII vectors re-encoded to that convention, a
change of encoding and not of value.

`conformance/vectors/per-state-concurrency.json`: descriptions that name the rule.

No configuration key is added, removed, or re-typed, so Section 6.4's cheat sheet is unaffected.

## Steps

1. **`Lowercase Normalization` exists as a named rule in Section 4.2.** Ensure Section 4.2 carries
   an entry defining the operation as the Unicode Default Case Conversion to lowercase, using the
   full mappings rather than the simple ones, with no language-specific tailoring, citing The
   Unicode Standard's "Default Case Algorithms" by title and number. Ensure the locale-sensitive
   reading is excluded normatively (MUST NOT), naming the observable consequence — a Turkish
   tailoring maps `I` to U+0131, so `In Progress` and `in progress` stop matching on that host.
   Done-condition: a reader can compute the normalized form of a non-ASCII state from Section 4.2
   alone, and the three readings of decision 0105's Background are distinguishable from the prose.

2. **Section 4.2 states that no Unicode normalization form is applied.** Ensure the entry says the
   result is the code-point sequence the mapping produces, so two spellings differing only in
   normalization form do not compare equal. Done-condition: a reader can tell the omission is
   deliberate rather than unstated.

3. **`Normalized Issue State` cites the rule and names what tests it.** Ensure it compares after
   `Lowercase Normalization` and states that the value is a comparison key rather than a display
   string, naming `active_states`/`terminal_states` membership, `max_concurrent_agents_by_state`
   lookup, and `(from, on)` transition uniqueness. Done-condition: no site in the document tests a
   state for equality without a rule that reaches it.

4. **The label rules cite the same operation.** Ensure `labels` (Section 4.1.1), the label bullet in
   Section 11.3, and `required_labels` (Section 5.3.1) all name `Lowercase Normalization`, keeping
   their existing trimming and matching semantics unchanged. Done-condition: grepping `SPEC.md` for
   `lowercase` shows the word defining the rule and citing it, and nowhere applying it unqualified.

5. **The state-keyed configuration sites cite the rule.** Ensure `max_concurrent_agents_by_state`
   (Section 5.3.5), the per-state limit in Section 8.3, and the eligibility bullet in Section 8.2
   name the normalization they compare under. Done-condition: the `Core Conformance` check in
   Section 17.1 that asserts the override map "normalizes state names" resolves to one operation
   from the text it cites.

6. **The Section 16 reference algorithm compares normalized states.** Ensure
   `reconcile_running_issues` tests `terminal_states` and `active_states` membership on the
   normalized value rather than on `issue.state` raw, in the neutral pseudocode style Section 16
   already uses. Done-condition: the reference algorithm and Section 8.2 agree on what is compared.

7. **The Section 17 checks name the operation.** Ensure the per-state concurrency check (Section
   17.1) and the label-normalization check (Section 17.3) name `Lowercase Normalization` or its
   section, so a check asserts one behavior. Done-condition: neither check can be satisfied by an
   ASCII-only or locale-sensitive implementation.

8. **`state-normalization.json` pins the mapping.** Ensure the file's `description` states the
   operation and that vectors exist for: a full-mapping expansion that separates all three readings
   irrespective of the runner's locale (`İnceleme` → `i̇nceleme`, U+0130 → U+0069 U+0307); a
   non-ASCII single-code-point mapping that also separates lowercase from case folding (`ẞ` → `ß`,
   never `ss`); and a decomposed input whose combining mark survives, pinning step 2 (`Ünder Review`
   as U+0055 U+0308 … → U+0075 U+0308 …, never U+00FC). Ensure each vector's `description` names its
   code points, following `workspace-key.json`. Done-condition: an ASCII-only, a locale-sensitive
   and a case-folding implementation each fail at least one vector on any host.

9. **No `normalize_label` function is added.** The label rules cite the operation `normalize_state`
   already pins; a second harness entry point would re-check the same mapping, and trimming is not
   the defect under repair. Done-condition: `conformance/README.md`'s coverage table is unchanged
   and the omission is recorded, so a later slice does not read it as an oversight.

10. **Non-ASCII vector values are `\uXXXX` escapes.** A literal is silently re-composable by an
    authoring tool, which turns a normalization-form vector into a tautology that passes under every
    reading. Ensure `conformance/README.md`'s vector-file schema states the convention and why, and
    that `state-normalization.json` and `workspace-key.json` — the two files with
    normalization-sensitive vectors — follow it. Done-condition: both files are pure ASCII, and
    re-parsing each yields the same values it had before the re-encoding.

11. **`conformance/README.md` records the finding.** Ensure "Surfaced findings" carries an entry for
    Section 4.2's unqualified `lowercase`: what the readings were, that the existing corpus checked
    the locale-sensitive reading only conditionally on the runner's host, and how it is resolved.
    Done-condition: the finding is readable without reference to this decision folder.

## Cross-cutting sync

Section 6.4's cheat sheet gains nothing: no configuration key changes shape or default. Section 17
is covered by step 7, Section 18 needs no new checklist item — the checklist carries no
normalization bullet today and this decision adds no new capability, only a definition for one that
exists.

## Anchor changes

Anchors added: `Lowercase Normalization`, a Section 4.2 rule name; and the Section 16.3 pseudocode
names `normalize_state` and `normalize_states`, of which the first matches the corpus function the
vectors already dispatch on, so the reference algorithm and the corpus now name the same operation.

Nothing is renamed or removed — `Normalized Issue State`, `Workspace Key`, `labels`,
`required_labels` and `max_concurrent_agents_by_state` all keep their spellings, and the word
`lowercase` survives inside the new rule's definition. No existing reference breaks.

## Status

Applied to `SPEC.md`, `conformance/vectors/state-normalization.json`,
`conformance/vectors/per-state-concurrency.json`, `conformance/vectors/workspace-key.json` and
`conformance/README.md`.
