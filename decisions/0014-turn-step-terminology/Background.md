# Background — 0014 Turn and step terminology

## Context

`SPEC.md` uses "turn" throughout (≈129 occurrences) for one orchestration-initiated
prompt-to-completion cycle on the live agent thread: `max_turns`, `turn_count`, `turn_id`,
`<thread_id>-<turn_id>`, the `turn_completed`/`turn_failed`/`turn_cancelled` events, the
`StreamingTurn` run phase, and the "first turn / continuation turns" worker loop (Section 7.1).
This matches the Codex app-server protocol the spec defers to, where a turn is `turn/start` ->
`turn/completed` (`v2/TurnStartParams.json`) and each adapter extracts a per-turn `turn_id`.

A second, distinct thing is also colloquially called a "turn": the coding agent's internal
tool-call loop — the model inferences and tool calls it conducts autonomously to satisfy one
prompt. The spec had no name for this (the term "step" was unused), and the app-server hides it,
surfacing only turn-level events. The ambiguity risks readers mis-reading `max_turns = 20` as a
bound on the agent's tool calls rather than on Symphony's prompt cycles.

Empirical grounding: a study of ~24 `openai/symphony` forks that swapped agent backends found the
"turn = orchestration-initiated cycle" usage is universal (`run_turn`, `max_turns`, `turn_number`),
and none of them named the agent's inner loop — confirming "turn" is the established word for the
outer cycle and the inner loop is the genuinely unnamed concept.

## Options considered

- **Keep turn = the orchestration cycle; add `step` for the inner loop (chosen).** No protocol
  divergence, minimal additive edits; `step` fills the one real gap. Nesting: a run contains turns,
  a turn contains steps.
- **Keep turn = the orchestration cycle; clarify in prose only, no new term.** Cheapest, but leaves
  the inner loop unnameable when the spec needs to refer to it.
- **Make turn = the inner tool-call loop; rename the orchestration cycle (e.g. `continuation`,
  `round`).** Matches one colloquial intuition but redefines "turn" to the opposite of the Codex
  protocol the spec normalizes against — every adapter would map Codex `turn_id`/`TurnStartParams`
  onto a non-"turn" field. Rejected as a protocol-vocabulary conflict and a large, risky rename.

## Decision and reasoning

Keep `turn` meaning the orchestration-initiated prompt-to-completion cycle (unchanged, aligned with
the targeted protocol). Introduce `step` as the agent's internal, autonomous tool-call iteration
within a turn — agent-internal, neither initiated nor counted by Symphony. Name the outer tier
`run` (already "run attempt" / "worker run" in Section 7.2). The nesting is run ⊃ turn ⊃ step.

We would reconsider only if a future adapter's source-of-truth protocol stopped calling its
prompt-cycle unit a "turn", which would weaken the alignment argument.

## Refinement: adapter-enforced step caps (Identione fork evidence)

A design note from the Identione fork (`/tmp/overseer_turn_boundaries.md`) confirmed this ambiguity
in the wild and sharpened the `step` definition. That fork shipped three different settings all
called "max turns" at different granularities: `agent.claude.max_turns` (40) bounds the Claude SDK's
inner model↔tool cycles — i.e. *steps* — via the SDK's `--max-turns`; `agent.max_turns` (20) and
`agent.overseer.absolute_max_turns` (500) bound Symphony *turns* (continuations). The Claude SDK
literally names steps "turns" (`--max-turns`), so an adapter's own step cap sits one config key away
from Symphony's turn cap.

This shows steps are not always unbounded: an adapter MAY enforce its own per-turn step limit, and
that limit is adapter-owned and distinct from `agent.max_turns`. A breach of it surfaces as a
turn-ending signal (the Claude SDK returns a terminal result, leaving the session idle and
resumable), not as a step count to Symphony. The per-adapter asymmetry is real: Claude has a step
cap, Codex has none (its only per-turn bound is Symphony's wall-clock `codex.turn_timeout_ms`).
Section 10.3 was extended to state the adapter step-limit nuance accordingly.

The same note's larger findings — turn timeouts not being cleanly resumable (the underlying turn is
still running), the interrupt-then-drain primitive needed to make any early stop a clean boundary,
and an LLM-judged "overseer" continuation layer — are out of scope for terminology and are recorded
as input to the neutral agent-runner contract decision instead.
