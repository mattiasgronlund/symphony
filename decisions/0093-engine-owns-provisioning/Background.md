# Background — 0093 The engine is the only VCS adapter, and the engine layer is required

## Context

Two components implement version control today, and the seam between them is provisioning.

`VCSX-SPEC.md` Section 1.3 and Section 2.2 place provisioning outside the engine — "Repository
provisioning (clone / object-store fetch) and credential storage — the consumer's" — and `SPEC.md`
Section 9.7 places it inside Broker Core: "It holds the VCS credentials directly and is never a
VCS-engine responsibility; the engine operates on an already-provisioned worktree."

Every VCS-touching call in `SPEC.md`'s reference algorithms:

```
vcs.clone_object_store(repo, store_path)      Section 16.5   initial clone
vcs.fetch_object_store(repo, store_path)      Section 16.5   refresh
workspace_manager.provision_for_issue(issue)  Section 16.6   "VCS worktree or bare dir"
vcs.attempt_clean_backmerge(issue, workspace) Section 16.6   per-issue back-merge
```

**The third call is where the duplication actually bites.** Creating each issue's working tree is
`git worktree add` against `jj workspace add` — VCS-specific work, and the step at which git-or-jj
stops being a choice and becomes a fact. It sits in the `Workspace Manager`, a component with no VCS
backend abstraction, in a service whose Section 9.7 says it has no VCS adapters. Anything that moves
"the clone" without moving this leaves Symphony holding a VCS implementation regardless, and leaves
the checkout mode decided by the component least equipped to decide it.

**The fourth call is a defect, and it is independent of everything else here.**
`attempt_clean_backmerge` is not provisioning — it is the per-issue back-merge, called inside
`run_agent_attempt`. Section 9.7 lists back-merge among the operations "realized through the VCS
engine contract", and states in the same bullet that "there are no parallel Symphony VCS/forge
adapters for those operations". So Section 16.6's `vcs.` prefix on it either means "whatever performs
VCS work", in which case the naming manufactures a Symphony VCS adapter that Section 9.7 denies
exists, or it is a genuine second implementation of an operation the engine already defines. It reads
as the former. Either way, an implementer reading Section 16 builds one Symphony VCS adapter holding
three `vcs.*` calls — the duplication, produced by a naming collision rather than by a design.

**What the duplication costs, after decision 0092.** The operator names the forge kind, the access
parameters, the credential pair and the remote once. Two independent implementations then consume
them: Symphony's, to clone and fetch and cut trees, and the engine's, to push and open pull requests.
Every future backend — a third forge, a native jj remote — must be implemented twice or the two
implementations disagree about what is supported.

**And one named topology cannot start at all.** `SPEC.md` Section 3.4 defines `engine-direct` as "the
VCS Engine alone, run directly by an operator who holds the credentials, with no Broker Core sandbox".
There is no orchestrator, no Symphony adapter, and Section 2.2 forbids the engine from provisioning.
Nothing in either specification gets a human from "no repository" to "a checkout".

## The constraint that shapes the answer

`SPEC.md` Section 18.1.1 lists, among the items **REQUIRED for conformance** of every implementation:

> Enabler-not-enforcer layering (Section 3.4): the Broker Core (secret isolation + scope) is the only
> enforced guarantee and is independently conformant; **the VCS engine and autonomous daemon are
> OPTIONAL layers**; the `daemon`, `interactive-agent`, and `engine-direct` topologies compose them.

The engine's optionality is a normative conformance requirement, not an editorial aside. An engine
that is the only component able to produce a checkout is not optional for anything that manages a
repository, so this decision cannot be made without also deciding that bullet.

## Options considered

- **A — keep Section 2.2 as written.** Steelmanned: it is a deliberate boundary, it keeps the engine
  small and testable, it lets the secret-isolation guarantee be claimed without adopting the workflow
  machinery, and the duplication it costs is bounded — clone, fetch and worktree are the whole of it.
  It loses on the three facts above: the duplication is not bounded once a third backend exists, the
  checkout mode is decided in the wrong component, and `engine-direct` has no path from nothing to a
  checkout.
- **B — an implicit ensure-step in the engine's entry points**, with Symphony continuing to provision
  its own way. Rejected: it *adds* a capability without removing one. Both implementations survive,
  now with two paths that must not race over the same directory, and a silent clone becomes a side
  effect of an entry called `status`.
- **C — an OPTIONAL provisioning operation a consumer may call.** Rejected on the same ground as B,
  with the sharper form: Symphony's adapter disappears only if Symphony chooses to call it, and the
  specification cannot require that choice without re-opening Section 18.1.1 anyway — which is the
  cost this option was chosen to avoid.
- **D — the engine becomes the only VCS adapter (chosen).**

On how the shared object store enters the contract, given D:

- **E — the engine does a plain single checkout only.** Not available: Symphony's model is one fetched
  store per repository with a tree per issue, so an engine that can only make standalone clones does
  not replace `provision_for_issue`, and the duplication survives in the topology that matters most.
- **F — a post-condition, "a usable checkout exists here", mechanism `Implementation-defined`.**
  Steelmanned: it matches how the document already handles checkout-mode detection and discovery
  precedence, and it lets a jj backend share storage in whatever way jj shares storage. It loses
  because a consumer running many issues against one repository is choosing an engine *for* its
  storage behaviour, and under F two conforming engines may differ in disk layout and fetch frequency
  with no way for the consumer to state a requirement.
- **G — the contract names a store and trees derived from it (chosen).**

## Decision and reasoning

**D and G.** Repository provisioning — the initial clone, the refresh, and the derivation of per-issue
working trees from a shared store — moves into the engine, and the engine becomes the only component
that implements version control. Section 2.2's non-goal is reversed rather than narrowed. Symphony's
`clone_object_store`, `fetch_object_store` and the VCS half of `provision_for_issue` are deleted and
delegate. `vcs.attempt_clean_backmerge` is rewritten as the engine call it always described.

**The engine layer stops being OPTIONAL, and Section 18.1.1's bullet is rewritten.** This is the price
and it is a real one: the enabler-not-enforcer framing exists so the secret-isolation guarantee can be
claimed without adopting the workflow machinery, and that claim narrows. What survives is narrower and
still true — Broker Core remains the only *enforced* guarantee, and it remains satisfiable for a
single agent session in a workspace that already exists. What it can no longer do is obtain one.

**The creation-time local-VCS choice lands where the choice is made.** Decision 0092 left detection
authoritative for a checkout the engine did not create, and deferred the creation-time input to this
decision because creation did not exist. It exists now: the consumer names the local VCS in the
consumer configuration 0092 defines, the engine's VCS backend performs the creation, and
`detect_mode()` continues to answer for every checkout the engine did not create. One component owns
both the choice and the detection.

**The store contract must not assume git's model.** A jj secondary workspace is not a git worktree,
and Section 3.3 already admits a jj workspace with no colocated git storage. The contract therefore
names a store and trees derived from it as a *relationship* — one fetched copy of a repository, and
working trees that share it — and leaves each backend to realize it, rather than specifying
`worktree add`. A backend that cannot share storage declares so through its capability descriptor,
which is the mechanism Section 9.3 already provides for a capability a backend cannot perform.

**The engine's identity changes, and the specification should say so rather than drift.** After this
decision and 0092 the engine reads its own configuration, holds credentials for the duration of an
invocation, obtains repositories, and is required. Section 1.3 opens "vcsx is driven by a consumer
that owns credentials… performs no repository provisioning… operates on an already-provisioned
worktree", and Section 2.2 and Section 11 rest on the same framing. These are rewritten, not amended.
Recording it here means a later reader finds a decision rather than an inconsistency.

**The secret-isolation invariant is unaffected.** Provisioning is host-side and credentialed, which is
where it already runs: `SPEC.md` Section 9.7 has the engine run "in the executor's credentialed
context", and Section 3.2 already classifies operations host-side or in-sandbox. A provisioning
operation is host-side, like `push` and `merge`; Section 11's guarantee that an in-sandbox edge never
receives credentials is untouched; and the agent reaches only the broker's verb set, to which no
provisioning verb is added. No new mechanism is needed to keep provisioning out of the sandbox — the
existing classification carries it.

## Reconsideration trigger

Reconsider if a deployment appears that needs Broker Core's secret isolation over repositories it
provisions by some other means entirely — a checkout materialized by an image build, a network mount,
a content-addressed cache — since that is a consumer for which the engine's provisioning is dead
weight and the OPTIONAL layering was written. The repair would then be to restore optionality with
provisioning as an OPTIONAL operation (option C), not to reinstate a second VCS adapter. Reconsider
the store contract if a backend appears whose storage model cannot express "trees derived from one
fetched copy" at all; the fallback is option F's post-condition, and the evidence is a backend
declaring the capability unsupported rather than an argument about disk layout.

Relates to 0092 (whose consumer configuration carries the values provisioning needs, and whose
deferred creation-time local-VCS input this decision supplies), 0091 (whose access parameters and
credential pair are what provisioning consumes), and 0062 (whose remote invariant survives unchanged,
now over a remote the engine itself provisioned from).

## Review finding, 2026-08-14 — `provision` has no lifecycle position, and is outside the machine

Found while applying this decision to `SPEC.md`, before the change was complete. The defect is in
this decision's own pinned token list, not in a document it edits.

**The shape of the defect.** `provision` was given a `before:provision` lifecycle position "like
every operation". A lifecycle position is a gate the **repository's policy** places before an
operation, and the repository's policy is `repo.policy.toml` — a file inside the repository. An
operation whose purpose is to make the repository exist therefore cannot be gated by it: on the
invocation that creates the checkout there is no policy to read, so no edge bound to
`before:provision` can be matched. The position would be present on a refresh and absent on a
creation, which is a position that sometimes exists — exactly the non-determinism Section 5.4's
one-edge-per-trigger rule is written to prevent.

**It is the same cycle this decision's sibling turns on, one level up.** Decision 0092 establishes
that the values needed to obtain a repository cannot be configured inside it. This is that argument
applied to *control flow* rather than to configuration: the policy that would route around a
provisioning outcome is not readable at the moment provisioning must first run. Recording it
strengthens 0092 rather than qualifying it — the cycle reaches further than the configuration keys,
and a reviewer who accepts it for `[engine] forge` has already accepted it here.

**The repair.** `provision` is an operation with a typed result (Section 4.2's envelope, the reasons
this decision registers), invoked by the consumer, and **outside the action-policy machine**: it has
no `before:provision` position, and its outcome does not re-enter the machine as an `<op>:<reason>`
trigger. The consumer classifies the result. This is not a special case carved for one operation but
a consequence of what the machine is: the machine is the repository's Way of Working, and a
repository has no Way of Working until it is present.

Two things corroborate the repair rather than merely permitting it. `SPEC.md` already recovers a
provisioning failure through `Repository Provisioning Failures` (Section 14.1), repo-scoped and ahead
of any worker, rather than through a policy edge — so the consumer-classifies disposition is what
that document already implements. And `SPEC.md` Section 9.12's operation vocabulary enumerates the
positions as `before:commit`, `before:push`, `before:create_pr` and `before:merge`; adding a fifth
would have put a gate in a repository-owned policy that the initial clone cannot consult.

**Blast radius, recorded because the token was propagated before the defect was found.**
`before:provision` reached `VCSX-CONTRACT.md`'s lifecycle-position list, `conformance/vcsx/`'s
`lifecycle_positions` group, and `VCSX-SPEC.md` Section 4.1 — three documents, from one wrong entry
in a shared token list. That is the cost of pinning tokens centrally before the design they encode
has been checked against every document that must carry them; the pinning was still correct, since
four independent spellings would have been worse, but the list should have been derived from the
plans rather than fixed ahead of them.

`Plan.md` step 3 is amended accordingly. The `provision:*` reasons and their proto classes are
unaffected: an operation outside the machine still returns a typed result, and Section 4.2's envelope
is what carries it.

## Review finding, 2026-08-14 — `provision` became an entry point with no invocation to stand on

Found in review of this decision's applied change, on the branch and before merge. Three defects, one
seam: what `provision` is invoked with, and what the engine runs before it.

**The shape of the defect, part one — the pipeline that precedes every operation.** Section 8.1 lists
`provision` among the entry points. Section 8.6 opens "Between validating the policy (Section 6.10)
and running it, the engine establishes the preconditions the invoked entry point depends on", and
neither section was given an exemption. Walk it for the invocation this decision exists to enable —
a `provision` into a location holding no repository:

- Validation takes "the policy document, with `vcsx.toml` merged in" as its first input, and
  Section 6.1 resolves `repo.policy.toml`'s path "relative to the repository root". There is no
  repository root. Section 6.1's only rule for a policy the engine cannot use is one that "does not
  parse"; an absent one has no disposition at all.
- Section 8.6 then "resolves the work branch …, which calls a VCS backend capability —
  `derive_work_branch`, or `current_branch` where no `branch_pattern` is configured".
  `derive_work_branch` needs `scope.branch_pattern` out of the file that does not exist;
  `current_branch()` needs the checkout that does not exist. Section 9.1 states the same thing from
  the other side: the engine consults `detect_mode()` "before the first dispatch, when it resolves
  the work branch".

So the invocation that creates a checkout is refused with `checkout_unreadable` before `ensure_store`
runs. The document relies on exactly this reading elsewhere: the test matrix this decision added
asserts that "a `ship` in a location holding no repository refuses on the checkout rather than
acquiring one as a side effect". That behavior is correct for `ship` and fatal for `provision`, and
nothing distinguishes them.

**This is the third register the cycle reaches, and the third time it was not carried forward.**
Decision 0092 established that the values needed to obtain a repository cannot be configured inside
it. The `before:provision` finding above carried it to *control flow*: the policy that would route
around a provisioning outcome is not readable when provisioning must first run. This carries it to
the *invocation pipeline*: the policy validation and the checkout-reading preconditions that precede
every operation are themselves downstream of the repository, so an operation that obtains the
repository precedes them too. Three recurrences of one argument, each found only after the previous
repair shipped. The pattern worth recording is that the cycle was treated as a fact about
configuration keys and re-derived from scratch at each new register, when it is a fact about
ordering: anything read out of the repository is unavailable to the step that obtains it. Applying
it as a sweep over "what does the engine read before dispatching?" would have found all three at
once.

**Part two — the operation's locations are not arguments.** "The location" is load-bearing in four
places: Section 4.1 ("create the store where the location holds none"), Section 4.3 (what separates
`provision:store_unsupported` from `capability_unsupported` is "what the location already holds"),
Section 9.1, and the Section 13.2 checklist. Section 8.1's argument list names neither a store
location nor a working-tree location, `ensure_store(remote, local_vcs)` takes no location, and
`derive_working_tree()` takes no arguments at all — so neither where the tree is derived nor which
store it derives from is expressible. `SPEC.md`'s reference algorithm had already written the
argument the contract cannot receive: `engine.provision(repo, store_path)`.

**Part three — one operation cannot serve `SPEC.md`'s two phases.** Section 4.1 makes `provision`
`ensure_store` then `derive_working_tree`, always both. `SPEC.md` calls it twice for different work:
`ensure_object_store` wants the store alone, once per repository, and `provision_for_issue` wants a
tree, once per issue. Under one indivisible operation the per-repository call derives a working tree
nothing named and nothing uses, which is a directory appearing on the host for no reason a consumer
asked for.

**The repair.** `store_location` is a REQUIRED argument of `provision` and `tree_location` is an
OPTIONAL one; the operation maintains the store and derives a working tree where the invocation
names a place to derive one. That supplies the missing locations, makes the store-only phase
expressible, and leaves the capability signatures able to carry what they act on. `provision` is then
stated as **the one entry point established without a policy document and without reading a
checkout**: no policy is validated for it, so no reason judged from the document — `malformed_policy`
through `version_floor_unmet` — can arise; and the preconditions established are exactly those judged
from the invocation's arguments, so no work branch is resolved, no mode detected, and no identity
accepted. `capability_unsupported` survives both cuts, because Section 6.10's third input is the
consumer's configuration rather than the repository's — which is the input decision 0092 added, and
is what makes the shared-store refusal "before anything is fetched" reachable for the one operation
that fetches.

The cost is stated rather than absorbed. A below-`version_floor` engine provisions successfully and
refuses on the next invocation, because the floor is declared in the file provisioning obtains; that
is the cycle again and not a gap in the repair. And `SPEC.md`'s per-issue invocation names both
locations, so it refreshes a store the tick's earlier call already refreshed — idempotent by the
property Section 13.1 already tests ("refreshes it and fetches no second copy"), and a redundant
acquisition rather than a wrong one. Making it avoidable would need a tree-only third phase, which
buys one saved fetch per issue at the price of an operation whose name would have to promise the
store is already current — a precondition on a location, which is the one thing Section 4.3 says the
descriptor cannot settle.

**The option not taken: split `provision` into two operations.** A `provision_store` and a
`provision_tree` would carry their own locations naturally, make the two phases explicit, and remove
the optional-argument-changes-the-work shape, which is a real smell. It loses on the contract: the
operation set is shared surface (`VCSX-CONTRACT.md` Section 6, `conformance/vcsx/vocabulary.json`),
and two operations need two reason sets where the failures are identical — `unreachable` belongs to
the store half and `store_unsupported` to the tree half, but `failed` and `unsupported` are universal
and would double. One operation whose arguments say how far to go keeps one reason registry over one
name, and the consumer that wants only the store omits an argument rather than learning a second
verb.

Reconsider the split if a third phase appears — a consumer that needs to derive a tree while
guaranteeing no acquisition, for example under a network the invocation must not touch. The evidence
is a consumer asking for provisioning with the network denied, and the repair is then two operations,
not an argument that means "skip the half you would otherwise do".

**Blast radius.** The missing exemption reached `VCSX-SPEC.md` Sections 6.1, 6.10 and 8.6; the
missing locations reached Sections 4.1, 4.3, 8.1, 9.1 and 13.2 and `SPEC.md` Section 16.5. Two new
precondition reasons follow, `store_location_missing` and `local_vcs_missing` (the latter from
decision 0092's finding), and both land in `conformance/vcsx/vocabulary.json` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
