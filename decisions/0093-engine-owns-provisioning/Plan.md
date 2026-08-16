# Plan — 0093 The engine is the only VCS adapter, and the engine layer is required

## Scope

`VCSX-SPEC.md`: Sections 1.3 "Relationship to Consumers", 2.1 "Goals", 2.2 "Non-Goals", 3.1
"Components", 3.3 "Checkout Modes", 4.1 "Operation Set", 8.1 "Entry Points and Arguments", 8.6
"Invocation Preconditions", 9.1 "VCS Backend Plugin", 9.3 "Capability Descriptors", 11 "Security and
Trust Model", 13.1 "Test Matrix", 13.2 "Implementation Checklist".

`VCSX-CONTRACT.md`: Sections 1 "Status and Deferral Boundary", 2 "Consumption Model", 6 "Engine
Operations and Typed Results", 11 "Deferred to the Full Engine Spec".

`SPEC.md`: Sections 3.4 "Layers, the VCS Engine, and Deployment Topologies", 9.7 "Repository
Provisioning and the VCS Engine", 16.5 "Ensure Repository Object Store", 16.6 "Worker Attempt
(Workspace + Prompt + Agent)", 17 "Test Matrix", 18.1.1 "Both Layer Profiles", 18 "Implementation
Checklist", and Section 14.1's `Repository Provisioning Failures` class.

`conformance/vcsx/vocabulary.json`.

## Tokens introduced

- `provision` — the operation, classified host-side. It has **no lifecycle position** and is outside
  the action-policy machine, per this decision's first review finding; it is also the one entry point
  established without a policy document and without reading a checkout, per the second.
- `store_location` (REQUIRED) and `tree_location` (OPTIONAL) — `provision`'s locations, added by the
  second review finding. `store_location_missing` is the precondition reason for the first's absence.
- Section 4.3 reasons: `provision:ok` (`done`), `provision:unreachable` (`needs_caller`),
  `provision:store_unsupported` (`error`), `provision:failed` (`error`). The universal `failed` and
  `unsupported` reasons apply; `blocked` and `hook_unanswered` do **not**, since they are defined for
  an operation gated at a lifecycle position and `provision` has none.

## Steps

1. **Non-goal reversed (Section 2.2)** — ensure the bullet "Repository provisioning (clone /
   object-store fetch) and credential storage — the consumer's" no longer lists provisioning, and
   retains credential *storage* as a non-goal, since the engine holds credentials only for the
   duration of an invocation (decision 0092). *Done when* Section 2.2 names credential storage alone
   and Section 2.1's goals name obtaining and maintaining a checkout.

2. **Relationship to Consumers (Section 1.3)** — ensure the bullet "performs no repository
   *provisioning*… operates on an already-provisioned worktree; provisioning is the consumer's
   responsibility" is replaced by a statement that the engine obtains and maintains the checkout from
   the consumer-supplied remote, access parameters and credentials, and that the consumer owns the
   agent boundary and the configuration. *Done when* the words "already-provisioned worktree" no
   longer appear in the document.

3. **The provisioning operation (Section 4.1)** — ensure the operation set carries `provision`:
   creating the store where absent, refreshing it where present, and deriving the working tree the
   invocation acts in. Ensure it has a typed result with reasons in the Section 4.3 registry and is
   classified host-side (Section 3.2). Ensure it has **no `before:provision` lifecycle position** and
   that its outcome does **not** re-enter the action-policy machine as an `<op>:<reason>` trigger:
   the policy that would carry such a gate is `repo.policy.toml`, which is inside the repository this
   operation exists to obtain, so the gate would be absent on creation and present on refresh (see
   this decision's review finding). Ensure the section states that the consumer classifies the
   result. *Done when* the operation appears in the required set with its reasons and context, no
   `before:provision` appears anywhere, and the exclusion from the machine is stated with its reason.

4. **Store and trees (Sections 3.3, 4.1)** — ensure the contract states the relationship rather than
   a mechanism: one fetched copy of a repository, and working trees that share it, with the
   realization the backend's. Ensure the statement does not presume git's worktree model, since a jj
   secondary workspace has no colocated git storage (Section 3.3). Ensure a backend that cannot share
   storage declares so through its capability descriptor (Section 9.3) rather than failing at first
   use. *Done when* the store/tree relationship is stated without naming `worktree`.

5. **Creation-time local VCS (Sections 3.3, 8.1)** — ensure the consumer names the local VCS for a
   checkout the engine creates, in the consumer configuration decision 0092 defines, and that
   `detect_mode()` remains authoritative for a checkout the engine did not create. *Done when* both
   paths are stated and neither is a `repo.policy.toml` key.

6. **VCS Backend Plugin (Section 9.1)** — ensure the capabilities realizing the provisioning
   operation are declared, act against the git-access parameter under the git credential (decision
   0091), and are counted with the network-touching set — so decision 0062's invariant reads "the
   capabilities that reach the network are exactly these" with the new members named. *Done when* the
   enumeration in Section 9.1 and the sentence in Section 11 agree on the count.

7. **Security and Trust Model (Section 11)** — ensure the enumeration of what a consumer mediates
   includes the provisioning capabilities, and that the section states provisioning is host-side and
   never reachable from an in-sandbox edge or hook. *Done when* the fixed list a consumer mediates is
   complete under the new operation set.

8. **`SPEC.md` layering (Sections 3.4, 18.1.1)** — ensure the VCS Engine is stated as a REQUIRED layer
   for any topology that obtains or maintains a repository, and that Section 18.1.1's
   enabler-not-enforcer bullet is restated: the Broker Core remains the only *enforced* guarantee and
   remains satisfiable for a single agent session in an existing workspace, while the engine is no
   longer OPTIONAL. Ensure the three topologies still compose as described. *Done when* no sentence in
   either document calls the VCS engine an OPTIONAL layer.

9. **`SPEC.md` provisioning delegates (Sections 9.7, 16.5, 16.6)** — ensure Section 9.7's split no
   longer places provisioning in Broker Core, and that `ensure_object_store` delegates to the engine's
   provisioning operation rather than calling `vcs.clone_object_store` / `vcs.fetch_object_store`.
   Ensure `provision_for_issue` obtains the working tree through the engine. Ensure
   `Repository Provisioning Failures` (Section 14.1) is retained and classified from the engine's
   typed result. *Done when* `grep -n "vcs\.[a-z_]*(" SPEC.md` matches nothing.

10. **`vcs.attempt_clean_backmerge` (Section 16.6)** — ensure the back-merge is written as the engine
    operation it describes, consistent with Section 9.7's "no parallel Symphony VCS/forge adapters for
    those operations". *Done when* the call names the engine and no `vcs.` prefixed function remains
    in Section 16.

11. **`VCSX-CONTRACT.md` surface (Sections 1, 2, 6, 11)** — ensure the operation list carries the
    provisioning operation, and that the consumption model no longer describes the engine as operating
    on a worktree the consumer provisioned. *Done when* the contract's operation set matches
    `VCSX-SPEC.md` Section 4.1.

## Cross-cutting sync

- **`VCSX-SPEC.md` test matrix (Section 13.1)** — provisioning into an empty location yields a usable
  checkout; provisioning where one exists refreshes and does not re-clone; two working trees derived
  from one store see the same objects; a backend declaring shared storage unsupported reports it at
  validation rather than at first use; provisioning is refused from an in-sandbox context.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — add the provisioning operation and the
  store/tree relationship.
- **`SPEC.md` test matrix (Section 17)** and **checklist (Section 18)** — Symphony obtains repositories
  through the engine; a provisioning failure remains repo-scoped and spawns no worker; the agent's
  broker verb set contains no provisioning verb.
- **`SPEC.md` cheat sheet (Section 6.4)** — no new operator key beyond decision 0092's, since
  provisioning consumes the same values.
- **`conformance/vcsx/vocabulary.json`** — add the provisioning operation to `operations` with
  `lifecycle_position: null`, and its reasons to the reason registry with their classes. No
  `before:<op>` position is added, per this decision's first review finding, and no `blocked` or
  `hook_unanswered` entry follows for it.
- **`conformance/vcsx/README.md`** — keep the derived counts honest: the reason table's row and entry
  totals, and the list of results that need fixtures rather than vectors.

## Anchor changes

- `SPEC.md` functions **`vcs.clone_object_store`, `vcs.fetch_object_store` and
  `vcs.attempt_clean_backmerge` are removed**, superseded by engine operations. `ensure_object_store`
  and `provision_for_issue` are retained and delegate.
- `SPEC.md` Section 18.1.1's phrase **"the VCS engine and autonomous daemon are OPTIONAL layers"** is
  removed, superseded by a statement that the engine is required where a repository is managed.
- `VCSX-SPEC.md` gains `provision`'s arguments **`store_location`** and **`tree_location`**
  (Section 8.1) and the precondition reason **`store_location_missing`** (Section 8.6), from this
  decision's second review finding. The capability signatures change with them:
  `ensure_store(remote, local_vcs)` → `ensure_store(store_location, remote, local_vcs)`, and
  `derive_working_tree()` → `derive_working_tree(store_location, tree_location)`.
- `SPEC.md`'s reference algorithm `ensure_object_store` calls `engine.provision` with a store
  location and no tree location; `run_agent_attempt`'s `provision_for_issue` names both.

## Status

Applied to `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `SPEC.md`, `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/README.md`. Step 3 was applied in the amended form recorded in this decision's
first review finding: `provision` has no lifecycle position and is outside the action-policy machine,
so it carries neither `blocked` nor `hook_unanswered`.

The second review finding adds three post-conditions, applied to `VCSX-SPEC.md` Sections 4.1, 6.1,
6.10, 8.1, 8.6, 9.1, 13.1 and 13.2, `SPEC.md` Sections 9.7 and 16.5, and the conformance corpus:

15. **`provision`'s locations (Sections 4.1, 8.1, 9.1)** — ensure `store_location` is a REQUIRED
    argument of `provision` and `tree_location` an OPTIONAL one, that the operation maintains the
    store and derives a working tree only where the invocation names a place for one, and that
    `ensure_store` and `derive_working_tree` take the locations they act on. *Done when* no sentence
    in the document says "the location" without an argument that names it.

16. **`provision` precedes validation (Sections 4.1, 6.1, 6.10)** — ensure the document states that
    `provision` is validated without a policy document, so no reason judged from the document can
    arise for it, and that `capability_unsupported` survives because Section 6.10's third input is
    the consumer's rather than the repository's. *Done when* Section 6.1 says what an absent policy
    means for `provision` and Section 6.10 names the entry point it does not judge from a document.

17. **`provision` reads no checkout (Section 8.6)** — ensure the section establishes for `provision`
    only the preconditions judged from the invocation's arguments, resolving no work branch, detecting
    no mode and accepting no identity. *Done when* the section names `provision`'s precondition set
    explicitly and `checkout_unreadable` is unreachable for it.

Open and deliberately not closed here: `SPEC.md` Section 9.12 still enumerates the machine's
operations as `commit`, `integrate`, `push`, `create_pr` and `merge`. That is arguably correct now
that `provision` is outside the machine, but it is correct by consequence rather than by decision.

Also opened rather than closed: making `provision` the one entry point that runs with no
`repo.policy.toml` discovered states nothing about what any *other* entry point does in that state,
and `VCSX-SPEC.md` Section 6.1 covers only a file that does not parse. Decision 0094 carries that
question, together with the `[base] branch` absence it turns out to share a disposition with.
