# Plan — 0188 A workspace is created when its `after_create` completes

## Scope

- **`SPEC.md`:**
  - Section 4.1.4 (Workspace), the `created_now` field;
  - Section 5.3.4 (`hooks.workspace` (object)), the `after_create` field;
  - Section 8.6 (Startup Terminal Workspace Cleanup);
  - Section 9.2 (Workspace Creation and Reuse);
  - Section 9.3 (Workspace Population);
  - Section 9.4 (Workspace Hooks), its Availability and Failure semantics lists;
  - Section 16.3 (Reconcile Active Runs), `terminate_running_issue`;
  - Section 16.6 (Worker Attempt (Workspace + Prompt + Agent));
  - Section 17.2 (Workspace Manager and Safety) and Section 18.1.2 (Broker Core Conformance).
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`:** Section 4.1 (Core), two rows.

The engine documents are unchanged. The engine has no notion of a workspace being created
(`SPEC.md` Section 5.3.4's boundary note), and the completion record is Symphony's.

## Steps

1. **Definition, in Section 9.2 (Workspace Creation and Reuse).** Ensure the section states, ahead
   of the algorithm:
   - A workspace is *created* once its `after_create` halves have completed, or once step 3
     completes when neither half is configured. A directory at the workspace path without a
     completion record is *uncreated*.
   - The completion record is held by the party holding the workspace (Section 3.1), outside the
     workspace and outside anything the sandbox can write (Section 9.6).
   - The record is written atomically, or is a marker whose existence alone is the signal, so that a
     partly written record never reads as present.
   - Where the record lives is `Implementation-defined`, and an implementation MUST document it.

   Done when the definition and the four record properties are in Section 9.2.
2. **Algorithm, in Section 9.2.** Ensure the numbered list:
   - At step 3: where the directory is absent, the completion record is cleared, durably, before the
     directory is created. Where the directory is uncreated, it is discarded (record first, then
     directory) and created again.
   - At step 4: `created_now=true` when step 3 created the directory, including after a discard, and
     `created_now=false` only for a created workspace. In `SPEC.md`, the text "only if the directory
     was created during this call" no longer stands alone.
   - After step 6: a final step writes the completion record once both configured halves have
     returned. The record is durable before any agent session starts against the workspace.

   Done when no path through the list leaves a directory reused without a completion record.
3. **Notes in Section 9.2.** Ensure a `Note:` says the rule depends on whether creation completed,
   never on why it did not. It names an `after_create` failure, a timeout, a signal, an attempt
   ending before `after_create`, and process death. It also says a discarded directory is
   recreated, not resumed, because a hook script is written for a new directory.
4. **Migration, in Section 9.2.** Ensure a bullet says that how an implementation treats workspaces
   that predate its writing of completion records is `Implementation-defined`, and that an
   implementation MUST document it. It also says why: an undocumented migration discards
   workspaces that may hold unpushed agent work.
5. **Section 9.3 (Workspace Population).** Ensure the bullet beginning "If failure happens while
   creating a brand-new workspace" keeps its MAY for eager removal. Ensure it says the directory is
   uncreated either way, and is discarded by the next attempt (the Section 9.2 discard). Ensure the
   Section 9.3 bullet beginning "Reused workspaces SHOULD NOT be destructively reset" is scoped to a created workspace,
   so it does not read as forbidding Section 9.2's discard (plan review, P).
6. **Section 9.4 (Workspace Hooks), Availability.** Ensure, beside the list of removal paths "this
   specification defines", a bullet says:
   - Discarding an uncreated directory is not a workspace removal, and no `before_remove` half runs
     on it, in either execution context.
   - A removal path that finds an uncreated directory discards it the same way.
   - The reason is that teardown unwinds a setup that completed, and a host-side `after_create` undoes
     its own partial effects itself.
7. **Section 9.4, Failure semantics.** Ensure the `after_create` bullet says a fatal half leaves the
   workspace uncreated, so the next attempt runs `after_create` again on a freshly created directory
   (Section 9.2).
8. **Section 5.3.4 (`hooks.workspace` (object)).** Ensure the `after_create` field's sub-bullets
   read: runs when a workspace is created, which includes recreating an uncreated one; and failure
   leaves the workspace uncreated (Section 9.2). Ensure the Section 5.3.4 `before_remove` field's
   first sub-bullet, "Runs before workspace deletion if the directory exists", says it runs for a created workspace,
   and that discarding an uncreated directory runs it in neither half (plan review, P).
9. **Section 4.1.4 (Workspace).** Ensure `created_now` is described as true when this call created
   the directory, including recreating an uncreated one, and that it gates `after_create`.
9a. **Section 9.1 (Workspace Layout).** Ensure the bullet "Workspaces are reused across runs" says a *created* workspace is reused, with an uncreated one recreated (Section 9.2)
    (plan review, P).
10. **Section 8.6 (Startup Terminal Workspace Cleanup).** Ensure step 2 says an uncreated directory is
    discarded with no `before_remove` half (Section 9.4).
11. **Section 16.3 (Reconcile Active Runs).** Ensure the `cleanup_workspace` comment in
    `terminate_running_issue` says a worker terminated before its `after_create` completed leaves an
    uncreated directory, which `cleanup_workspace_for` discards without `before_remove`.
12. **Section 16.6 (Worker Attempt (Workspace + Prompt + Agent)).** Ensure, after the
    `workflow_loader.read` arm and before `engine.integrate`:
    - An `if workspace.created_now:` block calls `run_hook("after_create", workspace.path)`, then
      `run_sandbox_hook("after_create", workspace)`. Each failure calls
      `fail_worker` with the reason `after_create hook error`.
    - The block then calls `workspace_manager.mark_created(workspace)`.
    - A comment cites Section 9.2: the half order, the short-circuit, and that a failure leaves the
      directory uncreated.
    - The `provision_for_issue` comment says it performs Section 9.2's discard and clears and
      reports `created_now`.

    Done when `after_create` appears in Section 16.6.
13. **Section 17.2 (Workspace Manager and Safety).** Ensure the matrix carries:
    - A row: `after_create` fails once, and the next attempt runs it again on a freshly derived tree.
    - A row: the service is killed during `after_create` and restarted, and the next dispatch runs
      `after_create` again.
    - A row: a directory deleted by hand, followed by a failing `after_create`, is still uncreated on
      the attempt after.
    - A row: no agent session starts against an uncreated directory.
    - Extended text in the `before_remove` row: discarding an uncreated directory runs neither half.
    - Revised rows (plan review, P): "Existing workspace directory is reused" applies to a created
      workspace, and the `after_create` row says it runs when creation has not completed rather than
      only on new workspace creation.
14. **`SPEC.md` Section 18.1.2 (Broker Core Conformance).** Ensure an item follows the one beginning
    "Both halves of a lifecycle point execute". It states: created means `after_create` completed; an uncreated
    directory is discarded and recreated; the record is outside the sandbox's reach, crash-safe and
    durably cleared; and a discard runs no `before_remove`. Ensure the item beginning "Both halves of
    a lifecycle point execute" scopes its removal-path clause to a created workspace (plan review, P).
15. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 (Core).** Ensure two rows cite Section 9.2:
    - `Where the workspace completion record is held`, with the resolution
      `<location, and how it is kept outside the sandbox's writable mounts>`.
    - `Treatment of workspaces that predate completion records`, with the resolution
      `<treated as created / discarded / other, and how an operator is told>`.

    Done when `python3 scripts/validate_spec_consistency.py` reports no errors.

## Cross-cutting sync

- **`SPEC.md` Section 6.4**: no configuration key changes.
- **`SPEC.md` Sections 17 and 18**: steps 13 and 14.
- **`CONFORMANCE-STATEMENT-TEMPLATE.md`**: step 15. Two `Implementation-defined` obligations are
  added (decision 0128).
- **`VCSX-SPEC.md` Section 13**: unchanged.

## Anchor changes

- Added: the terms *created* and *uncreated* for a workspace, and the *completion record* (`SPEC.md`
  Section 9.2).
- Added: `mark_created` and an `after_create` call site in `SPEC.md` Section 16.6's pseudocode.
- Changed: `created_now`'s meaning (`SPEC.md` Section 4.1.4), from *the directory was created during
  this call* to *this call created the directory, including recreating an uncreated one*.

## Plan review

Run against `c9f031f` (`check_plan_anchors.py --rev HEAD`). Q and R reported 8 findings on the first
draft and none after repair. Six were attribution artifacts of the Scope naming the engine
documents. Two were real: the hook checklist items live in Section 18.1.2, not 18.1.1, and two
quotations of proposed text were written as quotations of existing text. C found nothing: a sibling
worktree, cross-cutting sections named, and both new obligations given template rows.

P found five kept consequences whose premise this decision removes, namely that every directory at
a workspace path is a workspace. Each is now a step: Section 5.3.4's `before_remove` "if the
directory exists", Section 9.1's reuse bullet, Section 9.3's SHOULD NOT on resetting reused
workspaces, Section 17.2's reuse and `after_create` rows, and Section 18.1.2's removal-path
clause. Recorded as needing no change: Section 10.7's outline step "Create/reuse workspace for
issue" (a summary that defers to Section 9.2), and Section 16.1's `startup_terminal_workspace_cleanup()`
call (it carries no hook text).

## Status

Applied to `SPEC.md` and `CONFORMANCE-STATEMENT-TEMPLATE.md` on branch
`0188-uncreated-workspace`.
