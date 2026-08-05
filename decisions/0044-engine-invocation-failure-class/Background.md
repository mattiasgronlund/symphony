# Background — 0044 Engine invocation failure class

## Context

`VCSX-SPEC.md` Section 8.5 gives the consumer a `version_floor`: "an engine below the floor refuses to
run (fail-closed) with a usage/config result rather than mis-executing a policy that assumes newer
surface." Section 8.3 makes that outcome distinct in the subprocess encoding — exit code `2`, "usage
or configuration error; **the policy did not run**" — beside `0` (`ok`), `10` (`needs_caller`) and
`20` (`error`).

`SPEC.md` has nowhere to put it. Section 14.1's failure classes cover workflow/config, repository
provisioning, workspace, agent session, tracker, and observability failures, plus two OPTIONAL remote
classes; none names the engine. So the consumer-side half of the version-pin contract — the half
Symphony owns — has no classification and no recovery behavior in Section 14.2, and Section 18.1's
engine group requires a conforming engine without saying what happens when the one present is not.

The gap is narrower than "engine failures" in general, and the narrowness is the point. Once the
policy runs, every operation outcome already has a home: the action-policy machine (Section 9.12)
matches `<op>:<reason>` edges with the `#class` fallback over `done` / `needs_caller` / `error`, and an
unmatched operation outcome is fail-safe. A `needs_caller` result binds through `escalate`. What has
no home is the class of failures where **the policy never ran** — the engine is absent, does not
conform to the invocation contract, or refuses below the floor. No policy edge can match those,
because there was no operation.

The gap surfaced while verifying decision 0042's post-conditions; 0042 carries the `version_floor` pin
as a day-one implementation constraint, which is what made the missing consumer-side half visible. It
predates 0042 and is not caused by it.

## Options considered

- **Option A — a new `Engine Invocation Failures` class, scoped to pre-policy failures (chosen).**
  Covers exactly: the engine being unavailable or not conforming to the invocation contract, a
  below-`version_floor` refusal, and a usage/configuration result in which the policy did not run.
  Recovered repository-scoped, mirroring `Repository Provisioning Failures` (decision 0034), with a
  documented `Implementation-defined` park-vs-retry for persistent cases. Trade-offs: one more class
  to carry, but its boundary is sharp — it ends where Section 9.12 begins — and its blast radius
  matches an existing class exactly, so the recovery text is a known shape rather than a new one.
- **Option B — extend `Workflow/Config Failures` (class 1).** The precedent is real: "Missing
  coding-agent executable" already lives there, and an absent engine is the same shape. Trade-offs:
  cheapest, no renumbering — but class 1's recovery is the dispatch-validation disposition, "skip new
  dispatches, keep service alive", which is instance-wide. `version_floor` and the policy are declared
  in `repo.policy.toml`, so a below-floor engine or a malformed policy is *repository*-scoped. Folding
  it into class 1 would either halt the whole instance for one repository's bad floor or force a
  caveat that breaks class 1's uniform disposition. Rejected on the scope mismatch, not the cost.
- **Option C — add no class; rely on the action-policy machine's unmatched-outcome fail-safe.**
  Trade-offs: no spec growth at all, and it correctly covers everything *after* the policy starts. But
  exit code `2` means the policy did not run, so by construction no edge can match and the fail-safe
  never fires. Rejected as structurally unable to cover the case.
- **Option D — treat it as a per-worker failure and retry with exponential backoff.** Trade-offs:
  needs no new class and reuses the retry queue — but a below-floor engine, a missing binary, and a
  malformed policy are configuration defects, not transients. Backoff never converges on them; it just
  spends the retry budget. Rejected.

## Decision and reasoning

Choose **Option A**, scoped tightly to failures where the policy did not run.

The scoping is the substance of the decision. An "engine failures" class that also swallowed
operation outcomes would duplicate and eventually contradict Section 9.12, which is the document's
single owner of what happens when an operation returns a reason. Drawing the boundary at *did the
policy run* keeps the two mechanisms disjoint and makes the class trivially decidable from the result
envelope: `status`/exit `2` and the pre-invocation cases belong here, everything else belongs to the
policy machine.

Recovery mirrors `Repository Provisioning Failures` because the blast radius is identical. Both the
`version_floor` and the policy live in the repository's `repo.policy.toml`, so a bad one affects every
issue for that repository and no others: skip that repository's dispatches for the tick, keep the
service alive, retry on a later tick, and do not convert to a per-worker backoff. Persistent cases MAY
be parked under a documented `Implementation-defined` policy — the same clause three neighbouring
classes already carry, so the pattern is established rather than invented.

The engine being absent or non-conforming is instance-wide rather than repository-scoped, but it is
covered by the same class because the *disposition* is the same one level up: no dispatch can proceed,
the service stays alive, and the condition is a configuration defect an operator must clear. Splitting
it into a separate class would add a row to Section 14.1 that shares every behavior with this one.

We would reconsider if the engine contract grows an outcome that is neither an operation result nor a
pre-policy refusal — the boundary would then no longer be exhaustive; if `version_floor` moves out of
`repo.policy.toml` to an operator-owned surface, which would make the failure instance-scoped and
merge the class into `Workflow/Config Failures` after all (Option B); or if implementations find the
repository-scoped skip too coarse because one repository's engine floor is routinely different from
another's, suggesting the floor belongs to the engine pin rather than the policy.

The decision is **Accepted**; the `SPEC.md` change is planned in `Plan.md` and not yet applied.
