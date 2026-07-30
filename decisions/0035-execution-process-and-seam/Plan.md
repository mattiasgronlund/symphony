# Plan — 0035 The execution process and the always-present orchestrator↔executor seam

## Scope

Implements Option B (see `Background.md`): name the Execution Layer as a first-class component and
make the orchestrator↔executor seam always present, with local as the in-process transport. Affected
`SPEC.md` areas, by stable identity:

- Section 3.1 "Main Components" — add the **execution process** (the executor) as a named component,
  distinct from the orchestrator.
- Section 3.2 "Abstraction Levels" — state that the existing Execution Layer is realized by the
  execution process, reachable across an always-present orchestrator↔executor seam whose local form is
  in-process.
- Section 16.6 "Worker Attempt (Workspace + Prompt + Agent)" — reframe the worker as the executor
  running behind the seam; the in-memory `orchestrator_channel` becomes the in-process form of the
  seam's up-channel.
- Section 16.4 "Dispatch One Issue" — dispatch hands a run to an executor across the seam (in-process
  by default) rather than calling the worker directly.
- Sections 9 and 10 — note that the executor is what instantiates the sandbox (Section 9.6), the
  per-run broker socket (Section 10.8), the workspace/object store (Sections 9.2, 16.5), and speaks
  the agent protocol (Section 10); these responsibilities are the executor's wherever it runs.

The wire protocol, secret delivery, node-scheduler adapter, failure model, run registry, and the
state-writer reframing are **out of scope here** and specified in decisions 0036 (protocol), 0037
(node-scheduler adapter + failure/registry), and 0038 (executor-authoritative writes). This decision
establishes only the component and the seam.

This decision is `Accepted`; the `SPEC.md` edits below are the planned end-state, applied as the set
0035–0038, batched with the companion protocol sub-spec (0036) — not yet applied.

## Steps

1. **The executor exists as a named component in Section 3.1.** Add an **execution process**
   component to the Main Components list: the unit that, for one run, provisions the workspace and
   object store, builds prompts, runs the agent turn loop, mediates privileged operations through the
   broker, and runs workspace lifecycle hooks — i.e. everything Section 16.6 does today. State that
   the orchestrator dispatches runs to an executor and that exactly one executor serves one run.
   Done-condition: Section 3.1 lists the execution process as its own component, and the worker
   language in Section 16 refers to it.

   The executor **is the host relative to its own sandbox** (Section 9.6), so it runs **both hook
   trust levels** (Section 5.3.4): in-sandbox `WORKFLOW.md` hooks inside its sandbox, and host-side
   policy-config hooks in its own context (the node when remote, the orchestrator host when
   in-process). Host-side WoW/hooks are sourced from the protected base revision (decision 0029),
   which the executor already holds from its object-store clone — so no hook definition needs to
   cross the seam separately. Done-condition: the spec attributes both hook trust levels to the
   executor as host relative to its sandbox, and points host-side WoW sourcing at the base revision
   (0029).

2. **Section 3.2 ties the Execution Layer to the executor and the seam.** In "Abstraction Levels",
   state that the Execution Layer is realized by the execution process, and that the orchestrator
   reaches it across an **always-present orchestrator↔executor seam**. Say plainly that **local
   execution is the in-process transport** of that seam and remote execution (decisions 0036–0037) is
   the same seam over a network transport — one execution model, not two. Done-condition: Section 3.2
   names the seam, states that local is its degenerate in-process form, and forward-references
   0036/0037 for the remote transport without depending on them for the local case.

3. **The executor owns the boundary wherever it runs.** In the Section 3.2 / Section 9.6 vicinity,
   state that the sandbox (Section 9.6), the per-run broker socket (Section 10.8), and the
   credential-less-agent invariant (Section 15.3) are instantiated **by the executor**, so they hold
   identically for the in-process and (per 0037) the remote transport. Done-condition: the spec
   attributes boundary instantiation to the executor as a component property, not to "the host",
   so the remote transport inherits it by construction.

4. **Section 16.6 reads as the executor's run, not an in-process worker.** Reframe
   `run_agent_attempt` so its body is explicitly the executor's responsibility set (object store,
   `before_run`, prompt, turn loop, `release`, `after_run`), and describe the `orchestrator_channel`
   as the **in-process form of the seam's up-channel** (normalized events; Sections 10.4, 13.5).
   Keep the algorithm's behavior unchanged for the local case. Done-condition: Section 16.6 presents
   one executor run whose event delivery is the local transport of the seam, with no behavior change
   for a single-host deployment.

5. **Section 16.4 dispatches across the seam.** Reframe `dispatch_issue` so the spawn step hands a
   run to an executor over the seam (in-process by default). Leave `ensure_object_store` (Section
   16.5) attribution as-is for local; 0037 sites it on the executor for remote. Done-condition:
   `dispatch_issue` shows dispatch → executor(run) across the seam, and a single-host implementation
   still behaves as today (in-process transport).

## Cross-cutting sync

- **Section 6.4 (config cheat sheet):** no change here — this decision adds no config key (the
  `compute.*` namespace that selects local vs remote transport is introduced by 0037).
- **Section 17 (test matrix):** add a Core row asserting that local execution is the in-process
  transport of the seam and is behaviorally identical to today's worker (a conformance anchor so the
  refactor is observable-equivalent for single-host).
- **Section 18 (implementation checklist):** add a Core line: "the Execution Layer is realized by a
  single execution process behind an always-present orchestrator↔executor seam; local execution is
  its in-process transport."

## Anchor changes

New anchors introduced (no renames/removals of code-tokens):

- Component **execution process** (Section 3.1).
- Concept **orchestrator↔executor seam** (Section 3.2).

Terminology shift: the per-issue **worker** (Sections 7.2, 16.4, 16.6) is reframed as the **execution
process / executor**. The word "worker" may remain as a readable synonym in the worker-lifecycle
prose, but the component of record is the executor. Recorded here so later plans that cite "worker"
resolve to the executor. Section-number impact is expected to be minimal (no new numbered sections in
this decision); 0037's `provisioning` sub-state and 0036's protocol deference are the edits that may
renumber neighbours, and those are tracked in their own plans.

## Status

Applied to `SPEC.md`. The `Execution Process (executor)` and the always-present orchestrator↔executor
seam are added to Sections 3.1 and 3.2; `run_agent_attempt` (Section 16.6) and `dispatch_issue`
(Section 16.4) are reframed as the executor's run across the seam (local = in-process, behavior
unchanged); and the executor is stated to run both hook trust levels and instantiate the
secret-isolation boundary wherever it runs.

Deviation (per the 0034 precedent): `SPEC.md` is expressed in its current vocabulary because the
0027–0033 batch's spec edits are still deferred. The three-topology framing (0027) is not named in
`SPEC.md` — the executor is presented against Section 3.2's existing abstraction levels — and the
topology-scope nuance stays in `Background.md`. Host-side hook sourcing from a protected base revision
(0029) is expressed through the current two-trust-level hook model (Section 15.4) rather than by naming
the base revision. To be reconciled when the 0027/0029 edits land.
