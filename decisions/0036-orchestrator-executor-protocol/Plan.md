# Plan — 0036 The orchestrator↔executor protocol and direct secret delivery

## Scope

Specifies the network transport of the orchestrator↔executor seam (decision 0035): the wire contract,
its direction and lifecycle semantics, direct secret delivery, and version negotiation. Affected
`SPEC.md` areas, by stable identity:

- Section 10 "Agent Runner Protocol" — a deferral note: the orchestrator↔executor protocol is its own
  versioned artifact `SPEC.md` defers to (as Section 10 already defers to the agent app-server
  protocol and 0028 defers to the `vcsx` contract). Reaffirm that the **agent protocol terminates on
  the executor**; the orchestrator sees only normalized events (Section 10.4), usage (Section 13.5),
  and outcome.
- Section 15.3 "Secret Handling" — extend the secret **channel**: the orchestrator resolves outward
  credentials (secret-provider interface) and delivers them to a remote executor over a
  mutually-authenticated channel; the agent-side invariant (never in the sandbox) is unchanged.
- Section 16.6 / Section 3.2 — the seam's up-channel (normalized events) is durably buffered on the
  executor with a sequence cursor and replayed from the orchestrator's last-ack on reconnect.
- A new companion **orchestrator↔executor protocol sub-spec** (external to `SPEC.md`, versioned), owning
  message schemas and framing; `SPEC.md` references it and does not restate schemas.

Out of scope: the node-scheduler adapter, the `provisioning` sub-state, failure classes, the run
registry, and reattach (decision 0037); executor-authoritative writes and broker relocation (decision
0038). This decision owns the contract and secret delivery only.

This decision is `Accepted`; edits are the planned end-state, applied as the 0035–0038 set and
batched with the companion protocol sub-spec so contract names stay identical across both documents
(mirroring 0028's lockstep with the `vcsx` spec).

## Steps

1. **`SPEC.md` defers to a versioned orchestrator↔executor protocol sub-spec.** In Section 10, add a
   deferral note stating that the wire contract between the orchestrator and a remote executor
   (message shape, framing, method names) is defined by its own versioned protocol document, which the
   implementation MUST consult; `SPEC.md` owns orchestration semantics (what crosses the seam, when,
   and the secret/isolation rules) and does not restate the schema. Done-condition: Section 10 names
   the sub-spec as the source of truth for the orchestrator↔executor wire shape, parallel to its
   existing agent-protocol deferral, with no schema inlined.

2. **The agent protocol terminates on the executor.** State (Section 10) that when the executor is
   remote it speaks the targeted agent's app-server protocol locally and the orchestrator is never in
   agent communication; the orchestrator receives only normalized runtime events (Section 10.4), token
   usage (Section 13.5), and the run outcome. Done-condition: the spec makes explicit that raw
   agent-protocol traffic does not cross the orchestrator↔executor seam.

3. **The down-channel run-spec is defined at semantic altitude.** State what the orchestrator sends to
   start a run: normalized issue data (Section 11.3), the workflow template (Section 5), agent/effort
   selection (Section 10.9), `max_turns`, a wall-clock bound (enforced by the executor — decision
   0037), and `continuation_ref` (Section 10.7, for resume) — plus the run's secrets (Step 5) and,
   while connected, live tracker updates limited to terminal/cancel (decisions 0037/0038).
   Done-condition: the run-spec's contents are enumerated by role at spec altitude, with schema left
   to the sub-spec.

4. **The up-channel is defined, buffered, and replayable.** State that the executor streams normalized
   runtime events (Section 10.4), usage (Section 13.5), the outcome, and committed-state notifications
   (decision 0038); events carry a monotonic sequence cursor, are durably buffered on the executor,
   and are replayed from the orchestrator's last-acknowledged position on reconnect so no event or
   token-usage increment is lost across an orchestrator disconnect. On a **mid-run** drop (the
   orchestrator still alive) it reconnects to the executor's **known endpoint**; if that endpoint is
   stale (e.g. the node moved) it re-addresses via the node-scheduler's `lookup_by_run_id` (decision
   0037). The executor **continues the run autonomously** through the disconnect — it owns completion
   (decisions 0031/0038) — so a reconnect resumes a still-live run rather than restarting work. The
   orchestrator owns the durable usage ledger (Section 13.6); the executor is the emitter.
   Done-condition: the up-channel names its
   payloads and specifies buffer + ack-cursor + replay semantics guaranteeing gap-free observability
   across reconnect.

5. **Direct, mutually-authenticated secret delivery (Section 15.3).** Extend Section 15.3: for a
   remote executor, the orchestrator resolves outward credentials through the secret-provider
   interface and delivers them **directly to the executor** (never through the node-scheduler) over a
   channel secured by **scheduler-bootstrapped mutual auth** — the node-scheduler (decision 0037)
   provisions one-time trust material the executor presents and the orchestrator verifies (mutual
   TLS), enabling trust without seeing the secret. The agent-side invariant is unchanged: the secret
   reaches the executor's broker context only, never its sandbox (Sections 9.6, 15.3; decision 0003).
   Done-condition: Section 15.3 describes the direct secret channel and its mutual-auth bootstrap,
   states the scheduler is out of the secret path, and reaffirms the sandbox never receives the
   secret.

6. **Version negotiation with a minimum-supported floor.** State that the executor advertises its
   protocol version at bring-up; the orchestrator negotiates a mutually-supported version and
   **refuses, fail-closed, below a documented minimum floor** (a stale warm-node image fails cleanly
   at bring-up rather than mis-parsing mid-run). The exact version grammar lives in the sub-spec.
   Done-condition: the spec requires bring-up version negotiation with a fail-closed minimum floor,
   deferring the version grammar to the sub-spec.

## Cross-cutting sync

- **Section 6.4 (config cheat sheet):** no change here; the `compute.*` selector and its keys are
  introduced by decision 0037. (If the protocol sub-spec pin needs a config surface, 0037's `compute.*`
  namespace is its home, not a new top-level key here.)
- **Section 17 (test matrix):** add Extension rows — agent-protocol traffic never crosses the seam;
  events replay gap-free from last-ack after an orchestrator disconnect; secret delivery is direct and
  mutually authenticated with the scheduler out of the path; a below-floor executor version is refused
  fail-closed at bring-up.
- **Section 18 (implementation checklist):** add an Extension line for the orchestrator↔executor
  protocol: versioned sub-spec deferral, agent protocol terminating on the executor, buffered+replayed
  up-channel, direct mutual-auth secret delivery, and min-floor version negotiation.

## Anchor changes

New anchors introduced (no renames/removals):

- Concept **orchestrator↔executor protocol** (the versioned sub-spec `SPEC.md` defers to; Section 10).
- Concept **run-spec** (the down-channel start-of-run payload).
- Secret-channel extension in Section 15.3 (direct delivery to a remote executor; mutual-auth
  bootstrap). No existing Section 15.3 invariant is renamed or removed — the agent-side scrub/never-in-
  sandbox rule is preserved and extended by channel.

No code-token or section-title anchor is renamed or removed. Any section renumbering is expected to
come from 0037 (the `provisioning` sub-state) rather than this decision.

## Status

Applied to `SPEC.md`. Section 10 gains the orchestrator↔executor protocol block (agent protocol
terminates on the executor; run-spec down / normalized events up; buffered-and-replayed up-channel;
min-floor version negotiation), and Section 15.3 gains direct, mutually-authenticated secret delivery
to a remote executor with the node-scheduler off the secret path.

Deviation: the versioned protocol sub-spec is referenced as a forward external document and is not yet
authored; `SPEC.md` defers to it in prose, mirroring the existing agent-protocol deferral (Section 10)
and 0028's `vcsx`-contract deferral.
