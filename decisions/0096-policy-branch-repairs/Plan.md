# Plan — 0096 The three repairs decision 0094 needed

## Scope

`VCSX-SPEC.md`: Sections 6.10 "Validation", 8.1 "Entry Points and Arguments", 8.6 "Invocation
Preconditions", 13.1 "Test Matrix".

`SPEC.md`: Sections 9.7 "Repository Provisioning and the VCS Engine", 9.10 "Forge Operations, Pull
Requests, and Review Writes", 14.1 "Failure Taxonomy", 17 "Test Matrix", 18 "Implementation
Checklist".

`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`,
`conformance/vcsx/vectors/policy-validation.json`.

## Tokens introduced

- `policy_branch_is_target` — configuration reason (Section 6.10).
- `policy_branch_missing` — precondition reason (Section 8.6).

## Steps

1. **The collision is refused at validation (`VCSX-SPEC.md` Section 6.10)** — ensure the
   configuration table carries a row for a `policy_branch` equal to the resolved base branch,
   carrying `policy_branch_is_target`, and that the surrounding prose states it is judged from the
   consumer's configuration and the policy with no checkout opened. *Done when* the row exists and
   the refusal is stated to precede any operation.

2. **`policy_branch` resolves to the remote's copy (`VCSX-SPEC.md` Section 8.1)** — ensure the
   `policy_branch` bullet states that it resolves to the copy belonging to the resolved `remote` and
   never to a local branch of the same name, citing Section 6.4's rule for the base ref as the same
   discipline. *Done when* a checkout carrying a local branch of that name cannot change what the
   engine reads.

3. **`policy_branch_missing` (`VCSX-SPEC.md` Section 8.6)** — ensure the precondition table carries
   it, ensure it is established before validation alongside `arguments_unreadable` and
   `local_vcs_missing`, and ensure the paragraph naming the arguments judged from the invocation
   alone includes it. *Done when* the count of preconditions established before validation reads
   three and the row exists.

4. **The policy branch is never a permitted target (`VCSX-SPEC.md` Section 8.1)** — ensure
   `base_branch_allowed` is stated to exclude the policy branch whatever it lists, so a supplied
   target naming it yields `base_branch_not_permitted` without an operator configuring anything.
   *Done when* the exclusion is stated as a property of the bound rather than as advice.

5. **`SPEC.md` carries the operator-visible half (Sections 9.7, 9.10)** — ensure `vcs.policy_branch`
   documents the remote-copy resolution and states that a configuration in which it equals the
   resolved target is refused before any operation runs; ensure Section 9.10's MUST NOT is
   cross-referenced to that refusal so the guarantee and its enforcement are readable together.
   *Done when* Section 9.10's guarantee names where it is enforced.

6. **The refused issue (`SPEC.md` Sections 9.7, 14.1)** — ensure Symphony logs every occurrence of
   an issue naming the policy branch as its target, and, where the tracker adapter supports the
   capability, comments once per (issue, target) and transitions the issue to a configured blocked
   state. Ensure the MUST sits on the log and the tracker writes are conditional, since
   `add_comment` and `set_state` are OPTIONAL adapter capabilities (Section 11.7). *Done when* no
   requirement depends on a capability an adapter may decline, and the comment is bounded per
   (issue, target) rather than per tick.

## Cross-cutting sync

- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a `policy_branch` equal to the resolved base is
  refused with `policy_branch_is_target` and runs no operation, in particular no `commit` and no
  `push`; an invocation supplying no `policy_branch` yields `policy_branch_missing` and yields it in
  preference to any configuration reason; a checkout holding a local branch named as the policy
  branch reads the remote's copy; a supplied `base_branch` naming the policy branch yields
  `base_branch_not_permitted` whatever `base_branch_allowed` lists.
- **`SPEC.md` test matrix (Section 17)** — an operator config whose policy branch equals the
  resolved target is refused at configuration time rather than at `create_pr`; an issue naming the
  policy branch as its target is refused, logged, and where supported commented once and
  transitioned.
- **`SPEC.md` checklist (Section 18)** — 18.1.4's policy-branch item names the refusal and the
  remote-copy rule.
- **`conformance/vcsx/vocabulary.json`** — both tokens, and the precondition note's count of reasons
  established before validation.
- **`conformance/vcsx/README.md`** — `policy_branch_missing` joins the conditions determined by the
  invocation that no vector models; `policy_branch_is_target` is vector-modellable and belongs with
  the configuration reasons.
- **`conformance/vcsx/vectors/policy-validation.json`** — a vector for the collision, which is
  determined by inputs a vector file can express.

## Anchor changes

- `VCSX-SPEC.md` gains configuration reason **`policy_branch_is_target`** and precondition reason
  **`policy_branch_missing`**.
- `base_branch_allowed`'s meaning narrows: it bounds which targets are permitted *in addition to*
  the policy branch always being excluded. Not a rename; recorded because a plan reading it as the
  sole bound is stale.

## Status

Accepted. Applied to `VCSX-SPEC.md`, `SPEC.md`, `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/README.md` and `conformance/vcsx/vectors/policy-validation.json`.

Step 1's refusal is stated unconditionally because the specification as it stands has one mode. The
tunable model makes `policy_branch == target` legitimate under an operator opt-out, and scoping this
row to the strict mode belongs to that decision.
