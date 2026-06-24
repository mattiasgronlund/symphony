# Background — 0012 Token budget guards

## Context

The motivating survey was specifically about forks that bound or optimize token spend, and the most
direct of those add token-budget enforcement: `orocsy` runs a live cumulative cap in the worker loop
that parks the issue with a correction file on breach; `odyssey` adds per-agent (per-role) caps that
abort and requeue, plus global daily/weekly caps that pause dispatch; `digitaldrywood/symphony-elixir`
runs per-issue and per-day caps. `SPEC.md` has no budget or cap concept today — it measures and
exposes tokens (Section 13.5) but never acts on them.

Budget enforcement is an application of class D from decision 0010 (cumulative Symphony-attributed
spend is durable) and is the primary consumer of the ledger from decision 0011 (re-seed the counter by
replay).

Three things in this area genuinely need normative text, because implementations get them wrong
otherwise:

- **Two distinct exhaustion semantics, not one number.** A per-session/per-issue cap and a global cap
  fail differently: the former aborts and requeues the *single* issue (throughput preserved); the
  latter pauses *new dispatch* as a circuit breaker while in-flight runs continue. Different blast
  radius, different config owner.
- **A dedicated failure class kept out of the retry path.** `orocsy` classifies a budget breach as its
  own category and parks the issue with a correction, deliberately not feeding it into exponential
  backoff. Treating a budget breach as a generic worker failure would retry straight back into the
  cap.
- **Idempotent resume (the class-D contract).** The counter MUST be re-seeded from durable spend before
  enforcing, and re-applying a usage report MUST be idempotent (keyed by absolute snapshot). Without
  this, a crash mid-issue grants a fresh full budget — the exact `odyssey` gap.

## Options considered

- **Option A — a single cap number.** Trade-offs: minimal, but conflates the two exhaustion semantics
  and cannot express "pause the account vs abort the issue". Rejected.
- **Option B — per-session + per-issue + global caps, with distinct semantics, a distinct failure
  class, and durable counters (chosen).** Token is the unit of account.
- **Cost/currency overlay now vs later.** `symphony-elixir` budgets in dollars via a per-model pricing
  table (tokens priced at read time). Considered and **deferred**: pricing adds real burden (stale
  rates, currency, and unknown-model → silent \$0 fail-open) and a token-native cap is the load-bearing
  primitive. Captured here as a future layer rather than built now.

## Decision and reasoning

Specify token budget guards as an OPTIONAL extension, token as the unit of account:

- **Scopes and exhaustion semantics.** Per-session and per-issue caps, on breach, abort the run and
  requeue that single issue. A global cap (e.g. a daily/rolling window), on breach, pauses new dispatch
  while in-flight runs continue (a dispatch gate composing with Section 8.3 concurrency: a paused scope
  yields zero new slots).
- **Failure class.** Budget exhaustion is its own failure category (`token_budget_exceeded`) routed to
  a park/blocked state and kept OUT of the Section 8.4 exponential-retry/backoff path.
- **Soft warning.** Each cap MAY carry a soft warning threshold (`*_warning_pct`, default `80`) that
  emits a one-shot warning signal.
- **Durable, idempotent counters (class D, 0010).** Counters are re-seeded from durable spend (or the
  0011 ledger) before any enforcement decision, idempotent under restart, keyed by absolute snapshot.
- **Tripwire, not pre-authorization.** Caps are evaluated against observed cumulative usage and may
  overshoot by one report; estimate-based pre-authorization (the `symphony-elixir` p50 gate) is noted
  as a separate advisory option, not required here.
- **OPTIONAL constrained recovery.** On a cap breach the implementation MAY retry once through a narrow
  handoff iff fresh local progress exists, else park; a second breach without new progress parks
  terminally (the `orocsy` token-budget-handoff pattern). This avoids discarding nearly-finished work
  while still bounding cost.

The account-wide provider quota signal is explicitly a *different* quantity (decision 0013, class C)
and MUST NOT be summed into Symphony-attributed spend.

We would reconsider if cost-based budgeting becomes a requirement (promote the deferred pricing
overlay to a sub-decision with an explicit missing-pricing policy), or if pre-authorization is wanted
over the tripwire model.
