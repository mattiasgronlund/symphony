# Background — 0137 A backoff kept per repository, and the state model with no repository in it

## Context

Issue #96 was filed by the `symphony-rs` build alongside #95 and against the same unbuilt phase.
Section 14.2 requires that where an engine policy could not be used at all, "retry is **backed off
per repository** rather than attempted every tick". Section 4.1.8's Orchestrator Runtime State has
eight fields and not one of them is keyed by repository. Section 14.3 then says:

> Every field of the Orchestrator Runtime State (Section 4.1.8) — and any state introduced by an
> OPTIONAL extension — MUST be assigned exactly one recovery class…

The enumeration is exhaustive over the wrong set. It closes over extensions and leaves Core's own
additions outside it.

### The failure path

An implementation building the behaviour Section 14.2 mandates must hold, per repository, at least a
time before which it will not retry. It has three ways to comply and the document blesses none:

- Hold it in a field Section 4.1.8 does not list. Section 14.3's "every field" then does not reach
  it, and `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 — whose table is exactly Section 4.1.8's
  eight fields plus one `<extension state field>` row — has no line to put it on.
- Hang it off `running` or `claimed`. Both are `Reconstructable`, "rebuilt from tracker state and
  workspaces during reconciliation". A backoff schedule is derivable from neither, so a restart
  silently resumes retrying the failing repository on every tick — the exact load and log volume the
  clause's own reasoning says the backoff exists to prevent.
- Not hold it. That is not complying.

What ships broken is the Conformance Statement rather than the daemon. Section 19 and the template
are the mechanism by which two implementations are comparable, and Section 14.3 exists to make one
question answerable for every piece of runtime state: what does a restart cost. The state whose
answer an operator most needs — does my failing repository come back backed off, or come back
hammering — is the one the Statement has no row for. A generated Statement is complete against its
own table and silently missing this, which is decision 0128's failure mode arriving through the
enumeration rather than through a missed row.

### Three obligations, not one, and the count decides the answer

The drafting for the decision sheet said `repository_provisioning_failures` is "tick-local, holding
nothing". That is wrong, and wrong in the direction that mattered: it understated the case for the
rule. Read against `SPEC.md` at `cbc7d8a`:

- `engine_invocation_failures`, unusable policy: "retry is **backed off per repository** rather than
  attempted every tick" (`SPEC.md:3466`). Core, mandatory, and cross-tick.
- `repository_provisioning_failures`: "Persistent authentication/credential or invalid-store-path
  failures MAY be parked rather than retried indefinitely" (`:3457`). Core, optional, and a park is
  cross-tick by definition.
- `engine_invocation_failures`: "Persistent failures MAY be parked rather than retried indefinitely"
  (`:3484`). A second Core park MAY, in the same class as the mandatory backoff.

So what needs a home is one MUST and two Core MAYs, whose shapes are not the same. There is also a
consumer the issue does not name: Section 14.2 continues "Implementations SHOULD log transitions —
the first failure, each backed-off retry, and recovery — rather than every evaluation" (`:3474`).
"First" and "recovery" are both predicates over the previous tick's per-repository state, so the
state is load-bearing for the logging rule even for an implementation whose backoff schedule happens
to need no counter.

One more reading settles the shape of the repair. `node_provisioning_failures` carries the same park
MAY (`:3491`) and is an OPTIONAL extension, so Section 14.3 already admits its state, classes it and
gets it a template row. The identical construct is blessed on the extension path and homeless on the
Core path. That asymmetry is not a gap in the enumeration's coverage; it is a gap in what the
enumeration thinks Core is allowed to do.

## Options considered

### A field for the mandate and a widened rule for the rest — chosen

Section 4.1.8 gains `repository_backoff`, a map `repository -> { due_at_ms, attempt }`, classed
`Ephemeral`. Section 14.3 gains a clause admitting state that Core behaviour introduces beyond
Section 4.1.8, on the same terms it already sets for an extension's: exactly one recovery class,
documented.

The split follows the obligations. The backoff is a MUST with one shape — a repository, a time, and
enough to advance the schedule — so a field can state it and the template can compare two
implementations on it. The two parks are `Implementation-defined` down to whether they happen at
all, so a mandatory `parked` flag would force a representation for a choice an implementation may
decline, and would be `n/a` in half the Statements that carried it. Those the rule admits and
requires classed, without dictating a container.

### Add the field alone

#96's first offer, and the cheapest thing that answers it. One field, one vocabulary entry, one
template row; Section 14.3's "every field" then reaches the backoff because the backoff is now a
field, and nothing about the enumeration has to change. On this reading the widening is machinery
bought for a problem that adding the field already solved.

It loses on the two parks and on everything after them. A park record is still Core state with no
field, so the day after this lands the same question returns in the form the field cannot answer —
and it returns for state whose recovery behaviour is *more* surprising, not less, since a park that
does not survive a restart quietly un-parks a repository a human decided to stop retrying. Closing
one instance of a class while leaving the class open also leaves the next Core addition to
rediscover the argument; Section 14.1 already learned this and ends "Note: the set is not closed",
which is the shape being asked for here one section over.

### Widen the rule alone

#96's second offer. One clause in Section 14.3, no new field, no vocabulary entry, and every Core
addition — backoff, both parks, and decision 0136's generation counter — is admitted, classed and
documented in one move. It is the smaller diff and the more general fix, and on a document that
prefers stating a rule to enumerating its instances it has a real claim.

It loses on comparability, which is what #96 was actually about. A rule that says "class and
document whatever you hold" makes each Statement internally complete and mutually incomparable: one
implementation reports `repo_backoff_until`, another `policy_retry_state`, a third folds it into a
supervisor it never names, and the reader cannot tell whether they agree. The backoff is not an
implementation's private bookkeeping — it is behaviour Section 14.2 mandates, so the specification
owes it a name the way it owes one to `retry_attempts`. The rule is necessary and it is not
sufficient.

### Revert to retrying every tick and delete the requirement

Not offered on the decision sheet, and recorded because it is the obvious fourth answer: if the
per-repository backoff is the only Core state without a home, remove the backoff and the problem
goes with it.

It loses on its own clause's reasoning, which is still true — "None of the four clears without a
person acting, so retrying each `polling.interval_ms` produces load and log volume against a
condition nothing is changing." It also does not work: the two park MAYs survive the reversion and
are still Core state with nowhere to live, so the reversion pays a behavioural regression and does
not close the gap it was taken for.

## The class, and what a restart costs

`repository_backoff` is `Ephemeral`, matching `retry_attempts` ("timers are not restored; backoff
restarts from the first attempt") for the same reason: the schedule is a function of a failure
history the process no longer has, and re-deriving it would mean re-observing the failures. The
reset consequence is stated plainly rather than left to a reader — a restarted orchestrator retries
every backed-off repository on its next tick, once, and backs off from the first attempt again.

That is a real cost and it is the right one. A `Durable` class would make a restart unable to clear
a backoff that a human has just fixed the cause of, which inverts the failure the class is protecting
against; a `Reconstructable` class would be a lie, since nothing outside the process records it.

## Reconsideration triggers

- **A park that a restart must not clear.** The `Ephemeral` class is defensible for a backoff and
  weaker for a park, because a parked repository is closer to a decision than to a schedule. If an
  implementation reports that restart-clears-park is an operational problem, the answer is to give
  the park its own field and class, not to reclass the backoff around it.
- **A third Core addition arrives and the widened rule is doing all the work.** If the pattern
  becomes "state the rule, never name the field", the enumeration in Section 4.1.8 is decaying into
  a historical list and the split this decision makes should be re-argued rather than extended.
- **The Conformance Statement grows a machine-checked completeness test over Section 5.** Today the
  table is compared by a reader. A generator that could verify every held field appears would make
  the field-versus-rule trade-off measurable rather than argued, and this decision should be re-run
  against that measurement.
- **`repository` stops being the unit.** The clause says "the unit here is the repository". A
  multi-tenant or per-remote scope arriving from Section 9.11's node scheduler would change the
  field's key, and the field is where that change would have to be made visible.

## Review findings

**The widened rule had a twin site the plan did not name.** Section 14.3 is not the only place the
extension-only framing is written down. Section 19 (Conformance Statement) enumerates what a
Statement must contain, and one of its items reads "The recovery class assigned to each Orchestrator
Runtime State field (Section 4.1.8) **and to any state an OPTIONAL extension introduces**"
(`SPEC.md:4850`) — the same clause, in the section that defines what a Statement *is*. Widening
Section 14.3 alone would have left the document stating the narrower obligation in the more
authoritative place, and an implementation reading Section 19 for its checklist would have been
correct to omit exactly the field this decision exists to make visible.

It was found by `scripts/check_plan_anchors.py`'s anchor-reach check, which is the failure mode that
script was written for after decision 0134 shipped one. Adding the step then surfaced a *third* site
on the next run: Section 18.1.1's REQUIRED-for-conformance bullet summarising the published
Statement reads "each Orchestrator Runtime State field's recovery class", narrower than Section 19
even before this decision widens it. So the extension-only framing was written in three places and
the plan's first draft named one. That the second run found the third site is the argument for
re-running the check after repairing it, rather than treating one clean pass as the gate.
