# Background — 0073 The network-touching capabilities are named, and base resolution yields a commit

## Context

Resolves issue #22, raised while building `VCSX-SPEC.md` Section 8.6 and Section 6.2 against
`47d9d74d`. The report names three things a VCS backend is required to answer and Section 9.1 — the
document that says what a backend must be able to answer — does not list.

**Two judgements Section 8.6 assigns to the backend.** Section 8.6 fixes an order: validate the policy,
resolve the work branch, accept the commit identity, reporting the first failure. Two of its three
reason tokens describe a judgement no Section 9.1 capability makes. `work_branch_invalid` requires
someone to decide whether a derived name "is not a legal branch name for the VCS backend";
`derive_work_branch(pattern, identity)` derives and does not judge. `identity_invalid` requires someone
to decide whether an identity is "malformed as the VCS backend judges it"; the three capabilities that
take an identity — `commit`, `integrate`, `pull` — are operations Section 8.6 refuses *before*
reaching, and each attributes rather than judges, while `derive_work_branch` takes the identity as a
derivation input (decision 0068) and is not called at all where `branch_pattern` is unset, which is its
default.

The report anticipates the obvious defence — let `derive_work_branch` refuse and judge the identity
wherever the backend is constructed — and refutes it on timing rather than on shape. A backend
constructed with the identity judges it before the engine exists, so there is nothing to report a
Section 8.6 reason to. A `derive_work_branch` that merely refuses produces a refusal with no token, and
the engine would have to recover `work_branch_invalid` from a diagnostic string. Either way the backend
has refused, so Section 8.6 never reaches its own registry, and a precondition step that cannot run is
not a precondition step. That refutation holds and is the reason the answer is a capability rather than
a reading.

**A read with no named copy to consult.** Decision 0062 made the remote repository-owned through an
OPTIONAL `[engine] remote` and supplied it to `integrate`, `push` and `pull`; decision 0064 kept
`ahead_behind(base)` and `diff(base)` non-fetching, comparing "against the checkout's copy of the base".
Each answer is correct. Together they leave a read with no way to know which copy that is: a checkout
carrying two remotes carries two remote-tracking refs for the same base, and a local branch of that name
besides. A repository publishing to a fork would `integrate` the base as `fork` holds it and then report
its `behind` count and its `diff` against whatever the backend picked.

Two things sharpen the report's version of this. It is not only a fork problem — even a single-remote
checkout offers `refs/heads/<base>` and `refs/remotes/<remote>/<base>`, which differ whenever one was
updated after the other, and a workspace provisioned with only the work branch may hold neither.
Section 13.1 already asks for a check that `status` and `diff` "report against the checkout's copy and
acquire nothing", and that check is not writable as a deterministic vector until the copy is named.

And the report's own fallback — "or a sentence saying which copy a read consults" — is not available.
The only non-arbitrary answer is the copy belonging to the resolved remote, and Section 6.2 states that
a backend does not read the remote from the policy itself. A rule the published plugin API cannot
realize is not a rule. The remote had to reach the reads somehow; the only question was the shape.

The common shape of all three is what makes them one issue. Section 9.1 is a closed required list with
an escape hatch — "the minimum every backend MUST provide, not a maximum" — but the hatch is scoped to
capabilities an engine's *own additional operations* need, and it obliges the engine to publish them as
its own (Section 13.3). It is not a hatch for capabilities this specification's own normative text
requires. An engine closing these gaps by itself makes its plugin API wider than the published one,
which is the property a specified plugin API exists to prevent.

## Options considered

- **Option A — widen the list as asked.** Add `accepts_branch_name(name)` and
  `accepts_identity(identity)`, and give `ahead_behind` and `diff` the resolved remote. It is exactly
  what the report proposes and what the filing implementation had already built. Rejected as
  insufficient rather than wrong: passing a `remote` to a capability that acquires nothing falsifies
  decision 0062's invariant while leaving its consequence true, so `remote` would carry two meanings —
  *from where to acquire* and *which local copy to read* — and the one sentence a reviewer applies to
  the next capability would need a caveat holding both. It also leaves the name-to-commit step
  unspecified: each of the three base-taking capabilities would still close it privately, so two of them
  could still disagree inside one invocation, and the fix would depend on every backend resolving the
  same way rather than on the engine resolving once.
- **Option B — a compound base carrying the remote, and one combined precondition check.** Make the
  resolved base `{ branch, remote }` so base-taking signatures keep their arity, and replace the two
  predicates with `check_preconditions(work_branch, identity)` returning the first failure in Section
  8.6's order. Rejected: the compound value narrows the ambiguity without removing it, because the
  backend still performs the name-to-commit step per call; the forge's `create_or_update_pr(head, base,
  …)` takes a base too and a local remote name is meaningless to a forge; and the combined check makes
  Section 8.6's registry the return domain of a plugin capability, so adding a precondition reason later
  becomes a plugin-API change.
- **Option C — narrow Section 8.6 instead of widening Section 9.1.** Specify `derive_work_branch` as
  returning the work branch or refusing with `work_branch_invalid`, and narrow the identity precondition
  to *presence*, which the engine can check while holding identity opaque, letting malformation surface
  as the writing operation's `failed`. Rejected: it reopens decision 0065 one day after acceptance and
  reinstates that decision's own rejected Option B — a malformed identity reported as `commit:failed` is
  `error` class, exit `20`, which invites a retry against a state no retry changes, where exit `2` says
  "the policy did not run; fix the invocation". It also leaves Section 8.6's promise true of two of its
  three rows, and does nothing at all for the base.
- **Option D — resolve the base to a commit.** Base resolution produces a record: the base branch (a
  name, which the forge takes) and a base ref (an opaque handle to a commit, which the VCS takes). One
  new local capability, `resolve_base_ref(remote, branch)`, performs the name-to-commit step once per
  use, and the reads take the handle and no remote at all. Rejected only as a stopping point: it fixes
  the base and leaves `integrate` and `pull` as capabilities that acquire without being named for it, so
  the trust boundary is still read out of an operation's prose.
- **Option D-strong — Option D, and acquisition separates from use** (chosen). `integrate` decomposes
  into `fetch_base(remote, branch)` and `merge_base(base_ref, identity)`, `pull` into
  `fetch_counterpart(remote, work_branch)` and `merge_counterpart(ref, identity)`, and the
  network-touching capabilities become an enumeration of three: `fetch_base`, `fetch_counterpart`,
  `push`.

## Decision and reasoning

Section 9.1's required list gains six capabilities and loses two, Section 6.4 resolves the base to a
record rather than a name, and Section 4.3 gains one reason token, `base_unavailable`, for `integrate`
and for `diff`.

The reasoning worth keeping is the replacement of a proxy with the thing it stood for. Decision 0062
wanted one sentence a reviewer applies to the next capability, and chose an argument-shaped equivalence:
takes a `remote` ⟺ host-side ⟺ needs a credential. Issue #22 is that proxy failing — a read needs to
know *which* remote's copy it compares against while acquiring nothing at all, so the argument and the
credential come apart. **The network-touching capabilities are exactly `fetch_base`,
`fetch_counterpart` and `push`; every other Section 9.1 capability is local to the checkout, whatever
arguments it takes.** That is an enumeration rather than an inference, so no argument list can falsify
it, and it makes Section 3.2's host-side split checkable at the capability boundary instead of read out
of an operation's prose — which is what 0062 was reaching for and could only approximate.

The base change is the root-cause half. Sections 6.4 and 12.4 resolved the base to a branch *name* and
stopped; the step from name to commit happened privately inside `ahead_behind`, inside `diff` and inside
`integrate`, three times in one invocation, with nothing requiring the three to agree. That unspecified
step is the whole of the report's third gap, and naming a remote on the reads would have left it in
place. Resolving to a record — `branch` for the forge, which wants a name; `ref` for the VCS, which
wants a commit — performs the step once, in the engine, through one capability whose job is that step
and nothing else.

Decomposing the two acquiring operations costs two capabilities beyond Option D and buys three things.
It makes the enumeration above exhaustive rather than nearly so. It puts the halves where they belong
for a consumer that sandboxes its caller: the acquiring half is where the credential is, and the merging
half — the one that stops on conflicts and hands the worktree to whoever can resolve them (Section 4.1)
— is demonstrably local, so a mediating consumer could allow it in the sandbox where the resolver
already runs. And it makes a failure the engine can now distinguish reportable: with one call, a fetch
failure and a merge failure were both `integrate:failed` and the backend was the only thing that knew;
with two, the engine knows and Section 4.3 had no way to say so, which is the shape of defect this issue
is itself about.

That is what earns `base_unavailable` its place, and it earns it operationally rather than as
bookkeeping. Section 12.2 routes `push:non_fast_forward` to `integrate` and retries the push; if the
acquisition failed the retry cannot converge, the run burns the flow bound (decision 0060) and reports
`flow_exhausted`, which is decision 0064's own complaint that "the failure got quieter, not louder". A
distinct reason lets a policy escalate a remote it cannot reach instead of looping at it. The token is
one word from `base_unresolved` and means something else, so the difference is stated where both appear:
**unresolved is not knowing which branch; unavailable is not having its commit.**

Splitting `pull` buys only symmetry — nothing reads the counterpart separately, the way the reads need
the base's local half — and it is included anyway, because a naming rule that holds for `integrate` and
not for `pull` is the next report. `pull` gains no reason token: no built-in sequence retries it, so
`pull:failed` remains sufficient, and an absent counterpart stays a benign `pull:ok`, which the work
branch being engine-derived and possibly absent from the remote before the first push (Section 6.2)
makes a normal state rather than a failure.

Three consequences are stated rather than left to inference. A `base_ref` is opaque to the engine, as the
commit identity is (Section 10.1); the engine passes it and does not interpret it. Its validity ends
when an operation moves what it names, so the engine re-resolves rather than reusing a handle across a
`fetch_base` or a `merge_base`. And resolution can answer *absent* — a workspace provisioned with only
the work branch holds no copy of the base — which is a fact the engine can now report: `diff` cannot
produce a delta and is `base_unavailable`, while `status` is an inspection and reports `status:ok` with
null `ahead`/`behind` and a `base_absent` output, because "I cannot see the base" is a fact rather than
a failure.

`merge_base` and `merge_counterpart` are local although they write. That is not a new category:
Section 9.1's local set has always meant a capability that "reads **or writes** the worktree and the
history the checkout already holds", and `commit` is local and writes a commit. Local is about
credentials, not about mutation.

What the change costs is worth recording, because most of it is not transitional. The change impact
itself rounds to nothing — Section 8.5 freezes a surface per `MAJOR` and there is no published `MAJOR`,
no third-party backend and no consumer pin — and it is now-or-never cheap, since the same edit after a
1.0 is a major-version break. Three costs outlive it. Two more required methods than Option D would
have needed, permanently, in the surface hardest to shrink. A fused acquire-and-merge is foreclosed: a
backend whose VCS offers one primitive that does both better than the halves cannot use it, and while
no such primitive exists for git or jj today, the freedom is spent. And an enumeration is a list, which
goes stale when the next capability lands, mitigated by Section 13.3's documentation obligation rather
than eliminated. The handle and its lifetime — the most likely source of the next report — belong to
Option D and would have been paid under either.

What would make us reconsider: a backend whose VCS makes acquire-and-merge genuinely atomic and cheaper
than the pair, which would argue for an OPTIONAL fused capability declared in the descriptor rather than
for recombining the required two; or a consumer that needs the merge half in the sandbox in practice,
which would argue for Section 3.2 labelling capabilities rather than operations — a larger change, and
one that should be taken on its own evidence.

Relates to 0062 (whose invariant this replaces with the enumeration it approximated), 0064 (whose
asymmetry survives — the reads still acquire nothing — and whose "quieter, not louder" failure the new
reason answers), 0058 (whose "every required operation MUST be realizable through the required
capabilities" is what licenses a one-to-many split, as `status`'s six calls already show, and whose own
reconsideration trigger named revisiting a signature rather than the requiredness), 0065 (whose three
precondition rows now each name the capability behind them), 0068 (whose identity reaches
`merge_base` and `merge_counterpart` as it reached `integrate` and `pull`), 0060 and 0061.
