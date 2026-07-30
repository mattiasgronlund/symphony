# Plan — 0037 The node-scheduler remote adapter, provisioning failures, and the run registry

## Scope

Specifies remote acquisition, its failure model, and restart reattach for the orchestrator↔executor
seam (decisions 0035/0036). Affected `SPEC.md` areas, by stable identity:

- A new **OPTIONAL** section defining the **node-scheduler adapter** (four verbs + capability
  descriptor), the `compute.*` config namespace, boundary-travel as a fail-closed requirement, and the
  sharing hint/key — sited beside the other adapter sections in Chapter 9 (after "Forge Adapter, Pull
  Requests, and Review Writes", Section 9.10).
- Section 7 "Orchestration State Machine" — a `provisioning` sub-state covering the acquire window.
  (Decision 0038 also edits Section 7 — the driver-local / reconciler-remote reframing; the two
  Section 7 edits are complementary and applied together.)
- Section 8.3 "Concurrency Control" — a clarifying note that slot accounting is placement-opaque
  (session-count-based) and unaffected by scheduler packing.
- Section 14.1 "Failure Classes" — two new classes: `Node Provisioning Failures` and
  `Executor Bring-up Failures`.
- Section 14.2 "Recovery Behavior" — recovery for each: node-provisioning is scope-scoped skip +
  retry (mirroring `Repository Provisioning Failures`); executor bring-up is fail-closed.
- Section 14.4 "Partial State Recovery (Restart)" — a required remote-mode-only durable **run
  registry** and reattach via `lookup_by_run_id`.
- Section 16.4 "Dispatch One Issue" / Section 16.5 — async acquire ahead of the run; on remote,
  `ensure_object_store` (Section 16.5) runs on the executor's node.
- Section 6.4 (cheat sheet), Section 17 (test matrix), Section 18 (checklist) — cross-cutting sync.

Out of scope: the component and seam (0035); the wire protocol and secret delivery (0036);
executor-authoritative writes and broker relocation (0038). Everything cloud-shaped (vendor APIs,
variant catalog, pooling, autoscaling, billing, teardown timing) is the node-scheduler's and is
`Implementation-defined` — no `SPEC.md` surface.

This decision is `Accepted`; edits are the planned end-state, applied as the 0035–0038 set.

## Steps

1. **An OPTIONAL node-scheduler adapter section exists.** Add an OPTIONAL section (Chapter 9, after
   Section 9.10) that opens in the established extension register ("An OPTIONAL extension that …") and
   defines a `compute`-kinded adapter with a static capability descriptor (parallel to Sections 10.9 /
   11.7 / 9.10) declaring at least: `local` vs `remote`, supported `sharing` modes, and what
   `signal_done` requests. The default `kind` is `local` (the in-process transport of 0035), so an
   implementation that does not ship this extension behaves exactly as core. Done-condition: an
   OPTIONAL `compute` adapter section exists, `kind` defaults to `local`, and it declares a capability
   descriptor.

2. **The adapter has exactly four verbs.** Specify `request_node(selection, bound)`,
   `node_ready(endpoint, trust_material)`, `lookup_by_run_id(run_id) → endpoint`, and
   `signal_done(run_id)`, at spec altitude. `selection` = repository identity (Section 8.7),
   normalized issue labels (Section 11.3), agent/effort (Section 10.9), and a sharing key + hint (Step
   6); `bound` = the wall-clock/cost ceiling (Section 16.6 / decision 0036). State that reap, TTL,
   pooling, autoscaling, billing, variant catalog/selection, and teardown timing are the scheduler's
   and are `Implementation-defined`; Symphony treats the node as opaque. Done-condition: the four
   verbs are specified with inputs/outputs, and the out-of-scope scheduler responsibilities are
   explicitly `Implementation-defined`.

3. **Boundary travel is a fail-closed conformance requirement of `remote`.** State that a remote
   executor MUST instantiate the sandbox (Section 9.6), the per-run broker socket (Section 10.8), and
   the credential-less-agent invariant (Section 15.3; decision 0003) on its node; the object store
   (Section 16.5, `ensure_object_store`) is cloned/fetched fresh on the executor's node context using
   the directly-delivered credentials (decision 0036). If the boundary cannot be instantiated, bring-up
   fails closed (Step 5) — the run never proceeds credential-exposed. Done-condition: `remote` mode
   requires on-node boundary instantiation, ties `ensure_object_store` to the executor's node, and
   makes boundary-instantiation failure fail-closed.

4. **A `provisioning` orchestration sub-state exists (Section 7).** Add a sub-state covering the
   acquire window: after candidate selection, before running, the issue is `provisioning` (a node is
   being requested/booted and the executor brought up). The poll tick (Section 16.2) is not blocked;
   a `provisioning` issue is not counted as running for turn purposes but does hold a dispatch slot
   (so acquire cannot oversubscribe). Done-condition: Section 7 has a `provisioning` sub-state between
   selection and running, the tick does not block on acquire, and slot accounting accounts for
   in-flight acquires.

5. **Two new failure classes with distinct recovery (Sections 14.1–14.2).**
   - `Node Provisioning Failures` — the scheduler cannot supply a node (capacity, transport, invalid
     placement config). Recovery is **scope-scoped**, mirroring `Repository Provisioning Failures`
     (decision 0034): skip the affected dispatch scope, retry on a later tick, keep the service alive,
     do **not** convert to per-worker backoff. Persistent invalid-config/auth (the scheduler's own
     credentials) MAY be parked; `Implementation-defined`, MUST document.
   - `Executor Bring-up Failures` — the executor process will not start, fails mutual auth (decision
     0036), or cannot instantiate the sandbox / per-run broker socket / boundary on the node. Recovery
     is **fail-closed and run-fatal**: never run the agent without the boundary; the orchestrator MAY
     re-dispatch onto a fresh node (Step 8) but MUST NOT proceed credential-exposed.
   - The existing agent-session failure class (Section 14.1) is unchanged.
   Done-condition: Section 14.1 lists both classes distinctly; Section 14.2 gives node-provisioning a
   repo/scope-scoped retry and executor bring-up a fail-closed rule; agent-session is untouched.

6. **Sharing is a hint + key; Section 8.3 is placement-opaque.** In the adapter section, define a
   `sharing_key` (derived from inputs Symphony already has, e.g. repository) and a `sharing` hint
   (`exclusive` vs `shared`), passed on `request_node`; the scheduler maps sessions → instances by
   packing isolated executor processes (each with its own sandbox/broker/secrets). Add a clarifying
   note to Section 8.3 that slot accounting stays session-count-based and placement-opaque, so packing
   does not affect concurrency limits; a deployment bounds co-location with the existing
   `max_concurrent_agents` limits. Done-condition: sharing is expressed as hint + key with the
   scheduler owning packing, and Section 8.3 states placement-opacity with no new concurrency knob.

7. **A required remote-mode-only durable run registry + reattach (Section 14.4).** State that in
   remote mode the orchestrator durably persists a **run registry** mapping `run-id ↔ issue ↔ node`;
   on restart it reconciles in-flight remote runs by re-querying the scheduler `lookup_by_run_id` for
   the current endpoint (surviving node moves) and reattaching over the seam (decision 0036 replays
   buffered events). The same `lookup_by_run_id` re-addressing also serves a **mid-run** reconnect
   whose known endpoint went stale (a moved node), not only a full restart; the executor runs
   autonomously through any orchestrator disconnect (decisions 0031/0038), so reattach resumes a live
   run rather than restarting work. This is scoped to remote mode: **local execution keeps Section
   14.4's reconstruct-from-filesystem/tracker recovery unchanged**. Done-condition: Section 14.4
   requires the run registry only in remote mode, specifies reattach via `lookup_by_run_id` (covering
   both a mid-run stale endpoint and a restart), and leaves local recovery as-is.

8. **Across-run retry is orchestrator-owned and non-coercive (Section 8.4).** State that the executor
   owns within-run continuation (decisions 0031/0038) while the orchestrator owns across-run retry by
   re-dispatch; the orchestrator MAY request a fresh node but MUST NOT compel the scheduler to supply
   one (a denial is a `Node Provisioning Failure`, recovered scope-scoped). Done-condition: Section
   8.4 places across-run retry at the orchestrator, and states the orchestrator cannot force node
   capacity.

9. **`compute.*` config namespace (Section 6.4 + adapter section).** Define an extension-owned
   `compute.*` namespace, operator policy config (consumed outside the sandbox): `compute.kind`
   (default `local`); `compute.variant_by_label` (map, default `{}`, pass-through, mirrors
   `agent.agent_by_label`); `compute.variant_by_repo` (map, default `{}`, repo default overridden per
   issue by label); `compute.sharing` (default `exclusive`); `compute.sharing_key` (template over
   known inputs, default `repository`); `compute.max_wall_clock_ms` (the run bound sent to the executor
   — decision 0036); `compute.release` (`decommission` for remote / `noop` for local — the disposition
   `signal_done` requests). State these are extension-owned and not Core Conformance; provider-specific
   config (vendor creds, catalog, pool sizing, billing) lives under the provider and is
   `Implementation-defined`. Done-condition: the `compute.*` keys are documented in the adapter section
   with the field-doc pattern, flagged extension-owned, with a one-line Section 6.4 note.

## Cross-cutting sync

- **Section 6.4 (config cheat sheet):** add a note that `compute.*` is an extension namespace (`kind`
  default `local`; variant-by-repo/label pass-through; sharing hint/key; wall-clock bound; release
  disposition) — extension-owned, not Core Conformance, per the Section 6.4 convention that extension
  fields are documented where the extension defines them.
- **Section 17 (test matrix):** add Extension rows — `local` is behaviorally core (no scheduler);
  node-provisioning failure is scope-scoped and retried (not per-worker backoff); executor bring-up /
  boundary failure is fail-closed; a run reattaches via `lookup_by_run_id` after an orchestrator
  restart (surviving a node move); `signal_done` is emitted on completion and terminal/cancel; the
  orchestrator cannot force the scheduler to supply a node; the run registry exists only in remote
  mode (local still reconstructs).
- **Section 18 (implementation checklist):** add an Extension line for the node-scheduler adapter
  (four verbs + capability descriptor + `compute.*`), the `provisioning` sub-state, the two failure
  classes with their recovery, boundary-travel fail-closed, and the remote-mode run registry +
  reattach.

## Anchor changes

New anchors introduced (no renames/removals):

- OPTIONAL section **Node-Scheduler Adapter** (Chapter 9, after Section 9.10).
- Config namespace **`compute.*`** (`compute.kind`, `compute.variant_by_label`,
  `compute.variant_by_repo`, `compute.sharing`, `compute.sharing_key`, `compute.max_wall_clock_ms`,
  `compute.release`).
- Adapter verbs **`request_node`**, **`node_ready`**, **`lookup_by_run_id`**, **`signal_done`**.
- Orchestration sub-state **`provisioning`** (Section 7).
- Failure classes **`Node Provisioning Failures`** and **`Executor Bring-up Failures`** (Section
  14.1); recovery entries (Section 14.2).
- Concept **run registry** (Section 14.4, remote-mode only).

Section-number impact: inserting the node-scheduler adapter after Section 9.10 adds Section 9.11 (no
retitle of existing 9.x). The `provisioning` sub-state and the two failure classes are additions
within existing sections. Any renumbering will be recorded here append-only when the edits land.

## Status

Applied to `SPEC.md`. The OPTIONAL `Node-Scheduler Adapter` is Section 9.11 (four verbs, capability
descriptor, boundary-travel fail-closed, sharing, `compute.*`); the `Provisioning` state is added to
Section 7.1; `Node Provisioning Failures` and `Executor Bring-up Failures` are Section 14.1 classes 7
and 8 with recovery in Section 14.2; the remote-mode run registry is a `Durable`-class addition to
Section 14.4; Section 8.3 gains the placement-opaque note, Section 8.4 the non-coercive-retry note,
Section 6.4 the `compute.*` keys, and Section 16.4 the async-acquire comment.

No deviation of substance: the run registry is expressed within the existing recovery-class taxonomy
(`Durable`, Section 14.3), and the two failure classes are marked OPTIONAL alongside the existing core
classes. `ensure_object_store` (Section 16.5) is cited as running on the node's context for a remote
executor.
