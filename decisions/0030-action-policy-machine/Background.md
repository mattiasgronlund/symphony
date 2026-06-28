# Background — 0030 The action-policy machine

## Context

Symphony's orchestration logic had accumulated three overlapping shapes: the tracker transition graph
(decision 0017: trigger → tracker state), the positional lifecycle hooks (decision 0026:
`before_*`/`after_*` as a separate axis), and ad-hoc handling of VCS operation outcomes (non-fast-
forward, conflicts, rate limits). Holding these as separate mechanisms produced redundancy — e.g. an
`after_push` hook and a "push succeeded → do X" rule are the same thing expressed twice — and left two
gaps:

- **Unknown outcomes.** A config cannot enumerate every operation error code; new engine/adapter
  versions invent new ones. There must be a way to handle "any other error" without listing them.
- **Silent drops.** An operation outcome with no matching rule must not vanish; that would strand a
  run. (By contrast, an unmatched *milestone signal* doing nothing is correct — decision 0017.)

A further requirement from decision 0028: interactive `ship`/`land` and the daemon must run the
**same** executor, so the machine must express what is shared (the WoW flow) separately from what is
per-front-end (who resolves an escalation).

## Options considered

- **Option A — Keep three mechanisms.** Trade-offs: each is individually simple, but they overlap and
  drift, and none covers the unknown-outcome / no-silent-drop gaps uniformly. Rejected.

- **Option B — One `(trigger) → (action)` machine (chosen).**
  - **Triggers:** lifecycle positions (`before:commit`, `before:push`, `before:create_pr`,
    `before:merge`), typed operation results (`push:ok`, `push:non_fast_forward`,
    `integrate:merge_conflicts`, …), and task-state events (decision 0031).
  - **Actions:** `run_op` (an engine primitive), `run` (a hook command), `escalate` (abstract; bound
    per front-end), `create_task`, `set_state`, `notify`, `park`, `fail`.
  - **Hooks are policy edges**, not a separate axis: `after_push` becomes the `push:ok` edge, etc.
  - **Matching is most-specific-wins with `#class` fallback** over the engine proto's outcome classes
    (`done` / `needs_caller` / `error`): `push:non_fast_forward` → `push:#needs_caller` →
    `push:#error` → `#error` → built-in default.
  - **Two unmatched policies:** an unmatched *signal* is a benign no-op (decision 0017's rule); an
    unmatched *operation outcome* is **fail-safe** — park/fail and surface the proto reason, never
    silent.
  - **Abstract `escalate`** names the *need* ("resolution required"); the front-end binds the
    *resolver* (daemon → an agent task; interactive → return the typed result to the human).

## Decision and reasoning

Choose **Option B**. One machine subsumes the three shapes: decision 0017's transitions become one
binding of `set_state`; decision 0026's positional hooks become trigger names (the four `before_*` /
`after_*` positions persist as triggers, so 0026's intent is preserved while its separate axis is
superseded). The `#class` fallback means a config need not enumerate every code — only the **classes**
are stable — so the outcome vocabulary can grow without breaking configs; this makes the
"covers any thinkable WoW" property robust over time. The fail-safe default closes the silent-drop
gap. Abstract `escalate` is what lets the *same* WoW expression run under both front-ends (decision
0028), with only the resolver differing.

A consequence to record in the engine's reason-token contract: **the proto class of each reason token
becomes part of the public contract**, because configs branch on it via the `#class` fallback.

We would reconsider if the single machine proves too coarse for a particular surface, or if a useful
trigger/action cannot be expressed within it.

The decision is **Accepted** (dependencies 0027 and 0028 are Accepted); the corresponding `SPEC.md`
change is **not** made yet — application is deferred (see `Plan.md` Status). Generalizes decision 0017
(which stays Accepted); supersedes the positional-hook axis of decision 0026, which moves to the
`Superseded` state introduced by decision 0033 (positions kept as triggers, trust classification
preserved).
