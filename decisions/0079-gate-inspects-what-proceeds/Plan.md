# Plan — 0079 An operation acts on the state its position inspected

## Scope

`VCSX-SPEC.md`: Sections 4.3 "Reason-Token Registry", 5.6 "Flow Bound and Termination", 6.6
"`[hooks]`", 7.1 "`ship`", 9.1 "VCS Backend Plugin", 10.4 "Content Scanning", 12.2 "`ship` Sequence",
13.1 "Test Matrix", 13.2 "Implementation Checklist".

`conformance/vcsx/vocabulary.json`: one `reasons` entry, `commit:worktree_moved`, class
`needs_caller`.

`conformance/vcsx/README.md`: the new check's absence of a vector, recorded with the deferrals it
belongs to.

No section is added, removed, or renumbered.

One token, no `need` token. Step 5 routes the retry built in, so `commit:worktree_moved` ends an
invocation only where a repository binds it to an edge that does, and that edge names its own
`escalate` reason. Section 8.4's vocabulary is unchanged; Step 8 verifies.

No `VCSX-CONTRACT.md` edit. Section 14 requires shared tokens to be spelled identically; the contract
defers the exhaustive per-operation reason registry (its Section 11) and names no Section 9.1
capability, so neither the token nor the signature is shared surface.

No `SPEC.md` edit. Symphony branches on the engine's classes through the `#class` fallback, and a new
`needs_caller` reason lands on the edge it already has. The obligation option C would have placed on
the consumer — quiescing the writer for the duration of the gate — is not incurred, because the engine
closes the window itself.

Depends on 0078, which lands first: the invariant attaches to a position every dispatch runs.

## Steps

1. **Section 6.6 states the invariant.** Ensure the prose following the hook bullets states that a
   position gates the operation on the state it inspected; that where that state has an identity the
   backend can name, the engine takes the identity when the position completes and the operation acts
   on that state or reports that it could not, naming `expected_head` for `merge` and
   `expected_worktree` for `commit` with their reasons; and that the guarantee is not that the state
   holds still but that a state which moved is reported rather than acted on, the retry re-dispatching
   the operation. Done when the requirement is stated over the positions rather than per position.

2. **Section 6.6 states what the other two positions guarantee.** Ensure the same prose states that
   `before:create_pr` inspects the values the operation writes, nothing recomposing them in between;
   that `before:push` inspects the work branch and the operation sends it as it stands, so a branch
   that gained a commit sends one the position did not inspect — a commit gated at `before:commit`, a
   mechanical merge commit whose content is the resolved base or the branch's own counterpart, or a
   commit from a writer outside the engine, which is the consumer's boundary; and that the window is
   bounded by the position one operation earlier rather than by an identity of its own. Ensure it also
   states why the requirement is stated over the positions: an operation that acted on other state
   returns a `done`-class result for a run nothing gated, which the envelope cannot distinguish from
   one that was. Done when a reader finds the residue argued rather than unmentioned.

3. **`worktree_revision()` names the state without naming a mechanism.** Ensure Section 9.1 carries a
   `worktree_revision()` capability answering an identity for the working tree as `commit` would
   capture it, or that it could not determine one; that the identity MUST differ whenever a `commit`
   would capture different content, distinguishing exactly what `is_dirty()` counts including content
   the VCS has not yet recorded; that its form and derivation are `Implementation-defined` and MUST be
   documented, the specification stating the distinction and leaving the mechanism to the backend as it
   does for `fetch_counterpart` and for the conditioned merge; and that a backend MAY derive the
   identity by writing to its own staging or bookkeeping state, MUST NOT thereby change what a `commit`
   would capture, and MUST document the effect where it writes, because the capability is consulted at
   a position on invocations the gate then blocks. Ensure no claim is made that the value is naturally
   available from a checkout. Done when a backend author reads a required distinction and not a
   required implementation.

4. **`commit` takes the tree it must capture.** Ensure Section 9.1's `commit` bullet reads
   `commit(message, identity, expected_worktree)`; that `expected_worktree` is the identity
   `worktree_revision()` answered when the working tree was read at `before:commit`; that the capability
   MUST NOT create a commit from a working tree whose identity is no longer `expected_worktree` and
   reports `commit:worktree_moved`; and that where `worktree_revision()` could not determine an identity
   there is no `expected_worktree` to supply and the operation reports `commit:failed` rather than
   capturing a tree no position inspected. Done when the commit that succeeds is constrained, not only
   the commit that is refused.

5. **The registry carries the reason and `ship` routes it.** Ensure Section 4.3's table has a `commit` /
   `worktree_moved` row, class `needs_caller`, glossed "The working tree is no longer the one read at
   `before:commit`; re-read then retry", placed after `commit:nothing_to_commit`. Ensure Section 12.2's
   pseudocode wraps the dirtiness guard and the `commit` dispatch in a loop that checks the flow bound
   each turn, continues on `commit:worktree_moved`, and breaks otherwise; and that the prose states the
   loop is Section 12.3's one operation earlier, that routing it built in keeps the token count at one,
   and that a working tree written to between every attempt ends at the flow bound rather than
   committing a tree no position inspected. Ensure Section 7.1 states that `ship` commits the tree it
   read, mirroring Section 7.2's "It merges the head it read". Done when the reason has a token, a
   class, and a built-in recovery.

6. **Section 4.3 states why it is neither neighbour.** Ensure the prose following the table states that
   `commit:worktree_moved` is the `merge:head_moved` / `push:non_fast_forward` condition one operation
   earlier; that it is not `nothing_to_commit`, whose `done` class reports a `commit` owed nothing where
   this one was owed a tree that is no longer there; that it is not the universal `failed`, on the class
   argument the neighbouring paragraph already makes; and that the three together are the registry's
   answer to a state that moved between the read and the write. Done when a reader who finds a near-miss
   reason finds why it is not used.

7. **Section 10.4 closes `before:create_pr` by statement.** Ensure Section 10.4 states that the title
   and body scanned at `before:create_pr` are the values the operation writes, the engine composing
   them once and recomposing nothing in between, so that position needs no identity to condition on
   where the other two do. Done when the position that needs no mechanism says so.

8. **Cross-cutting sync.** Ensure Section 5.6's list of ordinary repeated `(trigger, edge)` pairs names
   `commit:worktree_moved → before:commit → commit` alongside the other two; ensure Section 13.1's
   operations check covers a `commit` whose working tree changed yielding `worktree_moved` rather than
   `ok` or `nothing_to_commit`, and a `worktree_revision()` that could not determine an identity
   yielding `commit:failed`; ensure its front-end check covers `ship` retrying a
   `commit:worktree_moved` and a worktree written to between every attempt ending at the flow bound;
   ensure Section 13.2's checkout-mode bullet names both operations conditioned on the state their
   position inspected; add `commit:worktree_moved` to `conformance/vcsx/vocabulary.json`; and verify
   Section 8.4's `need` vocabulary is unchanged. Done when the matrix, the checklist and the vocabulary
   agree with Sections 6.6 and 9.1.

9. **Conformance corpus note.** Ensure `conformance/vcsx/README.md` records that
   `commit:worktree_moved` has no vector for the reason `merge:head_moved` has none — the check needs a
   live working tree that can change between the position and the operation. Done when the absence is
   recorded rather than silent.

## Cross-cutting sync

- Section 13.1 test matrix — Step 8.
- Section 13.2 implementation checklist — Step 8.
- `conformance/vcsx/vocabulary.json` — Step 8, one entry added.
- `conformance/vcsx/README.md` — Step 9.
- Section 8.4's `need` vocabulary — verified unchanged, Step 8.

## Anchor changes

- **Added:** `worktree_revision` — the Section 9.1 capability answering an identity for the working
  tree as `commit` would capture it.
- **Added:** `expected_worktree` — the `commit` argument carrying that identity, alongside Section
  9.2's existing `expected_head`.
- **Added:** `commit:worktree_moved` — the Section 4.3 reason, class `needs_caller`.
- No anchor is renamed or removed. `commit(message, identity)` gains a third argument and keeps its
  name.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.3, 5.6, 6.6, 7.1, 9.1, 10.4, 12.2, 13.1, 13.2),
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.
