# Plan — 0095 A host-side hook's unit comes from the trusted source

## Scope

`SPEC.md`: Section 15.4 "Configuration Trust Sourcing and Hook Safety" (the hook implications),
Section 5.3.4 "Workspace Hooks", Section 17 "Test Matrix", Section 18 "Implementation Checklist".

`VCSX-SPEC.md`: Sections 6.6 "`[hooks]`", 8.6 "Invocation Preconditions" (the "property of the
worktree" sentence), 13.1 "Test Matrix", 13.2 "Implementation Checklist", 13.3 "Conformance
Statement".

`VCSX-CONTRACT.md`: Section 10 "Trust Sourcing".

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

## Tokens introduced

None. The repair constrains existing surface; the context names `host_side` and `in_sandbox` are
retained deliberately (see `Background.md`).

## Steps

1. **The unit's provenance (`SPEC.md` Section 15.4, hook implications)** — ensure the host-side
   bullet states that the unit a host-side hook runs is resolved from the policy branch and never
   from the working tree, so that the trust the declaration carries extends to the program it names.
   *Done when* no reading of Section 15.4 permits a host-side hook to execute content the agent can
   write.

2. **The working directory splits by context (`SPEC.md` Section 15.4)** — ensure the sentence "Hooks
   run with the workspace directory as their working directory" no longer applies to host-side
   hooks; ensure in-sandbox hooks keep it, and ensure a host-side hook receives the workspace path
   as an argument or environment value instead. *Done when* the working-directory rule names the
   context it applies to, and a host-side hook still has a stated way to reach the tree it inspects.

3. **The documentation obligation (`SPEC.md` Section 15.4)** — ensure an implementation MUST
   document how it resolves a host-side hook's unit, since the unit's form is
   `Implementation-defined`. *Done when* the obligation is stated where the rule is.

4. **Read as data, not as code (`SPEC.md` Section 15.4)** — ensure the section states that a
   host-side hook MAY read the workspace and MUST NOT execute from it, so a content scan or a build
   check remains expressible. *Done when* the distinction is stated rather than left to be inferred
   from the two rules above.

5. **The engine states it without branches (`VCSX-SPEC.md` Section 6.6)** — ensure the `[hooks]`
   section states that a `host_side` hook's unit resolves from the same source the host-side policy
   was read from, and that its working directory is not the working tree; ensure an `in_sandbox`
   hook's unit continues to resolve from the working tree. *Done when* the rule appears with no
   mention of a branch, and reads correctly for a consumer with no sandbox.

6. **The worktree sentence is qualified (`VCSX-SPEC.md` Section 8.6)** — ensure "Whether the unit a
   `run` names exists and can be started is a property of the worktree" is scoped to in-sandbox
   hooks, and that a host-side unit is a property of the trusted source. Ensure the first-use
   disposition (`hook_unanswered`) is unchanged for both. *Done when* the sentence no longer asserts
   the worktree for every hook.

7. **The contract carries the rule (`VCSX-CONTRACT.md` Section 10)** — ensure the trust-sourcing
   section states that a host-side hook's unit is sourced as its declaration is. *Done when* the
   contract's sourcing rule covers the program as well as the policy.

## Cross-cutting sync

- **`SPEC.md` test matrix (Section 17)** — a host-side hook whose declared unit names a path the
  agent can write does not execute agent-written content; a host-side hook still reads the workspace
  it is given; an in-sandbox hook continues to run with the workspace as its working directory.
- **`SPEC.md` checklist (Section 18)** — the two-trust-level hook item names unit provenance
  alongside declaration sourcing.
- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a `host_side` hook's unit resolves from the
  host-side policy source and a working-tree unit of the same name is not what runs; an `in_sandbox`
  hook's unit resolves from the working tree; both keep `hook_unanswered` where the unit cannot be
  started.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — hook units resolve by context.
- **`VCSX-SPEC.md` Conformance Statement (Section 13.3)** and
  **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — a row for how a host-side unit is resolved, which
  is `Implementation-defined`.

## Anchor changes

- `SPEC.md` Section 15.4's sentence **"Hooks run with the workspace directory as their working
  directory"** is removed, superseded by a context-dependent rule. Plans addressing it as a
  universal rule are stale.
- `VCSX-SPEC.md` Section 8.6's phrase **"a property of the worktree"**, as applied to every hook
  unit, is narrowed to in-sandbox hooks.
- No token is renamed. `host_side` and `in_sandbox` are retained; the alternative naming
  (`policy_branch`) was considered and rejected in `Background.md`.

## Status

Accepted. Applied to `SPEC.md`, `VCSX-SPEC.md`, `VCSX-CONTRACT.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

Deliberately out of scope, and recorded in `Background.md` with the measurement that defeated it: a
rule forbidding a `[policy]` edge from conditioning credentialed work on an in-sandbox gate's
outcome. The broker's verb set already exposes every credentialed operation such an edge could
dispatch, so the rule would forbid the ordinary `commit:ok → run_op push` flow while closing almost
nothing.
