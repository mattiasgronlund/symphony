# Background — 0033 A `Superseded` state in the decision-log lifecycle

## Context

The decision-log lifecycle (decision 0001) defined three states: `Proposed`, `Accepted`, and
`Rejected` (decided against; kept for the record). Decision 0030 (the action-policy machine) exposed
a gap in that vocabulary: 0030 **supersedes the positional-hook axis of decision 0026** while keeping
0026's durable contributions — the four lifecycle positions (now expressed as triggers) and their
two-trust-level classification (still referenced by decision 0029).

Neither existing state describes 0026's resulting status:

- `Rejected` means *decided against on its own merits*. That mischaracterizes 0026: its mechanism was
  sound and parts of it live on inside 0030. Marking it `Rejected` would tell a future reader the
  idea was wrong, which is false and would discourage mining it for the parts that survived.
- Leaving it `Proposed` is also wrong: its central framing is no longer under consideration — it has
  been overtaken — so the state would misrepresent it as a live candidate.

The missing concept is "**overtaken by a later decision, kept for the record**" — a decision that was
not refuted but replaced, possibly with parts carried forward into its successor.

## Options considered

- **Option A — Reuse `Rejected`.** Trade-offs: no new state to define, but conflates "decided
  against" with "replaced by a successor", losing the distinction that matters most when re-reading
  the log later. Rejected.

- **Option B — Leave the decision `Proposed` and annotate its Background.** Trade-offs: append-only
  history is preserved, but the at-a-glance `State` field stays misleading (a superseded decision
  reads as a live candidate), defeating the purpose of the field. Rejected.

- **Option C — Add a `Superseded` state (chosen).** A fourth lifecycle state: *replaced by a later
  decision; kept for the record*. A `Superseded` chapter MUST name the decision that replaced it, so
  the successor is one hop away. Distinct from `Rejected` because a superseded decision may have been
  sound and parts of it may survive in its successor. Trade-offs: one more state to keep in sync
  across the two places the vocabulary is written (the `DECISIONS.md` legend and `CLAUDE.md`), but it
  is the only option that keeps the `State` field truthful at a glance.

## Decision and reasoning

Choose **Option C**. Add `Superseded` to the lifecycle. Semantics: a decision moves to `Superseded`
when a later decision replaces its framing or mechanism; the chapter records the superseding decision
by number, and the superseded decision's `Background.md` is extended (append-only, per the 0001
workflow) to record the re-evaluation. The transition is `Proposed`/`Accepted` → `Superseded`.

This refines decision 0001 (which fixed the original three-state lifecycle). Decision 0026 is the
first user of the new state, superseded by decision 0030.

We would reconsider if `Superseded` and `Rejected` prove indistinguishable in practice, or if a
superseded decision needs to re-enter consideration (in which case it returns to `Proposed`).

This decision's change is applied immediately on acceptance — it edits only the decision-log legend
(`DECISIONS.md`) and its `CLAUDE.md` mirror, with no `SPEC.md` dependency or forward-reference.
