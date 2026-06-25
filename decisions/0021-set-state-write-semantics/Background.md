# Background — 0021 set_state write semantics

## Context

Section 11.1 lists `set_state(issue_id, target_state)` but says nothing about how it must behave. The
22-fork tracker sweep (0008 `Background.md`; `adapter-layer-fork-evidence` memory) showed `set_state` is the
write that diverges most from a plain field assignment, in three concrete ways the spec never named:

- **Idempotency (Jira).** Jira applies a state change as a *workflow transition*, and re-applying a
  transition already taken is illegal. The wagnersza adapter therefore short-circuits: if the issue is
  already in the target status it returns success without POSTing a transition. Without this rule, a
  retried or duplicate `set_state` errors on Jira.
- **Unreachable target (Jira).** A target the current state has no transition to yields
  `{:error, {:transition_not_found, state}}`. A `set_state(name)` that cannot be satisfied must fail, not
  silently succeed.
- **Concurrency (GitLab) and verification (GitHub).** GitLab has no `If-Match`, so issuepilot built an
  optimistic-lock label transition (`requireCurrent`, re-read verify) that raises `claim_conflict` when the
  state moved underneath the write. GitHub applies state as several eventually-consistent label writes, so
  abhijith verifies read-after-write (`state_label_verification_failed`).

Decision 0008/0017 already settled the altitude: the caller names a target *state*, the adapter resolves the
mechanism (status field / transition / label set). This decision specifies the obligations that altitude
implies, without lifting transition mechanics into the contract.

## Options considered

- **Leave `set_state` unspecified.** Rejected: adapters reinvent the semantics inconsistently, and the
  load-bearing "already-in-target is success" rule (without which Jira errors) would be left to chance.
- **Add transition primitives (`apply_transition`, transition payloads) to the contract.** Rejected: 0017
  deliberately kept `set_state(target)` as the verb; transition ids and screens stay inside the adapter.
- **Specify `set_state` obligations plus two typed outcomes (chosen):** idempotent no-op,
  `tracker_state_unreachable`, `tracker_state_conflict`, a SHOULD-verify rule, and an
  `Implementation-defined` escape for transitions that require extra input.

## Decision and reasoning

Add Section 11.8 "State Transition Write Semantics" requiring of `set_state`:

- **Idempotent**: already in `target_state` ⇒ successful no-op; the adapter MUST NOT re-apply a transition
  (some trackers reject re-applying one already taken).
- **Unreachable target** ⇒ fail with `tracker_state_unreachable` (new, Section 11.4) rather than silently
  succeeding.
- **Concurrent change** (state moved underneath the write) ⇒ fail with `tracker_state_conflict` (new,
  Section 11.4); the orchestrator re-reconciles from the tracker next tick rather than blindly retrying.
- **Verification**: where state is applied through several eventually-consistent writes, the adapter SHOULD
  confirm the result and surface a failure if it did not take.
- **Required transition input** (for example a Jira transition screen): `set_state` cannot express it; the
  adapter supplies a documented default or fails — `Implementation-defined`.

A `set_state` failure is logged and does not by itself fail the run: the agent's work is already done and
the transition is a side effect the orchestrator reconciles (Section 8.5).

Reasoning: this makes the write contract honest about the three real ways `set_state` differs from a field
write, gives the orchestrator typed outcomes to reason about (`tracker_state_unreachable` is a workflow/
config problem; `tracker_state_conflict` is a reconcile trigger), and preserves the `set_state(target)`
altitude 0008/0017 chose.

Problems to watch: verification is SHOULD, not MUST, so trackers with an atomic state field are not forced
into a needless read-after-write; required-transition-input stays `Implementation-defined` instead of adding
a payload parameter, which would re-introduce the `apply_transition` complexity 0017 avoided.
