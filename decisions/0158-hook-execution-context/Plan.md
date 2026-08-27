# Plan — 0158 Where a workspace hook runs

## Scope

- `SPEC.md` Section 9.4 Workspace Hooks — the execution contract, the failure semantics, and a new
  availability rule. This is the section the decision is about.
- `SPEC.md` Section 9.2 Workspace Creation and Reuse — step 5's single `after_create` call.
- `SPEC.md` Section 16.6 Worker Attempt (Workspace + Prompt + Agent) — the `run_hook` and
  `run_hook_best_effort` calls.
- `SPEC.md` Section 8.6 Startup Terminal Workspace Cleanup — the `before_remove` half that has no
  run context.
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
   Post-condition: an in-sandbox half runs in the run's sandbox, instantiated by the executor (Section
   3.1); where no run context exists the in-sandbox half is not run and the skip is logged. Done when
   the requirement is satisfiable at all four lifecycle points.

5. `SPEC.md` Section 9.6 Agent Sandbox and Execution Isolation is cited, not edited: ensure Section 9.4's
   availability rule reads against a sandbox scoped to the run attempt rather than to a turn, since
   `before_run` precedes the first turn. Done when step 4's rule and Section 9.6 can both be true
   without an implementation choosing a sandbox lifetime.

6. `SPEC.md` Section 8.6 Startup Terminal Workspace Cleanup: ensure step 2's workspace removal states that it
   runs the host-side `before_remove` half only, with no run context for an in-sandbox half. Done when
   the section names the disposition rather than leaving it to be derived from Section 9.4.

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
   ordering from step 2, the short-circuit from step 3, and the startup-cleanup skip from step 6. Done
   when a conforming implementation that ran only the host-side half would fail a row.

10. `SPEC.md` Section 18.1 REQUIRED for Conformance: ensure the hook obligations name both contexts and the
    ordering, matching the existing entry's altitude. Done when the checklist does not read as one
    hook per lifecycle point.

11. `conformance/vectors/config-defaults.json`: ensure the resolved path is
    `hooks.workspace.timeout_ms` with its value `60000` unchanged. Done when every dotted path the
    vector asserts exists in Section 6.4's cheat sheet.

12. `conformance/README.md`: ensure a "Surfaced findings" entry records the drift and its resolution,
    in the shape the existing entries use (finding, section, decision). Done when the entry names this
    decision.

## Cross-cutting sync

- Section 6.4 (config cheat sheet) — no change. No field is added, renamed, or given a new default;
  `hooks.workspace.timeout_ms` and its `60000` default are already correct there.
- Section 17 (test matrix) — steps 9 and its rows, above.
- Section 18 (implementation checklist) — step 10, above.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row, for the reason recorded in Scope.

## Anchor changes

None in `SPEC.md`. No section is retitled and no code token is renamed or removed; the decision adds
prose and pseudocode call sites at existing anchors.

The corpus correction in step 11 restores an existing anchor rather than changing one: the vector's
`hooks.timeout_ms` never named a `SPEC.md` field, and `hooks.workspace.timeout_ms` (Sections 5.3.4,
6.4, 9.4) is unchanged by this decision.

## Status

Not started — **Proposed**. Option A is recommended in `Background.md` and no `SPEC.md` change has been
made. Step 4's availability rule and step 5's run-scoped sandbox reading are the two post-conditions
worth confirming before the plan is executed, because they are normative additions rather than repairs
of existing text.
