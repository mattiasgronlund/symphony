# Background — 0081 A hook bound is a bound on a unit, not on the flow

## Context

Resolves issue #35, and resolves the corrected report rather than the filed one.

As filed, the report claimed that `grep -c timeout` over `VCSX-SPEC.md` is `0` and concluded that
"the concept does not appear in the document at all". The reporter withdrew that claim before this
decision was taken. The *word* does not appear; the **concept does**, in Section 5.6's closing
paragraph:

> An engine MAY impose further bounds on a running flow, a wall-clock deadline for example. A flow
> stopped by any bound the engine imposes reaches the same result, so the envelope does not reveal
> which one fired, and the engine MUST document each bound it imposes (Section 13.3).

So an engine may already bound a hook by wall clock and must publish that it does. What survives the
correction is narrower and sharper than what was filed, and it is two things.

**1. It is a `MAY`.** An engine that never imposes a bound conforms, so a repository hook that never
returns wedges a conforming engine indefinitely. Section 6.6 hands control to a program the engine
did not write and says nothing about getting it back. That is issue 4's argument one layer down, and
Section 5.6 has already accepted it for the flow: an optional bound leaves "the engine hangs"
conforming, and a hook is where hanging is most likely, because it is the one place the executor
waits on a program nobody in this specification wrote.

**2. `flow_exhausted` is the wrong diagnosis, and Section 5.6 forces it.** "A flow stopped by any
bound the engine imposes reaches the same result" routes a bounded hook to `needs_caller` carrying
`flow_exhausted`. But Section 5.6's own bound counts `run_op` dispatches, and Section 8.4 defines
`flow_exhausted` as the hold "the executor imposed, which is a condition to investigate rather than
an outcome the policy chose" — written for a policy graph that does not converge. A hook that never
returns is not a non-converging graph. It is one named unit, at one named position, that stopped
answering, and a caller can act on exactly that: the flow reached `before:commit`, `scan-content`
did not answer within its bound, fix that hook. Collapsing it into `flow_exhausted` discards both
facts, and Section 8.2 nulls `op`, `reason` and `class` for a flow the executor stopped, so the
envelope names neither the position nor the unit.

The reporting engine had already departed from the "same result" sentence, reporting a bounded gate
on its own fault channel because the two conditions are not the same thing — a departure it would
rather have settled here than defended locally.

## The distinction this decision draws

Section 5.6's further bounds are bounds on **a running flow**. They stop the executor, the pending
`run_op` is not dispatched, and the invocation ends. A hook bound is not one of those. It bounds
**one unit at one position**, inside one dispatch. The flow is not stopped: the gated operation
reports, and its result re-enters the machine like any other result, which is what the machine is
for.

That is why the answer is an operation reason rather than a `need`. It is also why Section 5.6's
"same result" sentence needs scoping rather than contradicting — it is right about bounds on the
flow and was never about a bound on a unit within one dispatch.

## One token, not three

Issue #38 reports a neighbouring set of conditions that reach no result at all, among them a
repository unit that will not run or that does not answer in the shape the engine fixed
(Section 6.6 makes that form `Implementation-defined`). The obvious disposition — read it as a hook
that blocked with an `error` result, so Section 6.6's existing rule surfaces `<op>:failed` — was
offered and is refused here, on this decision's own argument:

**A block is something the hook did.** A hook that never started, or whose answer the engine could
not read, decided nothing; the engine did. If a bounded gate earns a token because a broken gate and
a refusing gate need different repairs, the same holds for a gate that could not run and for one
whose answer could not be read. Spelling them as blocks puts a gate that ran and said no and a gate
that is broken on one token, and a repository routing `commit:failed → park` cannot tell them apart.

So the registry gains **one** `(any gated)` reason across both issues rather than one each:
`hook_unanswered`, class `error`, meaning the hook did not give the engine a usable answer — the
bound elapsed, the unit could not be started, or the answer could not be read. `<op>:failed` keeps
its meaning: a gate that answered and said no with an `error` result. Which of the three occurred is
diagnosis, and belongs in `outputs` rather than in a token, because the repair is the same shape in
each case and the routing decision is not refined by knowing which.

One condition splits off cleanly and does not belong to this token at all. A hook declared in
`[hooks]` with **no `run` unit** is judgeable from the document, so it is a Section 6.10
configuration error rather than a runtime result — the table declares the hook and gives it nothing
to run, which is the same shape as the row already there for an edge whose action cannot be
dispatched from the arguments it carries. It takes `malformed_policy` and mints no token: Section
6.10 states that `malformed_policy` covers a well-formedness failure no other condition in the table
names, and this is one. Whether the named unit *exists* is a property of the worktree rather than of
the document, so that stays runtime and is `hook_unanswered`.

## Why `error` and not `needs_caller`

Section 4.2 defines `needs_caller` as "the operation cannot proceed without a decision or action
from the caller". A hook that did not answer needs a repair, not a decision. Section 5.5
additionally invites a front-end to bind a resolver by the `need` token and resume the flow, which
on this condition resumes into the same hang.

## Options considered

- **A — a unit bound, with a reason of its own (chosen).** Bounding becomes REQUIRED in Section 6.6;
  the value is `Implementation-defined`, MUST be documented (Section 13.3), and MUST admit a
  configured value of at least 600 seconds; a gate that exceeds it reports `<op>:hook_unanswered`
  and the result re-enters the machine; an `after` hook that exceeds it is killed and the flow
  continues unchanged, with the fact reported in `outputs`; Section 5.6's "same result" sentence is
  scoped to bounds on a running flow.
- **B — reuse `<op>:failed`.** The same MUST, with the exceeded bound spelled as an `error`-class
  block so Section 6.6's existing rule carries it. Zero new tokens, and it escapes `flow_exhausted`
  just as A does. Rejected on the conflation above: Section 6.6 preserves only the *class* of a
  block, so the hook's own reason never reaches the envelope and a broken gate is indistinguishable
  from a refusing one. Symphony's own `SPEC.md` Section 9.4 folds "failure or timeout" into one
  condition deliberately, which is what makes B defensible rather than merely cheap — but Symphony's
  hooks are not routed through a policy machine that can branch on the difference.
- **C — keep Section 5.6's uniformity and mint a `need`.** A bounded hook still ends the invocation
  and carries a `need` of its own beside `flow_exhausted`. Rejected: it is a hold rather than a
  request (Section 8.4), so nothing routes it and a repository that wants "if the gate does not
  answer, park" cannot write that edge; Section 8.4 nulls `op` at a position whose operation has not
  run, so the position is not named portably without amending Section 8.4 too; and it treats a bound
  on one unit as a bound on the flow, which is the conflation this decision exists to undo.
- **D — a repository budget under an operator ceiling.** A plus an OPTIONAL `[hooks.<name>]
  timeout_ms` the engine clamps to the consumer's ceiling, so a worktree-sourced value can only ever
  *lower* the bound and Section 3.2's unanswerable sourcing question stops mattering. Not rejected
  on its merits — it is the right answer if one consumer-owned number proves wrong for the real
  spread, which is plausible, since a `notify-release` hook is a web request and a `before:commit`
  gate can be a repository's whole test suite. Deferred because it spends two numbers and a
  Statement row before anything has demonstrated one is insufficient, and because Section 6.1's
  forward-compatibility rule makes it addable in a `MINOR` without breaking a policy written today.
- **E — leave bounding a `MAY`.** Rejected on the reporter's own point 1 and on issue 4's argument,
  which Section 5.6 has already accepted for the flow.

## Decision and reasoning

**A.** Bounding becomes REQUIRED, the bound is the consumer's, and an unanswered hook is the gated
operation's own reason.

**The bound is the consumer's, and `[hooks]` gains no key.** The in-sandbox half of `[hooks]` is
worktree-sourced by design — Symphony's `SPEC.md` Section 15.4 places it there deliberately, because
running a pull request's own gate change against that pull request is correct — so a bound written
there is a bound the bounded thing sets: a hook that hangs and a hook that raised its own ceiling to
a day are the same hook. Section 3.2 denies the engine the one fact that would let it admit the key
host-side and refuse it in-sandbox, because it labels contexts and does not itself enforce the
sourcing rule, so it never learns which revision a value came from. A `timeout_ms` a repository
writes anyway is ignored under Section 6.1. It arrives the way Section 11 has the credential arrive:
the repository owns which unit runs, the operator owns how long their machine will wait for it.

**The floor.** The value is `Implementation-defined` and MUST admit a configured value of at least
600 seconds. The exact number is arbitrary in the way Section 5.6 already says its 64 is — what is
not arbitrary is that a floor is fixed, because it is what keeps two engines in agreement on every
hook that answers within it. Six hundred seconds is chosen so a repository whose `before:commit`
gate is its test suite runs the same on two engines; an engine free to bound at one second would
make that policy engine-specific.

**The honest limit, stated rather than glossed.** Killing a child does not kill what the child
started, so a hook that answers and leaves a grandchild holding the pipes is read from until the
bound elapses. The invocation is bounded; the machine is not. That belongs in the document, because
an operator who reads "the engine bounds a hook" and finds a process alive afterwards should find
the limit written down rather than discover it.

**Cost, priced.** One operation reason, permanent within a `MAJOR` — but Section 8.5 admits a new
reason in a `MINOR` and the `#class` fallback absorbs it, so no consumer changes to receive it. One
new REQUIRED behaviour for every engine, which is the point rather than the cost. And a repository
gains what B cannot give it: `commit:hook_unanswered` is a trigger, so "if the gate does not answer,
park" is an edge somebody can write.

## Review findings applied (PR #40)

Two findings against the follow-through, both the same defect and both this decision's own stated
failure mode recurring one clause over. The chosen option is unchanged; what changed is that the
disposition now covers the conditions the reason already did.

**The `after` half covered one condition where the gate half covered three.** As first written,
Section 6.6's `before:*` bullet folded three conditions into `hook_unanswered` — the bound elapsed,
the unit could not be started, its answer could not be read — while the `after` bullet spoke only of
the bound elapsing, and Section 8.2 scoped `unfinished_hooks` to the hooks "stopped at its hook
bound". So a result-triggered hook the engine could not start was neither: `hook_unanswered` is
`(any gated)`, and nothing had stopped it at a bound. It was silently dropped — which is what
Section 5.4 forbids and what that bullet cites as its own reason for reporting the bound case.

Both are widened to "gave the engine no usable answer", so the division stays where this decision put
it — by whether anything waits on the answer — rather than drifting to which condition occurred.
`unfinished_hooks` is now the non-gating half's mirror of `hook_unanswered`, and both carry which of
the three conditions occurred in `outputs`, since the reason routes and the condition diagnoses.

That the gap survived the drafting is itself worth recording: the decision reasoned carefully about
the gate half, where the token is, and treated the `after` half as the easy case. The easy case is
where the no-silent-drops principle had nothing enforcing it.

**A pre-existing count corrected in passing.** `conformance/vcsx/README.md` claimed Section 4.3's
table yields its entries from 33 rows; the base was already wrong at 34, and this decision's
recount fixed the entry total while carrying the row error forward. It is 35 rows, 56 entries.

## Reconsideration trigger

Reconsider if one consumer-owned number proves wrong for the real spread of hooks — option D returns
as an OPTIONAL `[hooks]` key clamped to the consumer's ceiling, addable in a `MINOR` under Section
6.1. Reconsider separately if the `outputs` report of a killed `after` hook proves to have no
consumer, which would mean the no-silent-drops principle was applied where nothing was listening.

Relates to 0084 (which reports the neighbouring conditions and takes this decision's token rather
than minting its own), 0060 (which introduced the flow bound and whose shape this copies), 0057
(which defined the universal reasons this one joins), 0056 (the configuration-reason registry) and
0066 (which gave the well-formedness conditions their reason).
