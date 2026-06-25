# Background — 0015 Neutral agent runner contract

## Context

Decision 0006 established a neutral agent runner contract plus per-agent adapters but, by its own
Plan's Status note, "retained Codex-specific field shapes as the Codex adapter's worked example
rather than mass-renamed" and left the contract thin: Section 10.9 lists it as five responsibility
bullets (start a session, run a turn, report completion, expose identity + usage, advertise tools).
Two later inputs show that thin contract is both under-specified and, in one place, wrong:

1. A `codex_*` bleed audit (this session) found Codex-shaped names and assumptions throughout the
   nominally-neutral layer (Sections 4.1.6, 4.1.8, 13.5, 16.x, 7.3, 13.8.2, 15.5, 17.5).
2. A study of ~24 `openai/symphony` forks that swapped or added a non-Codex agent backend (recorded
   in session memory) revealed what a contract that survived multiple real implementations actually
   looks like — and where Section 10's current shape leaks.

This decision elaborates 0006's contract into a concrete, transport- and agent-neutral shape, and
corrects the one place the current text bakes in a Codex assumption. It deliberately does NOT do the
full observability rename (the `codex_*` field sweep); that mechanical sweep is delegated to a
follow-on decision (0016) so this one stays reviewable. Agent *selection* (0006), the
privileged-operation broker (Sections 10.8, decisions 0003/0004), and the turn/step/run terminology
(0014) are unchanged and cross-referenced.

## What the fork study established

- **The parent has no agent behaviour.** `openai/symphony` abstracts the tracker (a 5-callback
  behaviour) but hardwires Codex in `agent_runner.ex` (`run(issue, codex_update_recipient, opts)`).
  Section 10 inherits exactly this asymmetry.
- **A convergent contract exists.** Four independent forks (a Python ABC, a Go `Runtime`, an Elixir
  `Agent` behaviour, an ACPx wrapper) converged on: run a turn given (workspace, prompt, issue, event
  sink), plus a neutral event vocabulary and a neutral token-usage record `{input, output, total}`,
  with raw protocol payloads carried opaquely.
- **The persistent-session assumption is the main leak.** The modal `start_session` -> `run_turn` ->
  `stop_session` triad assumes a live session that survives across turns — a Codex app-server
  property, not a universal one. CLI/PTY adapters expose it: `smithy` makes `start_session` /
  `stop_session` no-ops; `odyssey` kept them and shipped a latent multi-turn-memory bug (it never
  threaded the resume id back); `rondo` rejected the triad outright for `invoke(prompt, workspace,
  previous_run_ref, on_event)` with a serializable continuation token. Continuation belongs in an
  explicit, opaque token, not an implied live handle.
- **Capability is advertised as data, not a method.** No simple fork implemented 0006's "advertise
  capabilities" as a contract call; the sophisticated ones (`rondo` `capabilities()`, `fifony`
  `ProviderCapabilities`) expose it as a static descriptor.
- **Transport sits below the border.** Two transports for one agent are two adapters (`gaspardip`
  `codex` vs `codex_cli` are sibling copy-pasted modules). Forcing a non-native agent to impersonate
  another's wire protocol (`ant1m4tt3r` and `moonshot` make Claude speak Codex JSON-RPC) is a
  recognised anti-pattern, explicitly flagged "not recommended" by one fork's own design notes.
- **An interrupt-then-drain primitive is missing.** The Identione overseer note (decision 0014's
  refinement) shows a wall-clock turn timeout abandons a still-running turn, so the session is not
  cleanly resumable (late envelopes of the abandoned turn desync as the next turn's). Making any
  early stop a clean boundary needs: signal stop, drain to the real terminal envelope within a
  bounded secondary timeout, then yield an idle, resumable state.

## Options considered

### Contract shape
- **Keep the persistent-session triad (status quo / modal convention).** Least change, but bakes the
  Codex app-server assumption into core and forces CLI adapters into no-ops or bugs.
- **Pure stateless invoke + token (rondo).** Honest for CLI agents, but discards the warm-session
  optimisation persistent app-servers depend on (prompt-cache reuse, lower latency).
- **Continuation-reference model (chosen).** The contract is turn-centric and threads an explicit,
  opaque, adapter-owned `continuation_ref`; a persistent app-server is then just one adapter whose
  ref resolves to a warm handle, and a per-invocation CLI another whose ref is a resume token (or
  declares non-resumable). Fits both without no-ops, bugs, or discarding warm sessions.

### Capability advertisement
- **A contract method** — no fork did this; over-abstract. **A static data descriptor (chosen)** —
  matches `rondo`/`fifony`; the orchestrator reads `resume` mode, streaming, native step cap, and
  accepted `effort` values to drive behavior.

### Early-stop / cancel
- **Flat fail (status quo)** — a timeout fails the worker attempt and retries; safe but discards a
  recoverable session and cannot support clean mid-turn intervention. **Interrupt-then-drain (chosen;
  REQUIRED to cancel, RECOMMENDED to drain cleanly)** — enables clean boundaries for timeouts,
  budgets (0012), and a future overseer, with flat termination as the documented fallback.

### Observability vocabulary
- **Rename `codex_*` here** — would balloon this decision into a cross-document sweep. **Define the
  neutral types at the contract and delegate the field sweep to 0016 (chosen)** — keeps 0015
  reviewable; 0016 adopts the neutral `*_tokens` names introduced here.

## Decision and reasoning

Elaborate 0006's neutral runner contract into a turn-centric contract with: an explicit opaque
`continuation_ref` (replacing the "keep the subprocess alive across continuation turns" requirement,
which becomes a Codex-adapter realization); a REQUIRED `cancel` with RECOMMENDED interrupt-then-drain
to a resumable state; normalized events (the Section 10.4 vocabulary) and a neutral token-usage record
`{input_tokens, output_tokens, total_tokens}` plus an opaque extras map as the contract's outputs;
capability advertised as a static descriptor; and the rule that an adapter encapsulates one (agent,
transport) pairing and MUST NOT impersonate another agent's protocol. Selection (0006) and the broker
(0003/0004) are unchanged. The `codex_*` storage-field rename is delegated to 0016.

We would reconsider if a real adapter could not express its continuation as an opaque ref (none seen),
or if requiring `cancel` proved infeasible for some agent (process termination is the universal
fallback).

Open points resolved (this session): (a) there is no separate `prepare`/`start` operation — session
establishment is folded into the first `run_turn`, which an adapter performs lazily (a persistent
app-server launches its process on turn one); (b) the continuation token is named `continuation_ref`;
(c) the 0015 (contract) / 0016 (vocabulary sweep) split is confirmed. State moved to **Accepted**;
application to `SPEC.md` is still pending (see Plan `Status`).
