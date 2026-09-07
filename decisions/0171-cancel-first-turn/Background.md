# Background — 0171 A parameter that never named the turn

## Context

Reported from `symphony-rs` as issue #147, against `5a4fdf7`, found while building that repository's
roadmap D5a.

Section 10.7 (Agent Runner Contract) defines `cancel(continuation_ref)` and, three lines above,
fixes what the first turn passes:

> The first turn passes `continuation_ref = null` and the full task prompt

So a cancel issued against an in-flight **first** turn has no value to name it by, and Section 10.7
does not say what is passed. Section 10.6's note routes every early stop — "timeout, stall, or
operator/budget interruption" — through `cancel`, with no exemption, and the first turn carries the
full task prompt rather than continuation guidance, so it is the turn most likely to reach
`turn_timeout_ms` in the first place.

## The mechanism

**The parameter never identified the turn, on any path.** This is the report's own observation, made
in passing, and it is what decides the shape of the answer rather than merely motivating one. The
report describes its implementation as passing, for a later turn, "the continuation the running turn
was **started from**". That is exactly right, and it generalizes: `continuation_ref` names where a
turn resumes *from*, not which turn is running. Even where a value exists, `cancel(continuation_ref)`
names the cancelled turn's **input**, not the cancelled turn.

So this is not a first-turn defect with a first-turn repair. The first turn is where the absence
becomes visible, because it is the one turn whose input has no name.

**The single-in-flight invariant is not something the specification would be adding.** The report
offers it as an assumption a reader must supply, and it is already load-bearing. Section 16.6's
`run_agent_attempt`:

```text
  while true:
    prompt = build_turn_prompt(...)
    turn_result = agent.run_turn(..., continuation_ref=continuation_ref, ...)
    if turn_result failed: ...
    continuation_ref = turn_result.continuation_ref
```

`run_turn` is called, awaited, and its result assigned before the loop can come round: strictly
sequential, one turn per Agent Runner instance at a time. Section 10.7's own behavior outline has
the same shape — `run_turn`, then `cancel` an in-flight turn, then `release` at run end — and
`release` frees resources "when the worker run is ending", singular. Stating the invariant documents
what the reference algorithm already depends on; it constrains no adapter that was previously
conforming.

**Section 10.7's `cancel` carries a second clause no adapter can build, and it is in the same
sentence.** The bullet says the adapter SHOULD "interrupt the turn, drain … and **yield** a
resumable `continuation_ref`", which reads as a return value from `cancel`. `symphony-rs` supplied
the mechanical reason it cannot be one, and it is not a matter of their convenience:

> Resumability is not known at cancel time. It is the *result of the drain* … Whether the drain
> comes back cleanly is determined after `cancel` has returned, by the in-flight `run_turn` call. A
> `cancel` that returned a `continuation_ref` would have to either block until the drain finished —
> turning a cancel into a second turn-length wait — or promise a resumability it cannot yet know.

Their Codex adapter's two timeout paths produce different resumability — a plain `turn_timeout` with
no prior `cancel` goes straight to `kill()`, a cancel-initiated stop sends `turn/cancel` and has its
own secondary timeout — and both report it through the `run_turn` return, "because that is the only
call still alive when the answer exists".

Section 10.6 already places the yield there:

> A `turn_timeout` reached without a clean interrupt-then-drain leaves the underlying turn still
> running, so the session is not safely resumable and **the turn fails**; an adapter that can drain
> cleanly MAY instead yield a resumable `continuation_ref`.

The two sections disagree about which call answers, and Section 10.6 is the buildable one.

**A third site has the identical defect and is demonstrated by the reference algorithm itself.**
Found while confirming the report; in neither the report nor the response. `release(continuation_ref)`
takes the same parameter, and Section 16.6 passes it null:

```
$ awk '/^### 16\.6 /,/^### 16\.7 /' SPEC.md | grep -n 'release(continuation_ref)\|continuation_ref = null'
58:  continuation_ref = null  # first turn establishes the session lazily (Section 10.7)
66:      agent.release(continuation_ref)
```

Line 66 is the first turn's prompt-failure path, where the loop has not yet assigned a
`continuation_ref` and the value is still the `null` line 58 set. So the specification's own
algorithm calls `release` with the absent value that Section 10.7's signature does not admit. Fixing
`cancel` alone would leave the same contradiction one bullet down, in the one place the document
already exhibits it.

## Options considered

- **Option A — the parameter is OPTIONAL on both `cancel` and `release`, the single-in-flight
  invariant is stated, and the resumable-`continuation_ref` yield moves to the turn's own outcome**
  where Section 10.6 already puts it.

  Trade-offs: three changes to one bullet's neighbourhood rather than one, and it leaves a parameter
  that is not an identity — a reader can still mistake it for one, which is why the bullet has to
  say what it *is* for.

- **Option B — drop the parameter** (the report's reading 2): the adapter identifies its own
  in-flight turn.

  Trade-offs: it is the honest response to "the parameter never named the turn", and it removes a
  field that misleads by looking like a handle. It loses on what the parameter is actually good for:
  it carries the continuation the cancelled turn was started from, which is the state an adapter
  that *can* drain cleanly needs in order to yield a resumable turn. Dropping it removes that on
  every path, to repair a first turn where a clean drain is the least likely outcome anyway.

- **Option C — state the single-in-flight invariant and leave `cancel(null)` implicit** (the
  report's reading 3 alone).

  Trade-offs: the smallest edit, and the invariant genuinely does make a null unambiguous, so
  nothing is left undecidable. It loses because the signature would still require a value that
  Section 10.7's own text says the first turn does not have — a contradiction a reader has to
  resolve by inference — and because it does nothing about the unbuildable yield, which is the
  defect an implementer actually trips over.

## Decision and reasoning

**Option A**, with the invariant from Option C folded in, which is what makes the optional parameter
unambiguous rather than merely permitted.

**Why the parameter stays even though it is not an identity.** Because it is not there to identify
anything. It carries the cancelled turn's input so that an adapter capable of a clean drain has the
state it needs to produce a resumable continuation. On a first turn there is none, and the cancelled
turn is therefore resumable only if the adapter can mint one — which is a real difference in what a
first-turn cancel can achieve, and one the contract should say rather than leave an implementer to
discover. Option B would erase that difference by erasing the state it turns on.

**Why the yield moves rather than being deleted.** The behaviour it describes is real and is what an
adapter should attempt; what is wrong is only which call reports it. Section 10.6 already assigns
the outcome to the turn, so moving it makes the two sections agree rather than adding a rule.

**On `release`.** Included because the reference algorithm exhibits the defect at that call site, so
the document already contradicts itself there in a way a reader can see. Repairing `cancel` alone
would have left Section 16.6 calling an operation with a value its own contract does not admit.

## Reconsideration trigger

Reopen if an adapter is built whose protocol holds more than one turn in flight against a single
session — parallel turns, or a speculative turn issued while another is draining. The absent
parameter is unambiguous only under the single-in-flight invariant, and such an adapter would need
an explicit turn handle rather than a nullable continuation. The evidence would be a capability
descriptor (Section 10.9) that has to declare turn concurrency.

A second trigger: an adapter whose cancel is itself terminal, so that resumability is known when
`cancel` returns and no drain is outstanding. Section 10.7's original placement was right for that
shape, and the question would become whether the contract should permit both answers rather than fix
one — which it should not do lightly, since two places to look for one outcome is what this decision
is removing.
