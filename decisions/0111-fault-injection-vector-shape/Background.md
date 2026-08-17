# Background — 0111 The corpus states the assertion; the harness holds the fixture

## Context

Issue #59's second half asks for fault-injection conformance vectors covering 429, 5xx, timeout,
ETag-304 and schema drift, asserting the outcomes the sibling proposals define, and notes that
`head_moved` is already covered so the same discipline should extend "to the rate-limit / timeout /
drift axis". The cross-cutting item in the same study adds a concurrency-stress tier alongside it.

The observation driving both is the sharpest one in the study: **the failures that bit us are
exactly the ones with no test.** Ninety-nine vectors green, and not one of them in the transient
family.

## Why this cannot be an ordinary vector

Every vector in `conformance/vcsx/vectors/` today states a **pure function**: `exit_code_for_status`
maps a status to a code, `match_edge` maps a trigger and a policy to an edge, `resolve_base` maps
sources to a base. Each is checkable by reading a JSON file and comparing two values, which is what
makes the corpus language-neutral and what lets an engine in any language run it.

A fault-injection case is not that. To assert that a 429 yields `rate_limited` rather than `failed`,
something has to *be* a forge and *return* a 429 at a chosen moment. That is a harness — a
`ForgeTwin` standing in for a code host — and a harness is a program, not data. It lives with an
implementation, in the implementation's language, and this repository holds no such thing and should
not: the corpus derives from a specification and is consumed by every implementation, and a harness
written here would be written in one language for one of them.

So the choice is not whether fault-injection cases belong in the corpus but which half of them does.

## The split: the assertion is specified, the fixture is not

What this repository can state, and is the only place that can state it authoritatively, is **what a
conforming engine must produce** for an injected condition — the reason token, its proto class, the
need and its `retryable` value, and the envelope keys that must be present. Those are all read from
`VCSX-SPEC.md`, which is the rule the corpus already follows: every value is read from the sections
its `spec_refs` cite, and nothing is invented.

What it cannot state is the fixture: the bytes a particular forge returns for a rate-limited
request, which header carries the reset, what a drifted payload looks like after a specific upstream
release. Those are properties of a forge and of the backend talking to it, and they differ per
plugin — a GitHub twin and a Forgejo twin inject the same *condition* through entirely different
responses.

So this decision fixes the **vector shape** and the assertion set here, and leaves the cases to the
implementation that owns a harness. An implementation authors its own fixtures and asserts against
the schema this repository publishes, which keeps the checkable claim in the specification's gift
and the machinery in the implementation's.

## Why not author the data here anyway

The alternative — write the vectors here in full, harness obligation and all — was considered and
loses on a property the corpus currently has and would give up.

Every file in `conformance/vcsx/vectors/` today is runnable by anything that can read JSON. A
fault-injection file would be the first that is not: it would describe a scenario no reader in this
repository can execute, and its presence would make "the corpus is green" mean two different things
depending on which files a runner supports. That is the same hazard decision 0105 found in a vector
that had degraded into a tautology — a corpus whose green is conditional on something the corpus
does not state.

The honest form of the alternative is that a specification repository should be able to demand a
test, not merely describe one. That is real, and it is met here by the Section 13.1 checks the
sibling decisions added: the demand is normative in the specification, and the corpus carries the
schema an implementation's answer must fit. What is not claimed is that this repository verifies it.

## What the shape has to carry

Reading the sibling decisions, an injected condition must be assertable against five things, and the
schema names all five so an implementation cannot satisfy it partially:

- the **reason** the operation reports, and its **proto class** — the difference between
  `rate_limited` and `failed` being the difference between a run that escalates and a run that ends;
- the **need** and its **`retryable`** value, which is what a governing consumer branches on;
- the **`outputs` keys** that must be present — `forge_budget` on any forge-touching call,
  `forge_unavailable_condition` where the reason is that one, `pr_state_unchanged` on a satisfied
  conditional read;
- for a drift case, that the answer is **undetermined** and distinguishable from the legitimate
  absent case, which is the whole of the sibling parse decision;
- and that the operation **did not act** — no second pull request, no push over a closed one, no
  merge on an unread head.

The last is the one most easily omitted, because the first four are all readable off an envelope
while this one is a statement about the forge's state afterwards. A vector asserting only the
envelope would pass for an engine that reported `create_pr:failed` and created a pull request
anyway.

## Reconsideration trigger

Reconsider if two implementations produce fault-injection suites that disagree about what the same
injected condition should yield. That would mean the schema underspecifies the assertion and the
data has to come back here — at which point the language-neutrality cost above is worth paying,
because a corpus nobody can run beats two corpora that disagree.

Reconsider also if the concurrency-stress tier the cross-cutting item asks for turns out to need a
shape of its own rather than fitting this one. That tier asserts over N concurrent sessions rather
than over one injected response, and this schema does not attempt to cover it; it is deferred to the
Symphony-side work where the concurrency it stresses lives.

## Relationship to the other decisions

It is the checkable form of 0106's `304`, 0107's snapshot, 0108's transient reasons, 0109's bound
and 0110's drift rule. Without it each of those is a requirement stated in prose with a Section 13.1
check and no published shape for the answer.
