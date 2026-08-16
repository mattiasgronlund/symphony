# Background — 0097 Where the policy comes from, when it is read, and what happens when it cannot be

## Context

Decision 0094 moved the host-side Way of Working onto a branch the agent cannot reach. That fixed
the trust root and left three consequences unhandled, each of which this decision takes.

### The reload machinery describes something that can no longer work

`SPEC.md` Section 6.2 requires dynamic reload:

> The software MUST detect changes to all three configuration artifacts: `WORKFLOW.md`,
> `repo.policy.toml`, and the operator policy config. A `repo.policy.toml` host-side section is
> re-read from the policy branch, its in-sandbox `before:commit` gate from the worktree.

That requirement was written when `repo.policy.toml` was read from a revision the checkout already
held. It is now read from a **remote branch**, so "detect changes" means fetching, on a cadence
nothing specifies. A watch over a remote ref is a different mechanism from a watch over a file, and
the specification asks for the second while describing the first's subject.

### The policy is read far more often than anyone intended

`VCSX-SPEC.md` Section 6.10 opens "A policy is validated before use", and `SPEC.md` Section 9.9
makes each brokered verb a separate engine invocation. Counting for one issue: both `provision`
calls read no policy (Section 4.1 exempts them), the back-merge reads one, `ship` one, `land` one,
and each brokered verb the agent calls one more — bounded in practice by `agent.max_turns`, default
20. So **3 at minimum and roughly 23 at the default ceiling**, per issue, with up to
`agent.max_concurrent_agents` issues running at once.

The cost of that is not the count. Every operation Symphony invokes the engine for is
remote-touching anyway — the broker's verb set is `push`, `back-merge`, `pr` and `request-merge`,
and the agent commits with local git rather than through the broker — so the connection is being
made regardless. The cost is the **failure surface**: 23 places a policy load can fail mid-run, each
needing a disposition, each landing between two operations that have already half-completed the
work.

### Four ways a policy can be unusable, four different dispositions

- The policy branch cannot be read — no disposition at all; the case did not exist before 0094.
- No `repo.policy.toml` was discovered — no disposition except for `provision`, which
  decision 0093's repair exempted. The general case was the original scope of 0094 before that
  decision was reframed onto the policy branch, and it was never closed.
- A discovered file does not parse — `malformed_policy`, the engine refuses to run (Section 6.1).
- A discovered file parses but is invalid — one of Section 6.10's reasons, the engine refuses.

Two of the four are undefined and two are defined, and there is no reason for the split beyond which
ones happened to be thought about. A consumer facing "I cannot use this repository's policy" has one
situation and needs one response.

## Options considered

**For the loading cadence.** Three were live: read per invocation and fetch each time; read per
invocation from whatever provisioning last fetched; read once at work start.

Per-invocation fetching is the only one with zero staleness, and its cost is a fifth entry in
Section 9.1's network-touching capability list, which Section 11 treats as closed and which is how a
consumer knows the fixed set of operations it must mediate. Reading what provisioning fetched costs
nothing in the `daemon` topology, because `provision_for_issue` already runs per issue at worker
start — but it leaves two unbounded staleness windows in `interactive-agent` and `engine-direct`,
where no front-end sequence dispatches provisioning at all.

Load-once wins on neither of those axes. It wins on the failure surface: one load point has one
disposition, where 23 have 23. That is the argument, and the cost analysis above is what makes it
affordable rather than what recommends it.

**For where the load happens.** Load-once implies something holds the policy across many engine
invocations, and the engine cannot: it is pinned and invoked as an external tool, potentially a
fresh process per operation, so there is nothing run-shaped to key a cache on. The consumer holds
it. That is what `VCSX-SPEC.md` Section 3.2 already says — "the consumer sources config by trust" —
and it resolves that sentence's long-standing tension with Section 6.1's "the engine discovers and
reads".

It also dissolves a finding recorded but not closed: no capability in Section 9.1 reads a file at a
revision, so the engine was required to read `repo.policy.toml` from a branch through a plugin API
with no operation capable of it. If the consumer supplies the merged surface, no such capability is
needed. The consumer obtains it through **one engine operation, called once**, rather than through a
capability invoked per read.

**For the unusable cases.** The alternative to unifying was to keep four dispositions and define the
two missing ones consistently with the two that exist. It loses on what a consumer does with them:
the response to "this repository's policy cannot be used" is the same in all four — do not dispatch
new work for that repository, keep the service alive, retry. Four dispositions would be four ways of
spelling one response, and a consumer would have to learn which of them it was looking at before
discovering it did not matter.

What differs between the four is the **repair**, which is why the reasons stay distinct: create the
branch, commit the file, fix the syntax, fix the value. That is diagnosis, and diagnosis belongs in
the reason token and the log rather than in the disposition.

## Decision and reasoning

**`policy_source`** names where host-side policy is read from: `policy_branch` (the default, and
what 0094 established) or `target_branch` (the operator's opt-out, where the policy comes from the
pull-request target and no separate branch is needed). A named mode rather than a boolean, because
the trust guarantee becomes conditional on it and a guarantee is only worth stating if a consumer
can tell which state it is in — which is also what a Conformance Statement reports. Under
`target_branch`, `policy_branch` stops being REQUIRED and `policy_branch_is_target` stops being an
error, since the collision is the configuration rather than a defect in it.

The specification states what the opt-out gives up, in one sentence rather than leaving it to be
derived: the merge path to the trust root reopens, and any per-branch section becomes authorable by
whoever can land a pull request.

**The policy and the workflow are loaded once, at work start.** `WORKFLOW.md` changes timing only —
it stays worktree-sourced, because everything in it runs in-sandbox without credentials, so moving
its source would buy defence against instruction poisoning at the cost of a pull request's ability
to exercise its own gate change. The consumer obtains the merged host-side surface through one
engine operation and supplies it to subsequent invocations.

Section 6.2's dynamic-reload requirement is restated to match: what is re-read at work start is the
policy as of that moment, and a change to the policy branch takes effect for work started after it.
There is no watch over a remote ref, because there is no longer anything to watch — the read is per
run and the run is the unit of currency.

**Four causes, one resolution, four diagnoses.** A policy source that cannot be read, a policy that
cannot be found, one that does not parse, and one that parses invalidly all resolve the same way.
The engine refuses to run and reports `usage_or_config` with a reason naming the cause;
`policy_source_unreadable` and `policy_not_found` join the two that exist. Symphony classifies all
four as `Engine Invocation Failures`, which already covers "a usage or configuration result in which
the policy did not run", and recovers them repo-scoped: skip new dispatches for that repository,
leave other repositories and running workers untouched, keep the service alive.

`policy_source_unreadable` does not distinguish a branch that does not exist from a remote that
could not be reached from a credential that was refused, on the same reasoning
`provision:unreachable` already uses: which of them it was is not something the engine can establish
from the far side of a transport, and a reason per cause would be a registry of the ways a network
fails.

**Retry is backed off, not per-tick.** Today the disposition is "retry on a later tick", which for
an unusable policy means every `polling.interval_ms` — 30 seconds by default — indefinitely, against
a condition that will not clear until a human acts. Retry is therefore backed off per repository,
with the schedule `Implementation-defined` and MUST documented, matching how the adjacent
park-versus-retry choice is already treated. This does not conflict with Section 14.2's "do not
convert to a per-worker backoff retry": that forbids treating a repo-scoped failure as a worker's,
and the backoff here is the repository's.

**Logging carries the diagnosis.** Each failure is logged with the reason token that names its
cause, so the four are distinguishable in the record even though their disposition is not.
Transitions — first failure, each backed-off retry, and recovery — are logged rather than every
evaluation, because the point of the backoff is to stop a condition nobody has fixed from filling
the log.

**Last-known-good is scoped to work in flight.** A policy that was loaded and can no longer be read
stays in force for runs already under way, and new work is refused until it can be read again. That
bounds the window to what is already committed rather than leaving an unbounded period in which the
enforced policy is one nobody can currently see or change. A policy that was **never** loaded has no
last-known-good, so the refusal is immediate — which is the second axis, and the one place the four
causes' uniform resolution splits: uniform across causes, different by history.

Routing that report through `[policy]` edges was considered and deferred as too complicated for now.
It would work — the last-known-good policy is what would route it, which Section 5.6's existing rule
already provides — but it buys a repository a say in a situation whose response is already fixed.

**Reconsideration triggers.** Reopen the loading cadence if a deployment needs a policy change to
take effect within a run rather than at the next one — the evidence is an operator wanting to revoke
a host-side hook and finding that runs in flight keep it. Reopen the unified resolution if one of
the four causes turns out to want a different response: the likeliest is `policy_not_found`, which
for a repository that has never had a policy may deserve to park rather than retry, since nothing
about it is transient.

Relates to 0094 (whose policy branch created the reload and unreadability cases), 0093 (whose
`provision` exemption left the general absent-policy case open), 0092 (whose consumer configuration
carries `policy_source`), and 0002.
