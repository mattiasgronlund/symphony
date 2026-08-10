# Background — 0074 The commit-identity precondition is scoped to the entry point

## Context

Resolves issue #23, raised while implementing `VCSX-SPEC.md` Section 8.6 against `47d9d74d` and
recorded as decision 0021 in that implementation's own decision log.

Section 8.6 requires the caller-supplied commit identity "for an entry that can write a commit —
`commit`, `integrate`, `pull`, and a front-end sequence that dispatches one". Section 5.2 makes a
policy a graph: `run_op`'s result is itself a trigger, so an invocation dispatches whatever the graph
routes it to. The clause admits two readings — the sequence's *own* dispatches (Sections 12.2, 12.3),
or anything the invocation *can* dispatch — and the document does not say which, so a run exists that
the engine starts, cannot finish, and has no token to refuse with:

```toml
[[policy.edge]]
on = "status:ok"
do = "run_op"
op = "commit"
```

Invoked at the `status` entry point, which Section 8.6 does not list, with no identity supplied.

The issue's sharper point is the missing channel rather than the missing rule. Section 4.3 gives
`commit` no reason naming an absent identity, and Section 8.6's own closing rule — an engine MUST NOT
report a precondition reason for a condition an operation *could have* reported — does not bite,
because `commit` could not have reported it. The engine is left with a fault at exactly the point
Section 8.6 exists to refuse before.

Three things sharpen the report.

**The gap is the document's own example policy, not a contrived one.** Section 6.5 prints
`push:non_fast_forward → run_op integrate` as its illustration of the edge schema, and Section 12.2
builds the same routing in. `integrate` writes a merge commit and takes the identity (Sections 9.1,
10.1, decision 0068), and `push` is not in Section 8.6's list. So the most ordinary policy in the
document, invoked at an entry point Section 8.1 offers "for a driver that composes its own sequence",
reaches an identity-taking operation with no identity required. A `land` whose policy routes
`merge:ok` to `pull` is worse: the pull request has already merged when the dispatch fails.

**A channel does exist, and it is the wrong one.** `failed` is universal (decision 0057), so
`commit:failed` is expressible. It reports `error`, exit `20` — an invitation to retry a run no retry
changes — and it tells the caller the commit failed rather than that an argument was omitted. The
operation cannot answer *truthfully*, which is a narrower claim than the issue's and the one the
answer has to serve.

**The closing rule is itself ambiguous, and the ambiguity is load-bearing.** Read counterfactually —
"could have" meaning the registry holds a reason for it — the issue's conclusion follows. But applied
consistently that reading also empties Section 8.6's own table, because `failed` is universal and so
*every* precondition is one some operation "could have" reported, including `identity_invalid` at the
`commit` entry. Read ordinally — the sentence's own gloss, "once an operation is dispatched" — the
registry survives. The rule has to be repaired whichever way the scope question is answered.

**Absent and malformed diverge.** Section 8.6 has the backend judge a supplied identity's shape with
`accepts_identity`, but only for the entries the requirement covers. A malformed identity supplied to
a `status` run is therefore never judged at all.

## Options considered

- **Option A — scope the precondition to the entry *and* the policy** (the issue's reading 2, and
  what the reporting implementation built). Identity is required when the entry can write a commit or
  when any `run_op` edge names `commit`, `integrate` or `pull`. Trade-offs: it closes the fault by
  construction, needs no new token, keeps the refusal at exit `2` before any effect, and is decidable
  from artifacts already in hand. Rejected on its cost, which is larger than it first appears: because
  the canonical `push:non_fast_forward → integrate` edge is in essentially every real policy, A
  collapses in practice to "every invocation of every entry requires a commit identity", `status` and
  `diff` included. It also moves what a precondition is judged from — decision 0065's reusable line is
  that a configuration error is a property of `repo.policy.toml` alone and a precondition needs the
  invocation's arguments and the checkout; A adds the policy file to the second list, and the line
  loses its power to sort the next such case. Section 8.6's requirement is also not established from
  the run: an edge that mentions `commit` is a path the policy *might* take, not a dispatch the
  invocation determines.
- **Option B — keep the entry scope, say so, and give the operation a reason that names the
  condition** (chosen). `commit`, `integrate` and `pull` gain `identity_missing`, class
  `needs_caller`; a dispatch with no identity reports it, and the machine routes it like any other
  outcome. Trade-offs: the refusal is late and prior effects stand; two registries can name one human
  error, needing a stated boundary; and it adds a reason token and a `need` token to the major-stable
  surface, which Section 8.5 permits in a `MINOR`.
- **Option C — state the invariant and leave the analysis to the engine.** An engine MUST NOT
  dispatch an identity-taking operation without an accepted identity, with A's static test as the
  RECOMMENDED floor and a sound reachability analysis from the entry's own triggers permitted as a
  narrowing. Rejected: the argument set becomes engine-dependent, so the same policy and entry that
  one conforming engine refuses another runs, and the direction makes it worse — the permissive engine
  accepts more, so a consumer developed against it breaks when moved to the floor. That is the
  divergence the invocation contract exists to remove (Section 8.5). Reachability over the machine is
  also not a small analysis to specify neutrally: the class ladder, unscoped edges, built-in defaults
  and a hook's block surfacing as `<op>:blocked` all widen the reachable set.
- **Option D — require the commit identity on every invocation unconditionally.** Simpler than A and
  with the same practical effect, since A collapses to it. Rejected: it charges a read-only `status`
  or `diff` — operations Section 3.2 keeps local and credential-free — an attribution argument they
  never use, and it deletes a distinction the document otherwise maintains.
- **Option E — a precondition reason for the policy-graph case** (a fourth Section 8.6 token, or
  reusing `identity_invalid` at the dispatch). Rejected: Section 8.6's registry is for conditions
  judged before the policy runs, and this one is judged at a dispatch. Reusing the spelling across a
  class-free registry and a classed one would also make `reason` ambiguous about whether a class
  applies.
- **Option F — leave it `Implementation-defined`.** Rejected on decision 0065's reasoning: the exit
  code is the contract's coarsest branch point, and two engines answering `2` and `10` for the same
  policy is the divergence a driver cannot absorb.

## Decision and reasoning

The clause means the sequence's own dispatches. Section 8.6 now says so — `ship` requires an identity
and `land` does not, and a policy's `run_op` edges do not widen the set — and Section 4.3 gains
`identity_missing` (`needs_caller`) for `commit`, `integrate` and `pull`, which the dispatch reports
where no identity was required.

The reasoning worth keeping is that **the document had already answered this shape once**. Section 9.3
disposes of an unsupported capability in two tiers: `capability_unsupported` at validation where
determinable, and "where it is not determinable before the policy runs, it surfaces at first use as
the operation's `unsupported` reason". Identity is the same shape. At entry the engine knows a
commit-writing dispatch *may* occur, not that it will; the entries that certainly write are a
precondition, and the residual belongs to the operation. Answering this issue from that precedent
rather than from a fresh judgement is what keeps the two dispositions consistent, and it is the test
to apply to the next condition that straddles the boundary: ask whether the invocation determines it
or only the run does.

`needs_caller` is the honest class. Section 4.2 defines it as an operation that cannot proceed
without a decision or action from the caller, and a missing caller argument is that literally. It also
gives the condition a resolver seam (Section 5.5): the interactive front-end returns to the human, who
re-invokes with an identity, and a driver binds it to its own configuration. The built-in default for
an unmatched `needs_caller` already escalates (Section 5.4), so a policy that binds nothing still
behaves, and a repository that wants to bind `commit:identity_missing` can. `error` was the
conservative alternative and was not taken: exit `20` invites a retry that cannot succeed.

Two boundaries are stated because they are how this could rot.

**The first dispatch is the boundary, and `failed` does not count as a reason that names a
condition.** Section 8.6's closing rule is rewritten from "a condition an operation could have
reported" to "a condition an operation has a reason that names", with the dispatch as the line and an
explicit note that reading the universal `failed` as such a reason would make every precondition
reportable as `<op>:failed` and leave the registry nothing to name. Without that, the rule argues
against the registry it closes.

**A supplied identity is judged whatever the entry.** `accepts_identity` is a question with no side
effect, so asking it on every invocation that carries an identity costs nothing and leaves only
*absence* reachable at a dispatch — which is what makes `identity_missing` a truthful name rather
than a euphemism for two conditions. It also closes the divergence the issue did not raise: a
malformed identity handed to a `status` run is now refused before the policy runs, as it would be at
any other entry.

The cost is stated rather than glossed: a `land` whose policy routes `merge:ok` to `pull`, invoked
with no identity, merges the pull request and then stops at `pull:identity_missing`, and re-invoking
`land` answers `merge:not_open`. The escalation names what to supply and the operations already run
stand, which is the disposition Section 5.6 already gives a flow stopped at its bound; the recovery is
to supply the identity and invoke `pull`. Option A avoids that case and pays for it on every
invocation of every entry, which is the trade this decision declines.

Twelve conformance vectors pin the answer, because the scope is a pure function of the entry point
even though the judgement is not: `requires_commit_identity` is `true` for `commit`, `integrate`,
`pull` and `ship` and `false` for the rest, and two vectors assert that an edge dispatching `commit`
or `integrate` does not change it. Issue #13 established that "no vector pins whether X" is itself a
defect worth a decision; this is that rule applied before the ambiguity can return.

What would make us reconsider: a driver that cannot tolerate discovering a missing argument mid-flow
after a forge merge has landed would argue for Option A, and a consumer with no identity to give that
legitimately runs write-capable policies read-only argues the other way. If both appear, Option C is
the repair, and Section 8.6's clause is phrased as a scope over entry points rather than as an
analysis so that narrowing it later adds no token and changes no status.

Relates to 0065 (which created the precondition registry and the closing rule this repairs), 0068
(which made `integrate` and `pull` carry the identity, and so made them reachable cases here), 0057
(whose universal `failed` is what makes the closing rule ambiguous), 0073 (which introduced
`accepts_identity` as a published capability, without which the "judged whatever the entry" rule would
have nowhere to live), and 0053 (whose vector corpus this extends).
