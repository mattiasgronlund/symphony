# Plan — 0038 Executor-authoritative writes and the driver-local / reconciler-remote reframing

## Scope

Reframes state authority for a remote run and relocates the broker onto the executor. Affected
`SPEC.md` areas, by stable identity:

- Section 7 "Orchestration State Machine" — reframe as **driver-local / reconciler-remote**: the
  orchestrator drives dispatch/candidate selection; for an in-flight run the executor is the
  authoritative writer and the orchestrator reconciles from the tracker. (Decision 0037 also edits
  Section 7 — the `provisioning` acquire sub-state; the two Section 7 edits are complementary and
  applied together.)
- Section 10.8 "Privileged Operation Broker" and Sections 9.8–9.10 (git verbs, broker git verbs, forge
  writes) — the broker instance runs on the executor; git/forge writes are **executor-exclusive**.
- Sections 11.5 "Tracker Writes (Broker Boundary)" and 11.8 "State Transition Write Semantics" —
  tracker read/write is **shared**: both orchestrator and executor may read and write; the executor
  commits `set_state` and comments through its tracker access.
- Section 8.5 "Active Run Reconciliation" — the connected-forward / disconnected-self-check terminal
  guard; the orchestrator forwards terminal/cancel over the seam while connected (decision 0036); the
  executor re-checks tracker state before finalizing writes while disconnected.
- Cross-refs to the action-policy machine (decision 0030) and computed completion (decision 0031),
  whose execution now sits on the executor.

Out of scope: the component/seam (0035), the wire protocol/secret delivery (0036), and the
node-scheduler adapter/failure model/registry (0037). This decision owns write authority, broker
placement, and the terminal-mid-run guard.

This decision is `Accepted`. Because decisions 0029–0031's own `SPEC.md` edits are deferred (they
forward-reference the companion `vcsx` spec per 0028), this decision's edits are applied **in step
with** those, so the action-policy machine and `repo.policy.toml` are never named before they exist
(mirroring decision 0034's deferral of `vcsx`/broker-core vocabulary).

## Steps

1. **Section 7 reads driver-local / reconciler-remote.** State that the orchestrator drives dispatch
   and candidate selection, but for an in-flight run the executor is the authoritative writer of the
   run's outcome and the orchestrator **reconciles** its view from the tracker (as it already does for
   human ticket edits and in Section 8.5). Done-condition: Section 7 distinguishes the orchestrator's
   driving role (dispatch/selection) from its reconciling role (in-flight run state), and names the
   executor as the authoritative writer for a running issue.

2. **The broker runs on the executor; git/forge writes are executor-exclusive.** State (Sections 10.8,
   9.8–9.10) that the per-run broker socket and the credentialed git/forge operations run in the
   executor's context (in-process locally; on the node remotely), fed by the run's secrets (decision
   0036), with the agent's sandbox holding no credentials (Sections 9.6, 15.3; decisions 0003/0004).
   Only the executor's broker has the VCS/forge credential path. Done-condition: the broker is
   attributed to the executor, git/forge writes are executor-exclusive, and the credential-less-agent
   invariant is restated as preserved wherever the executor runs.

3. **Tracker read/write is shared (Sections 11.5, 11.8).** State that both the orchestrator (which
   holds tracker credentials to poll, Section 8.1) and the executor may read and write the tracker; the
   executor commits `set_state` (decision 0021) and comments through its tracker access as the
   action-policy machine (decision 0030) directs. Done-condition: Sections 11.5/11.8 permit tracker
   writes from both the orchestrator and the executor, and name the executor as the committer of a
   remote run's state transitions.

4. **The executor commits; the action-policy machine runs on the executor.** State that the
   action-policy machine (decision 0030), reading the repo-owned WoW from the base revision (decision
   0029), executes on the executor: it opens the pull request (executor broker), sets tracker state
   (shared tracker access), and posts comments. The orchestrator observes the results on reconcile.
   Done-condition: the spec places action-policy execution on the executor and describes the
   orchestrator as observing committed results, applied in step with the 0029–0031 edits.

5. **`escalate` is resolved by an executor tracker write.** State that the daemon front-end's abstract
   `escalate` action (decision 0030) is resolved by the executor writing the tracker (a comment / a
   blocked state), which the orchestrator observes on reconcile — no dedicated up-channel escalate
   message for the common case (the both-by-kind generalization stays available for a future non-tracker
   front-end). Done-condition: the spec routes daemon `escalate` to an executor tracker write and notes
   the orchestrator observes it on reconcile.

6. **Terminal-mid-run guard (Section 8.5).** State the hybrid: while the seam is connected the
   orchestrator forwards the terminal/cancel signal on the live down-channel (decision 0036) and the
   executor stops; while disconnected the executor re-checks tracker state before finalizing any
   git/forge/tracker write and aborts if terminal, so it never pushes for a closed issue. Done-condition:
   Section 8.5 specifies forward-while-connected and self-check-while-disconnected, and neither path
   requires the orchestrator to drive the run.

## Cross-cutting sync

- **Section 6.4 (config cheat sheet):** no new config key (write authority and broker placement are
  behavioral, not configured). The `compute.*` selector that gates local vs remote is 0037's.
- **Section 17 (test matrix):** add rows — a remote run's terminal transition and PR are committed by
  the executor and observed by the orchestrator on reconcile; git/forge writes never originate from the
  orchestrator in remote mode; a terminal issue stops a connected run via forwarded signal and a
  disconnected run via the executor's pre-finalize re-check; `escalate` surfaces as an executor tracker
  write.
- **Section 18 (implementation checklist):** add lines — Section 7 driver-local/reconciler-remote;
  broker on the executor with executor-exclusive git/forge and shared tracker access; the
  terminal-mid-run guard; `escalate`-via-tracker.

## Anchor changes

Reframings (no code-token removals):

- Section 7's state machine is reframed to driver-local / reconciler-remote (title may stay; the role
  split is prose). Recorded so later plans citing "the orchestrator owns issue state" resolve to the
  reconciler model for in-flight remote runs.
- The **broker** (Section 10.8) is attributed to the executor's context; no rename.
- Tracker-write permission (Sections 11.5/11.8) broadens from orchestrator to orchestrator+executor;
  no code-token rename.

No section-title or code-token anchor is renamed or removed. Section-number impact is expected to be
nil (edits are within existing sections); any renumbering from 0037's insertions is tracked in 0037.

## Status

Applied to `SPEC.md`. Section 7 distinguishes orchestrator-owned scheduling state from the shared
tracker ledger (the executor writes tracker state in-flight; the orchestrator reconciles); Section 10.8
gains the *Broker location* block (broker in the executor; git/forge executor-exclusive, tracker
shared); Section 11.5 states the shared tracker-write ledger and the escalation path; Section 8.5 gains
the connected-forward / disconnected-self-check terminal guard.

Deviation (per the 0034 precedent): the action-policy machine (0030) and repo-owned WoW from base
(0029) are not named in `SPEC.md`, since their spec edits are deferred. "Executor commits" is expressed
through the existing broker tracker writes (Section 11.5), the transition graph (Section 11.6), and
`set_state` semantics (Section 11.8); the abstract `escalate` is expressed through the existing
`blocked` milestone signal (Section 11.6). To be reconciled when the 0029/0030 edits land.
