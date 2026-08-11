# Background — 0079 An operation acts on the state its position inspected

## Context

Resolves issue #31, raised alongside issue #29 and deliberately kept out of it: #29 was a Section 4.3
registry claim and this is a Section 6.6 correctness claim, so they are different repairs and one
should not stall the other.

Section 6.6 makes a `before:*` hook a **gate**: it "MAY block by returning a `needs_caller` or `error`
result", and the block surfaces as the gated operation's own reason. A gate is only a gate if what it
inspected is what proceeds. In every position the engine defines, the gate inspects a read and the
operation performs its own afterwards:

| Position | What the gate inspects | What the operation acts on |
|---|---|---|
| `before:commit` | the working tree as `scan-content` read it (Section 10.4) | the working tree as `commit` captures it, "in full: every change the VCS does not ignore" (Section 4.1) |
| `before:push` | the work branch as the repository's own edges read it | the work branch tip as `push` sends it |
| `before:create_pr` | the composed title and body, scanned per Section 10.4 | what `create_or_update_pr` is handed (Section 9.2) |
| `before:merge` | the pull request, transformed by `pr_to_squash` (Section 10.3) | the head `expected_head` pins (Section 9.2) — closed by decision 0077 |

Decision 0077 closed the last row for `merge` alone, and closed it by adding an argument rather than by
stating a rule. That worked because a pull request has a head — a cheap, forge-native identity for "the
thing I inspected".

`before:commit` is the row that matters most, and for the reason Section 3.2 singles the position out:
it is the in-sandbox gate, the one position whose whole job is to inspect content the consumer does not
trust. For Symphony the window is not theoretical — the agent is a live process in that worktree, and
`SPEC.md` places the authoring, the scan and the commit in one session.

## Two corrections to the report's table

**`before:create_pr` is already closed, by construction.** The title and body are values the engine
composes (Section 10.2) and holds; the scan inspects those values and the same values are handed to
`create_or_update_pr`. Nothing re-reads anything. That is worth one sentence in Section 10.4 rather
than a mechanism: it is currently true of every reasonable engine and required of none.

**`before:push`'s window is the branch tip, not the pull-request state.** The report places
`pr_state` at the position, citing decision 0076; 0076 put that read *inside the operation* (Section
4.1). What remains is that the branch can gain a commit between the position and the push.

## Why this is not a shrug

Decision 0076 established the neighbouring rule one layer down (Section 9): a capability MUST NOT
report a condition it could not resolve as an absent answer, because what follows is a benign result
for a run that did nothing. The same argument applies here. A gate that approved state A and an
operation that acted on state B produces a `done`-class result for an operation nothing gated, and
there is nothing in the envelope (Section 8.2) that distinguishes it from one that was gated. The
failure is silent by construction, which is the property that made 0076 worth stating over the whole
list rather than per capability.

A second argument comes from the filing engine and is decisive against merely documenting the window:
**the gate is a hook the engine runs, so the engine cannot know what it inspected.** There is nothing
to compare after the fact. A worktree identity taken at the position is the only thing that can close
this window from inside the engine — which is also why handing the burden to the consumer does not
discharge it.

## One shape ruled out before the options

Letting `commit` write first and scanning the created commit, blocking by discarding it, is not
available: Section 11 states that no operation that updates the work branch rewrites, drops or
re-parents a commit already on it. A gate that has to drop a commit to say no is a gate the security
model forbids.

## What a working-tree identity costs, checked rather than assumed

The first draft of this decision claimed both checkout modes supply the value naturally, on the
grounds that a `jj` working copy is itself a commit. **That is true for `jj` and false for `git`**, and
the correction came from the filing engine. `git write-tree` needs the index to match and excludes
untracked files, while Section 4.1 requires `commit` to capture the tree *in full, including content
the VCS has not yet recorded* — so untracked content must be inside the identity, and there is no
`rev-parse`-shaped answer to reach for.

It can still be closed properly for `git`, and the reason is specific: `commit` in that backend is
`git add -A` then `git commit`, and `git commit` commits **the index**, not the worktree. The index is
therefore the atomicity boundary, and a mechanism falls out — `worktree_revision()` as `git add -A;
git write-tree`, and `commit` re-deriving the same tree and refusing where it differs. A tree object
cannot change afterwards, so it genuinely closes; the cost is one extra `write-tree` over an `add -A`
that already happens.

The price is that this `worktree_revision()` **mutates the index**: a read-shaped capability with a
side effect users see in `git status`, called at a gate on invocations that may then block. The
side-effect-free alternative — a digest over the porcelain status, the tracked diff, and hashes of
untracked files — leaves a narrow window between the digest and the `add -A`.

So `git` has two sub-shapes trading a side effect against closure, and **the specification does not
choose between them.** It states the distinction the value MUST make and leaves the mechanism to the
backend, exactly as decision 0075 stated a required distinction and left `git ls-remote --exit-code`
to the backend, and as 0077 left the conditioned merge to the forge's own parameter. What it does add
is the boundary the sub-shapes must respect: a backend MAY write to its own staging or bookkeeping
state to derive the identity, MUST NOT thereby change what a `commit` would capture, and MUST document
the effect where it writes. Section 9.1 claims nothing about the value being naturally available,
because an implementer who believed that would look for something that is not there.

## Options considered

- **A — state the invariant and close every position that can be closed.** Section 6.6 gains the
  general requirement; `commit` gains `worktree_revision()` and `expected_worktree`; `push` gains an
  `expected_head` of its own, pinning the refspec to the revision the position read rather than only
  to the branch, with a second new reason `push:head_moved`; `create_pr` gains the sentence. Rejected:
  it is the largest permanent surface any of these issues has asked for — Section 8.5 makes every token
  shared surface forever, and decision 0075 refused a single token on a thinner argument than this one
  would have to survive — and the `before:push` residue it buys is the one the argument below already
  bounds.
- **B — state the invariant, close `before:commit`, and argue the residue (chosen).**
- **C — state what a position guarantees and does not, and close nothing.** Section 6.6 says plainly
  that a position inspects a read taken before the operation, that the engine guarantees the two
  coincide only where a capability conditions on an identity the position supplied, and that a consumer
  needing a position to be binding MUST hold the state still. This is Section 11's own stance — "`vcsx`
  enforces no security invariant of its own; it provides the structure a consumer uses to enforce one"
  — and the report allows for it ("possibly an unanswerable one, in which case saying so … is itself
  the fix"). Rejected on the two arguments above: the failure stays invisible in the envelope, which is
  what 0076 refused one layer down; and the burden it hands the consumer is one the consumer cannot
  discharge from inside the engine either, since the engine cannot know what a hook it ran inspected.

## Decision and reasoning

**B.** Section 6.6 states the requirement over the positions: where the inspected state has an identity
the backend can name, the engine takes the identity when the position completes and the operation acts
on that state or reports that it could not. `merge` already realizes it through `expected_head`;
`commit` now realizes it through `worktree_revision()` and `expected_worktree`, reporting the one new
token `commit:worktree_moved`, class `needs_caller`.

**What makes the residue principled rather than unexamined.** Once `before:commit` is binding, every
commit this engine wrote passed the commit gate. A `push` whose tip advanced after `before:push`
therefore sends commits that are individually gated, together with the mechanical merge commits
`integrate` and `pull` write (Section 10.1), whose content is the resolved base and the branch's own
remote counterpart — and base resolution is configuration read from no untrusted content (Section 11).
What is left is a commit from a writer outside the engine entirely, which is the consumer's boundary
rather than the engine's. The window stays open; what can pass through it is bounded by the position
one operation earlier, and the bound is stated rather than assumed.

**Section 12.2 loops, on 0077's argument.** Routed built in, `commit:worktree_moved` never terminates
an invocation, so it needs no `need` token where Section 5.4's `needs_caller` default would have
required one — the same reasoning that kept 0077 at one token. A working tree written to between every
attempt ends at the flow bound, which for a caller still writing in the worktree is the correct report
rather than a failure to converge.

**Where Section 9's answer-domain rule already applies.** `worktree_revision()` is value-answering, so
by Section 9 it MUST be able to report that it could not determine an identity, and that non-answer
maps to `commit:failed` — not to a commit conditioned on nothing. Section 9.1 states it per capability
as that section requires.

Cost recorded: one reason token, one capability, one signature change. That is the same shape 0077
paid for `merge` and half the shape option A would have. Reconsider if `before:push`'s residue is ever
shown to admit content the commit gate did not see — a repository whose work branch gains commits from
outside the engine while the engine is running would be that evidence, and option A is then the
fallback.

Relates to 0077 (whose `expected_head` this generalizes), 0078 (which lands first and gives the
invariant a position on every dispatch path), 0076, 0075, 0063 and 0057.
