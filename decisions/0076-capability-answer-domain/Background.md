# Background — 0076 A capability that cannot determine its answer says so

## Context

Resolves issue #28, raised while implementing Section 9.2 against `a001ea2`.

Decision 0075 fixed `fetch_counterpart`: a capability that answered a bare value had two answers for
three conditions, so a fetch that failed was reported as "the remote carries none" and a `pull` that
pulled nothing reported `ok`. It considered and did not take a fourth option:

> **Option D — state an answer-domain invariant over Section 9.1 as a whole (not taken here).** …
> Not taken: an invariant quantified over the capability list sits at a different altitude than
> Section 9.1's prose, and the enumeration it would generalize is one decision old. **It is the
> repair to reach for if a second capability repeats this.**

Issue #28 is that second capability. `pr_state(work_branch)` answered `open`/`closed`/`merged` — three
answers for five states, since a work branch with no pull request is the ordinary condition before the
first `create_pr` and was unstated, and a forge that could not be asked has nothing left to answer
with. The consequences are worse than #26's, because two of the three readers act on the answer rather
than report it: `push` proceeds over a **merged** pull request, which is the exact act `push:pr_closed`
exists to refuse, and `create_or_update_pr` opens a **second** pull request for a work branch that
already has one, which is the one thing Section 9.2 says a forge backend maintains against. The third,
`status`, reports "no pull request" for a repository that has one — a read that lies where Section 4.1
already has the honest shape for the same situation on the base side (`base_absent`).

## What the audit found, which is why this is not "0075 again"

Taking Option D means applying the invariant, and applying it to the pinned revision finds more than a
second instance. The capabilities that answer a bare value, and what their absent answer already
means:

| Capability | Its absent answer already means | If the absent answer also carried "could not tell" |
|---|---|---|
| `is_dirty()` | a `commit` would capture nothing | **fails open** — see below |
| `is_conflicted()` | not conflicted | a conflicted tree reads as clean |
| `current_branch()` | the checkout has no current branch (Section 8.6) | refuses, with the wrong reason |
| `resolve_base_ref()` | the checkout holds no copy | `diff:base_unavailable` is right; `status`'s `base_absent` is a read that lies |
| `ahead_behind()`, `detect_mode()` | — | no non-answer exists at all, so widening them collides with nothing |
| `accepts_branch_name()` / `accepts_identity()` | illegal / malformed | refuses, with the wrong reason (least likely to arise) |
| `pr_state()` | *(unstated)* no pull request | the issue's own report |

`is_dirty()` is the one that matters, and it is worse than the report that prompted the decision.
Section 12.2 does not merely *report* on the predicate, it **branches** on it: `if worktree_dirty():
dispatch(run_op("commit", …))`. A false reading therefore produces no `commit:nothing_to_commit` — it
produces no commit result at all. `ship` proceeds to `push` and reports success with the work still
uncommitted in the worktree. A push over a merged pull request is at least visible at the forge; this
is a green run that did nothing it was asked to do, and nobody had reported it.

The filing implementation does not ship that bug, because its trait returns a `Result` and a failed
`git status` becomes a fault. That channel is the implementation's, not Section 9.1's, and it lands
outside the Section 8.2 envelope — which is the same objection issue #26 raised about its own
meanwhile. Every other engine must invent the same channel and choose its own mapping. **That is the
interoperability defect, and it was already present in five capabilities that nobody had reported.**
So this decision does not close a class prospectively; the class was already open, in a worse place
than the report that opened it.

## Section 11 is part of the defect, not tidying alongside it

Section 11 is the section that tells a consumer what it may rely on, and it said the capabilities
touching the network are "named and enumerable (Section 9.1)". Section 9.1's enumeration is scoped to
the VCS backend — "the version-control operations Section 3.2 places host-side" — while **all three
required Section 9.2 capabilities take a credential**. A consumer that mediates exactly Section 9.1's
three does not mediate the forge at all. That is an absence in the security model rather than a
citation slip, and this decision was editing both capability lists anyway.

## Options considered

- **Option A — widen `pr_state` alone and state the mapping, no token (contained in the choice).**
  0075's Option A one section over. Correct as far as it goes, and it leaves the rule that would have
  caught `is_dirty()` unwritten, so the third report of this shape is still available.
- **Option B — Option A plus a registered `push` reason for the refusal, class `error` (rejected).**
  It lets a policy escalate an unreachable forge without also catching a blocked gate. Rejected on
  0066's and 0075's shared ruling: the class is the same as `failed`'s, so the wider token fits, and
  Section 8.5 makes a reason permanent while admitting a new one in any `MINOR`. The reconsideration
  trigger 0075 named — a consumer that must act differently on the two — is unchanged and still
  applies.
- **Option C — Option A inside the answer-domain invariant, and the Section 9.1 audit it implies
  (chosen).** Section 9 states the rule over both capability lists; every value-answering capability's
  entry states what its "could not determine" maps to; Section 11 gains the forge half.
- **Option D — a per-capability `Result`-shaped return in the plugin API (rejected).** The shape the
  filing implementation already has. Rejected because it is a language-level mechanism in a document
  that names no language: the specification's business is which reason a caller reads, not how a
  backend signals upward. The invariant states the former and leaves the latter to the backend, as
  0075 did for `git ls-remote --exit-code`.

## Decision and reasoning

Section 9 states the invariant over both plugin sections: a capability either answers its operation's
typed result or answers a value; a value-answering capability MUST be able to answer that it could not
determine one; that answer MUST NOT be spelled as the value's absent or negative case; and every such
non-answer maps to a Section 4.3 reason where an operation has been dispatched or a Section 8.6
precondition reason where none has, with the capability's own entry stating which. **The first
dispatch is the boundary**, which is Section 8.6's existing rule reused rather than a second one.

The mappings, all but one to reasons that already exist:

- `pr_state` — `push:failed` and `create_pr:failed` (both fail closed; neither operation acts on a
  state nothing established), and a `pr_state_unavailable` output for `status`.
- `is_dirty` — `ship` dispatches `commit` rather than skipping it, and the operation reports
  `commit:failed`. The guard exists to skip a `commit` that would report `nothing_to_commit`, not to
  decide whether a commit is owed.
- `resolve_base_ref` — `diff:base_unavailable` covers both non-ref answers, because Section 4.3
  already defines it over "no copy in the checkout, **or** acquiring it failed"; only `status` needs
  the distinction, and it reports undetermined rather than `base_absent`.
- `is_conflicted`, `ahead_behind` — `status` outputs, reported undetermined.
- `detect_mode`, `current_branch` — consulted before the first dispatch, so the new precondition
  reason `checkout_unreadable`.
- `accepts_branch_name`, `accepts_identity` — no third answer: a predicate that cannot judge answers
  no, and the engine refuses through `work_branch_invalid` / `identity_invalid`. Stated so it is a
  choice rather than an accident, on the ground that a predicate failing closed refuses a legal name
  at worst while one failing open carries an unjudged identity into every operation that writes.

**One token, and why it is a precondition reason rather than an operation reason.** `checkout_unreadable`
is the only addition. A backend that cannot read the checkout is judged from the invocation's arguments
and the checkout, before any operation is dispatched, which is Section 8.6's own dividing line against
Section 6.10. Reporting it as `no_current_branch` would name a state the backend never established;
Section 8.6 already forbids the mirror image of that ("An engine MUST NOT report a precondition reason
for a condition an operation has a reason that names"). It goes in `precondition_reasons`, shares the
`usage_or_config` status, and a consumer branching on that status absorbs it with no class edge — which
is Section 8.5's whole reason for keeping precondition reasons out of the `#class` ladder.

**The output name.** `pr_state_unavailable`, not `pr_state_unknown` and not a second `_absent`.
Section 4.3 already draws the distinction the output needs — "**Unresolved is not knowing which
branch** … **Unavailable is not having its commit**" — and here the engine knows exactly which branch
and cannot get the answer, so it is the unavailable half. `base_absent` is the model for the *form* and
not for the word: absence is a fact about the checkout, and this is a failure to establish one.
`unknown` was rejected because it invites the question "to whom".

**What the fix costs.** The invariant is quantified over a list, which is the altitude objection 0075
raised and this decision overrides rather than answers: it is still a rule that reads at a different
level than the bullets around it, and a capability added later must be read against it rather than
against its neighbours. Accepted because the alternative is a per-capability repair whose failure mode
is silent by construction — the audit found five instances and one report. `push:failed` also still
covers "the forge could not be consulted" alongside every other push failure, the same cost 0075
accepted for `pull:failed` and on the same terms.

Relates to 0075 (whose Option D this takes, on the trigger it named), 0073 (whose capability split
created the value-answering half), 0066 (whose "one owner, one repair" test `checkout_unreadable`
satisfies and whose "wider token where it fits" ruling keeps Option B rejected), 0065 (whose
configuration/precondition dividing line places the new token), 0057 (whose universal `failed` most of
the mappings land on), and 0051 (whose derived registry gains the token). Sibling of 0077, which lands
after it and extends `pr_state`'s value with the head a conditional merge is pinned to.
