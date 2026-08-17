# Plan — 0101 Under `target_branch` the base is an argument, not a policy key

## Scope

`VCSX-SPEC.md`: Section 6.4 "`[base]` and Base Resolution" (the three-source list is qualified by
mode), Section 8.1 "Entry Points and Arguments" (the `policy_source` and `base_branch` descriptions
state the exclusion), Section 8.6 "Invocation Preconditions" (the base's scope becomes
mode-dependent, the before-validation set becomes mode-dependent, and `base_branch_missing`'s row is
requalified), Section 12.4 `resolve_base` (the algorithm takes no `[base]` under the mode), Sections
13.1 and 13.2.

`SPEC.md`: Section 9.7 "Repository Provisioning and the VCS Engine" (the three-source
pull-request-target list), Section 15.4 "Configuration Trust Sourcing and Hook Safety" (what the mode
costs), Section 18.1 (the restatement of the same list).

`conformance/vcsx/vocabulary.json`: `precondition_reasons` — `base_branch_missing`'s meaning, and the
registry note listing the reasons established before validation.

`conformance/vcsx/vectors/`: `base-resolution.json` and `policy-validation.json`, neither of which
exercises `policy_source` today.

## Steps

1. **`[base]` and Base Resolution — the precedence list is qualified by mode.** Ensure the `branch`
   bullet's "lowest of the three in precedence" sentence states that under `policy_source =
   "target_branch"` (Section 8.1) `[base]` contributes nothing and the base resolves from the
   invocation and the consumer configuration alone, because the document `[base]` lives in is the one
   the mode locates. Done-condition: Section 6.4 names `target_branch` and no longer states the
   three-source precedence unconditionally.

2. **`[base]` and Base Resolution — `resolve` and `prefixes` are covered too.** Ensure the
   qualification is stated over the `[base]` section rather than over `branch` alone, so
   `resolve = "by_prefix"` does not reach the same cycle by a second route, and ensure it states that
   one invocation resolves one base — a policy read under the mode does not re-resolve a different
   operational base. Done-condition: the `resolve` / `prefixes` bullets are not contradicted by
   step 1's sentence.

3. **Entry Points and Arguments — `policy_source`.** Ensure the `target_branch` bullet states that the
   mode requires a base from the invocation or the consumer configuration, since the target is what
   the policy is read from, and cross-references Section 8.6 for the refusal. Done-condition: a reader
   of Section 8.1 alone learns the mode needs a base.

4. **Entry Points and Arguments — `base_branch`.** Ensure the sentence "Where no source supplies a
   base, an entry that needs one is refused before the policy runs; an entry that needs none runs
   (Section 8.6)" is qualified by mode. Done-condition: the sentence names the `target_branch` case or
   defers to Section 8.6 for it.

5. **Invocation Preconditions — the base's scope becomes mode-dependent.** Ensure the paragraph
   beginning "The base is scoped by the same rule as `git_access`" states that the scoping holds under
   `policy_source = "policy_branch"`, and that under `target_branch` a base is REQUIRED whatever the
   entry — `provision` excepted — because an entry that needs no base to do its work still needs one
   to locate the policy that governs it. Done-condition: the sentence listing `commit`, `push`,
   `pull`, `merge`, `land` and `provision` as running without one is no longer stated unconditionally.

6. **Invocation Preconditions — the before-validation set becomes mode-dependent.** Ensure the "Three
   preconditions are established **before** validation" passage states the set as
   `arguments_unreadable`, then `local_vcs_missing`, then the argument that says where the policy is
   read from — `policy_branch_missing` under the default mode and `base_branch_missing` under
   `target_branch` — and that the ordering rule below it holds for every other reason unchanged.
   Done-condition: the passage no longer asserts a fixed set of three, and `policy_branch_missing`'s
   stated reason is unchanged.

7. **Invocation Preconditions — `provision` keeps its exemption.** Ensure the `provision` paragraph
   states that the mode adds no base requirement for it, on Section 6.1's sentence: it is the
   operation that obtains the repository the policy file is in, so it performs no policy read to
   locate. Done-condition: the paragraph's exhaustive list of what `provision` establishes is
   unchanged and now says why the base is absent from it under either mode.

8. **Invocation Preconditions — the `base_branch_missing` row.** Ensure the table row reads over both
   modes: an entry that needs a base under the default mode, or any entry under `target_branch`, with
   no source supplying one. Done-condition: the row names both modes and no new row is added.

9. **`resolve_base` — the reference algorithm.** Ensure Section 12.4 shows that `base_config` is not
   consulted under `target_branch`, in the neutral pseudocode style the section already uses.
   Done-condition: the algorithm is executable against a `target_branch` invocation without reading
   `repo.policy.toml`.

10. **`SPEC.md` — the pull-request target's three sources.** Ensure Section 9.7's numbered list ("1.
    the issue... 2. `vcs.base_branch`... 3. the base branch in `repo.policy.toml`") states that the
    third does not apply under `vcs.policy_source = "target_branch"`, and that under that mode a
    target from the issue or `vcs.base_branch` is REQUIRED. Done-condition: the list is qualified
    where it is stated.

11. **`SPEC.md` — what the mode costs.** Ensure Section 15.4's `target_branch` paragraph names the
    third thing the mode gives up: the repository can no longer state its own base, so the operator
    or the issue MUST supply one. Done-condition: the paragraph's "Two things are given up" count
    matches the number of things it then lists.

12. **`SPEC.md` — Section 18.1's restatement.** Ensure the conformance bullet restating "the
    pull-request target resolves from the issue, then `vcs.base_branch`, then `repo.policy.toml`"
    carries the same qualification. Done-condition: `grep -n 'repo.policy.toml' SPEC.md` shows no
    unqualified restatement of the three sources.

13. **`conformance/vcsx/vocabulary.json`.** Ensure `base_branch_missing`'s `meaning` states the
    mode-dependent scope and that it is established before validation under `target_branch`, and
    ensure the `precondition_reasons` note's list of the reasons established before validation says
    the third is mode-dependent. Done-condition: the note and the entry agree with Section 8.6.

14. **`conformance/vcsx/vectors/base-resolution.json`.** Ensure vectors exercise the mode: a
    `target_branch` invocation resolving the base from `base_branch`; one resolving it from the
    consumer configuration; one where `[base] branch` is present and ignored; one with
    `resolve = "by_prefix"` present and ignored. Done-condition: `python3 -c "import json; d =
    json.load(open('conformance/vcsx/vectors/base-resolution.json')); print(sum('policy_source' in
    json.dumps(v) for v in d['vectors']))"` is non-zero.

15. **`conformance/vcsx/vectors/policy-validation.json`.** Ensure a vector covers the refusal: under
    `target_branch`, no base from any source, an entry that needs none for its work, yielding
    `base_branch_missing` before validation. Done-condition: the vector exists and names the reason.

## Cross-cutting sync

Section 13.1's base-branch row gains the mode-dependent scope and the before-validation placement;
Section 13.2's checklist gains the same. `SPEC.md`'s config cheat sheet entry for
`vcs.policy_source` / `vcs.base_branch` is covered by steps 10–12. Section 13.3 gains nothing: no
choice is delegated.

## Anchor changes

None. No token is renamed, added or removed: `base_branch_missing`'s scope widens and
`policy_branch_missing`'s is unchanged.

## Status

Applied to `VCSX-SPEC.md`, `SPEC.md`, `conformance/vcsx/vocabulary.json` and the two vector files.
