# Plan — 0183 An allow-list of patterns with no pattern syntax

## Scope

- `VCSX-SPEC.md`: Section 8.1 (Entry Points and Arguments), the `base_branch_allowed` argument, which
  holds the syntax; and Sections 13.1 (Test Matrix) and 13.2 (Implementation Checklist).
- `SPEC.md`: Section 9.7 (Repository Provisioning and the VCS Engine), which points to the engine's
  definition; Section 6.3 (Dispatch Preflight Validation), which gains a check and its reason; Section
  6.4 (Core Config Fields Summary (Cheat Sheet)); Section 17.2 (Workspace Manager and Safety); and
  Section 18.1 (REQUIRED for Conformance).
- Conformance data:
  - `conformance/vocabulary.json` and `conformance/vectors/config-preflight.json`;
  - `conformance/vcsx/vocabulary.json`;
  - a new `conformance/vcsx/vectors/base-branch-allowed.json`, registered in
    `conformance/vcsx/README.md`.

`VCSX-CONTRACT.md` is unchanged, because it defers the bound to the engine.

## Steps

1. **`VCSX-SPEC.md` Section 8.1 defines the syntax.** Ensure the `base_branch_allowed` bullet carries
   three nested bullets:
   - each entry is a glob in the syntax of a gitignore pattern, with the rules for `*`, `?`, `[...]`
     (negated by `!` or `^`), `\` and `**` (special only as a whole segment), literal braces, and
     case-sensitive matching;
   - an entry matches the whole name, being "a gitignore pattern's glob, not a gitignore line", so
     `main` does not admit `release/main`;
   - an entry beginning with an unescaped `!`, or one that is not well formed, makes every supplied
     base `base_branch_not_permitted`.

   Done when the three bullets are present under `base_branch_allowed`.
2. **`SPEC.md` Section 9.7 defers to it.** Ensure the `base_branch_allowed` field gains two nested
   bullets: one says that each entry uses the syntax `VCSX-SPEC.md` Section 8.1 states, and that
   Symphony applies the same match when it refuses a per-issue target; the other says that a negated
   or ill-formed entry is a configuration error (Section 6.3). Done when both bullets follow
   `Default: unset — a per-issue target is otherwise unbounded`.
3. **`SPEC.md` Section 6.3 checks it.** Ensure the validation checks include one for
   `vcs.base_branch_allowed` entries, placed after the resolved-`vcs` check, and that the table has
   the row `invalid_base_branch_pattern` directly after `missing_vcs_field`. The stated order ("then
   each entry's resolved `vcs`") already covers its position. Done when the token appears in both the
   list and the table.
4. **Cheat sheet.** Ensure Section 6.4's `vcs.base_branch_allowed` line names the entry syntax by
   reference to `VCSX-SPEC.md` Section 8.1.
5. **Tests and checklist.**
   - Ensure `SPEC.md` Section 17.2's pull-request-target bullet asserts whole-name matching, and that
     Symphony and the engine refuse the same targets.
   - Ensure Section 18.1's dispatch-preflight item counts thirteen conditions.
   - Ensure `VCSX-SPEC.md` Section 13.1's base-branch bullet gives the whole-name examples and the
     whole-bound refusal.
   - Ensure Section 13.2's base-resolution item names the match.
6. **Conformance data.**
   - Ensure `conformance/vocabulary.json` lists `invalid_base_branch_pattern` after
     `missing_vcs_field`, and that `config-preflight.json` holds valid, negated, unclosed-bracket and
     escaped-`!` vectors.
   - Ensure `conformance/vcsx/vocabulary.json`'s `base_branch_not_permitted` and
     `base_branch_allowed` entries state the match.
   - Ensure `base-branch-allowed.json` exists with function `base_branch_permitted` and is listed in
     the slice table.

   Done when `python3 scripts/validate_spec_consistency.py` reports no errors.

## Cross-cutting sync

- **Section 6.4**: step 4. **Sections 17 and 18**: step 5. **`VCSX-SPEC.md` Sections 13.1 and
  13.2**: step 5.
- **Conformance Statement templates**: no row owed. The syntax is fixed, not
  `Implementation-defined`, and no MUST-document obligation is added.
- **`VCSX-SPEC.md` Section 13.3**: unaffected, for the same reason.

## Anchor changes

- Added: `invalid_base_branch_pattern` (`SPEC.md` Section 6.3).
- Added: `base_branch_permitted`, the vector function in
  `conformance/vcsx/vectors/base-branch-allowed.json`.

Nothing is renamed or removed.
