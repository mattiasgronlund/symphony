# Background — 0080 A cycle of lifecycle positions is refused at validation

## Context

Resolves issue #33, which was filed against decision 0078's follow-through rather than against the
specification as it stood: the configuration below only becomes reachable once the position moves
into the dispatch, so it is a gap the repair created.

```toml
[[policy.edge]]
on = "before:commit"
do = "run_op"
op = "commit"
```

Every clause is legal. `before:commit` is a known trigger, `run_op` a known action, `commit` a known
operation, and the edge carries the argument its action needs, so none of Section 6.10's eleven
reasons names it and the policy validates. Then it runs: dispatching `commit` runs `before:commit`
(Section 4.1, decision 0078), the position matches exactly one edge with no class fallback
(Section 5.3), that edge dispatches `commit` (Section 5.2), and the engine is back where it started.

The reporting engine measured **sixty-four dispatches and zero operations**, ending at `needs_caller`
with the `flow_exhausted` need. Section 8.2 nulls `op`, `reason` and `class` for a flow the executor
stopped, so the envelope names neither the position nor the edge; the only field that could is
`detail`, which is `Implementation-defined` and therefore not portable diagnosis. Section 5.6 glosses
the need as saying "either that the graph does not converge or that the remote is moving faster than
the engine can follow". Neither happened — no remote was consulted and nothing was retried, because
no operation ever ran.

**It is the migration hazard from the reading 0078 replaced.** Under that reading the sequence owned
the position and a `run_op` did not re-enter it, so this edge meant "commit now" and worked. Any
`repo.policy.toml` written against such an engine may carry it, which makes the population most
likely to meet the defect exactly the population upgrading.

## Why the bound is the wrong instrument, on Section 5.6's own terms

Decision 0078 refused static detection in passing, on Section 5.6's own "the bound is a count, not a
cycle detector". That paragraph is right and this decision does not weaken it: `push:non_fast_forward
→ integrate → push` is the built-in routing, an executor that refused a graph containing a cycle
would refuse it, and one that stopped at a repeated edge would abort a flow that was about to
converge. What the decline missed is that the paragraph also names a **measure**:

> What separates a converging flow from a looping one is how many operations it takes, not whether it
> revisits an edge.

On this configuration that number is zero and stays zero however long the flow runs. The measure
Section 5.6 chooses is not merely unsatisfied here — it is undefined, and a count of dispatches is
being read as a count of operations that never begin.

The line between the two kinds of loop is mechanical and visible in the trigger the cycle passes
through. Every cycle Section 5.6 defends turns on a **typed operation result**:
`push:non_fast_forward`, `merge:head_moved`, `commit:worktree_moved`. A typed result is a report
about state outside the engine — the remote may stop moving, the head may settle, the working tree
may go quiet — so the next traversal may differ and counting is the only honest way to decide when
to give up. A **lifecycle position** reports nothing: it is matched exactly, has no class fallback
(Section 5.3), binds at most one edge (Section 5.4), and that edge is taken every time the position
runs. A cycle whose every edge is bound to a position therefore turns on nothing at all. It cannot
converge, on any checkout, against any remote.

So refusing it is not the cycle detection Section 5.6 rules out. The check is over a subgraph in
which no cycle can be conditional, and every routing that paragraph defends survives it untouched.

## The defect is a family, not a line

The report describes an edge naming its own position, and that is the spelling people will write.
The same property has longer forms in which no edge names its own position:

```toml
[[policy.edge]]  on = "before:commit"  do = "run_op"  op = "push"
[[policy.edge]]  on = "before:push"    do = "run_op"  op = "commit"
```

Dispatch either operation and the engine walks `before:commit → before:push → before:commit` until
the bound stops it, again with zero operations. Any rule shaped around "an edge whose `op` equals the
operation its own position gates" catches the first spelling and misses this one, so the condition is
stated over the positions and the edges bound to them.

## The runtime shape, and the measurement that ruled it out

The report's "meanwhile" — and the reporting engine's shipped guard — refused a dispatch entered
while the operation's **own** position was already running, reporting the universal `<op>:failed`
with a detail naming the position, on the second dispatch rather than the sixty-fourth. It is the
obvious answer and it is wrong, for a reason that was measured rather than argued. Put to that engine:

```toml
[[policy.edge]]  on = "before:push"    do = "run_op"  op = "integrate"
[[policy.edge]]  on = "integrate:ok"   do = "run_op"  op = "push"
```

`before:push` integrates; `integrate:ok` pushes the result, which enters `before:push` a second time
**while the first is still open**; the inner `integrate` reports `up_to_date`, no edge matches a
`done` result, the inner position completes, and both pushes run. Measured with the guard off:
operations `[integrate, integrate, push, push]`, ending `ok` at `create_pr:created`. With the guard
on: operations `[integrate]`, ending `error` at `push:failed`.

The guard refuses a flow that terminates and does the right thing, and the shape it refuses is not a
corner — a position dispatching an operation whose result routes back through it is the one shape
where a position legitimately nests. The predicate "this operation's own position is on the stack" is
not the claim "this flow cannot terminate", and the engine's own boundary test had exercised a cycle
through a typed result, which passes either way, so it gave confidence it had not earned.

A second argument, from Section 8.6, is independent of that measurement. A configuration defect
routed through the operation-result channel re-enters the machine as a result: a repository binding
`#error` to `escalate` turns a typo into an escalation to a person. Section 8.6 rules the move out one
registry over — the universal `failed` "names no condition — reading it as one would make every
precondition reportable as `<op>:failed` and leave this registry nothing to name" — and Section 6.10's
own boundary test settles which registry this belongs to: "a configuration error is a property of
`repo.policy.toml` alone, detectable before any argument or checkout is in hand". This condition is
exactly that.

## Options considered

- **A — validation refuses it (chosen).** A twelfth Section 6.10 reason, `position_cycle`, judged from
  the policy document alone, stated over the `before:<op>` positions the engine defines and the
  `run_op` edges bound to them.
- **B — the dispatch refuses it.** A sentence in Section 4.1 fixing what a dispatch does when a
  position would re-enter itself, reported as the universal `failed`. Rejected on the measurement
  above — it refuses terminating flows — and on the Section 8.6 argument. It buys coverage of
  re-entrance reached through a typed result, but that is a flow which *runs operations*, which is
  where the bound is the right instrument by Section 5.6's own measure.
- **C — absorb the edge.** Read a `run_op` at `before:<op>` naming `<op>` itself as satisfied by the
  dispatch already in flight: no second dispatch, the pending operation proceeds. It is the only
  option under which the upgrading repository keeps working, and its net effect matches what the
  pre-0078 reading produced by a different route. Rejected: it makes `run_op` name two things, which
  is the ground 0078 rejected its own option B on; it silently assigns a meaning to a configuration
  whose author is never told it was defective; and it is defined only for the one-edge form, so the
  family above still spends the whole bound running nothing, in a spelling that is harder to find
  because the obvious one now works.
- **D — keep the bound and sharpen the report.** Require the envelope to name the last position and
  edge. Rejected as an answer: `detail` is `Implementation-defined`, so it is not portable, and the
  report would still be a convergence failure for a policy that never had a chance to converge.
  Worth doing on its own merits for every exhausted flow, which is a separate change.
- **E — skip the position on re-entry.** Rejected by the reporter before filing, and rightly: it
  produces a `commit` that ran no `before:commit`, which is the in-sandbox bypass 0078 exists to
  close, Section 10.1 states the commit-message validation unconditionally, and Section 6.6 states the
  principle — "a gate is only a gate if what it inspected is what proceeds". Trading a confusing
  exhaustion for a silent hole is the wrong direction.

## Decision and reasoning

**A.** Section 6.10 gains `position_cycle`; Section 5.6 gains the boundary in place of the sentence
0078 added, and its own measure becomes the reason for the boundary rather than a defence of the
bound alone. The split the specification now states is clean:

- a flow that **cannot** converge because it reaches no operation — refused at validation, before
  anything runs;
- a flow that **does not** converge while running operations — held by the bound, which is what a
  count is for.

The runtime guard comes out where an engine carries one, rather than being kept alongside the
refusal. Once a policy that cannot run is refused before it runs, what remains for a stack-shaped
predicate to catch is a terminating flow it would wrongly refuse.

**Cost, priced rather than waved at.** One configuration reason, permanent within a `MAJOR`
(Section 8.5). Cheaper than the report assumed: Section 8.5 admits a new configuration reason in a
`MINOR`, and Section 6.10 states that such a reason is absorbed by the `usage_or_config` status
without needing an existing class edge, so no consumer has to change to receive it.

**The migration cost, named as one.** The refusal is unconditional — Section 6.10 refuses to run and
does not run a partial policy — so a repository carrying the edge on a branch that never commits is
refused on every invocation, including a `status` that would have completed. That lands hardest on
the population this report is about, the one upgrading from the reading 0078 replaced. It is accepted
rather than mitigated: the edge means nothing under 0078, an operator who is told at load time is
told before any operation has run and while nothing has to be undone, and the alternative that
preserves those invocations (option C) preserves them by deciding what the author meant.

**Relation to 0078.** 0078's chosen option stands and is not revisited. What is revisited is its
incidental refusal of static detection, recorded there append-only: the decline reasoned about a
cycle detector over the policy graph, and this is a check over a subgraph in which no cycle can be
conditional, so the argument it rested on does not reach this shape.

**Vectors, not only prose.** The boundary lands as `policy-validation` vectors on both sides — a
position-only cycle refused, a cycle through a typed result accepted, and the two near-misses that
an implementer is most likely to get wrong (the two-position cycle, and a position edge to an
operation it does not gate). Per the reporting engine: that pair is what stops the next engine
deriving the predicate it derived.

## Reconsideration trigger

Reconsider if a policy is found whose position-only cycle is unreachable in practice and whose
refusal therefore costs an operator a working invocation for a graph no invocation would enter — the
narrower rule would refuse only a cycle reachable from an entry point, at the cost of making
validation depend on the entry, which Section 6.10 currently never does. Reconsider separately if
re-entrance reached *through* a typed result is shown to produce a flow that cannot converge; option
B's predicate is not the answer there either, but the evidence would mean the discriminator this
decision rests on is incomplete.

Relates to 0078 (whose follow-through created the reachable configuration and whose incidental
refusal this revisits), 0079, 0066 (which gave the well-formedness conditions their reason), 0060
(which introduced the bound) and 0056 (which introduced the configuration-reason registry).
