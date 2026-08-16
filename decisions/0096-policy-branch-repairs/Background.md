# Background — 0096 The three repairs decision 0094 needed

## Context

Decision 0094 split the policy branch from the base branch and was applied. Reviewing the applied
text turned up four defects; 0095 took the most serious. This decision takes the other three, plus
the small addition that closes the runtime half of one of them.

All three are defects in text already committed, not new design. They are grouped because they are
the same omission at three levels — 0094 stated a guarantee and left the ways of establishing it
unstated.

### Defect 1 — the guarantee has no refusal behind it

0094 states, at `SPEC.md` Section 9.10, that Symphony MUST NOT create or merge a pull request whose
base is the policy branch. Stating it over the operation was deliberate: a consumer can check it
through the forge operations rather than by reading a configuration file.

But nothing refuses the configuration that violates it. An operator who sets
`vcs.policy_branch = "main"` and leaves the target resolving to `main` — the most obvious first
configuration anyone writes — gets `commit` ok, `push` ok, and `create_pr` refused. The work branch
is on the remote and the pull request never opens.

That is the publish-then-die shape decision 0084 moved a check to validation to prevent, and which
0094's own reasoning cites 0084 by name to justify avoiding for a missing base. It is the third
appearance of the shape on this branch and the second introduced by a repair for a previous one.

The conflict is visible in the consumer's own configuration, with no checkout and no network. That
is what a configuration error is judged from (Section 6.10), so it belongs there.

### Defect 2 — nothing says which copy of the policy branch is read

`VCSX-SPEC.md` Section 6.4 is careful about this for the base ref, and says why:

> A checkout MAY hold several copies of one base branch — its own local branch, and a
> remote-tracking copy for each remote it carries — which are the same commit only until one of them
> is updated.

Resolution therefore selects the copy belonging to the resolved remote. For the base that buys
correctness. **For the policy branch the same ambiguity is a trust bypass.** In a checkout the
engine did not create — `engine-direct`, or any pre-existing working copy — a local branch named
`policy` is writable by whoever controls that checkout, and if the engine reads it, that person
chooses which host-side hooks run with the operator's credentials.

The exposure is not uniform: it is latent in `daemon`, where the store is the service's own; real in
`interactive-agent`, where the human driving it can write a local branch; and immediate in
`engine-direct`, where the checkout is outside the operator's control entirely.

### Defect 3 — REQUIRED with no failure mode

0094 made `policy_branch` REQUIRED and gave it no precondition reason. Its five siblings all have
one: `local_vcs_missing`, `git_access_missing`, `forge_access_missing`, `store_location_missing`,
`base_branch_missing`.

This is the fourth recurrence of a pattern first named in 0092's review finding — "REQUIRED has no
stated failure mode, being an unenforced adjective" — and the second time it was committed after
being named. Recording the count because the recurrences are the useful finding: the pattern is not
that a token was forgotten, but that adding a REQUIRED argument and adding its refusal are two
separate edits, and nothing in the process couples them.

### The runtime half of defect 1

Defect 1's refusal covers a target that configuration determines. It cannot cover a target an issue
supplies, because that is not known until the issue is read. 0094 already added the machinery for
that case — `vcs.base_branch_allowed` and the precondition `base_branch_not_permitted` — so the
question is only whether the policy branch is excluded from permitted targets automatically, or only
when an operator remembers to configure the bound.

## Options considered

**For defect 1 — where the refusal lands.** A precondition (Section 8.6) was the alternative to a
configuration error. It loses on 0092's own test: the conflict is repaired by editing the operator's
configuration, not by changing the invocation, and it is judged with no checkout opened. Both halves
put it on the configuration side.

**For defect 2 — what "which copy" resolves to.** Three were available: the copy belonging to the
resolved remote (chosen, reusing Section 6.4's rule verbatim); a rule that the engine fetches the
policy branch immediately before reading it, which is stronger but settles an acquisition question
this decision does not own; and leaving it `Implementation-defined`, rejected because the whole
point of a trust root is that two conforming implementations agree on what it is.

**For the runtime half — implicit versus configured exclusion.** Requiring an operator to list the
policy branch in a bound they must remember to configure makes the guarantee depend on an act of
diligence, and an operator who forgets gets the defect back. Excluding it implicitly cannot be
forgotten, needs no new mechanism, and leaves `base_branch_allowed` doing what it was introduced for
— bounding *which* targets are permitted, not re-stating a rule the specification already makes.

**For the refused issue — what Symphony does with it.** The log is the only guaranteed record,
because `add_comment` and `set_state` are both optional adapter capabilities (Section 11.7) and a
`none`-mode local adapter may have neither. A specification requiring the note to reach the ticket
would promise what a conforming deployment cannot deliver. So the MUST sits on the log and the
tracker writes are conditional on support — and the comment is bounded to once per (issue, target),
because the daemon re-evaluates every candidate every `polling.interval_ms`, default 30 seconds, and
an unbounded side effect there is 120 comments an hour on one ticket indefinitely.

## Decision and reasoning

All three defects repaired, plus the implicit exclusion.

**`policy_branch_is_target`** joins Section 6.10's configuration table: the policy branch is also
the branch the resolved target names. Judged from the consumer's configuration and the policy
together, with no checkout — which is what Section 6.10 is judged from. The refusal lands before
`commit`, so nothing is published by an invocation that cannot open a pull request.

**The policy branch resolves to the copy belonging to the resolved remote**, never to a local branch
of that name, stated in `VCSX-SPEC.md` Section 8.1 where the argument is defined and
cross-referenced from Section 6.4, whose rule it reuses. That collapses the `engine-direct` exposure
to the same level as `daemon`: whatever the local checkout carries, the trust root is what the
remote holds.

**`policy_branch_missing`** joins Section 8.6, established before validation for the same reason
`local_vcs_missing` is — the policy cannot be located without it, so nothing downstream can be
judged.

**The policy branch is never a permitted target**, whatever `base_branch_allowed` says. An issue
naming it is refused with `base_branch_not_permitted`, which already exists. Symphony logs every
occurrence, and where the tracker adapter supports it, comments once per (issue, target) and
transitions the issue to a configured blocked state.

**What this decision deliberately does not do.** It states the refusal in defect 1 unconditionally,
because as the specification stands today there is only one mode: the policy branch is always
separate. The tunable model — an operator opting out so the policy comes from the target branch —
makes `policy_branch == target` legitimate rather than an error, and scoping this refusal to the
strict mode is that decision's work, not this one's. Repairing applied text and introducing new
design in one record would bury the first in the second.

**Reconsideration triggers.** Reopen the implicit exclusion if a deployment appears that genuinely
wants work landing on its trust root — which would mean it has no trust root, and the repair is to
say so rather than to permit the collision. Reopen the remote-copy rule if an engine appears whose
consumer supplies the policy directly rather than naming a revision to read it from; there would
then be no copy to choose between.

Relates to 0094 (whose applied text these repair), 0084 (whose refuse-before-publishing argument
places defect 1's refusal), 0092 (whose config/precondition test places it on the configuration
side, and whose review finding named the pattern defect 3 repeats), and 0002.
