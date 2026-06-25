# Background — 0019 Neutralize tracker error vocabulary

## Context

Section 11.4's RECOMMENDED tracker error categories were named for the one tracker the spec originally
targeted: `linear_api_request`, `linear_api_status`, `linear_graphql_errors`, `linear_unknown_payload`,
`linear_missing_end_cursor`. The document is now multi-adapter — at least `linear` and `forgejo`, with a
declared write-capability surface (Section 11.1, Section 11.7) — so a `forgejo` (or any future) adapter
inherits error category names that say `linear` and `graphql`, neither of which it uses.

The 22-fork tracker sweep (0008 `Background.md`; `adapter-layer-fork-evidence` memory) flagged this as the
tracker-side instance of the same naming bleed decision 0016 fixed on the agent side (`codex_*` → neutral):
the clean forks neutralized these categories, and the Rust ports modelled them as a closed, transport-neutral
`TrackerError` enum (with structured `RateLimited{reset_at}`). This is the symmetric, mechanical cleanup.

## Options considered

- **Leave the `linear_*` names.** Rejected: a leak that contradicts the multi-adapter contract and the
  precedent set by 0016.
- **Keep `linear_*` and add `tracker_*` aliases.** Rejected: redundant; two names for one category invites
  drift and gives no adapter a clean home.
- **Rename the core categories to transport-neutral `tracker_*`; demote the Linear/GraphQL specifics to an
  example (chosen).** The categories describe failure *kinds* that any adapter hits; the GraphQL-over-HTTP
  detail is the Linear adapter's mapping onto them, captured as a `Note:`.

## Decision and reasoning

Rename the five categories and keep them transport-neutral:

- `linear_api_request` -> `tracker_api_request` (transport or connection failure)
- `linear_api_status` -> `tracker_api_status` (unsuccessful response status, for example non-2xx HTTP)
- `linear_graphql_errors` -> `tracker_backend_errors` (backend-reported errors in a well-formed response,
  for example a GraphQL `errors` array)
- `linear_unknown_payload` -> `tracker_payload_invalid` (unexpected or unparseable response payload)
- `linear_missing_end_cursor` -> `tracker_pagination_error` (pagination integrity failure, for example a
  missing continuation cursor)

A `Note:` records how the Linear adapter (GraphQL over HTTP) maps its failures onto the neutral categories,
so the Linear specifics survive as an example rather than as the contract's vocabulary. This sits beside the
already-neutral `tracker_unsupported_operation` (decision 0018), giving Section 11.4 one consistent
`tracker_*` namespace.

Scope: Section 11.4 category names plus the `Note:`, and the Section 17.3 "Error mapping" test row. The two
remaining `linear_` tokens elsewhere in the spec are genuinely Linear-specific and are left unchanged: the
retired `linear_graphql` client-side tool name (a historical reference, Sections 10.5/10.8) and the
`~/.linear_api_key` example bootstrap path (Section 15.x). No other references to the five codes exist.

Mirrors decision 0016 (agent `codex_*` neutralization); same rationale, the tracker side.
