# Plan — 0179 Structured-task operations are the extension's, and the descriptor declares each one

## Scope

`SPEC.md` Section 8.10 (Autonomous Task Management (OPTIONAL)), Section 11.7 (Adapter Capability
Descriptor), the Section 17.4 task-management row, and Section 18.2 (RECOMMENDED Extensions (Not
REQUIRED for Conformance)). `VCSX-CONTRACT.md`'s task-model section (the **Seeding** and
**Write-through materialization** bullets). `CONFORMANCE-STATEMENT-TEMPLATE.md`'s extension-scoped
table.

Section 11.1 (REQUIRED Operations) is unchanged.

## Steps

1. **Section 8.10 defines its tracker operations.** Ensure a "Tracker operations:" group in Section
   8.10 states two operations the extension adds to a tracker adapter, each declared in the
   descriptor (Section 11.7) and absent from Section 11.1:
   - `fetch_structured_tasks(issue_id)`: the issue's structured tasks (checklist items or
     sub-issues), each returned as a `Task` (Section 4.1.9) with its `tracker_ref`, and with its
     `id` where one was recorded.
   - `write_structured_task(issue_id, task)`: creates or updates the artifact for `task`, keyed by
     its `id`. The write records the `id` on the artifact so that `fetch_structured_tasks` returns
     it. It returns the `tracker_ref`.
   Ensure it says that how an artifact carries `id`, `status` and `assignee` is
   `Implementation-defined` and MUST be documented, and that an artifact with no recorded `id` is
   given one when it is seeded. Done when both operations are defined in Section 8.10.

2. **Section 8.10's gates cite the operations.** Ensure the Seeding bullet is gated on the adapter
   declaring `fetch_structured_tasks`, that the Write-through materialization bullet is gated on
   `write_structured_task`, and that the Recovery classification bullet's `Reconstructable` case
   requires both. Done when `structured-task-write` no longer occurs in Section 8.10.

3. **Section 11.7 declares them.** Ensure a descriptor bullet says that, where the adapter
   implements the OPTIONAL Section 8.10 operations, the descriptor declares whether it supports
   `fetch_structured_tasks` and whether it supports `write_structured_task`, and that the gate
   applies to them as it does to the writes. Done when Section 11.7 names both operations.

4. **The other `SPEC.md` sites re-cite.** Ensure the Section 17.4 row beginning "If autonomous task
   management is implemented (Section 8.10), tasks seed from the ticket" and the Section 18.2
   autonomous task management entry name the operation each gate depends on in place of
   `structured-task-write`. Done when `structured-task-write` no longer occurs in `SPEC.md`.

5. **`VCSX-CONTRACT.md` re-cites.** Ensure the **Seeding** and **Write-through materialization**
   bullets name `fetch_structured_tasks` and `write_structured_task` as the tracker operations each
   is gated on, citing `SPEC.md` Section 8.10. Done when `structured-task-write` no longer occurs in
   `VCSX-CONTRACT.md`.

6. **The Conformance Statement template carries the obligation.** Ensure
   `CONFORMANCE-STATEMENT-TEMPLATE.md`'s extension-scoped table has a row for Section 8.10: how a
   tracker artifact carries a task's `id`, `status` and `assignee`, per adapter. Done when the row
   exists.

## Cross-cutting sync

- Section 6.4: unaffected; no key changes.
- Section 17 and Section 18.2: step 4.
- Conformance Statement templates: step 6 (one new `Implementation-defined` obligation).
- `VCSX-SPEC.md`: unaffected; the engine does not touch tracker operations.
- `conformance/`: unaffected.

## Anchor changes

- Removed: `structured-task-write`, superseded by `fetch_structured_tasks` and
  `write_structured_task` (Section 8.10, declared in Section 11.7).

## Status

Applied, all steps, in the same pull request as decisions 0177–0182 (issues #173–#178).
