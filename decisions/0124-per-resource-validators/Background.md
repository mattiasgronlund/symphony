# Background — 0124 One token for two resources is a conditional read against the wrong thing

## Context

Issue #72. `VCSX-SPEC.md` Section 9.2 defines two capabilities that each take a `known_validator` and
each issue one: `pr_state` over the pull request, and `checks_state` over its required-check
aggregate. Section 8.1 defines a single `pr_state_validator` argument and presents it to both — "on
the `status` read and on each `await_checks` read" — and Section 8.2 returns a single validator, from
the pull-request data.

## What the defect does

The two resources move independently. A check run completing moves the check aggregate and not the
pull request; a push moves both. So a validator issued for one is not an answer about the other.

Section 9.2's prohibition is written to stop a backend inventing an `unchanged`:

> A backend MUST NOT answer `unchanged` where it presented no validator or made no conditional read

A backend handed the other resource's validator satisfies that clause to the letter — it presented a
validator and made a conditional read — while answering about the wrong resource. On a forge whose
validators are opaque entity tags over separate resources the mismatch is a plain miss and the read
is merely unconditional, which costs a saving and nothing else. On a forge that derives both from one
modification timestamp it is an `unchanged` for a resource that did move, which Section 4.1 turns
into `pr_state_unchanged` and a caller reads as "the state I hold is current".

That is the failure Section 9 names as silent by construction: the engine composes an operation from
a determinate-looking value and reports the outcome that value implies. It is worth being precise
that the second case needs a particular kind of forge to bite, which is what makes it the kind of
defect that survives review — a backend against a well-behaved forge shows nothing wrong.

## The saving is absent exactly where it was wanted

`checks_state`'s validator has no way out of the engine at all: Section 8.2 returns one validator and
attaches it to the pull-request data. Within one invocation Section 8.1 carries it forward from read
to read, so a long `await_checks` is cheap. Across invocations there is nothing to carry.

Across invocations is the normal case. `SPEC.md` Section 9.10 **parks** the issue on
`await_checks:still_pending` and `await_checks:budget_floor`, so the next read happens in a later
invocation — and the whole reason `checks_state` was given a conditional read is that polling a
CI run is the expensive loop. The saving exists inside a single bounded wait and disappears across
the park-and-resume cycle a consumer actually runs.

## Why the existing rule did not settle it

Section 9.1 fixes which reads carry a validator, and does it well — for `pr_state`:

> the engine presents a `known_validator` on the read whose answer it **reports** — `status`'s — and
> on neither of the two an operation **conditions a write on**.

That sentence is derived from `pr_state`'s three readers and settles `pr_state` completely.
`checks_state` has one reader and conditions no write, so it falls outside the sentence that decides
the question, and is covered only by Section 8.1's "on each `await_checks` read" — which is the clause
that hands it the other resource's token.

## Decision

Two arguments and two returned values, each named for its resource: `pr_state_validator` keeps its
name and its resource, and `checks_state_validator` joins it. Each is presented only to the
capability that issues it.

Keeping `pr_state_validator`'s spelling matters: it is in the major-stable surface, `SPEC.md` and the
conformance corpus already name it, and its meaning is unchanged — what changes is that it stops
being presented to a capability that did not issue it.

The engine holds each opaque, as it already holds the one. Section 9.2's `unchanged` prohibition is
extended by one clause: a backend MUST NOT be presented a validator issued for another resource, and
the obligation sits on the engine, because which resource issued a token is the one thing the engine
knows and the backend cannot check — it holds an opaque value it was handed.

## Options considered

**One opaque bag keyed by resource.** A single argument carrying a map from resource to validator,
extended by a key whenever a conditional read is added. Steelmanned: it is one argument rather than
one per resource, it makes a third conditional read a key rather than an argument, and it keeps the
round trip to one field in `outputs`. It loses on the engine's own posture toward opaque values —
Section 8.1 holds each opaque value separately and supplies it to the one plugin that takes it, and a
keyed bag would make the engine parse a structure to route its parts, which is the mixing Sections
9.1 and 9.2 are separate to prevent. It also makes the absent case ambiguous in a way two arguments
do not: a bag missing a key and a bag not supplied are two spellings of one condition.

**Leave one argument and require backends to ignore a foreign validator.** Steelmanned: no new
surface, and a backend that stamps its validators per resource can detect the mismatch. It loses
because it cannot be stated as a guarantee a consumer checks — Section 9.2 already says "what the
backend asked the forge is not something the engine can observe" — so it would be an obligation on the
party with the least information, enforced by nothing.

## Reconsideration trigger

Reconsider the shape if a third conditional read is added. Two arguments are the right answer for
two; at four the keyed bag's argument gets stronger, and the point to revisit is when a third read
appears rather than when the second one is tidied.

## Relationship to other decisions

It repairs the conditional-read surface 0106–0112 introduced, in the half that was added for
`await_checks` and inherited `pr_state`'s argument. It changes no proto class and adds no reason.
