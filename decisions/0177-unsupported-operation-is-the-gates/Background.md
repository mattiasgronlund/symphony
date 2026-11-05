# Background — 0177 `tracker_unsupported_operation` is the gate's, not a transport mapping

## Context

Reported from `symphony-rs` as issue #173, against `86a2188`, as the residual of decision 0162. It is
tracked there as decision 0011 R102. The report started from an earlier reading of Section 11.4,
under which a REST adapter owed `tracker_backend_errors`. Decision 0162 already answered that, and
the issue says so first: it scoped each REQUIRED spelling to "where the condition each names occurs"
and moved the transport categories to RECOMMENDED.

What remained is one sentence. Section 11.4 opens:

> Error categories are transport-neutral: each adapter maps its transport's failures onto them.

`tracker_unsupported_operation` is one of the four REQUIRED spellings, and its condition is "write
not in the adapter capability descriptor, Section 11.7". That condition is not a transport failure.

## The mechanism

The condition is a lookup in a static document, and the lookup happens before any adapter call.
Section 11.7: "The orchestrator reads the descriptor before invoking a write and MUST NOT invoke an
undeclared write … An undeclared write invoked anyway returns `tracker_unsupported_operation`." In
`symphony-rs` no adapter produces the token. The broker's descriptor gate does, before an adapter
is invoked (that repository's decisions 0115 and 0116).

So the opening sentence describes a party that, in a correct implementation, never sees the
condition. The REQUIRED bullet is already right, because 0162 put the obligation on "an
implementation" rather than on the adapter. Only the framing sentence over-reaches. Section 11.4
already has the shape for a token reported before any adapter is invoked: the note that
`unsupported_tracker_kind` and its siblings are preflight's reason tokens, "so no adapter maps a
transport failure onto it".

The sentence matters because the token makes one guarantee observable. Section 17.3 checks that an
undeclared write "surfaces `tracker_unsupported_operation` and is never silently no-oped". That
check is only meaningful while the token means "the gate refused this" and nothing else.

## Options considered

- **One sentence stating that the gate reports it** (chosen). The opening sentence is scoped to the
  transport categories, and a sentence beside the preflight note says that
  `tracker_unsupported_operation` is reported by the gate Section 11.7 places before a write, not
  mapped from a transport.
- **The adapter MAY also report it for a declared write that the backend refused as unsupported.**
  The report offered this as an alternative, with a plan-tier change at runtime as the example.
  Its strength is that it would give a runtime capability loss a precise name instead of a generic
  status failure. It loses because Section 11.7 rules out the premise: "The descriptor MAY depend
  on resolved config and is fixed for the run … determined once at adapter initialization." A
  declared write is in the descriptor by definition, so a backend refusing it is not "write not in
  the adapter capability descriptor". It is a backend failure, and the RECOMMENDED categories
  already name it: `tracker_api_status`, or `tracker_backend_errors` for a GraphQL tracker. Letting
  the token cover both cases would make Section 17.3's check unable to tell a gate that worked from
  a backend that changed. `symphony-rs` withdrew this arm on the thread for the same reason.
- **Leave it.** The REQUIRED bullet already binds the implementation, so a careful reader gets it
  right. It loses because the issue exists: a second adapter's author read the opening sentence as
  an assignment.

## Decision and reasoning

The sentence names **the gate**, not the broker or the orchestrator. Section 11.7 says the
orchestrator reads the descriptor, and Section 11.5 puts writes in the executor's broker. Which
component holds the gate depends on the topology, and the guarantee doesn't depend on which
component it is.

No change to the REQUIRED list, to Section 11.7, to Section 17.3, or to any template. The decision
adds no `Implementation-defined` value and no MUST-document obligation.

**Reconsideration trigger:** a descriptor that is no longer fixed for the run. If Section 11.7 ever
lets a capability be withdrawn mid-run, the gate and the backend could both observe "not
supported", and the second arm becomes the question again.
