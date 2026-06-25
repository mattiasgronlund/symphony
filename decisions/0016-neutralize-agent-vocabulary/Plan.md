# Plan — 0016 Neutralize agent observability vocabulary

## Scope

A cross-document rename of `codex_*` observability anchors to neutral names (per the mapping in
`Background.md`), consistent with decision 0015's contract outputs. Touches Sections 4.1.6, 4.1.8,
13.3, 13.5, 13.8.2, 16.x, 7.3, 15.5, and the cross-cutting surfaces (6.4, 17, 18). Depends on decision
0015 (which introduces the neutral `input_tokens` / `output_tokens` / `total_tokens` record the token
fields adopt). Leaves Codex-adapter-specific anchors (Section 5.3.6 `codex` block, Sections 10.1-10.8
worked example, `codex.command`) unchanged.

## Steps

1. Live-session fields. In Section 4.1.6 "Live Session (Agent Session Metadata)", ensure the fields are
   renamed to bare names (the struct is already agent-scoped): `codex_app_server_pid` -> `pid`,
   `last_codex_event` -> `last_event`, `last_codex_timestamp` -> `last_timestamp`, `last_codex_message`
   -> `last_message`, `codex_input_tokens` / `codex_output_tokens` / `codex_total_tokens` ->
   `input_tokens` / `output_tokens` / `total_tokens`. Ensure the "worked example" caveat is updated to
   state these are the neutral logical fields each adapter normalizes into (0015), not Codex shapes.
   Ensure any running-row snapshot surface that mirrors these fields (e.g. Section 13.3) follows. Done
   when no `codex_*` field name remains in 4.1.6.

2. Runtime-state fields. In Section 4.1.8 "Orchestrator Runtime State", ensure `codex_totals` ->
   `agent_totals` and `codex_rate_limits` -> `provider_rate_limits`, with their recovery-class
   annotations (0010) preserved. Done when both fields are renamed and 4.1.8 has no `codex_*` name.

3. Rate-limit references. Ensure every reference to `codex_rate_limits` outside 4.1.8 — Section 13.5
   "Session Metrics and Token Accounting" (rate-limit tracking) and Section 8.9 "Provider Quota
   Backpressure" (decision 0013) — uses `provider_rate_limits`. Done when `codex_rate_limits` appears
   nowhere in SPEC.md.

4. Token-accounting prose. In Section 13.5, ensure the Codex payload names (`thread/tokenUsage/updated`,
   `total_token_usage`, `last_token_usage`) are framed explicitly as Codex-adapter examples, and the
   neutral totals use `input_tokens` / `output_tokens` / `total_tokens` (0015). Done when 13.5
   distinguishes the neutral record from the Codex example payloads.

5. Reference algorithms. In Sections 16.4 "Dispatch One Issue" and 16.5 "Worker Attempt", ensure the
   pseudocode fields are renamed (`codex_app_server_pid` -> `agent_pid`, `codex_input_tokens` etc. ->
   `input_tokens` etc.) and the `codex_update` channel message -> `agent_update`. (Section 16.5 is also
   restructured by 0015 for `continuation_ref` / `cancel`; these renames compose with that.) Done when
   no `codex_*` token/field/channel name remains in Section 16.

6. Transition trigger. In Section 7.3 "Transition Triggers", ensure the `Codex Update Event` trigger is
   renamed `Agent Update Event` (consuming `agent_update`). Done when 7.3 uses the neutral trigger name.

7. REST API. In Section 13.8.2 "JSON REST API (`/api/v1/*`)", ensure the response field
   `codex_session_logs` -> `agent_session_logs` and any illustrative `codex` path segment is marked
   implementation-defined rather than normative. Done when the API field is neutral.

8. Security prose. In Section 15.5 "Harness Hardening Guidance", ensure Codex-worded phrasing ("Running
   Codex agents", "Tightening Codex approval and sandbox settings", "built-in Codex policy controls") is
   neutralized to the agent / the selected adapter's approval and sandbox settings. Leave the tracker
   ("Linear") wording for the tracker-vocabulary decision. Done when 15.5 carries no agent-specific
   "Codex" wording.

## Cross-cutting sync

- Config cheat sheet (6.4): no field renames (the renamed names are state/observability, not config).
  Confirm no cheat-sheet entry references a renamed `codex_*` state field.
- Test matrix (17) and checklist (18): update any row referencing a renamed field (e.g. token fields,
  `Codex Update Event`) to the neutral name; keep Codex-adapter-specific rows (e.g. `codex.command`)
  intact.

## Anchor changes

- Renames (old -> new): `codex_app_server_pid` -> `pid`; `last_codex_event` -> `last_event`;
  `last_codex_timestamp` -> `last_timestamp`; `last_codex_message` -> `last_message`;
  `codex_input_tokens` -> `input_tokens`; `codex_output_tokens` -> `output_tokens`; `codex_total_tokens`
  -> `total_tokens`; `codex_totals` -> `agent_totals`; `codex_rate_limits` -> `provider_rate_limits`;
  `codex_update` -> `agent_update`; `Codex Update Event` -> `Agent Update Event`; `codex_session_logs`
  -> `agent_session_logs`.
- Unchanged (intentionally): the `codex` config block and `codex.command` / `codex.*` keys (Section
  5.3.6, Codex adapter), the Codex worked-example adapter (Sections 10.1-10.8), Codex app-server
  protocol references.
- Note: decision 0013's `codex_rate_limits` anchor is renamed here to `provider_rate_limits`; 0013's
  decision docs remain as history (append-only) and SPEC.md is the source of truth for the current name.

## Status

Accepted — applied to `SPEC.md` (alongside decision 0015). All `codex_*` observability tokens renamed
per the mapping; no `codex_*` field name remains, and the Codex-adapter anchors are unchanged.
