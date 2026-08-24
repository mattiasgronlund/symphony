# Background — 0143 Where a substituted result lands in a front-end sequence

## Context

Issue #107, split out of issue #103's implementation response and separable from it: no resume is
involved and the defect is reachable today. Sections 12.2 and 12.3 write the front-end sequences as
pseudocode that tests each operation's result itself, and Section 5.4 says a result a `run_op` edge
disposed of is replaced by that edge's own result — "in the machine". Neither section says what the
**sequence** is handed when a repository's `[policy]` bound an edge to a result the sequence also
tests. Section 7.1 says the machine governs the sequence ("Each step passes through its lifecycle
position and its result re-enters the machine, so repository policy governs the sequence") without
saying what the sequence receives back.

The collision is with the specification's own example. Section 6.5 prints:

```toml
[[policy.edge]]
on = "push:non_fast_forward"
do = "run_op"
op = "integrate"
```

and `conformance/vcsx/vectors/match-edge.json`'s first vector is built on that same edge.

## The reading is one, not three — and it is wrong

The report offered three readings. Two are refused by prose that sits nowhere near the pseudocode,
and the narrowing makes the finding sharper rather than milder:

- **Both fire** — the sequence sees the operation's own result *and* the edge fires — is refused by
  the sentence under Section 12.2's block: a repository's `[policy]` edges "override each step",
  which is not "run alongside".
- **No edge fires under a sequence** is refused by Section 12.3's own prose: "Because the routing is
  built in, `merge:head_moved` reaches a caller through this sequence only where a repository binds
  it to an edge that ends the flow." That sentence presupposes a repository edge on
  `merge:head_moved` firing under `land` and taking effect. Under this reading no repository edge
  fires under a sequence at all, so `merge:head_moved` would reach a caller by no route whatever and
  the sentence would be false rather than narrow. One counterexample kills a global reading, so it
  settles the commit and push loops too.

What is left is **the sequence sees the disposed result** — and an implementer who reasons correctly
from the text arrives there and writes a wrong write. This is not an under-determination resolved by
a coin flip; it is a resolution the text supports.

## The two wrong writes

**Push loop.** `integrate:ok` takes the push outcome's place. It is not `push:non_fast_forward`, not
`push:pr_closed`, and its class is `done`, so the loop falls through every test and breaks, and
`create_pr` runs. `push:non_fast_forward` means the remote work branch carries commits the local one
does not (Section 9.1), so the invocation **opens or updates a pull request whose head is what the
remote already held, not the work the invocation committed** — and returns `create_pr`'s result, so
the caller is told the ship succeeded. The `integrate` even made the push viable; the sequence
simply never retries it.

**Commit loop.** `commit:worktree_moved → run_op <anything class done>` substitutes a `done` result
for the one the loop tests, the loop falls through, and `ship` **pushes a worktree it did not
commit** — nothing committed, and the push reporting `ok`.

Section 12.3 has the same shape with a milder symptom: an edge bound to `merge:head_moved` replaces
the result the loop tests for, the built-in re-read-and-retry is silently disabled, and `land`
returns some other operation's result without merging. Nothing is written wrongly there, but the
routing Section 12.3 describes as built in is gone.

### The `§13.1` row that is *not* falsified, and why that is worse

The commit-loop write reaches the state Section 13.1 names as the thing the `is_dirty()` guard
exists to prevent — "a `ship` whose `is_dirty()` cannot answer dispatches `commit` and yields
`commit:failed` rather than pushing an uncommitted worktree". But it does not falsify the row: that
row is scoped to the predicate *failing to answer*, and here the predicate answered fine, `commit`
was dispatched, and a substituted result satisfied the loop's exit test. The guard behaves exactly
as the row says; the state is reached **around** it.

That is worth more than a falsified row. **The document asserts the property only where the guard is
the mechanism, and asserts it nowhere in general.** There is no row saying `ship` does not reach
`create_pr` without a successful `push`, or `push` without a successful `commit` where the tree was
dirty. Those two sequence invariants are stated nowhere, which is why the wrong reading contradicts
no row while producing exactly the outcomes a reader would expect rows to forbid. They are the
subject of issue #111, filed separately and deliberately: this decision fixes the defect that is
here today; the invariants are what catch the next one.

## The two names, and the word with no referent

The pseudocode uses two helpers, **neither defined anywhere in the document**, and inconsistently:
`dispatch(` occurs once, at `VCSX-SPEC.md:2975`, wrapping the `commit` call; `result_of(` occurs
four times — 2993, 2996, 3041, 3051 — all on `return` paths.

```text
    c = dispatch(run_op("commit", message))   # one spelling
    r = run_op("push")                        # another, same document, eight lines apart
```

That is not merely inconsistent, it is misleading: an implementer reading `dispatch` as "policy is
consulted here" reads the bare `run_op` as "policy is not", which is the refuted third reading for
`push` alone.

Running decision 0138's own test over Section 12 — can a reader supply the body without changing
behaviour stated elsewhere — Section 12 calls about a dozen functions it does not define and all but
two pass: `flow_bound_reached` and `flow_exhausted` are fixed by Sections 5.6 and 8.4,
`worktree_dirty` by Section 12.2's own prose, `proto_class` by Sections 4.2 and 4.3,
`builtin_default` by Section 5.4, `resolve_base_ref` and `longest_prefix_match` by Section 6.4.
`dispatch` and `result_of` fail it — they are the two names at which the action-policy machine meets
a front-end sequence, and the disposition rule lives inside them. This is decision 0138's finding in
the other document.

The one-line statement of the gap is a word: Section 5.4's built-in default table ends with "for
`done` with no edge, continue." **Nothing in the document says what `continue` continues.** Every
substitution chain this decision is about terminates there — the edge dispatches, the dispatched
result matches no edge, its class is `done`, and the machine's answer is a verb with no object. The
corpus already noticed: `match-edge.json`'s notes say "`continue` and `no_op` are Section 5.4
outcomes, not Section 5.2 actions", a distinction it had to invent because Section 5.4 gives
outcomes where Section 5.2 gives actions.

## Decision

**Split what the pseudocode fuses — a disposition and a control transfer — and state the rule over
both:**

> A repository edge replaces the built-in **disposition** of the trigger. Where the disposition
> returns control to the sequence, the **control transfer** is a property of the trigger and is
> unchanged; where it ends the flow, the invocation ends and no transfer applies. Where the transfer
> is `return`, the sequence reports the result the machine last handed back.

with the transfer selected by the result of the **sequence's own** `run_op` — pinned to the root, so
every substitution inside the machine is invisible to the sequence. And `dispatch` and `result_of`
are defined, or one is spelled out of existence, so the sequences use one spelling at all six call
sites.

Sorted by control transfer, the rule is determinate for all ten branches:

| Transfer | Branches |
|---|---|
| `continue` | `commit:worktree_moved`, `push:non_fast_forward`, `merge:head_moved` |
| `return` | `push:pr_closed`, `push` class≠`done`, `create_pr`, `await` class≠`done`, `merge` fall-through |
| `break` | commit-loop fall-through, push-loop `done` |

- `push:non_fast_forward → run_op integrate` — disposition replaced, so `integrate` runs once rather
  than twice; transfer `continue`; the push is retried. Section 6.5's example is correct.
- `commit:worktree_moved → run_op status` — transfer `continue`, so the loop re-reads `is_dirty()`
  and re-dispatches `commit` rather than falling through to `push`. The second wrong write closes.
- `merge:head_moved → run_op status` — transfer `continue`, merge retried; Section 12.3's existing
  sentence stays true word for word, since only a flow-ending edge surfaces the reason.
- `push:pr_closed → run_op status` — no escalation raised, transfer `return`, `ship` reports
  `status:ok`. Odd policy, determinate outcome, edge honoured.

### Pinning the transfer to the root

"The trigger it replaced" is ambiguous once a repository binds `integrate:ok` as well as
`push:non_fast_forward`: the substituted result then replaced `integrate:ok`, which replaced
`push:non_fast_forward`. The transfer is selected by the sequence's own dispatch and by nothing else
— the same "the trigger is the whole of the key" discipline Section 5.4 already states.

### The clause the first draft of the rule was missing

As first phrased the transfer was unconditional: "a property of the trigger and is unchanged." That
is **false where the edge's action ends the flow.** `push:non_fast_forward → escalate` disposes of
the outcome by ending the flow (Section 5.6: `escalate`, `park` and `fail` end it), so there is no
control to transfer and nothing to continue; the same holds for a substituted result whose class
default is `fail`. Without the middle clause the rule says such an edge continues the push loop,
which is the one thing Section 5.6 says an `escalate` does not do. Recorded rather than fixed
quietly, because it is a defect introduced by the repair for a defect — the repair for an
under-specified landing point briefly specified a landing point that contradicts the action's own
definition.

## The permission, and the invariant it costs

`push:pr_closed → run_op status` makes `ship` return `status:ok` — a `done`-class success for an
invocation that pushed nothing and opened no pull request. This is not hypothetical: it is merged
behaviour in the reporting engine, verified there through three steps, and the only thing between it
and a consumer observing it is that no repository has yet written that edge. So the question is owed
an answer rather than a note.

**The answer is that policy may end a front-end early, and the argument is not the one first
offered.** The apparent tension was "edges override each step" against Section 7.1's "`ship` drives
the change from the current worktree up to and including opening or updating the pull request".
Those two do not conflict: Section 12.2's built-in sequence **already** ends `ship` without a pull
request on five paths — `flow_exhausted()` twice, `escalate("resolve_conflicts")` on
`integrate:merge_conflicts`, `escalate("human_review")` on `push:pr_closed`, and `return
result_of(r)` where the push's class is not `done`. Section 7.1 describes the extent of the
sequence, not a postcondition, and it never was one. A repository edge that ends it early does
nothing the built-in does not.

**What the edge introduces is a `done`-class early return, and that is the thing to state.** Every
one of those five built-in exits is non-`done`: two escalations and a flow bound are `needs_caller`,
and the fourth is `class != done` by construction. So `ship` returns a `done`-class result today
**only from `create_pr`**, and `land` only from `merge` — Section 12.3's other exits being
`flow_exhausted()` and a non-`done` await. That is a real invariant, it is what a caller reads to
know the pull request exists, and it is written down nowhere. `push:pr_closed → run_op status`
therefore does not violate a rule; it silently repurposes the only completion signal the envelope
has.

**The replacement test is the operation the result names, not its class**: a `ship` that completed
its sequence reports `create_pr`'s result, a `land` that completed reports `merge`'s. That is
readable from the envelope today and needs no new field. It has to be the operation rather than an
`outputs` key, and the corpus says why: `vocabulary.json`'s `output_keys` group carries the keys
Section 8.2 fixes — ten of them, `unperformed_intents`, `unfinished_hooks`, `unanswered_gates`,
`failed_by_policy`, `forge_budget`, the three `pr_state_*` keys, `forge_unavailable_condition` and
`resume_token` — and says "the rest of `outputs` is entry-specific and is not a shared vocabulary".
No pull-request identifier is among them, so one there is a front-end's own key and a consumer
cannot portably test it. (An earlier draft of this decision, and the reply on issue #107 it came
from, said the group fixes three. It fixes ten; the conclusion turns on the note rather than on the
count, but the count was wrong in both.) Section 13.1 is where the clause belongs — the same
row issue #111's invariants go to.

## Options considered

### Land a substituted result where the trigger's built-in disposition would have landed

The report's own rule, and the chosen rule is a strict refinement of it rather than a different
answer. It reads cleanly against `push:non_fast_forward`, whose built-in disposition ends in
`continue` — a place in the sequence. It is **determinate for three of Section 12's branches and
silent for five**: for a `return`-shaped branch the built-in disposition lands nowhere in the
sequence, it exits. Take `push:pr_closed → run_op status`: the built-in is `return
escalate("human_review")`, so the rule admits two answers — `ship` returns the escalation the
built-in would have raised, nullifying an edge the repository wrote and contradicting "edges
override each step"; or `ship` returns `status:ok`, which the rule does not say. The split decides
all ten.

### Make the built-in routings unoverridable

The reading in which `result_of` is where Section 5.4's disposition is applied and the sequence
calls it only where it stops, so a repository's edges on `push:non_fast_forward`,
`commit:worktree_moved` and `merge:head_moved` never fire under a front-end sequence. It has the
merit of making the wrong writes impossible by construction. It loses because Section 12.3:3078
already says the opposite in the document's own words, and because it would make the three built-in
routings the only unoverridable edges in a policy language whose stated property is that edges
override each step.

### Leave the rule to the prose beneath the pseudocode blocks

The status quo: "The routing above is the built-in default; a repository's `[policy]` edges override
each step" is already there, one line below the block. It loses on evidence — three call sites in a
shipping engine implement the wrong reading, each a faithful reading of the text, and the pseudocode
is what an implementer follows. Whatever the answer, Sections 12.2 and 12.3 should show it rather
than leave it to the sentence beneath them.

## On the vectors

`match_edge` pins the ladder and stops at edge selection **by construction**, so "the next operation
dispatched" is not its output. These vectors need a new corpus function whose inputs are the
sequence, the position in it, the trigger and the edge set — which is exactly the function the first
half of this decision defines. Defining the helpers and making the vectors authorable are one edit.

- Three pairs on the `continue`-shaped branches (`push:non_fast_forward`, `commit:worktree_moved`,
  `merge:head_moved`), each with and without a repository edge bound to it.
- A fourth, discriminating case on a `return`-shaped branch: `push:pr_closed → run_op status`, where
  the three candidate answers (built-in escalation / substituted result / retry) are distinguishable
  in one `expect`. Without it the corpus passes green over exactly the half the report's original
  rule already decided.
- Each `expect` names **three** things: the disposition taken, the control transfer, and what the
  invocation reports. Disposition and transfer are separately implementable — in the reporting
  engine `disposed` is computed before the transfer arm is chosen — so they are separately wrong;
  and a vector naming both but not the reported result cannot distinguish "returns `status:ok`" from
  "returns the built-in escalation", which is the pair the `done`-class permission is about.

## Relationship to issues #103 and #111

The dependency on #103 is one-directional and worth stating: under any rule of this shape the
landing point is a **named position in a sequence**, which is the same object #103's wide reading
needs the resume token to carry. Settle this and #103's token carries a thing the specification
defined; settle #103 first and its cursor points at a concept with no definition. And this decision
costs #103 nothing if #103 lands narrow, because the landing point is owed for the no-resume case
regardless.

Issue #111 is independent by design, and under the split its two invariants are **derivable rather
than additional**: `create_pr` is reached only by the push loop's `break`, and the transfer is
selected by the sequence's own `run_op` result, so the only results that reach `break` are `push:ok`
and `push:up_to_date` whatever a repository binds to them; likewise `commit:worktree_moved` keeps
its `continue`, so the fall-through to `push` is reachable only from a clean read or a `commit`
result that is neither `worktree_moved` nor flow-ending. That makes those rows a **regression test
on this rule** rather than a new constraint on policy — an argument for stating them, not against.

## What was checked

At `97617c2`, against the working tree:

- `dispatch(` occurs once (`VCSX-SPEC.md:2975`); `result_of(` four times (2993, 2996, 3041, 3051),
  all on `return` paths. Two carry the annotation "class default (Section 5.4)" (2993, 3041); 2996
  says "stops at the pull request" and 3051 "merge:not_open / checks_pending -> needs_caller". An
  earlier claim that all four carry the class-default annotation was wrong and is corrected here.
- Section 6.5's example edge is `push:non_fast_forward → run_op integrate`, and
  `conformance/vcsx/vectors/match-edge.json`'s first vector is built on it.
- Section 12.3's sentence refuting the third reading is at `VCSX-SPEC.md:3078`; Section 13.1's
  `is_dirty()` sentence at `VCSX-SPEC.md:3194`; `match-edge.json`'s `continue`/`no_op` note
  verbatim.
- Section 12.2's built-in exits without a pull request number five, and every one is non-`done`.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Reconsideration triggers

- **A front-end sequence gaining a branch whose transfer is not one of `continue` / `break` /
  `return`.** The rule enumerates the transfers the two sequences use; a third shape would need the
  rule restated over it rather than extended by analogy.
- **A repository wanting an edge to change the transfer as well as the disposition** — for example,
  binding `push:non_fast_forward` to something that should stop rather than retry. Today that is
  spelled with a flow-ending action, and the middle clause covers it; a demand for a non-ending edge
  that still exits the sequence would reopen the split.
- **A consumer relying on the class as a completion signal.** The permission above assumes the
  replacement test — the operation the result names — is adopted with it. If Section 13.1's clause
  is not written, the permission should be revisited rather than left standing alone.
- **Issue #103 landing wide with a different notion of a sequence position.** The landing point here
  and the token's cursor there must be the same object; two spellings of one concept is the defect
  issue #100 reports.
