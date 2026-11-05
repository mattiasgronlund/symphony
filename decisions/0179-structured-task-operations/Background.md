# Background — 0179 Structured-task operations are the extension's, and the descriptor declares each one

## Context

Reported from `symphony-rs` as issue #175, against `86a2188`, found while reconciling that
repository's Stage D6 and tracked there as decision 0011 R100.

`structured-task-write` is cited as a Section 11.7 tracker capability four times in `SPEC.md`
(Section 8.10 twice, the Section 17 task-management row, the Section 18.2 extension entry) and twice
more in `VCSX-CONTRACT.md`'s task-model section. Section 11.7's descriptor declares "which write
operations it supports: `add_comment`, `set_state`, and `link_pull_request`", and no fourth. Its gate
is that the orchestrator reads the descriptor before invoking a write, and there is nothing to read
for a capability the descriptor has no entry for.

## How the citation came to dangle

Decision 0031's chapter, which introduced the task model, says write-through is default on "where
0018 declares a structured-task-write capability". Decision 0018's chapter and folder never declared
one. Its scope was the three Section 11.1 writes, made capability-gated. So the citation pointed at
a decision that came before the capability it was supposed to define, and no later decision filled
the gap.

## The mechanism

**Half of what the capability gates is a read.** The report's preferred fix was to add one write to
the descriptor. One of the four sites gates something that isn't a write:

> Tasks seed from the ticket when the tracker exposes structured tasks — a checklist or sub-issues —
> gated by the tracker's `structured-task-write` capability (Section 11.7).

Seeding **reads** the ticket's checklist or sub-issues. Reconstruction is a read too: Sections 8.10
and 14.3 classify a materialized task list `Reconstructable`, meaning rebuilt from the tracker on
restart. None of Section 11.1's three reads returns structured tasks. `fetch_issue_states_by_ids`
returns the Section 4.1.1 record, and that record has no task field. `symphony-rs` confirmed on the
thread that it has no other read path for seeding. Adding a write to the descriptor would resolve
the citation text and leave seeding and reconstruction gated on a flag that says nothing about
whether the read exists.

**Reconstruction also needs the task `id` to round-trip through the tracker.** Section 8.10 keys
materialization by the stable task `id`, "so a crash mid-planning reconstructs the partial list
rather than duplicating it". That works only if the artifact the write creates carries the `id` in
a form the read returns. Otherwise the restarted list can't tell a task it already materialized
from one it hasn't, and the duplicate the sentence rules out is what happens. Trackers differ in
where such a key can live (a sub-issue field or label, a marker in a checklist line's text), so the
carrier is a real per-implementation choice.

## Options considered

- **The extension defines its two tracker operations, and the descriptor declares each one**
  (chosen). Section 8.10 states a read (`fetch_structured_tasks`) and a write
  (`write_structured_task`), as Section 11.1 states the core operations. Section 11.7 declares them
  as it declares the three writes. Seeding and reconstruction are gated on the read and write-through
  on the write. Core adapters declare neither, and Section 11.1 stays at three reads and three
  writes.
- **Add `structured-task-write` to Section 11.7 as a fourth write** (the report's first arm). It is
  the smallest edit and resolves the citation. It loses for the reason above: the read stays
  undefined, so seeding is still gated on the wrong thing.
- **Add both operations to Section 11.1 as OPTIONAL core operations.** This keeps every tracker
  operation in one list. It loses because the operations exist only for an OPTIONAL extension, and
  the convention is that an extension owns what it introduces. Section 8.10 already owns `[tasks]`
  and `[driver]` in the same way. Putting them in Section 11.1 would make a reader of the core
  contract learn an extension's surface.
- **Re-cite the sites elsewhere** (the report's second arm). There is no elsewhere: no section of
  any document in the corpus defines the operation.

## Decision and reasoning

The descriptor declares operations, not abstract capabilities. Section 11.7 already does this for
the three writes, and it means the gate can check an operation name against a list of operation
names. So the kebab-case `structured-task-write` goes away, and the two operation names take its
place. Section 11.7's sentence that the three reads "are not part of the descriptor" stays true,
because it is about REQUIRED reads. The new read is optional, so it is declared.

How a tracker artifact carries a task's `id`, `status` and `assignee` is `Implementation-defined`
and MUST be documented, because the round-trip above depends on it. That puts a row in the
extension-scoped table of `CONFORMANCE-STATEMENT-TEMPLATE.md`. An artifact with no recorded `id` is
one a person put on the ticket, for example a checklist line written by the ticket's author.
Seeding gives it an `id`, and write-through records that `id` on the artifact where write-through
is on.

`symphony-rs` doesn't ship Section 8.10, and its descriptor stays at three write lists. The new
declarations are absent there, and its existing gate answers any structured-task operation with
`tracker_unsupported_operation`, which is correct.

**Reconsideration trigger:** a tracker where structured tasks can be written but not read back, or
read but not written. The two declarations already allow either combination. If such a tracker
appears, check whether `Reconstructable` still holds for it. With write but no read it doesn't, and
Section 8.10's classification would then need a third case.
