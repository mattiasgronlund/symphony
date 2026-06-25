# Plan — 0014 Turn and step terminology

## Scope

Additive terminology clarification in `SPEC.md`. Introduces the term `step` and the run/turn/step
nesting in Section 10.3 "Streaming Turn Processing", and clarifies the `max_turns` field. No
behavior, field, error code, event, or conformance requirement changes; `turn`, `turn_id`,
`turn_count`, and `max_turns` retain their current meanings.

## Steps

1. In Section 10.3 "Streaming Turn Processing", ensure a definitional lead-in exists that: defines a
   *turn* as one orchestration-initiated prompt-to-completion cycle on the live thread (the targeted
   protocol's turn unit; the Codex adapter maps it to one `turn_id`, Section 10.2); defines a *step*
   as the agent's internal model-inference/tool-call iteration within a turn, explicitly
   agent-internal and not initiated or counted by Symphony (`max_turns` bounds turns, not steps),
   while noting that an adapter MAY impose its own per-turn step limit distinct from
   `agent.max_turns`; and states the nesting that a *run* (Section 7.2) contains turns and a turn
   contains steps. Done when "step" is defined in Section 10.3, the turn/step distinction is stated,
   and the adapter step-limit nuance is present.

2. In the `max_turns` field documentation (Section 5.3.5 "`agent` (object)"), ensure a sub-bullet
   clarifies that it bounds turns (orchestration-initiated prompt cycles, Section 10.3), not the
   agent's internal tool-call steps within a turn. Done when the `max_turns` entry distinguishes
   turns from steps.

## Cross-cutting sync

None. The config cheat sheet (6.4) `agent.max_turns` entry, the test matrix (17), and the checklist
(18) describe conformance surfaces unchanged by a terminology clarification; no rows are added or
renamed.

## Anchor changes

- New anchor: the term `step` (Section 10.3 "Streaming Turn Processing").
- No renames or removals: `turn`, `turn_id`, `turn_count`, `max_turns`, and the `run` / run-attempt
  vocabulary retain their meanings.

## Status

Applied to `SPEC.md`.
