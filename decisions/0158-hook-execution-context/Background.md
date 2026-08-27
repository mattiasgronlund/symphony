# Background — 0158 Where a workspace hook runs

## Context

Decision 0025's re-evaluation (update of 2026-08-27) recorded an adjacent gap it did not close:
Section 9.4 "Workspace Hooks" documents one execution contract for what Sections 5.3.4 and 15.4 make
two execution contexts. This is that decision.

The split itself is settled and is not reopened here. Section 5.3.4 states it as configuration —
hooks defined in `repo.policy.toml` are policy-branch-sourced and "run on the host outside the
sandbox with host access"; hooks defined in `WORKFLOW.md` are worktree-sourced and "run inside the
sandbox without credentials" — and adds that "a lifecycle point MAY be defined in either artifact;
when both define it, the `repo.policy.toml` hook runs on the host and the `WORKFLOW.md` hook runs
inside the sandbox". Section 15.4 states the same split as trust, and derives from it a rule about
working directories.

What is not settled is every surface that has to *execute* those hooks. Section 9.4's execution
contract, Section 9.2's creation algorithm, the `run_hook` calls in Section 16.6, and Section 17.2's
matrix rows all model one hook per lifecycle point, which is what the document said before the split
existed. The result is not a document that is merely vague about the second context: it is a document
whose execution surface contradicts its configuration surface, and an implementation built from the
execution surface reproduces the pre-split behavior while passing every row that checks it.

## The failure paths

**1. Section 9.4's `cwd` sentence is false for host-side hooks, and implementing it defeats a control
Section 15.4 states.** Section 9.4 says hooks "Execute in a local shell context appropriate to the
host OS, with the workspace directory as `cwd`". Section 15.4 says the opposite for the host-side
half, and says why: "An in-sandbox hook runs with the workspace directory as its working directory. A
host-side hook does not. It receives the workspace path as an argument or environment value, so a
relative invocation inside it resolves against the policy branch rather than against agent-written
content." It then names the case that motivates the rule — "This matters for a workspace lifecycle
hook (Section 5.3.4) as much as for a `[hooks]` unit: the body is an inline script, trusted when
policy-branch-sourced, but a relative command inside it would otherwise reach the working tree."

So an implementer who reads Section 9.4 — the section whose title is the hooks and whose subheading is
"Execution contract" — sets the working directory that Section 15.4 exists to prevent, and a
policy-branch-trusted hook body invoking `./scripts/setup` runs an agent-written script with host
access and the operator's credentials. The contradiction is not between a rule and its exception; it
is between a security control and the section an implementer would naturally build from.

**2. The reference algorithm has one hook call per lifecycle point, at a moment when no sandbox
exists.** Section 16.6 calls `run_hook("before_run", workspace.path)` once, before the turn loop and
therefore before `agent.run_turn` brings up the agent session. Section 16.6's failure branches call
`run_hook_best_effort("after_run", workspace.path)` the same way. One name, one call, no context
parameter, and the shape of the call — the workspace passed as an argument rather than as a working
directory — is the host-side convention from Section 15.4. The in-sandbox half of each lifecycle point
has no call site at all, and nothing says which sandbox it would run in if it had one.

**3. Two lifecycle points occur where no run context exists.** `before_remove` runs during startup
terminal workspace cleanup (Section 8.6), which happens in the orchestrator at service start: no
issue is dispatched, no executor is composed, and no sandbox is instantiated. `after_create` runs
inside workspace creation (Section 9.2, step 5), which for a VCS-managed repository derives the
working tree the sandbox would later mount. An in-sandbox half of either has nowhere to run under the
current text, and the document neither provides one nor says the half is skipped.

This is the part that cannot be fixed by better wording alone. Section 9.2's own note routes
preparation to the in-sandbox context — "Additional workspace preparation (for example dependency
bootstrap, build, or code generation) is handled via in-sandbox hooks (Section 5.3.4)" — so an
in-sandbox `after_create` is not a hypothetical the split permits by accident; it is the case the
specification points a repository at.

**4. Nothing orders the two halves, or says what a fatal half does to the other.** Section 5.3.4 says
both run. Section 9.4's failure semantics are stated per lifecycle point — "`after_create` failure or
timeout is fatal to workspace creation" — and were written when a lifecycle point had one hook. With
two, three questions have no answer: which half runs first; whether a fatal host-side `after_create`
still runs the in-sandbox half; and whether an in-sandbox `before_run` failure is fatal to the attempt
in the same way the host-side one is. An implementation may answer all three differently from another
and both conform.

**5. The conformance corpus pins a field the specification does not define.**
`conformance/vectors/config-defaults.json` asserts `"hooks.timeout_ms": 60000`. `SPEC.md` contains no
`hooks.timeout_ms`: the field is `hooks.workspace.timeout_ms` (Sections 5.3.4, 6.4, 9.4), and Section
5.3.4 explains the prefix — "The namespace is `hooks.workspace` rather than `hooks`, and the engine's
named units are `hooks.engine.<name>`". An implementation that defaults the path the corpus names
defaults a key the specification never defines; one that implements the specification fails the
vector. It is the derived-artifact drift class of decision 0132, on this decision's surface, and it is
repaired here rather than left for whoever trips over it.

## Options considered

- **Option A — repair the execution surface to match the split.** Section 9.4 states both execution
  contexts, each with its own working-directory rule (deferring to Section 15.4 rather than restating
  it), the order the two halves run in, and the failure semantics of each half. Section 9.2's step 5
  and Section 16.6's `run_hook` calls distinguish the halves. Section 17.2 gains rows for the second
  context and for the ordering. The corpus path is corrected. Trade-offs: the largest of the three,
  and it forces answers to the three open questions in failure path 4 rather than leaving them
  `Implementation-defined`. It also has to say what happens where no sandbox exists, which is a
  normative addition and not only a clarification.

- **Option B — repair Section 9.4's prose only.** Fix the `cwd` sentence, add a pointer to Sections
  5.3.4 and 15.4 for the split, and leave the reference algorithm and the matrix as they are.
  Trade-offs: closes the security-relevant contradiction at its worst site for a fraction of the cost,
  and is the smallest change that stops Section 9.4 from being actively wrong. But the reference
  algorithm is what an implementation copies — decision 0157 turned on exactly that point — so a
  document whose prose describes two contexts and whose algorithm calls one hook has moved the
  contradiction rather than removed it, and the two lifecycle points with no run context stay
  unanswered.

- **Option C — narrow the contract instead of the documentation.** Resolve the mismatch by restricting
  in-sandbox lifecycle hooks to the points where a run context exists (`before_run`, `after_run`),
  making `after_create` and `before_remove` host-side-only. Trade-offs: the execution surface becomes
  correct without any new machinery, and the two impossible cases stop being impossible by ceasing to
  be permitted. Against it, and decisively: Section 9.2's note points repositories at in-sandbox
  `after_create` for dependency bootstrap and build preparation, which is the single most useful
  in-sandbox hook and the one decision 0025's operator brief was about. Removing it to fix a
  documentation gap trades a capability for a paragraph.

## Decision and reasoning

**Option A**, with the availability rule Option C is right about folded in as one of its answers
rather than as a restriction on what may be configured.

Option B is rejected on decision 0157's precedent: the reference algorithm is the artifact an
implementation copies, and a prose repair that leaves `run_hook("before_run", workspace.path)`
standing leaves the defect where implementations will meet it. Option C is rejected because the
capability it removes is the one the specification actively recommends two sections earlier.

The answers Option A must give, and the reasoning for each:

- **Working directory.** Section 9.4 states the rule per context and cites Section 15.4 as its source
  rather than restating the rationale. One statement, one home; the security reasoning stays where the
  trust model is.
- **Order.** Setup points run host-side first, then in-sandbox; teardown points run in-sandbox first,
  then host-side. The halves nest: trusted setup establishes what untrusted preparation builds on, and
  teardown unwinds in the reverse order so the trusted half runs last and can act after the untrusted
  half is finished. The alternative — a fixed order for all four points — reads simpler and puts the
  trusted half of teardown before the work it is meant to follow.
- **Failure.** Each half keeps the fatality Section 9.4 already assigns to its lifecycle point, and a
  fatal half short-circuits the other: a host-side `after_create` that fails means workspace creation
  has failed, so the in-sandbox half does not run. This is the reading that keeps Section 9.4's
  existing sentences true rather than qualifying each of them.
- **Availability.** An in-sandbox half runs only where a run context exists to instantiate its sandbox.
  At startup terminal cleanup (Section 8.6) there is no run, so the in-sandbox `before_remove` half is
  not run, and that it was skipped is logged — consistent with `before_remove` failures already being
  "logged and ignored". Where a run context does exist, the executor (Section 3.1) instantiates the
  sandbox, which makes explicit something the document currently implies: the sandbox is scoped to the
  run attempt, not to a turn, because `before_run` precedes the first turn.

That last answer is the one substantive addition rather than a clarification, and it is what makes the
others checkable: without it, "the in-sandbox half runs" is a requirement no implementation can
satisfy at two of the four lifecycle points.

**Reconsideration trigger.** If the sandbox's scope is later narrowed below the run attempt — a
per-turn sandbox, or an agent adapter that owns sandbox lifetime itself (Section 10.9) — the
availability answer above stops holding for `before_run`, and the ordering and failure answers have to
be re-derived against whatever bounds the sandbox then has. A second trigger is a repository that
needs an in-sandbox `before_remove` at startup cleanup: the skip recorded here is a consequence of
there being no run context, and a deployment that wants one is asking for a run context to be created
for cleanup, which is a different decision.
