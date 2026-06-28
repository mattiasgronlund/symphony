# Plan — 0034 Repository provisioning failure class and clone reference algorithm

## Scope

Implements Option C (see `Background.md`). Affected `SPEC.md` areas, by stable identity:

- Section 9.7 "VCS Adapter and Repository Provisioning" — one forward reference into the failure
  model and the reference algorithm; no change to the existing `vcs` config object.
- Section 14.1 "Failure Classes" — a new class `Repository Provisioning Failures`.
- Section 14.2 "Recovery Behavior" — a repo-scoped recovery entry for provisioning failures.
- Section 16 "Reference Algorithms" — a new `ensure_object_store(repo)` algorithm, referenced from
  the worker flow in Section 16.5 "Worker Attempt (Workspace + Prompt + Agent)".
- Cross-cutting sync: Section 17 (test matrix) and Section 18 (implementation checklist). Section 6.4
  (config cheat sheet) needs no change — no new config key (see Step 6).

This decision is `Proposed`; the `SPEC.md` edits below are the planned end-state, applied when the
decision is Accepted (batched with the companion `vcsx` spec work per 0028 if convenient).

## Steps

1. **Failure class `Repository Provisioning Failures` exists in Section 14.1.** Add a new numbered
   class to the Section 14.1 list, parallel to `Workspace Failures`, with entries covering the
   host-side credentialed clone/fetch:
   - `Object-store clone failure` (initial provisioning of a repository's shared store)
   - `Object-store fetch failure` (refreshing an existing store)
   - `Repository authentication/credential failure` (host-side; resolved through the secret provider,
     Section 15.3 — distinct from the agent's `scope_denied`, which is run-fatal per decision 0007)
   - `Remote unreachable / network transport error`
   - `Invalid object-store path configuration`
   Done-condition: Section 14.1 lists a `Repository Provisioning Failures` class whose entries name
   clone, fetch, auth/credential, transport, and path-config failures, and it is distinct from
   `Workspace Failures` (which stays issue/worktree-scoped).

2. **Recovery behavior for provisioning failures exists in Section 14.2.** Add a bullet describing
   repo-scoped recovery, parallel to the existing `Tracker candidate-fetch failures` entry:
   - Skip new dispatches for the affected repository.
   - Keep the service alive; other repositories are unaffected.
   - Retry on a later tick (do **not** convert to a single-worker backoff retry — the store is shared
     across all of that repository's issues).
   - Persistent authentication/credential or invalid-path failures: whether to park the repository
     rather than retry indefinitely is `Implementation-defined`; implementations MUST document the
     choice (a credential or config fix may require operator action).
   Done-condition: Section 14.2 has a `Repository provisioning failures` recovery bullet that is
   repo-scoped (skip dispatches for that repo, retry next tick, service stays alive) and explicitly
   not converted to per-worker backoff.

3. **`ensure_object_store(repo)` reference algorithm exists in Section 16.** Add a neutral-pseudocode
   algorithm (```text``` block, `snake_case`, same altitude as `provision_for_issue`) that:
   - computes the host-side object-store path (outside the workspace root);
   - on first provisioning, performs the credentialed clone; otherwise fetches to refresh;
   - runs host-side with credentials the agent never sees (Section 15.3);
   - returns a `Repository Provisioning Failures` error (Section 14.1) on failure, so the caller can
     apply repo-scoped recovery (Section 14.2).
   A one-line comment MUST state the layer: this is broker-core/daemon work and is **not** a `vcsx`
   responsibility (decisions 0007, 0027). Candidate shape, for reference (final wording to match
   neighbouring algorithms):

   ```text
   function ensure_object_store(repo):
     # Host-side, credentialed; agent never sees credentials (Section 15.3).
     # Broker-core/daemon responsibility, not vcsx (decisions 0007, 0027).
     store_path = object_store_path(repo)          # outside the workspace root (Section 9.6)
     if not exists(store_path):
       result = vcs.clone_object_store(repo, store_path)
     else:
       result = vcs.fetch_object_store(repo, store_path)
     if result failed:
       return provisioning_error(result)           # Repository Provisioning Failures (Section 14.1)
     return store_path
   ```

   Done-condition: Section 16 contains an `ensure_object_store` algorithm that distinguishes
   initial clone from refresh fetch, is annotated as host-side broker-core/daemon work (not `vcsx`),
   and returns a provisioning error on failure.

4. **Worker/dispatch flow ensures the object store before per-issue worktree provisioning.** Ensure
   the flow makes the dependency explicit: `ensure_object_store(repo)` succeeds (or its repo-scoped
   recovery applies) before `workspace_manager.provision_for_issue(issue)` runs in Section 16.5. The
   natural site is the per-repository dispatch path (Section 16.4 "Dispatch") rather than inside the
   per-issue worker, since the store is shared; if placed at dispatch, a provisioning failure skips
   that repository's dispatches for the tick (Step 2) and no worker is spawned. Done-condition: the
   reference algorithms show `ensure_object_store` running per repository ahead of
   `provision_for_issue`, with provisioning failure routed to repo-scoped recovery, not a worker
   failure.

5. **Section 9.7 forward-references the failure model and algorithm.** In Section 9.7 under
   "Repository provisioning", add a sentence stating that the host-side clone/fetch is owned by
   Symphony (not the agent, not `vcsx`), and that its failures are classified as
   `Repository Provisioning Failures` (Section 14.1) with recovery in Section 14.2 and the reference
   algorithm in Section 16. Done-condition: Section 9.7 points a reader from the provisioning prose to
   the new class, recovery, and algorithm; no new `vcs` config key is introduced.

6. **No new config key.** Confirm the object-store location stays `Implementation-defined` (host-side,
   derived; e.g. a sibling of `workspace.root`), reusing the existing `vcs` object
   (`kind`, `base_branch`, `author`/`actor`, `api_key`) from Section 9.7. Done-condition: no addition
   to the `vcs` config object or to Section 6.4; if an implementation needs a configurable store path,
   that is recorded as `Implementation-defined` with a "MUST document" clause rather than a normative
   key.

## Cross-cutting sync

- **Section 6.4 (config cheat sheet):** no change (no new config key, per Step 6).
- **Section 17 (test matrix):** add rows for the `Repository Provisioning Failures` paths — initial
  clone failure blocks the repository's dispatch for the tick and retries next tick; fetch-refresh
  failure on an existing store; authentication/credential failure handling (`Implementation-defined`
  park vs. retry); and the credential-isolation property (clone runs host-side, agent never sees
  credentials).
- **Section 18 (implementation checklist):** add a line for "ensure the per-repository object store
  (host-side credentialed clone/fetch) before per-issue worktree provisioning, classifying failures
  as `Repository Provisioning Failures`."

## Anchor changes

New anchors introduced (no renames/removals):

- Failure class `Repository Provisioning Failures` (Section 14.1).
- Reference algorithm function `ensure_object_store` (Section 16).

None removed or renamed.

## Status

Applied to `SPEC.md`. All steps implemented: `Repository Provisioning Failures` class (Section 14.1),
repo-scoped recovery (Section 14.2), `ensure_object_store` algorithm (new Section 16.5, with Worker
Attempt and Worker Exit renumbered to 16.6/16.7) wired into `dispatch_issue` (Section 16.4), the
Section 9.7 forward reference, and cross-cutting sync to Sections 17.2, 17.4, and 18.1. No new config
key (object-store path stays `Implementation-defined`).

Deviation from Step 3: the in-spec algorithm comment states the durable property in `SPEC.md`'s own
vocabulary ("Symphony's own provisioning work … never delegated to the agent") rather than naming the
`vcsx`/broker-core layer. `SPEC.md` does not yet carry that vocabulary (decisions 0027/0028 spec edits
are deferred), so naming it would introduce undefined terms. The `vcsx`-vs-broker-core layer nuance
remains in `Background.md`, to be reconciled when the 0027/0028 edits land.
