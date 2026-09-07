# Background — 0167 Did the engine run, and separately, what did it answer

## Context

Reported from `symphony-rs` as two issues against `5a4fdf7`, and recorded as one decision because
they are one defect at two sites.

- **#143** — `Section 16.5`'s `ensure_object_store` comments every failure
  `# Repository Provisioning Failures (Section 14.1)`, while `Section 14.1` class 7 gives "the VCS
  engine is unavailable" its own number.
- **#148** — `Section 16.6`'s `run_agent_attempt` checks the failure of every step it takes except
  `engine.integrate`, where a postponed merge conflict and an engine that never ran share one
  silence.

Measured at `75a258d`, `Section 16` contains exactly two engine dispatches:

```
$ awk '/^## 16\. /,/^## 17\. /' SPEC.md | grep -n 'engine\.'
284:  result = engine.provision(repo, store_location = store_path)
341:  engine.integrate(issue, workspace)
```

One labels every failure with the domain class; the other checks none. In both, the missing
distinction is the same: **did the engine run**, and separately, **what did it answer**.

## The mechanism

**The distinction is already total, already free, and already held up by this specification as the
example to follow.** This is the fact that decides the shape of the fix rather than merely
motivating one. `VCSX-SPEC.md` Section 8.3 (Exit Codes) fixes four status-bearing exit codes —
`0` `ok`, `10` `needs_caller`, `20` `error`, `2` `usage_or_config` — and then closes the set:

> `1` — the invocation produced no result at all (below); this is not an invocation status.
> ... **Any exit code other than the four status-bearing ones means the same thing**, which is what
> makes a caller's mapping total without this specification enumerating the ways a process can end.

So a caller separates "the engine ran and answered" from "no result" **without parsing anything**,
and the mapping is total by construction. Section 8.2 supplies the second half: `usage_or_config` is
the status "for a run in which the policy did not run". Class 7's four bullets land on exactly those
two conditions — no readable envelope, or an envelope whose status is `usage_or_config` — and class
7's own boundary says so from the other side:

> Important boundary: this class covers only failures in which the policy never ran.

`SPEC.md` already knows this. Section 10.7 (Agent Runner Contract) argues the agent adapter's
evidenced-success rule by pointing at the engine as the model:

> The engine contract already works this way — an engine's result is evidenced by a composed
> envelope and an exit code outside its four status-bearing ones means no result at all
> (`VCSX-CONTRACT.md`, `VCSX-SPEC.md` Section 8.3) — so a conforming implementation already builds
> this discipline for the one subprocess whose contract this specification defers to, and this
> states it for the other.

That is the finding. The specification holds the engine's envelope up as the discipline it is
teaching the agent adapter, and then its own two engine call sites do not branch on it.

**What the collapse costs at `ensure_object_store` is a misfiled class with a different blast
radius.** Class 2's own first bullet conditions on a result existing — "Classified from **the
engine's typed provisioning result** (Sections 9.7, 16.5)" — so an engine that is not installed
produces nothing for it to classify. The two classes then part company in Section 14.2, and not
cosmetically:

```
$ awk '/^### 14\.2 /,/^### 14\.3 /' SPEC.md | grep -n -i 'every repository'
49:  - An unavailable or non-conforming engine skips dispatch for every repository that requires one,
```

Class 2 skips dispatch for the affected repository and leaves others unaffected. Class 7 does that
for a `version_floor` or a policy failure — both repository-declared — and widens to the whole
instance for an unavailable or non-conforming engine, "because no repository's policy can be
executed". Misfiling an absent engine as class 2 therefore keeps every other repository dispatching
against an engine that is not there.

**What it costs at `engine.integrate` is a wrong-state run rather than a failed one.** The comment
there explains a postponement — "postpone if it would conflict (resolved later only if a push is
rejected)" — which is an outcome of an operation that *ran*, owned by the action-policy machine
(Section 9.12) and correctly not fatal. An engine that could not be invoked produced no such
outcome, and the attempt proceeds to run an agent against a work branch never brought up to date
with its base, then push it. Section 10.7 refuses this trade at the neighbouring seam in one line:
"A failed run retries; a wrongly successful one lands."

**The collapse is not confined to Section 16, and that is the part neither issue found.** Checked at
`75a258d`:

```
$ awk '/^## 17\. /,/^## 18\. /' SPEC.md | grep -c '14\.2'
4
$ awk '/^## 17\. /,/^## 18\. /' SPEC.md | grep -c -i 'every repository'
0
```

Four Section 17 checks cite Section 14.2 and every one of them asserts the narrow scope — a
`WORKFLOW.md` failure blocking no other repository, a storage failure retried repo-scoped, the four
unusable-policy conditions skipping "that repository's" dispatches, a provisioning failure leaving
the issue unclaimed. Section 14.2's one wide clause has no check at all. `symphony-rs` reports the
consequence from the far end: its build maps both `EngineInvocation` and `RepositoryProvisioning`
onto a single repository-scoped disposition, passes every check, and its own traceability cell
records the collapse *approvingly* — which against the check text it is. That is evidence about the
check list rather than about that build.

Section 18 is worse than silent, because it states the narrow scope for the wide condition
outright:

```
$ awk '/^## 18\. /,/^## 19\. /' SPEC.md | grep -n 'repo-scoped'
76:  `repository_provisioning_failures` and recovered repo-scoped (skip the repository's dispatches,
220:  run as `engine_invocation_failures`, recovered repo-scoped per Section 14.2
```

Line 76 is correct: it is conditioned on "classified from the engine's typed result". Line 220 is
Section 18.1.4's engine bullet, and it names "an unavailable or non-conforming engine" among the
conditions "recovered repo-scoped per Section 14.2" — citing, as its authority, the section whose
next bullet says the opposite. An implementation reading Section 18 as its definition of done is
told the wrong disposition for the one condition that has a different one.

## Options considered

- **Option A — split at both call sites, once.** State the two-layer rule where Section 16
  introduces its engine dispatches; narrow `ensure_object_store`'s comment; give `engine.integrate`
  a failure arm for the no-usable-result case; route that arm to Section 14.2's disposition rather
  than to the worker's; give the wide clause a Section 17 check; correct Section 18.1.4.

  Trade-offs: the largest of the three. It reaches Sections 7.1, 7.3 and 8.5 as well, because a new
  worker-exit arm is a new site in the claim partition Section 8.5 states.

- **Option B — fold class 7's "engine unavailable" bullet into class 2 and drop it from class 7**
  (#143's second option, offered by the report as a coherent alternative).

  Trade-offs: it is coherent, and it is the cheaper repair — one bullet moved, no algorithm change,
  and `Section 16.5`'s comment becomes true as written. It loses on what it silently discards: the
  two classes have different blast radii in Section 14.2, so folding them collapses an instance-wide
  skip into a repo-scoped one. The specification would then say, of an engine that is not installed,
  that other repositories are unaffected — while none of them can execute a policy either. The
  option repairs the comment by making the specification wrong about the world.

- **Option C — confirm the silence at `engine.integrate` is total** (#148's reading 1): an engine
  invocation failure at that step is deliberately not fatal, and the specification says what a run
  does with an un-integrated work branch.

  Trade-offs: it is the only option that requires no algorithm change at all, and it has a real
  argument behind it — the back-merge is a convenience, and a run that skips it still produces a
  pull request the forge will refuse to merge if it has diverged. That argument does not survive
  Section 9.10: the run pushes and opens a pull request, and Section 10.7's rule is that a wrongly
  successful run lands. There is no disposition that makes an unannounced un-integrated run safe, so
  the silence cannot be deliberate for that arm.

## Decision and reasoning

**Option A**, and the reason it is worth its size is that the two smaller options each repair one
site by contradicting something the specification says elsewhere.

**One decision rather than two.** The rule is stated once, where Section 16 introduces its engine
dispatches, so a third call site added later inherits it instead of restating it. Two decisions
stating the same principle at two call sites would drift, and the drift would be invisible: each
would read correct against its own algorithm.

**The rule is stated as an application, not as new substance.** Class 7's boundary already draws the
line; `VCSX-SPEC.md` Section 8.3 already makes it free to make. What Section 16 lacks is not a rule
but the instruction that its call sites are governed by one. The new paragraph therefore says where
the existing rule applies and adds no requirement of its own.

**Why the Section 17 check is part of this decision rather than a follow-on.** The split at the call
sites is *for* the disposition difference; a decision that makes the distinction and leaves the wide
clause unchecked leaves it exactly as unenforced as it is today. The check is written to be
discriminating rather than satisfiable by skipping everything: it pairs the two classes in one
instance — a class-2 provisioning failure on one repository leaves a second repository dispatching,
while an unavailable engine suppresses both. A build that collapses the classes fails the pair and
passes either half alone.

The check does **not** turn on a repository that requires no engine, though Section 14.2's clause is
worded over "every repository that requires one" and Sections 9.1–9.3 do recognize non-VCS
workspaces. No configuration key distinguishes them: `repository.<name>.vcs` resolves from the
orchestrator level and `vcs.local_vcs` is REQUIRED (Section 18.1.4), so "requires an engine" is not
something a test can set. A check resting on it would be unverifiable from configuration — the
defect issue #151 is filed about, which this decision is not going to reproduce while fixing
another. Two engine-requiring repositories are enough to separate the narrow disposition from the
wide one, and that is what the check uses.

**On the Section 18.1.4 correction.** It was found while confirming #143 and is in neither report.
It is included because it is the same defect in its most consequential position: Section 17 omits
the wide disposition, and Section 18 asserts the narrow one for the wide condition. An implementer
who reads Section 14.2 and Section 18.1.4 together finds a contradiction and has no way to tell
which governs; one who reads only Section 18.1.4 does not find one at all.

## Where the published call was wrong: `fail_worker` is the worker's disposition, not class 7's

The comment posted on #148 said `engine.integrate` "gains a failure arm ... `fail_worker`, like
every neighbouring step". That is wrong on Section 14.2's own text, and it is corrected here rather
than left in a thread.

`fail_worker` exits the worker abnormally. `on_worker_exit` (Section 16.7) then reaches
`schedule_retry` with `min(10000 * 2^(attempt - 1), config.agent.max_retry_backoff_ms)` — an
exponential per-worker backoff. Section 14.2 forbids exactly that for this class, twice, and states
its reason:

> Keep the service alive and retry on a later tick. Do not convert to a per-worker backoff retry: a
> below-floor engine, a missing engine, and an invalid policy are configuration defects rather than
> transients, and backoff does not converge on them.

So the arm as published would have routed a class-7 failure to the *worker's* disposition — which is
the same confusion the decision exists to remove, reintroduced by the repair for it, at a third
site. The shape is worth naming because it is the second time in this round that a repair reproduced
the defect it was repairing (decision 0165's backfill was the first).

What the arm does instead is what `dispatch_issue` already does for the same class one call earlier:
end the run, release the claim, arm no retry, and leave the issue for a later tick — where the
repository's next `ensure_object_store` re-discovers the condition and applies Section 14.2's
disposition at the unit that section names. Section 8.5 anticipated a site like this and states the
obligation:

> The claim follows the same ownership, as a partition rather than as a rule per site: every site
> that ends a dispatched run either releases the claim or hands it to a retry entry, and there is no
> third. ... A site added later MUST state which side of that partition it is on.

The new arm is on the releasing side, which is why this decision also touches Sections 7.1, 7.3 and
8.5. That is not scope creep: it is the sync obligation the document wrote down in advance for
precisely this change.

## Reconsideration trigger

Reopen if `usage_or_config` turns out not to be co-extensive with class 7 at some call site — a
status-bearing result the policy did not produce, or a `usage_or_config` reason that names an
operation outcome rather than a configuration one. The rule stated in Section 16 rests on the two
partitions coinciding, and `VCSX-SPEC.md` Section 6.11's reason registry is deferred (Section 11
there), so a later engine `MINOR` could add a reason that sits astride the line. The evidence would
be a reason token an implementation cannot classify without reading `message`.

A second trigger is the Section 17 check being satisfied by a build that still gets the scope wrong
— for instance by suppressing dispatch instance-wide for *every* class-7 cause, including the
repository-declared `version_floor` and policy conditions Section 14.2 keeps repo-scoped. The check
pairs class 2 against class 7 and would not catch that; if it is observed, the check needs a third
arm pairing the two halves of class 7 against each other rather than a fourth section.

A third trigger belongs to what this decision deliberately did not build. The classification half —
an invocation result in, a failure class out — is a pure function of the kind the conformance corpus
already carries three of (`retry_fire_disposition`, `worker_exit_disposition`,
`reconcile_disposition`), and it is not added here. The reason is that the half `symphony-rs`
actually got wrong is the **scope** half, which is a statement about a set of repositories rather
than about one result, and a vector covering only the classification half would go green against a
build carrying the defect — the failure mode decision 0166 recorded for `resolve_repository_config`
asserted without its `absent` paths. Reopen if a scope-shaped vector function is designed for
another purpose, since the input schema is the whole of the cost and this rule would then be nearly
free to add.
