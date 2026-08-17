# Background — 0112 The wait becomes an operation, and the non-goal it tests gets written down

## Context

Issue #60 proposes a consumer-neutral governance layer and states its own fork: either (a) a shared
thin consumer client library both Symphony and a skill-driven agent call, or (b) a bounded engine
subcommand — `vcsx await-checks` / `vcsx land --await` — "cleanest for a skill (zero consumer
logic), at the cost of adding a *bounded* wait to the engine". The choice was put to the maintainer
and **(b)** was selected.

The motivation is worth restating because it is not convenience. There are two consumers — the
Symphony orchestration product and an agent invoking `vcsx` from a skill — and the check-watch loop
sits in neither specification. If it is built inside the product, the skill consumer must
re-implement it, and the study records what that re-implementation looked like in practice: a
hand-rolled forge poll loop that drained an API budget to zero.

## A finding, first: the boundary this decision changes was never written

The objection to (b) is that the engine scopes retry, back-off and budget to the consumer, so a wait
inside it undoes the layering. That is how the study frames it, and it is how two earlier decisions
in this same slice were drafted — 0107 and 0109 each wrote "(Section 2.2)" after the claim.

Section 2.2 does not say it. Its Non-Goals are four: credential storage, any agent-sandbox or
secret-isolation mechanism, prescribing a commit convention or branch-protection policy, and a
general-purpose workflow engine beyond the VCS/forge domain. Retry, back-off and budget appear
nowhere in the section, and grepping the whole document finds the claim asserted only in text this
slice added.

So the boundary everyone has been reasoning from — including this repository's own decision drafts,
and the downstream study that says "VCSX deliberately scopes out retry, back-off, and budget" — is
**folklore**. It is substantively true of the design: nothing in the engine retries, no operation
backs off, and until 0107 no budget was even observable. But it was never stated, which means it was
never checkable and no decision was ever recorded for it.

That changes what this decision has to do. You cannot state a bounded exception to a rule that does
not exist. So Section 2.2 gains the non-goal first — deciding *when* to retry, *how long* to back
off, and *what a budget is worth* are the consumer's — and this decision's addition is then a
stated, bounded exception to a written rule rather than a quiet drift away from an unwritten one.
The two citations 0107 and 0109 made become true in the same change, and that is recorded in their
Plan files rather than left to look like they were right all along.

## What (b) actually costs, and how the cost is contained

The real objection to the subcommand is not that the engine waits. It already waits: on a hook, for
a bound Section 6.6 fixes, and on a network call, for the bound 0109 just added. Decision 0081
settled that a bound is a bound on a **unit**, and a bounded wait inside a dispatch is not a
violation of running a bounded sequence and exiting. A poll loop with a bound is one more such unit.

The real cost is that a *budget-aware cadence* needs a budget policy, and a budget policy is
consumer configuration. An engine that decided how long to sleep between reads, or how much
remaining budget is too little to keep polling, would have taken exactly the decision the non-goal
above reserves — and it would have taken it without knowing what else the consumer intends to spend
that budget on, or how many other holders of the same credential are spending concurrently.

So the containment is: **the engine executes a wait the consumer parameterizes, and decides none of
it.** The bound, the read interval, and the budget floor all arrive as invocation arguments, the way
`git_access` and the credential pair already do. The engine loops, reads, compares against numbers
it was handed, and exits with an envelope. Remove the arguments and there is no loop; supply
different ones and the same engine behaves differently. Nothing about "when to retry, how long to
back off, what a budget is worth" is answered inside the engine.

That is what makes this an exception to the non-goal rather than a repeal of it, and the distinction
is checkable: the non-goal forbids the engine *deciding* those three, and this operation decides
none of them.

## The loop needs a read that does not exist

Awaiting checks means polling something. What?

`merge` reports `checks_pending` and exits, so a loop could re-dispatch `merge` until it stops
saying so. That is the shape requiring no new surface, and it is wrong: every attempt is a *mutating*
request, charged at a mutation's cost against the budget, with whatever side effects a forge attaches
to a refused merge request. A poll loop built out of merge attempts is the most expensive possible
way to ask a cheap question.

Decision 0106 gave the conditional-read validator to `pr_state`, because `pr_state` was the only
forge read that existed. Issue #58's VX-1 names two — "check status, PR state" — so 0106 covered one
of the two, and the other is added here where its consumer appears. `checks_state` joins Section 9.2
with the same four answers 0106 fixed: the aggregate state of the pull request's required checks,
none where the forge reports no required checks, `unchanged` against a presented validator, or
undetermined. The conditional-read machinery is reused rather than rebuilt, which is the payoff for
having stated it over a validator rather than over an ETag.

Adding the read has a benefit beyond the loop: the check state stops being reachable only by
attempting a merge. A consumer that wants to know whether checks passed no longer has to ask a
question whose answer, if favourable, merges the work.

## Why it is an operation and not only a front-end

`await_checks` is an operation in Section 4.1's sense and an entry point in Section 8.1's, which is
the arrangement `status`, `commit` and `merge` already have. That matters for three things the
alternative — a front-end sequence like `ship` and `land` — would have left unanswered.

It gets `<op>:<reason>` results, so its outcomes route through the action-policy machine like every
other operation's and a repository can bind them. A front-end sequence produces no operation token of
its own.

It is gated at no fixed lifecycle position, joining `integrate` and `pull` in that category
(Section 4.1). A gate on a poll loop would be a hook running before a wait, which inspects nothing
and blocks nothing worth blocking.

And it counts as **one** dispatch against the flow bound (Section 5.6), not one per read. The flow
bound counts `run_op` dispatches, and the loop's own bound is what limits its reads; conflating the
two would make a policy's flow budget depend on how long a CI run took.

`land --await` is then the composition rather than a second mechanism: `await_checks` followed by the
`merge` `land` already runs.

## The need and the operation share a name, deliberately

`merge:checks_pending` has carried the default need `await_checks` since the registry was written.
The operation added here has the same spelling, and the collision is worth keeping rather than
renaming around.

The need names what the caller must do; the operation is now the thing that does it. A consumer
reading `need: await_checks` previously had to build a loop; it can now dispatch the operation the
need is named after. Needs and operations are separate namespaces (Sections 4.1, 8.4), so nothing is
ambiguous, and the coincidence makes the contract self-describing at the one point where a consumer
was previously sent away to write its own machinery.

## Terminal outcomes

Four, plus the transient reasons 0108 already defines for any forge-touching operation:

- `ok` — the required checks completed successfully.
- `checks_failed` — they completed and did not pass. Class `error`, mirroring `merge:checks_failed`,
  because there is nothing to wait for.
- `still_pending` — a bound was reached with checks still pending. Class `needs_caller`, need
  `await_checks`, retryable: awaiting again is the repair, and the caller decides whether the work is
  worth more waiting.
- `budget_floor` — the consumer's budget floor was reached. Class `needs_caller`, need `retry_after`,
  retryable. It is a reason of its own rather than `still_pending`, because the two carry different
  repairs: one is met by waiting longer and the other by waiting for a bucket to refill, and a
  consumer that cannot tell them apart will raise the wrong bound.

`still_pending` is deliberately not `rate_limited`'s shape even though both end in waiting. Nothing
refused anything: the loop did what it was told for as long as it was told to.

## What was not built

No retry of failed operations, no back-off curve, no budget accounting across invocations. The
operation reads until one of four conditions holds and exits. In particular it does not re-attempt a
`merge` that returned `head_moved`, does not widen its own bound, and does not carry state between
invocations — the engine holds nothing between them (Section 1.3), so a consumer re-invoking supplies
the validator and the bounds again, exactly as 0106 has it supply the validator.

## Steelmanning (a) and (c)

**(a) a shared consumer library.** It is the option that changes no contract, and its advocate's
strongest point is that the cadence policy stays with the party that owns the budget, where this
decision has to work to keep it. It loses on the consumer it was proposed for: a skill invoking
`vcsx` from a shell has a dependency-free relationship with the engine today, and a library turns
that into a language-specific build dependency. The failure mode is not theoretical — a consumer that
finds the library inconvenient hand-rolls the loop, which is the exact origin of the drain, and a
library nobody links is a governance layer that governs nothing.

**(c) specify the loop's obligations, leave the packaging implementation-defined.** This is the
repository's own idiom and it was the recommended option on the sheet. It loses on the same consumer
for a sharper reason: it specifies nothing a skill can *call*. "Written once" is the whole premise of
issue #60, and an obligation each implementation satisfies its own way is written once per
implementation. It would have been the right answer if the two consumers needed different loops; they
need the same loop.

## Reconsideration trigger

Reconsider if the argument surface grows. Four parameters is already at the edge of what belongs on
an invocation, and a fifth — a back-off curve, a per-bucket policy, a jitter — would mean the engine
is accumulating the budget policy this decision claims it does not hold, one argument at a time. That
accumulation, not the wait itself, is what would turn (b) into the mistake its objectors expect.

Reconsider also if a forge appears whose check state is not aggregable — where "the required checks"
is not a single answer but a set a consumer must judge individually. `checks_state` answers one
aggregate, and a consumer needing per-check detail would be back to reading the forge itself.

## Relationship to the other decisions

It consumes 0106's validator (extended here to a second read), 0107's budget snapshot (the floor is
compared against it), 0108's transient reasons and `retryable`, and 0109's per-call bound, which
bounds each read inside the loop the loop's own bound bounds in aggregate. It states the non-goal 0107
and 0109 assumed.
