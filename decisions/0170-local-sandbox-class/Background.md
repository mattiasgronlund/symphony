# Background — 0170 A fail-closed MUST with no class to report it under

## Context

Reported from `symphony-rs` as issue #146, against `5a4fdf7`, found while building that repository's
roadmap D5e.

Section 9.6 (Agent Sandbox and Execution Isolation) opens with an unqualified requirement:

> Each coding-agent run MUST be runnable inside a sandbox that isolates the agent from the host and
> from Symphony's credentials.

Every run, and Section 3.1's local executor is always present. The failure class that names a
sandbox which cannot be brought up is scoped to a node twice over — in class 9's header
(`executor_bring_up_failures`; OPTIONAL, remote execution — Section 9.11) and again in its bullet
("cannot be instantiated **on the node**"). So a local run carries a fail-closed MUST with no class
to report it under, and Section 14.2 therefore assigns it no disposition.

## The mechanism

**Reaching for class 9 anyway is not a harmless approximation; it makes the condition permanently
unrecoverable.** This is the report's strongest leg and it checks out against Section 14.2 rather
than resting on the classes' names. Class 9's whole disposition:

> Fail-closed and run-fatal: the run MUST NOT proceed without its sandbox, per-run broker socket,
> and credential-less agent (Section 9.6). The orchestrator **MAY** re-dispatch onto a fresh node
> (Section 8.4) but MUST NOT run the agent credential-exposed.

The only route back into service is a permission, and it is a permission to do something a
deployment without a node-scheduler cannot do. There is no backoff arm and no retry arm. A local
deployment filing a typo'd sandbox profile under class 9 would park every run in the instance,
indefinitely, against a condition an operator fixes in one line. The worker disposition converges
instead — "Convert to retries with exponential backoff" — so the attempt retries, Section 8.4's
bound is reached, the run fails normally, and the operator sees it.

That asymmetry is not incidental to class 9: the class *is* a topology. Its header names the
OPTIONAL extension it belongs to, and its disposition is written for a world where another node
exists.

**Class 3 and class 4 are indistinguishable in behaviour, and Section 14.2 says so outright.**

> Worker failures (`workspace_failures`, `agent_session_failures`):
> - Convert to retries with exponential backoff.

and, in the same section's opening, "`workspace_failures` and `agent_session_failures` share the
worker disposition because both fail one attempt". So nothing observable turns on which of the two
this lands in. That is worth stating plainly rather than arguing the choice as though it decides
something: what the choice decides is **where a reader looks**, and a later reader who takes it for
load-bearing will be looking for a difference that is not there.

Class 4 is still the right one, on what the sandbox is rather than on what happens to it. Section
9.6 describes it as isolating "the agent"; the per-run broker socket is mounted into it; Section
16.6 orders teardown so that the sandbox "is scoped to the attempt and outlives the agent session".
A boundary that must exist before the session can start and that outlives it belongs to the
session's lifecycle. The workspace is a directory that exists before either and survives both.

**The existing class 4 bullet is not stretched to cover it.** "Startup handshake failure" names a
protocol event; a sandbox that will not instantiate is not one. Adding a bullet is cheaper than
straining one, and a strained bullet is what produces the next report of this kind.

**Why the gap survived is visible in the text, and neither report leg names it.** Measured at
`60092ef`:

```
$ awk '/^### 9\.6 /,/^### 9\.7 /' SPEC.md | grep -c '14\.'
0
```

Section 9.6 cites Section 14 nowhere and carries no fail-closed language of its own. So the MUST
sits with no disposition in view: a reader of Section 9.6 has nothing to follow, and a reader of
Section 14.1 arriving from the other side finds the condition under a header marked OPTIONAL and
reads "remote". The two halves each look complete from where they stand, which is the shape of gap
that survives review.

## Options considered

- **Option A — class 4 gains a bullet naming the local condition; class 9 keeps its header and its
  node-scoped bullet.** The fail-closed obligation is stated on both bullets, so it survives
  wherever a reader enters. Section 9.6 gains the pointer it lacks.

  Trade-offs: two bullets for one condition at two sites, which a reader could mistake for two
  conditions. Mitigated by each naming the other's site.

- **Option B — widen class 9** (the report's first option): drop "on the node" from the bullet and
  the `OPTIONAL, remote execution` qualifier from the header.

  Trade-offs: this is the tidier taxonomy and deserves saying so — one condition, one class, one
  bullet, and the fail-closed obligation is genuinely identical at both sites. It loses on what it
  drags with it. Class 9's Section 14.2 disposition is written for a deployment that has another
  node; widening the class would need a second disposition inside it that branches on whether a
  node-scheduler exists. That is a fork in the recovery table on deployment topology, in the one
  class whose identity *is* a topology, and it would put a Core condition under a class Section 14.1
  marks OPTIONAL.

- **Option C — class 3, `workspace_failures`.** The report calls it arguable and it is.

  Trade-offs: the sandbox is instantiated around a workspace, workspace provisioning precedes it in
  Section 16.6, and the disposition is identical, so nothing an operator can observe differs. It
  loses on the reader's question rather than on behaviour: someone tracing why a run refused to
  start reads the class name first, and `workspace_failures` sends them to the directory rather than
  to the boundary the run was refused for.

## Decision and reasoning

**Option A.** The deciding consideration is that class 9's disposition and its class membership are
the same fact — a node-scheduler's — and a Core condition cannot be filed under a fact that does not
hold for it.

**On the choice between class 3 and class 4 being unobservable.** It is recorded above rather than
argued away, because the honest statement of this decision is that it fixes one real defect (a
condition with no class) and makes one presentational choice (which of two identically-disposed
classes). Conflating the two would give a later reader the impression that reclassifying to class 3
would change behaviour. It would not, and the reconsideration trigger below is written for the case
where that stops being true.

**On Section 9.6's pointer**, which goes beyond what the issue asks and beyond the call published on
it. The measurement above is the reason: the requirement and its consequence had no path between
them in either direction, and adding the class bullet alone repairs only the direction a reader of
Section 14.1 travels. A reader of Section 9.6 — which is where an implementer of the sandbox is
working — would still find a MUST with no stated consequence.

## Reconsideration trigger

Reopen if Section 14.2 ever gives `workspace_failures` and `agent_session_failures` different
dispositions. The choice between class 3 and class 4 is unobservable today and becomes load-bearing
the moment they diverge; this decision would then be resting on a reader-orientation argument to
settle a behavioural question, which is not what it was decided on.

A second trigger: a local sandbox failure a per-worker backoff does not converge on — a profile that
fails only under load, or a host resource the retry itself exhausts. The worker disposition would
then be the wrong one, and the answer is a park within class 4 rather than a move to class 9, whose
disposition still needs a node this deployment does not have.
