# Background — 0188 A workspace is created when its `after_create` completes

## Context

Reported from `symphony-rs` as issue #188, at pin `c9f031f`. It was found while moving in-sandbox
hook halves into the run's sandbox (that repository's decision 0161).

`SPEC.md` gives a workspace two states and no third:

- Section 9.2 step 4 marks `created_now=true` "only if the directory was created during this call",
  and step 6 runs the `after_create` halves only when it is true.
- Section 9.4 says an `after_create` failure or timeout in either half "is fatal to workspace
  creation". Section 5.3.4 says "Failure aborts workspace creation", and Section 17.2 repeats it.
- Nothing says what a fatal creation leaves behind. Step 3 has already made the directory and, for a
  VCS-managed repository, derived a working tree into it. Section 9.3 says an implementation MAY
  remove a partially prepared directory, which does not require that anything be removed.

## The failure path

1. Attempt 1 for `ENG-1` reaches step 3, which creates the directory and derives the tree.
2. `after_create`'s host-side half fails, times out or is killed by a signal (which Section 9.4
   counts as failing). Or the attempt ends before reaching `after_create` at all. `symphony-rs` lists
   seven such causes between creation and the first hook, among them a broker bind, an egress bind,
   credential resolution and a refused sandbox launch. Its directory has to exist before the
   sandbox launches, because the sandbox binds it.
3. The directory stays. Attempt 2 reaches step 4 with the directory present and marks
   `created_now=false`. Step 6 skips `after_create`.
4. Attempt 2 and every later attempt run the agent in a workspace without what Section 5.3.4 puts
   there: dependency bootstrap, build, or code generation. Nothing retries the hook, and nothing
   reports anything after attempt 1's failure.

"Fatal to workspace creation" reads most naturally as "there is no workspace". But the spec defines
no step that makes that true.

## Why cleaning up when the attempt ends does not close it

The first fix that suggests itself is the one `symphony-rs` built (its decision 0011 R116, PR
Identione/symphony-rs#202): when an attempt ends before the `after_create` halves of a workspace it
created have completed, remove the directory. That PR does it with a drop guard
(`crates/symphony-host/src/composition/attempt.rs:568`, with `Drop` at `:595`).

Any rule that runs when an attempt ends needs something still running at that point to carry it
out. A host crash, a `SIGKILL`, a reboot, or a remote node lost under Section 9.11 all end the
attempt with nothing left to run the cleanup. The directory then survives exactly as in step 3
above. So the cleanup shrinks the window and does not close it, as `symphony-rs` agreed on the
issue. The gap is a fact about the directory that is never recorded, so the fix has to be a record
that survives the process dying.

## Decision

**Created means completed.** A workspace is created when its `after_create` halves have completed,
or when step 3 completes if neither half is configured. Symphony keeps a completion record of that
moment. A directory that exists with no completion record is **uncreated**:

- Section 9.2 step 4 marks `created_now=true` when it creates the directory, and also when it finds
  an uncreated one. In that case it discards the existing directory and creates it again before
  step 5, so `after_create` runs against a freshly derived tree. It does not run against whatever a
  half-run `after_create` left behind, since hook scripts are written for a new directory, not to
  be re-entered. `git clone` into a directory that already exists is the commonest example.
- The rule depends on whether creation completed, never on why it did not. A failing half, a
  timeout, a killed half, a pre-hook failure and process death all leave the same state, so one rule
  covers every cause, including causes the spec has not listed.
- Eager removal when an attempt fails, Section 9.3's MAY, stays as a tidy-up. Correctness no longer
  depends on it.

**Discarding an uncreated directory is not a workspace removal.** No `before_remove` half runs on it.
Section 9.4 orders teardown so that it "unwinds setup", and `before_remove` is written against a
setup that completed. Running it against a setup that did not complete is wrong in both directions:
it may undo things that never happened, or miss things that partly did. A host-side `after_create`
that has to undo its own partial effects does that inside the script, for example with a `trap`,
where the knowledge of what it did lives. The same holds where an existing removal path finds an
uncreated directory: the startup sweep (Section 8.6), or reconciliation terminating a worker
mid-`after_create` with `cleanup_workspace=true` (Section 16.3). Each discards it with no
`before_remove`.

**The record's own requirements.** Each rule below exists because without it the record reproduces
the failure it was introduced to close:

- **Outside the workspace and outside anything the sandbox can write.** Section 9.6 bind-mounts the
  working tree into the sandbox, writable. A record inside the tree could be written by an
  in-sandbox `after_create` half that then fails, and the directory would read as created. An agent
  could also delete it, which discards its own work on the next attempt.
- **Kept by whichever party holds the workspace** (the executor, Section 3.1). Under Section 9.11 the
  workspace lives on a node. A record held on the orchestrator's side can disagree with the
  directory it describes after either side fails, with no process alive to reconcile them. Stating
  this as "same host" would describe a mechanism, not a guarantee. The guarantee is that the record
  and the directory cannot fail separately.
- **Written only after the second half returns.** It is written atomically, or it is a marker whose
  existence alone is the signal, so that a half-written record never reads as present.
- **Durable before the first agent session starts against the workspace.** "Durable" here means it
  survives a crash of the host holding it. Otherwise a crash loses a record that was written but
  never saved, and the next attempt discards a workspace the agent had already worked in.
- **Cleared before step 4 creates the directory, and durably.** Without the clear, a directory
  deleted by an operator leaves its record behind. The next creation then has a record from the
  start, an `after_create` failure leaves directory and record together, and the attempt after that
  treats the workspace as created. The clear also has to be durable before the directory is created.
  Removing a file and creating a directory are separate operations, and a filesystem does not
  promise to make them durable in the order they ran. On POSIX, a removal is durable only once its
  containing directory is synced (`fsync(2)`: syncing a file "does not necessarily ensure that the
  entry in the directory containing the file has also reached disk"). A crash can therefore keep
  the new directory and lose the removal.
- **Cleared before the directory on removal or discard.** A crash between the two then leaves a
  directory with no record, which the next attempt discards. The other order leaves a record with no
  directory. That is harmless only because of the clear-before-create rule, which is why removal
  needs no durability rule of its own. Clearing at removal mainly stops stale records piling up.

**Where the record lives is `Implementation-defined`, and an implementation MUST document it.** An
operator needs to know, because deleting it forces the workspace to be rebuilt from scratch. **How an
implementation migrates is `Implementation-defined` too, and it MUST document that.** On the day an
implementation starts writing records, no existing workspace has one. Under the new step 4 each
would be discarded, including workspaces whose agent work has not been pushed. Outside migration
that risk does not exist: no agent session can run in a directory without a record, so a discarded
directory never holds agent work. Each obligation takes a row in `CONFORMANCE-STATEMENT-TEMPLATE.md`
(decision 0128).

**The reference algorithm gains its `after_create` call sites.** Section 16.6 never calls
`after_create`. `provision_for_issue` derives the tree, and `WORKFLOW.md` is read after it. But
Section 9.2 step 5 says the in-sandbox half's declaration is read from that file, so the in-sandbox
half cannot run inside `provision_for_issue`. `symphony-rs` hit the same order: its
`provision::perform` has to read `WORKFLOW.md` before the in-sandbox half can run. Section 16.6 now
makes the calls after the workflow read and before `before_run`, then writes the completion record.

## Options considered

- **A. Clean up when the attempt ends (`symphony-rs` R116 as first built).** The steelman: it adds no
  state and no new artifact, it matches Section 9.3's existing MAY, and it handles every cause the
  process survives. It loses because the cause it cannot handle, the process dying, is exactly the
  one a long-running service meets in a crash, a node loss or a deploy. It leaves the same
  permanent, silent skip with no one to report it.
- **B. Keep the record inside the workspace** (a marker file in the tree). The steelman is strong:
  the record shares the directory's failure domain without any rule saying so, and removing the
  directory removes the record. That makes the stale-record problem impossible and the clear rules
  unnecessary. It loses because the tree is the sandbox's writable mount (Section 9.6). An
  in-sandbox `after_create` half could write the marker and then fail, and an agent could delete it
  or commit it. That turns a correctness signal into something untrusted code controls, which
  Section 15.4's split by trust exists to prevent.
- **C. Tie the record to the directory's identity** (an inode, or a creation nonce) rather than
  clearing it. A stale record then fails to match a new directory, with no clear needed. It loses
  because inode numbers are reused and are not portable across filesystems or backends. A nonce has
  to live somewhere checkable from the directory, and that puts it inside the tree, which is option
  B's flaw.
- **D. Treat existing workspaces as created at migration (a grandfather clause).** This was
  `symphony-rs`'s first proposal for migration. It names the safe default directly. It loses because
  "existed before the implementation began writing records" depends on the implementation's own
  upgrade history, which no one outside the implementation can check. So a requirement built on it
  fails the test a guarantee has to pass. A documented migration gives the operator the same answer
  without the spec claiming to know something it cannot.
- **E. Run `before_remove` on a discard.** This is consistent with treating every removal alike.
  It loses on teardown semantics, as argued above.

## Review findings

The proposal was revised on the issue thread before it was accepted, and each revision is recorded
here rather than folded in silently.

- `symphony-rs` found that the first proposal said when the record is written and never when it is
  cleared (the operator-deleted directory above).
- `symphony-rs` found that the record's write was not required to be crash-safe. The proposal
  answered with atomic-or-existence and added the durable-before-first-session rule.
- `symphony-rs` found that the clear before creation was not required to be durable.

These three are one shape. The proposal argued from process death, then twice failed to apply that
argument to the record's own operations: first the write, then the clear, which is the write's
mirror. The second finding was introduced by the repair for the first. A rule that a record survives
a crash has to be checked against every operation on the record, not only the one that motivated it.

## Reconsideration triggers

- A sandbox or executor backend where the party holding the workspace has no durable storage outside
  the sandbox's writable mounts. The record's placement rules would then need restating.
- Evidence that discarding and rebuilding is too costly in practice, for example a very large tree
  whose derivation dominates an attempt. That would argue for re-running `after_create` in place, or
  resuming it, instead of discarding. That option needs a different contract for hook scripts and is
  not taken here.
- A later decision giving the executor a durable state store (compare Section 14.3). The record would
  naturally move there, and the clear rules would become that store's own guarantees.

Relates to 0128 (template rows), 0158 and 0185 (hook execution context and shell), and 0118
(provisioning survivability: a partially written tree MUST NOT be presented as a usable one).
