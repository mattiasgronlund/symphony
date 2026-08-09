# Background — 0067 An edge with no `from` is unscoped

## Context

Raised as issue #13 by an engine implementation (`vcsx-policy`) built against `06a3bc19`, which had to
pick a reading to compile and recorded it as resolution R2 of its own decision 0011.

`VCSX-SPEC.md` Section 5.4's determinism bullet keys the policy graph on `(from-context, trigger)` and
closes with:

> "from-context" allows a repository to give the same trigger different edges at different lifecycle
> points where the engine models them (for example a transition graph keyed on a workflow-state
> `from`, Section 6.7); absent such a model the key is the trigger alone.

That sentence settles the two all-or-nothing configurations. It does not settle the **mixed** one — and
mixed is the only configuration a repository running a transition graph is ever in. Section 6.7's graph
is keyed `(from, on)` by construction, while the edges that make a policy work carry no `from` at all:
the `push:non_fast_forward → integrate` routing, the `#error` catch-all, the `before:commit` scan. So a
repository that adds one transition edge immediately holds a policy in which some edges name a context
and most do not, and the specification says nothing about the second kind while a context is in force.

The two readings differ by a whole policy rather than by one edge:

- **Unscoped** — an edge with no `from` is a candidate in every context. Adding a transition edge
  changes what one trigger does in one context.
- **Own null context** — `from` is part of the key and an absent `from` means the key `(null, on)`, so
  an ordinary edge matches only when the caller is in no context. Every ordinary edge stops firing the
  moment the consumer supplies a context, silently and all at once.

The corpus made the silence visible rather than creating it: 22 of `match-edge.json`'s 24 vectors pass
`"from_context": null`, and the two that do not — `from_context_disambiguates_same_trigger` and
`from_context_scoped_edge_does_not_leak` — both exercise edges that *carry* `from`. An unscoped edge
under a non-null from-context is exactly the untested combination.

Answering the question exposes a second one the issue does not ask, which any mixed policy hits on its
first edge. Once an unscoped edge is a candidate in a context, one trigger key can have two candidates
— a scoped edge and an unscoped one — and Section 5.4's "at most one edge per key" does not choose
between them, because they are not the same key. Section 12.1's `policy.lookup(from_context, key)` is
written as though the lookup were total and says nothing about the unscoped edge. Both halves have to
be settled together or the first answer is unusable.

## Options considered

- **Option A — an edge with no `from` is unscoped; a scoped edge outranks an unscoped one for the same
  key; the ladder selects the key first (chosen).** Trade-offs: a repository wanting a context to act
  as a *mode* — "in `Human Review` every error escalates rather than fails" — cannot get it from one
  scoped `#error` edge, because an unscoped exact edge is more specific and is selected first. It must
  scope the edges it wants overridden, at the specificity they are written.
- **Option B — an absent `from` is the null context.** It is the most literal reading of "a key of
  `(from-context, trigger)`", and it needs no precedence rule at all, since no two edges are ever both
  candidates. Rejected: it contradicts an existing requirement rather than merely reading badly (see
  below), it makes a local addition silently disable an entire policy, and under it a policy cannot
  express "in every context" — the from-context is supplied by the consumer out of its own tracker
  (Section 6.7), so the contexts are not a closed set the policy can enumerate or the engine validate.
- **Option C — mixing a scoped and an unscoped edge over one trigger is a configuration error.** It
  catches the ambiguity at validation time, where Section 6.10 catches the rest of them, and forces a
  repository to be explicit. Rejected: it makes adding one transition edge retroactively invalidate a
  working policy, it needs a tenth configuration reason for a condition that is not a defect, and it
  forbids the default-plus-override idiom that is the reason to have a default. The enumeration
  objection to Option B applies unchanged: "every other context" cannot be written out.
- **Option D — unscoped, but resolve the from-context before the ladder.** Walk the whole ladder in the
  current context, then walk it again unscoped, so a context's edges are consulted first. It buys
  Option A's missing mode behavior: one scoped `#error` edge would override every unscoped edge while
  the context holds. Rejected: it lets a broader trigger beat a more specific one — a scoped
  `push:#needs_caller` edge would shadow an unscoped `push:non_fast_forward` edge — which is the exact
  property Section 5.3's most-specific-wins exists to prevent, and it reproduces Option B's failure
  mode in miniature, since one scoped class edge silently changes what every unscoped edge does. It
  also inverts Section 12.1, where the ladder is already the outer loop.
- **Option E — answer in the corpus alone and leave Section 5.4 as written**, which is what the issue
  asks for. Rejected: `conformance/vcsx/README.md` states that the specification governs and that every
  value is read from the sections a file's `spec_refs` cite. Neither the scope rule nor the precedence
  rule can be read out of Section 5.4 as it stands, so the vector would be authoring the answer, which
  decision 0045's hygiene rule reserves for a decision. The corpus is also the wrong home for the
  second half: a vector can pin which edge wins, but only the prose can say why, and an implementer
  reading Section 5.4 would still have to guess.

## Decision and reasoning

Choose **Option A**. Section 5.4 gains two bullets: an edge carrying no `from` is unscoped and is a
candidate in every from-context, including none; and where one trigger key has both a scoped and an
unscoped edge the scoped one is selected, the from-context acting as a tiebreak *within* a key rather
than as an outer loop over the ladder.

Option B is not merely the less attractive reading — it is unavailable. Section 13.1 requires that "the
same `repo.policy.toml` yields the same operation flow through `ship` and an embedded driver", and
`VCSX-CONTRACT.md` Section 3 states the same rule for the two front-ends. The interactive front-end has
no tracker binding and so supplies no from-context (Section 5.2), while an embedded driver running the
consumer's workflow states supplies one. Under Option B the unscoped `push:non_fast_forward → integrate`
edge fires under `ship` and does not fire under the driver — two different operation flows from one
policy, which that requirement forbids. Deriving the answer from a rule the document already states is
what makes it stable; the issue's own argument from failure modes agrees with it, but does not have to
carry it.

The precedence rule is the half worth reasoning about, because it is where the two dimensions meet.
Section 5.3 makes trigger specificity the ordering principle, and Section 12.1 already encodes it as the
outer loop; from-context is a second axis, and the choice is whether it wraps that loop or sits inside
it. It sits inside: for one trigger key, an edge naming the current context is a more specific statement
than one naming no context, and it wins. Across keys, nothing changes — naming a context does not make a
broader trigger the more specific match. Read the other way (Option D), a repository's single scoped
`#error` edge would take over from every unscoped edge the moment the context held, which is the
whole-policy surprise this decision exists to remove, arriving from the other direction.

The accepted cost is stated rather than hidden: per-context *modes* are not expressible in one edge. A
repository that wants every error escalated in one workflow state scopes the edges it wants overridden,
rather than writing one scoped class edge and expecting it to outrank exact ones. That is more edges,
and it is the price of keeping "most specific wins" true in the only dimension the specification claims
it for.

Two things stay untouched, and are worth naming because a reader might expect them to move.
`duplicate_edge` (Section 6.10) is unchanged: a scoped and an unscoped edge over one trigger are
different keys, so they were never a duplicate, and the new bullet says so to keep a validator from
inventing one. Section 6.7's `tracker.transitions` graph keeps its own determinism rule, since its rows
are keyed `(from, on)` by construction and have no unscoped form.

What would make us reconsider: a from-context vocabulary the *engine* owned — a closed, enumerable set
rather than the consumer's tracker states — would make Option B's completeness checkable and Option C's
validation meaningful, and would be worth re-deriving against. Or evidence that per-context modes are
common enough that scoping each overridden edge is the dominant cost of authoring a policy, in which
case the answer is an explicit mode construct rather than inverting the ladder, since inverting it
breaks the specificity guarantee for every policy that does not want a mode.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 12.1, 13.1, 13.2) and the
corpus (`match-edge.json` gains `unscoped_edge_matches_inside_a_from_context`,
`scoped_edge_wins_over_unscoped_edge_in_its_context`, and `ladder_outranks_the_from_context`). Relates
to 0030 (the action-policy machine this refines), 0053 (the corpus that made the gap visible), 0045
(the hygiene rule that makes it a decision rather than a guessed-at vector), and 0054 and 0055 — the two
sibling `match_edge` clarifications, each of which likewise settled a case Section 5.4 or 5.3 had left
to inference.
