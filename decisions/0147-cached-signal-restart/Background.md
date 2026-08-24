# Background — 0147 What a restart restores, and which class the Core field is

## Context

Issue #105, filed by the `symphony-rs` build while implementing Section 4.1.8's runtime state
against Section 14.3's per-field classification. Two `Daemon Conformance` sentences ask for opposite
things about one Core field.

Section 14.3, the `Cached external signal` bullet:

> - The most recent successfully fetched value (the last-known-good) MUST be carried across both a
>   failed refresh and a process restart.

Section 14.4, first paragraph and third bullet:

> Scheduler state is `Reconstructable` or `Ephemeral` (Section 14.3) and is therefore held in memory:
> it is rebuilt or reset at startup rather than restored from a durable store. Only `Durable` state
> introduced by an OPTIONAL extension is restored across a restart.

> - Any `Durable` state (Section 14.3) configured by an OPTIONAL extension is restored from its store
>   before that extension enforces on it; with no store, the extension degrades as documented.

Section 4.1.8's `provider_rate_limits` is Core and is classed `Cached external signal`, so it is
inside both, and Section 14.3's closing paragraph says the class does not require a store at all:
"Core conformance requires only that every runtime-state field has a documented class; it does not
require any durable store."

Three readings are faithful to the text and observably different — carry it and falsify Section
14.4; drop it and violate Section 14.3's MUST for the one Core field carrying the class; or carry it
only where a store is configured, which makes a Core field's restart behaviour depend on an OPTIONAL
extension's configuration and is what neither section says. After a restart the field is either the
last reading taken or `UNKNOWN`, and Section 14.3 makes the policy on `UNKNOWN` a configured
fail-open/fail-closed choice, so a fail-closed deployment pauses on one reading and proceeds on the
other.

## The rest of the corpus already answers it, three times, the same way

The intended contract is not actually open; it is stated everywhere except in the two sentences that
disagree.

- **Section 16.1** initializes `provider_rate_limits: null` and then: "`restore_cached_and_durable_
  state` overlays class `Cached external signal` and `Durable` fields (Section 14.3) from their
  store when an OPTIONAL extension configures one; otherwise the zero/null defaults above stand."
- **Section 17.4**'s row is conditioned the same way: "If a `Durable` or `Cached external signal`
  extension is implemented, restart restores its state before enforcement …"
- **Section 14.3**'s own closing paragraph says the class belongs to an extension: "… and `Cached
  external signal` is introduced by an OPTIONAL provider-quota extension."

So: **last-known-good survives a restart where a store backs it, and starts `UNKNOWN` where none
does.** Section 14.3's unconditional MUST and Section 14.4's "only `Durable`" are the two outliers,
and Section 4.1.8's Core `C` classification is what puts a Core field inside a rule the class's own
summary says only an extension reaches.

Neither half of the issue's ask is sufficient alone, which is why this is three edits rather than
one:

- Making only Section 14.4 agree leaves Section 14.3's MUST unsatisfiable by a store-free
  implementation — including a quota extension shipped without a store, a case Section 14.3's own
  `Durable` bullet contemplates and Section 8.9 contemplates for `budget.*`.
- Making only Section 14.3 agree leaves Section 14.4's "only `Durable`" false for the with-a-store
  case, which Section 16.1 reaches whether or not `provider_rate_limits` stays Core.

## The three edits

### 1. Reclass `provider_rate_limits`, on the `agent_totals` precedent

The document already has a field that is one class in Core and another under an enforcing extension:

> - `agent_totals` (aggregate tokens + runtime seconds) — `Ephemeral` for observability (resets to
>   zero); becomes `Durable` when a budgeting extension enforces on it …

`provider_rate_limits` has exactly that shape. In Core it is Section 13.5's "Track the latest
rate-limit payload seen in any agent update" — observability, with no `fetched_at`, no bound, no
store and **no Core consumer**: Section 4.1.8 already says the `UNKNOWN` policy "is defined by the
consuming provider-quota extension". The `C`-class thing is Section 8.9's *normalized snapshot*, an
extension field carrying its own `fetched_at` and `stale_after_ms`. So the field becomes `Ephemeral`
for observability, with the reset consequence stated — the status surface reports no rate-limit
reading until the next agent update refreshes it — and becomes `Cached external signal` when the
provider-quota extension enforces on it, which is where its staleness bound and its `UNKNOWN` policy
come from.

**This closes the issue's second edge as a side effect rather than by adding a sentence about it.**
Section 14.3 says a cached value "carries an age; once it is older than its configured staleness
bound it is promoted to an explicit `UNKNOWN`", and no section defines a staleness bound for
`provider_rate_limits` — Section 8.9's `stale_after_ms` belongs to the OPTIONAL extension. Under the
reclass a Core-only build has no aging value because it has no consumer that defines a bound, and
the bound arrives with the extension that owns it.

**And the reclass is more than a re-labelling, for a reason that has nothing to do with tidiness.**
`Ephemeral` is the one class whose reset consequence is a *required part of the class* — Section
14.3 requires it documented, Section 19 and the Conformance Statement are where it is published. So
reclassing the field to `Ephemeral` in Core is what makes the sentence "the status surface reports
no rate-limit reading until the next agent update refreshes it" get written down somewhere a
consumer reads. Under `Cached external signal` there is nothing to write, because a class that
carries its value across a restart has no reset to describe. The minimal fallback — keep it `C` and
say Core has no store — leaves the obligation stated in Section 14.3 and reaching no artifact that
publishes it.

In the `symphony-rs` build this is checkable rather than argued: the recovery class *is* the wrapper
type on the field (`Reconstructable<T>`, `Ephemeral<T>`, `CachedExternal<T>`,
`crates/symphony-orchestrator/src/recovery.rs:1-27`), `State::recovery_classes` destructures `State`
itself, and reclassing makes the compiler demand the reset sentence.

### 2. Section 14.3's `C` bullet — scope the restart half to a store

The `Durable` bullet already carries the clause this one needs ("Durable storage is OPTIONAL. When
no store is configured, the implementation MUST document its degradation"). The `C` bullet takes the
same shape: the last-known-good MUST be carried across a **failed refresh** unconditionally — that
is an in-memory property every implementation can promise, namely not clobbering last-known-good
with a failure — while carrying it across a **process restart** requires a store: where one backs
the field it MUST be restored before any decision that enforces on it; where none is configured the
field starts `UNKNOWN` and the implementation MUST document the degradation.

That makes the class agree with Section 16.1's reference algorithm rather than inventing a rule.

### 3. Section 14.4 — say both restorable classes

Section 14.4's first paragraph and third bullet are false today **independently of the Core-field
question**: a quota extension with a store configured restores a `C` field per Section 16.1, and
Section 14.4 says only `Durable` is restored. The paragraph becomes a statement about which classes
provide for restoration — `Durable`, and `Cached external signal` where a store backs it, both
introduced by OPTIONAL extensions — and the After-restart list gains a `C` bullet beside the
`Durable` one with the same second clause.

### 4. Section 8.9's own bullet needs the same scoping, and was not in the ask

Its Recovery-semantics bullet restates the unconditional promise:

> - The snapshot is class `Cached external signal` (Section 14.3): the last-known-good value is
>   carried across a failed refresh and a process restart …

so an edit touching only Sections 14.3 and 14.4 leaves the extension's own section still promising
what the class no longer does.

## The fail-closed bootstrap, and the clause the section turns on

Once the store-free default is `UNKNOWN`, a deployment with the in-band path only and a fail-closed
policy has no way out of it. Section 8.9's in-band ingestion is fed by Section 13.5's agent updates,
which exist only while a worker runs; Section 14.4 restores no running session in local mode; and
the gate pauses new dispatch. Restart therefore reaches `UNKNOWN` → dispatch paused → no agent
updates → no reading → still `UNKNOWN`.

Section 14.3's existing escape does not cover it, because it turns on a distinction that requires a
reading to have been seen: "An implementation MAY distinguish a permanently `UNKNOWN` signal (the
agent exposes no such interface) from a transiently `UNKNOWN` one (a temporary block)". At startup
with no store, a never-yet-read signal is indistinguishable from a permanently unavailable one.

**The clause took four drafts, and the three that were discarded are the useful record.**

**First: condition on the configuration.** "An `UNKNOWN` that has never held a reading in this
process MUST fail open unless an out-of-band refresh path (Section 8.9's poller) is configured." It
cannot see a deployment with a store configured and a *failed* restore — store unreachable, or empty
on first deploy. Both have an `UNKNOWN` that has never held a reading and no out-of-band poller,
both satisfy Section 16.1 exactly as written, and both reach the livelock the clause exists to
prevent.

**Second: condition on the value.** "An `UNKNOWN` this process has not yet replaced with a reading
MUST fail open. A restored value is a reading; a restore that produced none is not." That fixes
*which value counts* and covers all four startup shapes — no store, store restored, store present
and empty, store unreachable. It has two holes, and neither involves a store:

- **A restore that arrives already stale.** `stale_after_ms` defaults to `180000`. A restored
  snapshot carries the `fetched_at` it was written with, and Section 14.3 promotes a value older
  than the bound to an explicit `UNKNOWN`. So any restart whose downtime exceeds three minutes hands
  back a value that is `UNKNOWN` on arrival — and it **is** a reading under this wording, so the
  escape does not apply. Store configured, restore successful, same livelock.
- **The drained idle, with no restart at all.** Section 8.9's gate says "Running workers and
  reconciliation are not affected", so in-band readings arrive only *while a worker runs*. A
  deployment that finishes its last run and sits idle for `stale_after_ms` ages its snapshot to
  `UNKNOWN` with nothing running, fails closed, and cannot start anything. Three minutes of quiet is
  not an edge case for an issue-driven daemon; it is what one does between tickets. **The deployment
  held a reading, replaced it in this process, and still deadlocks** — so any rule worded over "has
  this process held a reading" cannot see it.

**Third: condition on whether a reading can arrive at all.**

> Where no out-of-band refresh path (Section 8.9's poller) is configured, an `UNKNOWN` MUST fail
> open: the only source of readings is then an agent update, which a paused dispatch prevents, so a
> fail-closed policy would never release.

This is the general form of the reason the first draft already gave, applied without the never-read
scoping that was hiding two cases from it. It reaches the same four startup shapes with the same
answers, reaches both holes above, and **keeps fail-closed for the deployment that configured a
poller in order to have it** — including the startup window, which is the interval a fail-closed
operator most wants covered. A poller that reaches nothing pauses a deployment that asked to be
paused, and says why in the snapshot's `error` field, where a dispatch-fed loop pausing itself says
nothing at all.

**Fourth, and taken: release no more than obtaining a reading requires.**

Raised on the implementation reply to PR #114, against the third draft as captured. The deadlock
argument justifies releasing *enough to produce a reading*; the third draft releases the whole
limit. A deployment at `max_concurrent_agents: 20` that configured a fail-closed quota gate goes
from paused to twenty on a missing reading — at startup and after every idle drain, which is when
nothing has read the account since before the gap and a burst is least well covered by anything
else.

> Where no out-of-band refresh path (Section 8.9's poller) is configured, an `UNKNOWN` MUST NOT
> pause dispatch outright: the gate clamps headroom to one run in flight until a reading arrives.
> The only source of readings is then an agent update, which a paused dispatch prevents, so a
> fail-closed policy would never release — and one run is what makes an agent update arrive, which
> is as far as the deadlock argument reaches.

This is the third draft's rule evaluated on the third draft's condition: same four startup shapes,
same two holes, same answers about *whether* to release. It differs only in **how much**, and it is
the amount the derivation actually supports. What it costs is a quantity stated in the gate, which
the third draft did not have to state.

**The clamp does not sentence anyone to concurrency 1**, because Section 8.9 already carries the
exit: a provider or agent that exposes no quota interface is a permanently `UNKNOWN` signal, and the
gate's existing SHOULD defaults that arm to fail-open. Permanence there is a property of the
provider rather than of a reading, so it is decidable without waiting for one — the clamp governs
the transient and the not-yet-classified cases, which are exactly the ones a fail-closed operator
configured the gate for.

**The two halves live in different sections.** The condition is a property of the class — an
`UNKNOWN` that no configured path can replace MUST NOT be allowed to stop the only path that would
replace it — and belongs in Section 14.3 beside the permanently-versus-transiently allowance. The
quantity is a property of the gate, and the concurrency limit it clamps is Section 8.3's, so the
concrete form belongs in Section 8.9's dispatch-gate bullet with the rest of what the gate does.
Putting the number in Section 14.3 would state a dispatch policy in the section that classifies
state.

**The value-conditioning survives the change of job.** "A restored value is a reading; a restore
that produced none is not" stops being the escape and becomes the input to a distinction Section 8.9
owes anyway: its gate bullet distinguishes "a permanently `UNKNOWN` signal (a provider/agent that
exposes no quota interface)" from "a transiently `UNKNOWN` one (a temporary block)", gives the first
a SHOULD and the second a MAY, and gives an implementation **nothing to decide between them with**.
An `UNKNOWN` that has never held a reading in this process is a different condition from one whose
reading aged past `stale_after_ms`, and only the second can be a temporary block. Section 8.9 owes
that explicitly, and the sentence above is what decides it.

This is the one clause the two sides of the issue had not converged on when the decision was
captured. The third draft was recorded as taken with its full derivation so that a reversal would
have something to argue against rather than a preference to overturn, and that is what the reply
argued against: on the derivation, and on the one axis it was wider than the derivation. The third
draft is kept above rather than replaced, because the difference between the two is the whole
question and a later reader weighing a return to the wider form needs both.

## What the dual class costs, and the column header that stops it being read wrongly

A field that is `Ephemeral` in Core and `Cached external signal` under an extension cannot be both
in one implementation. `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5's "Spec default" cell for
`provider_rate_limits` becomes two-valued like `agent_totals`'s, and its "Reset consequence" cell
stops being `n/a`. The cost is a generator parsing that table gaining a second dual-valued cell, and
the risk is that the cell reads as "both".

The clause belongs on the **column header** rather than in either row: the cell states which of the
two the implementation ships. `agent_totals` has carried the same ambiguity since it was written and
nobody has read it wrongly only because no generator has read it at all — the Symphony statement is
not generated yet, only the `vcsx` one is (decision 0041). One rule for the column, two instances
under it, and the second instance arrives before the parser rather than after.

## Options considered

### Keep `provider_rate_limits` class `C`, and say Core has no store

The minimal fallback, and the one the `symphony-rs` build is executing today under decision 0011
**R75**: its `State::after_restart` has exactly one arm that does not zero its field, and it is this
one. It is the smallest possible edit, it changes no class, and it leaves the `agent_totals`
precedent unextended.

It loses on two counts. Section 14.3's summary claim — that `Cached external signal` is introduced
by an OPTIONAL provider-quota extension — stays false while a Core field carries the class, so the
inconsistency is narrowed rather than closed. And the reset obligation it leaves in place reaches no
artifact that publishes it: under `C` there is no reset consequence to document, so the fact that a
Core-only build's status surface reports no rate-limit reading after a restart is stated nowhere a
consumer looks. The fallback's honest half is worth recording: at a **real** restart that build
already reads `Unknown`, because a Core build ships no store and an actual process restart starts
from a fresh state — the carry only ever reached a second call against a state still held in memory,
which is what a simulated restart is. The reclass makes the published class agree with the
observable behaviour rather than with the half a simulated restart can see.

### Make Section 14.4 agree with Section 14.3 (the issue's first option, alone)

Add a `C` bullet to the After-restart list and stop there. It is the smallest edit that removes the
contradiction as reported, and it keeps the class's meaning intact. It loses because Section 14.3's
MUST stays unsatisfiable by a store-free implementation, which is the case Section 14.3's own
closing paragraph says Core conformance permits.

### Make Section 14.3 agree with Section 14.4 (the issue's second option, alone)

Scope the `C` bullet's restart half to a store and stop there. It loses because Section 14.4's "only
`Durable`" is false for the with-a-store case regardless of what class the Core field carries —
Section 16.1 restores both.

### Leave the fail-closed bootstrap to the existing permanently-versus-transiently `UNKNOWN` MAY

The status quo for the third edge. It loses because that distinction is unevaluable at the moment it
is needed: at startup with no store, a never-yet-read signal and a permanently unavailable one are
the same observation. It also loses on the drained-idle case, which the distinction does not reach
at all.

## What was checked

At `22b5194`, against the working tree:

- Section 14.3's `C` bullet and Section 14.4's first paragraph and third bullet read verbatim as
  quoted; Section 14.3's closing paragraph names `Cached external signal` as introduced by an
  OPTIONAL provider-quota extension.
- Section 4.1.8 classes `provider_rate_limits` as `Cached external signal` and says its `UNKNOWN`
  policy "is defined by the consuming provider-quota extension"; `agent_totals` carries the
  two-valued class this decision follows.
- Section 16.1 initializes `provider_rate_limits: null` and calls
  `restore_cached_and_durable_state`, whose paragraph conditions the overlay on an OPTIONAL
  extension configuring a store.
- Section 8.9's `stale_after_ms` default is `180000`; its gate bullet says "Running workers and
  reconciliation are not affected"; its Recovery-semantics bullet carries the unconditional promise.
- Section 13.5 is the in-band source and is fed by agent updates.
- Section 17.4 carries two conditioned rows naming both classes; Section 18's "every field has a
  documented recovery class" is unaffected.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 carries `Durable-store degradation when no store
  is configured | 14.3`; its Section 5 table carries `provider_rate_limits | Cached external signal
  | <...> | <n/a>` and `agent_totals | Ephemeral (Durable under a budgeting extension) | <...> |
  <...>`.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Reconsideration triggers

- **A Core consumer of `provider_rate_limits`.** The reclass rests on there being none — the field
  is observability in Core and enforcement only under Section 8.9. A Core behaviour that branches on
  it would put the `C` class back and reopen edits 1 and 2 together.
- **An in-band reading source that does not require a running worker.** The rule's entire
  justification is that a paused dispatch prevents the only source of readings. This trigger has
  already fired on its second clause: a gate that permits one probe dispatch is the fourth draft,
  and the clause is narrowed to it rather than left at the whole limit. What stays reconsiderable is
  the first clause — a provider interface reachable with nothing running would make fail-closed
  stateable without a poller and without the clamp.
- **A deployment where one run cannot produce a reading.** The clamp rests on an agent update
  following from a run. A provider that reports quota on only some turns, or an agent whose updates
  carry no rate-limit payload while the signal is not classifiable as permanently `UNKNOWN`, would
  leave the gate releasing one run indefinitely without resolving the state. The choice would then
  be between the third draft's whole-limit release and a bounded number of probes, and the four
  drafts above are what both would be argued from.
- **A second Core field taking the `Cached external signal` class.** The scoping in edit 2 is stated
  over the class rather than over the field, so it would apply — but the reclass argument in edit 1
  is specific to this field's Core role, and a second field would need its own.
- **A generated Symphony Conformance Statement.** The dual-valued cells are the first thing such a
  generator has to interpret; if it cannot, the column header clause is not enough and the table
  needs a shape change rather than a note.
