# Plan — 0073 The network-touching capabilities are named, and base resolution yields a commit

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set", 4.3 "Reason-Token Registry", 6.2 "`[engine]`", 6.4
"`[base]` and Base Resolution", 8.6 "Invocation Preconditions", 9.1 "VCS Backend Plugin", 11 "Security
and Trust Model", 12.4 "Resolve Base", 13.1 "Test Matrix", and 13.2 "Implementation Checklist".

`conformance/vcsx/vocabulary.json` gains the new reason entries; `conformance/vcsx/README.md` records
why the new behavior has no vectors yet.

No section is added, removed, or renumbered: every change lands inside an existing subsection, so no
cross-reference in either engine document moves.

No `VCSX-CONTRACT.md` edit. Section 14 requires every *shared* token to be spelled identically, and the
contract surface names no Section 9.1 capability, no `[engine] remote`, and no base-resolution shape —
the plugin API is entirely on the deferred side. The one token it could have shared is
`base_unavailable`, and the contract enumerates no per-operation reason.

No `SPEC.md` edit. Symphony references the engine's operations, triggers, classes and reason vocabulary,
not its plugin API; `base_unavailable` reaches Symphony only as another `error`-class `integrate:*` or
`diff:*` result, which its `#class` fallback already absorbs.

No `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit beyond verification. Section 13.3 already obliges an
engine to record the capability descriptors its plugins advertise and the capabilities any operation
beyond Section 4.1 requires; the required list growing does not change what is recorded. Step 14
verifies rather than assumes this.

## Steps

1. **`status` reports a base it cannot see.** Ensure Section 4.1's `status` bullet states that
   `ahead`/`behind` are reported against the resolved base and are null, with a `base_absent` output,
   where the checkout holds no copy of it (Section 6.4). Ensure `status` gains no reason token: it
   remains `status:ok`. Done when a `status` in a workspace provisioned with only the work branch has a
   stated outcome instead of an assumed one.

2. **The read-side Note names the resolved base ref.** Ensure Section 4.1's Note — the one beginning
   "the operations that reach the remote are exactly those Section 3.2 places host-side" — states that
   `status` and `diff` report against the base ref the checkout already holds (Section 6.4), rather than
   against "the base as the checkout already holds it". Ensure the rest of the Note is unchanged: the
   staleness admission, the trust-split reasoning, and "A caller that needs current figures runs
   `integrate` first". Done when the Note no longer names a copy the specification does not identify.

3. **`base_unavailable` is in the registry twice.** Ensure Section 4.3's table carries
   `integrate` / `base_unavailable` / `error` — the base could not be acquired from the remote
   (Section 9.1 `fetch_base`) — and `diff` / `base_unavailable` / `error` — the checkout holds no copy of
   the resolved base (Section 6.4). Ensure the row for `integrate` / `base_unresolved` is unchanged and
   that the two are distinguished in prose: unresolved is not knowing which branch (Section 6.4);
   unavailable is not having its commit. Done when a reader cannot mistake one for the other, and when
   `diff` has an `error`-class reason that is not `failed`.

4. **Base resolution produces a record.** Ensure Section 6.4 states that resolving the base produces
   two values: the base **branch**, a name, which the pull-request operations take (Section 9.2); and
   the base **ref**, an opaque backend-supplied handle to the commit the checkout holds for that branch,
   which the version-control capabilities take (Section 9.1 `resolve_base_ref`). Ensure it states that
   the engine holds the ref opaque as it holds the commit identity opaque (Section 10.1), that a ref's
   validity ends when an operation moves what it names — so the engine re-resolves rather than reusing
   one across a `fetch_base` or a `merge_base` — and that resolution MAY answer that the checkout holds
   no copy, which Sections 4.1 and 4.3 report. Ensure the existing `branch`, `resolve`, `prefixes` and
   "Base resolution is configuration, not a hook" material is unchanged. Done when the step from a base
   name to a base commit is in the document rather than in each backend.

5. **The reference algorithm returns the record.** Ensure Section 12.4's `resolve_base` pseudocode —
   which keeps its name, and is the engine's algorithm rather than the capability — takes the resolved
   remote, returns the record of Step 4, and reaches the ref through the `resolve_base_ref` capability.
   Ensure the `fixed` / `by_prefix` selection and the `base_unresolved` error are otherwise unchanged.
   Done when the algorithm's return value and Section 9.1's capability arguments agree.

6. **Section 8.6 names the capability behind each row.** Ensure Section 8.6 states the order it already
   fixes — resolve the work branch, judge the derived name, accept the commit identity — and names the
   capability that answers each: `derive_work_branch`, or `current_branch` where no `branch_pattern` is
   configured; `accepts_branch_name`; `accepts_identity` (Section 9.1). Ensure the existing framing is
   unchanged: a precondition failure is not an operation result, the run is refused with
   `usage_or_config` and null `op`/`class`, the three reason tokens keep their spellings and conditions,
   and an engine MUST NOT report a precondition reason for a condition an operation could have reported.
   Done when Section 8.6's order is realizable from the published plugin API without inference.

7. **`current_branch()` answers an optional branch.** Ensure Section 9.1 states that `current_branch()`
   answers the checkout's current branch or none, so a detached checkout is a state the engine reports
   (Section 8.6 `no_current_branch`) rather than a backend failure. Done when the condition
   `no_current_branch` describes has a stated return value behind it.

8. **The two judgement capabilities are required.** Ensure Section 9.1's required list carries
   `accepts_branch_name(name)` — whether the name is a legal branch name for the backend — and
   `accepts_identity(identity)` — whether the commit identity is well formed as the backend judges it
   (Section 10.1). Ensure both are stated as questions with no side effect, answered before any
   operation is dispatched (Section 8.6). Done when neither of Section 8.6's judgements requires a
   capability beyond the published list.

9. **The base-taking capabilities take the ref.** Ensure Section 9.1 carries
   `resolve_base_ref(remote, branch)` → the base ref, or none where the checkout holds no copy;
   `ahead_behind(base_ref)`; and `diff(base_ref)` → `diff:*`. Ensure none of the three is described as
   acquiring anything, and that `ahead_behind` and `diff` take no `remote`. Done when a read names one
   commit rather than choosing among the checkout's copies.

10. **Acquisition separates from use.** Ensure Section 9.1 replaces `integrate(remote, base, identity)`
    with `fetch_base(remote, branch)` → the base ref, acquiring the base as `remote` holds it
    (Section 4.1), and `merge_base(base_ref, identity)` → `integrate:*`, merging it into the work branch
    and preserving recorded conflict resolutions where supported. Ensure it replaces `pull(remote,
    work_branch, identity)` with `fetch_counterpart(remote, work_branch)` → the counterpart ref, or none
    where the remote carries no counterpart, and `merge_counterpart(ref, identity)` → `pull:*`, merging
    it in and rewriting none of the branch's commits (Section 4.1). Ensure `push(remote, work_branch)`
    is unchanged, refspec pinned and never forced. Done when the operations `integrate` and `pull` are
    unchanged in Section 4.1 while each is realized through one acquiring capability and one local one.

11. **The invariant is an enumeration.** Ensure Section 9.1 states that the network-touching
    capabilities are exactly `fetch_base`, `fetch_counterpart` and `push` — they acquire over the
    network or write to it, need a credential, and realize the version-control operations Section 3.2
    places host-side — and that every other capability in the list is local to the checkout, reading or
    writing the worktree and the history the checkout already holds, whatever arguments it takes.
    Ensure it states that `merge_base`, `merge_counterpart` and `commit` are local although they write,
    because the distinction is credentials rather than mutation. Ensure the replaced sentence — "the
    three capabilities that take one are exactly the version-control operations Section 3.2 places
    host-side" — is gone, since `resolve_base_ref` takes a `remote` and acquires nothing. Done when the
    trust boundary is read off the list rather than inferred from an argument.

12. **The identity paragraph follows the split.** Ensure Section 9.1's identity paragraph names
    `commit`, `merge_base` and `merge_counterpart` as the capabilities that take a commit identity —
    exactly those that can write a commit — so a mechanical merge commit is attributed no differently
    from one `commit` writes (Section 10.1, decision 0068). Ensure `derive_work_branch(pattern,
    identity)` keeps its stated role as a derivation input rather than an attribution. Done when
    decision 0068's invariant survives the rename of the capabilities it was written about.

13. **The descriptor field follows the merging half.** Ensure Section 9.1's descriptor-fields sentence
    states that recorded-resolution reuse is a property of `merge_base`. Ensure the other fields —
    supported modes, and operating in a workspace with no colocated remote — are unchanged. Done when
    the descriptor names a capability that exists.

14. **Section 13.3 still covers the list.** Verify that Section 13.3's capability bullet — the
    descriptors a plugin advertises, and the capabilities any operation beyond Section 4.1 requires —
    reads correctly with a longer required list, and that `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s
    corresponding section needs no change. Done when an engine filling the template records the same
    things it did before, and the verification is recorded here rather than assumed.

15. **The trust model names the credentialed surface.** Ensure Section 11 states that the capabilities
    that touch the network are named and enumerable (Section 9.1), so a consumer mediating credentialed
    access has a fixed list rather than an inferred one. Ensure the existing bullets — no long-lived
    credentials, context labelling, the pinned and never-forced refspec, the history-preserving update,
    no provisioning — are unchanged. Done when the trust model's claim about what a consumer can mediate
    matches what Section 9.1 now makes checkable.

16. **The test matrix covers the four new behaviors.** Ensure Section 13.1's `Operations and reasons`
    check states that a read reports against the base ref resolved for the configured remote, so a
    checkout carrying more than one remote yields one answer; and that an `integrate` whose acquisition
    fails yields `base_unavailable` rather than looping to the flow bound. Ensure its `Invocation
    contract` check names `accepts_branch_name` and `accepts_identity` as the judgements behind
    `work_branch_invalid` and `identity_invalid`. Ensure its `Plugins` check states that the
    network-touching capabilities are exactly `fetch_base`, `fetch_counterpart` and `push`, and that a
    `status` in a checkout holding no copy of the base is `status:ok` with null `ahead`/`behind`. Done
    when each behavior this decision adds is a testable line.

17. **The checklist names the split.** Ensure Section 13.2's plugin bullet states that the VCS backend
    separates acquisition from use, and its base bullet — or the loader bullet that names base
    resolution — states that resolution yields a base ref. Done when the definition of done includes
    both halves of this decision.

18. **The vocabulary registry carries the reasons.** Ensure `conformance/vcsx/vocabulary.json`'s
    `reasons` group gains `integrate:base_unavailable` and `diff:base_unavailable`, both `error` class,
    in the shape its existing entries use. Done when the registry and Section 4.3's table hold the same
    set.

19. **The corpus records why it has no vectors.** Ensure `conformance/vcsx/README.md` records that the
    capability split and base-ref resolution have no vectors: both are judged against a real checkout
    with a real remote, which no vector file supplies, and both belong with the plugin behavior the
    corpus already defers. Done when the absence is stated rather than inferred.

20. **`[engine] remote` says what it does for a read.** Ensure Section 6.2's `remote` bullet states
    that the remote also names which of the checkout's copies of the base a read resolves against, and
    that resolving acquires nothing (Section 6.4). Ensure the rest of Section 6.2 — the default, the
    repository-ownership reasoning, the once-per-invocation resolution, and a name the checkout does
    not carry surfacing as the operation's `failed` reason — is unchanged. Done when the answer to
    "which copy" is reachable from the key that raised the question.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 18) and `conformance/vcsx/README.md` (Step 19).

Section 3.2 needs no edit: it labels *operations*, and the operation set is unchanged — `integrate`,
`push` and `pull` remain host-side. Whether Section 3.2 should label capabilities instead is the
reconsideration `Background.md` records; it is a larger change and is deliberately not taken here.

Section 6.2 keeps its substance: the remote is still repository-owned, still resolved once per
invocation, still supplied by the engine rather than read from the policy by a backend, and Section 9.1
rather than Section 6.2 enumerates the capabilities it reaches. One clause is added, as Step 20, so a
reader who goes to Section 6.2 to learn what the remote is for finds the read-side answer there.

Section 8.5 needs no edit: a new operation reason in a compatible release is already provided for, and
no invocation status, exit code or class changes.

Section 9.3 needs no edit: the rule that the executor reads a descriptor before invoking a capability
and MUST NOT invoke an undeclared one is unchanged, and the capabilities added here are required rather
than declared-optional.

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` are untouched; this decision changes
`VCSX-SPEC.md`, whose counterparts are Sections 13.1 and 13.2, handled in Steps 16 and 17.

## Anchor changes

Removed capabilities: `integrate(remote, base, identity)` → superseded by `fetch_base(remote, branch)`
and `merge_base(base_ref, identity)`; `pull(remote, work_branch, identity)` → superseded by
`fetch_counterpart(remote, work_branch)` and `merge_counterpart(ref, identity)`.

Changed signatures: `ahead_behind(base)` → `ahead_behind(base_ref)`; `diff(base)` → `diff(base_ref)`.

Added capabilities: `accepts_branch_name(name)`, `accepts_identity(identity)`, `resolve_base_ref(remote,
branch)`, `fetch_base(remote, branch)`, `merge_base(base_ref, identity)`,
`fetch_counterpart(remote, work_branch)`, `merge_counterpart(ref, identity)`.

Added reason token: `base_unavailable`, defined for `integrate` and for `diff`.

Added output: `base_absent` on `status`.

The **operations** `integrate` and `pull` keep their spellings, their reason tokens and their lifecycle
positions; only the capabilities realizing them are renamed. `commit`, `push`, `detect_mode`,
`current_branch`, `is_dirty`, `is_conflicted` and `derive_work_branch` are unchanged.

## Out of scope

- **Section 3.2 labelling capabilities rather than operations.** It is what would let a consumer allow
  `merge_base` in a sandbox while keeping `fetch_base` host-side. Recorded in `Background.md` as a
  reconsideration trigger; it should be taken on its own evidence.
- **A `pull:up_to_date` reason.** `integrate` and `push` each have one and `pull` does not, so an absent
  counterpart and an already-current branch both land on `pull:ok`. The asymmetry predates this
  decision and a `done` class already tells a policy what it needs.
- **An OPTIONAL fused acquire-and-merge capability.** The reconsideration trigger for a backend whose
  VCS makes the pair genuinely atomic; it would be declared in the descriptor rather than replace the
  required two.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 6.2, 6.4, 8.6, 9.1, 11, 12.4, 13.1, 13.2),
`conformance/vcsx/vocabulary.json`, and `conformance/vcsx/README.md`.
