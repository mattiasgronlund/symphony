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
   **Superseded on this point (2026-08-27):** the sandbox-wrap contract has no configuration surface
   a deployment can reach — see correction 3 in the update below.

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
**Qualified on this point (2026-08-27):** a workspace hook's execution context now follows the
artifact that declares it, so these hook names no longer locate the cost — see correction 1 in the
update below.

A separable concern in the same brief — propagating a curated set of *non-secret* gate-control
environment variables (`ENTRY_CHECK_JOBS` / `_LOAD` / `_SLOTS` / `_DIR`) into the session so the gate's
cap and `-j`/`-l` settings actually apply — is out of scope here. It touches the Section 15.3
secret-scrubbing invariant: the spec scrubs every secret-bearing variable before the sandbox starts
but has no positive mechanism to inject a non-secret allowlist into the sandbox. That is a candidate
for its own later decision, not this one.
**Superseded on this point (2026-08-27):** it is not a separate concern but a fourth option here, and
its carrier now exists (decision 0117) — see Option D in the update below.

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
**Retired (2026-08-27):** nothing was measured and the agent subtree was never governed, so this gate
described a condition nobody was positioned to observe; it is replaced by a trigger that arrives on
its own — see the update below.

## Update — 2026-06-28: repository provisioning's failure-model half addressed by 0034

This decision's finding 2 listed "repository provisioning and `git fetch` (Section 9.7)" among the
host-side ops the spec models as behaviors with no governance seam. A separate gap in the *same* op —
the spec described the provisioning *result* but gave it no failure class, recovery, or reference
algorithm — was closed by decision 0034 (Accepted): a `Repository Provisioning Failures` class
(Section 14.1), repo-scoped recovery (Section 14.2), and an `ensure_object_store` reference algorithm
(Section 16.5). That renumbered the worktree-provisioning algorithm cited above from Section 16.5 to
Section 16.6.

This does **not** select an option here. 0034 is about *error handling* for repository provisioning;
this decision's open question is *per-session CPU governance* of host-side ops, which 0034 leaves
untouched. The two are neighbours on the same under-specified surface, not the same concern.

## Update — 2026-07-03: Option C's seam is realized (as placement) by decision 0035

This decision's finding 2 named the gap precisely: "the spec has no launch-governance seam for
host-side work" — Symphony "models host-side ops as behaviors, not launches", so there is no
wrapper/command indirection the orchestrator can interpose. Option C proposed closing it with a
host-side execution-wrapper seam, a "session resource domain" that a session's host-side work and its
sandbox both join.

Decision 0035 (Accepted) closes that seam gap — along a **different axis than governance**. It gives
the Execution Layer (Section 3.2) a component identity (the **execution process**) and makes the
orchestrator↔executor seam always present, with local execution as the in-process transport. That is
exactly the launch indirection finding 2 said was missing: dispatch no longer calls the worker as a
behavior, it hands a run to an executor across a seam. A "session resource domain" that can be
governed is, structurally, one step from a session resource domain that can be *placed* — on another
machine (0036/0037). 0035 takes the placement step; the executor is the session resource domain
Option C described, now a real component.

This still does **not** select a governance option here. 0035–0038 are about *where and how* a
session's execution detaches from the orchestrator (placement, the wire contract, acquisition, write
authority); this decision's open question remains *per-session CPU fairness* of host-side work. But
the relationship is now concrete rather than anticipated: once execution is a component behind a seam
(0035), per-session resource governance has a natural home — the executor's own launch context, which
for a remote run is the node and for a local run is the in-process executor. If and when the
governance question is chosen, Option C's mechanism should be expressed against the 0035 executor
rather than invented separately: the seam Option C wanted already exists as the executor boundary.
The distinguishing evidence for choosing is unchanged (whether host-side per-session CPU is material
once the agent subtree is governed); what changed is that the seam it would attach to is no longer
hypothetical.

## Update — 2026-08-27: three corrections, a fourth option, and a trigger that arrives on its own

A re-evaluation session re-read this decision against `SPEC.md` as it now stands. The finding is
smaller and differently shaped than recorded above, and three of the claims it rests on no longer hold
as written. The State becomes `Proposed (partly overtaken by 0035, 0117)` — the question is still
open, but two of the surfaces it reasoned over have since been built. Nothing above is erased; the
claims that changed carry an inline marker pointing here.

### Correction 1 — a workspace hook's execution context follows the artifact that declares it

The Context above names the dominant host-side CPU cost as "concurrent `after_create` / `before_run`
build/install hooks", treating a workspace hook as host-side by virtue of being a workspace hook. The
specification no longer has one execution context for those names. Section 5.3.4 splits them by
declaring artifact: hooks defined in `repo.policy.toml` are sourced from the policy branch and "run on
the host outside the sandbox with host access", for "privileged setup (for example dependency
bootstrap that reaches credentialed mirrors)"; hooks defined in `WORKFLOW.md` are worktree-sourced,
"run inside the sandbox without credentials", and are for "in-sandbox build/test/workspace
preparation". A lifecycle point MAY be defined in both artifacts, and when it is, both run — one on
each side of the boundary (Sections 5.3.4, 15.4).

This narrows the host-side CPU tail rather than removing it. The build-cache warm in the original
example is in-sandbox build preparation, so it lands on finding 1's side of the line and is already
covered by the sandbox attach point; the dependency bootstrap is the specification's own host-side
example and stays host-side. What is no longer true is that the hook *names* locate the cost. Whether
a session's setup hook contends on the host is a repository's choice of declaring artifact, made on
the policy branch — which also means the orchestrator that would have to govern it cannot tell from
its own configuration how much host-side work a given repository's sessions will do.

### Correction 2 — the seam exists; the gap is that a local executor has no launch context of its own

Finding 2's premise was that host-side per-session subprocesses are children of the long-lived
orchestrator and therefore inherit the orchestrator's cgroup. Decision 0035 changed the structure that
premise described. Section 3.1 now gives the per-issue run an `Execution Process` — the *executor* —
which composes the Workspace Manager, the Agent Runner, and the per-run Privileged Operation Broker,
and which "is the host relative to its own agent sandbox", running both hook trust levels wherever it
runs. Every host-side op finding 2 listed — worktree and object-store provisioning, the brokered git
verbs, the host-side hooks — is now work of a named per-session component rather than an unattributed
behavior of the orchestrator.

That splits the remaining gap by topology, and only one half is still Symphony's:

- **Remote.** Under the node-scheduler extension (Section 9.11) the executor runs on a node the
  scheduler owns, and where the scheduler packs several executor processes onto one node under
  `compute.sharing = shared`, Section 8.3 makes Symphony deliberately placement-opaque and points a
  deployment wanting to bound co-location at `max_concurrent_agents`. Per-session CPU fairness there
  is the scheduler's concern by design, not an omission.
- **Local.** The seam is an in-process call and the executor runs in the orchestrator's process, so
  its host-side work shares the orchestrator's cgroup exactly as finding 2 described.

Option C therefore shrinks from "define a session resource domain and a launch-wrapper indirection"
to a much smaller question: **MAY a local executor be its own launch context?** The abstraction it
wanted to introduce already exists as the executor boundary; what is unstated is whether that
boundary is permitted to be a process boundary when the transport is in-process.

### Correction 3 — finding 1 closes the agent side on a contract with no configuration surface

Finding 1 declares the agent side already satisfied: "an operator wraps the sandbox invocation (for
example a systemd transient scope under a shared parent slice) without Symphony defining anything
new." Two facts recorded here undercut that.

The first is the absent measurement, recorded next to the claim it bears on, as the missing half of
the Context's CPU-stall figures: **as of 2026-08-27 the cgroup wrap was never deployed and host-side
per-session CPU was never measured.** The operator filed a measured congestion report and then did not
apply the fix this decision called free. That is behavioral evidence about the fix, not only about
priorities.

The second is the mechanism. `SPEC.md` has no `sandbox.*` configuration namespace at all. Section 9.6
says the sandbox profile "is configurable" and `Implementation-defined`; Section 6.4 names no field
that selects it, and the only sandbox keys in the cheat sheet — `codex.thread_sandbox`,
`codex.turn_sandbox_policy` — configure the *agent's own* sandbox, not Symphony's. Section 17 then
asserts that "Agent launch wraps the session in the configured sandbox (strict profile by default)"
against a configuration no section defines. So "wrapping the sandbox invocation" means patching
whatever code performs the launch, in an implementation, per deployment. The operator asked for
governance driven "from the Symphony side, with a per-host enable flag that no-ops on dev laptops, CI,
and non-systemd hosts" — a configuration surface — and that is precisely what the contract finding 1
points at does not offer.

Finding 1 is therefore true in principle and unreachable in a deployment, which is the same shape of
defect finding 2 named for host-side work: a gap declared closed by pointing at a contract that has no
surface a deployment can reach. The agent side is not settled; it is unconfigured.

### Option D — cooperative capping through the constructed environment

The Context above sets the brief's non-secret env-passthrough half out of scope as a separate concern.
It is not a separate concern: it is a fourth way to reach the same goal, and it belongs in this
decision's option list.

- **Option D — cooperative capping.** Divide a CPU budget across concurrent runs by telling each run
  what share it may use — the gate-control variables from the brief (`ENTRY_CHECK_JOBS` / `_LOAD` /
  `_SLOTS` / `_DIR`), which set the build's own `-j` / `-l` caps — instead of enforcing weights around
  it. When this decision was written the mechanism had no carrier, which is why it was deferred.
  Decision 0117 has since supplied one: Section 9.6's *Constructed environment* clause makes the run's
  environment composed rather than inherited, requires that "variables the deployment intends are
  passed explicitly", and makes the composed set `Implementation-defined` and documented in the
  Conformance Statement.

  Trade-offs. It reaches both execution contexts without a new abstraction — in-sandbox and host-side
  work read the same constructed environment, which is the whole-subtree coverage Option C wanted the
  cgroup for. It has no cgroup-v2, delegation, or systemd dependency, so it degrades to a no-op on
  laptops, CI, and non-systemd hosts by construction rather than by an enable flag. Against it: it is
  advisory, so a run that ignores the variables is ungoverned, and it is not work-conserving in the
  way the brief asked for — a fixed per-run `-j` leaves the box idle when one session runs alone,
  where a CPU weight would let it saturate. It also only governs ecosystems whose build tools honor
  such variables, and the number handed to each run has to come from somewhere: nothing in the spec
  derives a per-run share from `max_concurrent_agents`, so today it would be an operator's constant.

  What 0117 supplies is the carrier, not the policy. No decision says a deployment should divide a CPU
  budget across concurrent runs, and none derives the per-run number. The separately-tracked future
  decision this Context promised is therefore **absorbed in part** — its mechanism exists, its policy
  does not — and is now this decision's Option D rather than an unowned thread. Nothing else in the
  decision log has ever referred to it.

### The four options ranked as of this date

Still selecting none. The ranking below is as of 2026-08-27 and does not revise the June list above,
which records what was considered then.

1. **D, cooperative capping.** The only option that reaches host-side and in-sandbox work alike
   without introducing an abstraction, and the only one whose no-op fallback is structural. Weakest
   on enforcement, which is a real loss against the brief's "fairness" framing.
2. **B, restated.** The clarifying note is worth more now than in June, because correction 3 shows the
   attach point it would name is unconfigured. A B that only names the sandbox launch repeats the
   defect; a B that also introduces a configuration surface for it is a genuine improvement.
3. **C, shrunk.** Reduced by correction 2 to "MAY a local executor be its own launch context", and by
   correction 1 to a narrower motivating cost. Cheap in its shrunken form, but it governs only the
   local topology, the one case a deployment can already address by putting the whole service in a
   slice.
4. **A, silence.** Weakest of the four now. Silence was defensible while the attach point was believed
   reachable; correction 3 shows it is not, so staying silent conceals a gap that has been observed to
   bite an operator.

### Reconsideration trigger, replacing the evidence gate

The original gate — measure whether host-side per-session CPU is material once the agent subtree is
governed — is retired. Nothing was measured and the agent subtree was never governed, so the gate
described a condition nobody was positioned to observe; a trigger nobody watches for reads as
diligence while functioning as a deferral.

The replacement is a trigger that arrives on its own: **implementation reaching the Execution
Process.** The phase that builds the Section 3.1 executor cannot be planned without answering whether
a local executor is its own launch context, which is exactly correction 2's remaining question, and
whether the sandbox launch gets a configuration surface, which is correction 3's. A secondary trigger
is a second operator report of concurrency congestion, from any deployment — one report is an anecdote
about one box, two is a property of the design.

### Adjacent gap discovered here and not closed

Section 9.4 "Workspace Hooks" documents a single execution contract — "Execute in a local shell
context appropriate to the host OS, with the workspace directory as `cwd`" — for what Sections 5.3.4
and 15.4 make two execution contexts with different trust, different sourcing revisions, and (per
Section 15.4) different working directories. A reader who configures hooks from Section 9.4 alone
cannot tell which context a hook runs in, and the `cwd` sentence is true only of the in-sandbox half.
That is a documentation-consistency defect on the surface that decided correction 1, not a governance
question, and it needs its own decision rather than a quiet repair folded into this one.
