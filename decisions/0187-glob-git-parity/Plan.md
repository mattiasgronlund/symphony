# Plan — 0187 A glob with git as its reference, and five places it is not git's

## Scope

- `VCSX-SPEC.md`:
  - Section 8.1 (Entry Points and Arguments), the `base_branch_allowed` argument and its three
    nested bullets, which hold the syntax;
  - Sections 13.1 (Test Matrix) and 13.2 (Implementation Checklist).
- `SPEC.md`:
  - Section 9.7 (Repository Provisioning and the VCS Engine), the `base_branch_allowed` field;
  - Section 6.4 (Core Config Fields Summary (Cheat Sheet));
  - Section 17.2 (Workspace Manager and Safety).
- Conformance data:
  - `conformance/vcsx/vectors/base-branch-allowed.json`;
  - `conformance/vcsx/vocabulary.json`;
  - `conformance/vectors/config-preflight.json`.

These stay unchanged:

- `VCSX-CONTRACT.md`, which defers the bound to the engine.
- `SPEC.md` Section 6.3 (Dispatch Preflight Validation). Its check says "is a well-formed pattern"
  by reference to Section 9.7, so the new not-well-formed cases reach it with no edit, and
  `invalid_base_branch_pattern` keeps its meaning.
- `SPEC.md` Section 18.1 (REQUIRED for Conformance). It still counts thirteen conditions.

## Steps

1. **`VCSX-SPEC.md` Section 8.1 states the glob over bytes, with git's bracket grammar.**
   - Ensure the first nested bullet under `base_branch_allowed` ("Each entry is a glob in the syntax
     of a gitignore pattern") states:
     - that matching is byte by byte: `*` matches any run of bytes other than `/`, `?` one byte other
       than `/`, and `[...]` one byte;
     - that `[...]` holds members, ranges `lo-hi` and the classes `[:alnum:]`, `[:alpha:]`,
       `[:blank:]`, `[:cntrl:]`, `[:digit:]`, `[:graph:]`, `[:lower:]`, `[:print:]`, `[:punct:]`,
       `[:space:]`, `[:upper:]` and `[:xdigit:]`, each with its ASCII meaning;
     - that a leading `!` or `^` negates the set, and the set never matches `/`;
     - that a `]` straight after the opening `[`, or after its `!` or `^`, is a member;
     - that a `-` first, last, or directly after a range or a class is a member;
     - that `\` makes the next byte literal inside a set as outside one.
   - Ensure the same bullet states `**`'s rule as a whole segment: the name's start or a `/` before
     it, and the name's end or a `/` after it. The three existing forms stay as its instances, and a
     bare `**` matches every name.
   - Done when the bullet contains "byte" and `[:alpha:]`, and no longer says that `?` matches "one
     character".
2. **Section 8.1's not-well-formed list names the new cases.**
   - Ensure the bullet beginning "An entry beginning with an unescaped `!`" lists, beside "an
     unclosed `[`" and "a trailing unescaped `\`":
     - a range whose first endpoint is above its second;
     - an unknown class name.
   - Ensure it states that `[]` and `[!]` are unclosed under the `]`-first rule.
   - Done when the list holds four kinds and names `[]`.
3. **Section 8.1 says what an empty bound means.**
   - Ensure the `base_branch_allowed` bullet states that a bound configured as an empty set admits no
     base, so every supplied `base_branch` is `base_branch_not_permitted`.
   - Ensure it states that an unconfigured bound bounds nothing but the `policy_branch` exclusion,
     and that the two are distinct.
   - Done when the bullet contains "empty".
4. **`SPEC.md` Section 9.7 says the same for `vcs.base_branch_allowed`.**
   - Ensure the field's `Default: unset — a per-issue target is otherwise unbounded` line is
     followed by a nested bullet stating that a configured empty list permits no per-issue target.
   - Done when the field's bullets say what an empty list means.
5. **Cheat sheet.**
   - Ensure Section 6.4's `vcs.base_branch_allowed` line, after its "default unset (unbounded)",
     adds that an empty list admits no target.
6. **Tests and checklist.**
   - Ensure `VCSX-SPEC.md` Section 13.1's base-branch bullet, the one containing "`release**`
     admits `release-1`", also asserts:
     - `a/?` does not admit `a/é`;
     - `[[:alpha:]]` admits `a`;
     - a bound holding `[z-a]`, `[]` or `[[:bogus:]]` refuses every supplied base;
     - a bare `**` admits `release/1.2`;
     - a configured empty bound refuses every supplied base.
   - Ensure Section 13.2's base-resolution item names byte matching and the empty bound.
   - Ensure `SPEC.md` Section 17.2's pull-request-target bullet, the one containing "`release/*`
     does not admit `release/1.2/hotfix`", asserts that a configured empty `vcs.base_branch_allowed`
     refuses every per-issue target while an unset one refuses none but `vcs.policy_branch`.
7. **`base-branch-allowed.json`.**
   - Ensure `notes[0]` names the method as git's `t/helper/test-tool wildmatch wildmatch <base>
     <entry>` at git 2.56.1, and gives the reason `for-each-ref` is not used: `match_name_as_path`
     prefix-matches a plain entry.
   - Ensure vectors exist, by id, for:
     - `question_mark_matches_one_byte`: `a/?` refuses `a/é`;
     - `two_question_marks_match_a_two_byte_character`: `a/??` admits `a/é`;
     - `posix_class_matches_its_ascii_members`;
     - `unknown_posix_class_refuses_every_base`;
     - `reversed_range_refuses_every_base`;
     - `close_bracket_first_is_a_member`: `[]]` admits `]`;
     - `empty_brackets_are_unclosed`: `a/[]` refuses every base;
     - `dash_after_a_range_is_a_member`: `a/[a-c-m]` admits `a/-`, and `a/d` is refused;
     - `backslash_escapes_inside_brackets`: `a/[a\-c]` refuses `a/b`;
     - `bare_double_star_matches_every_name`: `**` admits `release/1.2`;
     - `plain_entry_does_not_admit_a_branch_below_it`: `release` refuses `release/1.2`;
     - `empty_bound_admits_no_base`: `base_branch_allowed` `[]` refuses `main`.
   - Done when every well-formed, non-negated vector, re-run with `test-tool wildmatch wildmatch`,
     agrees with its `expect`.
8. **Vocabularies.**
   - Ensure `conformance/vcsx/vocabulary.json`'s `base_branch_allowed` note says the match is over
     bytes and that an empty set admits no base.
   - Ensure the `base_branch_not_permitted` meaning includes the empty bound.
   - Ensure `conformance/vectors/config-preflight.json` holds one vector refusing a reversed range as
     `invalid_base_branch_pattern`, and one admitting an empty `vcs.base_branch_allowed` as valid
     configuration.
   - Done when `python3 scripts/validate_spec_consistency.py` reports no errors.

## Cross-cutting sync

- **Section 6.4**: step 5. **Sections 17 and 18**: step 6, and Section 18.1 is unchanged.
  **`VCSX-SPEC.md` Sections 13.1 and 13.2**: step 6.
- **Conformance Statement templates**: no row owed. Every answer is fixed. None is
  `Implementation-defined`, and no MUST-document obligation is added.
- **`VCSX-SPEC.md` Section 13.3**: unaffected, for the same reason.

## Anchor changes

- Added: the twelve vector ids in step 7, in `conformance/vcsx/vectors/base-branch-allowed.json`.

Nothing is renamed or removed. `question_mark_matches_one_character` keeps its id; its entry and base
are ASCII, so bytes and characters agree on it.

## Status

Not started.
