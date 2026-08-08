# Background — 0061 `pull` preserves the work branch's committed history

## Context

Issue #8. `VCSX-SPEC.md` Section 4.1 defines `pull` as "update the local work branch from its remote
counterpart" and Section 4.3 gives it two outcomes, `pull:ok` and `pull:conflict`. A `conflict` outcome
means the update reconciles a divergence, and the two ways to reconcile one — merge and rebase — differ
in whether the branch's existing commits survive. The document does not say which, so an engine that
chose a rewriting update would conform.

The issue reaches the gap from Section 9.1 and Section 11, which pin every push refspec to the work
branch and forbid a force push, and argues that a rebasing `pull` therefore leaves the branch
unpushable: the rewrite makes the next `push` non-fast-forward, Section 12.2 routes that to `integrate`
and retries, and the flow runs to the bound decision 0060 set and ends at `flow_exhausted`. Working the
issue moved that argument in both directions.

### Narrower: on git the chain does not reach `push:non_fast_forward`

`git pull --rebase` replays onto the branch's own remote counterpart, so the commits it rewrites are
exactly the ones the remote does not have, and the result descends from the remote tip. The next push is
a fast-forward. So on a git backend a rewriting `pull` does not by itself produce
`push:non_fast_forward`, and the live-lock decision 0060 bounds is not this defect's failure mode. The
harm on git is quieter, and it is the two items below.

### Wider: on jj the never-force rule turns the rewrite into a dead end

The issue names jj in passing — "the same shape would reach jj, where the natural update is also not a
merge" — and that is the case that carries its own argument. jj rewrites commits as an ordinary
operation, including commits already published, and publishing a rewritten commit needs a force push.
Section 9.1 and Section 11 forbid one without exception, so on jj a rewriting update produces a work
branch the engine cannot publish at all. That is not a retry loop with a bound at the end of it; it is a
branch that is stuck, whose `push` result is whatever the backend reports for a refused push. What
breaks is Section 2.1's goal that the same policy runs across checkout modes without policy changes: the
identical repository state ships on git and does not ship on jj.

### Wider: the required operation set cannot finish a rebase's conflict

This is the argument that settles the question independently of the backend, and it is derivable from
the document rather than from either VCS's behavior.

`pull:conflict` is `needs_caller` (Section 4.3), the need that names it is `resolve_conflicts`
(Section 8.4), and Section 5.5 has the caller resolve and re-invoke. On re-invocation Section 12.2 finds
a dirty worktree and dispatches `commit`. `commit` — "create a commit from the working tree"
(Section 4.1) — finalizes a merge, which is a single conflicted state resolved once. It does not
finalize a sequential replay, which stops once per conflicting commit and needs a resume step to reach
the next one, and Section 4.1's required operation set contains no `continue` and no `abort`. An engine
MAY define additional operations, but that does not close the hole: it would mean the *required* set
carries a `needs_caller` reason with no specified path back, which is a gap in the required surface
rather than something an engine's extension fills.

So `pull:conflict` is recoverable through the specified operations only if the update is a merge. The
shape is the one decision 0060 used to pick its unit: the answer follows from the action and operation
lists rather than being asserted over them.

### A rewriting update also fights `integrate`'s stated contract

Section 4.1 requires `integrate` to preserve "recorded conflict resolutions where the backend supports
them". A linearizing update drops the merge commit `integrate` created, and with it the resolution
recorded against that merge, and replays the base's own commits onto the work branch as the branch's
commits. The two required operations would undo each other's work: `integrate` records a resolution and
the next `pull` discards the merge it was recorded against.

### The host-dependence the issue found by test

The issue surfaced this from a failing test rather than from a reading, which is the part that shows the
gap is real rather than theoretical. git refuses a divergent branch outright when no strategy is
configured:

```
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

An implementation that does not decide therefore does not get a default — it gets the operator's
`pull.rebase`. Which of Section 4.3's two reasons comes back would then be a property of the machine the
engine runs on, which is the divergence Section 2.1's plugin-layer goal and Section 14's shared-token
rule exist to keep out of the contract.

## Options considered

- **Option A — state that `pull` preserves the branch's existing commits: the remote counterpart is
  merged in, and no commit already on the branch is rewritten, dropped or re-parented; state the
  no-rewrite half once as an engine-wide invariant beside Section 11's never-force rule (chosen).**
  Trade-offs: it fixes a required operation's semantics in the document rather than leaving it to the
  backend, which is a narrowing of what a conforming engine may do — affordable now, on decision 0056's
  and 0057's argument, because decision 0049's engine is not written. Costs one clause in each of two
  places rather than one, because a backend author reads Section 9.1 and a policy author reads
  Section 4.1.
- **Option B — forbid the rewrite without naming the reconciliation ("`pull` MUST NOT rewrite
  history").** What the issue literally asks for. Trade-offs: smaller, and it removes the harm this
  decision is about. Rejected because it leaves a fast-forward-only `pull` conforming, and under
  fast-forward-only a divergence has no reconciliation to attempt: one engine returns `pull:conflict`
  and another an `error`-class result for the same repository state. That is the same host-dependence
  one layer up, and `pull:conflict`'s reachability should not vary by engine.
- **Option C — a repository-configurable strategy, for example `[engine] pull_strategy`.** Trade-offs:
  it defers to the repository, which is what this engine does with a Way of Working everywhere else.
  Rejected because reconciliation is not a Way of Working: it costs a configuration key, a validation
  rule and a Section 6.4 cheat-sheet row in order to re-introduce the divergence as a supported feature,
  and it would offer a mode whose conflict the operation set cannot finish.
- **Option D — `Implementation-defined`, documented in Section 13.3.** Trade-offs: the cheapest change,
  and it makes each engine's choice visible. Rejected on the line decisions 0056, 0059 and 0060 hold:
  `Implementation-defined` covers mechanisms — checkout-mode detection, discovery precedence, argument
  encodings — and never the class or reason a caller branches on. Here it would go further than any
  existing use, because the choice changes what the repository ends up *containing*, not only what the
  envelope reports.
- **Option E — permit a rewriting update and add `continue`/`abort` operations so its conflict is
  resolvable.** Trade-offs: the honest way to support a rebase, and it would suit a jj-native workflow
  where a rewrite is the natural update. Rejected because it grows the required operation set, the
  reason registry and the lifecycle positions to serve a strategy nothing in the document asks for, and
  it does not remove the collision on jj — a rewritten commit that was already published still needs a
  force push, which Section 11 forbids. Recorded rather than discarded: a future rebase mode lands on
  this surface *and* on Section 11's rule, and needs both.
- **Option F — `pull` is fast-forward-only and a divergence is an error.** Trade-offs: the simplest
  rule, and it cannot rewrite anything. Rejected because it makes `pull:conflict` unreachable, leaving
  Section 4.3 carrying a dead token, and because a work branch legitimately diverges: a forge writes to
  the head branch when a reviewer commits a suggestion or presses "update branch". Refusing to reconcile
  hands the caller a state the engine has no operation to leave.

## Decision and reasoning

Choose **Option A**. `pull` updates the local work branch by merging its remote counterpart into it and
preserves the commits already on the branch; the no-rewrite half is stated once in Section 11 as a
property of the engine, alongside the never-force rule it makes sound.

Four properties carry the decision.

**The operation set decides it, so the clause records a consequence rather than a preference.** A
`needs_caller` reason is only worth having if the caller has a way back, and the only way back
Section 12.2 provides is resolve-and-`commit`, which finalizes a merge and not a replay. Any other
answer requires adding operations first. This is why the clause is worth stating even though it changes
no token: it makes an existing token's recovery path exist.

**Never-force is a constraint on the engine's own operations, and nothing said so.** Section 11 offers
the pinned, never-forced refspec as a scope guarantee a consumer's guard can rely on. That guarantee is
only safe if nothing the engine does creates a state that *requires* a force — otherwise the engine
eventually has to choose between its own rule and making progress. Stating the no-rewrite invariant next
to it closes that: the work branch is always publishable under the rule, so the rule never has to bend.
This is worth more than the `pull` clause it was written for, in the way decision 0060's `run_op` count
was worth more than the loop it was written for: an operation added later is checked against it by
asking only whether it can rewrite a published commit.

**Portability across checkout modes fails first, and it fails on jj.** Section 2.1 promises the same
policy runs across checkout modes without policy changes, and the failure is not symmetric between the
backends — git's rewriting `pull` degrades the history, jj's blocks the push. So the requirement has to
bind the *capability* in Section 9.1, where a backend author reads, and not only the operation
description in Section 4.1 that a policy author reads.

**The invariant is scoped to updates of the work branch, not to history in general.** Section 6.8
configures a `rebase` or `squash` merge strategy, and both rewrite the work branch's commits in the
sense a reader pattern-matches on. Neither is an exception, because both write the result to the *base*
branch and leave the work branch's own history intact — Section 11 says so rather than leaving the
reader to derive it, since an invariant stated one section away from `[messages]` would otherwise read
as narrowing the strategies a repository may configure. What the invariant constrains is the branch the
engine pushes, which is what makes it the precondition for never-force.

**`integrate` needs no clause of its own,** which agrees with the issue. Section 4.1 already calls it "a
merge/update-branch" and already requires it to preserve recorded resolutions; both name a
history-preserving update, and Section 11's invariant covers it without a second statement. Adding one
would restate a requirement rather than fix a gap.

**Deliberately left open and recorded.**

- **No built-in sequence dispatches `pull`.** Neither `ship` (Section 12.2) nor `land` (Section 12.3)
  runs it; it exists for a repository's own `[policy]` edges and for the embedded driver. That is
  consistent — the built-in routing reconciles through `integrate` against the base, not through `pull`
  against the remote counterpart — but it means `pull`'s recovery path is described here and exercised
  nowhere in the reference algorithms. Not changed: adding `pull` to `ship` would be a routing decision
  issue #8 does not ask for.
- **A `pull` whose remote counterpart does not exist.** Section 6.3 derives the work branch and it need
  not exist on the remote before the first `push`, so a `pull` before then has nothing to merge. Whether
  that is `pull:ok` as a benign no-op or an `error`-class result is unstated, and it is the same family
  as the questions issue #9 bundles rather than the one issue #8 asks.

We would reconsider if a backend appeared whose only update is a rewrite *and* which can publish a
rewritten branch without a force — a forge with an explicit replace semantics and an audit trail, say —
or if the operation set grew the resume step Option E describes. At that point the merge requirement
could relax to the weaker invariant that the *published* history is append-only, which is what
Section 11 actually needs.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.1, 11, 13.1, 13.2) and
`conformance/vcsx/README.md`. It resolves issue #8. Relates to 0060 (whose flow bound the issue's own
argument routes through, and which this decision finds is not the failure mode), 0058 (which last
changed Section 9.1's capability list and stated it as a minimum), and 0057 (whose
`major-stable surface` argument for changing settled surface before an implementation exists this
decision reuses).
