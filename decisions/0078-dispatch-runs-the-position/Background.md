# Background — 0078 A dispatch runs the operation's `before:<op>` position

## Context

Resolves issue #30, surfaced while deciding Section 12.3's routing for decision 0077 and deliberately
filed rather than folded in: the built-in loop 0077 chose is correct under either reading, so the
question was over every gated operation rather than over `merge`.

Two passages describe the relation between a lifecycle position and the operation it is named after,
and they do not agree.

**The sequence owns the position.** Section 12.2 writes the gate and the operation as two statements:

```text
run_lifecycle("before:push")
r = run_op("push")
```

If `run_op` ran the gate itself, the line above it would be redundant. Section 12.3 sharpened the
reading rather than softening it — its retry "re-enters the lifecycle position **rather than the
operation alone**", which only distinguishes anything if entering the operation alone is possible.

**The operation owns the position.** Section 4.1 states gating as a property of each operation —
"`commit` — create a commit from the working tree, gated at `before:commit`" — rather than as a step
some caller takes around it. Section 6.6 surfaces a block as "the gated operation's own reason", which
is a result the operation returns. Section 13.1 asks for that surfacing "at **every gated operation**".
Section 5.6 says "the retried `push` re-gates the position", attributing the gating to the push.

## Where the readings differ, and what it costs

Section 5.2 makes `run_op(op, args?)` an action a policy edge carries and Section 5.4 makes the graph
reachable from anywhere, so this is legal configuration:

```toml
[[policy.edge]]
on = "status:ok"
do = "run_op"
op = "commit"
```

Under the first reading that `commit` runs with no `before:commit` — no `scan-content`, no gate — not
because anything defeated the gate but because nothing ran it. Under the second it gates normally.

Section 8.6 already uses *precisely this edge* as its worked example of an operation reached outside a
front-end sequence, and concludes that the operation reports `identity_missing`. The document knows the
shape exists; it has never said whether the gate travels with it.

`before:commit` is where Section 10.1 puts message validation and Section 10.4 puts content scanning,
and it is the one position Section 3.2 labels in-sandbox — because it is the position whose whole job is
to inspect content the consumer does not trust. Under the first reading a `run_op` edge is a route to
`commit` that no scan sees, and a repository binding both gets the scan on the `ship` path and not on
the other one, with nothing in the document marking the difference.

## A correction to the report

Issue #30 says the same question decides `before:push`, "which is where `§9.2`'s `pr_state` guard now
sits (decision 0076)". It does not sit there. Decision 0076 put that read **inside the operation**:
Section 4.1 has `push` read the work branch's pull-request state itself and refuse a CLOSED/MERGED one.
That guard therefore travels with any dispatch under either reading. What a policy-dispatched `push`
would skip is the *repository's* own edges at `before:push` — a real difference, and a smaller one than
the report states. The filing implementation's tree matches this reading.

## What the filing implementation shows

The engine that filed the report implements the first reading, and got there **by where `gate()`
happened to be called rather than by deciding**. That is the interoperability defect in its purest
form: an implementer who had read Sections 4.1, 6.6, 12.2 and 13.1 closely enough to cite all four in
one report still inherited the reading from whichever sentence they built the sequence from.

It also carries a test that pins the disputed behavior deliberately —
`flow::ship_runs_the_commit_gate_even_when_there_is_nothing_to_commit`, whose comment names exactly
what this decision changes: "§12.2 runs `run_lifecycle("before:commit")` ahead of the dirty check, so
an in-sandbox scan runs even on a clean worktree. Easy to lose when reading the sequence as 'commit,
then push'." So the clean-tree gate is pinned on purpose, and on examination it pins nothing anyone
needs.

**What a `before:commit` hook can observe on a clean tree is nothing.** The gate is a Section 6.6 hook
— a run unit, a process — and the invocation carries the hook's name, unit, execution context, position
and operation, and no content. The engine hands the hook nothing; the hook reads the working tree by
running in it. On a clean working tree there is nothing there to find, so an inspecting hook can only
pass. The unconditional run is observable **only** to a hook that does something other than inspect,
and Sections 6.6 and 10.4 sanction only inspecting and blocking.

The mutating pattern is mechanically available in that engine today, which is worth stating plainly
rather than assuming away: the order is gate → `is_dirty()` → `commit`, so a formatter bound at
`before:commit` would dirty the tree and get its output committed. Nothing in that repository does it,
no test covers it, and the seam cannot see it happen. It works by accident, not by design.

## Options considered

- **A — the dispatch carries the position (chosen).** The engine runs `before:<op>` whenever `<op>` is
  dispatched, from a front-end sequence, a `run_op` edge, or a retry. Sections 12.2 and 12.3 lose their
  explicit `run_lifecycle` calls, and `expected_head` stops being an argument Section 12.3 threads.
- **B — the `run_op` action carries the position; the sequences keep theirs.** State it at Section 5.2
  instead: the action runs the position and then the operation, while the front-end sequences stay
  exactly as Section 12.2 writes them. Same observable result for policy edges, and it preserves
  `ship`'s unconditional `before:commit`, so nothing that works today stops working. Rejected on two
  grounds. It makes `run_op` name two things — the policy action (position + operation) and the
  pseudocode's dispatch (operation alone) — which has to be disambiguated by renaming one of them; and
  it makes gating a property of *each dispatch path* rather than of the operation, so every future
  front-end and every engine-defined entry has to be told again. That is the shape Section 9
  deliberately rejected one layer down when decision 0076 stated the answer-domain rule over the whole
  capability list rather than per capability, on the same argument: a rule that must be repeated per
  caller is one a caller can be written without.
- **C — positions are sequence steps; a policy dispatch is ungated, said out loud.** Adopt the first
  reading explicitly and make the consequence visible at validation (Section 6.10), reporting a policy
  that binds both a `before:<op>` hook and a `run_op` edge to that operation. Rejected. It is the only
  shape under which Section 12.2's pseudocode is already correct as written, and it keeps a position
  exactly what Section 5.4 calls it — an offered interposition point rather than part of an operation —
  but Section 6.6's "surfaces as the gated operation's own reason" then has to be realized for a
  position no operation ran, and the in-sandbox trust boundary is left with a documented bypass.
  Stating a hole precisely is better than leaving it ambiguous; it is still a hole.
- **D — A plus a per-edge escape hatch** (`gated = false` on a `run_op` edge, `Default: true`).
  Rejected: it adds permanent schema surface for a case nobody asked for, and an ungated dispatch of a
  gated operation is the exact condition this decision exists to remove.

## Decision and reasoning

**A.** It is the reading three normative passages already assume — Section 4.1's "gated at", Section
6.6's "the gated operation's own reason", Section 13.1's "at every gated operation" — so choosing it
makes the document consistent by removing one sentence's implication rather than by re-stating three.
It costs no vocabulary: no reason token, no `need`, no configuration key. It closes the in-sandbox
bypass rather than documenting it. And it makes gating one rule stated once instead of a discipline
each dispatch path repeats, which is the property that decides it against B.

**The consequence, recorded rather than discovered later.** Section 12.2 ran `before:commit`
unconditionally, above the dirtiness guard; under A the position runs only when `commit` is dispatched,
so a clean working tree enters no `before:commit`. The principled line is that a position gates an
operation and where none is dispatched there is nothing to gate; the empirical line is the one above —
an inspecting hook on a clean tree can only pass, so the run that disappears is observable only to a
hook doing something the document does not sanction. A repository that wants a unit to run whether or
not a commit follows binds it to a result trigger rather than to a gate.

**Self-dispatch is not a new hazard.** A `run_op` edge at `before:<op>` naming that same operation now
loops — the dispatch runs the position that dispatches it. Section 5.6's flow bound already ends it,
and Section 5.6 states in as many words that "the bound is a count, not a cycle detector" and that an
executor refusing a graph containing a cycle would refuse the built-in routing. Detecting this one
statically at Section 6.10 was considered and rejected on that argument; Section 5.6 gains a sentence
naming the loop instead.

**Interlock with 0079.** This decision is what gives 0079's invariant one place to attach. Every
mechanism that closes a read-then-act window hands the operation a value read at its position; if a
policy-dispatched operation ran no position it would carry no such value, and the invariant would be
void on exactly the path this decision is about.

Relates to 0077 (which filed the question and is correct under either reading), 0076, 0067, 0060 and
0053.

## Revisited by 0080 (2026-08-12) — the static refusal, reconsidered

The paragraph above ("Self-dispatch is not a new hazard") is superseded on its conclusion, not on its
premise. Decision 0080 refuses the shape at Section 6.10 as `position_cycle`; the chosen option of
this decision is untouched, and Section 5.6's sentence naming the loop is replaced by the boundary.

The decline here reasoned about **cycle detection over the policy graph**, which Section 5.6 rules
out and rightly: `push:non_fast_forward → integrate → push` is the built-in routing and an executor
refusing a graph containing a cycle would refuse it. What it did not weigh is that Section 5.6 names
a measure in the same paragraph — "what separates a converging flow from a looping one is how many
operations it takes" — and that on this shape the number is zero on every traversal. A cycle made
only of lifecycle positions passes through no typed operation result, and a position is matched
exactly, has no class fallback and binds at most one edge, so nothing outside the engine appears on
the cycle and no traversal can differ from the last. Refusing it is therefore a check over a subgraph
in which no cycle can be conditional, rather than the detector Section 5.6 refuses, and every routing
that section defends survives it.

Two facts arrived after this decision landed and are what made the revisit worth doing. Issue #33
measured the shape against the filing engine — sixty-four dispatches, zero operations, reported as
`flow_exhausted`, a need glossed as a convergence failure or a fast-moving remote, with `op`,
`reason` and `class` null so the envelope names neither position nor edge. And the runtime guard that
engine shipped instead was measured refusing a flow that terminates (`before:push` → `run_op
integrate` with `integrate:ok` → `run_op push`), which is what ruled out answering this at the
dispatch. See `decisions/0080-position-cycle/Background.md`.
