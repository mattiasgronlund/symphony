# Background — 0115 Observing the budget is free; spending on it is not

## Context

Two items land together because one is the other's input.

**SY-1** (issue #60): since `merge` returns `checks_pending` and exits, Symphony must specify the
re-invocation loop — an overall bound terminating in a hold, conditional reads so polling is near
free, a cadence that respects the surfaced budget, and a positive terminal read on the current head
before merging.

**SY-2** (issue #62): promote the OPTIONAL budget guards to Core wherever many sessions share one
forge token, with a pre-emptive check before a mutating call, bucket-aware accounting, a warn
threshold, and back-off "not only park-on-exhaustion".

## What the engine work already settled

Most of SY-1 is no longer Symphony's to specify. Decision 0112 made the wait an engine operation:
`await_checks` reads until the checks pass, fail, a supplied bound is reached, or a supplied budget
floor is reached, with each read conditional where the forge supports one and the whole thing
bounded by parameters the consumer hands it.

So Symphony's half of SY-1 is smaller and sharper than the issue anticipated: **when** to dispatch
the wait, **which bounds** to hand it, and **what to do** with each of its four outcomes. The loop
itself is not written here and must not be — a second loop in Symphony over an operation that already
loops would be two bounds with no defined relationship.

Two of the issue's four requirements were also answered by that decision rather than by this one.
Conditional reads are the engine's (0106), and the "cadence that respects the surfaced budget" is the
`await_budget_floor` argument. What remains genuinely Symphony's is the overall bound terminating in
a hold, and the positive terminal read before the merge.

The `checks:*` trigger the issue asks for turns out to be unnecessary, and that is a real payoff
worth recording. Because 0112 made awaiting an **operation** rather than a front-end sequence, its
outcomes are already `<op>:<reason>` results — `await_checks:ok`, `still_pending`, `checks_failed`,
`budget_floor` — and the action-policy machine (Section 9.12) already routes those with the `#class`
fallback. A new trigger vocabulary would have been a second spelling for outcomes the machine
already carries.

## The budget: what is free and what is not

SY-2 asks for a promotion to Core, and the conformance stance chosen for this slice is to split by
what a requirement costs a deployment running one session at a time. Applied here, the answer is not
a single verdict, because the item is two things with very different costs.

**Observing** the budget is free. After decision 0107 the snapshot arrives in `outputs.forge_budget`
on every forge-touching operation, whether or not anything was near a limit. Symphony does not poll
for it, does not configure anything to get it, and cannot avoid receiving it. Recording what arrived
is therefore Core: a deployment that discards a figure the engine handed it has thrown away the only
evidence that would explain a drain afterwards, and it paid nothing for that figure.

**Spending on** the budget is not free. A pre-emptive check before a mutating call, a warn threshold,
paced dispatch, a floor below which work is held — each needs configuration, each needs an operator
to choose numbers, and each can wrongly withhold work from a deployment that was never near a limit.
That is exactly the shape Section 8.9's provider-quota gate already has, and it stays an OPTIONAL
extension for the same reason.

So SY-2 is neither accepted nor rejected as filed: the half that costs nothing becomes Core and the
half that costs something stays an extension. This is the stance doing real work rather than being
restated — the filed item bundled the two, and the bundle is what made "promote it to Core" look
like a single question with a yes or no answer.

## Why a sibling section rather than an extension of Section 8.9

Section 8.9 governs the **coding-agent provider's** account headroom. The forge's API budget is a
different account, reached with a different credential, spent by different operations, and — verified
while writing decision 0107 — accounted in different units, since a forge may account its
request-based and query-based interfaces separately and in different currencies.

Section 8.9 states the separation rule this inherits: account-wide quota "MUST NOT be summed into
Symphony-attributed consumed-token totals or budgets". Folding a forge budget into that section's
snapshot would put two accounts in one structure whose gate compares a single threshold, and the
first thing anyone would do with it is read one bucket's percentage as the deployment's headroom.

The new section is therefore free to differ where the forge case differs, and it does in two places
that matter: the figure arrives with an operation's result rather than from a poller, so it has no
`fetched_at`/`stale_after_ms` staleness machinery and no `UNKNOWN` state; and what a consumer does
with it is a pre-emptive check before a **mutating call**, not only a dispatch gate, because the
expensive moment for a forge budget is the write rather than the decision to take on work.

The cost of a sibling section is two mechanisms that look alike and can drift. That is real, and the
mitigation is that they share no fields and are not claimed to: this section states its own shape,
and neither reads the other's.

## The bound terminates in a hold, not a failure

The one piece of SY-1 that is wholly Symphony's is what happens when awaiting runs out.

`await_checks:still_pending` is `needs_caller` with `retryable: true` (0108, 0112), so the engine has
correctly declined to decide. Symphony's answer is that an issue whose checks did not complete within
the operator's bound is **parked**, not retried and not failed.

Retry is wrong because the backoff schedule (Section 8.4) exists for transient failures and a check
run that is still running is not failing — retrying re-enters a wait that will exhaust the same bound
again, and the run consumes a worker slot each time. Failure is wrong because nothing failed. Parking
is what Section 14.2 already does for a condition that needs a person and will not resolve itself,
and it is what `token_budget_exceeded` already does for the closest analogue: a bound the operator
set, reached.

`await_checks:budget_floor` parks too, and for a reason worth distinguishing: the work is fine and the
budget is not, so waking it on a schedule would spend the budget the floor was protecting.

## The positive terminal read before the merge

The issue asks for "a positive terminal read on the current head before merge", and the requirement
is already satisfied twice over — by `expected_head` (decision 0077), which refuses a merge whose head
moved after the read, and by decision 0114's identity re-verification.

What this decision adds is the ordering statement that makes them compose: a successful
`await_checks` is **not** authority to merge. It reports that the checks passed for the head it read,
and the merge must still condition on the head *it* reads. Awaiting and merging are two operations
with a gap between them, and a push into that gap is precisely the `head_moved` case. Stating it
prevents an implementation from treating `await_checks:ok` as a token that licenses an unconditioned
merge — which would undo 0077 by way of a feature added to help it.

## Steelmanning: fold the forge budget into Section 8.9 after all

The argument is maintenance: two quota mechanisms is one more than anybody wants, and Section 8.9's
snapshot shape — opaque buckets, a `Cached external signal` recovery class, a fail-open/fail-closed
policy under `UNKNOWN` — is proven, general, and was designed for heterogeneous providers.

It is the better argument than it first appears, and what defeats it is the staleness machinery. Half
of Section 8.9's structure exists because a provider quota is fetched out of band and can be old; a
forge budget is never old, because it arrives attached to the call that just spent it. Reusing the
shape would mean carrying `fetched_at`, `stale_after_ms` and an `UNKNOWN` state that cannot occur,
and an implementation reading that section would reasonably build a poller for a figure that needs
none.

## Reconsideration trigger

Reconsider if operators end up configuring the await bounds per repository and finding one set of
numbers wrong for every repository — that would mean the bound belongs in `repo.policy.toml`, where a
repository knows how long its own CI takes, rather than in operator configuration where this decision
puts it.

Reconsider also if the recorded budget turns out never to be read. Core recording is justified by its
being free and by its value after the fact; if no implementation surfaces it and no operator consults
it, the justification was about cost rather than value and the requirement is doing nothing.

## Relationship to other decisions

It consumes 0107's snapshot and 0112's operation, defers the loop to the latter, and sits alongside
0114, whose identity re-verification is the other half of the pre-merge check.
