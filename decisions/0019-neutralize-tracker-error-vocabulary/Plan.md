# Plan — 0019 Neutralize tracker error vocabulary

## Scope

Renames the five `linear_*` error categories in Section 11.4 "Error Handling Contract" to transport-neutral
`tracker_*` names and records the Linear adapter's mapping as a `Note:`. Neutralizes the Section 17.3
"Error mapping" test row. No config, behavior, or other sections change.

## Steps

1. In Section 11.4, ensure the error-category list uses the neutral names — `tracker_api_request`,
   `tracker_api_status`, `tracker_backend_errors`, `tracker_payload_invalid`, `tracker_pagination_error` —
   and no longer lists any `linear_*` category. Ensure the list is introduced as transport-neutral. Done
   when no `linear_*` token remains in Section 11.4.

2. Ensure Section 11.4 carries a `Note:` mapping the Linear (GraphQL-over-HTTP) adapter's failures onto the
   neutral categories (non-2xx -> `tracker_api_status`, GraphQL `errors` array -> `tracker_backend_errors`,
   missing page cursor -> `tracker_pagination_error`). Done when the Note is present.

3. Ensure the Section 17.3 "Error mapping" row no longer names `non-200`/`GraphQL errors` transport
   specifics and instead refers to the neutral failure kinds (Section 11.4). Done when the row is neutral.

## Cross-cutting sync

- Section 6.4 cheat sheet: no change (error categories are not config fields).
- Section 18 checklist: no change (it does not enumerate tracker error codes).

## Anchor changes

- `linear_api_request` -> `tracker_api_request`
- `linear_api_status` -> `tracker_api_status`
- `linear_graphql_errors` -> `tracker_backend_errors`
- `linear_unknown_payload` -> `tracker_payload_invalid`
- `linear_missing_end_cursor` -> `tracker_pagination_error`

## Status

Applied to `SPEC.md`.
