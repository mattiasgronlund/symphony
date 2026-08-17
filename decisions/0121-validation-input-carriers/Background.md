# Background — 0121 A validation input with no carrier is a verdict each engine reaches on its own

## Context

Issue #68. `VCSX-SPEC.md` Section 6.11 fixes what validation is judged from — "five inputs and no
others" — and turns three configuration reasons on the last two of them: `set_state_unbound` on "the
actions the consumer can effect", and `template_unbound` and `transform_unbound` on "the repository
units the consumer bound".

Section 8.1 enumerates the invocation surface twice, once as arguments and once as the
consumer-configuration keys, and neither list carries either input. So two of the five arrive through
nothing.

## What the defect does

The three reasons are in the major-stable surface. Section 8.5 fixes "the configuration reasons
(Section 6.11)" as unchanging within a `MAJOR`, so these are public tokens a consumer branches on —
and their truth conditions depend on values the contract does not transmit. Two conforming engines
handed the identical policy document and the identical consumer configuration may legitimately
disagree about whether a policy is valid, which is the one thing a validation registry exists to
prevent.

The concrete cost is the one Section 6.11 already names, arriving by the route it was written to
close:

> first use of a `template` body source is a `create_pr`, which a `ship` reaches only after it has
> pushed (Section 12.2). A policy that cannot compose a body would then publish a work branch before
> saying so.

An engine that cannot read the input has no way to refuse early, so it defers to first use, and that
is exactly the failure. `transform_unbound` carries the same argument with more of the flow behind
it — its first use is a `merge` a `land` reaches only once the pull request is open.

The conformance corpus already assumes the input exists, which is the strongest evidence that the
omission is an oversight rather than a decision. `conformance/vcsx/vectors/policy-validation.json`
feeds its validation vectors a `consumer_capabilities` field — the vector for
`same_trigger_at_different_from_contexts_is_valid` supplies `["set_state"]` — so the corpus models a
value the invocation contract never defines and no engine can be handed. A runner executing that
vector against a real engine has to invent the channel the vector assumes.

Section 6.11 is careful about the third input for precisely this reason, and the care is what makes
the omission legible as an omission rather than a choice: it explains that the consumer's selection
"is an input rather than something the engine holds because the consumer supplies it with the
invocation", and traces the ordering that guarantees the engine holds it in time. The fourth and
fifth get no such sentence, and Section 8.6's ordering does not mention them, so there is no point in
the sequence at which an engine is stated to hold them.

## The shape of the repair

Two consumer-supplied values, on the same footing as the backend selection and the access parameters:
declared by the consumer, readable from the consumer configuration, and judged before the policy runs.

**`effectable_actions`** — which of the consumer-effected actions (`create_task`, `set_state`,
`notify`) this consumer can perform. Default empty.

**`bound_units`** — the repository unit names the consumer bound, which is what a `[messages.pr]`
`body_source = "template"` and a `[messages.squash]` `transform` are checked against. Default empty.

Both default empty because that is the fail-closed direction, and the direction Section 5.2 already
argues for the one action it treats as fatal: a `set_state` binding "is a configuration error [...]
because a workflow state that never advances strands the flow rather than merely losing information".
A default of "the consumer can do everything" would validate that policy and then strand the flow,
which is the outcome the reason exists to prevent. This is the posture `policy_branch` already takes
— REQUIRED with no default, because every available default was worse than asking.

The asymmetry between the three actions survives unchanged. `set_state` outside the set is
`set_state_unbound` and the policy is refused. `create_task` and `notify` outside it are valid: the
engine emits the intent and reports it, which is what Section 5.2 requires and what makes "a policy
that degrades against a lesser consumer degrades visibly" true.

## A second thing the static set fixes, checked rather than assumed

`outputs.unperformed_intents` reports "the consumer-effected intents the engine emitted and no
consumer performed" (Section 8.2). Read without a declared action set, that field needs the engine to
learn at runtime whether the consumer performed each intent — which an in-process consumer can return
and a subprocess invocation cannot, the process having exited with the envelope that would carry the
question.

With the set declared up front the field becomes computable from what the engine already holds: an
intent naming an action outside `effectable_actions` was not performed, by construction. So the
argument for carrying these as arguments is not only that validation needs them; the envelope key
that reports the same fact at runtime needs them too, and needs them in the one form that works under
both encodings.

## Options considered

**Drop the three reasons and defer all of it to first use.** The honest alternative: if the engine
cannot know, stop claiming it can. Steelmanned — it is a strictly smaller contract, it removes three
tokens from the major-stable surface rather than adding two arguments to it, and Section 9.3 already
has a first-use disposition for exactly this shape ("refused before the policy runs where the
invocation determines it, reported at first use where only the run does"). It loses on the cost
Section 6.11 quantifies and this decision quotes above: first use of a template is after a push, and
first use of a transform is after a pull request is open. Deferring is not a smaller contract, it is
a contract that publishes a branch before reporting a defect the document could have shown.

**Derive the action set from the entry point or the front-end.** An interactive `ship` could be
taken to mean "no task model, no tracker, no channel", and an embedded driver to mean all three.
Steelmanned: it adds no argument at all, and it tracks the real correlation — Section 7.3's task
model is the driver's, and Section 1.3's human at a prompt has none of the three. It loses because
the correlation is not an entailment. A driver with no notification channel and an interactive
front-end wired to a tracker are both ordinary, and an engine that inferred either would refuse a
valid policy or admit a stranding one, with no argument the consumer could make to correct it. It
also reintroduces front-end divergence into the executor, which Section 5.5 keeps to `escalate`
alone.

## Reconsideration trigger

Reconsider `bound_units` if the set of consumer-bound repository units stops being two. It is a bare
name set because the only questions asked of it are "was this name bound" — twice. A third unit kind
that needs the engine to know something *about* a unit rather than that it exists would make the flat
set the wrong shape, and the argument for a keyed structure would be worth re-reading then rather
than pre-empting now.

## Relationship to other decisions

It completes the input list 0086–0090 fixed when validation was made total, by supplying carriers for
the two inputs that list named without locating. It takes the Core/consumer split as given.
