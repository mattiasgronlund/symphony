# Plan — 0158 Where a workspace hook runs

## Scope

- `SPEC.md` Section 9.4 Workspace Hooks — the execution contract, the failure semantics, and a new
  availability rule. This is the section the decision is about.
- `SPEC.md` Section 9.2 Workspace Creation and Reuse — step 5's single `after_create` call.
- `SPEC.md` Section 16.6 Worker Attempt (Workspace + Prompt + Agent) — the `run_hook` and
  `run_hook_best_effort` calls.
- `SPEC.md` Section 8.6 Startup Terminal Workspace Cleanup — the `before_remove` half that has no
  run context.
- `SPEC.md` Section 16.3 Reconcile Active Runs — `terminate_running_issue`'s `cleanup_workspace_for`
  call. This is the second workspace-removal path and the only other one this specification defines;
  it has no live sandbox either, because `terminate_worker` runs before the cleanup call.
- `SPEC.md` Section 17.2 Workspace Manager and Safety — the four hook rows, which state one hook per
  lifecycle point.
- `SPEC.md` Section 18.1 REQUIRED for Conformance — the hook obligations.
- `conformance/vectors/config-defaults.json` — the `hooks.timeout_ms` path, which `SPEC.md` does not
  define.
- `conformance/README.md` — a "Surfaced findings" entry for that drift.
- `SPEC.md` Section 14.4 Partial State Recovery (Restart) — **unchanged**, cited only. Its recovery
  bullet names startup terminal workspace cleanup as a step and states nothing about hooks, so step 6
  changes what that step does without changing what Section 14.4 says about it.
- `SPEC.md` Section 5.3.4 `hooks.workspace` (object) — **unchanged**, cited only. It already states
  the split, that both artifacts carry both namespaces, and that both halves run when both define a
  lifecycle point. This decision adds no configuration and changes no field.
- `SPEC.md` Section 15.4 Configuration Trust Sourcing and Hook Safety — **unchanged**, cited only.
  It owns the working-directory rule and its rationale; Section 9.4 cites it rather than restating it,
  so the trust reasoning keeps one home.
- `SPEC.md` Section 9.6 Agent Sandbox and Execution Isolation — **unchanged**, cited only. Its
  run-scoped sandbox is what step 5 makes explicit; the profile, the privileged channel, and the
  constructed environment are untouched.
- `SPEC.md` Section 17.5 Coding-Agent Adapters — **unchanged**, cited only. Its row stating that a
  workspace hook terminated by a signal is failed, "so a killed `after_create` is fatal to workspace
  creation as a failing one is", stays true of each half: step 3 keeps the signal rule's scope and
  applies it per half, so no row is added or reworded here.
- `SPEC.md` Section 4.1.4 Workspace — **unchanged**. `created_now` gates the `after_create` lifecycle
  point, which is both of its halves; no field changes and no gate moves.
- `SPEC.md` Section 9.3 Workspace Population — **unchanged**. Its non-VCS allowance names which
  lifecycle points MAY populate a workspace, not which half runs, and its allowance to remove a
  partially prepared workspace is a creation-failure path that names no hook and gains none here.
- `SPEC.md` Section 3.1 Main Components — **unchanged**, cited only. The `Execution Process` already
  "runs both hook trust levels" and "is the host relative to its own agent sandbox"; step 5 relies on
  that sentence rather than adding to it.
- `conformance/vocabulary.json` — **unchanged**. No published token is added, renamed, or removed:
  `config_namespaces` publishes the `hooks` top-level key, which is unaffected by correcting a dotted
  path inside a vector.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **unchanged**. This decision adds no `Implementation-defined`
  choice and no "MUST document" obligation: every answer it fixes is prescriptive, so there is no row
  to add (the working-directory rule, the order, the failure short-circuit, and the availability rule
  are all stated, not delegated).

## Steps

1. `SPEC.md` Section 9.4 Workspace Hooks, *Execution contract*: ensure it names both execution contexts rather
   than one. Post-condition: the contract states that a lifecycle point's `repo.policy.toml` half runs
   host-side and its `WORKFLOW.md` half runs in-sandbox (Sections 5.3.4, 15.4); that the working
   directory differs by context, with Section 15.4 stating the rule and this Section 9.4 no longer
   carrying "with the workspace directory as `cwd`" unconditionally; and that the `sh -lc` / `bash -lc` default and
   `hooks.workspace.timeout_ms` apply to each half independently. Done when Section 9.4 contains no
   sentence that is true of only one context while reading as though it were true of both.

2. `SPEC.md` Section 9.4, ordering: ensure the order of the two halves is stated for each lifecycle point.
   Post-condition: `after_create` and `before_run` run the host-side half first and the in-sandbox
   half second; `after_run` and `before_remove` run the in-sandbox half first and the host-side half
   second, so teardown unwinds setup. Done when a reader can say, for any of the four names, which
   half runs first.

3. `SPEC.md` Section 9.4, *Failure semantics*: ensure each existing bullet is true of each half, and that a
   fatal half short-circuits the other. Post-condition: `after_create` failure or timeout in either
   half is fatal to workspace creation and the half that has not run does not run; `before_run`
   likewise for the current run attempt; `after_run` and `before_remove` failures stay logged and
   ignored in both halves. The signal-termination rule keeps its current scope and applies per half.
   Done when no bullet reads as though a lifecycle point has one process.

4. `SPEC.md` Section 9.4, availability: ensure the in-sandbox half is required only where a run context exists.
   Post-condition: an in-sandbox half runs in the run attempt's sandbox, instantiated by the executor
   (Section 3.1) and available for the whole attempt — it outlives the agent session's
   `release(continuation_ref)` (Section 10.7) and ends with the attempt; where no run context exists
   the in-sandbox half is not run and the skip is logged. The lifetime is stated because every
   `after_run` call site in Section 16.6 follows `agent.release`, and Section 10.7's `release` frees
   "warm resources (a live subprocess, a session handle)" — without the clause the in-sandbox
   `after_run` half rests
   on a sandbox lifetime no section fixes. Done when the requirement is satisfiable at all four
   lifecycle points, and when placing an in-sandbox `after_run` needs no implementation choice about
   how long the sandbox lives.

5. `SPEC.md` Section 9.6 Agent Sandbox and Execution Isolation is cited, not edited: ensure Section 9.4's
   availability rule reads against a sandbox scoped to the run attempt rather than to a turn, since
   `before_run` precedes the first turn. Step 4 states the lifetime in Section 9.4, where the
   availability rule lives; Section 9.6 keeps its "Each coding-agent run MUST be runnable inside a
   sandbox" framing untouched. Done when step 4's rule and Section 9.6 can both be true with no
   sentence added to Section 9.6.

6. `SPEC.md` Section 8.6 Startup Terminal Workspace Cleanup and `SPEC.md` Section 16.3 Reconcile Active
   Runs: ensure each workspace-removal path states which halves run. Post-condition: Section 8.6's
   step 2 removal runs the host-side `before_remove` half only, no run context existing at service
   start; `terminate_running_issue`'s `cleanup_workspace_for` call likewise, the worker having been
   terminated before cleanup. Section 9.4 states the consequence rather than leaving it to be
   derived: a `WORKFLOW.md`-declared `before_remove` is valid configuration that no removal path this
   specification defines supplies a run context for, so its half does not run and the skip is logged.
   Done when both removal sites name the disposition and Section 9.4 says so plainly, rather than a
   reader having to compose the availability rule with the two call sites to find out.

7. `SPEC.md` Section 9.2 Workspace Creation and Reuse, step 5: ensure the `created_now=true` step runs both
   halves in the order step 2 fixes, rather than one call reading `run after_create hook if configured`. Done when the algorithm
   summary distinguishes the halves.

8. `SPEC.md` Section 16.6 Worker Attempt (Workspace + Prompt + Agent): ensure `run_hook("before_run", ...)`
   and each `run_hook_best_effort("after_run", ...)` distinguish the two halves in the order step 2
   fixes, keeping the host-side call's existing shape — the workspace passed as an argument, not as a
   working directory. Post-condition: the pseudocode has a call site for each half at each of the two
   lifecycle points it covers, and the `before_run` failure branch keeps `fail_worker(run_id,
   "before_run hook error")`. Done when no lifecycle point in Section 16.6 has exactly one call.

9. `SPEC.md` Section 17.2 Workspace Manager and Safety: ensure the four hook rows cover both halves, the
   ordering from step 2, the short-circuit from step 3, and the removal-path skip from step 6. Done
   when a conforming implementation that ran only the host-side half would fail a row, and when the
   working-directory rule is not restated: Section 17.2 already carries it in the row beginning "A
   host-side hook declaring a unit at a path the agent can also write".

10. `SPEC.md` Section 18.1 REQUIRED for Conformance, under `18.1.2 Broker Core Conformance`: ensure the
    hook obligations name the ordering and the removal-path disposition, matching the existing entry's
    altitude. Section 18.1.2's "Workspace lifecycle hooks at two trust levels sourced by trust" entry
    already names
    both contexts and the host-side working directory; what it does not carry is which half runs first
    at each lifecycle point, that a fatal half short-circuits the other, and that a removal path runs
    the host-side half only. Done when the checklist does not read as one hook per lifecycle point.

11. `conformance/vectors/config-defaults.json`: ensure the resolved path is
    `hooks.workspace.timeout_ms` with its value `60000` unchanged. Done when every dotted path the
    vector asserts exists in Section 6.4's cheat sheet.

12. `conformance/README.md`: ensure a "Surfaced findings" entry records the drift and its resolution,
    in the shape the existing entries use (finding, section, decision). Done when the entry names this
    decision.

## Cross-cutting sync

- Section 6.4 (config cheat sheet) — no change. No field is added, renamed, or given a new default;
  `hooks.workspace.timeout_ms` and its `60000` default are already correct there.
- Section 17 (test matrix) — step 9 and its rows, above. Section 17.5's signal row is unchanged, for
  the reason recorded in Scope.
- Section 18 (implementation checklist) — step 10, above, under Section 18.1.2.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row, for the reason recorded in Scope.

## Anchor changes

Nothing renamed or removed in `SPEC.md`; no section is retitled. **Added:** two pseudocode function
names in Section 16.6, `run_sandbox_hook` and `run_sandbox_hook_best_effort`, the in-sandbox
counterparts of the existing `run_hook` and `run_hook_best_effort`. The existing pair keeps its name,
its host-side meaning, and its call shape — the workspace passed as an argument — so no call site
changes meaning; the new names carry the half that had none. Their semantics are Section 9.4's, as
the existing pair's are.

The corpus correction in step 11 restores an existing anchor rather than changing one: the vector's
`hooks.timeout_ms` never named a `SPEC.md` field, and `hooks.workspace.timeout_ms` (Sections 5.3.4,
6.4, 9.4) is unchanged by this decision.

## Plan review

Reviewed with `plan-review` against `38e3e25`, the revision the plan was written on and the one whose
`SPEC.md` is unchanged at review time. Lenses Q, R, C, P.

- **Q, R (mechanical):** `python3 scripts/check_plan_anchors.py` reported 0 findings from 9 quoted
  spans on the plan as first written. After the repairs below it quotes 14 spans; one R site remains
  unnamed on purpose — `conformance/vcsx/vocabulary.json` `hook_conditions` carries the four-word
  window "a unit at a" from Section 17.2's host-side-unit row, in the engine's `[hooks]` vocabulary,
  which is a different hook axis and is untouched here.
- **R (repaired):** the plan named Section 8.6 as the `before_remove` path with no run context and
  missed the second one. Section 16.3's `terminate_running_issue` removes a workspace too, after
  `terminate_worker`, so it has no live sandbox either. In Scope and step 6.
- **P (repaired):** the in-sandbox `before_remove` half had no surviving producer. Step 4 makes it
  conditional on a run context, step 6 makes startup cleanup host-side only, and the reconciliation
  path kills the worker before cleanup — while Section 5.3.4, which this decision leaves unchanged,
  keeps `before_remove` declarable in `WORKFLOW.md`. Settled by stating it: both removal paths run
  the host-side half only, and Section 9.4 says plainly that no removal path this specification
  defines supplies a run context for the in-sandbox half. Step 6.
- **P (repaired):** the in-sandbox `after_run` half rested on a sandbox lifetime no section fixed.
  Every Section 16.6 `after_run` call site follows `agent.release`, and Section 10.7's `release`
  frees warm resources. Settled by stating the lifetime in Section 9.4 beside the availability rule
  rather than editing Section 9.6, and keeping Section 16.6's call order. Steps 4 and 5.
- **C:** implementation lands in the sibling worktree `../symphony-0158-hook-execution-context`. The
  cross-cutting sections are named (Sections 6.4 no-change with its reason, 17 via step 9, 18.1.2 via
  step 10). No Conformance Statement row is owed, re-checked against the settled forks: the
  availability rule, the removal-path disposition, the ordering and the short-circuit are all
  prescriptive, and none adds an `Implementation-defined` choice or a "MUST document" obligation.

## Status

Applied. Steps 1 to 10 are in `SPEC.md` (Sections 8.6, 9.2, 9.4, 16.3, 16.6, 17.2, 18.1.2); step 11
is in `conformance/vectors/config-defaults.json` and step 12 in `conformance/README.md`. Sections
5.3.4, 9.6, 15.4, 3.1, 6.4 and 17.5 are unchanged, as Scope records, and `conformance/vocabulary.json`
and `CONFORMANCE-STATEMENT-TEMPLATE.md` are untouched. `python3 scripts/validate_spec_consistency.py`
reports 0 errors and 0 warnings.

The two post-conditions flagged before execution were both settled by the operator against the plan
review's findings: the in-sandbox half's availability is stated with the sandbox lifetime it depends
on (step 4), and a `WORKFLOW.md`-declared `before_remove` is stated to have no removal path that runs
it rather than being given one at reconciliation teardown (step 6). `Background.md` records both under
"What the plan review changed".
