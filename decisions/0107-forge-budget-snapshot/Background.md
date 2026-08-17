# Background — 0107 The budget the call already saw

## Context

Issue #58's second primitive: every forge-touching operation MUST emit the observed rate-limit
snapshot in the envelope's `outputs`, "whether or not it hit a limit — so the consumer governs
budget from the same call, not a separate probe".

The failure it comes from is stated precisely in the issue and is worth keeping in that form:
exhaustion was **discovered as a mid-`land` failure**. Not as a warning, not as a threshold
crossing — as the operation that was supposed to merge the work reporting that it could not.

## What a consumer can learn about its own budget today

Nothing, unless it fails.

A consumer supplies one `forge_credential` at one `forge_access` (Section 8.1) and dispatches
operations against it. Every capability in Section 9.2 reaches the code host. On each of those
calls the forge reports what the credential has left — every mainstream forge does, in response
headers or in the response body — and the engine discards it. A `create_pr:created`, a
`merge:checks_pending`, a `status` carrying a pull-request state: each is a call that observed the
budget and reported everything except the budget.

So the only signal a consumer receives is the exhaustion itself, which arrives as a failed
operation. A consumer holding one credential across many concurrent units of work — the topology
that produced the report — cannot pace, cannot warn, and cannot decide to defer a mutating call
until a reset, because the number that would inform each of those decisions was read by the engine
and thrown away.

This is the half of the polling problem that 0106 does not solve. 0106 makes a *conditional* read
cheap where the forge offers one; verified there, GitHub GraphQL offers none, so a consumer polling
that API has no cheap read available at any price. What it can still do is pace — but only if it
can see what it is pacing against.

## Why it rides along rather than being probed

The obvious alternative is a capability of its own: a `budget()` the consumer calls when it wants
to know. It loses twice, and both are mechanical.

A probe **costs the thing it measures**. On a forge that charges per request, asking how much
budget remains spends budget, so a consumer polling its headroom every thirty seconds has built a
second drain to monitor the first. On a forge with a dedicated free endpoint for it that is not
true — GitHub's rate-limit endpoint is documented as not counting — but a specification cannot rest
a primitive on one forge's exemption.

A probe's answer is also **stale before it is used**. The consumer's real question is not "what was
my budget a moment ago" but "what did my last call leave me", and only the call itself can answer
that. Between a probe and the next mutating call, every other session sharing the credential has
spent against the same bucket. Riding along makes the number and the call that produced it the same
event.

So the snapshot is stated over the capability list, in the shape Section 9.1 already uses to state
its write-allowance over the whole list rather than on the capabilities that happen to need it:
every capability of Section 9.2 answers the budget the forge reported on the call it made, or that
the forge reported none.

## Buckets are opaque, and the numbers are in the forge's own unit

Verified against the upstream documentation on 2026-08-17: GitHub's GraphQL API is accounted in
**points** — "5,000 points per hour per user", with a separate secondary limit of "no more than
2,000 points per minute" — and its own documentation states that "The REST API also has a separate
primary rate limit". Two budgets, two accounting units, one credential.

Two things follow, and both are requirements rather than presentation choices.

The snapshot carries **several buckets**, not one number. A consumer that read a single "remaining"
would be reading whichever bucket the engine happened to pick, and pacing REST work against a
GraphQL balance is not a conservative approximation — it is an unrelated number. The observed
drain exhausted one of the two while the other was untouched.

Bucket **identity is opaque**: the engine carries the name the forge used and compares nothing. A
bucket set the engine normalized would be a mapping from each forge's accounting model into one the
engine invented, and the engine has no basis for it — it does not know whether a forge's second
bucket is a stricter window on the first or an unrelated pool. A consumer compares a bucket against
itself over time, which is the only comparison the data supports.

The numbers therefore carry no unit this specification names. `limit` and `remaining` are counts in
the bucket's own unit, which is the forge's; a `resets_at` says when the bucket refills. An engine
that divided one bucket's remaining by another's limit would be computing with two different units,
which is why the snapshot states none.

## The engine reports and does not act

Section 2.2 keeps retry, back-off and budget outside the engine, and this decision does not move
them. Nothing here pauses a dispatch, delays a call, or refuses an operation because a bucket is
low. The engine observes a number it was already given and puts it where the consumer can read it.

That boundary is worth stating because the snapshot makes the opposite tempting: once the engine
holds `remaining`, having it decline to make the next call looks like an improvement. It is not one
the engine can make correctly. Whether a low bucket should stop a call depends on what else the
consumer intends to spend it on, how many other sessions share the credential, and whether the
operation at hand is the one worth spending the last of it on — none of which is visible from
inside a single invocation. Decision 0112's bounded loop takes the cadence argument and takes it as
a consumer-supplied parameter, which is the same boundary drawn one layer up.

## Where it is absent

The key is absent where the invocation reached no forge capability, and equally where it reached
one and the forge reported no budget. Those are different events and they get one spelling,
deliberately: in both the consumer learned nothing new and does the same thing about it — keeps
whatever figure it last held. That is the reasoning 0104 recorded for `hook_unanswered`, where
three conditions carrying one repair take one token and the diagnosis lives elsewhere.

This is the one place in the surrounding text where an absence is *not* distinguished from a
non-answer, so the departure is stated rather than left to be noticed. Section 9's discipline
governs a capability answering a **value the engine composes an operation from** — a value that
decides what the operation does. The budget snapshot decides nothing inside the invocation: no
operation branches on it, no reason is derived from it, and no precondition consults it. It is
carried through to the consumer untouched. A distinction the engine makes and nothing acts on is a
field with no reader.

## What is not covered

`git_access` and the four network-touching VCS capabilities (Section 9.1) report no budget and are
not in scope. A git transport does not publish a quota, so there is nothing for a backend to
observe and a snapshot there would be a field permanently absent. The report's failures were forge
failures, and the scope matches.

## Reconsideration trigger

Reconsider if a forge appears whose budget is reported **only** on a dedicated endpoint and not on
ordinary responses. The whole design rests on the number arriving with the call; a forge that
withholds it there forces either a probe (which this decision rejects) or a permanently absent key
(which tells a consumer nothing), and neither is a small adjustment to what is written here.

Reconsider also if a consumer is observed pacing correctly on the snapshot and still exhausting the
budget, which would mean the figure the forge reports is not the figure the forge enforces —
against a shared credential with concurrent spenders that is possible, and it would make the
snapshot advisory in a way this record does not currently claim it is.

## Relationship to the other engine decisions

0106 makes a read cheap where the forge supports it; this makes the spend visible whether or not it
does. 0108 gives the exhaustion itself a reason a consumer can route on, distinct from a permanent
failure. 0112's bounded loop consumes both.
