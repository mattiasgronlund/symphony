# Background — 0037 The node-scheduler remote adapter, provisioning failures, and the run registry

## Context

Decisions 0035 and 0036 give remote execution a component (the executor) and a wire contract (the
orchestrator↔executor protocol with direct secret delivery). This decision specifies how the
orchestrator obtains a remote executor in the first place, what happens when it cannot, and how it
finds an in-flight remote run again after a restart. It is where the operational goal lands: run
sessions on **Cloud Instances** billed per started hour, provisioned and reaped by an external system,
with the instance variant chosen per repository and/or issue label and work shared across instances
under a configurable policy — while keeping cloud logic out of Symphony.

The governing move is to introduce a **node-scheduler**: an external system Symphony can be
*configured to connect to*, which owns node lifetimes end to end. The node-scheduler provisions and
reaps nodes, deploys the executor software, bootstraps the mutual-auth trust material (decision 0036),
tracks node lifetimes, and owns everything cloud-shaped — vendor APIs, the instance-variant catalog
and the logic that maps a request to a variant, pooling and reuse, autoscaling and warm capacity,
billing, and teardown timing. It is deliberately **not** in the secret path (0036) and **not** in
agent communication (the agent protocol terminates on the executor, 0036). Symphony connects to it
through a thin adapter, structurally a sibling of the tracker (Section 11), VCS (Section 9.7), and
forge (Section 9.10) adapters: a `kind` selector, a small operation set, and a capability descriptor.
This is what "as little as possible in Symphony" means concretely — the cloud complexity is the
node-scheduler's; Symphony's marginal surface is an adapter, a failure model, and a run registry.

Three gaps in the current spec have to close for this to work:

1. **Acquire is slow.** Section 16.2's poll-and-dispatch tick and Section 16.4's `dispatch_issue`
   assume near-instant local workspace creation. Obtaining a node can take minutes (cold boot). The
   state machine (Section 7) has no state for "a run is provisioning but not yet running", so a slow
   acquire would either block the tick or masquerade as a running session.

2. **Provisioning can fail in new ways with new blast radii.** Decision 0034 established the pattern:
   repository provisioning (the shared object-store clone/fetch) gets its own `Repository Provisioning
   Failures` class (Section 14.1) with **repo-scoped** recovery (Section 14.2) — skip the repository's
   dispatches, retry on a later tick, keep the service alive — precisely because its blast radius and
   recovery differ from an issue-scoped worker failure. Node provisioning is the same shape one layer
   out: "the scheduler cannot supply a node" is a capacity/transport condition to retry later, not a
   per-worker backoff. But executor **bring-up** failures are different again: if the executor process
   will not start, fails mutual auth, or cannot instantiate the sandbox + per-run broker socket on the
   node, the run must **not** proceed — the boundary decision 0004 required is exactly what is missing,
   so this is fail-closed, not a soft skip.

3. **Restart can orphan a paid node.** Section 14.4's recovery leans on **reconstructing** state from
   the tracker and filesystem rather than durable orchestrator state. That works when execution is
   local: the workspace is on disk, the tracker holds the issue state. It does not work for a remote
   run: after an orchestrator restart the node endpoint that was in memory is gone, and an
   in-flight per-hour node keeps billing whether or not the orchestrator remembers it. Reattaching
   requires the orchestrator to know which node runs which issue.

## Options considered

- **Adapter operation set — request/ready/lookup/done (chosen) vs. add release/enumerate vs.
  request/ready only.** A four-verb adapter — `request_node(selection, bound)`,
  `node_ready(endpoint, trust_material)`, `lookup_by_run_id(run_id) → endpoint`, `signal_done(run_id)`
  — is the smallest set that supports acquire, reattach, and reclaim while leaving reap, TTL, pooling,
  and teardown timing scheduler-internal. Adding explicit `release_node` / `enumerate_runs` gives the
  orchestrator more control and easier reconciliation, but pulls lifetime and enumeration into
  Symphony's contract — the opposite of the mandate. Dropping to `request` / `ready` only is thinnest
  but loses run-id lookup (a node that moved breaks reattach) and any Symphony-initiated done signal
  (reclaim becomes purely the scheduler's idle timer, slowing cost recovery). Four verbs is the knee
  of the curve.

- **Acquire scheduling — async with a `provisioning` sub-state (chosen) vs. blocking worker vs.
  require a warm pool.** A new `provisioning` orchestration sub-state (Section 7) models the cold-boot
  window: the issue is neither idle nor running until the executor is ready, so the tick is not
  blocked and a slot is not misattributed. Blocking the worker on acquire keeps the state machine
  simpler but parks a worker and holds a slot through the whole cold boot, and a stuck acquire ties up
  capacity. Requiring the scheduler to keep a warm pool makes acquire fast but pushes real cost and
  complexity out while assuming warm capacity exists — a poor default for per-hour billing. Async +
  sub-state keeps the orchestrator responsive and honest about what is happening.

- **Failure taxonomy — three distinct surfaces, two new classes (chosen) vs. fold node+bring-up into
  one vs. split only by fail-closed-vs-retry.** Three distinct surfaces — **node-provisioning**
  (scheduler can't supply) → scope-scoped retry mirroring 0034; **executor bring-up / auth /
  isolation** → fail-closed, fresh node; **agent-session** (Section 14.1 existing) → unchanged — of
  which the first two are **new** failure classes and agent-session already exists. Keeping them
  distinct gives precise recovery per layer at the cost of more taxonomy. Folding node-provisioning
  and bring-up into one class conflates "no node, retry later" with "auth/isolation failed, fail
  closed" under one recovery rule, which is wrong. Splitting only by behavior (fail-closed vs. retry)
  maps to recovery but loses the node-vs-executor-vs-agent attribution operators need to debug a
  remote run. Distinct surfaces match blast radius to recovery, as 0034 did for repository
  provisioning.

- **Restart recovery — required durable run registry (chosen) vs. reconstruct-from-tracker vs.
  scheduler-is-the-registry.** A required, **remote-mode-only** durable registry mapping
  `run-id ↔ issue ↔ node` lets the orchestrator reconcile in-flight remote runs after a restart:
  re-query the scheduler `lookup_by_run_id` for the current endpoint (surviving node moves) and
  reattach. Reconstructing the run-id from tracker/forge artifacts preserves Section 14.4's philosophy
  but overloads tracker metadata and depends on the scheduler indexing by that id. Making the
  scheduler the registry avoids new orchestrator state but makes the scheduler contract authoritative
  for run discovery and needs an enumerate verb. The registry is the honest cost of remote reattach;
  it is scoped to remote mode so local execution keeps Section 14.4's reconstruct-from-filesystem
  recovery unchanged.

## Decision and reasoning

Accepted; the chosen directions are the four-verb adapter, async acquire with a `provisioning`
sub-state, two new failure classes (over three distinct surfaces, with agent-session unchanged), and a
required remote-mode-only durable run registry. Together they make remote execution operable while
keeping cloud logic external.

**The adapter and what stays out.** Symphony connects to a node-scheduler through a `compute`-kinded
adapter with four verbs. `request_node(selection, bound)` carries the selection inputs Symphony
**already computes** — repository identity (Section 8.7), normalized issue labels (Section 11.3),
agent/effort selection (Section 10.9), and a sharing key + hint — plus the wall-clock/cost bound the
paying orchestrator sets (enforced by the executor, which self-terminates and reports a timeout).
`node_ready(endpoint, trust_material)` returns a dialable endpoint and the mutual-auth bootstrap
(decision 0036). `lookup_by_run_id` supports reattach. `signal_done` tells the scheduler a run is
finished; the scheduler decides keep-warm / reuse / destroy and reaps idle or orphaned nodes.
Everything else is the scheduler's and is `Implementation-defined`: vendor APIs, the variant catalog
and variant-selection logic (Symphony passes the inputs; the scheduler picks the variant), pooling,
autoscaling, billing, and teardown timing. Symphony treats the node as opaque.

**Boundary travel is a fail-closed conformance requirement.** A remote executor MUST instantiate the
same boundary the in-process executor provides (0035 Step 3): the sandbox (Section 9.6), the per-run
broker socket (Section 10.8), and the credential-less agent (Section 15.3, decision 0003). The
object-store clone/fetch (Section 16.5, decision 0034) runs on the executor's node context using the
directly-delivered credentials (0036) — a fresh, per-executor-process store. If the boundary cannot be
instantiated, bring-up **fails closed**; the run never starts credential-exposed. This is the specific
gap 0004 named, now a conformance condition of the remote transport.

**Sharing needs no new orchestration mechanism.** The scheduler packs **isolated executor processes**
onto nodes; each executor independently holds its own sandbox, broker, and secrets (delivered over its
own mutual-auth channel — 0036), so cross-credential co-tenancy risk dissolves — secrets are
per-executor-process, never per-node. Symphony passes a `sharing_key` (derived from inputs it already
has, e.g. repository) and a `sharing` hint (`exclusive` vs `shared`); the scheduler decides sessions →
instances. Section 8.3 concurrency is **unchanged** — it stays session-count-based and
placement-opaque, so packing is invisible to slot accounting. A deployment that wants Symphony to
bound co-location reuses the existing `max_concurrent_agents` limits; no new knob.

**Retry stays layered and non-coercive.** The executor owns within-run continuation (turns,
`continuation_ref`, completion — decisions 0031/0038); a wholesale run failure returns a typed outcome
and the orchestrator owns **across-run** retry (Section 8.4) by re-dispatch. The orchestrator **may**
re-dispatch but **may not compel** the scheduler to supply a fresh node — it requests, and the
scheduler may reuse or deny (a denial is a node-provisioning failure, recovered scope-scoped). This
keeps Symphony an enabler, not an enforcer (decision 0027).

What would make us reconsider: if reattach proves unnecessary in practice (short runs, cheap
re-dispatch) the durable run registry could downgrade from required to an OPTIONAL, capability-gated
component; and if a provider class genuinely cannot carry the boundary to its nodes, remote mode is
capability-gated off for it rather than relaxing the fail-closed rule.

This decision relates to 0004 (makes boundary travel a fail-closed conformance requirement — the
reintroduction 0004 anticipated), 0034 (reuses its repo-scoped recovery shape for node-provisioning,
and its `ensure_object_store` now runs on the executor's node), 0025 (the placement seam this fills is
its Option C generalized — see 0025's update), 0027 (enabler-not-enforcer; the orchestrator cannot
compel capacity), 0035 (the executor obtained here), 0036 (the endpoint/trust/secret channel and the
wall-clock bound), and 0038 (the executor commits writes; terminal/cancel updates flow while
connected). Depends on 0035 and 0036.
