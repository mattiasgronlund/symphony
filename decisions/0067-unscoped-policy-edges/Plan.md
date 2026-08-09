# Plan — 0067 An edge with no `from` is unscoped

## Scope

`VCSX-SPEC.md` Sections 5.4 "Unmatched Policy and Determinism", 6.5 "`[policy]` Edges", 12.1 "Match a
Trigger", 13.1 "Test Matrix", and 13.2 "Implementation Checklist". The corpus
(`conformance/vcsx/vectors/match-edge.json` and `conformance/vcsx/README.md`) follows.

No edit elsewhere, for stated reasons:

- **No `VCSX-CONTRACT.md` edit.** Its Section 5.3 describes matching at surface level and its Section 11
  defers the algorithm and the field-level `repo.policy.toml` schema to `VCSX-SPEC.md`; no shared token
  is added, renamed, or removed, so Section 14's alignment rule is not engaged.
- **No `SPEC.md` edit.** Symphony consumes the engine's front-ends; it authors no policy edge and
  supplies no from-context of its own.
- **No `conformance/vcsx/vocabulary.json` edit.** No token is added, renamed, or removed. `from` is a
  field of Section 6.5's edge schema, and the registry carries token groups — `trigger_kinds` describes
  the three trigger *forms*, not an edge's keys.
- **No `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit.** The decision introduces no
  `Implementation-defined` behavior, no reason token, and no `need`.
- **No Section 6.10 edit.** `duplicate_edge` is unchanged: a scoped and an unscoped edge over one
  trigger are distinct `(from, on)` keys and were never a duplicate. Section 5.4 states that explicitly
  so a validator does not read one into the rule.
- **No Section 6.7 edit.** `tracker.transitions` rows are keyed `(from, on)` by construction and have no
  unscoped form, so its own determinism rule is untouched.

## Steps

1. **Section 5.4 states that an edge with no `from` is unscoped.** Ensure the bullet list following
   "The policy graph MUST be deterministic" contains a bullet establishing that an edge carrying no
   `from` is a candidate in every from-context, including none, that scoping is opt-in per edge, and
   that this is what keeps the same `repo.policy.toml` yielding one flow under a front-end that
   supplies a from-context and one that does not (Section 13.1). Done when the mixed case — some edges
   scoped, the rest not — has a stated answer rather than one inferred from "absent such a model the
   key is the trigger alone".
2. **Section 5.4 states the precedence between a scoped and an unscoped edge.** Ensure a bullet
   establishes that where one trigger key has both, the scoped edge is selected; that the two are
   distinct keys rather than a duplicate `(from, on)`; and that the from-context is a tiebreak within a
   key rather than an outer loop over the ladder, so an unscoped `push:non_fast_forward` edge is
   selected over an edge scoped to the current context on `push:#needs_caller`. Done when a reader can
   resolve a policy holding both kinds of edge without consulting an implementation.
3. **Section 6.5 says it where the edge schema is defined.** Ensure the sentence introducing the
   OPTIONAL `from` key continues into the unscoped rule and the precedence, citing Section 5.4. Done
   when a policy author reading only the `[policy]` schema can tell what omitting `from` means.
4. **Section 12.1's `match_edge` shows the fallback.** Ensure the loop over `ladder(trigger)` looks up
   the edge scoped to `from_context` and falls back to the unscoped edge for the same key before
   advancing to the next key. Done when the pseudocode's `policy.lookup` is no longer written as though
   it were total, and the ladder remains the outer loop.
5. **The corpus asserts all three behaviors.** Ensure `match-edge.json` contains
   `unscoped_edge_matches_inside_a_from_context` (an edge with no `from` fires under a non-null
   from-context), `scoped_edge_wins_over_unscoped_edge_in_its_context` (both present for one trigger,
   the scoped edge selected), and `ladder_outranks_the_from_context` (an unscoped exact edge selected
   over a context-scoped class edge). Done when no `match_edge` vector leaves an unscoped edge under a
   non-null from-context untested, and every `id` in the file is unique.
6. **The corpus README's count tracks the addition.** Ensure the vector total and the parenthetical
   recording how the slice grew name this decision's three vectors. Done when the stated count equals
   the number of vectors across `conformance/vcsx/vectors/*.json`.
7. **The README records the finding as resolved.** Ensure "Surfaced findings" carries an entry in the
   shape decisions 0054–0056 use, noting that this one came from an implementation reading the corpus
   rather than from authoring it. Done when the entry names the decision, the resolution, and the
   vectors that cover it.
8. **Sections 13.1 and 13.2 stay in step.** Ensure 13.1's Matching bullet covers an unscoped edge under
   a from-context, the scoped edge's precedence, and the ladder-before-context ordering, and that
   13.2's action-policy-machine item names from-context scoping. Done when the test matrix names every
   behavior the new vectors assert.

## Cross-cutting sync

`conformance/vcsx/vectors/match-edge.json` (Step 5) and `conformance/vcsx/README.md` (Steps 6 and 7),
plus `VCSX-SPEC.md` Sections 13.1 and 13.2 (Step 8). Nothing in `SPEC.md`'s config cheat sheet, test
matrix, or checklist: the change is entirely within the engine documents.

## Anchor changes

None. No code token or section title is added, renamed, or removed. `from`, `duplicate_edge`, and
`tracker.transitions` all keep their spellings and their meanings; what changes is that the
specification now states how an edge *without* `from` behaves.

## Out of scope

- **Restricting or widening what `from` may scope.** Section 6.5 says `from` is "used only by transition
  edges"; this decision neither relaxes nor tightens that, since the question asked is about edges that
  carry no `from` at all.
- **A per-context mode construct.** Making one scoped edge override every unscoped edge is Option D of
  the Background, rejected there; if the cost of scoping each overridden edge ever dominates, the answer
  is an explicit construct rather than a reordered ladder.
- **The `from_context` argument's provenance.** How a consumer determines the context it invokes in is
  the consumer's, per Section 6.7's rule that mapping a state name to a tracker's representation is the
  consumer's.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 12.1, 13.1, 13.2) and `conformance/vcsx/` (vectors and
README).
