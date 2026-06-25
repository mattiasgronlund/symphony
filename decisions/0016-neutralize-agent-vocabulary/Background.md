# Background — 0016 Neutralize agent observability vocabulary

## Context

Decision 0006 created the neutral agent contract but deliberately "retained Codex-specific field
shapes as the Codex adapter's worked example rather than mass-renamed". Decision 0015 then defined the
neutral runner contract and introduced its neutral output types (the event vocabulary, the token-usage
record `{input_tokens, output_tokens, total_tokens}`, `continuation_ref`). What remains is the
mechanical-but-cross-cutting sweep 0006 deferred: the persisted and emitted observability surfaces
still carry `codex_*` names and Codex-worded prose even though they describe any agent.

The fork study (session memory) showed this residue is the single most common real-world leak: even
forks that removed Codex entirely kept `{:codex_worker_update}` / `codex_app_server_pid` and a
Codex-named dashboard/token vocabulary, because the persisted field names anchor everything
downstream. A `codex_*` bleed audit (this session) catalogued the spots: Section 4.1.6 (live-session
fields), Section 4.1.8 (`codex_totals`, `codex_rate_limits`), Section 13.5 (token accounting), Section
16.x (reference-algorithm fields and the `codex_update` channel), Section 7.3 (`Codex Update Event`),
Section 13.8.2 (`codex_session_logs`), and Section 15.5 (Codex-worded hardening prose).

## Scope boundary: what stays "Codex"

This decision renames only names that mean "agent" but say "codex". It does NOT touch genuinely
Codex-adapter-specific anchors, which are correct: the `codex` config block (Section 5.3.6, scoped by
0006), the Codex worked-example adapter text (Sections 10.1-10.8), `codex.command`, and references to
the Codex app-server protocol. Tracker vocabulary (e.g. "Linear" in Section 15.5) is a separate
concern (decision 0008 lineage) and is out of scope. The config-key namespace wart — generic timeouts
living under `codex.*` (`codex.turn_timeout_ms`, `codex.read_timeout_ms`, `codex.stall_timeout_ms`) —
is a config-schema change, not an observability rename, and is left for a separate decision.

## Options considered

- **Leave as worked-example with disclaimers (status quo, 0006).** Cheapest, but the fork evidence
  shows the names themselves are the leak; a one-line "reflects the Codex adapter" caveat does not stop
  every consumer (dashboard, REST API, reference algorithms) from speaking Codex.
- **Rename to a generic neutral scheme (chosen).** The persisted/emitted fields adopt neutral names
  that the Codex adapter (and every other) normalizes into, matching the 0015 contract outputs.
  Adapter-specific extras (cache tokens, cost) live in the opaque extras map from 0015.

## Decision and reasoning (proposed)

Sweep the `codex_*` observability vocabulary to neutral names consistent with the 0015 contract,
keeping Codex-adapter-specific anchors intact. Naming principle: neutral fields are **bare by
default** inside their already-scoped struct, taking a scope qualifier only where signals of different
scope sit together. So the agent-session struct (Section 4.1.6 "Agent Session Metadata") uses bare
names, while the orchestrator runtime map (Section 4.1.8) qualifies by scope — `agent_*` for
Symphony-attributed agent telemetry, `provider_*` for the external provider-account signal. Mapping:

| Current (`codex_*`) | Neutral | Where (hint) |
|---|---|---|
| `codex_app_server_pid` | `pid` | 4.1.6, 13.8.2, 16.x |
| `last_codex_event` | `last_event` | 4.1.6, 13.3 |
| `last_codex_timestamp` | `last_timestamp` | 4.1.6 |
| `last_codex_message` | `last_message` | 4.1.6 |
| `codex_input_tokens` | `input_tokens` | 4.1.6, 16.x |
| `codex_output_tokens` | `output_tokens` | 4.1.6, 16.x |
| `codex_total_tokens` | `total_tokens` | 4.1.6, 16.x |
| `codex_totals` | `agent_totals` | 4.1.8 |
| `codex_rate_limits` | `provider_rate_limits` | 4.1.8, 8.9, 13.5 |
| `codex_update` (channel msg) | `agent_update` | 16.x |
| `Codex Update Event` (trigger) | `Agent Update Event` | 7.3 |
| `codex_session_logs` | `agent_session_logs` | 13.8.2 |

Plus prose neutralization in Section 15.5 ("Running Codex agents" / "Tightening Codex approval and
sandbox settings" / "built-in Codex policy controls" -> agent / the selected adapter's approval and
sandbox settings) and the Section 13.5 framing of Codex payload names as Codex-adapter examples.

State **Accepted** (applied to `SPEC.md`): the naming convention is bare in the session struct, with
`agent_*` / `provider_*` scope qualifiers in the runtime map. Applied alongside decision 0015.
