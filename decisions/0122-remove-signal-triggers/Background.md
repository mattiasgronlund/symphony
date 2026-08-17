# Background — 0122 A trigger kind nothing can raise is surface, not a feature

## Context

Issue #70. `VCSX-SPEC.md` Section 5.1 makes signals one of three trigger kinds — agent milestone
signals (`ready-for-review`, `blocked`, `done`) and task-state events (`tasks:all_closed`,
`task:#needs_help`) — "raised by the consumer". Six further sections give them matching (5.3),
disposition (5.4), a place in an edge's `on` (6.5), a validation reason (6.11), an escalation nulling
rule (8.4), a reference-algorithm arm (12.1) and a conformance check (13.1).

Section 8.1's entry points are the front-end sequences and the individual operations, and no argument
carries a token. Nothing raises one.

## What the defect does

A repository can write `on = "ready-for-review"`, have it validate, have it counted for
`duplicate_edge` against the determinism rule, and never see it fire. That is worse than an
unimplemented feature: it is a policy surface that reports success. An author reading Section 5.1
writes the edge, the engine accepts it, and the behavior it was written for silently never happens.

The validation consequence is the sharper one. Section 5.4 requires "at most one edge per
`(from-context, trigger)` key" and Section 6.11 refuses a `duplicate_edge` on that key. Signals are in
the key space, so a conforming engine can refuse a policy for a duplicate pair of edges neither of
which is reachable.

## What is actually built, checked against `SPEC.md`

The one signal with a concrete producer is routed outside the engine everywhere it appears.
`SPEC.md` Section 8.10:

> The `tasks:all_closed` trigger (Sections 9.12, 11.6) fires when every implementation task is closed
> and, wired through `[driver]`, runs `ship`.

That is the consumer observing its own task state and invoking an entry point. The engine is never
told `tasks:all_closed` happened; it is told `ship`. `[driver]`'s `on` / `run` pair lives in
`repo.policy.toml` (Section 6.9) and nothing in Section 5 dispatches it — it is a table the consumer
reads. The milestone signals are the same: `SPEC.md` Section 11.6 carries `ready-for-review` among the
tracker's transition triggers, which Symphony evaluates.

So the trigger kind is specified as engine surface and realized, everywhere it is realized, as
consumer surface. Section 13.1's "an unmatched signal is a no-op" is satisfied vacuously by an engine
that cannot receive one, which is why nothing caught this.

## Decision

Remove signals from the engine's trigger kinds. The executor matches lifecycle positions and typed
operation results. `[tasks]` and `[driver]` stay in `repo.policy.toml` as tables the **consumer**
reads — which is what they already are — and the specification says so where it currently implies the
executor reads them.

## The consequence that reaches further than the issue does

`tracker.transitions` (Section 6.7) is keyed on a `from` state and a trigger, and its worked example
is `on = "pull_request_opened"`, glossed as "a consumer-supplied run outcome, or a milestone signal /
op:reason". Two of those three go away with this decision, so the transition graph needs its trigger
space re-grounded rather than merely trimmed.

The re-grounding is an improvement rather than a cost, and it is the part of this decision worth the
most scrutiny later. `pull_request_opened` is a second spelling for an event the operation registry
already names: `create_pr:created`. Keeping a signal vocabulary alongside the typed results meant two
tokens for one occurrence, differing in which layer emitted them, with nothing stating which a
repository should bind. Grounding `tracker.transitions` on the same `<op>:<reason>` triggers the rest
of the machine uses removes the second vocabulary instead of leaving it half-populated.

This is more surface than the finding named, and it is named here rather than discovered during the
edit: the issue lists nine touch points and the true set includes Sections 6.7, 6.9 and 7.3, plus
`VCSX-CONTRACT.md` Sections 5.1, 5.4 and 8.

## Review finding: the first re-grounding was wrong, and the defect it had is this decision's own

The plan above was first executed by re-grounding `tracker.transitions`' trigger space on the engine's
typed results, replacing `pull_request_opened` with `create_pr:created`. Checking that against
`SPEC.md` before finishing showed it was wrong, and wrong in a way worth recording.

`SPEC.md` Section 11.6 already fixes a **closed trigger vocabulary** for this table, with three
origins: agent milestone signals, run outcomes the orchestrator observes (`dispatched`,
`pull_request_opened`, `run_succeeded`, `run_failed`, `retries_exhausted`), and task-state events. It
also states who acts: "in state `from`, when trigger `on` fires, **Symphony** performs
`set_state(issue_id, to)`". So the table is consumer-read, its matching is the consumer's, and
`pull_request_opened` is not a second spelling for `create_pr:created` — it names a pull request
opened during the run by any means, which is a broader condition than one operation's result.

Re-grounding it on engine triggers would have narrowed a consumer vocabulary to the subset the engine
happens to produce, and broken four of Section 11.6's five run outcomes, none of which any engine
operation reports.

The shape of the mistake is the one this decision is about. Signals were engine surface with no engine
producer; the first repair made `tracker.transitions` engine surface with no engine matcher. Both
mistake a table that travels in `repo.policy.toml` for a table the executor reads. The correct
treatment is the one `[tasks]` and `[driver]` already get and that Section 11.6 already describes: the
repository owns the wiring, the consumer owns the matching and the vocabulary, and the engine
validates the document's determinism without matching it. That is what was applied.

Recorded rather than fixed quietly because the recurrence is the useful part: this is the second time
in one decision that consumer surface was read as engine surface, and the first time produced the
defect being repaired.

## Options considered

**Add a signal entry point to Section 8.1.** An invocation names a token and the executor runs the
policy from it. Steelmanned, and this is the option with the best claim: it makes every existing
clause true as written, it costs one entry point rather than nine deletions, and it gives a driver a
way to drive policy from an event that is not an operation result — which is a real capability, and
the one an autonomous consumer would reach for when it wants the repository rather than the driver to
decide what a milestone means.

It loses on what the new entry point would have to answer. An invocation entering at a signal has no
operation, so `entry` reports a token that is not an operation or a sequence; Section 8.6's
preconditions are scoped by "the entry point alone fixes that scope" and a signal entry needs a scope
of its own for the identity, the base and `git_access`; and Section 5.4's disposition rule — an
operation outcome must be disposed of, a signal need not — means a signal-entry invocation that
matched nothing returns `ok` having done nothing, which is a status a caller cannot distinguish from
work performed. Each is answerable. Together they are a second entry-point shape carried for a
capability that no consumer in evidence uses, and the evidence is that both consumers route around it.

**Keep signals and state that raising one is `Implementation-defined`.** The minimal edit. It loses
because Section 8.1's own rule forbids it: "argument *names* for shared concepts MUST match this
specification". A trigger a policy binds by name is a shared concept, and delegating its delivery
makes a `repo.policy.toml` that runs on one engine and not another — which is the property the whole
of Section 5 is written to prevent.

## Reconsideration trigger

Reconsider if a consumer appears that wants the **repository** rather than the driver to decide what
a milestone means — the case where `ready-for-review` should select between two operation flows the
policy defines, rather than selecting which entry point the consumer invokes. That is the capability
the entry-point option buys, and evidence of a repository that needs it is what would make the
answers it requires worth working out. Nothing in Symphony produces that today: its milestones select
a tracker state, and its task events select an entry point.

## Relationship to other decisions

It removes surface 0026–0032 introduced when the three shapes were unified into one machine. The
unification stands; what goes is the third trigger kind, which was the one shape that had no engine
producer. Issue #75's `SPEC.md` Section 9.12 drift is repaired in step with it (decision 0127).
