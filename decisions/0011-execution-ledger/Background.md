# Background — 0011 Per-execution durable ledger

## Context

Several planned extensions want the full token/usage history of a single execution: token budget
guards (0012) need a durable, re-seedable cumulative spend; provider quota work (0013) and operators
debugging an expensive or looping run want the per-turn timeline; cost attribution wants per-session
totals. Separately, decision 0010 introduces class D (Durable) and requires Symphony-attributed
accounting to be persisted with an idempotent, re-seed-before-enforcement contract.

An append-only ledger, summarized by a high-water mark per `(issue, session)`, is simultaneously both
things: the per-execution history surface *and* the natural realization of class D — replaying it
yields the cumulative total, and taking the maximum per session makes repeated appends (live updates,
reconnects, final snapshots, retries) idempotent. The fork survey shows convergence on this shape:
the `igor-im` fork ships an append-only JSONL ledger keyed by `(issue_identifier, session_id)` and
summarized by high-water mark; `odyssey` uses SQLite session/issue/daily rollups; `niasand` emits
per-run usage to a notification sink. Each independently arrived at "absolute snapshots, summarize by
max, never sum every event".

Earlier in this work the ledger was dismissed as "minor observability" and folded into the abstract
class-D requirement. That under-weighted the per-execution history, which is a primary deliverable in
its own right and is reusable across all of the spend-control extensions.

## Options considered

- **Option A — keep durability abstract (a plain durable counter); add no ledger.** Trade-offs:
  smallest surface, but there is no per-execution history and each enforcement extension reinvents its
  own persistence. Rejected: loses the history value and the natural idempotency.
- **Option B — mandate the ledger as THE class-D durability mechanism.** Trade-offs: gives history and
  idempotency for free, but over-couples — it forces one storage shape onto conformance and makes a
  simple durable counter non-conforming. Rejected.
- **Option C — define the ledger as an OPTIONAL extension that is the RECOMMENDED realization of class
  D, while class D's contract stays abstract (chosen).** A non-ledger durable counter still conforms;
  implementations that want history get it from the same artifact that satisfies D.

## Decision and reasoning

Specify a per-execution usage ledger as an OPTIONAL extension under observability (Section 13):

- Append-only and durable, keyed by `(issue_identifier, session_id)`; entries record absolute token
  snapshots (consistent with the Section 13.5 accounting rules), not deltas.
- Entry schema at the Section 13.5 altitude: `schema_version`, `observed_at`, `final`, `issue_id`,
  `issue_identifier`, `session_id`, `turn_count`, `input_tokens`, `output_tokens`, `total_tokens`,
  `source_event`; `issue_identifier` and `session_id` are REQUIRED for a valid entry.
- Read/summarize rule: take the maximum `total_tokens` per `(issue_identifier, session_id)` (the
  high-water mark), then sum across sessions; never sum every observed entry. This is what makes
  appends idempotent under retries, reconnects, and the end-of-session snapshot.
- It is named the RECOMMENDED realization of class-D durability (0010): replaying the ledger re-seeds
  enforcement counters idempotently — but D's abstract contract still admits non-ledger stores.
- I/O is non-fatal: write failures MUST log and continue (never crash orchestration); readers MUST
  tolerate and skip truncated/garbage/unknown-`schema_version` lines (a torn final line is normal for
  an append-only file).
- Observability-first: the core schema carries no pricing/cost/`model` field. A note records that
  post-hoc cost attribution would require a `model` field, so omitting it is a deliberate boundary
  (mirroring `igor-im`'s "not a billing surface" stance), not an oversight.
- The extension owns its config (storage location, retention) under its own namespace.

This realizes the Section 18.2 TODO "Persist ... session metadata across process restarts". We would
reconsider the boundary if billing/cost attribution becomes a goal (then revisit adding a `model`
field and a stronger durability bar), or if no enforcement extension is ever adopted (the ledger then
stays pure observability and could be trimmed).
