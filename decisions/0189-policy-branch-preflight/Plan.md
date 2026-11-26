# Plan — 0189 Check 3 reaches `vcs.policy_branch`, and the corpus says so

## Scope

- **`SPEC.md`:**
  - Section 6.3 (Dispatch Preflight Validation), the third validation check;
  - Section 17.1 (Workflow and Config Parsing), the `vcs.local_vcs` row;
  - Section 18.1.3 (Daemon Conformance), the dispatch-preflight items.
- **Conformance data:** `conformance/vectors/config-preflight.json`.

The reason table in `SPEC.md` Section 6.3 is unchanged: its `missing_vcs_field` condition is stated
over "unresolved", which this decision defines and does not reword. No token is added, so
`conformance/vocabulary.json` and the `SPEC.md` Section 18.1.3 count of thirteen conditions are
unchanged.

## Steps

1. **`SPEC.md` Section 6.3, check 3.** Ensure the bullet beginning "The `vcs` fields Section 9.7
   requires are resolved" names the conditional field next to its example. A deployment supplying
   no `vcs.local_vcs` for one repository, or under the default `vcs.policy_source` no
   `vcs.policy_branch`, fails configuration rather than defaulting one for it. Ensure it also says:
   - A required field is unresolved when absent or empty.
   - A value with any character in it is resolved, and a malformed one is judged where its value is
     used.
   - Under `policy_source = "target_branch"` check 3 does not reach `vcs.policy_branch`
     (Section 9.7).

   Done when the bullet names `vcs.policy_branch` and states the empty rule.
2. **`SPEC.md` Section 17.1 (Workflow and Config Parsing).** Ensure the row ending "fails
   configuration rather than defaulting one" also covers a default-mode deployment supplying no
   `vcs.policy_branch`. Ensure a row follows it saying:
   - An empty required `vcs` field fails check 3 with `missing_vcs_field`.
   - A whitespace-only one is resolved for check 3.
   - A `target_branch` deployment with no `vcs.policy_branch` passes check 3.
3. **`SPEC.md` Section 18.1.3 (Daemon Conformance).** Ensure an item follows the one beginning
   "Dispatch preflight surfaces the reason token". It states that preflight refuses an absent or
   empty `vcs.policy_branch` under the default policy source with `missing_vcs_field`, that the
   empty rule covers every field check 3 reads, and that the key is not required under
   `target_branch` (Sections 6.3, 9.7).
4. **`conformance/vectors/config-preflight.json`, shape and notes.**
   - Ensure `given` reads `vcs: { local_vcs, policy_source?, policy_branch?, base_branch_allowed? }`.
   - Ensure a note says that an absent `policy_source` means `policy_branch` (`SPEC.md` Section 9.7).
     The note also says that a required field is unresolved when absent (omitted or `null`, as
     `missing-vcs-field` already writes it) or empty, and that every vector with a repository entry
     states `policy_branch` unless the vector is about it.
   - Ensure `spec_refs` still lists Section 9.7.
5. **The 22 existing vectors.** Ensure every vector with a repository entry carries
   `"policy_branch": "policy"` beside `local_vcs`. The exceptions are the new vectors of step 6 that
   are about the key. Done when only `no-repository-configured` and
   `order-repository-before-agent-command` lack it, each having no repository entry.
6. **New vectors.** Ensure, placed after `missing-vcs-field`:
   - `missing-vcs-policy-branch`: `vcs: { local_vcs: "git" }`, expecting `missing_vcs_field`.
   - `empty-vcs-policy-branch`: `vcs: { local_vcs: "git", policy_branch: "" }`, expecting
     `missing_vcs_field`.
   - `valid-target-branch-mode-without-policy-branch`:
     `vcs: { local_vcs: "git", policy_source: "target_branch" }`, expecting valid. Its description
     says the target that mode REQUIRES is judged per issue, at dispatch, not at preflight
     (Section 9.7), since the issue may supply it.

   Done when the file holds 27 vectors and `python3 scripts/validate_spec_consistency.py` reports no
   errors.

## Cross-cutting sync

- **`SPEC.md` Section 6.4:** no key changes. The `vcs.policy_branch` and `vcs.policy_source` rows
  already state the conditional requirement and the default.
- **`SPEC.md` Sections 17 and 18:** steps 2 and 3.
- **Conformance Statement templates:** no row owed. Nothing is `Implementation-defined`.
- **`conformance/README.md`:** the file table carries no vector count, so it is unchanged.

## Anchor changes

- Added: the vectors `missing-vcs-policy-branch`, `empty-vcs-policy-branch` and
  `valid-target-branch-mode-without-policy-branch` (`conformance/vectors/config-preflight.json`).
- Changed: that file's `given` shape gains `policy_source?` and `policy_branch?`.

## Plan review

`check_plan_anchors.py --rev HEAD` against `b480096`: 0 findings from 11 quoted spans.

- **C:** sibling worktree; Sections 6.4, 17 and 18 named; no `Implementation-defined` obligation,
  so no template row.
- **P:** the reason table is kept unchanged on the premise that "unresolved" is defined elsewhere;
  its producer is step 1's empty rule in check 3. Two gaps were folded in:
  - The file writes an absent field as `null` (`missing-vcs-field`) as well as by omission, so the
    step 4 note names both.
  - The `target_branch` vector is valid although Section 9.7 REQUIRES a target under that mode with
    no `vcs.base_branch` here. That requirement is judged per issue at dispatch, because the issue
    may supply the target, so the step 6 description says so rather than leaving it to read as a
    preflight gap.

## Status

Applied to `SPEC.md` and `conformance/vectors/config-preflight.json` on branch
`0189-policy-branch-preflight`.
