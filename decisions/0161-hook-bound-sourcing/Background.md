# Background — 0161 Who sets the bound on a workspace hook

## Context

Decision 0160 filed this rather than fixing it: "a `hooks.workspace.timeout_ms` declared in
`WORKFLOW.md` bounding the *host-side* half, which is decision 0158's execution-context axis".

Decision 0158 separated the two halves of a workspace lifecycle point and gave each its own
execution context, working directory, order and failure semantics. It left the one member of
`hooks.workspace` that is not a script body untouched. `timeout_ms` is documented once, for both
artifacts (Section 5.3.4, "Applies to all workspace hooks"), and Section 9.4 spends it on both
halves — "The bound applies to each half, not to the pair." The four bodies are split by artifact
because the artifact fixes where a body runs. The bound is split by nothing, because it does not
run anywhere: it is how long Symphony waits.

Which makes the key the one thing `WORKFLOW.md` declares that the premise licensing `WORKFLOW.md`'s
sourcing does not cover.

## The failure paths

**1. The premise that makes worktree sourcing safe is about bodies, and the bound is not a body.**
Section 15.4 sources `WORKFLOW.md` from the worktree and justifies it in one sentence: "An agent
edit there is harmless: these run inside the sandbox without credentials or host access." That is
true of the prompt template, of the four in-sandbox hook bodies, and of a `before:commit` gate's
unit. It is false of `timeout_ms`, which nothing in the sandbox reads. Section 3.1 says who reads
it: "The executor is the host relative to its own agent sandbox (Section 9.6), so it runs both hook
trust levels (Section 15.4)". The executor runs both halves and waits on both from outside the
sandbox, so the value governs host behavior in both directions and is agent-supplied in one.

Section 5's prohibition does not catch it either. `WORKFLOW.md` "MUST NOT carry credentials,
authorization scope, or any setting Symphony executes with host access" — three things, and a
timeout is none of them. It is not executed; it parameterizes execution. The clause enumerates the
kinds of authority known when it was written, and this key is a fourth: a setting that governs
Symphony's own behavior outside the sandbox.

**2. A one-millisecond bound disarms a trusted teardown half, and nothing fails.** Host-side
`after_run` and `before_remove` failures are "logged and ignored" (Section 9.4). Put
`hooks.workspace.timeout_ms: 1` in the workspace's `WORKFLOW.md` and the host-side `after_run`
half — the credentialed teardown, the half that unmounts a mirror, scrubs a file, or drops a
short-lived token — is stopped a millisecond in, and its failure is discarded by the rule that was
written for a flaky cleanup script. The control does not run and the run reports success.

No commit is needed. Section 5.1 resolves the file "within the working tree the run acts in", so
the copy in the tree is the copy that is read, edited or not. No cross-issue reach is needed either:
Section 9.2 step 5 re-reads `WORKFLOW.md` from that tree at the start of each unit of work, and a
retry attempt on the same workspace is the next unit of work. The agent edits during attempt N and
the bound is in force for attempt N+1, in its own workspace, against the operator's own hook.

**3. A day-long bound satisfies the requirement that exists to prevent it.** Section 15.4 ends with
"Hook timeouts are REQUIRED to avoid hanging the orchestrator." Under the current text the number
that discharges that requirement may be named by the party the trust model exists to contain. And
the defect is not repaired by scoping each artifact's value to its own half: the executor waits on
the in-sandbox half from the host too, so an agent that raises its own half's ceiling holds an
executor open for as long as it likes. What is bounded is a wait, and the wait is the host's at both
trust levels.

**4. The fail-closed sibling, for completeness.** The same one-millisecond value times out the
host-side `after_create` and `before_run` halves, which are fatal to workspace creation and to the
attempt, and 0158's short-circuit then leaves the in-sandbox half unrun. That direction stops the
repository's own runs and is loud, so it is self-denial rather than an attack — but it is the same
mechanism, and an implementation that fixes only path 2 has fixed half a key.

**5. Nothing says which artifact wins.** Section 5.3.4 documents `timeout_ms` once for two artifacts
that both carry the `hooks.workspace` namespace, and no section states a precedence. Where both
declare it, three faithful readings ship — policy wins, workflow wins, last loaded wins — and
the conformance corpus cannot separate them: `vectors/config-defaults.json` asserts
`"hooks.workspace.timeout_ms": 60000` in a flat view whose description says it abstracts "over which
of the three artifacts owns each field".

## What the corpus already decided, one document over

`VCSX-SPEC.md` answers this exact question for the engine's own hooks, and answers it by removing
the key:

> The bound is the consumer's, and `[hooks]` carries no key for it. A `timeout_ms` a repository
> writes here is an unknown key and is ignored (Section 6.1). The reason is Section 3.2: the
> in-sandbox half of this table is worktree-sourced by design, so a bound declared here would be a
> bound the bounded thing sets — a hook that hangs and a hook that raised its own ceiling to a day
> are the same hook — and the engine labels contexts without enforcing the sourcing rule, so it
> never learns which revision a value came from and cannot admit the key host-side while refusing it
> in-sandbox. The bound arrives the way Section 11 has the credential arrive: the repository owns
> which unit runs, and the consumer owns how long the machine will wait for it.

Two halves: a principle, and a limitation. The principle — the bounded thing does not set the
bound — transfers unchanged. The limitation does not. `VCSX-SPEC.md` Section 3.2 says `vcsx`
"labels each policy edge and hook with its context ... but does not itself enforce the sourcing
rule; **the consumer sources config by trust**", and Symphony is that consumer: Section 15.4 reads
each artifact from exactly one revision, so Symphony always knows which revision a value came from.
The fact the engine lacked is the fact Symphony has, which is why Symphony can keep the key on the
trusted revision where the engine had to delete it.

Neither engine document carries a hook-timeout *key* to reconcile with: `grep -c -i timeout
VCSX-CONTRACT.md` is 0 and `VCSX-SPEC.md` is 1, the passage quoted above (repository at `1e33468`).

**Measured prior art.** `symphony-rs` at `3255c9c` implements both sides and its two sides disagree
in the way the specification does:

- `crates/vcsx-hooks/src/runner.rs` refuses the key and records why in the same terms:
  "`§15.4` sources in-sandbox hooks from the **worktree**: a bound stated there is a bound the
  bounded thing sets, and a hook that hangs and a hook that raised its own ceiling to a day are the
  same hook", followed by the cost — "an operator driving many repositories has one bound for all
  of them, and the repository that needs ten minutes forces ten minutes on every other one."
- `crates/vcsx-cli/src/run.rs::hook_bound` is
  `requested.unwrap_or(DEFAULT_BOUND).max(MINIMUM_BOUND)` with both constants at 600 s: a
  consumer-named bound, clamped up to the floor `VCSX-SPEC.md` Section 6.6 fixes so "a repository
  whose `before:commit` gate is its own test suite otherwise runs on one engine and not on
  another". That floor is a portability property, not a trust one — it
  protects the repository from the consumer, which is the opposite direction to this decision.
- `crates/symphony-config/src/flat.rs` carries `hooks.timeout_ms` in the flat view as
  repository-owned, and `crates/symphony-config/src/operator.rs` asserts it: an operator policy
  config naming `hooks.timeout_ms` fails with "the operator policy config named `{absent}`, which is
  repository-owned". So the implementation has the ownership this decision keeps, and no notion of
  which of the two repository artifacts supplies it — there being nothing to implement.
- Recorded in passing, since a later reader will meet it: that same `flat.rs` comment says "The
  corpus asserts `hooks.timeout_ms`", which decision 0158 made false —
  `vectors/config-defaults.json` asserts `hooks.workspace.timeout_ms` today. It is downstream drift
  against a corpus fix, not a finding about this specification.

## Options considered

- **Option A — the key is `repo.policy.toml`'s, read from the policy source, and bounds both
  halves.** A `timeout_ms` in `WORKFLOW.md` MUST NOT be honored. Trade-offs: fixes every path above,
  states the precedence path 5 wants, and keeps the number where the repository can still say it.
  What it costs is authorship distance — a pull request that makes the in-sandbox build slower can
  no longer raise that build's bound in the same commit, because the bound now lives one merge away
  on the policy branch. That is the point of the decision rather than an accident of it, but it is a
  real cost to a repository whose hook bodies and their timing change together. It also leaves a
  repository able to name a long wait on the operator's machine.

- **Option B — the bound is the operator's.** Move `hooks.workspace.timeout_ms` to the operator
  policy config, per repository under `repository.<name>` (Section 5.3.7 resolves entries against
  the orchestrator level leaf by leaf, which is precisely the machinery whose absence made the
  engine record "one bound for all of them" as a cost). Trade-offs: it matches the engine's sentence
  exactly — the consumer owns how long the machine will wait — and it closes the residual Option
  A accepts, since no repository-authored revision names the operator's wait at all. Against it:
  the number is a fact about the repository's hooks, so an operator setting it is an operator
  knowing them, and Section 5 states the opposite as a property — "Configuring Symphony therefore
  needs no knowledge of a repository's policy machine, host-side hooks, transitions, or branch-name
  pattern." Decision 0160 rejected the operator-held `WORKFLOW.md` on this shape of reasoning: the
  smallest edit that matches the implementations was refused because it retracted a stated goal.
  The same argument refuses this one.

- **Option C — an operator ceiling with the repository's value under it.** The operator names a
  maximum, `repo.policy.toml` names its own value, the effective bound is the lower of the two, and
  `WORKFLOW.md` is still ignored. Trade-offs: it gives each party what it owns, and it imitates a
  clamp the corpus already has (`hook_bound`'s `max(MINIMUM_BOUND)`). But the clamp it imitates
  exists to protect a repository's conforming hook from a consumer that configured the bound too
  low — a portability floor, in the other direction — whereas this ceiling would protect the
  operator from the policy branch, which is not the untrusted party in this model. It buys that with
  a new operator key and a merge rule, against a threat the operator has already accepted in full:
  the same policy branch supplies host-side hook bodies that run on the host with the operator's
  credentials.

- **Option D — each artifact bounds its own half.** The tidy split, and the one that keeps
  same-commit authorship. It fixes paths 2 and 4 and leaves path 3 standing: the executor waits on
  the in-sandbox half from the host, so an agent-authored ceiling still holds a host process open
  for as long as it names. A rule that repairs the disarming and keeps the hanging has repaired the
  symptom it noticed.

## Decision and reasoning

**Option A.** `hooks.workspace.timeout_ms` is a `repo.policy.toml` key, read from the policy source
with the rest of that artifact's host-side parts, and it bounds both halves of every lifecycle
point. A `timeout_ms` in `WORKFLOW.md` front matter MUST NOT be honored; whether an implementation
reports it is free, Section 5.3's unknown-key rule being a `SHOULD` about ignoring rather than a
prohibition on diagnosing.

The reasoning in one line: the bound is not consumed inside the sandbox, and Section 5's second
dividing rule gives `WORKFLOW.md` only what is. What remains is a repository-owned setting that
governs Symphony's behavior outside the sandbox, and the artifact for a repository-owned setting the
host acts on is the one sourced from the revision the agent cannot write.

Three consequences are stated rather than left derivable:

- **"Applies to all workspace hooks" survives with a narrower producer.** One value, from one
  artifact, bounding both halves — which is what Section 9.4's "each half, not the pair" already
  meant, now with a source.
- **"Changes SHOULD be re-applied at runtime for future hook executions" loses its producer and
  gains another.** That sentence was written when a repository artifact was watched. Decision 0160
  established that neither repository artifact is (Section 6.2): both are read once at the start of
  each unit of work. The bound in force for a run is therefore the one read when that run started,
  which delivers what the sentence promised by a different mechanism, and the sentence is restated
  to name it rather than to imply a reload.
- **No topology loses the ability to name the bound.** `interactive-agent` (Section 3.4) runs the
  engine's `ship`/`land` over the same `repo.policy.toml`, so the artifact the bound moves into is
  one that topology already reads; what it reads from the worktree is the in-sandbox halves
  themselves (Section 5.1), which is unchanged.

No `Implementation-defined` choice and no MUST-document obligation is created, so no Conformance
Statement row is owed (`CONFORMANCE-STATEMENT-TEMPLATE.md`).

**Reconsideration triggers.**

- A deployment whose operator does not trust a repository's policy branch to bound the operator's
  own machine — a multi-tenant instance running repositories from parties it has not vetted. That
  is the evidence for Option C's ceiling, or for Option B outright, and it arrives as an operator
  asking how to cap a repository's hook timeout.
- A topology where the wait on the in-sandbox half is not the executor's: an agent adapter that owns
  sandbox lifetime (Section 10.9), or a node-scheduler executor (Section 9.11) running the half on a
  machine the orchestrator does not hold open. The argument above turns on one process waiting on
  both halves; where that stops being true, who owns each bound has to be re-derived.
- A repository whose in-sandbox hook body and its timing must change in one commit — a build whose
  duration is a function of the same change that alters it. That is Option D's case, and the answer
  would not be Option D but a way to state a bound in the worktree that can only *lower* the policy
  source's, which is a different decision with a different failure mode to argue.

## What the plan review changed (2026-08-27)

Reviewing the plan before its first edit (`plan-review`, lenses Q, R, C, P) left the decision itself
untouched and changed what the plan reaches.

- **R found a site the plan had not named, and it is the operator-facing one.** Section 14.5
  "Operator Intervention Points" lists editing `WORKFLOW.md` and editing the operator policy config,
  and names no third artifact — so once the bound moves, the operator looking for where to change it
  finds neither the key nor `repo.policy.toml` in the list of things an operator may edit. The plan
  gained a step for it.
- **Q found the plan's own addressing rather than a claim about the corpus.** Eight quoted spans
  were bound to the wrong document because the steps cited section numbers without naming
  `SPEC.md`, and two more were attributed to the section cited nearest rather than the section they
  came from. The plan's steps now name their document, and each quote sits beside its own section.
  Twelve findings from thirteen spans became one, which is a site the plan already records as
  needing no change.
- **P found one sentence being kept whose producer had already gone.** Section 5.3.4's "Changes
  SHOULD be re-applied at runtime for future hook executions" assumed a watched artifact, which
  decision 0160 removed; the surviving producer is the per-unit-of-work read, and the plan restates
  the sentence over it rather than carrying it forward as written.

Implementing it found one more, the same lens one level out. Section 5's `repo.policy.toml` bullet
enumerates what that artifact holds — the branch-name pattern, the action-policy edges and host-side
hooks, the transitions, the task settings, the engine floor — and the plan moved a key into the
artifact without adding it to the artifact's own enumeration. Section 5.6's list gained it by step 5; Section 5's
did not, and a reader sent to `repo.policy.toml` by the `WORKFLOW.md` bullet three lines
above would have arrived at a list the key was missing from.
