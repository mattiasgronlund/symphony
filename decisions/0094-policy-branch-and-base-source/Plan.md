# Plan — 0094 The policy branch is not the base branch

## Scope

`SPEC.md`: Sections 5 "Configuration Model" (dividing rules), 5.3 "Operator Policy Config", 5.6
"`repo.policy.toml` (Repository Way of Working)", 6.4 "Configuration Cheat Sheet", 9.7 "Repository
Provisioning and the VCS Engine", 9.8 "Git Automation and Work Branch", 9.10 "Forge Operations,
Pull Requests, and Review Writes", 15.4 "Configuration Trust Sourcing and Hook Safety", 17 "Test
Matrix", 18 "Implementation Checklist".

`VCSX-SPEC.md`: Sections 3.2 "Execution Contexts (Trust)", 6.4 "`[base]` and Base Resolution", 8.1
"Entry Points and Arguments", 8.6 "Invocation Preconditions", 11 "Security and Trust Model", 13.1
"Test Matrix", 13.2 "Implementation Checklist", 13.3 "Conformance Statement".

`VCSX-CONTRACT.md`: Sections 4 "`repo.policy.toml` (Config Surface)", 10 "Trust Sourcing".

`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`,
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## Tokens introduced

- `vcs.policy_branch` — `SPEC.md` operator key. REQUIRED, no default.
- `vcs.base_branch` — `SPEC.md` operator key, the default pull-request target. OPTIONAL.
- `vcs.base_branch_allowed` — `SPEC.md` operator key bounding what an invocation may name. OPTIONAL.
- `policy_branch`, `base_branch`, `base_branch_allowed` — the matching `VCSX-SPEC.md` Section 8.1
  argument names.
- `base_branch_missing`, `base_branch_not_permitted` — Section 8.6 precondition reasons.

## Steps

1. **The trust root is the policy branch, not the base (`SPEC.md` Section 15.4)** — ensure the
   host-side bullet reads its Way of Working from the operator-named policy branch rather than from
   "the resolved base revision", and ensure the two legs of the argument are stated separately: the
   agent cannot push there because the scope guard permits no branch but the work branch (Section
   10.8), and no pull request Symphony creates or merges targets it. *Done when* the phrase
   "Way-of-Working trust equals base-branch trust" no longer appears and the replacement names the
   policy branch.

2. **The non-merge-target guarantee is stated over Symphony's behavior (`SPEC.md` Sections 9.10,
   15.4)** — ensure the specification states that Symphony MUST NOT create or merge a pull request
   targeting the policy branch, phrased as a property of the operations a consumer can observe
   rather than as a constraint on a configuration file. *Done when* the guarantee is checkable from
   the forge operations alone, without reading operator config.

3. **The policy branch is operator config (`SPEC.md` Sections 5, 5.3, 6.4, 9.7)** — ensure
   `vcs.policy_branch` exists as a REQUIRED operator key with no default, described as the revision
   host-side Way of Working is read from; ensure Section 5's dividing rules place it with the
   operator on the stated ground that a value selecting the trusted revision cannot be read from the
   revision it selects. *Done when* the key appears in the top-level list, the cheat sheet, and
   Section 9.7's configuration bullet.

4. **The policy branch MUST be unwritable by the agent (`SPEC.md` Section 15.4)** — ensure the
   specification requires it and states that how an implementation establishes it is
   `Implementation-defined` and MUST be documented, noting that the scope guard already covers the
   agent's push path so the obligation covers the remaining routes. *Done when* the requirement and
   the documentation obligation both appear.

5. **`[base] branch` becomes the lowest-precedence source (`VCSX-SPEC.md` Section 6.4)** — ensure
   `branch` is marked OPTIONAL, described as the policy's contribution to a value the invocation and
   the consumer configuration may also supply, with precedence stated as invocation, then consumer
   configuration, then policy. Ensure `resolve`/`prefixes` keep their meaning as a refinement of
   whichever value applies. *Done when* Section 6.4 states the precedence and no longer reads as the
   sole source.

6. **The target and its bound are invocation arguments (`VCSX-SPEC.md` Section 8.1)** — ensure
   `base_branch` is an OPTIONAL argument, `policy_branch` is named as the consumer-supplied trusted
   revision, and `base_branch_allowed` bounds what an invocation may name. Ensure all three are
   listed among the values the consumer configuration MAY carry. *Done when* the three appear with
   the existing access-parameter and coordinate arguments.

7. **Two precondition reasons, entry-scoped (`VCSX-SPEC.md` Section 8.6)** — ensure
   `base_branch_missing` is established for an entry that needs a target — `ship`, `integrate`,
   `create_pr` — and not for `commit`, `push`, `pull`, `merge`, `land` or `provision`; ensure
   `base_branch_not_permitted` is established where an invocation names a target outside
   `base_branch_allowed`. Ensure an entry outside the set that reaches a target-needing operation
   through a `run_op` edge reports that operation's own reason, which is the disposition the section
   already gives `git_access`. *Done when* both rows exist and the entry sets are enumerated.

8. **The engine's trust prose stops naming the base (`VCSX-SPEC.md` Sections 3.2, 11;
   `VCSX-CONTRACT.md` Sections 4, 10)** — ensure "for example a protected base branch" becomes a
   revision the consumer names, and ensure `VCSX-CONTRACT.md` Section 10's "read from the resolved
   base revision, which the agent cannot push to and which is review-gated" is replaced by the
   policy-branch framing. Ensure Section 4 lists the policy branch among the consumer
   configuration's contents. *Done when* neither engine document derives the trusted revision from
   `[base]`.

9. **Symphony's own base reads follow the precedence (`SPEC.md` Sections 9.8, 9.10)** — ensure the
   back-merge source and the pull-request target are described as the resolved target rather than as
   "the base branch (`repo.policy.toml`)", and ensure the per-issue source and its bound are named
   with the carrier left `Implementation-defined` and MUST-documented. *Done when* no passage
   attributes the target solely to `repo.policy.toml`.

## Cross-cutting sync

- **`SPEC.md` cheat sheet (Section 6.4)** — add `vcs.policy_branch`, `vcs.base_branch`,
  `vcs.base_branch_allowed`; the `repo.policy.toml` list keeps the base branch as the
  lowest-precedence source rather than the only one.
- **`SPEC.md` test matrix (Section 17)** — host-side policy is read from `vcs.policy_branch` and not
  from the pull-request target; no pull request Symphony creates or merges targets the policy
  branch; an agent commit on the work branch does not change host-side behavior even after its pull
  request merges, because the merge does not reach the policy branch; the three target sources
  resolve in precedence order; an invocation naming a target outside the operator's bound is
  refused.
- **`SPEC.md` checklist (Section 18)** — 18.1.1's configuration-artifact item names the policy
  branch; 18.1.4 names the three target sources and the bound.
- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a `commit` and a `push` run with no target
  available while a `ship` is refused with `base_branch_missing`; an invocation-supplied target
  beats the consumer configuration's, which beats `[base] branch`; a target outside
  `base_branch_allowed` yields `base_branch_not_permitted`; a `status` reports against the resolved
  target whichever source supplied it.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — the three-source resolution, the
  bound, and the two precondition reasons.
- **`VCSX-SPEC.md` Conformance Statement (Section 13.3)** and
  **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — a row for the per-issue target carrier, which is
  `Implementation-defined`.
- **`conformance/vcsx/vocabulary.json`** — add both precondition reasons with their meanings.
- **`conformance/vcsx/vectors/policy-validation.json`** — the corpus supplies `base.branch` in all
  32 vectors; with the key OPTIONAL those vectors stay valid, but add a vector for a policy omitting
  it, which is now well formed rather than an unstated case.
- **`conformance/vcsx/README.md`** — the entry-scoped precondition reasons join the list of
  conditions determined by the invocation, which no vector file models.

## Anchor changes

- `SPEC.md` gains operator keys **`vcs.policy_branch`**, **`vcs.base_branch`** and
  **`vcs.base_branch_allowed`**.
- `SPEC.md` Section 15.4's phrase **"Way-of-Working trust equals base-branch trust"** is removed,
  superseded by the policy-branch statement; `VCSX-CONTRACT.md` Section 10's **"WoW-config trust
  therefore equals base-branch trust"** likewise.
- `VCSX-SPEC.md` Section 6.4's **`[base] branch`** changes from required-by-omission to OPTIONAL and
  lowest-precedence. Not a rename; recorded because plans addressing it as the sole source are
  stale.
- `VCSX-SPEC.md` gains arguments **`policy_branch`**, **`base_branch`**, **`base_branch_allowed`**
  and precondition reasons **`base_branch_missing`**, **`base_branch_not_permitted`**.
- The decision folder was renamed from `0094-policy-determines-no-base` to
  `0094-policy-branch-and-base-source` when the subject changed under review.

## Status

Accepted. Applied to `SPEC.md`, `VCSX-SPEC.md`, `VCSX-CONTRACT.md`,
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

Superseded framings, kept because the path is the argument: this decision was opened as "what
happens when the policy determines no base" and once carried an A/B/C option set over that question.
Both earlier framings are recorded in `Background.md`; the missing-value question survives as step
7.
