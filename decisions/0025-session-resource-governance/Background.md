# Background — 0025 Session resource governance and the host-side launch seam

## Context

A handoff from the operator of an `Identione/symphony` deployment reports CPU congestion under
concurrent sessions. Measured on the VPS, concurrent build/test gate runs are hard CPU-bound (CPU
stall 3 -> 18 -> 62 -> 89% at concurrency 1 -> 2 -> 4 -> 8; memory and disk are non-issues). The
observed process tree is Symphony -> per-session agent process -> coding-agent CLI -> build/test gate
(`mise run check` -> cargo/rustc). The operator wants per-session CPU *fairness* — work-conserving
weights, not quotas, so a lone session still saturates the box — governed from the Symphony side, with
a per-host enable flag that no-ops on dev laptops, CI, and non-systemd hosts.

The question for this repo is narrow: does `SPEC.md` need a new mechanism, and if so where does it
attach? Two findings from mapping the brief onto the spec:

1. **The agent's CPU-bound work runs inside the sandbox.** Section 9.6 already requires each agent run
   to be runnable inside a configurable, `Implementation-defined` sandbox (reference baseline `jai` in
   `Strict` mode). The sandbox launch is therefore the already-present attach point for a per-session
   cgroup / CPU weight: an operator wraps the sandbox invocation (for example a systemd transient
   scope under a shared parent slice) without Symphony defining anything new. The agent-side
   requirement is already satisfied by the existing sandbox-wrap contract.

2. **The spec has no launch-governance seam for host-side work.** Symphony performs repository
   provisioning and `git fetch` (Section 9.7), branch / back-merge / push (Section 9.8) behind the
   broker git verbs (Section 9.9), worktree provisioning and `attempt_clean_backmerge` (Section 16.5),
   and host-side policy-config hooks `after_create` / `before_run` / … (Sections 9.4, 15.4) — all
   *outside* the sandbox, in the orchestrator's own process context. The spec describes these as
   behaviors ("Symphony performs fetch/push on the host"), never as launches with a wrapper or command
   indirection. The only host-side launch with an explicit execution contract is workspace hooks
   (Section 9.4: `sh -lc` / `bash -lc` + `hooks.timeout_ms`), and even that carries no governance hook.

Consequence: host-side per-session subprocesses are children of the long-lived orchestrator process,
so they inherit the *orchestrator's* cgroup, not the session's. Even a perfect per-session sandbox
cgroup does not reach the brief's "whole-subtree coverage" goal — host-side VCS and policy hooks for a
session escape that session's weight. Magnitude is uneven: fetch / merge / worktree are mostly
network- and IO-bound and bounded; the genuinely CPU-heavy host-side path is operator build/install
hooks (for example `after_create` warming a build cache or installing dependencies), which under K
concurrent sessions contend much like the in-sandbox gate runs.

A separable concern in the same brief — propagating a curated set of *non-secret* gate-control
environment variables (`ENTRY_CHECK_JOBS` / `_LOAD` / `_SLOTS` / `_DIR`) into the session so the gate's
cap and `-j`/`-l` settings actually apply — is out of scope here. It touches the Section 15.3
secret-scrubbing invariant: the spec scrubs every secret-bearing variable before the sandbox starts
but has no positive mechanism to inject a non-secret allowlist into the sandbox. That is a candidate
for its own later decision, not this one.

## Options considered

- **Option A — Status quo; governance is wholly a deployment concern, spec silent.** The agent's gate
  runs are inside the sandbox, so an operator attaches a cgroup / weight by wrapping the
  `Implementation-defined` sandbox launch (Section 9.6); host-side VCS and hooks are governed by
  putting the whole Symphony service in a slice at the service-manager level. Trade-offs: simplest,
  maximally framework-neutral, nothing to maintain. But it leaves the host-side seam gap undocumented,
  so an implementer aiming for per-session fairness discovers only by inspection that host-side work
  escapes the session weight; the "whole-subtree per-session" goal is silently unreachable.

- **Option B — Clarifying note only.** Add an OPTIONAL note (near Section 9.6) that the
  sandbox launch is the per-session resource-governance attach point: a deployment MAY place the
  agent's sandboxed process tree in its own cgroup with a configurable, work-conserving weight under a
  shared parent, `Implementation-defined` and no-op where cgroup-v2 / delegation is absent, never
  granting the sandbox any new privilege (Sections 9.6, 15.3). State explicitly that this governs the
  agent subtree only; host-side VCS operations (Sections 9.7–9.9) and policy-config hooks (Section
  9.4) run in the orchestrator's context and are governed at the service/orchestrator level, not per
  session. Trade-offs: low-cost and honest; sets expectations and names the gap without inventing a
  mechanism; preserves neutrality. Does not close the host-side tail, but makes it explicit by design.

- **Option C — Introduce an OPTIONAL host-side execution-wrapper seam ("session resource domain").**
  Define an OPTIONAL construct so host-side per-session work (broker git verbs, policy-config hooks)
  and the agent sandbox can share one per-session cgroup / weight. This requires modeling host-side
  operations as per-session-attributable launches that the orchestrator can place into the session's
  resource domain (a launch-wrapper indirection), plus a per-host config block (enable flag, parent
  slice, per-session weight, optional collective reserve), all work-conserving, no-op fallback,
  host-side only. Trade-offs: actually achieves whole-subtree per-session fairness — but it is the
  largest change, introducing an execution abstraction the spec deliberately avoided (it models
  host-side ops as behaviors, not launches), and risks over-specifying a concern whose dominant cost
  (the in-sandbox gate run) is already coverable. The host-side CPU cost that motivates it (concurrent
  build hooks) is real but secondary and not yet measured in isolation.

## Decision and reasoning

Proposed; **no option selected**. The operator does not need a decision yet, so this decision records
the finding only and does not endorse an option. The finding has two halves:

- The agent-side answer is already settled by an existing contract: the sandbox-wrap (Section 9.6) is
  the per-session attach point for the CPU-bound gate run, and needs no new mechanism.
- The open question is host-side: VCS operations and policy-config hooks run in the orchestrator's
  process context with no per-session governance seam, so whole-subtree per-session fairness is not
  reachable for them today. Options A, B, and C above span leave-it / name-it / close-it.

The distinguishing evidence, when someone does choose, is whether host-side per-session CPU is a
material share once the agent subtree is governed: concurrent `after_create` / `before_run`
build/install hooks are the path to watch, while fetch / merge / worktree appear bounded. Until that
is measured, no option is preferable on the evidence here. The non-secret env-passthrough half of the
brief (Section 15.3) is tracked separately and does not gate this decision.
