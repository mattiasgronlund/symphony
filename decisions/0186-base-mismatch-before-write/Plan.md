# Plan — 0186 The identity check that runs after the write it guards

## Scope

- **`VCSX-SPEC.md`:**
  - Section 4.1 (Operation Set), the `integrate` and `push` bullets;
  - Section 4.3 (Reason-Token Registry), the `(any forge)` paragraph and the table;
  - Section 9.1 (VCS Backend Plugin), the paragraph on `pr_state`'s readers;
  - Section 9.2 (Forge Backend Plugin), the `pr_state` bullet;
  - Sections 13.1 (Test Matrix) and 13.2 (Implementation Checklist).
- **`SPEC.md`:**
  - Section 9.8 (Git Automation and Work Branch);
  - Section 9.10 (Forge Operations, Pull Requests, and Review Writes);
  - Section 14.2 (Recovery Behavior);
  - Section 16.6 (Worker Attempt (Workspace + Prompt + Agent));
  - Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry) and Section 18.1.3 (Daemon
    Conformance).
- **Conformance data:**
  - `conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`;
  - `conformance/vcsx/vectors/front-end-sequence.json`.

`VCSX-CONTRACT.md` is unchanged, because it defers the reason registry (its Section 11). No
`integrate` argument is added, so `VCSX-SPEC.md` Section 8.1 is unchanged.

## Steps

1. **`integrate` refuses a base mismatch.** Ensure `VCSX-SPEC.md` Section 4.1's `integrate` bullet
   says that, where a forge is configured, the operation reads `pr_state` first. An open pull request
   targeting another base refuses as `integrate:base_mismatch` before the work branch is touched, and
   an undetermined state reports `integrate:failed`.
2. **`push` refuses a base mismatch.** Ensure the `push` bullet adds `push:base_mismatch` for an
   open pull request targeting a base other than the one the invocation resolved, and says that an
   invocation that resolved no base is not refused on that ground.
3. **Registry.**
   - Ensure Section 4.3's `(any forge)` paragraph names `integrate`.
   - Ensure the table has rows `integrate` / `base_mismatch` and `push` / `base_mismatch`, both
     `needs_caller` / `human_review`.
   - Ensure the `create_pr` / `base_mismatch` row reads `needs_caller` / `human_review`.
4. **Readers of `pr_state`.**
   - Ensure Section 9.2's `pr_state` bullet says an undetermined state refuses `integrate`, `push`
     and `create_or_update_pr`.
   - Ensure the Section 9.1 paragraph beginning "`pr_state` has" counts four readers, three of
     which act on the answer.
   - Ensure the 13.1 and 13.2 conditional-read items name `integrate` among the reads presented no
     validator.
5. **`VCSX-SPEC.md` Sections 13.1 and 13.2.**
   - Ensure the operations-and-reasons item states the three refusals, the untouched work branch,
     `integrate:failed` on an undetermined state, and the base-less `push`.
   - Ensure a checklist item follows the one beginning "The forge backend's pull-request read".
6. **`SPEC.md` Section 9.8.** Ensure a back-merge bullet follows "it is postponed so the agent is
   not interrupted up front". It says the engine refuses `integrate:base_mismatch` before touching
   the work branch, that Symphony parks the issue, and why the check precedes the back-merge.
7. **`SPEC.md` Section 9.10.**
   - Ensure a bullet follows the refusal bullet. It says `integrate`, `push` and `create_pr` refuse
     as `base_mismatch`, that Symphony surfaces each as `pr_identity_mismatch` and parks, and that an
     undetermined state reports `failed`.
   - Ensure a `Note:` follows the concurrency paragraph. It says a base mismatch needs no second
     writer, names the two repairs, and says closing the pull request is not one on its own.
8. **`SPEC.md` Section 14.2.** Ensure a bullet for the three `base_mismatch` results follows the
   `await_checks` bullet: parked, not retried and not failed, with the repair cited to Section 9.10.
9. **`SPEC.md` Section 16.6.** Ensure `integrate:base_mismatch` takes an arm calling `park_run` with
   `pr_identity_mismatch` before the hooks run.
10. **`SPEC.md` Sections 17.4 and 18.1.3.** Ensure a check and an item state the park at run start,
    the later refusals, and that none of them is retried or failed.
11. **Conformance data.**
    - Ensure `conformance/vcsx/vocabulary.json` holds `integrate:base_mismatch`,
      `integrate:rate_limited`, `integrate:forge_unavailable` and `push:base_mismatch`, with
      `create_pr:base_mismatch` re-classed.
    - Ensure the group note names `integrate` and `await_checks` among the `forge_universal`
      operations.
    - Ensure `conformance/vcsx/README.md` counts 47 rows, 80 entries, and 22 rows with a need
      yielding 33 entries.
    - Ensure `front-end-sequence.json` has `push_base_mismatch_builtin`.

    Done when `python3 scripts/validate_spec_consistency.py` reports no errors.

## Cross-cutting sync

- **`SPEC.md` Section 6.4**: no configuration key changes.
- **`SPEC.md` Sections 17 and 18**: step 10.
- **`VCSX-SPEC.md` Sections 13.1 and 13.2**: step 5.
- **`VCSX-SPEC.md` Section 13.3 and both Conformance Statement templates**: no row owed. Nothing is
  `Implementation-defined`.

## Anchor changes

- Added: `integrate:base_mismatch`, `push:base_mismatch`, `integrate:rate_limited` and
  `integrate:forge_unavailable` (`VCSX-SPEC.md` Section 4.3, `conformance/vcsx/vocabulary.json`).
- Changed: `create_pr:base_mismatch`'s class, from `error` to `needs_caller`, with default need
  `human_review`. This is a change to the major-stable surface (`VCSX-SPEC.md` Section 8.5).
- Added: `park_run` in `SPEC.md` Section 16.6's pseudocode.
