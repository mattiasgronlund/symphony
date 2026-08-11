# Background — 0077 A merge lands the head it read, or reports `merge:head_moved`

## Context

Resolves issue #29, raised while implementing Section 12.3 against `a001ea2`.

Section 12.3 had `land` read the pull request and then merge it. Two calls, so a window, and both
named forges report what happens when something lands in it — someone pushed, a bot amended, a
concurrent invocation of this same engine got there first. Section 4.3's six `merge` rows had no token
for it, and the two nearest each routed the caller somewhere wrong:

- `merge:conflict` is `needs_caller`, "The merge would conflict". A repository binding it sends the
  caller to resolve a conflict that does not exist — the branches merged cleanly a second ago and will
  merge cleanly on the next attempt.
- `merge:rejected` is `error`, "Branch protection or forge policy refused the merge". It blames a rule
  nobody configured. An operator goes to read branch protection, which is fine, and finds nothing,
  which is not.

GitHub names the condition separately from everything else on that endpoint — `409`, "Head branch was
modified. Review and try the merge again", with `405` reserved for a pull request that is not
mergeable, where a real conflict and a failing gate land. Forgejo does not separate them, which is
itself evidence that the condition had no agreed name to be reported under.

The report asked the question underneath rather than for a token: **what does an operation report when
the state it was asked about moved underneath it?** `push` answers `non_fast_forward` — `needs_caller`,
recovery in the gloss, routing pinned by Section 13.1, retry bounded by Section 5.6. `merge` answered
nothing, and `create_pr` has the same window.

## The argument that decided it, which the report does not make

Both shapes the report offers — the universal `failed`, or a `merge` reason for the condition — treat
the forge's refusal as the thing to name. **The dangerous case is not the merge that gets refused. It
is the merge that succeeds.** GitHub's endpoint merges whatever the head currently is; its `409` is
opportunistic race detection, not a guarantee. The evidence is the parameter's own existence: if the
endpoint reliably refused on any head change, `sha` would be redundant.

So a decision that only mints a token mints it for a symptom the forge reports at its discretion, and
leaves untouched the path where `land` merges content no lifecycle position inspected. That path is not
hypothetical: for a squash strategy `before:merge` is where the pull request is read *and* where
`pr_to_squash` transforms its title and body (Section 10.3), and Section 6.6 lets a repository put a
blocking scan at the same position. Without a conditional merge, `land` can merge a revision the gate
never saw and write a squash message describing a revision that is not the one squashed.

Both forges expose the parameter, verified rather than assumed:

- **GitHub** — `sha`, "SHA that pull request head must match to allow merge".
- **Forgejo / Gitea** — `head_commit_id`, confirmed against Codeberg's live `swagger.v1.json`:
  `MergePullRequestOption` carries `Do`, `MergeCommitID`, `MergeTitleField`, `MergeMessageField`,
  `head_commit_id`, `force_merge`, `merge_when_checks_succeed`, `delete_branch_after_merge`.

## Options considered

- **Option A — no token: name the condition under `merge:failed` and forbid the two misroutes
  (rejected).** It passes 0073's own test for minting a token, restated by 0075 — `base_unavailable`
  was earned because a *built-in loop* was misdiagnosing, and Section 12.3 had no loop. Rejected
  because the test is about whether a wider token *fits*, and here it does not: `failed` is class
  `error` and this is a state a caller acts on, which is Section 4.2's definition of `needs_caller`.
  That is a class argument rather than a convenience one, which is the bar 0075 said would carry.
- **Option B — mint `merge:head_moved`, leave the window open (rejected).** The report's first shape.
  Rejected on the argument above: a token for a condition no backend can reliably detect, reported
  where the forge chooses to report it, with the merge-that-succeeds path untouched.
- **Option C — Option B plus a merge conditioned on the head that was read (chosen).**
  `request_merge` takes `expected_head` and MUST NOT merge a pull request whose head is no longer
  that. The condition becomes deterministic, so every backend reports it alike, and what
  `before:merge` inspected is what gets merged or nothing is.
- **Option D — Option C with the guarantee softened to "best effort, document the residual window"
  for a forge with no such parameter (rejected).** It converts a correctness property into a
  documentation obligation, which is below this document's bar everywhere else. Section 9.3 already
  has the honest disposition for a capability a backend cannot provide, and no surveyed forge needs
  it.
- **Option E — route the retry through policy rather than Section 12.3 (rejected).** Keeps `land`
  three lines. Rejected on token economy, below.

## Decision and reasoning

`merge:head_moved`, class `needs_caller`, gloss "The pull request's head advanced after it was read;
re-read then retry". `request_merge(pr, strategy, expected_head)` MUST NOT merge a pull request whose
head is no longer `expected_head`. Section 12.3 loops: re-run `before:merge`, re-issue the merge with
the fresh head, bounded by Section 5.6.

**The mechanism stays the backend's.** The specification states the required refusal and names no API,
as 0075 stated the required distinction and left `git ls-remote --exit-code` to the backend. A backend
whose forge offers no means of conditioning the merge does not declare the capability (Section 9.3),
so the condition surfaces as `capability_unsupported` at validation or `merge:unsupported` at first
use — machinery that already exists, rather than a new escape hatch.

**Why the routing is built in, which is the token-economy argument.** Routed built in, the engine mints
**one** token: `merge:head_moved` never terminates an invocation, so no `need` is required, and a
repository that overrides the routing supplies its own reason to `escalate` (Section 5.2). Left to
policy, the engine mints **two**: Section 5.4's built-in default for an unmatched `needs_caller` is
`escalate`, Section 8.2 makes the escalation present exactly then, and none of Section 8.4's needs
fits — `integrate_then_retry` names `integrate`. Two further reasons: the report's whole frame is "push
already answers this", and Section 12.2's routing is built in with Section 13.1 pinning it, so a
policy-only routing would leave `merge` asymmetric one layer down; and the retry is sound only because
it re-gates, which a built-in loop guarantees and a `run_op` edge does not obviously do — see below.

**The retry re-enters the position, not the operation.** That is what makes it converge on something
correct rather than merely converge: `before:merge` is where the pull request is read and where
`pr_to_squash` runs, so a retry that re-merged without re-gating would reintroduce exactly the defect
the conditional merge closes.

**A question this surfaced and did not answer.** Whether a policy edge's `run_op("merge")` runs
`before:merge` at all is not settled by the document: Section 12.2's pseudocode calls
`run_lifecycle("before:push")` *and then* `run_op("push")`, which reads as the sequence owning the
gate, while Section 4.1 calls the gate a property of the operation, Section 13.1 says a block surfaces
"at every gated operation", and Section 8.6 contemplates a policy routing `status:ok` to `commit`,
which would skip `before:commit` under the first reading. The built-in loop is correct under either
reading; a policy-only routing would have been correct only under the second. Filed as issue #30
rather than settled here — it is a Section 5.2 dispatch question over every gated operation, not a
`merge` question.

**A second one, and why it is not folded in.** The conditional merge closes the `before:merge` window
as a consequence, but the same window exists at every position: a gate inspects a read and the
operation performs its own, and `before:commit` — the in-sandbox content gate — has no cheap identity
for the state it inspected the way a pull request has a head. That is a Section 6.6 correctness claim
rather than a Section 4.3 registry claim, so it is issue #31 and this decision does not wait for it.

**What the fix costs.** A capability signature changes, which no reason addition would have — recorded
as an anchor change. That is affordable now and will not be cheaper later: 0073 restructured Section
9.1 with five new capability names and an opaque ref handle, the realizing implementation absorbed that
churn in one slice, and the document is Draft v1. The loop also re-runs `before:merge` hooks on each
turn, which is new for `land` and not new for the engine — Section 12.2's loop re-gates `before:push`
the same way.

**What would make us reconsider**, named rather than left implicit: a forge in real use whose merge
cannot be conditioned on the head. Option D is then the fallback, and the cost of having chosen C first
is one `MINOR` release relaxing a MUST — cheaper than the reverse, which would be a correctness
property nobody could rely on having ever been true.

Relates to 0075 (whose `pr_state` value this extends with the head, and whose "state the distinction,
leave the mechanism" precedent this follows), 0076 (which lands first and rewrites `pr_state`'s answer,
including the undetermined case that leaves `land` with no expected head), 0057 (whose universal
`failed` Option A would have used), 0060 (whose flow bound makes the retry terminate), and 0051 (whose
derived registry gains the token).
