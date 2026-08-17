# Background — 0125 A gate that stopped existing should not read as a gate that passed

## Context

Issue #73. `VCSX-SPEC.md` Section 4.1 bounds `await_checks` by four terminal conditions — checks
passed, checks failed, a supplied bound reached, a supplied budget floor reached. Section 9.2's
`checks_state` has a fifth determinate answer: "none where the forge reports no required checks for
it". No reason covers it.

## What the defect does

It is not reachable through Section 9's catch-all. That rule governs a value a capability *could not
determine*, and requires the non-answer not be spelled as the absent case. `none` **is** the absent
case, and the specification treats it as determinate on purpose — Section 9.2 says so in the same
entry: "a state the backend could not determine MUST NOT be answered as no required checks, because a
pull request with no checks is mergeable and one whose checks could not be read is not."

So the specification knows a pull request with no required checks is mergeable, and the operation
whose job is to say when it is safe to merge has no token for it.

The reachable paths are the two that do not run `merge` first. `await_checks` is an entry point in its
own right (Section 8.1), so a driver composing its own sequence meets the condition on its first call.
And Section 7.2's `land --await` "dispatches `await_checks` and then the `merge` it already runs,
ending on the await's own result where that result is not `ok`" — so for a repository with no required
checks that is a `land` ending on an undefined result instead of merging, the operation composed to
make awaiting cheap defeating the merge it was composed with. Symphony's own route in,
`merge:checks_pending`, requires the forge to have reported checks pending first, so it reaches this
only where the required-check configuration changed between two reads; that is the narrower case and
not the one that matters.

Read literally — "until one of four conditions holds" — an invocation that supplied `await_bound_ms`
burns the whole bound and reports `still_pending` for a pull request that was mergeable from the first
read. An invocation supplying no await parameter "makes a single read and cannot loop" (Section 2.2)
and then has no terminal condition at all.

## Decision

A fifth reason, `await_checks:no_checks`, class `done`.

Class `done` because the flow should continue: Section 4.2 defines `done` as "the operation reached
its intended effect (including a benign no-op)", and a wait for checks that do not exist is the
benign no-op that definition already covers. Under the built-in default a `done` result with no edge
continues (Section 5.4), so a `land --await` against such a repository merges, which is the behavior
the composition was built for.

A reason of its own rather than folding into `ok`, because the two are different facts and the
difference is the one worth being able to see. `ok`'s gloss is "the required checks completed
successfully"; reporting it for a pull request with no required checks describes something that did
not happen, and leaves a consumer unable to distinguish a repository whose checks all passed from one
that configures none. That distinction is how a merge gate silently stops existing — a required check
removed from branch protection, or a workflow file that stopped matching, turns every subsequent merge
into an unchecked one, and under a shared `ok` nothing in the record shows the day it changed.

The `#class` fallback is what makes the new token cheap: Section 4.3 states that "new reasons MAY be
added in a compatible release and existing consumers absorb them through the `#class` fallback", so a
consumer with a `#done` edge or none at all behaves exactly as before, and one that wants to notice
binds `await_checks:no_checks`.

## Options considered

**`await_checks:ok`.** Steelmanned: it is the smallest possible change, it adds no token to the
major-stable surface, and the disposition is identical — the flow continues either way, so the
distinction buys nothing a consumer *must* have. The counter is not that a consumer must have it but
that the cost of providing it is one row and the cost of withholding it is a fact the envelope cannot
express. Where the two dispositions agree, the token is free; where a deployment later wants to alert
on an ungated merge, a shared `ok` is not something a policy can recover.

**`no_checks` as `needs_caller`.** Surface it as a condition to look at rather than continue past.
Steelmanned: for a deployment whose Way of Working requires checks, a pull request with none is
exactly the anomaly worth stopping on, and `needs_caller` is how this specification stops without
failing. It loses because the engine is the wrong layer to hold that opinion — Section 1.1 states that
the engine "ships no Way of Working of its own", and "a repository must have required checks" is a Way
of Working. A repository that holds it writes `await_checks:no_checks → fail` or `→ escalate` and gets
the behavior; a repository that does not is not made to. Defaulting to `needs_caller` would escalate
on every merge in every repository that runs no checks, which makes the common case the noisy one.

## Reconsideration trigger

Reconsider if `checks_state` gains a way to distinguish "this pull request has no required checks"
from "this forge reports no required checks for any pull request" — the second being a forge whose
check interface is not configured rather than a repository that runs none. The single `none` answer
collapses them, and a consumer that wanted to alert on an ungated merge would be alerting on both.
Nothing in the current capability distinguishes them, and inventing the distinction on the engine side
would be normalizing a forge's model, which Section 9.2 refuses for buckets on the same ground.

## Relationship to other decisions

It completes the `await_checks` reason set 0106–0112 introduced. The `SPEC.md` disposition it forces
is decision 0125's own scope rather than a separate one: Section 9.10 lists four outcomes and gains a
fifth.
