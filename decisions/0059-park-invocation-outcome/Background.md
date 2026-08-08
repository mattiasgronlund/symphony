# Background — 0059 A parked flow is `needs_caller` with the `intervention` need

## Context

Issue #3. `VCSX-SPEC.md` Section 5.2 defines `park` as "stop the flow and hold for intervention without
failing it", and Section 6.5 lets a repository write `do = "park"` on any edge, so a parked flow is an
ordinary outcome of an ordinary, correct `repo.policy.toml`. Section 8.2 offers four invocation statuses
and maps none of them to it.

Elimination narrows it to one:

- Not `ok`, which Section 8.2 defines as "all steps `done`" — a parked flow stopped short of the entry's
  intended effect.
- Not `error`: Section 5.2 says `park` does not fail the flow.
- Not `usage_or_config`, which Section 8.2 reserves for "a run in which the policy did not run" — this
  policy ran, and ran correctly.

That leaves `needs_caller`, reached by elimination rather than by anything the document says. What makes
it worth a decision rather than a shrug is Section 8.3: status maps to exit code, so two conforming
engines could give the same `repo.policy.toml` different exit codes for the same run. Unlike a malformed
input or a non-terminating graph, this changes the answer for a policy that is doing exactly what it was
written to do.

Implementing it surfaced the sharper half, recorded as a comment on the issue: Section 8.2 has no
**shape** for a parked envelope either.

- `op` / `reason` / `class` are described as "the decisive operation result" and permitted to be null
  only "for a clean `ok` with no decisive operation". A parked flow has no decisive operation result —
  the policy stopped it, not an operation. Reporting the last result the flow saw would be wrong twice
  over: it is typically `done`-class (a `push:ok` on the way to a park edge), so it would tell the caller
  an operation asked them something when none did, and it would put a `done`-class reason under a
  `needs_caller` status.
- `escalation` is "present exactly when `status == "needs_caller"`". A parked flow must therefore carry
  an escalation, which requires a Section 8.4 `need` token — and of the four named,
  `integrate_then_retry`, `resolve_conflicts` and `await_checks` each name a specific remedy that a park
  does not have, leaving `human_review` fitting only by elimination.

### What actually separates `park` from `escalate`

The two documents already draw the line; Section 8.2 is where it stops being visible.

- **`escalate(reason)` names something; `park` names nothing.** `escalate` takes a `need` token from
  Section 8.4's vocabulary, and that token is a binding key. `park` takes no argument.
- **`escalate` has a resolver; `park` has none.** `VCSX-CONTRACT.md` Section 5.6 is titled "Abstract
  `escalate`": the action names a point where the flow cannot proceed autonomously and the *front-end*
  supplies the resolver. `park` is not abstract — Section 5.2 gives it one meaning and no binding step.
- **An escalation is expected to resume; a park is not.** Section 5.5: an embedded driver "binds
  `escalate` to its own resolver — for example creating an agent-assigned task — and resumes the flow
  when the need is met"; interactively, "the human resolves and re-invokes." Nothing says a parked flow
  resumes.
- **`escalate` is the front-end divergence point; `park` is not.** Section 5.5 closes with "`escalate` is
  the single point at which their behavior legitimately differs" — that is its purpose. `park` behaves
  identically under both front-ends.

Underneath is a consistent aim of fire. `needs_caller` (Section 4.2) means "the caller — the agent, the
human, or the driver", and under a driver an escalated need becomes an *agent-assigned* task;
`VCSX-CONTRACT.md` Section 8 pairs parking with the other case, "`need-help` is an agent-created
**human-assigned** task that parks for feedback." Symphony's `SPEC.md` uses it the same way:
`token_budget_exceeded` "is parked, not retried", and a second breach "parks terminally". A park is the
shape for *no automated party can move this*.

That is what makes the token choice load-bearing rather than cosmetic. If a parked flow escalated with
`human_review`, Section 5.5 would instruct an embedded driver to bind a resolver by that token and resume
the flow when the need is met — so a conforming driver would auto-resolve a park and continue, which is
not "hold for intervention".

### Two adjacent holes on the same path

Both are fixed here, because leaving them reproduces the same defect one step over:

- Section 8.4 states escalation's `op` as "the `op` that produced it" with no null case, yet a policy may
  escalate — or park — on a signal or at a lifecycle position, where no operation produced anything. This
  is not new with `park`: `blocked → escalate("human_review")` already has it today.
- Section 8.2 never states that `class` and `status` agree, though "the overall proto class" implies it.
  That implication is exactly what rules out reporting `push:ok` under a parked flow, so it has to be
  said out loud for the parked shape to be derivable rather than argued.

## Options considered

- **Option A — `needs_caller`, with a new `intervention` need and a null `op`/`reason`/`class`
  (chosen).** Trade-offs: adds one token to a vocabulary Section 8.5 already permits a `MINOR` to extend,
  and keeps every existing envelope rule intact — "escalation present exactly when `needs_caller`" holds
  without exception, and the null case is the one Section 8.2 already has, widened by a second entry.
  A front-end can tell a hold from a request by token, so Section 5.5's driver rule stays honest. Cost:
  a fifth `need`, and a MUST NOT that applies to only one member of the vocabulary.
- **Option B — `needs_caller`, with `human_review` covering it.** Trade-offs: the cheapest change, one
  sentence, no new token. But it collapses "the policy held this flow" into the token Section 12.2
  already emits for `push:pr_closed`, so a driver cannot distinguish them; and Section 5.5 would then
  have a conforming driver bind a resolver and resume a parked flow, which contradicts Section 5.2.
  Rescuing it needs a carve-out sentence in Section 5.5 — trading a token for an exception, and an
  exception is the worse of the two because it makes a general rule conditional.
- **Option C — `needs_caller` with no escalation**, relaxing "exactly when" to "when the flow escalated".
  Trade-offs: adds nothing to any vocabulary and the wire shape already permits null there, which is why
  the implementation that filed the issue took this reading. But it converts a total rule into a
  conditional one, and a caller reading exit `10` can no longer assume a payload — so a parked flow
  becomes indistinguishable from an engine bug that dropped the escalation, which is precisely the
  "reported, never silently dropped" property Section 5.4 is built on.
- **Option D — a fifth invocation status for a parked flow.** Trade-offs: the cleanest semantics, and it
  needs neither a new `need` nor a null relaxation. But Section 8.5 makes the invocation status values
  and the exit-code mapping major-stable, and every caller branching on the existing four would fall
  through on the new one. Paying a major-surface change to avoid a `MINOR`-compatible token addition is
  the wrong direction.
- **Option E — `needs_caller`, reporting the trigger the flow parked at when that trigger's class agrees
  with the status.** So `merge:conflict → park` reports `merge:conflict` and `push:ok → park` reports
  null. Trade-offs: it preserves information wherever doing so is coherent, and it makes the
  class-agreement invariant a definition rather than a constraint. Rejected because a consumer must
  handle the null case regardless — the signal and lifecycle-position parks have nothing to report — so
  the rule adds a case without removing one, and two parks would then carry different envelope shapes for
  a difference the caller did not ask about. The parked-at trigger remains available in `message` and in
  the escalation's `detail`.

## Decision and reasoning

Choose **Option A**. A flow the policy stopped with `park` ends the invocation at `needs_caller`
(exit `10`), carrying an escalation whose `need` is `intervention` — Section 5.2's own word for what a
park is holding for — with `op`, `reason` and `class` null.

Three properties carry the decision.

**`intervention` is the one need no front-end resolves.** Every other need names something a caller can
supply; this one names a hold. Section 8.4 therefore states that a front-end MUST NOT bind a resolver to
it and MUST NOT resume the flow on it — the hold is released out of band, by a new invocation. That
single restriction is what keeps Section 5.5's claim true: `park` reaches the same envelope as `escalate`
without becoming a second point at which the two front-ends legitimately differ, because both do the same
thing with it. It also makes the `park`/`escalate` distinction readable in the envelope rather than only
in the policy that produced it, which is what a consumer branching on exit `10` actually needs.

**The null case is stated by defining what "decisive" excludes.** Section 8.2 gains the invariant it only
implied: where `op`/`reason`/`class` are non-null, `class` is the class `status` reports — `done` under
`ok`, and the same token under `needs_caller` and `error`. With that said, a parked flow's null envelope
follows rather than being asserted: the policy ended the flow, no operation asked the caller for
anything, and the last result the flow saw could not be reported without putting a `done`-class reason
under a `needs_caller` status. The invariant is worth more than the parked case that motivated it,
because it is the property a reviewer can check the next time a terminal action is added.

**Totality over the trigger kinds, not just over `park`.** Section 8.4's escalation `op` is stated
nullable, with the two cases named: at a signal, and at a lifecycle position, where the gated operation
has not yet run. That is the same class of defect as the status gap — a rule quantified over operations
meeting a trigger that is not one — and decision 0057 already paid for learning it once.

**Deliberately left open and recorded.** `fail(reason)` has the mirror-image question: an explicit
`do = "fail"` on a `done`-class trigger yields `status == "error"` with no `error`-class result to
report, and it is not settled here what `fail`'s own `reason` argument is — a Section 4.3 token, a
Section 6.10 token, or free text. The class-agreement invariant constrains the answer but does not pick
it, and picking it needs the `fail` reason question answered first, which is a different question from
the one issue #3 asks. Issue #4's bounded traversal has the same shape as the parked case and is left to
its own decision; the invariant added here is what that decision builds on, since a budget exhausted
after `push:ok` also ends a flow with nothing decisive to report.

We would reconsider if a front-end appeared with a legitimate automated response to a park — at which
point `intervention` would stop being the un-resolvable need and Option E's finer envelope would start to
pay for itself.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 5.2, 5.5, 8.2, 8.4, 13.1), the
vocabulary registry, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. It resolves issue #3. Relates to 0044
(whose `Engine Invocation Failures` class consumes the status this fixes), 0056 (which added
`usage_or_config`, the last invocation status to be found missing), and 0057 (the same
rule-outruns-its-enumeration shape, one section over).
