# Plan — 0033 A `Superseded` state in the decision-log lifecycle

## Scope

Process-level (the decision log itself), not `SPEC.md`. Affected anchors:

- The **States** legend in `DECISIONS.md` (the canonical enumeration).
- The decision-log description in `CLAUDE.md` that mirrors the state list (`Proposed` / `Accepted` /
  `Rejected`).

No `SPEC.md` change. No `decisions/_template/` change (the template carries no state enumeration).

## Steps

1. **Add the state to the canonical legend.** Ensure the `DECISIONS.md` **States** line lists
   `Superseded` (replaced by a later decision; kept for the record) alongside the existing three, and
   states the rule that a `Superseded` chapter names the superseding decision. Done when the legend
   enumerates four states and the successor-pointer rule is stated.

2. **Mirror the state in `CLAUDE.md`.** Ensure the decision-log section's inline state list reads
   `Proposed` / `Accepted` / `Rejected` / `Superseded`. Done when both files agree.

3. **First use.** Decision 0026 moves to `Superseded` (by decision 0030). Done when 0026's `State` is
   `Superseded` and its chapter names 0030 as the successor. (Executed as part of decision 0030's
   acceptance, not owned by this plan.)

## Anchor changes

New token: the `Superseded` state. Refines decision 0001 (original three-state lifecycle). First
applied to decision 0026.

## Status

Accepted and applied: the legend in `DECISIONS.md` and the mirror in `CLAUDE.md` both enumerate
`Superseded`.
