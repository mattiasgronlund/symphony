# Background — 0035 The execution process and the always-present orchestrator↔executor seam

## Context

SSH-based remote execution was removed in decision 0004. Its `Anchor changes` dropped the *SSH Worker
Extension* (Appendix A) and its `worker.ssh_hosts` / `worker.max_concurrent_agents_per_host` config,
because remote execution "must now carry the sandbox, per-run socket, and credential-broker boundary
to the remote host, which is more than the appendix specifies", and 0004 recorded that we "may
reintroduce a reworked remote-execution extension later." This decision (with 0036–0038) is that
reintroduction, in a form that does carry the boundary — and it starts by naming the seam the old
extension lacked.

The new driver is a concrete operational need: run coding-agent sessions on **Cloud Instances** that
may be billed per started hour, provisioned and torn down by an external system, with the instance
variant chosen per repository and/or issue label, and work shared across instances under a
configurable policy. The governing constraint is to implement **as little as possible inside
Symphony** — but "as little as possible" resolves to *little cloud/scheduler logic*, not *no new
surface*. Vendor APIs, provisioning, pooling, autoscaling, billing, and node lifetimes belong to an
external node-scheduler (decision 0037). What Symphony genuinely needs is a clean place for execution
to *detach* from the orchestrator's host.

Today the spec has no such place. `SPEC.md` describes where work runs only implicitly: Section 16.6
`run_agent_attempt` provisions a workspace and calls `agent.run_turn(...)` in the orchestrator's own
process, streaming events back over an in-memory `orchestrator_channel` (Section 16.4 `dispatch_issue`
spawns the worker). "Where" a session runs is never a modeled choice — it is always "this host". The
worker's boundary with the orchestrator was never a contract; it is a function call. Section 3.2
already names an **Execution Layer** ("workspace + agent subprocess") distinct from the Orchestration
Layer, and decision 0027 already factors Symphony into a broker core, a `vcsx` engine, and an
autonomous daemon — but the Execution Layer has never been given a component identity or an addressable
contract. Remoting execution cleanly requires exactly that.

Decision 0025 (Proposed) is the nearest prior art. Its finding 2 observed that "the spec has no
launch-governance seam for host-side work": Symphony "models host-side ops as behaviors, not
launches", so there is no wrapper/command indirection the orchestrator can interpose. Its Option C
proposed a host-side execution-wrapper seam — a "session resource domain" — to bring a session's
host-side work under one governable launch. This decision generalizes that finding: the missing seam
is not only about CPU weight, it is about *placement*. A session resource domain that can be governed
is one step from a session resource domain that can live on another machine.

## Options considered

- **Option A — Remote execution bolts on; core stays single-host.** Keep the in-process worker
  (Section 16.6) as the core execution path and add remote execution as an OPTIONAL, parallel path
  with its own code. Trade-offs: smallest blast radius on the existing spec and on Core Conformance.
  But it creates two execution shapes that duplicate the turn loop, prompt construction, broker use,
  and lifecycle hooks, and they will drift; every behavior added to core must be mirrored into the
  remote path or silently diverge. It also leaves Section 3.2's Execution Layer un-named as a
  component, so the "reworked remote-execution extension" 0004 anticipated has nowhere coherent to
  attach.

- **Option B — A first-class execution process behind an always-present seam.** Give the Execution
  Layer (Section 3.2) a component identity: the **execution process**, a specified, independently
  describable unit that owns everything the current worker does (workspace, object-store clone, the
  turn loop, prompt construction, the agent protocol, the broker, lifecycle hooks). Define one
  orchestrator↔executor seam that is **always present**: local execution is the degenerate
  **in-process transport** of that seam, and remote execution is the same seam over a network
  transport (decision 0036). One execution model; the node-scheduler (0037) is purely a placement +
  transport adapter behind it. Trade-offs: a real new component and a real new boundary to specify —
  it refactors Sections 3.1/3.2, 9, 10, and 16.6 so the worker becomes the executor. But there is
  exactly one execution path, local and remote cannot diverge, and the seam is the thing 0004 said a
  correct remote-execution story needs. This is 0027's Execution Layer made concrete.

- **Option C — Reconsider the split; find a lighter remote mechanism.** Treat a first-class executor
  as possibly over-engineered and look for a smaller remote-exec primitive before committing.
  Trade-offs: defers surface area, but the "lighter" mechanisms are the ones 0004 already rejected —
  they ship the agent without the boundary, or they re-introduce a second execution path (Option A).
  The design interview that produced this decision set walked the space and concluded the boundary
  and the component are irreducible once you require the sandbox + per-run broker socket + credential
  isolation to hold on the far side.

## Decision and reasoning

Accepted; **Option B** is the chosen direction. The execution process becomes a first-class
Symphony component and the orchestrator↔executor seam is always present, with local as the in-process
transport and remote as the network transport. The executor is the **execution layer of 0027 given a
component identity**: the same execution process runs the session whether in-process or on a node, so
the three topologies (daemon, interactive-agent, engine-direct) share **one execution process** rather
than three coincidentally-similar ones.

The unification is of the **component and the seam**, not of the wiring around them. The network
transport and direct secret delivery (0036), node-scheduler acquisition (0037), and
executor-authoritative writes (0038) are the **autonomous-daemon topology's** realization of that
wiring — they assume an orchestrator that dispatches, holds secrets, and reconciles. The
interactive-agent topology (broker core + `ship`/`land`) and the engine-direct topology (operator
holds secrets, no daemon) reuse the *same execution process* but supply their own initiator and
secret-sourcing per 0027; 0036–0038 do not re-specify those cases. So "one execution model" is a claim
about the execution process and its seam, scoped precisely: the process is shared, the surrounding
wiring is per-topology.

The reasoning is that a single execution model is the only way "as little as possible in Symphony"
survives contact with remote execution. Option A's duplication is not less Symphony — it is *more*,
paid twice and drifting. By making local the degenerate transport, the marginal cost of remote is the
transport and the placement adapter (0037), not a second executor. And the boundary that 0004
demanded — sandbox (Section 9.6), per-run broker socket (Section 10.8), credential-less agent (Section
15.3) — becomes a property the executor instantiates *wherever it runs*, so carrying it to a node is a
conformance requirement of the transport, not an afterthought bolted onto a fork.

This decision deliberately owns only the **component and the seam**. Three companions carry the rest,
so each stays independently reviewable: the wire **protocol** and secret delivery (0036), the
**node-scheduler adapter**, async acquire, failure classes, and the durable run registry (0037), and
the **state-writer reframing** — executor commits, orchestrator observes (0038). The four are a set
(like 0027–0032): 0036–0038 depend on this one.

What would make us reconsider: if refactoring the worker into a standalone component proves to leak
orchestrator-only concerns across the seam that cannot be cleanly serialized (0036's contract is where
that would surface), or if a measured deployment shows the in-process transport carries unacceptable
overhead versus today's direct call. Neither is expected — the worker is already close to standalone —
but both are checkable at 0036.

This decision relates to 0004 (reintroduces the deferred remote execution, carrying the boundary the
SSH extension lacked; does not change 0004's sandbox/broker guarantees), 0025 (generalizes its Option
C host-side launch seam from governance to placement — see 0025's forthcoming update), 0027 (the
executor is its Execution Layer given a component identity, shared across the three topologies, with
the daemon-topology wiring carried by 0036–0038), and 0003 (the broker whose per-run socket the
executor instantiates). It is the parent of 0036–0038.
