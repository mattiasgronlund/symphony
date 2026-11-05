# Background — 0180 `add_comment` is not idempotent, and the key a caller keeps has a recovery class

## Context

Reported from `symphony-rs` as issue #176, against `86a2188`, found while reconciling that
repository's Stage D6 and tracked there as decision 0011 R101.

Section 11.8 gives `set_state` an explicit rule: "Idempotent: if the issue is already in
`target_state`, `set_state` is a successful no-op." `add_comment` has no counterpart anywhere in
Sections 11.1, 11.5 or 11.7. Repeats are ordinary: Section 8.4 re-dispatches a failed attempt and
Section 16.6 runs the same turn sequence again, so an agent that commented before a failure
comments again after it. The specification limits a repeat in exactly one place, Section 9.7's
refusal comment, "written once per (issue, target) rather than once per evaluation", and does it
with a rule of its own.

## The mechanism

**`set_state` is idempotent because its target is an identity, and a comment has none.** "Already in
`target_state`" is something an adapter can read back and compare. A comment's body is not an
identity. Section 11.5 makes the agent its author, so two identical bodies are two statements, and
an adapter that merged them would be editing what the agent said. Any de-duplication key has to come
from the caller, because only the caller knows whether two calls mean the same thing. Neither Linear
nor Forgejo exposes a client-supplied comment key, and `symphony-rs` checked both.

**The case worth a MUST is the adapter's own resend, not the agent's.** The re-dispatch repeat is
the agent commenting twice, and that is correct once the text says the operation is not idempotent.
The harmful repeat is the one nobody asked for. A comment write that times out has an unknown
outcome: the tracker may have stored it. An adapter that re-sends on its own initiative and reports
one result has posted two comments for one call, and its caller has no way to know.
`symphony-rs` checked that neither of its adapters retries a POST (`ureq` 3.4.0 has no retry path,
and neither tracker crate loops).

**The same mistake can happen one layer up, and it did.** `symphony-rs`'s daemon turned *every*
`add_comment` error into an undelivered effect, which dropped the Section 9.7 key, so a timeout whose
comment had in fact landed was posted again on the next tick. The adapter's rule alone doesn't stop
that. A caller that keeps a key for at-most-once has to treat an unknown outcome as possibly
delivered, or the adapter's ban on resending comes back as a resend from the caller.

**"Couldn't determine" has to be defined, or the MUST has no edge.** It covers any failure after the
request may have reached the tracker: a transport timeout, or a connection lost after the request
was sent. It does not cover a failure the tracker answered with a definite refusal, such as a
non-2xx status, because that response is itself a determined outcome. `symphony-rs` asked for this
on the thread, so that a timeout clearly falls under it.

**The key Section 9.7 keeps has no recovery class.** The (issue, target) record is state that Core
behavior asks an implementation to hold wherever it comments. Section 4.1.8 doesn't list it, and
Section 14.3's note naming "the cases this document creates today" omits it, so nothing says
whether it survives a restart. It can't be `Reconstructable`, because no Section 11.1 read returns
comments. As `Ephemeral`, a restart posts the refusal comment once more, which is bounded and
acceptable if documented. As `Durable`, it has to be persisted. Those give different meanings to
"at most once", so the classification has to be stated somewhere. `symphony-rs` holds it as
`Ephemeral`.

## Options considered

- **Not idempotent; the adapter doesn't resend an unknown outcome; a caller keeps its own key and
  keeps it through an unknown outcome; the Section 9.7 key gets a class** (chosen). This matches
  what both trackers support and makes the one limited case in the spec the model for the rest.
- **An idempotency key on `add_comment`** (the report's second arm). It would make at-most-once a
  property of the operation instead of each caller's job, which is the stronger guarantee. It loses
  because no tracker in the corpus can carry it. An adapter would have to keep the key itself, in a
  store that Section 14.3 would then have to classify, and on Linear or Forgejo it would also need a
  read of the issue's comments to check against. That read doesn't exist, so the key would protect
  only within one process lifetime, which is exactly what a caller's own `Ephemeral` key already
  does.
- **Leave it to the reader.** Arguably, without a stated rule, nothing is promised. It loses because
  an implementation, `symphony-rs`, got the caller-side half wrong, and nothing in the text would
  have told it.

## Decision and reasoning

The rule goes in Section 11.8's neighbourhood, after `set_state`'s rules, so the two writes' repeat
semantics read side by side. Section 11.8 is titled for state transitions, so the rule is a short
paragraph after the `set_state` bullets rather than a bullet among them, and the section keeps its
title.

The Section 9.7 record joins Section 14.3's note on unlisted Core state, with its class left to the
implementation (`Ephemeral` or `Durable`) and documented. That adds a row to
`CONFORMANCE-STATEMENT-TEMPLATE.md`'s state table, as CLAUDE.md requires for a MUST-document
obligation.

**Reconsideration trigger:** a tracker in the corpus that accepts a client-supplied comment key, or
a comment read added to Section 11.1. Either would make an operation-level key implementable with
more than per-process protection, and the second arm would be worth weighing again.
