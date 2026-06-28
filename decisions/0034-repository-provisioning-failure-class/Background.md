# Background — 0034 Repository provisioning failure class and clone reference algorithm

## Context

Section 9.7 "VCS Adapter and Repository Provisioning" describes the *result* of repository
provisioning — "Symphony keeps one fetched object store per repository on the host", with "Fetch and
other network git operations run on the host with credentials the agent never sees" — and the
credential boundary around it. It does **not** specify what happens when that host-side clone or
fetch fails: there is no failure class for it in Section 14.1, no recovery behavior in Section 14.2,
and no reference algorithm in Section 16 for the credentialed clone/fetch step.

This is an acknowledged asymmetry in the spec. Per-issue worktree provisioning is fully specified —
a reference algorithm (Section 9.2), config (`workspace.root`), lifecycle hooks (Section 9.4), safety
invariants (Section 9.5), and a `Workspace Failures` class (Section 14.1) with recovery behavior
(Section 14.2). The *initial* object-store clone/fetch that those worktrees are cut from has none of
these. Section 16.5 calls `workspace_manager.provision_for_issue(issue)` and handles its failure, but
the object store that `provision_for_issue` depends on is assumed to already exist; the step that
creates it is invisible to the failure model.

Decision 0025 (Proposed) already named this work: it lists "repository provisioning and `git fetch`
(Section 9.7)" among the host-side operations that "run in the orchestrator's own process context",
"outside the sandbox". This decision builds on that finding and addresses a different half of it —
not CPU governance, but error handling and the reference algorithm.

**Layer ownership (the framing this decision fixes).** The initial clone is broker-core / daemon
work, **not** a `vcsx` engine responsibility:

- Decision 0007 states the division of labor directly: "Symphony performs everything touching the
  remote: clone/fetch/branch/back-merge/push/PR." Clone and fetch are Symphony's, listed first.
- Decision 0027 sites the secret store in the broker core ("secret isolation, scope enforcement, the
  per-run socket, and credentialed-operation mediation") and confines the `vcsx` engine to "VCS
  mechanics, the `ship`/`land` orchestrators, and the policy executor" — operations on an
  *already-provisioned* worktree. The engine is never handed an un-cloned repository in any topology;
  in engine-direct topology the operator already has a local checkout.
- Cloning reaches the remote with credentials, which only the secret-holding layer can do. `vcsx` is
  credential-mediated through the broker for push/PR/merge; it has no credential path to clone a repo
  from scratch. So the clone cannot be its job.

An earlier framing held that the clone mechanism was "deferred to the `vcsx` engine contract (0028)".
That is incorrect: 0028 defers only the realization of "the broker's commit/push/pr/merge … through
the engine contract" — clone and fetch are conspicuously absent from that list. The clone is in scope
for Symphony's own `SPEC.md` at the broker-core/daemon layer, not pushed out to the external engine.

A second consequence of correct layering: the object-store clone/fetch is *repo-scoped*, shared
across every issue for that repository. A failure there is not a single worker's problem — it blocks
every dispatch for the affected repository. The existing `Workspace Failures` class is *issue-scoped*
(one worktree, one worker, converted to a backoff retry per Section 14.2). Repository provisioning
needs its own class precisely because its blast radius and its recovery are different.

## Options considered

- **Option A — Status quo; spec silent on provisioning failure.** Section 9.7 keeps describing only
  the success result; clone/fetch failures surface however the implementation chooses, unmodeled.
  Trade-offs: zero change, maximal implementation freedom. But it leaves a real conformance hole: an
  implementer has no normative guidance on classifying or recovering from a failed initial clone, and
  the asymmetry with the fully-specified worktree path is left as a silent trap. The repo-scoped
  blast radius (a bad clone blocks every issue for that repo) is exactly the case most worth
  specifying, and it stays unspecified.

- **Option B — Failure class and recovery only (the error-handling half).** Add a
  `Repository Provisioning Failures` class to Section 14.1 (parallel to `Workspace Failures`) and its
  recovery behavior to Section 14.2 (repo-scoped skip + backoff, distinct from issue-scoped worker
  retry), and a one-line forward reference from Section 9.7. No reference algorithm. Trade-offs:
  closes the conformance hole with the smallest surface; stays at the altitude of the existing
  failure model. But it leaves Section 16 silent on *where* in the flow the clone/fetch is ensured,
  so the relationship between the object store and `provision_for_issue` remains implicit.

- **Option C — Failure class, recovery, and a Section 16 reference algorithm.** Everything in Option
  B, plus a short neutral-pseudocode `ensure_object_store(repo)` reference algorithm in Section 16
  (at the same altitude as the existing `provision_for_issue`), invoked before per-issue worktree
  provisioning, sited explicitly at the broker-core/daemon layer (holds credentials, Section 15.3)
  and explicitly not at `vcsx`. Trade-offs: closes both halves of the gap and makes the
  object-store/worktree dependency ordering explicit and self-checking; mirrors how the worktree path
  is already specified. Larger surface than B, and adds an algorithm where the spec previously relied
  on prose — but Section 16 already carries `provision_for_issue`, so the addition matches existing
  altitude rather than deepening it.

## Decision and reasoning

Accepted; **Option C** is the chosen direction (applied to `SPEC.md`). The clone gap is genuinely unaddressed in the spec
(not merely under-documented), and the two halves are best fixed together: a failure class without an
algorithm leaves the failure unanchored to a point in the flow, while the algorithm without a class
has no taxonomy to return into. Option C mirrors the already-settled worktree path (algorithm + class
+ recovery) and so introduces no new altitude — the worktree precedent is the argument that this is
the spec's own register, not over-specification.

The decision is explicit on layer ownership because that is what the framing got wrong before:
`ensure_object_store` is broker-core/daemon work that uses the secret store (Section 15.3), and is
**not** a `vcsx` responsibility (0007, 0027). Recording this in the decision log prevents the clone
from drifting into the engine contract in a future edit.

Recovery is repo-scoped, not issue-scoped: a clone/fetch failure skips dispatches for the affected
repository and retries on a later tick (like tracker candidate-fetch failures in Section 14.2), keeps
the service alive, and does not convert into a single worker's backoff retry. Whether a persistent
authentication/config failure is parked rather than retried indefinitely is `Implementation-defined`
(the credential may need operator action), mirroring how the token-budget extension parks rather than
backs off.

What would make us reconsider: if the companion `vcsx` spec (0028) turns out to define a host-side,
credentialed provisioning primitive after all, the algorithm's siting note would move to cite it
rather than restate the layer split — but the failure class and recovery stay in Symphony's spec
regardless, because the daemon is the component that observes and recovers from the failure.

This decision relates to 0007 (clone is Symphony's, host-side), 0009 (object store keyed by repo),
0025 (named the host-side provisioning seam), 0027 (broker-core holds credentials; `vcsx` owns
post-provision mechanics), and 0028 (engine contract scope). It depends on 0027 (Accepted).
