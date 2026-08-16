# Plan — 0097 Where the policy comes from, when it is read, and what happens when it cannot be

## Scope

`VCSX-SPEC.md`: Sections 3.2 "Execution Contexts (Trust)", 4.1 "Operation Set", 6.1 "File Discovery
and `vcsx.toml` Merge", 6.10 "Validation", 8.1 "Entry Points and Arguments", 13.1 "Test Matrix",
13.2 "Implementation Checklist", 13.3 "Conformance Statement".

`SPEC.md`: Sections 5.6 "`repo.policy.toml` (Repository Way of Working)", 6.2 (dynamic reload),
6.4 "Configuration Cheat Sheet", 9.7 "Repository Provisioning and the VCS Engine", 14.1 "Failure
Taxonomy", 14.2 (recovery), 15.4 "Configuration Trust Sourcing and Hook Safety", 17 "Test Matrix",
18 "Implementation Checklist".

`VCSX-CONTRACT.md`: Sections 4, 6, 10.

`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`,
`conformance/vcsx/vectors/policy-validation.json`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## Tokens introduced

- `policy_source` — consumer configuration value, `policy_branch` | `target_branch`. `SPEC.md`
  operator key `vcs.policy_source`.
- `load_policy` — the engine operation returning the merged host-side surface, called once per unit
  of work.
- `policy_source_unreadable`, `policy_not_found` — configuration reasons (Section 6.10).

## Steps

1. **`policy_source` (`VCSX-SPEC.md` Section 8.1; `SPEC.md` Sections 9.7, 6.4)** — ensure the
   consumer configuration carries a named mode with `policy_branch` as the default, ensure
   `policy_branch` is REQUIRED only under that mode, and ensure `policy_branch_is_target` is not an
   error under `target_branch`. *Done when* both modes are named and every rule 0094 and 0096 stated
   about the policy branch says which mode it holds under.

2. **What the opt-out gives up (`SPEC.md` Section 15.4)** — ensure the specification states, in its
   own sentence, that under `target_branch` the merge path to the trust root reopens and any
   per-branch section becomes authorable by whoever can land a pull request. *Done when* an operator
   choosing the mode can read its cost without deriving it.

3. **Load once at work start (`VCSX-SPEC.md` Sections 4.1, 6.1, 8.1)** — ensure the merged host-side
   surface is obtained once per unit of work through `load_policy` and supplied to subsequent
   invocations, rather than discovered and read per invocation. Ensure Section 6.1's "the engine
   discovers and reads" is reconciled with Section 3.2's "the consumer sources config by trust" in
   the latter's favour. *Done when* no invocation but `load_policy` reads the repository, and no
   Section 9.1 capability is required to read a file at a revision.

4. **`WORKFLOW.md` timing only (`SPEC.md` Sections 5.2, 15.4)** — ensure it loads at work start with
   the policy and remains worktree-sourced. *Done when* the in-sandbox trust split is unchanged and
   only the cadence differs.

5. **Reload restated (`SPEC.md` Section 6.2)** — ensure the dynamic-reload requirement no longer
   asks for change detection over a remote ref; ensure it states that the policy in force for a unit
   of work is the one read at its start, and that a change takes effect for work started afterwards.
   Ensure operator-config and `WORKFLOW.md` reload keep their existing behavior where they are still
   local. *Done when* nothing requires watching a branch.

6. **Four causes, one resolution (`VCSX-SPEC.md` Sections 6.1, 6.10)** — ensure a policy source that
   cannot be read, a policy that cannot be found, one that does not parse, and one that is invalid
   all refuse with `usage_or_config` and a reason naming the cause; ensure
   `policy_source_unreadable` and `policy_not_found` exist and that `policy_source_unreadable` does
   not distinguish an absent branch from an unreachable remote from a refused credential. *Done
   when* Section 6.1 states one disposition for all four and Section 6.10's table carries both new
   reasons.

7. **Repo-scoped backoff and logging (`SPEC.md` Sections 14.1, 14.2)** — ensure all four are `Engine
   Invocation Failures`, recovered repo-scoped; ensure retry is backed off per repository with the
   schedule `Implementation-defined` and MUST documented; ensure each failure is logged with the
   reason naming its cause and that transitions rather than evaluations are logged. *Done when* an
   unusable policy no longer produces a log line every `polling.interval_ms` indefinitely.

8. **Last-known-good scoped to work in flight (`SPEC.md` Sections 6.2, 14.2)** — ensure a policy
   that was loaded and can no longer be read stays in force for runs already under way while new
   work is refused, and that a policy never loaded has no fallback. *Done when* the two histories
   are distinguished and the four causes are not.

## Cross-cutting sync

- **`VCSX-CONTRACT.md`** — the consumer configuration carries `policy_source`; `load_policy` joins
  the named operations; the trust-sourcing section names the mode.
- **`VCSX-SPEC.md` test matrix (Section 13.1)** — the policy is read once per unit of work and a
  change to the policy source mid-run does not take effect until the next; each of the four causes
  yields its own reason under one status; `policy_source_unreadable` covers an absent branch, an
  unreachable remote and a refused credential alike; under `target_branch` a `policy_branch` equal
  to the target is not an error.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** and **Conformance Statement
  (Section 13.3)** plus **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — `load_policy`, and the
  backoff schedule as an `Implementation-defined` row.
- **`SPEC.md` cheat sheet (Section 6.4)** — `vcs.policy_source`, and `vcs.policy_branch`'s REQUIRED
  status becoming mode-dependent.
- **`SPEC.md` test matrix (Section 17)** and **checklist (Section 18)** — the four causes' shared
  disposition, the backoff, and the last-known-good scope.
- **`conformance/vcsx/vocabulary.json`** — both configuration reasons and `load_policy`.
- **`conformance/vcsx/vectors/policy-validation.json`** — vectors for the two new reasons where a
  vector file can express the input; `policy_source_unreadable` needs a source that cannot be read,
  which it cannot model, so record that as a fixture case in the README rather than authoring a
  vector that lies.

## Anchor changes

- `VCSX-SPEC.md` gains `policy_source`, `load_policy`, `policy_source_unreadable` and
  `policy_not_found`.
- `SPEC.md` gains operator key **`vcs.policy_source`**; **`vcs.policy_branch`** changes from
  unconditionally REQUIRED to REQUIRED under `policy_source = "policy_branch"`.
- `SPEC.md` Section 6.2's phrase **"The software MUST detect changes to all three configuration
  artifacts"** is narrowed: `repo.policy.toml` is no longer watched, being read per unit of work.
- `VCSX-SPEC.md` Section 6.1's **"the engine discovers and reads"** framing is superseded by the
  consumer supplying the merged surface.

## Status

Accepted. Applied to `VCSX-SPEC.md`, `SPEC.md`, `VCSX-CONTRACT.md`,
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.

Steps 1-8 applied. `policy_source_unreadable` and `policy_not_found` have no behavior vectors: a
vector file supplies a policy document rather than the place one was read from, so both are recorded
in `conformance/vcsx/README.md` as fixture cases rather than authored as vectors that would model an
input the corpus cannot express.
