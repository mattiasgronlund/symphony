# Background — 0178 A refused target transitions nothing, and a budget park gets a trigger of its own

## Context

Reported from `symphony-rs` as issue #174, against `86a2188`, found while building that repository's
roadmap D6e and tracked there as decision 0011 R99. Section 9.7's third obligation for an issue
whose per-issue pull-request target is refused:

> SHOULD transition the issue to a configured blocked state where the adapter supports `set_state`,
> so a refused issue leaves the dispatch queue rather than being re-evaluated forever.

Section 17.2 repeats it. Nothing configures a blocked state. Section 5.3.1 has no such key, and the
only place a deployment says where an issue moves is `tracker.transitions`, Section 11.6's
`{from, on, to}` graph. The only trigger that could reach the state is `blocked`, which Section 11.6
groups under "Milestone signals, emitted by the agent through the broker CLI". The published data
is stricter than the prose. `conformance/vocabulary.json` gives `blocked`'s condition as "The agent
signals that it is blocked." A refusal happens before any run, so no agent exists to signal anything.

The report offered two fixes: let the orchestrator fire `blocked` (preferred), or give the refusal
its own trigger or a `tracker.blocked_state` key. `symphony-rs` fires `blocked` today, keyed on the
issue's current state, and records `no_blocked_transition_bound` when nothing is wired.

## The mechanism

**The bullet contradicts the paragraph that ends its own list.** Section 9.7, after the three
obligations:

> The issue is not dispatched and no work branch is created. Correcting the issue's target makes it
> dispatchable again with no other action, which is why the refusal changes nothing else about it.

A blocked state is not in `active_states`. Once the issue has moved there, correcting the target
does nothing: Section 8.2's state-membership condition fails, and a human has to correct the target
and also move the issue back. The section promises recovery with no other action and then
recommends the action that takes it away. Both of the report's fixes keep that contradiction. They
differ only in how the transition is reached.

**A refused target is a Section 8.2 eligibility condition in all but name.** It is a property of the
issue record, it holds until someone changes the record, and changing the record is the whole
recovery. Section 8.2 handles conditions like that by filtering, not by writing. The `Todo` blocker
rule is the precedent: an issue with an open blocker is skipped on every tick, nothing writes to the
tracker, and it becomes dispatchable when the blocker closes. The bullet's justification, "rather
than being re-evaluated forever", describes what Section 8.2 already does with every ineligible
candidate, and filtering costs nothing anyone has asked to bound.

The only costly part of re-evaluating forever is the write, and the second obligation already bounds
it: the comment "is written once per (issue, target) rather than once per evaluation: the daemon
re-evaluates every candidate each `polling.interval_ms`". That bound is written for an issue that
stays a candidate, so the comment bullet already assumes the issue doesn't leave the queue.

**Under `vcs.policy_source = "target_branch"`, any transition reads its table from the refused
branch.** `tracker.transitions` is host-side Way of Working, which Section 11.6 says is sourced from
the protected policy branch. Under `target_branch`, host-side Way of Working is read from the
target. For an issue refused because its target is outside `vcs.base_branch_allowed`, firing any
transition means looking it up in the `repo.policy.toml` of the branch the operator excluded, so the
excluded branch would choose the state the refusal moves the issue to. Section 9.7's boundary
paragraph exists to keep a target from selecting host-side behavior. This argument applies to a
dedicated trigger as much as to `blocked`. It does not apply under `policy_branch`, where the
contradiction above is enough on its own.

**The same undefined disposition appears in Section 8.8, and there it needs a token, not a
deletion.** Budget exhaustion "is parked, not retried: the run is aborted and the issue is moved to
the policy's blocked disposition (Section 11.6)". Section 11.6 has no orchestrator-side token that
reaches one. This case is different from the refusal. It happens inside a run, with the run's policy
already read, so there is no trust problem, and the operator does want the issue moved, because
budget exhaustion does not clear by itself. Reusing `blocked` would make an agent's signal and an
orchestrator's park indistinguishable to the repository wiring them. A repository that sends an
agent's `blocked` to `Needs Info` could not send a budget park somewhere else.

## Options considered

- **Drop the bullet; give the budget park its own trigger** (chosen). Section 9.7 keeps MUST log and
  SHOULD comment once per (issue, target). The issue stays in the queue and is filtered, as Section
  8.2 filters every ineligible candidate. Section 8.8 fires a new run-outcome trigger,
  `token_budget_exceeded`, owned by the OPTIONAL extension (`core: false` in the vocabulary).
- **Let the orchestrator fire `blocked`** (the report's preference). It is the smallest edit, and
  every repository that already wires `blocked` would get the behavior with no further
  configuration. It loses on all three mechanisms above: it keeps the contradiction, it fires a
  transition looked up in the refused target's table under `target_branch`, and it merges an agent
  signal with an orchestrator condition the repository may want to route differently. It also
  needs the published vocabulary's condition text rewritten.
- **A dedicated refusal trigger or a `tracker.blocked_state` key** (the report's second arm). This
  keeps the origins separate, so it avoids the third objection. It still keeps the contradiction,
  and a trigger still reads the refused target's table under `target_branch`. A `tracker.blocked_state`
  key would sit on the operator's side and avoid the trust problem, but it would be the first state
  Symphony writes that the repository's transition graph doesn't own, and it would still contradict
  "dispatchable again with no other action".

## Decision and reasoning

The third bullet comes out of Section 9.7, and the Section 17.2 row follows it. `blocked` stays an
agent signal and the vocabulary entry is unchanged.

For Section 8.8, `token_budget_exceeded` fires when the budget aborts a run attempt, **in place of**
`run_failed` for that attempt. Firing both would give a repository two transitions from one
`from`-state at one moment, and Section 11.6's determinism rule ("at most one transition per
`(from, on)` pair") would not settle which applies. A run attempt therefore ends with one run-outcome
trigger. The spelling repeats the failure category's because the two name the same condition, and
an extension elevating one condition is exactly how Section 14.1 describes `token_budget_exceeded`.
Where no transition binds the trigger, Section 11.6's existing rule applies: no transition happens,
and the issue is parked where it is.

Confirmed on the thread by `symphony-rs`. It has no operator workflow that needs refused issues to
leave the queue, and it removes its orchestrator-fired `blocked` and `no_blocked_transition_bound`.

Left unfixed and noticed while reading: Section 8.8's first bullet says a per-session or per-issue
cap aborts the worker "and requeue[s] that one issue as a budget failure", while its failure
disposition says the issue "is parked, not retried". The two words pull in different directions.
Section 14.2 and Section 17's budget row both say parked, so the disposition is not in doubt, but
"requeue" is a stale word worth a report of its own.

**Reconsideration trigger:** an operator workflow that needs a refused issue out of the active
states, for example a board where active refused issues are noise nobody can filter out. That would
reopen a refusal-driven transition. It would have to come from the operator's side, never from a
table the refused target can supply, and Section 9.7's "no other action" sentence would have to
change with it.
