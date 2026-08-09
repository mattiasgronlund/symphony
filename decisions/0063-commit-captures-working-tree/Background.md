# Background — 0063 `commit` captures the working tree, and `is_dirty()` is its predicate

## Context

Resolves part 2 of issue #9, raised while building the first real `VCSX-SPEC.md` Section 9.1 VCS
backend (`vcsx-plugin-git`, against `06a3bc19`).

`VCSX-SPEC.md` Section 4.1 defines `commit` as "create a commit from the working tree" and offers no
`stage` operation a driver could call first. Section 12.2 then guards the operation:

```text
  run_lifecycle("before:commit")
  if worktree_dirty():
    dispatch(run_op("commit", message))
```

Two things went unstated. Whether `commit` is itself responsible for putting working-tree content into
the commit, and whether content the VCS has never recorded counts toward `worktree_dirty()` — the same
question asked of `is_dirty()`, the Section 9.1 capability the guard is realized by.

The phrasing already points one way: "from the working tree" is not "from the index", and the engine
defines no operation that would populate an index. But the issue is right that pointing is not enough
here, because the failure is silent and asymmetric. An engine that read "from the working tree" as
"from whatever was selected out of band" would conform to the letter, and an agent whose entire change
is new files would then be reported clean, skip the commit, and ship an empty branch — with `ship`
returning `create_pr:created`, every step `done`-class, and nothing in the result envelope indicating
that the work was lost. The reverse mistake is loud: a commit that captured too much fails review.

The filing implementation's meanwhile-answer is yes to both: `commit` stages everything the VCS does not
ignore, and `is_dirty` reports untracked files as dirty.

## Options considered

- **Option A — `commit` captures the working tree in full, and `is_dirty()` is true exactly when a
  `commit` would capture something** (chosen). It states what the phrasing implies and ties the guard
  to the operation with one predicate. Trade-offs: it fixes a policy the specification could have left
  to the repository, and it forecloses a partial-commit workflow that no part of the current schema can
  express anyway.
- **Option B — `commit` captures only content selected out of band, and Section 4.1 gains a `stage`
  operation** (rejected). It would model a two-step workflow faithfully, and it is what a backend
  author transcribing a VCS's own verbs might reach for. But it adds an operation and a `before:stage`
  lifecycle position to the required set for a workflow the engine has no way to drive: nothing in
  Section 4.1's operations or Section 5.2's actions could decide *what* to select, so the argument would
  have to come from the caller — and Section 6.3's refusal to accept a caller-named branch is the same
  document declining that shape for the same reason. It also inverts the failure: the default becomes
  an empty commit.
- **Option C — leave it, since "from the working tree" already points that way** (rejected). It is the
  cheapest option and the reading is probably what every implementer would take. It is refused because
  Section 12.2 makes the predicate load-bearing: the guard decides whether the commit runs at all, so a
  disagreement between the guard and the operation is not a difference in what gets committed but the
  difference between committing and not. A reading that is merely probable is not enough for a branch
  that silently ships nothing.
- **Option D — make it `Implementation-defined`** (rejected). Two conforming engines would then produce
  different commits from the same worktree, and `commit:nothing_to_commit` would mean something
  different on each. The reason registry's value is that a token means the same thing everywhere
  (Section 4.3); a reason whose truth condition varies by engine is the one thing it cannot afford.

## Decision and reasoning

`commit` captures the working tree in full: every change the VCS does not ignore, including content the
VCS has not yet recorded. The engine defines no staging operation and no way to commit a subset, so
nothing selects the commit's content out of band. `is_dirty()` is `commit`'s own predicate: it reports
the working tree dirty exactly when a `commit` would capture something.

The reasoning worth keeping is the second half, not the first. That `commit` commits the working tree is
a policy choice, and a defensible one either way in isolation. That **the guard and the operation share
one predicate** is not a choice — it is what makes Section 12.2's `if worktree_dirty()` a correct guard
rather than an independent opinion about the same worktree. State them separately and any drift between
them turns into skipped work; state them as one predicate and the skip is provably benign, because the
only tree the guard declines to commit is one a commit would have found empty.

Framing it that way also decides the ignored-content question without a second rule. Ignored content
does not count as dirty because a commit would not capture it, not because a separate clause says so —
and if a repository changed what its VCS ignores, both halves move together.

`commit:nothing_to_commit` keeps its `done` class and needs no change. It is the honest answer for a
worktree that really has nothing, and under this predicate it is now the only way the flow reaches a
commit with nothing to do: `ship` skips the operation when `is_dirty()` is false, and a driver calling
`commit` directly gets the no-op.

Two things this deliberately does not do. It does not say the commit's *message* comes from anywhere new
— Section 10.1 already makes it the caller's, validated at `before:commit` — and it does not touch
Section 10.4's scan, which inspects "a commit diff" and now demonstrably sees new files, which is the
behavior a content scan would want anyway.

What would make us reconsider: a consumer that legitimately needs to commit a subset of a worktree — a
partial-commit review flow, say. That would need `commit` to take a selection argument, and the
selection would have to come from somewhere the engine trusts, which is the question Section 6.3 answers
"not the caller" for branches. It is a larger change than relaxing this predicate.

Relates to 0057 (whose universal `commit:failed` covers a backend that cannot capture the tree) and
0061 (the sibling case where a `pull:conflict` is finalized by `commit`, which now demonstrably captures
the resolved tree including any file the resolution added).
