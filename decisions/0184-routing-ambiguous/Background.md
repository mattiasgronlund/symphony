# Background — 0184 One condition reported under a spelling, and its sibling under none

## Context

Reported as issue #171 from `symphony-rs`, against `86a2188`, and settled in that thread at
`b04797e`. `SPEC.md` Section 8.7 (Multiple Repositories and Shared Polling) says an issue the
mapping matches to more than one repository "is not routed and not dispatched, and the condition is
reported to the operator", and names no token. One section over, decision 0175 gave Section 8.5
Part B's standing-condition report a REQUIRED token, `standing_condition_lost`, whose `routing`
reason covers a running issue that has become ambiguous. So one implementation reports the mapping
naming several repositories under a REQUIRED spelling when it stops a run, and under nothing when it
declines a dispatch. An operator filtering the record sees the second only as free text.

Decision 0175 recorded this as left unfixed and predicted it might "genuinely belong to a failure
class". Two spellings were already in circulation when the issue was filed:

- `symphony-rs`'s `step.rs:1554` emitted `ambiguous_repository_mapping`;
- `conformance/vectors/issue-routing.json` used `multiple_rules_matched`. That is wrong on its own
  terms: the same file's `two-rules-match-same-repository-named-twice` has multiple rules matched
  and is not refused.

## Why a token of its own, and not Part B's

The issue offered two shapes: give Section 8.7's report its own token, or state that it is
reported under Part B's token, "the two being one condition observed at two moments". The second
is the smaller edit. It does not hold, because they are not one condition.

- Part B's `routing` reason means a fresh evaluation no longer names the repository the run holds.
  That has three outcomes: no repository, a different one, or several. Only the third is an
  ambiguity.
- Section 8.7 itself says that at dispatch "there is no earlier answer to compare against", so
  nothing has been lost.
- `standing_condition_lost` reports a stop and this reports a refusal. Sharing the token would make
  a filter for stopped runs count issues that never ran.

One issue can correctly produce both: `standing_condition_lost` with reason `routing` on the
refresh that stops the run, then `routing_ambiguous` on each later tick that declines to dispatch
it. `routing_ambiguous` is the noun Section 8.5 already uses ("a reported routing ambiguity").

## Why it is not a failure class, which corrects decision 0175

0175 called the ambiguity "an operator's configuration defect" that is "wrong until edited". Take
one repository with a rule on `labels: backend` and another on `labels: frontend`, and an issue
someone labels with both. The configuration has not changed and is still valid; the repair is a
label edit on one issue. That is exactly why Section 8.7 states the rule over the issue and not over
the configuration. The candidate fetch succeeded and the mapping answered, so nothing failed.

Both `workflow_config_failures` dispositions in Section 14.2 are also wrong for it, as they were for
Part B in 0175:

- "Skip new dispatches" stops the whole instance over one issue.
- The workflow-file disposition retries a run attempt that does not exist.

So the report carries no class, and Section 14.2 states its disposition beside the other
non-failures: not dispatched, not retried, not failed; no claim, no running entry and no retry
entry; the issue stays a candidate the next tick evaluates again. `symphony-rs`'s
`routing::AmbiguousRouting` carried `FailureClass::WorkflowConfig`, which decision 0011 **R86** chose
as "the least wrong of the nine". That choice is retired here, as 0175 retired it for Part B.

## The report's scope, which the implementation side found

The first proposal put the report in a new `dispatch_issue` branch for an issue with no single
repository. `symphony-rs` pointed out that this reports only issues that already passed eligibility,
while their build evaluated routing earlier, in `dispatch_target` (`step.rs:685`, retry fire
`:1157`), ahead of `should_dispatch`, and asked:

> Is `routing_ambiguous` owed for every candidate the mapping overlaps, or only for an issue
> otherwise eligible to dispatch?

Two implementations following different readings report different sets of issues, so the scope has
to be stated. The answer is neither of the two: the report is owed for an issue that fails none of
Section 8.2's conditions **over the record** — field presence, state membership,
`tracker.required_labels`, `tracker.assignee` and the `Todo` blocker rule — whatever the instance's
own state. The `running` and `claimed` memberships and both concurrency limits do not gate it.

**Against "only an otherwise eligible issue".** Full eligibility includes `running`, `claimed` and
both concurrency limits, and those describe the instance, not the issue. If they gate the report,
the same overlap is reported or not depending on load, and a saturated deployment hears nothing
about an issue it will never be able to run. The build's own shape showed it: the check sat after
the `global_slots(state) == 0` break (`step.rs:680`), so a tick with no free slots reported nothing.
A report that follows capacity cannot be checked from the record and the mapping, which is the
comparability the token exists for. This is why Section 16.2's `on_tick` now evaluates routing for
every candidate ahead of the dispatch loop, which also lines the pseudocode up with the tick
sequence in Section 8.1: it routes at step 3 and dispatches at step 5.

**Against "every candidate" (the option not taken).** Steelman: it is the simplest rule, it is
closest to Section 8.7's "each polled issue", and it needs no reference to Section 8.2 at all. It
loses because it reports issues that were never going to run here. Section 8.2 tests
`tracker.required_labels` and `tracker.assignee` over the record, so on a shared tracker those can be
what separates this instance's issues from another's. An instance would then report, at tick rate,
overlaps on issues no one meant it to touch, and an operator would learn to ignore the token. The
cost of not reporting them is small: nothing is withheld from an issue that could not dispatch
anyway.

**What the rule costs.** A blocked `Todo` issue with an overlap goes unreported until its blocker
clears. The operator then hears about it at the moment it starts to matter, and no earlier.

## The report names every repository

The record names every repository the mapping matched (Section 13.1), for the reason a routing stop
names the repository it held: without the whole overlap an operator cannot see which rules to
separate. The implementation side asked for "every" explicitly, because "the repositories matched"
could be read as satisfied by two, and their `Routed::Ambiguous { first, second }`
(`routing.rs:173`) stopped walking at the second distinct repository (`routing.rs:246`). A new vector,
`three-repositories-match`, pins it. How the list renders, and the log level, are not fixed: the
specification fixes the token and the content, as it does for Part B.

## Left out on purpose: how often it is reported

`symphony-rs` reports on every tick that reaches the check, for as long as the overlap lasts, and
that stays conforming. Reporting once would need a per-issue record, and that record would owe a
recovery class (Section 14.3), as the Section 9.7 comment key did in #176. There is no evidence the
repetition hurts anyone.

## The registry: 0175's second trigger, arrived

0175's second trigger was "a fourth non-failure token appearing in Section 14.2", at which point the
set wants publishing together. `routing_ambiguous` is that token. `conformance/vocabulary.json`
gains `non_failure_conditions`: `routing_ambiguous`, `standing_condition_lost` with its three
reasons, `await_checks:still_pending`, `await_checks:budget_floor` and `token_budget_exceeded`
(`core: false`). The group is `exhaustive: false`: Section 14.2 lists its members without closing the
list, and one member is already an OPTIONAL extension's. Two vector-file notes that called their
labels unpublished are rewritten: `issue-routing.json`'s and `standing-conditions.json`'s. The
second had been stale since 0175 named its reasons. `symphony-rs` noted that the new group fails
their `xtask vocab` gate until they render it, which is the gate working.

## Decision and reasoning

Section 8.7's report carries the REQUIRED token `routing_ambiguous` and names every repository the
mapping matched. It is owed for an issue that fails none of Section 8.2's conditions over the
record, whatever the instance's own state. It is not a Section 14.1 failure class, and Section 14.2
states its disposition. Both dispatch sites report: `on_tick` ahead of its dispatch loop, and a retry
fire after `should_dispatch`, returning with the issue released. `dispatch_issue` keeps a branch
that returns for an issue with no single repository, without reporting, because both callers have.

## Reconsideration triggers

- **An operator shown to need the overlap reported while a record condition still holds the issue
  back** — for example a blocked `Todo` issue whose overlap they wanted to fix before the blocker
  cleared.
- **Tick-rate reports seen drowning a real log.** That is the evidence for reporting once, and for
  the per-issue record and recovery class that would cost.
- **An ambiguity shown to be configuration-only**, with a preflight check that could catch every
  case. Two entries that both configure no `routing` could be caught that way today; the label case
  above cannot, which is why the rule stays per issue.
