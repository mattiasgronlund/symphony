# Plan — 0160 Where `WORKFLOW.md` is read from, and whose it is

## Scope

`SPEC.md`: Section 1 (Problem Statement), Section 3.1 (Main Components), Section 3.2 (Abstraction
Levels), Section 4.1.3 (Service
Config (Typed View)), Section 5 (Configuration Contracts), Section 5.1 ("WORKFLOW.md Discovery and
Path Resolution"), Section 5.3.7 (`repository` (map of objects)), Section 5.5 ("Workflow Validation
and Error Surface"), Section 6.1 ("Configuration Resolution Pipeline"), Section 6.2 ("Dynamic Reload
Semantics"), Section 6.3 ("Dispatch Preflight Validation"), Section 6.4 ("Core Config Fields Summary
(Cheat Sheet)"), Section 9.2 ("Workspace Creation and Reuse"), Section 10 (Agent Runner Protocol
preamble, the orchestrator↔executor run-spec), Section 13.8 ("OPTIONAL HTTP Server Extension"),
Section 14.2 ("Recovery Behavior"), Section 14.5 ("Operator Intervention Points"), Section 15.4
("Configuration Trust Sourcing and Hook Safety"), Section 16.1 (`start_service`), Section 16.6
(`run_agent_attempt`), and the cross-cutting sections: 17.1, 17.2, 17.7, 18.1.1, 18.1.3, 18.2.

`conformance/vocabulary.json` (`config_namespaces` entry `server`) and `conformance/README.md`
(the open `server.*` finding).

No new section. No section is removed or renumbered.

## Steps

1. **The per-repository pointer (`repository.<name>.workflow`, Section 5.3.7 "`repository` (map of
   objects)").** Ensure the `Fields:` list carries a `workflow` bullet beside `policy`, in the field
   documentation pattern the section already uses: `` - `workflow` (path string) ``, described as the
   pointer to that repository's `WORKFLOW.md` (Section 5.1), resolved relative to the repository
   rather than to the host filesystem — the file is read from the run's working tree — with
   `` - Default: `WORKFLOW.md` ``. Ensure the section's "Resolution against the orchestrator level"
   text is untouched: like `policy`, `workflow` has no orchestrator-level counterpart, and the
   leaf-by-leaf rule governs only the keys that exist at both levels.
   *Done when* Section 5.3.7 documents two pointers with the same shape and `workflow` appears in no
   orchestrator-level key list.

2. **One sourcing rule (Section 5.1 "WORKFLOW.md Discovery and Path Resolution").** Ensure the
   section states that `WORKFLOW.md` is resolved *within the working tree the run acts in* and never
   at a host location outside one, and that the two ways of naming that tree are:
   - a dispatched run — the per-issue workspace (Section 9.1), with the file at the repository's
     `repository.<name>.workflow` pointer (Section 5.3.7);
   - a deployment that drives a session in a workspace it did not dispatch (the `interactive-agent`
     topology, Section 3.4) — the workspace the process runs in, named by the explicit
     application/runtime setting (set by CLI startup path) or, absent one, the current process
     working directory.

   Ensure the existing loader bullets survive with the resolved path now being the tree-relative one:
   `missing_workflow_file` where the file cannot be read at the resolved path, and the statement that
   the workflow file is repository-owned and version-controlled — which is now a property of where it
   is read from rather than an expectation about it. Ensure the section says the artifact is read
   once at the start of each unit of work (Section 6.2) rather than held open.
   *Done when* no bullet in Section 5.1 names a path that is not inside a working tree, and the
   `interactive-agent` naming is attributed to the topology rather than stated as the general rule.

3. **The artifact description (Section 5, the `WORKFLOW.md` bullet in "Symphony reads configuration
   from three artifacts").** Ensure the bullet says the operator policy config points each managed
   repository at its `WORKFLOW.md` through `repository.<name>.workflow`, that the file is read from
   the working tree the run acts in (Section 5.1), and that it is therefore read once at the start of
   each unit of work as `repo.policy.toml` is (Section 6.2). Keep the existing untrusted /
   MUST-NOT-carry-credentials sentence unchanged.
   *Done when* the bullet names the pointer and the tree, and the `repo.policy.toml` bullet's
   "per repository" phrasing has a symmetric counterpart.

4. **The typed view's examples (Section 4.1.3 "Service Config (Typed View)").** Ensure the
   `Examples:` list no longer presents poll interval, workspace root, active/terminal issue states,
   concurrency limits and coding-agent executable/args/timeouts as values derived from
   `WorkflowDefinition.config`: those are operator policy config (Sections 5, 5.3). Ensure the entry
   describes the typed runtime view as derived from the resolved configuration of all three
   artifacts (Section 6.1), with the `WORKFLOW.md`-sourced part being the prompt template and the
   in-sandbox hook halves.
   *Done when* no example in Section 4.1.3 names a setting Section 5 assigns to the operator policy
   config as one `WORKFLOW.md` supplies.

5. **The goal line (Section 1 "Problem Statement").** Ensure the bullet beginning "It keeps the
   workflow policy in-repo (`WORKFLOW.md`)" names what the artifact actually versions — the agent
   prompt and its in-sandbox hooks — rather than "runtime settings".
   *Done when* the sentence is consistent with Section 5's dividing rules.

6. **The component and the layer (Sections 3.1 "Main Components" `Workflow Loader`, and 3.2
   "Abstraction Levels" `Configuration Layer`).** Ensure `Workflow Loader`'s description says it
   reads the repository's `WORKFLOW.md` from the run's working tree, so a reader does not infer a
   startup-time singleton from the component list. Ensure the paragraph beginning "The per-issue run
   is carried by an `Execution Process`" names the loader among what the executor composes for one
   issue, since the artifact is now read where the tree exists — today it lists the `Workspace
   Manager` (5), the `Agent Runner` (6) and the per-run broker (7), and the loader has moved into
   that set. In Section 3.2, ensure the `Configuration Layer` bullet "Parses front matter into typed
   runtime settings" no longer implies the front matter is where runtime settings come from; the
   layer parses all three artifacts (Section 6.1) and the front matter supplies the in-sandbox hook
   halves.
   *Done when* `Workflow Loader` names a per-run, tree-relative read, and no bullet in Section 3.2
   attributes a runtime setting to `WORKFLOW.md` front matter that Section 5 assigns elsewhere.

7. **Unified failure disposition (Section 5.5 "Workflow Validation and Error Surface").** Ensure the
   `Dispatch gating behavior:` block states one behavior: every class in this section fails the
   affected run attempt, and none blocks new dispatches for the instance. Ensure the reason is
   stated: the artifact is read from the run's working tree at the start of the unit of work
   (Sections 5.1, 6.2), so a read or parse failure is discovered inside a run attempt and there is no
   earlier point at which it could gate dispatch. Ensure the requirement that an implementation-defined
   class be assigned a dispatch gating behavior becomes an assignment to *this* behavior, since there
   is now one.
   *Done when* "block new dispatches until fixed" appears nowhere in Section 5.5 and the retained
   error-class list is unchanged.

8. **The resolution pipeline (Section 6.1 "Configuration Resolution Pipeline").** Ensure step 1
   resolves each managed repository's `repository.<name>.workflow` pointer beside its
   `repository.<name>.policy` pointer, and no longer selects a single `WORKFLOW.md` path from a
   runtime setting or the process working directory. Ensure step 2 parses "the operator policy
   config, each repository's `WORKFLOW.md` front matter, and each `repo.policy.toml`", with the
   `WORKFLOW.md` front matter read from the run's working tree as the `repo.policy.toml` host-side
   sections are read from the policy branch. Ensure decision 0159's ordering sentence in step 3
   (resolution against the orchestrator level precedes defaulting) is untouched.
   *Done when* no step of Section 6.1 reads one workflow while reading each policy.

9. **The watched set (Section 6.2 "Dynamic Reload Semantics").** Ensure the first bullet requires
   detecting changes to the one configuration artifact the software holds locally — the operator
   policy config — and that the second bullet covers both repository-owned artifacts: neither
   `repo.policy.toml` nor `WORKFLOW.md` is watched, both are read once at the start of each unit of
   work, and the prompt, in-sandbox hooks and policy in force for a run are the ones read when that
   run started. Ensure the reason is given for `WORKFLOW.md` in its own terms: it is read from the
   run's working tree, of which there is one per workspace, so a watch would not say which copy it
   binds. Ensure the bullet naming "prompt content for future runs" keeps a producer: that content
   now reaches a future run through the per-unit-of-work read rather than through a reload, so the
   bullet names the artifact whose reload it still describes and leaves the prompt to the read.
   *Done when* Section 6.2 no longer calls `WORKFLOW.md` locally held, its "together with
   `WORKFLOW.md`" clause is a statement rather than a contradiction of the bullet above it, and no
   surviving bullet promises a reload for an artifact that is no longer watched.

10. **The preflight check (Section 6.3 "Dispatch Preflight Validation").** Ensure the
    `Validation checks:` list no longer contains "Workflow file can be loaded and parsed", and that
    the section says why: the workflow file is inside a per-issue working tree that does not exist
    until the issue is dispatched, so the check cannot run where this validation runs — the same
    reason `repo.policy.toml` is not read here — and the condition is disposed of at the run attempt
    (Section 5.5). Ensure every other check in the list is unchanged, including decision 0159's
    `repository`-entry and `Repository Key` checks. Ensure the section's opening paragraph — "It
    validates the workflow/config needed to poll and launch workers" — no longer claims to validate
    the workflow, which has no producer here once the check is gone.
    *Done when* no preflight check reads an artifact that lives in a working tree, and no sentence
    in Section 6.3 promises a validation the list does not perform.

11. **The cheat sheet (Section 6.4 "Core Config Fields Summary (Cheat Sheet)").** Ensure a
    `` `repository.<name>.workflow` `` row exists beside the `` `repository.<name>.policy` `` row,
    with the same row shape: path resolved relative to the repository, default `WORKFLOW.md`, the
    pointer to that repository's `WORKFLOW.md` (Sections 5.1, 5.3.7). Ensure the section's opening
    paragraph, which lists what a `repository` entry carries, names the workflow pointer alongside
    the policy pointer. Ensure the "Workspace hooks" block's parenthetical still attributes the
    in-sandbox halves to `WORKFLOW.md` and names where it is read from.
    *Done when* `scripts/validate_spec_consistency.py` reports no new warning for a dotted token
    absent from Section 6.4.

12. **The workspace-creation ordering (Section 9.2 "Workspace Creation and Reuse").** Ensure the
    algorithm summary makes explicit that for a VCS-managed repository the working tree is derived
    before the `after_create` halves run, so the in-sandbox half's body — declared in `WORKFLOW.md`
    and read from that tree (Sections 5.1, 15.4) — is readable when the half is invoked.
    *Done when* no step invokes an in-sandbox hook half before the tree its declaration is read from
    exists.

13. **The run-spec (Section 10, "Orchestrator↔executor protocol").** Ensure the enumeration of what
    the orchestrator sends across the seam no longer includes the workflow template, and that the
    text says the executor reads the repository's `WORKFLOW.md` from the working tree it derived
    (Sections 5.1, 16.6) — which for a remote executor is derived on the node (Section 9.11), so the
    orchestrator never holds the bytes. Ensure the rest of the run-spec list is unchanged.
    *Done when* nothing crossing the seam is an artifact the orchestrator cannot obtain.

14. **`server.*` becomes operator config (Section 13.8 "OPTIONAL HTTP Server Extension").** Ensure
    the `Enablement (extension):` bullets start the HTTP server when a CLI `--port` argument is
    provided or when `server.port` is present in the operator policy config, and that the sentence
    "The `server` top-level key is owned by this extension" also says the key belongs to the operator
    policy config. Ensure the reason is stated in the extension's own terms, matching Section 18.2's
    reasoning for `observability.*`: binding a host port is a deployment concern with host-side
    effects, which a repository-owned in-sandbox artifact MUST NOT carry (Sections 5, 15.4), and the
    listener serves instance-wide state rather than one repository's.
    *Done when* no bullet in Section 13.8 reads a value out of `WORKFLOW.md`.

15. **Two dispositions for one class (Section 14.2 "Recovery Behavior").** Ensure the bullet
    disposing of `workflow_config_failures` splits on where the failure occurred, in the shape the
    section's own opening paragraph already uses for `tracker_failures`: a failure in the operator
    policy config or in the coding-agent executable skips new dispatches, keeps the service alive and
    continues reconciliation; a failure reading or parsing a repository's `WORKFLOW.md` fails the
    affected run attempt and takes the worker disposition (Section 8.4's backoff), because the
    artifact is read inside the run. Ensure the opening paragraph's list of classes that take more
    than one disposition names `workflow_config_failures` as well as `tracker_failures`. Ensure no
    new backoff schedule and no new `Implementation-defined` choice is introduced.
    *Done when* Section 14.2 disposes of a `WORKFLOW.md` read failure without blocking dispatch for
    repositories that have none.

16. **Operator intervention (Section 14.5 "Operator Intervention Points").** Ensure the two bullets
    about editing `WORKFLOW.md` say what is true under the new sourcing: the artifact is
    repository-owned, so an operator edits it in the repository, and the change takes effect for work
    started after it reaches the run's working tree — not detected and re-applied without restart.
    Ensure the bullet no longer claims `WORKFLOW.md` carries "most runtime settings".
    *Done when* Section 14.5 and Section 6.2 agree about what a `WORKFLOW.md` edit does and when.

17. **Trust sourcing (Section 15.4 "Configuration Trust Sourcing and Hook Safety").** Ensure the
    in-sandbox-parts bullet names the working tree the run acts in and cites Section 5.1 for how that
    tree is named, so the revision an in-sandbox part is read from is one a reader can point at.
    Ensure the paragraph beginning "Each artifact is read from exactly one revision" is unchanged and
    now has a producer. Ensure a statement exists that Symphony reads `WORKFLOW.md` host-side from
    the workspace directory as data — the read/execute distinction this section already draws for a
    host-side hook — and that the in-sandbox half's body is handed to the sandbox to run.
    *Done when* the "exactly one revision" property is checkable for `WORKFLOW.md` from Section 5.1
    alone.

18. **The reference algorithm (Section 16.6 `run_agent_attempt`).** Ensure the workflow template the
    turn prompt is built from is read from the provisioned working tree after
    `workspace_manager.provision_for_issue`, with a comment saying it is the repository's
    `repository.<name>.workflow` within that tree (Sections 5.1, 5.3.7) and that a read or parse
    failure fails this attempt (Section 5.5). Ensure `build_turn_prompt`'s inputs name that value.
    *Done when* no line of Section 16.6 uses a workflow template that arrived from outside the run.

19. **The startup algorithm (Section 16.1 `start_service`).** Ensure
    `start_workflow_watch(on_change=reload_and_reapply_workflow)` no longer arms a watch on
    `WORKFLOW.md`: the one artifact the process holds locally is the operator policy config
    (Section 6.2), and the call is the producer of the watch step 9 removes. Ensure the surrounding
    prose does not describe a workflow reload the algorithm no longer performs, and that
    `validate_dispatch_config()` stays as it is — it is Section 6.3's list, which step 10 shortens.
    *Done when* no line of Section 16.1 watches an artifact Section 6.2 says is not watched.

## Sites checked, needing no change

Recorded so a later reader can see the reach was walked rather than sampled.

- **Section 14.1 class 1 (`workflow_config_failures`).** Its bullet list names conditions, not
  dispositions; Section 14.2 is where a class splits. `tracker_failures` is listed once in Section
  14.1 and disposed of twice in Section 14.2, which is the precedent step 15 follows, so no
  Section 14.1 edit is owed.
- **Section 5.3's extension note** ("whether they belong to the policy config or `WORKFLOW.md`").
  Section 5's rule already forbids an extension from putting a host-executed setting in
  `WORKFLOW.md`; step 14 repairs the one violation rather than the permission. The note stands.
- **Section 18.1.2's hook row** ("`WORKFLOW.md` hooks in the sandbox from the worktree"). It is the
  producer that keeps step 2's second naming reachable: `Broker Core Conformance` reads
  `WORKFLOW.md` for its in-sandbox hook halves even in a topology with no dispatch, so the
  process-working-directory arm has a consumer and is not dead text.
- **Section 5.2 ("File Format") and its Design note.** Both already say `WORKFLOW.md` carries only
  what the agent needs inside the sandbox; step 14 makes that true rather than changing it.
- **Section 12.1 ("Inputs") and Section 4.1.2 ("Workflow Definition").** Both name
  `prompt_template`/`workflow.prompt_template` without saying where the file came from, and both
  stay produced by the loader.
- **`INSTALL.md`, `USAGE.md`, `docs/`.** Searched for `WORKFLOW.md`, workflow-path and `server.port`
  wording; no occurrence, so no derived document repeats the premise.
- **`conformance/README.md:581`** carries "against the orchestrator level" from decision 0159's
  resolved finding, which is about entry inheritance rather than about this artifact. Unrelated.
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`.** No obligation is created, so no row is owed; confirmed
  by re-reading the template's rows against the applied text.

## Cross-cutting sync

- **Section 17.1 ("Workflow and Config Parsing").** Ensure the workflow-path-precedence bullet checks
  the tree-relative rule: a dispatched run resolves the file at the repository's
  `repository.<name>.workflow` inside its per-issue workspace, and a session driven in an existing
  workspace resolves it by explicit setting then process working directory. Ensure the bullet
  "Workflow file changes are detected and trigger re-read/re-apply without restart" is replaced by
  one asserting the per-unit-of-work read: a `WORKFLOW.md` change mid-run does not alter that run and
  takes effect for the next, as the corresponding `repo.policy.toml` bullet in Section 17.2 already
  states. Ensure a bullet asserts that a `WORKFLOW.md` that is missing or whose front matter does not
  parse fails that run attempt and does not block dispatch for other repositories. Ensure a bullet
  asserts two repositories under one instance carry their own prompt templates and in-sandbox hook
  halves.
- **Section 17.2 ("Workspace Manager and Safety").** Ensure the trust-sourcing bullets name the
  working tree the in-sandbox declarations are read from, and that a bullet asserts an in-sandbox
  hook half is read from the tree the workspace provisioning derived.
- **Section 17.7 ("CLI and Host Lifecycle").** Ensure the three workflow-path bullets state which
  case they check — a process that runs in the workspace it acts in (Section 5.1) — rather than
  asserting the daemon resolves a workflow from its own working directory.
- **Section 18.1.1 ("Both Layer Profiles").** Ensure the three-artifacts row says what Section 6.2
  says: the operator policy config is watched and reloaded with last-known-good on invalid reload,
  while `repo.policy.toml` and `WORKFLOW.md` are read once at the start of each unit of work. The
  phrase "dynamic watch/reload/re-apply for all three" is decision 0097's superseded wording and
  MUST NOT survive. Ensure the row names `repository.<name>.workflow` as the pointer for the third
  artifact, as it already implies a pointer for the second.
- **Section 18.1.3 ("Daemon Conformance").** Ensure the "Workflow path selection supports explicit
  runtime path and cwd default" row is restated as the tree-relative resolution, and that the
  multiple-repositories row names the workflow pointer alongside the policy pointer.
- **Section 18.2 ("RECOMMENDED Extensions").** Ensure the HTTP server bullet names the operator
  policy config as the artifact `server.*` lives in, so the namespace paragraph that already places
  `observability.*` there covers both.
- **`conformance/vocabulary.json`.** Ensure the `config_namespaces` entry for `server` carries
  `"artifact": "operator_policy_config"` and a note recording that Section 13.8 enables the server
  from the operator policy config, with the placement decided here.
- **`conformance/README.md`.** Ensure the "**`server.*` is repository-owned by Section 13.8
  (open)**" finding is rewritten as resolved, naming this decision, stating what it was and what the
  resolution is, and keeping the observation that decision 0069 placed `observability.*` in the
  operator policy config rather than following `server.*` — which is now the precedent the repair
  followed rather than a route around a live rule.
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`.** No row is owed: this decision creates no
  `Implementation-defined` choice and no "MUST document" obligation. Confirm by re-reading the
  applied text before closing.
- Run `python3 scripts/validate_spec_consistency.py` and record the result.

## Ordering

Steps 1–3 first: the pointer and the sourcing rule are what every later step cites. Steps 4–6 are
independent vestige repairs and may run in any order. Steps 7, 10 and 15 travel together — the
preflight check, the gating behavior and the recovery disposition are one argument stated in three
places, and applying any one alone leaves the document briefly inconsistent. Steps 8, 9, 13, 17,
18 and 19 follow the sourcing rule, and step 19 travels with step 9 — the watch and the call that
arms it are one change in two places. Step 14 and its two corpus updates are separable from the rest and may
be applied independently. Cross-cutting sync last, and the validator after it.

## Out of scope, and owed separately

- **`hooks.workspace.timeout_ms` declared in `WORKFLOW.md` bounding a host-side half** (Section
  5.3.4). The defect is which half a declared bound applies to, which is decision 0158's axis rather
  than this one's. Filed, not fixed.
- **"Non-VCS workspaces"** (Sections 9.1, 9.3). A workspace with no working tree has no
  `WORKFLOW.md` to read; the case is already unreachable for a daemon-routed issue because
  `vcs.local_vcs` is REQUIRED of every `repository` entry (Sections 6.3, 9.7). The residue predates
  this decision and its repair turns on a different premise.

## Anchor changes

- `repository.<name>.workflow` — new key (Section 5.3.7).
- Section 5.1's workflow path precedence is no longer the general rule: the explicit
  application/runtime setting and the process-working-directory default now name the working tree a
  session runs in, for a deployment that drives a session in a workspace it did not dispatch. Any
  plan citing "cwd default" as the daemon's resolution is stale.
- Section 5.5's `Dispatch gating behavior:` no longer distinguishes workflow file/YAML errors from
  template errors; the two-behavior split is removed and one behavior replaces it.
- Section 6.3's `Validation checks:` no longer contains "Workflow file can be loaded and parsed".
- Section 6.2's "the two configuration artifacts it holds locally" becomes one artifact. (Decision
  0097 narrowed "all three" to "the two"; this narrows it again.)
- Section 13.8's `server.*` moves from `WORKFLOW.md` front matter to the operator policy config;
  `conformance/vocabulary.json`'s `server` entry changes `artifact` from `workflow_md` to
  `operator_policy_config`.
- Section 10's run-spec no longer carries the workflow template.
- Section 16.1's `start_workflow_watch(on_change=reload_and_reapply_workflow)` no longer watches
  `WORKFLOW.md`.

## Plan review (2026-08-27)

`python3 scripts/check_plan_anchors.py … --rev 987b949` reported 57 findings from 61 quoted spans.
Almost all are the file-attribution heuristic following this plan's own structure — a quote
attributed to `conformance/README.md` because a cross-cutting bullet named that file earlier, with
the script then reporting the span at exactly the `SPEC.md` section this plan cites. One Q finding is
a deliberate forward-quote: "the operator policy config, each repository's `WORKFLOW.md` front
matter, and each `repo.policy.toml`" (step 8) occurs nowhere in the corpus because it is the
post-condition, not a quotation of it.

Reading the R and P lenses found five defects in this plan, all repaired above before the first edit:

- **R** — "runtime settings" occurs at Section 3.2 as well as at Sections 1 and 14.5; the plan named
  two of three (step 6 now covers the third).
- **P** — Section 16.1's `start_workflow_watch` is the *producer* of the watch step 9 removes, and
  the plan did not name it (step 19).
- **P** — Section 6.3's opening sentence claims to validate "the workflow/config needed to poll and
  launch workers"; step 10 removes the only check that validated the workflow (step 10 extended).
- **P** — Section 6.2's "prompt content for future runs" survives step 9 with a different producer,
  the per-unit-of-work read rather than a reload; the plan said "stay true" without naming what
  makes it true (step 9 extended).
- **P** — Section 3.1's executor-composition paragraph lists components 5, 6 and 7; with the loader
  running per run it belongs in that set, and the plan said only "consistent with" (step 6 extended).

## Status

Applied to `SPEC.md` (Sections 1, 3.1, 3.2, 4.1.3, 5, 5.1, 5.3, 5.3.7, 5.5, 6.1, 6.2, 6.3, 6.4, 9.2,
10, 13.8, 14.2, 14.5, 15.4, 16.1, 16.6, 17.1, 17.2, 17.7, 18.1.1, 18.1.3, 18.2),
`conformance/vocabulary.json` and `conformance/README.md`.
`python3 scripts/validate_spec_consistency.py` → `0 error(s), 0 warning(s)`.
