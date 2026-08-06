# Background — 0056 A configuration-error reason registry and the `usage_or_config` status

## Context

Decision 0053 surfaced this as the most substantive of the three gaps authoring the engine conformance
corpus exposed. `VCSX-SPEC.md` Section 6.10 enumerates five conditions under which the engine refuses
to run, and Section 8.3 maps that refusal to exit code `2` — but names no reason token for any of them.
The `validate_policy` vectors could therefore assert only that *a* configuration error was raised, not
which, which is a weak assertion for the one code path where a caller most needs to know what to fix.

That is a sharp inconsistency in an engine whose entire contract is built on stable tokens. Section 4.3
gives every operation outcome a registry reason with a frozen proto class precisely so a consumer can
branch mechanically instead of parsing prose, and Section 8.3 states the same goal for exit codes — "so
a caller can branch without parsing". Configuration errors were the one outcome class left to
`message`.

Resolving it exposed a second, related defect. Section 8.2 defines `status` as "the invocation's
overall proto class: `ok` ..., `needs_caller`, or `error`" — three values — while Section 8.3 defines
four exit codes, with `2` for a usage or configuration error. **No `status` value corresponds to exit
`2`.** An engine following Section 8.2 literally must report a refused policy as `status: "error"`,
which Section 8.3 maps to exit `20`, contradicting the exit-`2` requirement. The two sections could not
both be satisfied. Section 8.2's `op` / `reason` / `class` sentence has the same shape of problem: it
describes "the decisive operation result", and a policy that never ran has no operation.

## Options considered

### Carrying the cause

- **Option A — a configuration-reason registry, carried in `reason` (chosen).** A stable token per
  condition, reported in the existing envelope `reason` field with `op` and `class` null.
  Trade-offs: reuses the field and the registry pattern the specification already has for operation
  reasons, so a caller reads the cause from where it already reads causes. Costs one new
  `Implementation-defined` site, for which reason is reported when several conditions hold.
- **Option B — leave the cause in `message` and add nothing.** Trade-offs: no surface change. But it
  is the status quo the gap describes, and it makes the one error class a caller most needs to act on
  the only one requiring prose parsing.
- **Option C — a structured `errors` array replacing `reason` for this case.** Report every condition
  found. Trade-offs: strictly more information, and it removes the multiple-conditions ambiguity by
  construction. But it adds a second, differently-shaped error channel to an envelope whose whole
  virtue is one shape, and a caller wanting the simple case must now handle a collection.

### Reconciling the status values

- **Option D — a fourth status value, `usage_or_config` (chosen).** Trade-offs: makes the status →
  exit-code mapping total and keeps Section 8.3's "mirror the status" property literally true. It
  requires reframing Section 8.2's `status` as the invocation's *outcome* — the overall proto class
  for a run that executed the policy, and `usage_or_config` for one that did not — because a refused
  policy has no proto class.
- **Option E — report a refused policy as `status: "error"` and derive exit `2` from the reason.**
  Trade-offs: keeps three status values. But it breaks the property Section 8.3 exists for: a caller
  could no longer branch on status alone, since `error` would map to either `20` or `2` depending on a
  field it would have to parse first.

## Decision and reasoning

Choose **Option A** and **Option D**. Define nine configuration reasons in a Section 6.10 registry —
`unknown_trigger`, `unknown_action`, `unknown_operation`, `unknown_hook`, `duplicate_edge`,
`duplicate_transition`, `base_unresolvable`, `set_state_unbound`, `version_floor_unmet` — and add
`usage_or_config` as a fourth invocation status.

The registry follows Section 4.3's shape because the problem is the same one: a caller needs to branch
on a cause without parsing prose, and the set is closed enough to enumerate and open enough to need an
extension rule. Section 6.10's first condition is deliberately split into four tokens rather than one
`unknown_name`, because the four are found at different points in a policy and repaired differently.
The `unknown_trigger` / `unknown_operation` split is the subtle one and is stated explicitly: Section
6.5 recognizes a trigger only as an `op:reason` form *over a known operation*, so a bad operation in a
trigger is `unknown_trigger`, while `unknown_operation` is the `run_op` argument case.

**Configuration reasons carry no proto class**, and this is worth stating rather than leaving implicit.
A proto class classifies an operation result; a refused policy has none. That also settles how a new
configuration reason is absorbed in a `MINOR` release: not through the `#class` fallback — which has
nothing to fall back on — but through the `usage_or_config` status, which does not change. The
specification now says so, so a consumer knows it never needs a class edge for these.

The status fix is not scope creep; the gap could not be closed without it. A reason token is carried in
an envelope whose `status` field had no value for the case that produces it, so defining the tokens
while leaving `status` three-valued would have produced a registry no conforming engine could report.
Fixing it now is also cheap in a way it will not be later: Section 8.5 makes the status values and the
exit-code mapping major-stable, and decision 0049's engine is not yet written, so there is no
implementation to migrate.

The accepted cost is the new `Implementation-defined` site. A policy can hold several configuration
errors at once, and no useful total order over them exists — document order is brittle, and severity is
not defined. Rather than invent one or pretend the case away, the specification requires an engine to
document its choice and permits reporting several. The corpus deliberately does not exercise it: every
failing vector holds exactly one condition, so each vector's expected reason is determined.

We would reconsider Option C if operator experience showed that one-reason-at-a-time repair loops were
the dominant cost of authoring a policy, at which point reporting all conditions would earn the second
error shape. We would reconsider the token split if the four `unknown_*` reasons proved never to be
handled differently in practice.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 6.10, 8.2, 8.3, 8.5, 13.3), the
vocabulary registry (`config_reasons`, `invocation_statuses`), the corpus
(`policy-validation.json`'s failing vectors now name their reason, and a vector distinguishes
`unknown_operation` from `unknown_trigger`), and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (the new `Implementation-defined` row and a
configuration-reason table). Depends on 0053, which surfaced it; relates to 0044 (Symphony's
engine-invocation failure class, which consumes the refusal this decision makes legible) and to 0051
(the registry the new tokens join).
