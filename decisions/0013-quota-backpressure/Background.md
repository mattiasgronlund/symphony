# Background — 0013 Provider quota backpressure

## Context

When the underlying provider account is near its usage limit, Symphony should pause taking on *new*
work rather than dispatch runs that will fail or throttle — independently of Symphony's own token
budgets (decision 0012). The spec already TRACKS the latest rate-limit payload (Section 13.5,
`codex_rate_limits`) but acts on none of it. The `Identione` fork demonstrates the missing half: a
normalized provider-quota snapshot, a poller (`quota_collector`) for the out-of-band case, and a
dispatch gate that pauses new dispatch when the account crosses a threshold.

This is an application of class C from decision 0010 (a cached external signal): the authority is an
external, account-wide provider API that not every agent exposes and that is intermittently reachable.
It reports *account totals*, not Symphony-attributed usage, so it MUST stay separate from spend
(decision 0012).

## Options considered

- **Option A — do nothing (keep tracking-only).** Trade-offs: simplest, but leaves a known
  runaway/throttle risk unmanaged; the tracked rate-limit data stays inert. Rejected.
- **Option B — fail-open only (as `Identione` does).** Trade-offs: simple and safe against a wedged
  poller, but cannot pause on a transient block, and holds the snapshot only in memory (lost on
  restart). Rejected as the sole policy.
- **Option C — a class-C signal with a configurable fail-open/closed policy and last-known-good carry
  (chosen).** A dispatch-only gate over a normalized snapshot, fed by either ingestion path.

## Decision and reasoning

Specify provider quota backpressure as an OPTIONAL extension that activates `codex_rate_limits` into a
normalized provider-quota snapshot governed by class C (0010):

- **Normalized snapshot shape.** `provider`, `source`, `fetched_at`, a staleness bound
  (`stale_after_ms`), `buckets` each with a comparable `used_percent` (0–100) and optional `resets_at`,
  and optional `error`. Bucket identity is treated as opaque (vendor bucket names are vendor-specific
  and unstable); the gate only tests "any bucket ≥ threshold".
- **Two ingestion paths, one shape.** In-band (the rate-limit payloads already tracked in Section
  13.5) and an OPTIONAL out-of-band poller against a provider usage API both normalize to the snapshot.
- **Class-C semantics (0010).** Last-known-good is carried across restart and across failed refresh; a
  value older than `stale_after_ms` is promoted to `UNKNOWN`; `UNKNOWN` is distinct from any
  `used_percent` value, including `0`.
- **Dispatch-only gate.** Pause only NEW dispatch when any bucket `used_percent` ≥
  `dispatch_pause_percent`; running agents and reconciliation are untouched. Resume is implicit — the
  gate is re-evaluated each tick, with no dedicated paused state.
- **Configurable unknown policy.** The policy on `UNKNOWN` is configurable (fail-open proceed vs
  fail-closed pause). *Unsupported* (the agent exposes no quota API → permanent UNKNOWN) defaults to
  fail-open, since pausing forever is wrong; *blocked* (transient, e.g. 429/auth) MAY fail-closed.
- **Separation from spend.** Account-wide headroom MUST NOT be summed into Symphony-attributed
  consumed-token totals or budgets (decision 0012).
- **Implementation-defined credentials.** An out-of-band poller's token/credential source and any
  refresh subprocess are Implementation-defined and MUST be documented and bounded.

We would reconsider if providers expose a stable, Symphony-scoped quota (it could then resemble class
D), or if a single ingestion path proves sufficient.
