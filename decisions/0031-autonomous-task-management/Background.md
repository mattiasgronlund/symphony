# Background — 0031 Autonomous task management and computed completion

## Context

Completion was a single agent-asserted milestone signal (`done`, decision 0008). For unattended,
autonomous operation that is weak: Symphony cannot *see* progress and must trust a flag. A stronger
model — like the task/todo list a coding agent already maintains — lets the orchestrator **compute**
completion and observe progress. Interactive sessions do not need this: a human present simply types
`ship`/`land` (so this surface is daemon-only).

The task model also unifies two escalation directions that had been separate: the orchestrator
handing work *to* the agent (a merge conflict) and the agent asking *for* help (it is stuck).

## Options considered

- **Option A — Keep the single `done` signal.** Trade-offs: minimal, but progress is opaque and
  completion is an unverifiable assertion. Rejected for the autonomous case.

- **Option B — A daemon-side task model with computed completion (chosen).**
  - **Tasks** carry an id, description, status (`open`/`closed`/`blocked`), an **assignee**
    (`agent` | `human`), an optional parent (splits), and an optional tracker link.
  - **Seeding:** derive from the ticket when the tracker exposes structure (checklist / sub-issues —
    capability-gated, decision 0018); otherwise open with a **planning turn** where the agent creates
    the list.
  - **Agent verbs** on the broker socket CLI (decisions 0003/0004): `add`, `split`, `close`,
    `need-help`, `update`.
  - **Completion is computed:** `tasks:all_closed` runs `ship` (decision 0028); it is not asserted.
  - **Escalation directions** are both tasks: a conflict binds `escalate` (decision 0030) to an
    agent-assigned task; `need-help` is an agent-created human-assigned task that parks for feedback.
  - **Tracker sync** is optional/capability-gated (decision 0018); otherwise tasks are
    Symphony-internal.
  - Daemon-only; interactive sessions use `ship`/`land` (decision 0027).

## Decision and reasoning

Choose **Option B**. The task model is the daemon's progress/completion surface and the home of the
`escalate` resolver binding from decision 0030. It refines decisions 0008 and 0017: the coarse
milestone vocabulary is enriched/partly superseded by computed task state — `done` becomes
`tasks:all_closed`, `blocked` becomes a `need-help` task — and task-state events become triggers in
the action-policy machine.

The task list is **new run state**, so it must be classified under decision 0010's taxonomy. The
initial leaning was "reconstructable where synced, ephemeral otherwise (durable admissible)," recorded
as a genuine open fork with restart consequences. That fork is now **resolved** — see *Fork
resolution* below.

The agent verbs extend the broker CLI (decisions 0003/0004) — a natural addition, not a reversal of
the credential boundary (task verbs carry no credentials).

We would reconsider the durability default if restart behavior demands a different stance, or fold
`ready-for-review` into a computed "implementation tasks closed" if the explicit signal proves
redundant.

## Fork resolution — materialize-into-tracker (2026-06-28)

The ephemeral case (a planning-turn task list that lives only in orchestrator memory) is the weak one:
its "re-derive from the ticket on restart" is not a faithful resume but a **re-plan**, non-idempotent
if the ticket drifted, and it loses progress. We resolve the fork by largely *dissolving* that case
rather than tolerating it.

- **Materialize-into-tracker (write-through sync).** During seeding/planning, the agent's
  credential-free `add`/`split` verbs cause the **broker** (host-side, credentialed — the agent never
  gets tracker secrets, decision 0003) to create and maintain the corresponding structured tracker
  artifacts (sub-issues / checklist items). The issue thereby *holds* the task list, so the
  seed-from-ticket-structure path (already in this decision) and the restart-reconstruct path become
  the **same** path: a restart cannot tell whether the human authored the checklist or Symphony did —
  both reconstruct identically. This is this decision's optional tracker-sync used **write-through**
  as the seeding mechanism, not a passive mirror.
- **Default on, policy can disable.** Where the tracker's capability descriptor (decision 0018)
  declares a **structured-task-write** capability, write-through is the default; a repo turns it off in
  `repo.policy.toml` (decision 0029) when it does not want Symphony writing into its issues.
- **Durability classification (decision 0010).** Where materialized, the task list is
  **`Reconstructable`** — the tracker is the source of truth, Symphony primary-persists nothing, and
  restart is faithful, preserving 0010's no-durable-DB stance (the durability lives in the external
  tracker). Where the tracker **cannot** represent structured tasks, or write-through is disabled, the
  fallback is **`Durable`** (0010's narrow OPTIONAL D class with idempotent re-seed-before-enforcement)
  so restart still resumes exactly. The task list is therefore **never `Ephemeral` by default** — the
  chosen stance is faithful restart everywhere; `Ephemeral` remains an admissible opt-in for a
  deployment that prefers re-plan over persistence.
- **Idempotency.** Materialization and the durable fallback are both keyed by stable task `id` (a
  fenced "Symphony tasks" marker / sub-issue ids), so a crash mid-planning reconstructs the partial
  list and continues rather than duplicating it.

This refines decisions 0008 and 0017 (as above); exercises decision 0010's `D` exception for the
fallback and classifies the task list as `R` for the default; adds a structured-task-write capability
under decision 0018's descriptor; and the write-through itself is a broker-mediated tracker write
(decisions 0008/0021/0023), keeping the agent credential-free.

The decision is **Accepted** (dependencies 0027 and 0030 are Accepted; the durability fork is
resolved above); the corresponding `SPEC.md` change is **not** made yet — application is deferred (see
`Plan.md` Status). Refines decisions 0008 and 0017; exercises 0010's taxonomy and adds an 0018
capability; relates to 0011 and 0003/0004 (broker CLI).
