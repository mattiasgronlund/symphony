# Background — 0123 A termination guarantee that holds in one encoding is not a guarantee

## Context

Issue #71. `VCSX-SPEC.md` Section 5.5 defines a resume as re-entering "the point that raised the
need", and Section 5.5 requires that "any **re-entry** a resume causes counts against the flow bound
(Section 5.6)" — the stated reason being that "a resolver that always resolves would otherwise loop
there with nothing to stop it".

Two facts therefore have to survive from the invocation that escalated to the one that resumes: which
point, and how much of the bound is spent. Nothing carries either. Section 8.2's fields and
`outputs` keys carry neither, Section 8.4's `escalation` carries neither — its `op` is explicitly null
in the case Section 5.5 says the resume must re-enter — and Section 8.1 accepts no resume argument.

## What the defect does

Section 8.1 states the engine's own model plainly, arguing for the validator round trip:

> each invocation is a bounded run that exits, so there is no engine-side cache for a validator to
> live in

Under that model a resume cannot re-enter a point a previous invocation reached, and a bound cannot
accumulate. Section 8.3 makes it concrete for the subprocess encoding: an escalation is exit `10`,
and the process is gone.

So the property Section 5.6 relies on holds for an in-process embedded driver, whose resolver returns
into a live traversal, and fails for everything else. Section 5.5's interactive arm — "The human
resolves and re-invokes" — starts a fresh invocation with a fresh bound at the entry point rather than
at the point that raised the need. A resolver that always resolves therefore loops forever under the
interactive front-end, which is exactly the failure the counting rule was written to prevent, and
Section 13.1 asserts the property with no front-end qualification.

Two further claims become conditional. Section 8's "The contract is the same either way; only the
encoding differs" is false if a resume is expressible in one encoding and not the other. And Section
5.5's closing sentence — `escalate` is "the single point at which their behavior legitimately
differs" — is false if the two front-ends also differ in whether the flow bound bounds the work or
one invocation of it.

## Decision

Carry the resume. An invocation that ends at `needs_caller` with a **resolvable** need returns an
opaque `resume_token` in `outputs`; a later invocation supplies it as the `resume` argument and
re-enters the point the token names, with the flow bound continuing from the count the token carries.

Opaque, for the reason `pr_state_validator` is opaque and the base ref and the coordinate are: the
consumer round-trips it and interprets nothing. Here the value is the engine's own rather than
another party's, which makes opacity a choice rather than a necessity — and the choice is worth
making, because the alternative publishes the executor's traversal position as contract surface. An
engine would then owe a stable spelling for "the point that raised the need" across every graph shape
a policy can express, which is a schema for the executor's internals in exchange for nothing a
consumer does with it.

The token binds to what it was issued against. An engine MUST refuse one it cannot establish as its
own and current — a token issued under a different policy, against a different repository, or by a
different major version — with a precondition reason of its own rather than resuming into a point
that no longer means what it meant. Refusing is fail-closed in the direction that matters: a rejected
resume costs a re-invocation from the entry point, where an accepted stale one runs an operation the
policy no longer routes.

Holds get no token. Section 8.4 already fixes that `intervention` and `flow_exhausted` are not
resolvable and that "a front-end MUST NOT bind a resolver to either and MUST NOT resume the flow on
either" — so the two needs that name a hold carry no `resume_token`, and its absence is what makes the
prohibition checkable from the envelope rather than only from the policy that produced it.

## What the token does not carry, which is the load-bearing half

Section 5.5 states a property this decision must not break:

> Nothing a position established carries across a resume. The state a position inspected is read
> again, so an operation conditioned on an inspected identity — `expected_worktree`, `expected_head`
> — is conditioned on what the re-entered position saw.

The token carries the **point** and the **count**. It carries no `expected_worktree`, no
`expected_head`, and nothing else a position established. That is what keeps the guarantee intact: an
engine that packed the inspected identity into the token would hand an operation state no position
had inspected since, which is the condition Sections 4.3 and 6.6 exist to report rather than to
produce. The distinction is worth stating in the specification and not only here, because a token
that already carries two things is where a third looks harmless.

## Options considered

**Scope the guarantee to the in-process front-end and say so.** State that a resume is an embedded-driver
behavior, that an interactive re-invocation is a fresh invocation with a fresh bound, and rewrite
Section 5.5's closing sentence. Steelmanned, and it is the honest minimal move: it adds no surface,
it makes an existing property true instead of aspirational, and it costs two paragraphs. Nothing in
evidence resumes across a subprocess boundary today.

It loses on what it concedes. Section 5.6's bound is the engine's answer to non-termination, and
Section 5.6 is written as an unconditional property — "a bound on that count bounds every loop the
schema can express". Scoping it makes the answer conditional on an encoding the consumer chose for
unrelated reasons, and leaves the interactive front-end with a resolver loop nothing stops. A
consumer reading Section 5.6 would then have to read Section 5.5 to learn whether the bound applies
to it, which is the shape of guarantee this specification avoids elsewhere by stating properties over
what a consumer can check.

**Bound the resolver instead.** Treat the front-end's resolver as the third place the engine hands
control to a program it does not describe, after a hook and a network call, and bound the wait.
Steelmanned: it closes a real hole the other two options leave open — nothing today bounds an
engine's wait on a resolver, and Sections 6.6 and 9 bound the other two for exactly that reason.

It loses as a *replacement* rather than on its merits. It bounds how long one resume waits and says
nothing about how many resumes happen, so a resolver that returns instantly every time still loops
forever. It is orthogonal, not alternative, and it is recorded here as the reconsideration trigger
below rather than folded in — this decision's scope is the carrier.

## Reconsideration trigger

Reconsider when an engine's wait on an escalation resolver is shown to hang an invocation in
practice. That is the hole the third option names, this decision does not close, and Sections 6.6 and
9 have a settled shape for. It is left open deliberately: the argument for bounding a hook and a
network call is that the engine hands control to a program *this specification* does not describe,
and a resolver is the consumer's own — a consumer holding its own invocation open is a different
condition from a hook that hangs, and whether it deserves the same treatment is worth deciding on
evidence rather than by analogy.

## Relationship to other decisions

It rests on 0060's flow bound and 0059's park/hold mapping, and takes both as given: the bound's value
and floor are unchanged, and the two holds keep their unresolvable status, which is what lets the
token's absence carry meaning.
