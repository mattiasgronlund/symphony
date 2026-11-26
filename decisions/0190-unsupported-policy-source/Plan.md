# Plan — 0190 A policy source the implementation does not support

## Scope

This plan is applied on top of decision 0189 and depends on the vectors and the `given` shape 0189
adds to `conformance/vectors/config-preflight.json`.

- **`SPEC.md`:**
  - Section 6.3 (Dispatch Preflight Validation): the checks list, the reason table, and the order
    paragraph;
  - Section 6.4 (Core Config Fields Summary (Cheat Sheet)), the `vcs.policy_source` row;
  - Section 9.7 (Repository Provisioning and the VCS Engine), the `policy_source` field;
  - Section 15.4 (Configuration Trust Sourcing and Hook Safety), the paragraph beginning "An operator MAY set";
  - Section 17.1 (Workflow and Config Parsing);
  - Section 18.1.3 (Daemon Conformance) and Section 18.1.4 (VCS Engine).
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`:** Section 4.1 (Core), one row.
- **Conformance data:**
  - `conformance/vocabulary.json`, the `config_error_reasons` group;
  - `conformance/vectors/config-preflight.json`;
  - `conformance/README.md`, the harness contract's interpretation notes.

`VCSX-SPEC.md` and `VCSX-CONTRACT.md` are unchanged (see `Background.md`, Not done here).

## Steps

1. **The decline rule, in `SPEC.md` Section 15.4.** Ensure that the paragraph beginning "An operator
   MAY set" is followed by text stating:
   - Whether an implementation supports `target_branch` is `Implementation-defined`, and an
     implementation MUST document it.
   - An implementation that supports the mode MUST behave as Sections 9.7 and 15.4 state.
   - One that declines it refuses it at dispatch preflight with `unsupported_policy_source` (Section
     6.3).
   - `policy_branch` is always supported.
   - Why declining is permitted: an implementation that cannot be configured into the mode
     guarantees that no configuration puts the trust root on a branch the service merges into.

   Done when Section 15.4 names `unsupported_policy_source`.
2. **`SPEC.md` Section 9.7, the `policy_source` field.** Ensure a sub-bullet of the `policy_source`
   field says that an implementation MAY decline `target_branch` (Section 15.4), and that a value
   the implementation does not support, including one outside the two, is refused at preflight
   rather than read as the default (Section 6.3).
3. **`SPEC.md` Section 6.4, the `vcs.policy_source` row.** Ensure the row ends by naming the decline
   and the preflight refusal, citing Sections 6.3 and 15.4.
4. **`SPEC.md` Section 6.3, the checks list.** Ensure a bullet sits between the `Repository Key`
   bullet and check 3. It says:
   - Every `repository` entry's `vcs.policy_source`, after resolution against the orchestrator level
     (Section 5.3.7), names a policy source the implementation supports (Sections 9.7, 15.4);
     otherwise configuration error.
   - A value outside `policy_branch` | `target_branch` is refused, never read as the default. The
     rule that unknown keys SHOULD be ignored (Section 5.3) concerns keys, not values.
5. **`SPEC.md` Section 6.3, the reason table.** Ensure a row between `invalid_repository_key` and
   `missing_vcs_field` reads: a `vcs.policy_source` names a policy source the implementation does
   not support (Sections 9.7, 15.4) → `unsupported_policy_source`.
6. **`SPEC.md` Section 6.3, the order paragraph.** Ensure the paragraph beginning "Where several
   conditions hold at once" says that, within each entry's resolved `vcs`, the policy source is read
   first, because it fixes which fields check 3 requires.
7. **`SPEC.md` Section 17.1.** Ensure a row says:
   - A `vcs.policy_source` outside the two values, or a declined `target_branch`, fails with
     `unsupported_policy_source`.
   - It is reported ahead of `missing_vcs_field` and every later condition.
   - A supported `target_branch` passes the check.
8. **`SPEC.md` Section 18.1.3.**
   - Ensure the item beginning "Dispatch preflight surfaces the reason token" counts fourteen
     conditions.
   - Ensure an item states the policy-source refusal, its position ahead of check 3, and that a
     misspelt value is not read as the default.
9. **`SPEC.md` Section 18.1.4.** Ensure the `vcs.policy_source` item scopes its `target_branch`
   clauses to an implementation that supports the mode (Section 15.4).
10. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 (Core).** Ensure a row reads
    `Whether vcs.policy_source = target_branch is supported`, citing Section 15.4, with the
    resolution `<supported / declined, refused at preflight>`.
11. **`conformance/vocabulary.json`, `config_error_reasons`.** Ensure an `unsupported_policy_source`
    entry sits between `invalid_repository_key` and `missing_vcs_field`, with the Section 6.3
    condition. Ensure the group's `spec_refs` names `SPEC.md` Section 15.4, and that the group's
    `note`, where it gives the order, says the policy source is read first within each entry's
    resolved `vcs`.
12. **`conformance/vectors/config-preflight.json`.**
    - Ensure `given` carries `supported_policy_sources?` at the top level, beside `descriptor`.
    - Ensure a note says three things. The field is what the implementation's Conformance Statement
      declares, and an absent field means `["policy_branch"]`. A vector is run against its own set,
      never skipped. The corpus does not check the implementation's real set; the Conformance
      Statement does.
    - Ensure `spec_refs` names Section 15.4.
    - Ensure `valid-target-branch-mode-without-policy-branch` states
      `["policy_branch", "target_branch"]`.
    - Ensure four new vectors: `unsupported-policy-source-declined`,
      `unsupported-policy-source-outside-type`, `order-policy-source-before-vcs-field`, and
      `order-policy-source-before-tracker-kind`, as `Background.md` defines them.
    - Ensure the file's note on `order-*` vectors counts five.

    Done when the file holds 31 vectors.
13. **`conformance/README.md`, Harness contract.** Ensure the interpretation notes carry a
    `validate_dispatch_config` entry. It says that `supported_policy_sources` is an input like
    `descriptor`, that an absent field means `["policy_branch"]`, and that every vector is run
    whatever the implementation declares.

14. **References to the `vcs` fields check by its position.** Step 4 makes that check the fourth
    bullet of Section 6.3's list, so nothing may call it the third. Ensure the `SPEC.md` Section
    17.1 row beginning "A required `vcs` field that is empty", the `SPEC.md` Section 18.1.3 item
    beginning "Dispatch preflight refuses an absent or empty", the `config-preflight.json` note
    beginning "vcs.policy_source is" and the `empty-vcs-policy-branch` description name the check
    by what it checks, the required `vcs` fields, rather than by ordinal.

    Done when `python3 scripts/validate_spec_consistency.py` reports no errors and "third check"
    occurs in neither `SPEC.md` nor `conformance/vectors/config-preflight.json`.

## Cross-cutting sync

- **`SPEC.md` Section 6.4:** step 3.
- **`SPEC.md` Sections 17 and 18:** steps 7 to 9.
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`:** step 10, for the one new `Implementation-defined`
  obligation (decision 0128).
- **`VCSX-SPEC.md` Section 13:** unchanged.

## Anchor changes

- Added: `unsupported_policy_source` (`SPEC.md` Section 6.3, `conformance/vocabulary.json`).
- Added: the input `supported_policy_sources?` and four vectors
  (`conformance/vectors/config-preflight.json`).
- Changed: `target_branch` support moves from REQUIRED (Section 18.1.4) to `Implementation-defined`
  (Section 15.4).

## Plan review

First pass, `check_plan_anchors.py --rev HEAD` against `b480096`. R reported `conformance/README.md:699`, which
carries the same order wording. It needs no change: the line is in the README's Surfaced findings,
a historical account of decision 0164, and restating it would rewrite history.

Second pass, after 0189 merged, against `c45aa32`: 0 findings from 8 quoted spans.

- **C:** sibling worktree; Sections 6.4, 17 and 18 named; the one new `Implementation-defined`
  obligation has its template row (step 10), placed after the Section 15.4 rows.
- **P, the ordinal.** 0189 wrote "Section 6.3's third check" into `SPEC.md` Sections 17.1 and
  18.1.3 and into two places in the vector file. Step 4 puts a bullet ahead of that check, and every
  one of the four would then name the policy-source check instead. Step 14 renames them by identity.
- **P, the vocabulary note.** The `config_error_reasons` note restates the order and gives its
  reason. Step 6 changes that reason in `SPEC.md`, and the note would keep the old one. It is
  folded into step 11.
- **P, kept unchanged:** the `target_branch` rules in Sections 9.7, 9.10, 15.4 and 18.1.4, and
  0189's statement that a `target_branch` deployment with no `vcs.policy_branch` passes the `vcs`
  fields check. Each is stated under the mode, which a decliner refuses before any of them is
  reached, so each still holds for an implementation that supports the mode, and none needs a
  decliner's exception. `VCSX-SPEC.md`'s `target_branch` sites are the engine's, and the engine
  still implements both modes (`Background.md`).

## Status

Applied to `SPEC.md`, `CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/vocabulary.json`,
`conformance/vectors/config-preflight.json` and `conformance/README.md` on branch
`0190-unsupported-policy-source`.
