# Plan — 0015 Neutral agent runner contract

## Scope

Reshapes Section 10 "Agent Runner Protocol (Coding Agent Integration)" from a Codex-app-server-shaped
contract into a turn-centric, transport-neutral one, elaborating decision 0006's Section 10.9.
Affects Section 10.7 "Agent Runner Contract", Section 10.9 "Agent Adapters and Selection", and the
continuation/timeout text in Sections 10.2, 10.3, 10.6, plus the Section 16.5 reference algorithm.
Introduces neutral contract anchors. Does NOT rename the persisted `codex_*` observability fields
(Sections 4.1.6, 4.1.8, 13.5, 13.8.2, 16.x, 7.3) — that is decision 0016. Selection (0006), the broker
(Section 10.8, decisions 0003/0004), and turn/step/run terminology (0014) are unchanged.

## Steps

1. Continuation-reference model. In Section 10.7 "Agent Runner Contract" and Section 10.3 "Streaming
   Turn Processing", ensure the contract threads an explicit, opaque, adapter-owned `continuation_ref`
   across turns: the first turn passes no ref and the full task prompt; each continuation turn passes
   the prior turn's `continuation_ref` and continuation guidance (per 0014). There is no separate
   session-start operation; an adapter establishes whatever underlying session or process it needs
   lazily on the first `run_turn`. Ensure the prose states
   that `continuation_ref` is the contract-level continuation state and that an adapter MAY realize it
   as a warm session handle, a resume token, or declare it non-resumable (see Step 5). Done when
   `continuation_ref` is defined and threaded, and no contract-level text requires a live session to
   persist between turns.

2. Reframe the persistent-session requirement. In Section 10.2 "Session Startup Responsibilities" and
   Section 10.3, ensure the statement that "the app-server subprocess SHOULD remain alive across those
   continuation turns" is scoped as a Codex-adapter realization of holding a warm `continuation_ref`,
   not a core requirement. Done when keeping a process alive across turns is adapter-specific and the
   core requirement is expressed in terms of `continuation_ref`.

3. Cancel with interrupt-then-drain. In Section 10.7 (referenced from Section 10.6 "Timeouts and Error
   Mapping"), ensure a `cancel` operation: every adapter MUST support cancelling an in-flight turn; the
   adapter SHOULD interrupt the turn, drain to the targeted protocol's real terminal envelope within a
   bounded secondary timeout, and yield a resumable `continuation_ref`; if it cannot drain cleanly it
   MUST still terminate, in which case the turn fails (the existing flat-fail behavior). Ensure Section
   10.6 notes that a `turn_timeout` without a clean drain is not safely resumable. Done when `cancel`
   is specified with the drain semantics and the timeout-resumability note is present.

4. Normalized events and token usage as contract outputs. In Section 10.4 "Emitted Runtime Events" and
   Section 10.7, ensure the contract REQUIRES adapters to emit the neutral event vocabulary already
   listed in Section 10.4 and a neutral token-usage record with `input_tokens`, `output_tokens`,
   `total_tokens`, plus an opaque map for adapter-specific extras (for example cache tokens, cost,
   rate-limit payloads); raw protocol payloads are carried opaquely and never exposed as the normalized
   shape. Ensure the text records that the persisted `codex_*` fields are renamed to these neutral
   names by decision 0016. Done when the neutral event + token-usage outputs are REQUIRED at the
   contract and the 0016 dependency is recorded.

5. Capability descriptor (data, not a method). In Section 10.9 "Agent Adapters and Selection", ensure
   each adapter advertises a static capability descriptor covering at least: `resume` mode
   (`warm_session` | `resume_token` | `none`), whether it streams, whether it enforces a native
   per-turn step cap (0014), and its accepted `effort` values (0006). Ensure the prose states the
   orchestrator reads this to drive behavior (e.g. `resume = none` means it re-feeds context or treats
   each turn fresh; a native step cap's breach is a turn boundary, not a failure). Replace 0006's
   "advertise capabilities" responsibility-as-call with this data descriptor. Done when the capability
   descriptor is specified as data and consumed by the orchestrator.

6. Transport below the border. In Section 10.9, ensure the prose states an adapter encapsulates one
   (agent, transport) pairing; two transports for the same agent are two adapters; and an
   implementation MUST NOT require a non-native agent to impersonate another agent's protocol (each
   adapter defers to its own protocol as source of truth, preserving the 0006 / CLAUDE.md boundary).
   Done when (agent x transport) = separate adapters and the no-impersonation rule are stated.

7. Reference algorithm. In Section 16.5 "Worker Attempt (Workspace + Prompt + Agent)", ensure the
   pseudocode threads `continuation_ref` across turns and uses `cancel` on timeout/stall in place of
   the `start_session`/`stop_session` lifecycle, releasing any warm resources when the run ends. Done
   when the reference algorithm reflects the continuation-reference contract.

## Cross-cutting sync

- Config cheat sheet (6.4): no new config keys (the contract is structural). Confirm the `agent.*` /
  `codex.*` entries still align; the `effort` accepted-values pointer remains adapter-owned (0006).
- Test matrix (17.5 "Coding-Agent Adapters"): add rows for `continuation_ref` threading across turns,
  `cancel` + interrupt-then-drain, the capability descriptor, neutral token usage (`input_tokens`,
  `output_tokens`, `total_tokens`), and the no-impersonation rule.
- Checklist (18): add REQUIRED items for the continuation-reference contract and `cancel`; record the
  clean-drain and capability descriptor at their respective RECOMMENDED/REQUIRED levels.

## Anchor changes

- New anchors: `continuation_ref`; the `cancel` operation (interrupt-then-drain); `release` of warm
  resources at run end; the capability descriptor with `resume` (`warm_session` | `resume_token` |
  `none`); the neutral token-usage record fields `input_tokens` / `output_tokens` / `total_tokens`.
- Reframed (not removed): the "app-server subprocess SHOULD remain alive across continuation turns"
  requirement (Sections 10.2, 10.3) becomes a Codex-adapter realization.
- Delegated to decision 0016 (vocabulary sweep): the persisted `codex_*` field rename — `codex_*` token
  fields (Section 4.1.6), `codex_totals` / `codex_rate_limits` (Section 4.1.8), token accounting
  (Section 13.5), `codex_session_logs` (Section 13.8.2), reference-algorithm fields (Section 16.x), and
  the `Codex Update Event` trigger (Section 7.3) — all adopting the neutral `*_tokens` names introduced
  here.

## Status

Accepted — applied to `SPEC.md` (alongside decision 0016): Section 10.7 turn-centric contract with
`continuation_ref` / `cancel` / `release`, Section 10.9 capability descriptor and transport rule, the
Section 10.3 / 10.6 reframing, and the Section 16.5 reference algorithm.
