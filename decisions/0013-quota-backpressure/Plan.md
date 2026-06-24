# Plan — 0013 Provider quota backpressure

## Scope

Adds a new OPTIONAL provider-quota-backpressure extension. Generalizes the rate-limit tracking in
Session Metrics and Token Accounting (Section 13.5) into a normalized quota snapshot, reclassifies
`codex_rate_limits` (Section 4.1.8) to class C, and adds a dispatch gate in the poll/dispatch path
(Sections 8.1, 8.3). Config keys live under the extension's namespace (`quota.*`). Depends on 0010
(class C); kept separate from 0012 (spend).

## Steps

1. Ensure a provider quota backpressure extension is specified as OPTIONAL. Done when the subsection
   exists and is marked OPTIONAL.
2. Ensure a normalized provider-quota snapshot shape is defined: `provider`, `source`, `fetched_at`, a
   staleness bound `stale_after_ms`, `buckets` each with a comparable `used_percent` (0–100) and
   optional `resets_at`, and optional `error`; bucket identity is opaque. Done when the snapshot fields
   are specified.
3. Ensure two ingestion paths feed the same shape: in-band (the rate-limit payloads already tracked in
   Section 13.5 "Rate-limit tracking") and an OPTIONAL out-of-band poller against a provider usage API.
   Done when both paths are specified and unified onto the snapshot.
4. Ensure the snapshot is classified class C (decision 0010): last-known-good carried across restart
   and failed refresh; staleness past `stale_after_ms` promotes it to `UNKNOWN`; `UNKNOWN` is distinct
   from any `used_percent` value including `0`. Done when the class-C cross-reference and the
   UNKNOWN-not-zero rule are present.
5. Ensure the dispatch gate pauses only NEW dispatch when any bucket `used_percent` ≥
   `dispatch_pause_percent`, leaving running agents and reconciliation untouched, with implicit resume
   (re-evaluated each tick; no dedicated paused state). Done when the gate, its scope, and implicit
   resume are specified.
6. Ensure the policy on `UNKNOWN` is configurable (fail-open proceed vs fail-closed pause), with
   *unsupported* (permanent UNKNOWN) defaulting to fail-open and *blocked* (transient) permitted to
   fail-closed. Done when the policy and the unsupported/blocked distinction are specified.
7. Ensure the quota signal is kept separate from Symphony-attributed spend (decision 0012):
   account-wide headroom MUST NOT be summed into consumed-token totals or budgets. Done when the
   separation is stated.
8. Ensure an out-of-band poller's token/credential source and any refresh subprocess are
   Implementation-defined and MUST be documented and bounded. Done when stated.
9. Ensure config keys are specified under `quota.*` with defaults (`enabled` default `false`;
   `dispatch_pause_percent` default `95`; `stale_after_ms` default `180000`; a poller `refresh_ms`).
   Done when the keys and defaults are present.

## Cross-cutting sync

- Config cheat sheet (6.4): note the quota extension owns `quota.*`; document the keys in the extension
  subsection.
- Session metrics (13.5): the "Rate-limit tracking" bullet is generalized to feed the normalized
  snapshot.
- Test matrix (17): add `Extension Conformance` rows under 17.4/17.6 — snapshot normalization across
  providers; dispatch-only pause leaves running agents untouched; `UNKNOWN` is never `0` and
  last-known-good survives restart; fail-open vs fail-closed policy; unsupported vs blocked.
- Checklist (18): add the quota-backpressure extension to 18.2.

## Anchor changes

- `codex_rate_limits` (Section 4.1.8) generalized to a normalized provider-quota snapshot and
  reclassified to class C.
- New anchors: config keys `quota.*`, `dispatch_pause_percent`, `stale_after_ms`; the snapshot fields
  `provider` / `source` / `fetched_at` / `buckets` / `used_percent` / `resets_at`.
- Depends on the `UNKNOWN` sentinel and class C introduced by decision 0010.

## Status

Not started. Decision drafted; not yet applied to `SPEC.md`.
