# Background — 0186 The identity check that runs after the write it guards

## Context

Reported from `symphony-rs` as issues #180 and #181, against `b04797e`, found while wiring the
top rung of `SPEC.md` Section 9.7's target ladder, the per-issue target.

- **#180** reports an ordering gap. Section 9.8's start-of-run back-merge runs before Section
  9.10's identity re-read, so a retargeted issue merges the new base into a pull request that still
  targets the old one.
- **#181** proposes closing the gap in the engine contract. `integrate` would take an OPTIONAL
  `expected_base`, as `request_merge` takes `expected_head`.

The two are one decision, because #181's proposal is one answer to #180's first question.

## The failure path, and where it actually lands

1. Run 1: the issue resolves target `release/1`, and Symphony opens `release/1 ← symphony/ENG-1`.
2. The issue is relabelled, so Section 9.7 now resolves `release/2`, a permitted target. Section 9.7
   says correcting a target takes effect with no other action.
3. Run 2: the Section 9.8 back-merge integrates `release/2` into `symphony/ENG-1`. Section 16.6
   places that straight after provisioning, before the agent and before any forge write.
4. The agent works and asks for `pr`. Section 9.10's re-read finds the pull request targeting
   `release/1`, refuses with `pr_identity_mismatch`, and hands the repair to an operator.

The report says "anything pushed from that branch" then shows the wrong history. Checking the
engine contract shows the damage lands earlier than the report implies, at the first `push` and not
the `pr` call. `push` already reads the work branch's pull-request state (`VCSX-SPEC.md` Section 4.1).
Since decision 0169 that state carries the base, yet `push` refuses only a CLOSED/MERGED pull
request. So the first push after the back-merge puts `release/2`'s commits on the open `release/1`
pull request. Section 9.10's check and `create_pr:base_mismatch` both fire only after that. Both
are checks that run after the write they exist to prevent.

Two facts make it worse than a refusal arriving late:

- **There is no second writer.** Section 9.10's refusal text says a mismatch "means a second writer
  is acting on the same pull request". Here nobody else acted: an operator corrected a label, which
  Section 9.7 invites.
- **No repair is mechanical, in either direction.** The work branch carries the old base's history.
  Retargeting the pull request to `release/2` shows `release/1`'s commits as changes, and merging
  `release/2` into a `release/1` pull request is the pollution itself.

## Where the check lives: engine-resolved, not an argument (#181)

`expected_head` carries a value the caller **observed**: the head an earlier read returned, which
the engine cannot know otherwise. An `expected_base` would carry a value the engine **already
resolves itself**, from the same three sources in the same order (`VCSX-SPEC.md` Section 6.4; "One
invocation resolves one base"). So the argument adds nothing the engine lacks. It does add a way to
leave the gap open: a caller that does not pass it, or passes the base it resolved without
comparing, gets no check. The precedent #181 cites — `expected_head`, `expected_worktree`, 0169's
base — is honoured by the chosen form, which still conditions the operation on an identity inside
the engine, adjacent to the write.

So `integrate` and `push` compare an open pull request's base against the base the engine resolved,
with no new argument. That covers every caller, including a developer's interactive invocation, and
it puts the read next to the write, which was #181's reason for wanting the engine. #181's
`expected_base` is not adopted.

**Steelman for `expected_base`, the option not taken.** It is explicit: a reader sees the
comparison in the invocation rather than inferring it from the base resolution. It is also
OPTIONAL, so it imposes nothing on an invocation that does not want it. It loses because the value
being compared is not the caller's to supply. The two can only disagree where the caller passes a
base other than the one the invocation resolved, and then the caller should have passed that value
as `base_branch`.

**Steelman for a Symphony-only check**, which is what `symphony-rs` does meanwhile from the
provisioning `status`. It needs no engine change and no new reason. It loses because it is a read
followed later by a write, with provisioning in between, and it is rebuilt by every consumer that
back-merges. That last point is #181's own argument.

## Which operations refuse

Both `integrate` and `push`. `integrate` is the one #180 names, and the check must precede it,
because once the new base is merged into the work branch no later refusal takes it out. `push` is
included because `integrate` is not the only route to the forge: under `ship`,
`push:non_fast_forward` dispatches `integrate`, and a run whose base was resolved after an earlier
back-merge can push without one. `push` already makes the read, so the refusal costs no forge call.
`create_pr` already refuses as `create_pr:base_mismatch`.

`push` runs without a base in some invocations (`VCSX-SPEC.md` Section 13.1: "a `commit`, a `push`
… all run without one"). Where an invocation resolved no base, the comparison has nothing to
compare, and the refusal is scoped to an invocation that resolved one. `integrate` always has one,
since an `integrate` with no base is `base_branch_missing`. Symphony supplies the target on every
invocation it makes (`SPEC.md` Section 9.7), so for Symphony the scoping never opens the gap.

Adding a forge read to `integrate` brings it under the `(any forge)` rows. `integrate:rate_limited`
and `integrate:forge_unavailable` join the registry on the footing `push`'s have: an operation that
**acts** on a forge answer gets both.

## Disposition: park

The mismatch is parked: `needs_caller` with default need `human_review`, and Symphony parks the
issue, as Section 14.2 now states.

- **Not a retry.** A retry re-reads a pull request that still targets the other base. Section 14.2's
  `await_checks` entry is the precedent: a condition that does not clear by being attempted again is
  parked, and a retry only holds a worker slot.
- **Not a failure.** The work is intact. The refusal came before the write, which is the point of
  moving it.
- Section 9.12's unmatched-outcome rule already allows "parked or failed", so park is a permitted
  disposition, not a new one.

`create_pr:base_mismatch` was class `error`, which fails the flow, for the same condition. It is
re-classed `needs_caller` / `human_review`, so the three refusals of one condition share one
disposition. That is a change to the major-stable surface: `VCSX-SPEC.md` Section 8.5 lists "the
class of every listed reason". It is affordable for the reason decision 0073 recorded: the change
impact rounds to nothing while no `MAJOR` is published. `symphony-rs` absorbs it at its re-pin.

## Reasons and the Symphony-side token

The engine reasons are `integrate:base_mismatch` and `push:base_mismatch`, the spelling
`create_pr:base_mismatch` already uses, so a policy keyed on `#needs_caller` or on `*:base_mismatch`
sees one condition. #181 suggested `integrate:pr_base_mismatch`. The shorter form wins on
consistency with the existing reason. Symphony surfaces all three as `pr_identity_mismatch`, the
token Section 9.10 already names for this refusal, so nothing new reaches the broker's verbs.

## An undetermined state fails closed

#181's second question: a forge that cannot report the pull request's base. `push` already refuses
an undetermined state as `push:failed`, because "a state it could not determine is not the absence
of a pull request" (`VCSX-SPEC.md` Section 4.1). `integrate` takes the same rule, `integrate:failed`.
Proceeding would merge into exactly the case this exists to catch. `symphony-rs` asked for fail
closed.

## The operator's repair, and a correction to what the decision sheet offered

Section 9.10 now carries a note: a base mismatch needs no second writer, it does not clear by
itself, and the repair is the operator's.

The decision sheet (`symphony-open-issues-180-181`, `49dab92d`) offered this repair: "relabel back,
or close the pull request and delete the work branch". The second half does not work, and the error
was found while writing the note:

- `pr_state` is keyed on the work branch as head "whatever base the pull request targets"
  (`VCSX-SPEC.md` Section 9.2).
- The work branch is derived from the issue (Section 9.8), so a rebuilt branch has the same name.
- The next run's `push` therefore finds the closed pull request and refuses with `push:pr_closed`.

Closing parks the issue again under a different reason. The note instead names two repairs that do
work:

- **Restore the earlier target.** The next run continues against the pull request it opened.
- **Move the work by hand.** Rebuild the work branch on the new target and retarget the pull
  request to it. The base then matches, and the branch carries only the new history.

It also says that closing alone is not a repair, and why.

Recorded as found here: the specification states no repair for an issue whose pull request was
closed and that should start over. It is not this decision's to settle (trigger below).

## Measurements and checks

- The engine contract was checked against `b04797e`'s text: `push`'s `pr_state` read (Section 4.1),
  the base 0169 added to `pr_state` (Section 9.2), the reason table (Section 4.3), the major-stable
  list (Section 8.5) and the base-less entries (Section 13.1).
- Registry counts recomputed from the Section 4.3 table: 47 rows yield 80 entries, and 22 rows with a
  need yield 33. `conformance/vcsx/README.md` had said 44 and 75, which was already one row behind
  before this decision: `await_checks:no_checks` (decision 0125) was added without the count
  moving. The total is corrected here.

## Decision and reasoning

- **The check.** `integrate` and `push` read the work branch's pull-request state before they write.
  Each refuses an open pull request whose base differs from the base the engine resolved, as
  `base_mismatch` (`needs_caller` / `human_review`), before touching the work branch or the remote.
  An undetermined state refuses as `failed`.
- **`create_pr:base_mismatch`** is re-classed to match.
- **Symphony** parks the issue as `pr_identity_mismatch` (Section 14.2), at the start of the run
  where the back-merge refuses (Sections 9.8, 16.6), and wherever a later operation refuses.
- **Section 9.10** states the operator's two repairs.

## Review finding: the arm the other refusals did not have

Found by `symphony-rs` on #180 (comment 7135611903, against #185's `d213ef7`), after the decision
was applied.

- **The shape.** Section 16.6 gave `engine.integrate` two arms: no usable result, and the new
  `integrate:base_mismatch`. Its comment said the conflict "takes no arm and the attempt
  continues", and nothing gave the remaining results an arm, so they continued too. That includes
  `integrate:failed`, which this decision itself made the fail-closed answer for an undetermined
  `pr_state`, and the two forge-reachability reasons this decision added to the registry.
- **What it did.** The agent started on a work branch the run had not brought up to date, whose
  pull request's base was never checked. The work stayed safe only because `push` makes the same
  check and fails closed at the first push. The agent had then spent a run producing work it could
  not push.
- **Introduced by this decision.** The gap in the `else` branch was older: before 0186,
  `integrate:failed` already continued. But 0186 added the fail-closed case and both forge reasons
  to the set that fell through. It was a repair that left the fall-through it was relying on in
  place: the comment's own reason for the no-result arm, the agent starting "against a work branch
  never brought up to date with its base (Section 10.7)", holds for every refusal.
- **The repair.** The rule is stated positively: the attempt continues past `integrate` only on
  `integrate:ok`, `integrate:up_to_date` or the conflict. Every other result that is not
  `base_mismatch` takes `fail_worker` with the reason surfaced, the Section 9.12 fail-safe "failed"
  disposition. `fail_worker` schedules the backoff retry (Section 16.7), which is what a
  rate-limited or unavailable forge clears by, so one arm serves both. `symphony-rs` suggested
  exactly this split, `fail_worker` for `integrate:failed` and a backoff retry for the reachability
  reasons; in Symphony's vocabulary these are the same exit. Section 9.8 says the same in prose, and
  Sections 17.4 and 18.1.3 carry a check and an item.
- **Steelman for parking the rest instead.** `integrate:identity_missing` and
  `integrate:unsupported` do not clear by retrying, so backoff only holds a slot. It loses on the
  case that motivated the finding: a rate-limited forge does clear, and parking it would hand an
  operator a condition that resolves itself. A repository that wants a specific reason parked can
  say so with a policy edge (Section 9.12).

`symphony-rs`'s own build has the same fall-through (`engine_call.rs:123`, `:130`;
`integrate.rs:78-85`), which they fix on their side.

## Reconsideration triggers

- **A caller that needs to integrate against a base other than the one its invocation resolves.**
  That is the case `expected_base` would serve, and it would reopen the argument form.
- **A deployment that wants a retargeted issue to follow its new target automatically.** For
  example, with Symphony rebuilding the work branch on the new target and retargeting the pull
  request itself. That is a new behaviour with its own trust questions, and park is what keeps it
  out of reach until it is decided.
- **An operator who closes a Symphony pull request to start an issue over**, and finds it parked on
  `push:pr_closed`. That is the gap recorded above: no stated way for a closed pull request's issue
  to start over under the same derived work branch.
