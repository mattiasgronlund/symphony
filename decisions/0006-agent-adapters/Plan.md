# Plan — 0006 Agent adapters (Codex, Claude Code)

## Scope

Generalizes the Agent Runner Protocol (Section 10) into a neutral contract plus per-agent adapter
sections; the existing Codex content becomes the Codex adapter. Adds agent-selection and effort to
policy config. Generalizes the session identity (Section 4.1.6) and token accounting (Section 13.5)
off Codex-specific shapes. Depends on 0003 (CLI-only broker decouples tools) and 0005 (policy config).

## Steps

1. Ensure Section 10 defines an agent-neutral runner contract (session start, turn run, event stream,
   normalized token usage, capability advertisement) with per-agent adapters deferring to their own
   protocol. Done when the neutral contract exists and Codex is one adapter among at least Codex and
   Claude Code.
2. Ensure agent selection lives in policy config as a per-repo default (agent plus native effort).
   Done when policy config carries the default and the spec states agent choice is operator-owned.
3. Ensure a per-issue override exists via an explicit policy table mapping tracker labels to
   (agent, effort) pairs, where only mapped labels take effect. Done when the mapping table is
   specified.
4. Ensure `effort` is defined as pass-through of the agent's native value, with each adapter
   documenting accepted values. Done when the pass-through semantics are stated.
5. Ensure session identity and token accounting are generalized into the neutral contract, with
   adapters normalizing. Done when `<thread_id>-<turn_id>` and the `codex_*` token fields are
   expressed as adapter-normalized neutral fields.

## Cross-cutting sync

Config cheat sheet (6.4): the `codex.*` block becomes adapter-scoped; add agent-selection and effort
policy keys. Test matrix (17.5) and checklist (18): reframe the "Codex app-server client" rows as
neutral-contract plus per-adapter rows.

## Anchor changes

- `codex` config block and `codex.*` keys (Sections 5.3.6, 6.4) — rescoped under a per-agent adapter
  namespace (the Codex adapter); neutral runner fields replace Codex-specific ones in core.
- Session identity `<thread_id>-<turn_id>` and `codex_*` token fields (Sections 4.1.6, 13.5) —
  generalized to adapter-normalized neutral fields.
- New anchors: the neutral agent runner contract, the agent adapter concept, `effort`, and the
  agent/effort label mapping table.

## Status

Not started. Recorded as `Proposed`; `SPEC.md` not yet edited.
