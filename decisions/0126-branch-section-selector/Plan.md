# Plan — 0126 A section cannot supply the value that selects it

## Scope

`VCSX-SPEC.md`: Section 6.10 "`[[branch]]` Sections" (what a section may carry), Section 6.11
"Validation" (the reason), Section 6.4 "`[base]` and Base Resolution" (the ordering against section
selection), Sections 13.1, 13.2.

`VCSX-CONTRACT.md`: Section 4, where `[[branch]]` sections are described at the surface.

## Steps

1. **What a section may carry.** Ensure Section 6.10's any-key rule excepts `[base]` and `[scope]`,
   and states the reason in the section's own idiom: both are inputs to the resolution that selects
   the section — `[base]` directly, `[scope] branch_pattern` through the work-branch name a
   `by_prefix` resolution reads — so a section carrying either supplies the value that decides whether
   it applies. Done-condition: the rule names the two tables and the argument is readable without
   Section 6.4 in hand.

2. **The validation reason.** Ensure Section 6.11's table carries a row for a `[[branch]]` section
   carrying `[base]` or `[scope]`, with the reason `branch_section_selector_key`. Done-condition: the
   row exists and is placed among the consistency failures, not the well-formedness ones.

3. **Why not `malformed_policy`.** Ensure the paragraph following the table covers this row where it
   already covers the others: `malformed_policy` names a well-formedness failure no other condition
   names, and this condition has a specific repair — move the key to the top level, or express the
   variation through `[base] resolve = "by_prefix"`, which resolves in one pass. Done-condition: the
   choice of a distinct reason is argued, as `base_unresolvable`'s already is.

4. **The ordering, stated once.** Ensure Section 6.4 states that base resolution runs before section
   selection and reads no `[[branch]]` section, and Section 6.10 states that selection reads the
   resolved base — so the two sections name each other's place in the order rather than each
   describing itself alone. Done-condition: an implementer reading either section learns the order.

5. **What is untouched.** Ensure Section 6.10 states that every other top-level key remains available
   in a section, the worked example being one, so the exception reads as the narrow one it is.
   Done-condition: the feature's purpose — varying the Way of Working by the branch a unit of work
   targets — is intact for hooks, edges, messages and tasks.

6. **`VCSX-CONTRACT.md` Section 4.** Ensure the surface's description of `[[branch]]` sections — "each
   matching a base-branch prefix and merging its keys over the top level" — names the exception at the
   surface's altitude. Done-condition: a reader of the surface alone does not believe every key may
   appear.

7. **Sections 13.1, 13.2.** Ensure the test matrix checks that a section carrying `[branch.base]` and
   a section carrying `[branch.scope]` are each refused with `branch_section_selector_key` before any
   operation runs; that a section carrying `[branch.messages.squash]`, a hook or an edge still applies
   and merges over the top level; and that a top-level `[base] resolve = "by_prefix"` still resolves,
   so the mechanism that replaces the refused one is exercised. Ensure the checklist's validation
   bullet names the refusal. Done-condition: steps 1, 2 and 5 each have a check.

## Cross-cutting sync

Section 8.5: a new configuration reason is a `MINOR`, absorbed through the `usage_or_config` status,
which does not change.

Section 13.3 gains nothing.

`SPEC.md`: Section 5.6 describes `repo.policy.toml` at Symphony's altitude and names no `[[branch]]`
key, so nothing there changes. Section 15.4's note that under `target_branch` these sections come from
the pull-request target is unaffected — the refusal is about which keys a section may carry, not about
where it is read from.

## Anchor changes

New anchor: the `branch_section_selector_key` configuration reason. No anchor is renamed or removed;
`[base]` and `[scope]` keep their spellings and their meanings at the top level.

## Status

Applied to `VCSX-SPEC.md` (Sections 6.4, 6.10, 6.11, 13.1, 13.2), `VCSX-CONTRACT.md` (Section 4) and
`conformance/vcsx/vocabulary.json`.
