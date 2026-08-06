# Plan — 0054 An unmatched lifecycle position proceeds

## Scope

`VCSX-SPEC.md` Section 5.4 "Unmatched Policy and Determinism" gains one bullet. The corpus
(`conformance/vcsx/vectors/match-edge.json`) tightens one vector and adds one. No `VCSX-CONTRACT.md`
or `SPEC.md` edit: no shared token is added, renamed, or removed, and the contract defers the machine's
algorithms to `VCSX-SPEC.md`.

## Steps

1. **Section 5.4 states the unmatched-lifecycle-position rule.** Ensure the bullet list covers a
   lifecycle position with no matching edge: a benign no-op, nothing runs at the position, the
   operation proceeds. Done when all three trigger kinds named in Section 5.1 have a stated
   unmatched behavior.
2. **The rule carries its rationale.** Ensure the bullet states why a position differs from an
   operation outcome — a position is an offered interposition point rather than a result requiring
   disposition, so leaving one unbound strands nothing — and connects that to the no-class-fallback
   rule Section 5.3 already states. Done when a reader cannot reach the fail-safe generalization from
   the neighbouring bullet without meeting this one.
3. **The corpus asserts the outcome.** Ensure `match-edge.json`'s
   `lifecycle_position_has_no_class_fallback` expects `action: "continue"` rather than leaving the
   outcome unconstrained, and that a vector covers a policy binding only some required positions.
   Done when no `match_edge` vector relies on the "keys absent are unconstrained" rule for this
   behavior.
4. **The README finding is marked resolved.** Ensure `conformance/vcsx/README.md`'s "Surfaced
   findings" records the resolution and names this decision, in the shape decision 0046's README used
   once 0047 resolved its finding. Done when the entry reads as resolved rather than open.

## Out of scope

- **Section 12.1's pseudocode.** `builtin_default(trigger)` is already correct at its level of
  abstraction; this decision fixes what that function returns for one trigger kind, not the algorithm
  that calls it.
- **The other two findings 0053 surfaced.** The signal class form and the absence of
  configuration-error tokens are taken up as decisions 0055 and 0056.

## Cross-cutting sync

None in `SPEC.md`, `VCSX-CONTRACT.md`, `vocabulary.json`, or
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. No token, action, or trigger is added or renamed — the
change fixes an outcome the specification had left unstated.

## Anchor changes

None.

## Status

Applied to `VCSX-SPEC.md` (Section 5.4) and `conformance/vcsx/` (vectors and README).
