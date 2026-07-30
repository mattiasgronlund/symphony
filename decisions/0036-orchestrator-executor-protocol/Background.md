# Background — 0036 The orchestrator↔executor protocol and direct secret delivery

## Context

Decision 0035 makes the execution process a first-class component and the orchestrator↔executor seam
always present, with local execution as the in-process transport. This decision specifies the seam's
**network transport** — the wire contract the orchestrator and a remote executor speak — and the one
thing that contract must carry that the local transport got for free: the run's secrets, delivered so
the boundary decision 0004 required actually reaches the far side.

In-process (0035) the seam is a function call over an in-memory `orchestrator_channel` (Section 16.6);
serialization, authentication, and secret handling are non-issues. Across a network they are the whole
problem. Three shaping facts come from the design interview:

1. **The agent protocol terminates on the executor.** Section 10 already defers agent-protocol shape,
   framing, and method names to the targeted agent's app-server protocol as the source of truth, and
   requires implementations to consult that protocol rather than this spec. When the executor is
   remote, the executor is what speaks that protocol — locally, on the node. The orchestrator MUST NOT
   be in agent communication: it dispatches a run and receives Symphony's *normalized* runtime events
   (Section 10.4), token usage (Section 13.5), and the outcome. Keeping the agent protocol on the node
   preserves Section 10's deference boundary unchanged and keeps the orchestrator↔executor contract
   agent-neutral.

2. **Secrets are delivered orchestrator→executor directly.** The node-scheduler (0037) provisions and
   deploys nodes but is deliberately **not** in the secret path. The orchestrator resolves outward
   credentials through the secret-provider interface (Section 15.3) and hands them to the executor
   over the seam, so the executor's on-node broker (0038) can perform credentialed git/forge
   operations while the agent stays credential-less (Section 15.3, decision 0003). Section 15.3 today
   assumes host-side secret resolution and scrubs secret-bearing variables before the sandbox starts;
   this decision extends the *channel* (a secret now transits the seam to a remote executor) while
   preserving the *invariant* (the agent never holds it, wherever the executor runs — 0035 Step 3).

3. **The two halves may version-skew.** The executor is an independently deployable component (0035),
   and a node image can lag the orchestrator (a warm node built against an older release). The
   contract must degrade safely under skew rather than mis-parse.

Where to specify the protocol has a settled precedent. Section 10 defers agent-protocol shape to the
external app-server protocol; decision 0028 defers `vcsx` mechanics to the `vcsx` **contract**,
"mirroring the existing Codex-app-server-protocol deferral so the spec stays language-agnostic." The
orchestrator↔executor protocol is the same kind of artifact: a wire contract with message schemas and
transport framing that would drag `SPEC.md` below its altitude if inlined.

## Options considered

- **Option A — Inline the protocol in `SPEC.md`.** Specify messages, directions, framing, and
  lifecycle directly in the spec's language-agnostic prose. Trade-offs: one artifact, nothing external
  to track. But it pushes `SPEC.md` to wire-level detail it has consistently avoided (it defers both
  the agent protocol and the `vcsx` contract for exactly this reason), and a schema maintained as
  prose drifts from any generated/validated form.

- **Option B — Its own versioned sub-spec that `SPEC.md` defers to.** Define the orchestrator↔executor
  protocol in a dedicated, versioned document; `SPEC.md` owns orchestration semantics (what crosses
  the seam and when, secret-delivery rules, the secret-isolation invariant) and **references** the
  sub-spec for message shape and framing — exactly as Section 10 defers to the agent protocol and 0028
  to the `vcsx` contract. Version is **negotiated with a documented minimum-supported floor**; the
  executor advertises its protocol version at bring-up and the orchestrator refuses (fail-closed)
  below the floor. Trade-offs: a second source-of-truth document to keep in lockstep (the same cost
  0028 accepted for `vcsx`). But it keeps `SPEC.md` at altitude, makes the schema a first-class
  versioned artifact, and the min-floor negotiation turns silent skew into a clean bring-up refusal.

- **Option C — Inline the neutral contract; external concrete schema.** State message names, directions,
  and lifecycle in `SPEC.md`; put the concrete schema/transport in an external generated artifact.
  Trade-offs: a middle path, but it splits the protocol's definition across two homes with no single
  owner of the contract — the failure mode 0028 avoided by deferring the *whole* contract to one place.

## Decision and reasoning

Accepted; **Option B** is the chosen direction. The orchestrator↔executor protocol is specified
as its own versioned sub-spec that `SPEC.md` defers to, mirroring the Section 10 agent-protocol and
0028 `vcsx`-contract deferrals; the protocol version is negotiated with a documented minimum floor and
the orchestrator fails closed below it.

The contract carries, by direction:

- **Down (orchestrator → executor):** the **run-spec** — normalized issue data (Section 11.3), the
  workflow template (Section 5, prompt body + in-sandbox hooks), agent/effort selection (Section
  10.9), `max_turns`, a wall-clock bound (the paying orchestrator sets it; the executor enforces —
  0037), and `continuation_ref` for resume (Section 10.7) — plus the run's **secrets**, and, while
  connected, **live tracker updates limited to terminal/cancel** (the executor self-guards on
  disconnect — 0038, 0037).
- **Up (executor → orchestrator):** **normalized runtime events** (Section 10.4), **token usage**
  (Section 13.5), the run **outcome**, and **committed-state notifications** (the executor commits
  tracker/forge writes and reports them — 0038). Events are **durably buffered on the executor with a
  sequence cursor and replayed** from the orchestrator's last acknowledged position on reconnect, so
  an orchestrator disconnect leaves no gap in the event log or in token accounting (Sections 13.5,
  13.6). The orchestrator owns the durable usage ledger; the executor is the emitter.

Secret delivery is direct and mutually authenticated. The orchestrator resolves secrets via Section
15.3 and sends them to the executor over a channel secured by **scheduler-bootstrapped mutual auth**:
the node-scheduler (0037) provisions one-time trust material the executor presents and the
orchestrator verifies (mutual TLS), so the scheduler *enables* trust without ever *seeing* the
secrets. The agent-side invariant is unchanged — the executor's sandbox never receives the secret
(Section 15.3, 0035 Step 3); only the executor's broker context does.

The reasoning for deferral over inlining is continuity: `SPEC.md` already draws its altitude line at
"defer protocol shape, own the semantics" twice (Section 10, 0028). Doing the same here keeps the spec
language-agnostic and gives the wire contract a versioned home where a generated schema can live.
Min-floor negotiation is chosen over strict-match because warm-node reuse (0037) makes benign skew
routine; a hard version equality would fail every run against a slightly-stale image, whereas a floor
lets compatible versions interoperate and turns a genuinely incompatible image into an explicit,
fail-closed bring-up error rather than a mis-parsed message mid-run.

What would make us reconsider: if the run-spec cannot be cleanly serialized because it carries an
orchestrator-only object that resists a neutral encoding, the seam abstraction (0035) is leaking and
the contract is where that surfaces — the fix would be to narrow what crosses, not to widen the
schema. And if a generated schema artifact never materializes, Option C's "inline neutral contract"
becomes the pragmatic fallback for the message list while keeping framing external.

This decision relates to 0004 (delivers the boundary the SSH extension lacked, now as a secret-channel
+ isolation contract), 0035 (specifies that decision's seam over the network transport), 0037 (the
node-scheduler bootstraps the mutual-auth trust material and is kept out of the secret path; wall-clock
bound and terminal/cancel updates originate there), 0038 (the executor's committed-state
notifications and on-node broker are what the secrets feed), 0028 (the deferral pattern this reuses),
0003 (the credential-broker invariant preserved end-to-end), and Section 15.3 (the secret-provider
interface extended by channel, not by invariant). Depends on 0035.
