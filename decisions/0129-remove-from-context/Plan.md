# Plan — 0129 A matching axis the contract cannot transmit

## Scope

`VCSX-SPEC.md`: Sections 5.4 "Unmatched Policy and Determinism", 6.5 "`[policy]` Edges", 6.11
"Validation", 8.5 "Versioning and the Version Grammar", 12.1 "Match a Trigger", 13.1, 13.2.

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: Section 2 "Required Surface Implemented".

`conformance/vcsx/`: `vocabulary.json`, `vectors/match-edge.json`, `vectors/policy-validation.json`,
`README.md`.

`VCSX-CONTRACT.md`: expected **none** — verified, see "Cross-cutting sync".

`SPEC.md`: none — it writes no `from`-scoped policy edge.

## Steps

1. **Determinism over the trigger alone.** Ensure Section 5.4's determinism bullet states at most one
   edge per trigger key, a duplicate being a configuration error (Section 6.11), with no composite
   key and no `(from-context, trigger)` token. Ensure the claim the removed bullets carried — one
   `repo.policy.toml` yields one operation flow whichever front-end runs it — is *kept* and stated as
   the reason, now holding unconditionally rather than by hedge. Done-condition: Section 5.4 mentions
   no from-context, and the front-end-independence claim is still made somewhere in it.

2. **The two scoping bullets go.** Ensure Section 5.4 carries neither the unscoped-edge bullet ("An
   edge that carries no `from` is **unscoped**…") nor the scoped-beats-unscoped tiebreak bullet
   ("Where one trigger key has both an edge scoped to the current from-context and an unscoped
   edge…"). Done-condition: the token `unscoped` does not appear in Section 5.4.

3. **An edge binds a trigger to an action.** Ensure Section 6.5's opening sentence states that and no
   OPTIONAL `from`, that no `[[policy.edge]]` in its TOML example carries a `from` key, and that its
   duplicate sentence reads over the trigger rather than over `(from, on)`. Done-condition: `from` is
   absent from Section 6.5 except in the forward-compatibility sentence of step 4.

4. **The stale key is ignored, not refused.** Ensure Section 6.5 carries a forward-compatibility
   sentence in the shape it already uses for the `context` key decision 0100 removed: a `from` key on
   an edge is ignored rather than refused, under Section 6.1's rule for unknown keys. Done-condition:
   a policy written against the earlier version still loads, and the section says so.

5. **The invalidated cross-reference.** Ensure Section 6.5 no longer cross-references Section 6.7 for
   an edge key — the "used only by transition edges" clause is the one decision 0122 invalidated and
   this removes. Done-condition: no clause in Section 6.5 sends a reader to `tracker.transitions` for
   the meaning of an edge key.

6. **`duplicate_edge` keyed on the trigger.** Ensure Section 6.11's `duplicate_edge` row reads "A
   duplicate policy edge — non-determinism (Section 5.4)". Ensure the `duplicate_transition` row is
   **untouched** and still reads `(from, on)`, that table remaining keyed on a `from` and validated
   (Section 6.7). Done-condition: exactly one row in the table carries `(from, on)`, and it is the
   transition row.

7. **`position_cycle` over one graph.** Ensure Section 6.11's `position_cycle` prose judges the
   condition over the `before:<op>` positions and the `run_op` edges bound to them, without "a policy
   is refused where any from-context yields such a cycle, an edge scoped to a context being selected
   over an unscoped one". Done-condition: the judgement is stated over a single graph.

8. **`match_edge` takes two parameters.** Ensure Section 12.1 is `match_edge(policy, trigger)` and its
   body walks the ladder with a single `policy.lookup(key)`, losing the scoped lookup and its unscoped
   fallback, and still returning `builtin_default(trigger)`. Ensure `ladder()` is unchanged.
   Done-condition: no `from_context` identifier remains in Section 12.1.

9. **Test matrix.** Ensure Section 13.1's matching check drops the from-context clause and keeps the
   `op:#class`, `#class`, and exact-position clauses. Ensure its determinism check distinguishes the
   two tables: a duplicate edge on one trigger, and a duplicate `(from, on)` transition.
   Done-condition: no check in Section 13.1 asserts behavior for an axis the executor no longer
   matches, and the transition half still names its own key.

10. **Implementation checklist.** Ensure Section 13.2's action-policy-machine bullet no longer lists
    "from-context scoping with unscoped edges". Done-condition: the bullet lists only machinery the
    executor has.

11. **Conformance Statement template.** Ensure
    `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 2's action-policy-machine item mirrors Section
    13.2 as it now reads: no from-context scoping, and **no-op on an unmatched position** rather than
    "no-op on an unmatched signal", which decision 0122 left behind. Ensure Section 3 gains and loses
    no row, this decision adding no `Implementation-defined` obligation and removing none.
    Done-condition: the template's checklist item and Section 13.2's bullet name the same machinery,
    and no item names a trigger kind or matching axis that does not exist.

12. **`match-edge.json`.** Ensure the `from_context` key is absent from all vectors and from the
    file-level `given` string. Ensure the five vectors exercising the axis are **removed**, not
    rewritten — the behavior they assert no longer exists:
    `from_context_disambiguates_same_trigger`, `from_context_scoped_edge_does_not_leak`,
    `unscoped_edge_matches_inside_a_from_context`,
    `scoped_edge_wins_over_unscoped_edge_in_its_context`, `ladder_outranks_the_from_context`. Ensure
    what they *also* asserted survives where it is not already covered: the ladder claims are
    (exact over class, class-fallback default) already carried by
    `exact_beats_op_class_and_bare_class` and `default_for_done_is_continue`, and the one thing no
    surviving vector carries is an `expect` that pins an action **argument** — so pin
    `"op": "integrate"` on `exact_beats_op_class_and_bare_class`, which Section 12.1's `return edge`
    supports and which keeps the file-level `expect` clause "any action argument the vector pins"
    describing something. Done-condition: 19 vectors, no `from_context` key, and at least one vector
    pinning an action argument.

13. **`policy-validation.json`.** Ensure `same_trigger_at_different_from_contexts_is_valid` is
    inverted rather than deleted: two edges differing only by `from` are now a plain `duplicate_edge`,
    with an id, description and `expect` that say so. Ensure the `duplicate_edge_is_non_deterministic`
    vector's description no longer glosses the key as `(from-context, trigger)`. Ensure the
    `tracker.transitions` vectors (`duplicate_transition_is_non_deterministic` and the valid one) are
    untouched. Done-condition: 38 vectors, the transition vectors unchanged, and no description
    describing the edge key as composite.

14. **`vocabulary.json`.** Ensure `duplicate_edge`'s `meaning` reads over the trigger and drops
    `(from, on)`; ensure `duplicate_transition`'s keeps it. Done-condition: the two meanings differ in
    their key, as the two tables now do.

15. **`conformance/vcsx/README.md`.** Ensure the vector-count parenthetical's running total and its
    decision-0067 clause are corrected for the five removed vectors. Ensure the **Surfaced findings**
    entry for decision 0067 is *not* rewritten — it is a historical record of what the corpus surfaced
    — and that a new finding is appended beside it naming that the repair 0067 made is what this
    decision removed, with the recurrence count. Done-condition: the stated total equals the vector
    count on disk, and 0067's finding still reads as written with its outcome recorded after it.

## Cross-cutting sync

`VCSX-SPEC.md`: Section 13.1 (test matrix), Section 13.2 (implementation checklist) — steps 9 and 10.
Section 13.3 gains and loses nothing: it carries no from-context obligation, and this decision adds no
`Implementation-defined` answer. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 therefore needs no
row; its Section 2 checklist mirror is step 11.

Section 8.5 is unaffected in mechanism and affected in fact: removing a matching axis changes the
major-stable surface, so it lands in the next `MAJOR`. Record it in the section's own terms, as
decision 0122 did for a trigger kind, rather than as an exception.

`VCSX-CONTRACT.md`: **no edits**, verified rather than assumed. `grep -n "from-context\|\bfrom\b"`
over it returns no matching or determinism text; Section 5.3 "Matching and the `#class` Fallback"
gives the ladder alone and Section 5.4 "Unmatched Policy" states the two dispositions without a
determinism key. The contract never spelled `from`, so Section 12's alignment rule — no token spelled
in one document and absent from the other — is satisfied by removal rather than broken by it.

`SPEC.md`: no change. It writes no `from`-scoped policy edge, and Section 9.12's trigger vocabulary
was repaired by decision 0127.

## Anchor changes

Removed anchors:

- The **from-context** as an engine matching axis, and with it the `from` key on a `[[policy.edge]]`.
  The key survives only as an ignored unknown key (Section 6.1), not as an anchor.
- `match_edge`'s `from_context` parameter (Section 12.1).
- `from_context` as a `given` field in `conformance/vcsx/vectors/match-edge.json`.
- The five `match-edge.json` vector ids listed in step 12, and the id
  `same_trigger_at_different_from_contexts_is_valid` in `policy-validation.json`, renamed to the
  inverted vector it becomes.

Not removed, and deliberately so: `tracker.transitions`' own `from` key and its `(from, on)`
determinism key (Section 6.7), the `duplicate_transition` configuration reason, and every
`tracker.transitions` vector. That table is consumer-read and keeps its scoping.

No section is renamed or renumbered; nothing is inserted or reordered, so every existing `Section N.M`
cross-reference keeps its target.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.4, 6.5, 6.11, 8.5, 12.1, 13.1, 13.2),
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 2), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/match-edge.json`, `conformance/vcsx/vectors/policy-validation.json`, and
`conformance/vcsx/README.md`.
