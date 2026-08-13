# Plan — 0083 The push guarantee is quantified over the effect, and a read may write its own bookkeeping

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set", 9.1 "VCS Backend Plugin", 11 "Security and Trust
Model", 13.1 "Test Matrix", 13.2 "Implementation Checklist", 13.3 "Conformance Statement".

No `VCSX-CONTRACT.md` change: the plugin API and the operation semantics beyond the shared names are
deferred to this document (`VCSX-CONTRACT.md` Section 11), and no shared token is renamed.

## Steps

1. **`push(remote, work_branch)` (Section 9.1)** — ensure the capability entry reads that the
   refspec is pinned to the work branch and that the capability MUST NOT cause a push that drops,
   rewrites or re-parents a commit already on the remote work branch. Ensure the phrase "never a
   force push" no longer appears in the entry. *Done when* `grep -n "force push\|force-push"
   VCSX-SPEC.md` returns nothing for Section 9.1 and the effect requirement is stated on the
   capability.

2. **Security and Trust Model (Section 11), the push bullet** — ensure the bullet states that the
   engine pins every push refspec to the derived work branch, so a consumer's scope guard has a
   fixed target, and that no push the engine causes drops, rewrites or re-parents a commit already
   on the remote work branch. Ensure the existing sentences that follow are preserved: no operation
   that updates the work branch rewrites, drops or re-parents a commit already on it, an update that
   reconciles a divergence merges, and a `rebase` or `squash` merge strategy is not an exception
   because it writes to the base branch. Ensure the bullet no longer says "never force-pushes" and
   no longer implies a guard may be written against the presence of a flag. *Done when* Section 11
   states the effect requirement, names the pinned refspec as the guard's fixed target, and contains
   no mechanism claim.

3. **Read-only (Section 4.1)** — ensure the `status` and `diff` entries' "Read-only" is defined
   where the operation set defines its terms: an operation marked read-only writes nothing to the
   history, nothing to the remote, and nothing that changes the content a `commit` would capture.
   Ensure the definition states that a backend MAY write its own bookkeeping state to answer one
   (Section 9.1). *Done when* "Read-only" has a stated quantification in Section 4.1 and
   cross-references Section 9.1.

4. **Section 9.1's capability list** — ensure the bookkeeping allowance is stated **over the list**
   rather than inside `worktree_revision()`: a backend MAY derive any capability's answer by writing
   to its own staging or bookkeeping state, MUST NOT thereby change the content a `commit` would
   capture, and MUST document the effect where it writes (Section 13.3). Ensure
   `worktree_revision()`'s entry keeps the reason its own consultation makes the obligation acute
   (it is consulted at a position on invocations the gate then blocks) without restating the general
   allowance. *Done when* the allowance appears once, applies to every capability in the list, and
   `worktree_revision()` no longer carries the only copy of it.

## Cross-cutting sync

- **Test matrix (Section 13.1)** — under "Plugins" / "Checkout-mode handling": a push that would
  drop, rewrite or re-parent a commit already on the remote work branch is refused whatever the
  transport, including where the local work branch has been moved to an ancestor of the remote's tip
  by a writer outside the engine, and the refusal is `push:non_fast_forward`; a backend that answers
  a read by writing its own bookkeeping state still leaves the history, the remote and the content a
  `commit` would capture unchanged.
- **Implementation checklist (Section 13.2)** — replace "a pinned, never-forced push refspec" with
  the pinned refspec and the effect requirement, so the checklist and Sections 9.1/11 agree.
- **Conformance Statement (Section 13.3)** — extend the resolution that covers
  `worktree_revision()`'s written effect so it covers any capability the backend answers by writing
  bookkeeping state.
- **`conformance/vcsx/vectors/`** — no vector: both boundaries need a checkout and a remote, so they
  are not the deterministic, host-independent subset the corpus carries (Section 13.1).

## Anchor changes

- Section 11's phrase "never force-pushes" and Section 9.1's "never a force push" are **removed** as
  anchors. Any plan or report locating text by them should locate the push effect requirement in
  Sections 9.1 and 11 instead.
- Section 13.2's checklist phrase "a pinned, never-forced push refspec" is **removed**, superseded
  by the pinned refspec plus the effect requirement.

## Status

Applied to `VCSX-SPEC.md`.
