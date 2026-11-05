# Background — 0182 The engine reads the commit subjects, through a capability that did not exist

## Context

Reported from `symphony-rs` as issue #178, against `86a2188`, found at that repository's roadmap G2
(its decision 0151) while it was making Symphony supply the durable inputs a pull-request body is
composed from. It is tracked there as decision 0011 R112. `VCSX-SPEC.md` Section 10.2:

> `body_source = "auto"` — compose the body from durable inputs the consumer supplies: the work item
> (title and link), a closed task list when the consumer runs the task model (Section 7.3), and the
> commit subjects.

The reference algorithm (Section 12.5) takes them as `inputs.commit_subjects`, and `SPEC.md` Section
9.10 and `VCSX-CONTRACT.md`'s message-composition bullet repeat the list.

## The mechanism

**The third input isn't the consumer's to supply.** The consumer knows the work item because a
tracker gave it the ticket, and it knows the closed tasks because it closed them. The commit subjects
are history on the work branch, a version-control read inside the checkout the engine holds.
`symphony-rs`'s engine front end declined to read them for exactly that reason: doing so would be
the front end performing a VCS read outside the engine that owns VCS reads.

**And no party can produce it today.** The report put this as an input "only a `§9.1` read can
obtain". Checked at `86a2188`, `VCSX-SPEC.md` Section 9.1's capabilities are `ensure_store`,
`derive_working_tree`, `detect_mode`, `current_branch`, `is_dirty`, `is_conflicted`, `ahead_behind`,
`accepts_branch_name`, `accepts_identity`, `resolve_base_ref`, `read_at_source`, `diff`,
`derive_work_branch`, `worktree_revision`, `worktree_diff`, `commit`, `fetch_base`, `merge_base`,
`fetch_counterpart`, `merge_counterpart`, `push` and `export_source`. None returns commit subjects.
`diff(base_ref)` returns the branch's content delta, not its history. So the consumer may not read the
branch, and the engine has no capability to read it with. Every conforming implementation publishes
an `auto` body without subjects, whichever party it assigns them to. `symphony-rs` confirmed this on
the thread: its own premise was wrong, and in the direction that makes the gap worse.

**An unreadable history and an empty one would publish the same body.** Once the engine reads the
subjects, the read can fail, and a composer that drops an empty section prints the same body for
"no commits ahead of the base" as for "could not read the log". Section 9.1 already has the
principle for this, in `is_dirty()`: "A dirtiness it could not determine is not cleanliness." A
pull-request body isn't a guarantee the way `is_dirty()`'s answer is. Nothing branches on it, so
failing `create_pr` over a missing summary would cost more than it protects. But a body that hides
the failure misleads its reader. So the body says the subjects could not be read, with a fixed marker
rather than free prose, so that a `before:create_pr` scan and a later update of the same pull
request can recognise it. `symphony-rs` asked for the fixed marker on the thread.

## Options considered

- **The engine reads them through a new Section 9.1 capability** (chosen). Section 10.2 lists the
  work item and closed task list as what the consumer supplies, and the commit subjects as what the
  engine reads. Section 9.1 gains `commit_subjects(base_ref)`, shaped like `ahead_behind(base_ref)`
  and `diff(base_ref)`, resolved against the same base. An undetermined read puts a fixed marker in
  the body.
- **The consumer reads them** (the text as written). It keeps the engine's surface unchanged. It
  loses because it needs a VCS read exported to consumers, which Section 9.1 withholds by design, and
  because the consumer would read a checkout the engine may be mutating in the same invocation.
- **Drop commit subjects from the `auto` inputs.** This is the smallest change and matches what every
  implementation already publishes. It loses because the subjects are the one input that summarizes
  the change itself, not its context, and the squash path (Section 10.3) launders this body into
  durable history. A pull request whose body omits what changed is a worse default than one that
  says it could not read it.
- **Fail `create_pr` when the read fails.** This is the strongest form of the `is_dirty()` principle.
  It loses because no guarantee depends on the body's content, and refusing to publish work over a
  missing summary turns a cosmetic failure into a delivery failure.

## Decision and reasoning

`commit_subjects(base_ref)` answers the subject (the first line of the message) of each commit on the
current branch that is not reachable from `base_ref`, oldest first, or that it could not determine
them. It is read-only and acquires nothing. It is a required capability, not an optional one:
`symphony-rs` confirmed that it cannot be absent for git or jj, and every VCS the engine targets has a
log, so Section 9.3 needs no descriptor field.

The undetermined case puts the fixed token `commit_subjects_undetermined` in the place of the
subjects in an `auto` body, and a `template` unit is told the read was undetermined rather than
handed an empty list. The token is spelled by the specification, not by each engine, because the
point is that something other than the engine can recognise it.

No Conformance Statement row is owed on either side: the decision adds no `Implementation-defined`
value and no MUST-document obligation. The `VCSX-SPEC.md` test matrix, checklist, and message
composition row gain the capability and the marker. `SPEC.md` Section 9.10 and `VCSX-CONTRACT.md`
change their wording from "inputs the consumer supplies" to name who supplies each input.

**Reconsideration trigger:** a VCS backend in scope with no linear notion of "commits on this branch
not reachable from the base", for example a patch-based system. `commit_subjects` would then need to
be optional, declared in Section 9.3, and the composed body would need a third state.
