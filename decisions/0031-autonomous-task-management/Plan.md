# Plan — 0031 Autonomous task management and computed completion

## Scope

Affected anchors in `SPEC.md`:

- The agent milestone-signal vocabulary (decision 0008) and `tracker.transitions` triggers (decision
  0017) — enriched with task-state.
- The broker CLI (Sections 10.8 / decisions 0003/0004) — task verbs.
- A new `[tasks]` config block in `repo.policy.toml` (decision 0029) and the `[driver]` table.
- Section 7.2 (run/turn/step) — a planning sub-phase at run start.
- The state model (Section 18.2 / decision 0010) — task-list classification.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Task model.** Ensure `SPEC.md` defines a task with `id`, `description`, `status`
   (`open`/`closed`/`blocked`), `assignee` (`agent`/`human`), optional parent, optional tracker link.
   Done when the task fields and statuses are defined.

2. **Broker task verbs.** Ensure the broker CLI gains `add`, `split`, `close`, `need-help`, `update`,
   carrying no credentials. Done when the verbs are listed on the broker CLI surface.

3. **Seeding.** Ensure tasks seed from the ticket when the tracker capability descriptor (decision
   0018) exposes checklist/sub-issues, else a **planning turn** creates them. Done when both seeding
   paths are specified, the ticket path gated on capability.

4. **Computed completion.** Ensure `tasks:all_closed` is computed by the daemon and runs `ship`
   (the `[driver]` `on`/`run`), replacing an asserted `done`. Done when completion is described as
   computed and wired to `ship`.

5. **Escalation as tasks.** Ensure a conflict binds `escalate` (decision 0030) to an agent-assigned
   task and `need-help` is an agent-created human-assigned task that parks for feedback (e.g.
   `set_state = Blocked`, `notify = human`). Done when both directions are expressed as tasks.

6. **Materialize-into-tracker (write-through sync).** Ensure the spec defines write-through task↔
   tracker sync: the agent's `add`/`split` verbs cause the **broker** (credentialed; agent stays
   secret-free per decision 0003) to create/maintain structured tracker artifacts (sub-issues /
   checklist items). Gated by a **structured-task-write** capability in the tracker descriptor
   (decision 0018) and **default on** where present; a repo disables it via `repo.policy.toml`
   (decision 0029). Done when write-through, its capability gate, the default-on rule, and the
   broker-mediated (credential-free) write path are specified.

7. **State classification.** Ensure the task list is classified under decision 0010:
   **`Reconstructable`** where materialized into the tracker (the tracker is source of truth; nothing
   primary-persisted; faithful restart), and **`Durable`** (0010's OPTIONAL D class, idempotent
   re-seed) where the tracker cannot represent structured tasks or write-through is off — **never
   `Ephemeral` by default** (`Ephemeral` admissible only as an explicit opt-in). Materialization and
   the durable fallback are keyed by stable task `id` so a mid-planning crash reconstructs rather than
   duplicates. Done when the class per case, the restart behavior, and the idempotency key are stated.

8. **Daemon-only.** Ensure the surface is marked daemon-only; interactive sessions use `ship`/`land`
   (decision 0027) and have no task manager. Done when the daemon-only scope is stated.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** add `[tasks]` and `[driver]` config keys.
- **Section 17 (test matrix):** seed-from-ticket; plan-if-empty; `tasks:all_closed` runs `ship`;
  `need-help` parks and notifies; write-through materializes a planned list into the tracker and a
  restart reconstructs it; with write-through off (or no structured-task-write capability) a restart
  resumes from the durable task list; a mid-planning crash does not duplicate tasks.
- **Section 18 (checklist):** OPTIONAL, daemon-scoped extension under 18.2.

## Anchor changes

New tokens: task verbs (`add`/`split`/`close`/`need-help`/`update`), `tasks:all_closed`,
`task:#needs_help`, `[tasks]`, `[driver]`, **write-through** materialize-into-tracker, the
**structured-task-write** tracker capability (decision 0018). Refines decisions 0008 and 0017
(milestone vocabulary → computed task state); classifies the task list under 0010 (`R` materialized /
`D` fallback). Relates to 0011 and 0003/0004. Depends on decisions 0027, 0030.

## Status

Accepted; `SPEC.md` application not started. Dependencies 0027 and 0030 are Accepted. The open fork
(default task-list durability) is **resolved**: write-through materialize-into-tracker (default on
where the structured-task-write capability exists) → `Reconstructable`; `Durable` fallback otherwise;
never `Ephemeral` by default — see this decision's `Background.md` *Fork resolution*. The
re-evaluations are recorded: decisions 0008 and 0017 carry append-only `Background.md` notes (both
stay Accepted), and decision 0010 notes the task list as a new R/D consumer. `SPEC.md` application is
deferred and batched with the companion `vcsx` spec (0028) and decision 0029 (`repo.policy.toml`
houses `[tasks]`/`[driver]`).
