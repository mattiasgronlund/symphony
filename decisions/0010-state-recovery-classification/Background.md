# Background — 0010 State recovery model and class taxonomy

## Context

A survey of downstream Symphony forks that bound or optimize token spend (token-budget guards,
per-agent budgets, cost/spend modules, provider quota-aware dispatch pausing, per-issue usage
ledgers) surfaced a class of state the current spec cannot place. While planning those extensions we
found `SPEC.md` already takes an explicit recovery stance, resolved entirely to one pole:

- Section 7.4 "Idempotency and Recovery Rules": restart recovery is "tracker-driven and
  filesystem-driven (without a durable orchestrator DB)".
- Section 14.3 "Partial State Recovery (Restart)": scheduler state is "intentionally in-memory"; retry
  timers, running sessions, and live worker state do not survive a restart.
- Section 16.1 "Service Startup": every Orchestrator Runtime State field is initialized empty/zero/null
  (`codex_totals` → zeros, `codex_rate_limits` → null, `retry_attempts` → empty).

So Symphony today has, in effect, a **two-class** model with **zero durable state**: every field is
either reconstructable from an external source of truth (tracker state, git/branch/PR, workspace) or
reset-and-lossy (re-derived as zero/null at startup, harmlessly). The implicit question "persist or
recreate?" is answered "always recreate".

The new extensions break that binary. Their counters are **neither** safely reconstructable **nor**
safely lossy: cumulative Symphony spend cannot be recovered from the tracker or git (not
reconstructable), and resetting it to zero on restart hands a partially-spent issue a fresh full
budget (the concrete bug observed in the `odyssey` fork, which persists per-issue totals but never
re-seeds the per-agent cap on restart). That is the first state that forces a durable class.

The decisive distinction underneath all of this is one the two-class model hides: **"account totals"
vs "Symphony-attributed totals"**. They are different quantities with different sources *and*
different unknown-value semantics:

- Symphony-attributed usage is derived internally by summing per-session token reports (Section 13.5).
  The authority is us; loss is a correctness bug.
- Account / provider headroom is fetched from an external, account-wide provider API (it reflects all
  usage on the account, not just Symphony), is not exposed by every agent, and is intermittently
  reachable (rate-limited, auth-expired). It may legitimately be *unknown*, and "unknown" must not be
  modeled as "0% used".

## Options considered

- **Option A — keep the two-class model; forbid durable state.** Trade-offs: simplest, preserves the
  current stance verbatim. But it forces every spend/quota extension either to re-fetch values that
  have no external source (impossible for Symphony-attributed spend) or to accept incorrectness on
  restart (fresh budget). Rejected: it makes correct budgeting unspecifiable.
- **Option B — add one "persisted" class for everything not reconstructable.** Trade-offs: admits
  durability but lumps account headroom (external, may be UNKNOWN, wants a fail-open/closed policy and
  last-known-good carry) together with Symphony accounting (internal, must-be-correct, idempotent
  re-seed). Too coarse — it cannot express the last-known-good and explicit-UNKNOWN machinery the
  external signal needs.
- **Option C — a four-class taxonomy with a per-field classification obligation (chosen).** Classes
  R (Reconstructable), E (Ephemeral), C (Cached external signal), D (Durable). Every Orchestrator
  Runtime State field is assigned exactly one class with an explicit restart/unknown contract.

## Decision and reasoning

Adopt the four-class taxonomy as a cross-cutting invariant and classify every field of the
Orchestrator Runtime State (Section 4.1.8):

- **R — Reconstructable.** Authoritative source of truth lives outside the orchestrator
  (tracker/git/workspace); rebuilt by reconciliation. MUST NOT be primary-persisted (avoid divergence
  from the source of truth). This is the spec's default and stays the default.
- **E — Ephemeral.** No external source, but loss is harmless or self-correcting; reset at startup.
  MUST document the reset consequence (e.g. retry backoff restarts; observability counters restart
  from zero).
- **C — Cached external signal.** Authority is an external, account-wide, intermittently-reachable
  provider API. MUST carry last-known-good across restart *and* across failed refresh; carry a
  staleness age; represent never-known/too-stale as an explicit `UNKNOWN` sentinel distinct from any
  in-band value (never `0`); and apply a configured policy on `UNKNOWN` (fail-open proceed vs
  fail-closed pause new dispatch). MAY distinguish *unsupported* (permanent UNKNOWN; fail-open is the
  only sane default) from *blocked* (transient UNKNOWN; fail-closed permitted).
- **D — Durable.** Symphony-attributed accounting with no external source where loss is harmful. MUST
  be persisted with an idempotent, re-seedable contract, restored *before* any enforcement read, keyed
  by absolute snapshot (not additive). MUST document degradation when no store is configured.

This admits class D as a **narrow, OPTIONAL exception** to the "no durable orchestrator DB" stance —
durable accounting only; R and E remain the default character of the service, and D is degradable
(durability stays an opt-in extension, mirroring the forks, all of which gate it behind a persistence
mode). It also explicitly **walks back an over-broad "fail-open everywhere" reading**: fail-open is
right for unsupported signals and observability, but for an enforcement signal the operator may want
fail-closed, which is only expressible because `UNKNOWN` is first-class.

Immediate consequences the taxonomy forces:

- `codex_rate_limits` is reclassified from implicit-E to **C**: `null` must mean UNKNOWN, not 0%, and
  it wants last-known-good plus a pause policy (the substrate for decision 0013).
- `codex_totals` is **E** for observability but becomes **D** the moment a budget enforces on it
  (decision 0012) — and that copy must be Symphony-attributed, never account-wide.
- `retry_attempts` / retry timers stay **E**, now as a *defended* choice (consequence: backoff
  restarts), not an accident.

This decision is the shared prerequisite for the per-execution ledger (0011, the recommended
realization of class D), token budget guards (0012, an application of D), and provider quota
backpressure (0013, an application of C). It also clarifies the open item in Section 18.2 ("Persist
retry queue and session metadata across process restarts"): the retry queue is E by decision; session
accounting becomes D only under an enforcement extension.

We would reconsider if no enforcement/quota extension is ever adopted (classes C and D go unused and
the service can remain two-class), or if a durable store ever becomes mandatory rather than the narrow
optional exception scoped here.
