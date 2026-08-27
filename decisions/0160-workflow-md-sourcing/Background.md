# Background — 0160 Where `WORKFLOW.md` is read from, and whose it is

## Context

Decision 0097 moved `repo.policy.toml` to a revision on a remote and restated Section 6.2 around it,
and while doing so it said what it believed about the other repository-owned artifact:
"`WORKFLOW.md` changes timing only and stays worktree-sourced, since everything in it runs in-sandbox
without credentials." Its `Anchor changes` narrowed Section 6.2's "all three configuration artifacts"
to the two the daemon "holds locally", and it left `WORKFLOW.md` in that watched set. So the
timing claim and the sourcing claim were made in the same sentence and only one of them reached
`SPEC.md`.

Decision 0159 then gave the operator policy config a repository dimension: `repository` is a map
keyed by the `Repository Key`, and each entry carries that repository's `vcs`, its agent selection,
its routing rules, and — the anchor that matters here — `repository.<name>.policy`, "the pointer to
that repository's `repo.policy.toml`". Two of the three configuration artifacts now have a repository
dimension and a stated revision. The third has neither.

What `SPEC.md` says about `WORKFLOW.md` today splits cleanly in two, and the halves are incompatible.

The trust half. Section 5: "repository-owned, in-sandbox … It is sourced from the worktree (the
agent's own checkout), so an agent edit is honored where it is harmless (Section 15.4)." Section
15.4: "In-sandbox parts — the `WORKFLOW.md` prompt, its `hooks.workspace` lifecycle hooks, and the
`hooks.engine` units the `before:commit` gate/scan runs — are read from the **worktree**", followed by
the property the whole trust model is checkable by: "Each artifact is read from exactly one revision,
which is what makes 'sourced by trust' checkable rather than a rule about parts of a file."

The mechanism half. Section 5.1: the workflow file is at an "explicit application/runtime setting
(set by CLI startup path)", otherwise "`WORKFLOW.md` in the current process working directory".
Section 6.1 step 1 "select[s] the `WORKFLOW.md` path (explicit runtime setting, otherwise cwd
default)". Section 6.2 requires detecting changes to it as one of "the two configuration artifacts
it holds locally". Section 6.3 validates that it "can be loaded and parsed" before every dispatch
cycle. Section 16.1 runs that validation at startup, before any workspace exists.

A host path in the daemon's own working directory is not a worktree and is not a revision. The two
halves cannot both be right, and every surface that has to *execute* the artifact implements the
half the trust model denies.

## The failure paths

**1. The pipeline resolves one workflow and each policy, in one sentence.** Section 6.1, step 1:
"Load the operator policy config, select the `WORKFLOW.md` path (explicit runtime setting, otherwise
cwd default), and resolve each managed repository's `repository.<name>.policy` pointer." Step 2
parses "the operator policy config, the `WORKFLOW.md` front matter, and each `repo.policy.toml`".
One and each, in adjacent clauses. Section 8.7 lets one instance manage several repositories and
Section 5 calls `WORKFLOW.md` repository-owned; a repository cannot own an artifact the instance
holds one of. The consequence is concrete: two repositories under one daemon share a prompt template
and share their in-sandbox hook halves, and neither can state its own. Section 11.2 argues about "a
field a repository's `WORKFLOW.md` names" — possessive, per repository — while nothing lets a
repository have one.

**2. The stated sourcing has no producer, and the trust argument that rests on it collapses in both
directions.** Section 15.4's "read from exactly one revision" is the property that makes "sourced by
trust" a thing a reader can check. Read at the daemon's cwd, `WORKFLOW.md` is read from no revision
at all, so the property is false for the one artifact whose trust level is *untrusted-and-harmless*
and whose harmlessness is the reason it may be agent-editable.

Both directions fail. If the file really is the operator's copy in the daemon's cwd, Section 5's "an
agent edit is honored where it is harmless" names a behavior nothing produces, and Section 15.4's
`before:commit` division — "the agent can change what the gate does and not whether it runs" —
loses its first half: the agent cannot change what the gate does either, because the gate's
declaration is in a file it cannot reach. If the file really is worktree-sourced, then Sections 5.1,
6.1, 6.2, 6.3 and 16.1 describe a resolution, a watch, and a preflight check against a path that
belongs to no run.

**3. Section 6.2 contradicts itself about the same file.** First bullet: the software "MUST detect
changes to the two configuration artifacts it holds locally: `WORKFLOW.md` and the operator policy
config". Second bullet, about `repo.policy.toml`: "It is instead read once at the start of each unit
of work, **together with `WORKFLOW.md`**." An artifact read at the start of each unit of work from
the run's own working tree is not one the daemon holds locally, and there are as many copies of it
as there are workspaces — so the watch requirement does not say which one it binds.

Section 18.1.1 compounds it by preserving the phrasing decision 0097 replaced: "dynamic
watch/reload/re-apply for **all three** with last-known-good on invalid reload", which Section 6.2's
own second bullet denies for `repo.policy.toml`. 0097's `Anchor changes` recorded the narrowing;
the checklist row was never brought along. That is decision 0128's class — a cross-cutting section
left behind by the change that invalidated it — and it is measurable today rather than inferred.

**4. Two repository-owned artifacts, two failure scopes, and nothing says why.** Section 5.5:
"Workflow file read/YAML errors block new dispatches until fixed" — every repository the instance
manages. Section 14.1 classifies "Missing `WORKFLOW.md`" and "Invalid YAML front matter" as
`workflow_config_failures`, and Section 14.2 disposes of that class as "Skip new dispatches", with no
repository qualifier. The other repository-owned artifact takes the opposite scope: an unusable
`repo.policy.toml` is `engine_invocation_failures` and Section 14.2 says "Skip new dispatches for the
affected repository … so the failure is repo-scoped, not a single worker's. Other repositories are
unaffected." Under the cwd reading the instance-wide scope is at least coherent, there being one
file. Under the worktree reading it is one repository's bad YAML halting every other repository —
and unfixable by observation, because the daemon cannot re-read the file without dispatching a run
into the repository it has just stopped dispatching to.

**5. A preflight check on a file that does not exist yet.** Section 6.3's per-tick list opens with
"Workflow file can be loaded and parsed", and Section 16.1 runs the same validation at startup. A
worktree-sourced `WORKFLOW.md` lives inside a per-issue working tree that is derived at dispatch
(Sections 9.2, 16.6). At preflight there is no tree for any candidate issue, so the check has
nothing to read — which is precisely why `repo.policy.toml`, read from a revision on a remote, is
not in that list either.

**6. The only top-level key the published registry assigns to `WORKFLOW.md` binds a host port.**
`conformance/vocabulary.json`'s `config_namespaces` carries sixteen entries. Fifteen are
`operator_policy_config`, `repo_policy_toml`, or `repository_owned`. The sixteenth is `server` →
`workflow_md`, from Section 13.8: "Start the HTTP server when `server.port` is present in
`WORKFLOW.md` front matter." Binding a network listener on the host is exactly what Section 5 says
this artifact MUST NOT carry — "any setting Symphony executes with host access" — and the listener
serves the runtime snapshot (Section 13.3) and the JSON API (Section 13.8.2), which are
instance-wide and carry agent free text from every repository, not only from the one whose front
matter opened the port.

`conformance/README.md` already files this as open: "`server.*` is repository-owned by Section 13.8
(open) … reconciling the two is a spec-clarification candidate, and is why decision 0069 places
`observability.*` in the operator policy config rather than following `server.*`." The corpus is
routing around a rule the specification still states. Giving `WORKFLOW.md` a repository dimension
makes the placement not merely a trust contradiction but unanswerable: which repository's front
matter binds the instance's port, and what happens when two disagree.

## Prior art, measured

`symphony-rs` at `3255c9c` (measured 2026-08-27), the implementation that tracks this specification,
carries both halves of the contradiction, because the specification does.

- `crates/symphony-config/src/workflow.rs` defines
  `pub fn workflow_path(explicit: Option<&Path>, cwd: &Path) -> PathBuf`, documented as "Where
  `WORKFLOW.md` is, as a function of `(explicit, cwd)` (`SPEC §5.1`)", claiming two traceability
  items. The path is a function of the process working directory and of nothing repository-shaped.
- `crates/symphony-config/src/validate.rs` runs the preflight as
  `validate(config, repository, workflow_source, transitions, ambient)` — **per repository**, against
  **one** `workflow_source` — and `ValidConfig` holds a single `workflow`.
- `crates/symphony-config/src/operator.rs` models `Repository` with `policy`, `vcs`, `agent` and
  `issues`. There is no workflow pointer, because `SPEC.md` names none.
- The same repository's trust tables say the opposite. `CLAUDE.md` and
  `.claude/skills/secret-isolation/SKILL.md` both tabulate "`WORKFLOW.md`, in-sandbox hooks, the
  `before:commit` gate | the **worktree**".

So one repository holds a loader that reads the artifact from the daemon's cwd and a trust table that
says it is read from the worktree, and both are faithful transcriptions of `SPEC.md`. That is the
cost of leaving the artifact's identity split: it is not that an implementation gets it wrong, but
that a careful one gets it both ways.

## Options considered

### Option A — `WORKFLOW.md` is read from the working tree the run acts in, and each repository has one (recommended)

Section 5.1 states one rule: the workflow file is resolved *within the working tree the run acts in*,
never at a host location outside one. For a dispatched run that tree is the per-issue workspace
(Section 9.1) and the file sits at `repository.<name>.workflow`, a new per-entry pointer defaulting
to `WORKFLOW.md` and resolved relative to the repository exactly as `repository.<name>.policy` is.
For a deployment that drives a session in a workspace it did not dispatch — the `interactive-agent`
topology — that tree is the workspace the process runs in, which is what the explicit runtime setting
and the process-working-directory default have always named. One rule, one source, two ways of
naming the same tree.

It follows that the artifact is read once at the start of each unit of work, with `repo.policy.toml`
— which Section 6.2's second bullet already says — that it leaves the watched set, that its
read/parse failures fail the run attempt rather than blocking the instance, and that the preflight
check on it goes.

Trade-offs: it is the largest of the four in surface, touching Sections 5, 5.1, 5.3.7, 5.5, 6.1, 6.2,
6.3, 10, 13.8, 14.1, 14.2, 14.5 and the cross-cutting sections. It removes a REQUIRED watch and a
preflight check rather than adding to them, and both removals are retractions a reader must be given
a reason for. And it makes a `WORKFLOW.md` mandatory in every managed repository: a repository that
ships none cannot be run, where today the operator's single copy covered every repository. That cost
is stated rather than softened, and it is what "repository-owned" means.

### Option B — `WORKFLOW.md` is operator-held and instance-level; the repository-owned language is what is wrong

Steelmanned: this is the smallest edit. It matches every executable surface in the document today
(Sections 5.1, 6.1, 6.2, 6.3, 16.1) and the one existing implementation, so nothing has to be
rebuilt. It is also arguably safer: an agent that can edit its own prompt template can rewrite the
instructions the next attempt of its own issue is given, and Section 5.4's entire "Prompt authority"
passage exists only because the artifact is untrusted. Remove the untrust and that passage becomes
unnecessary rather than load-bearing. A single prompt across repositories is what a small deployment
actually wants.

It loses on what it has to retract. Section 1's goal — "keeps the workflow policy in-repo
(`WORKFLOW.md`) so teams version the agent prompt … with their code" — goes. Section 15.4's
in-sandbox half of the trust model goes with it, and with that its `before:commit` division, which
needs the gate's declaration to be worktree-sourced for "the agent can change what the gate does and
not whether it runs" to mean anything. Section 5.3.4's two-trust-level hook model loses the artifact
its in-sandbox half is declared in. Decision 0029's `base-sourced vs worktree-sourced` axis — the
axis 0005 was *superseded by* — loses one of its two poles. And it does not fix failure path 1: one
prompt for N repositories survives, it merely stops being called a defect.

### Option C — keep both: an instance-level `WORKFLOW.md`, overridden per repository from the worktree where one is present

Steelmanned: nothing is retracted. A single-repository deployment writes one file where it always
did; a repository that wants its own prompt commits one and it wins. It is additive, it preserves
Section 5.1 unchanged, and it gives Option A's benefit to the deployments that ask for it without
imposing Option A's mandatory per-repository file on the ones that do not.

It loses on the one property the trust model is checkable by. The artifact would then be read from
two revisions — the operator's host copy and the run's working tree — and Section 15.4's "each
artifact is read from exactly one revision" is exactly what is given up. A reader could not tell,
from a `hooks.workspace` in-sandbox half, which trust level it was read at, and the front matter's
keys would resolve leaf by leaf *across a trust boundary* — the resolution decision 0159 established
for the operator's own two levels, applied to a pair where one level is untrusted and the other is
not. It also leaves failure path 4 open: whose defect blocks whose dispatch when the instance-level
copy parses and a repository's does not.

### Option D — declare the discovery `Implementation-defined`, as the operator policy config's already is

Steelmanned: consistent with how this document treats the *operator's* artifact, whose "format and
discovery path are `Implementation-defined` and MUST be documented" (Section 5). One clause, no
retraction, and every deployment gets the layout its host wants.

It loses because the two artifacts have different readers. An operator reads the implementation's
documentation and configures to it; a repository author writes `WORKFLOW.md` without knowing which
implementation will run it, and needs to know whether an edit is honored, which is the answer this
option declines to give. It would also make Section 15.4's "read from exactly one revision"
implementation-defined, converting a property a consumer can check into one an implementation
asserts about itself — the substitution the `spec-guarantee` skill exists to refuse.

## Decision and reasoning

Option A.

### The pointer follows `policy`, not `vcs`

`repository.<name>.workflow` is a path string with Default `WORKFLOW.md`, resolved relative to the
repository. It has no orchestrator-level counterpart, and that is deliberate: `repository.<name>.policy`
has none either, for the reason that a path *inside* a repository says nothing about any other
repository's layout. Decision 0159's leaf-by-leaf resolution against the orchestrator level governs
the keys that exist at both levels — `vcs`, `agent` — and neither pointer is one of them. Two
pointers, same shape, same section, adjacent rows.

### One source, two ways of naming the same tree

The temptation is to write two rules — a daemon rule and an interactive rule — and that would
reintroduce the split this decision closes. There is one rule: the file is inside the working tree
the run acts in. The daemon derives that tree at dispatch and names the file by the repository's
pointer. A session driven in a workspace that already exists (Section 3.4's `interactive-agent`)
*is* running in the tree, which is what a process working directory and an explicit startup path have
always named. Section 5.1's precedence survives as the way that second case names its tree, and stops
being the daemon's rule.

This also settles what "reads the artifact" means across the sandbox boundary. Symphony reads
`WORKFLOW.md` host-side, from the workspace directory, as *data* — the discipline Section 15.4
already fixes for a host-side hook, which "MAY **read** the workspace and MUST NOT **execute** from
it". The in-sandbox hook half's body is then handed to the sandbox to run, and the prompt body is
rendered into a prompt that Section 5.4 already governs as untrusted content. Nothing about reading
worktree content host-side grants it host execution.

### The failure disposition unifies rather than splitting

Section 5.5's dispatch gating has two behaviors: "Workflow file read/YAML errors block new dispatches
until fixed" and "Template errors fail only the affected run attempt". The split exists *because* the
file was assumed host-local and preflight-checkable — one kind was catchable before a run and the
other was not. Remove that premise and the split has no producer: both kinds are now discovered at
the same moment, reading the same file out of the same tree. So all five classes of Section 5.5 fail
the affected run attempt, and none blocks dispatch instance-wide.

`workflow_config_failures` therefore takes two dispositions, on the precedent Section 14.2 already
sets in its own opening paragraph for `tracker_failures` — "what a tracker failure costs depends on
where it occurred". The operator-config half (unsupported tracker kind, missing tracker credentials
or project slug, missing coding-agent executable) keeps the instance-wide dispatch skip. The
`WORKFLOW.md` half takes the worker disposition and Section 8.4's backoff. No new
`Implementation-defined` schedule is introduced: a repository whose workflow cannot be read fails
runs like any other failing run, capped by `agent.max_retry_backoff_ms`.

### The seam stops carrying a file the executor already has

Section 10 lists what crosses the orchestrator↔executor seam: "the normalized issue, the workflow
template, the `agent`/effort selection, `agent.max_turns`, a wall-clock bound, and any
`continuation_ref`". Under Option A the orchestrator has no workflow template to send. The working
tree is derived by the executor (Section 16.6 `provision_for_issue`), and for a remote executor it is
derived on the node against a store provisioned there (Section 9.11), so the orchestrator never holds
the bytes. The run-spec drops the template and the executor reads it from the tree it derived. This
is a consequence with a vanishing producer rather than a tidy-up: left in, the seam would specify the
orchestrator sending something it cannot obtain.

### `server.*` moves, and the corpus finding closes with it

Section 13.8's enablement reads `server.port` from `WORKFLOW.md` front matter. That is already a
violation of Section 5's rule; with `WORKFLOW.md` per-repository it is also unanswerable. The key
moves to the operator policy config on Section 18.2's own stated reasoning for `observability.*` —
"these are deployment concerns with host-side effects, and a repository-owned, in-sandbox artifact
MUST NOT carry them". The registry entry's `artifact` changes with it, and
`conformance/README.md`'s open finding is rewritten as resolved, naming this decision.

## What this decision does not fix, and why it is separable

**`hooks.workspace.timeout_ms` in the untrusted artifact.** Section 5.3.4 documents `timeout_ms` once
and says both artifacts carry the `hooks.workspace` namespace, so a `WORKFLOW.md` value bounds the
*host-side* half as well as the in-sandbox one — an agent-editable bound on a host-side hook.
Nothing here changes that: the defect is about which half a declared bound applies to, which is
decision 0158's axis (execution context), not this decision's (where the artifact is read from).
Fixing it here would be adding a second premise to a decision that has one. It is filed so it can be
decided on its own, the way decision 0148 filed the repository-enumeration gap that decision 0159
closed.

**"Non-VCS workspaces" (Sections 9.1, 9.3).** A workspace with no working tree has no `WORKFLOW.md`
to read. The case is already unreachable for a daemon-routed issue: Section 6.3 requires
`vcs.local_vcs` to be resolved "for every `repository` entry", and Section 9.7 makes `local_vcs`
REQUIRED, so every managed repository is VCS-managed. The residue predates this decision and its
repair turns on a different premise — whether a managed repository may be non-VCS at all — so it is
noted, not fixed.

## Reconsideration triggers

- **A deployment wanting one prompt across many similar repositories.** Under Option A that is N
  identical committed files. If that becomes the common case, the specification owes an
  orchestrator-level default the entries inherit — the shape Section 5.3.7 already has for `vcs` and
  `agent`, and the point at which Option C's two-revision objection has to be met rather than
  avoided.
- **An `interactive-agent` deployment with no `repository` entry.** Section 5.3.7's floor is stated
  over "a deployment that manages a repository", so a session in a workspace that already exists
  configures none, and the working-directory arm of Section 5.1 is the only naming it has. A later
  decision that requires an entry there collapses the two namings into one and Section 5.1 shortens.
- **A prompt that must vary by issue class beyond `agent_by_label`.** That reopens whether `workflow`
  is one pointer or a selection, which is a different question from where the artifact lives.
- **An operator-supplied prefix or wrapper around every repository's prompt.** That reintroduces a
  second source for one artifact and is Option C arriving through the back door; it would have to
  answer Option C's revision objection first.

## Conformance Statement

No `Implementation-defined` choice and no "MUST document" obligation is created. The workflow pointer
has a default and a stated resolution; the sourcing rule is stated over a tree a consumer can point
at; the unified failure disposition reuses Section 8.4's existing backoff rather than declaring a new
schedule. The operator policy config's existing "format and discovery path" row (Section 5) is
unchanged and now covers `server.*` as it covers `observability.*`. No row is owed in
`CONFORMANCE-STATEMENT-TEMPLATE.md`.

## What implementing it changed (2026-08-27)

One finding, and it is a subtraction the plan had written as a substitution. Section 17.1 carried
"Invalid workflow reload keeps last known good effective configuration and emits an operator-visible
error", and the cross-cutting step restated it as a policy-config check. Applied, that restatement
duplicated a bullet three lines below it — "Policy-config changes are detected and re-applied without
restart, with last-known-good on invalid reload" — which had been added when the policy config joined
the watched set and already covers the case. The workflow check had no surviving counterpart at all:
last-known-good is a property of a *reload*, and there is no reload of an artifact read fresh at the
start of each unit of work. So the check count drops by one rather than being carried across, and a
check that would have asserted a behavior nothing performs is gone rather than reworded. The plan's
own P lens is what the finding belongs to, applied one level further out than it had been: a check is
a consequence too, and it needs a surviving producer like any other.
