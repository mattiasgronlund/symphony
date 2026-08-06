# Background — 0054 An unmatched lifecycle position proceeds

## Context

Decision 0053 surfaced this while authoring the engine conformance corpus. `VCSX-SPEC.md` Section 5.4
"Unmatched Policy and Determinism" fixes what happens to two of the three trigger kinds when no edge
matches — an unmatched **signal** is a benign no-op, and an unmatched **operation outcome** MUST be
fail-safe, with built-in defaults per proto class — but says nothing about a **lifecycle position**
with no edge. Section 5.3 establishes only the negative: a position is matched exactly and takes no
class fallback.

The omission is not hypothetical. Section 4.1 defines four required lifecycle positions, and a policy
binds whichever it needs; the minimal valid policy in the corpus binds `before:commit` and leaves the
other three unbound. Under a reading that treated an unmatched position like an unmatched operation
outcome, that policy could not run at all. So the specification's silence sits directly on the ordinary
case, and no vector could assert the outcome — `lifecycle_position_has_no_class_fallback` asserted only
that nothing matched.

## Options considered

- **Option A — a benign no-op; the operation proceeds (chosen).** Nothing runs at the position and the
  flow continues into the operation. Trade-offs: the only reading under which a policy may bind a
  subset of positions, which every example policy in Section 6.5 already does. Requires stating why a
  position differs from an operation outcome, since Section 5.4's existing rationale for fail-safe
  ("a dropped operation outcome would strand a flow") reads as if it should generalize.
- **Option B — fail-safe, as for an operation outcome.** Park or fail when a position is unbound.
  Trade-offs: uniform with the neighbouring bullet. But it makes every policy that does not bind all
  four positions unrunnable, which contradicts Section 6.5's own examples and would make the required
  positions mandatory bindings rather than available ones.
- **Option C — a configuration error requiring every position to be bound.** Trade-offs: fully
  deterministic and catchable at validation. Same fatal objection as B, moved earlier: it converts an
  offered interposition point into an obligation, and Section 6.10's condition list would have to grow
  a rule contradicting Section 4.1's description of positions.

## Decision and reasoning

Choose **Option A**. An unmatched lifecycle position is a benign no-op: nothing runs at the position
and the operation proceeds.

The reasoning worth recording is the distinction, not the outcome, because the outcome is the only
workable one and the distinction is what makes Section 5.4 coherent rather than arbitrary. **An
operation outcome is a result that must be disposed of**; dropping it strands a flow, which is exactly
what that bullet says. **A lifecycle position is an offered interposition point**; declining to
interpose is the normal case and strands nothing, because the operation the position gates still runs.
The same distinction explains the negative Section 5.3 already states: a position has no class fallback
because there is no outcome to classify.

The edit therefore adds the rule *and* its rationale to Section 5.4, so a later reader does not
re-derive the fail-safe generalization and reach Option B.

We would reconsider if a future position were introduced that gates something whose omission is unsafe
rather than merely unhooked — a position whose whole purpose is to force a decision. Such a position
would not be an interposition point in the sense used here, and it would belong with the fail-safe
outcomes rather than under this rule.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Section 5.4) and the corpus
(`match-edge.json`: `lifecycle_position_has_no_class_fallback` now asserts the outcome, and
`unbound_lifecycle_position_proceeds` is added). Depends on 0053, which surfaced it; relates to 0030
(the action-policy machine).
