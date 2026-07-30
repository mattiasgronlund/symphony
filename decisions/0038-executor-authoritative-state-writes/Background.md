# Background — 0038 Executor-authoritative writes and the driver-local / reconciler-remote reframing

## Context

Decisions 0035–0037 place a first-class executor behind an always-present seam, give it a wire
protocol with direct secret delivery, and let the orchestrator acquire it from a node-scheduler. This
decision resolves the consequence those three force but do not settle: once the executor runs the
whole session on a node — building prompts, running the turn loop, computing completion, and holding
the only credential path to git/forge — **who writes the authoritative record of the run**, and what
that does to the orchestration state machine.

The design interview settled the allocation deliberately. The executor runs the whole loop
autonomously and owns completion, because the signals that decide "is this done" — turn count, and
"has the work progressed" (decision 0031's computed completion) — live where the agent runs, not in
the orchestrator. The executor already holds the repository (it cloned it, 0037) and the credentials
(delivered directly, 0036), so the repo-owned Way of Working (decision 0029, `repo.policy.toml` read
from the protected base revision) and the action-policy machine that runs it (decision 0030) execute
**on the executor**. Given all that, the executor is also the natural place to **commit** the
run's outcome: open the pull request through its on-node broker, and set the tracker state through the
action-policy machine's `set_state` action. The alternative — stream every outcome back and have the
orchestrator re-commit — puts the orchestrator back in the run's internals it was just removed from,
and splits a single logical completion ("done on the forge" and "done in the tracker") across two
processes and a round-trip.

Two structural facts make "executor commits, orchestrator observes" less of a break than it first
appears:

1. **The orchestrator already reconciles rather than owns.** Section 7's state machine is not the sole
   author of issue state even today: humans edit tickets, and Section 8.5 already reconciles the
   tracker's live state against the orchestrator's view every tick (terminating workers whose issue
   went terminal). The orchestrator has always had to treat the tracker as a shared ledger it observes,
   not a variable it exclusively writes. Making the executor an authoritative writer for an in-flight
   run extends a reconciliation the orchestrator already performs; it does not invent one.

2. **The broker moves, the invariant does not.** Decisions 0003/0004 put all credentialed operations
   behind a per-run broker socket so the agent never holds secrets. With a remote executor the broker
   **instance** runs on the node (fed by directly-delivered secrets, 0036), but the invariant is
   identical: the agent's sandbox never holds credentials; the broker mediates. Git/forge writes
   (Sections 9.8–9.10) are **executor-exclusive** — only the executor's broker has the VCS/forge
   credential path. Tracker read/write, by contrast, is **shared**: the orchestrator already holds
   tracker credentials to poll (Section 8.1) and may write state; the executor may also read and write
   the tracker (to set state, post comments, resolve `escalate`). Tracker access on both sides is what
   makes the reconciler model coherent — both parties can read the shared ledger, and either can write
   it under the action-policy contract.

Two edges need explicit handling under this model:

- **`escalate` has no human in front of the executor.** Decision 0030's abstract `escalate` action
  binds per front-end; the daemon front-end has no interactive operator at the executor. The executor
  resolves `escalate` by **writing the tracker** (a comment / a blocked state), which the orchestrator
  observes on reconcile — consistent with "executor commits, orchestrator observes" and needing no new
  up-channel message type for the common case.

- **An issue can go terminal mid-run.** The executor does not poll; the orchestrator does (Section
  8.1). While the seam is connected the orchestrator forwards the terminal/cancel signal on the live
  down-channel (limited to terminal/cancel — decision 0036), and the executor stops. While the seam is
  **disconnected**, the executor keeps running the loop autonomously (it owns completion — decision
  0031) and cannot be told — so before finalizing any git/forge/tracker write it **re-checks tracker
  state** (which it can read) and aborts if terminal, so it never pushes for a closed issue. The
  re-check is the disconnected-path guard; the forwarded signal is the connected path. Neither requires the orchestrator to drive the run.

## Options considered

- **Who commits the terminal transition — executor commits / orchestrator observes (chosen) vs.
  executor proposes / orchestrator commits vs. keep orchestrator sole writer.** Executor-commits makes
  the run self-contained: the action-policy machine (0030) runs on the node and sets state / opens the
  PR / posts comments, and the orchestrator reconciles from the tracker. It is the most coherent with
  0029–0031 running on the executor, at the cost that the orchestrator is no longer the single writer.
  Executor-proposes keeps a single writer and a central state machine but re-inserts a round-trip and
  splits "PR by executor, state by orchestrator". Keeping the orchestrator as sole writer contradicts
  the whole executor-owns-the-run direction and re-centralizes the policy machine. Executor-commits was
  chosen because the reconciler model is already true (humans edit tickets; Section 8.5 reconciles) and
  the split-writer alternative fights the layering rather than using it.

- **Terminal-mid-run guard — forward-while-connected + self-check-while-disconnected (chosen) vs.
  best-effort orchestrator cancel only vs. always self-check.** The hybrid uses the cheap path when
  available (the orchestrator is already polling, so forward the terminal signal) and the safe path
  when not (the executor reads the tracker before finalizing). Cancel-only lets a disconnected run
  complete and push for a closed issue. Always-self-check adds a tracker read at every finalize even
  when the orchestrator could just have said "stop". The hybrid matches mechanism to whether the seam
  is up.

- **`escalate` routing — executor writes tracker (chosen) vs. escalate crosses the seam up vs. both by
  kind.** Writing the tracker keeps escalation on the shared ledger the orchestrator already observes,
  with no new message type; it is only as visible as the tracker write, which for the daemon front-end
  is exactly where a human would look. Routing escalate up centralizes it but re-couples the
  orchestrator to run internals. Both-by-kind is the general form but adds classification the common
  case does not need; it stays available if a future front-end needs a non-tracker escalation.

## Decision and reasoning

Accepted; the chosen directions are executor-commits / orchestrator-observes, the broker on the
executor with executor-exclusive git/forge and shared tracker access, the connected-forward /
disconnected-self-check terminal guard, and `escalate` resolved by an executor tracker write. Section
7 is reframed as **driver-local / reconciler-remote**: the orchestrator drives dispatch and candidate
selection, but for an in-flight run the executor is the authoritative writer and the orchestrator
reconciles its view from the tracker.

The reasoning is that this is the honest description of where authority already sits once 0035–0037
land. The executor holds the repo, the credentials, the agent, the policy machine (0030), and the
completion computation (0031); making it the writer of the run's outcome removes a round-trip and a
split commit rather than adding risk, because the orchestrator was never the tracker's sole writer —
Section 8.5 reconciliation and human ticket edits already made it an observer of a shared ledger. The
broker relocation carries the 0003/0004 invariant unchanged: the credential path is the executor's
broker, the agent sandbox holds nothing. Keeping git/forge executor-exclusive while sharing tracker
access falls directly out of who holds which credential — VCS/forge creds are delivered only to the
executor (0036), tracker creds are already on the orchestrator for polling and may be on the executor
too.

Batching note: decisions 0029–0031's own `SPEC.md` edits are deferred (they forward-reference a
companion `vcsx` spec, per 0028). This decision's edits — which relocate the action-policy machine's
execution onto the executor and reframe Section 7 around it — are therefore applied **in step with**
those edits, so the spec never names the action-policy machine or `repo.policy.toml` before they
exist (the same deferral discipline decision 0034 followed for the `vcsx`/broker-core vocabulary).

What would make us reconsider: if reconciling an executor-committed transition against a
concurrently-human-edited ticket produces conflicts the action-policy machine cannot resolve cleanly,
the single-writer alternative (executor proposes, orchestrator commits) is the fallback — but the same
conflict already exists today between the orchestrator and human editors, so the executor does not add
a new class of it.

This decision relates to 0003/0004 (the broker invariant, preserved with the broker instance on the
executor), 0017 (`tracker.transitions` → the action-policy `set_state` binding, now committed by the
executor), 0021 (`set_state` write semantics, executed by the executor's tracker access), 0029 (the
repo-owned WoW the executor reads from base), 0030 (the action-policy machine, now running on the
executor; `escalate` resolved by a tracker write), 0031 (computed completion on the executor), 0035
(the executor component), 0036 (the terminal/cancel down-channel and committed-state up-notifications),
and 0037 (acquisition; the executor's node context). Depends on 0035, 0036, 0037.
