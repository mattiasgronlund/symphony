# Background — 0152 What a front-end sequence must reach, not only where it stops

## Context

Issue #111, split from #107 (decision 0143) and independent by design. `VCSX-SPEC.md` Section 13.1's
Front-ends row states four things, and they divide into three kinds:

- an **upper bound** — `ship` stops at the pull request;
- a **guard property** — a tree the guard reads clean enters no `before:commit`;
- two **convergence properties** — each retry re-dispatches, and a tree or head that moves between
  every attempt ends at the flow bound.

**None of them is a lower bound.** Nothing says the sequence must *reach* anything. So a `ship` that
reaches `create_pr` without a push that landed, or reaches `push` without a commit that captured a
dirty tree, falsifies no row in the test matrix — while being exactly the outcome a reader would
expect the matrix to forbid.

The nearest thing to a progress condition is in a different row. Section 13.1's
Operations-and-reasons bullet:

> a `ship` whose `is_dirty()` cannot answer dispatches `commit` and yields `commit:failed` rather than
> pushing an uncommitted worktree (Sections 9.1, 12.2)

That is scoped to the predicate **failing to answer**. It states what the guard does when it cannot
decide, and nothing about what the sequence does when the guard decided fine and the operation the
guard sent it to did not succeed.

## Why this is not a documentation nit

**A wrong reading of Section 12.2 passes the whole matrix.** Decision 0143's reading 2 dispatches
`commit`, has a policy-substituted result satisfy the loop's exit test, and carries on to `push` and
`create_pr` over a tree nothing committed. Check it row by row and every row holds: `is_dirty()`
answered, so the Operations-and-reasons sentence does not apply; `ship` stopped at the pull request,
so the Front-ends bound holds; no retry misbehaved. The document asserts the property only where the
guard is the mechanism, and the state is reached **around** the guard rather than through it.

**The `is_dirty()` sentence makes the omission harder to see, not easier.** It is about the same
hazard — pushing an uncommitted worktree — so a reader looking for the invariant finds a sentence
that reads like it, satisfies themselves, and stops. That is why this survived a review rather than
being caught by one.

**The pseudocode shows it more plainly than the row does**, and this exhibit needs no repository
policy at all. Section 12.2's commit loop ends in a bare `break`:

```text
    c = dispatch(run_op("commit", message))
    if c is commit:worktree_moved:
      continue                              # re-read, re-gate, retry
    break
```

while the push loop below it tests `if r.class != done`. Whatever `dispatch` turns out to mean, the
block as printed walks from **any** non-`worktree_moved` commit result into the push loop. The
invariant this decision states is exactly what makes that `break` sound, and nothing in the document
states it.

**And Section 13.1 is a test matrix.** What it does not state, a conformance suite does not check.
The absence is the difference between an engine that has the invariant and one that happens to.

**The exposure is the whole trigger vocabulary.** Section 6.5 says a repository's `[policy]` edges
override each step of Section 12.2's built-in routing, so the number of ways a policy can move the
sequence is the number of triggers it can bind. An invariant stated over the sequence is the only
thing quantified over all of them; a row per hazard is not.

## Decision: three invariants, stated normatively and mirrored into the matrix

- the `ship` sequence dispatches no `create_pr` step unless a `push` **in the flow** returned a
  `done`-class result;
- it dispatches no `push` step unless a `commit` in the flow returned a `done`-class result, where
  the guard read the working tree dirty;
- the `land` sequence returns a `done`-class result only where a `merge` in the flow reported
  `merge:ok`.

Three corrections to the issue's own phrasing are folded in, and each is load-bearing.

### 1. Section 13.1 alone is not a home

Its lead-in is "A conforming engine SHOULD include tests covering:". An invariant that lives only
there is a **test recommendation with nothing behind it**: an engine that ships the outcome violates
no requirement, and a Conformance Statement's Section 13.1 checkbox is the only place it shows.

Sections 7.1 and 7.2 are the natural home, because they already carry the same shape of guarantee
one operation over — "It commits the tree it read: where the working tree changes between the
`before:commit` position and the capture, nothing is committed …" and "It merges the head it read:
where the pull request's head advances between the read and the merge, nothing is merged …". "It
pushes what it committed" and "it opens a pull request over what it pushed" **complete that
paragraph** rather than starting a new one. Normative there, mirrored into Section 13.1.

### 2. Quantify over the flow, not the invocation

"A `push` in that invocation" is falsified by a conforming resume. Section 13.1's own Front-ends row
has a driver that resolves a need and re-enters "the point that raised it — re-dispatching the
operation whose result escalated", so a `ship` continuing a resolved `create_pr:blocked` dispatches
`create_pr` in an invocation that contains no push. Stated over the invocation, the row would refuse
the resume the row above it requires.

The document already has the quantifier. Section 5.6 bounds "a count of `run_op` dispatches and
resume re-entries" and says what the unit is: a flow "an `escalate` ended and a resume continued is
one flow, and a resumed invocation continues from the count its `resume_token` carries rather than
starting a fresh budget". Using that unit keeps the rows true across the invocation boundary
decision 0153 works in.

### 3. State it over the sequence's step, not over `ship`

Section 6.5 lets a repository's `[policy]` edges override each step, so an edge whose `run_op`
dispatches `create_pr` is the **repository's** dispatch and must not be falsified by this row. The
invariant is about what the built-in sequence does with its own steps; a repository that writes an
edge dispatching `create_pr` after a push that failed has written a strange policy with a
determinate outcome, which is the disposition decision 0143 settles and not a conformance failure. A
row that falsified it would take back what that decision grants.

The third bullet's tightening is worth the change from the issue's "`land` does not report a merge
it did not make": Section 4.3 gives `merge` exactly one `done` reason, so the class test and the
reason test coincide, and no engine has to interpret "a merge it did not make".

## The third invariant, and why it is the row this pair pays for

Section 12.2's built-in sequence already ends `ship` without a pull request on five paths —
`flow_exhausted()` twice, `escalate("resolve_conflicts")` on `integrate:merge_conflicts`,
`escalate("human_review")` on `push:pr_closed`, and `return result_of(r)` where the push's class is
not `done` — and **every one of them is non-`done`**. So `ship` returns a `done`-class result today
**only from `create_pr`**, and `land` only from `merge`, Section 12.3's other exits being
`flow_exhausted()` and a non-`done` await.

That is a real invariant, it is what a caller reads to know the pull request exists, and it is
stated nowhere. It is also exactly what decision 0143's permitted `done`-class early return spends:
`push:pr_closed → run_op status` makes `ship` return `status:ok` — a `done`-class success for an
invocation that pushed nothing and opened no pull request — violating no rule while silently
repurposing the only completion signal the envelope has.

**The replacement test is the operation the result names, not its class.** A `ship` that completed
its sequence reports `create_pr`'s result; a `land` that completed reports `merge`'s. Readable from
the envelope today, no new field. It has to be the operation rather than an `outputs` key, and the
corpus says why: `conformance/vcsx/vocabulary.json`'s `output_keys` group carries the ten keys
Section 8.2 fixes — `unperformed_intents`, `unfinished_hooks`, `unanswered_gates`,
`failed_by_policy`, `forge_budget`, `forge_unavailable_condition`, the three `pr_state_*` keys and
`resume_token` — and notes that "the rest of `outputs` is entry-specific and is not a shared
vocabulary". No pull-request identifier is among them, so one there is a front-end's own key and a
consumer cannot portably test it. (An earlier statement of this on the issue thread, and in decision
0143's first draft, said the group fixes three. It fixes ten; the conclusion turns on the note
rather than on the count, and the count was wrong in both. Corrected here rather than left to be
re-derived.)

**One clause the row should lean on**, because without it the row tells a caller to read a field
whose nullability they then have to go and establish for themselves: the envelope's `op` is present
exactly where a result was decisive and null only where none was — Section 8.4 nulls it for the two
escalation shapes that name no operation. So a caller reading `op` has an answer on every ending a
sequence produced: a completed `ship` names `create_pr`, a truncated one names whatever the edge
dispatched, and the one case with no operation is the case where no step produced the result at all.
This is field-verified against an emitter: `status: ok` with `op: create_pr` is a completed `ship`,
`status: ok` with `op: status` is a truncated one, and `status: needs_caller` with `op: push` is the
built-in escalation.

**The two are about different classes and both hold**, which is worth stating side by side because
read as one thing they look contradictory: the **class** is what the sequence tests of a step's own
result — "a `push` in the flow returned a `done` class" is exactly right — and the **operation** is
what the caller reads off the invocation's result.

## What the rows are for

Under decision 0143's transfer split the first two are **derivable rather than additional**.
`create_pr` is reached only by the push loop's `break`, and the control transfer is selected by the
**sequence's own** `run_op` result, pinned to the root, with every substitution inside the machine
invisible to it — so the only results that reach `break` are `push:ok` and `push:up_to_date`
whatever a repository binds to them. The commit loop is the same shape: `commit:worktree_moved`
keeps its `continue`, so the fall-through to `push` is reachable only from a clean read or a
`commit` result that is neither `worktree_moved` nor flow-ending. `merge:head_moved` likewise keeps
its `continue`, so the built-in re-read-and-retry cannot be disabled by binding it.

That makes them a **regression test on the landing rule** rather than a new constraint on policy,
and it is an argument **for** stating them: a later change to that rule that broke either would be
caught by a row instead of by a wrong write. It is also the answer to a reader who takes them as new
constraints and asks why policy may truncate a sequence but not skip a step — the split already
decides both.

The third is not derivable from anything. It is the invariant the rule deliberately gives up, and
the row is where a caller learns what to read instead.

## Ordering: two decisions, one editing pass

The issue argued this decision should go **before** 0143's, so the landing-rule question would be "a
choice constrained by something written down". That argument was good and its premise is gone: 0143
is captured, both sides accepted the disposition/control-transfer split, and the reading that
violated these rows is what it removes. There is no open choice for the rows to constrain.

What survives is the mechanical half, and it is right: this decision and 0143 edit one anchor set —
Section 12.2's block, Section 12.3's block, Section 13.1's Front-ends row, and now Sections 7.1 and
7.2. Two decisions editing one set in series with a gap between them is where quoted spans go stale.
So: two decisions, **one editing pass**, 0143's record first because it supplies the premise the
derivation rests on, and both plans naming the other.

## Options considered

### Fold these into decision 0143

One decision, one edit, no ordering question. It loses on what the rows are for: 0143's rule fixes
the defect that is here today, and these catch the next one — the next trigger, the next front-end,
the next step a repository can override. Folded in, they read as part of the landing rule's
justification rather than as constraints that survive it being changed, which is precisely the
property that makes them a regression test.

### State them in Section 13.1 only, as the issue asked

The smallest edit, and it puts them where a conformance suite reads them. It loses because Section
13.1's lead-in is a SHOULD over tests: an engine that ships the outcome violates no requirement. The
mirror into Section 13.1 is kept; the home is not.

### A row per hazard rather than an invariant over the sequence

Enumerate the specific wrong writes — no `create_pr` after `push:non_fast_forward`, no `push` after
`commit:worktree_moved`, and so on. It loses on quantification: Section 6.5 lets a repository bind
any trigger, so the number of hazards is the size of the trigger vocabulary, and a row per hazard is
complete only until the next reason token is added.

### Quantify over the invocation

The issue's own phrasing. It loses concretely rather than in principle: a resumed `ship` continuing
a resolved `create_pr:blocked` dispatches `create_pr` in an invocation containing no push, so the
row would refuse the resume Section 13.1's own Front-ends row requires two lines above it.

## What was checked

At `22b5194`, against the working tree:

- Section 13.1's Front-ends row and its Operations-and-reasons `is_dirty()` clause are verbatim as
  quoted; the row's lead-in is "A conforming engine SHOULD include tests covering:".
- Section 12.2's commit loop ends in a bare `break` and its push loop tests `if r.class != done`.
- Section 12.2's exits without a pull request number five — `flow_exhausted()` twice,
  `escalate("resolve_conflicts")`, `escalate("human_review")`, and `return result_of(r)` on a
  non-`done` push — and every one is non-`done`. Section 12.3's other exits are `flow_exhausted()`
  and a non-`done` await.
- Sections 7.1 and 7.2 carry "It commits the tree it read" and "It merges the head it read", each
  with its re-read-and-retry clause.
- Section 5.6 defines the flow across the invocation boundary: "an `escalate` ended and a resume
  continued is one flow".
- Section 4.3 gives `merge` exactly one `done` reason.
- `conformance/vcsx/vocabulary.json`'s `output_keys` group carries **ten** entries, listed above,
  and the note "the rest of `outputs` is entry-specific and is not a shared vocabulary". No
  pull-request identifier is among them.
- `conformance/vcsx/vectors/` carries seven files and none of them is over a sequence — the
  `front_end_sequence` function decision 0143's plan creates does not exist yet.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## On vectors

Both halves go to the `front_end_sequence` file decision 0143's plan creates, rather than to a file
of their own:

- the **negative** — no vector's `expect` names `create_pr` after a push that did not report `done`.
  A negative over the corpus is weaker than a positive vector, which is an argument for the rows
  rather than against them: the rows are what a reader checks an implementation against when the
  corpus has no case in the shape of the bug.
- the **positive** — each `expect` naming what the invocation reports, alongside the disposition
  taken and the control transfer. That pins the completion signal by a case rather than only by the
  absence of one, and a vector naming disposition and transfer but not the reported result cannot
  tell "returns `status:ok`" from "returns the built-in escalation" — the pair this whole thread
  turned on.

## Reconsideration triggers

- **A third front-end sequence.** The invariants are stated over `ship`'s and `land`'s steps; a new
  sequence would need its own progress conditions rather than inheriting these by analogy, and its
  absence of them would be invisible for the same reason this one's was.
- **A `done`-class exit added to a built-in sequence.** The third invariant rests on `ship`
  returning `done` only from `create_pr` and `land` only from `merge`; a built-in path that returned
  `done` from somewhere else would break the caller-facing test rather than the row, which is the
  harder failure to notice.
- **Decision 0143's transfer split being changed.** The first two rows become non-derivable, which
  is the case they exist to catch — but if the split is replaced rather than refined, they should be
  re-read against the replacement rather than assumed to still hold.
- **A shared `outputs` key for a pull-request identifier.** That would make an `outputs` test
  portable, and the "read the operation" clause would then be one of two answers rather than the
  only one.
