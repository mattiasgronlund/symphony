# Background — 0109 The other program the engine waits on

## Context

Issue #58's fourth primitive: the forge and VCS network timeout MUST be documented and configurable
"as the hook bound already is", and its expiry MUST surface as a retryable-transient reason rather
than a generic error. The issue notes the implementation carries "a good 60 s hardcode in
`http.rs`, but not a documented/configurable conformance point".

## The engine's own boundedness is conditional on a server it does not describe

Section 6.6 states why a hook is bounded, and the sentence is exact: "A hook is the one place the
engine hands control to a program this specification does not describe, so an engine MUST bound the
time it waits for a hook to answer."

It is not the one place. A network call is the other, and it has the same shape. The engine hands a
request to a server this specification does not describe and waits for an answer it does not
control. Nothing in the specification bounds that wait.

What that costs is not a slow operation. It is the property the whole contract rests on. The engine
"runs a bounded sequence and exits" (Sections 1, 2.2) — that is the sentence a consumer builds an
escalate-and-exit loop against, and it is what Section 5.6's flow bound and Section 6.6's hook bound
each exist to keep true. An unbounded network call makes it **false**: a TLS handshake to a host
that accepts the connection and never replies holds the invocation open indefinitely, and the exit
the consumer is waiting for never arrives.

The failure this reproduces is the one the study catalogues as hung wrappers with no timeouts. It is
also worse for the consumer than for the engine, because a consumer that shells out to a subprocess
and waits for an exit code has no way to distinguish a long clone from a dead socket, and the only
tool it has is a bound of its own — which is a consumer re-implementing a bound the engine is better
placed to apply, at the layer that knows which call is in flight.

A hardcoded value does not settle it either, and the reason is the one Section 6.6 already gives for
the hook bound's floor: a value fixed by the engine means the same work succeeds on one engine and
fails on another. Sixty seconds is generous for a forge API call and far too short for
`ensure_store` fetching a repository, so an engine that picks one number picks it wrong for one of
the two.

## Where the bound is configured, and why not in the policy

The consumer's, exactly as the hook bound is, and `repo.policy.toml` carries no key for it.

Section 6.6's reasoning transfers with one substitution and gains force on the way. There the
argument is that the in-sandbox half of `[hooks]` is worktree-sourced, so a bound declared in the
policy would be "a bound the bounded thing sets". Here the argument is more direct: the endpoint the
call reaches and the credential it presents are already the consumer's (Section 8.1, `git_access`,
`forge_access` and the credential pair), and how long to wait for an endpoint is a fact about that
endpoint and the network to it — the consumer's environment, not the repository's way of working. A
repository cannot know whether its policy is being run against a forge on a LAN or across a
saturated link.

So the bound arrives the way Section 11 has the credential arrive, and the sentence Section 6.6
closes with extends: the repository owns which unit runs, and the consumer owns how long the machine
will wait for it — for a hook it declared, and for a server the consumer chose to point the engine
at.

## The floor, and what it has to accommodate

`Implementation-defined` with a documented default, and an engine MUST admit a configured value of
at least 600 seconds — the same floor Section 6.6 fixes for the hook bound, for a reason of its own
rather than by copying.

The bound covers `ensure_store`, which fetches an entire repository. A first provision of a large
repository over an ordinary link takes minutes, and an engine that capped the configurable bound
below that would make the specification's own provisioning operation unusable at scale while
remaining conformant. The floor has to accommodate the **slowest** network unit in the capability
set, not the typical one.

That the floor's exact value is arbitrary is true here as Section 5.6 and Section 6.6 both say it is
of theirs. That it is fixed is not: without it, "configurable" permits an engine offering a maximum
of thirty seconds, and the consumer whose clone needs four minutes has a conformant engine it cannot
use.

The bound applies to **one network call**, not to the sum of an operation's calls. An operation
realized through two capabilities (Section 9.1: `integrate` is `fetch_base` then `merge_base`,
`provision` is `ensure_store` then `derive_working_tree`) is not held to one deadline across both,
because the second is local and a bound covering it would be bounding something other than a wait on
a server. An engine that applies different values to different capabilities is permitted and MUST
document them, which is what `Implementation-defined` already means here.

## What expiry reports

On the forge side, `forge_unavailable` with the condition `bound_elapsed` in `outputs` (decision
0108). That is the whole of the wiring, and it is why this decision follows 0108 rather than
standing alone: the reason and the condition token already exist, and an expired bound is exactly
the uninformed-repair case that reason names — back off and try again, with no reset time to aim at.

The condition token is `bound_elapsed`, deliberately reusing the spelling Section 6.6 fixes for a
hook that was still running when its bound elapsed. The same word for the same event on two
different units is a consumer reading one token, and inventing a second spelling would make a
diagnosis differ by which program the engine happened to be waiting on.

On the version-control side, the operation reports the reason it reports today —
`provision:unreachable` for a provision, whose gloss already names "the network between them", and
the universal `failed` for `integrate`, `pull` and `push`. That is decision 0108's recorded scope
limit applied here rather than quietly widened: this decision bounds the wait on both transports and
changes the reported reason on only one of them. A git fetch that hits the bound therefore still
fails the flow, which is the same gap 0108 named and the same trigger reopens it.

## What this does not do

It does not retry. The bound stops a call and reports it; whether to call again is the consumer's,
as Section 2.2 has it and as decisions 0107 and 0108 each preserved. An engine that retried inside
the bound would be making the bound mean something else — a bound on the total wait, silently
multiplied by an engine-chosen attempt count.

## Reconsideration trigger

Reconsider if the single-bound-per-call shape produces a documented per-capability table on every
conforming engine. That would mean the specification chose the wrong unit: the real bound would be
per capability, and stating one value with an allowance to vary it would be recording a default
nobody uses.

Reconsider also on a report of the 600-second floor being reached by an `ensure_store` in ordinary
use, which would mean the floor accommodates the wrong end of the distribution and the operation
needs a bound distinct from the API calls' rather than a shared one with a high ceiling.

## Relationship to the other engine decisions

0081 bounded the first program the engine waits on; this bounds the second. 0108 supplies the reason
and the condition token an expiry reports through. 0112's bounded loop sits above both and is
bounded in its own right, so a consumer's wait is bounded at each of the three layers that can hang.
