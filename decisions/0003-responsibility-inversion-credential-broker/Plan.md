# Plan — 0003 Responsibility inversion and the credential broker boundary

## Scope

Reframes Symphony from "tracker reader" to "privileged broker" across `SPEC.md`. Touches the Section 1
"Important boundary", Goals and Non-Goals (Section 2), the agent integration material where
`linear_graphql` lives (Section 10.5), the "Tracker Writes (Important Boundary)" (Section 11.5), and
"Secret Handling" (Section 15.3). Introduces two cross-cutting concepts used by later decisions: the
`symphony` broker CLI and the per-run broker socket. Socket and sandbox mechanics are owned by 0004;
the config split is owned by 0005; this decision establishes the principle and the boundary.

## Steps

1. Ensure `SPEC.md` states that Symphony performs all privileged outward side effects (VCS remote
   operations, pull-request creation, and all issue-tracker interaction) and that the agent supplies
   only operation content and holds no credentials. Done when the Section 1 "Important boundary" and
   the "Tracker Writes" boundary describe the broker model rather than the reader-only model.
2. Ensure a `symphony` broker CLI is defined as the sole channel for agent-requested side effects,
   reached over a per-run socket, with a fixed neutral core verb set plus an extension mechanism (the
   verb set itself is detailed in 0007). Done when the CLI and its per-run socket are named and
   cross-referenced to 0004.
3. Ensure brokered operations return structured results (status plus reason code) and that a scoped
   authorization denial (`scope_denied`) is REQUIRED to fail the run. Done when the result contract
   and the `scope_denied` run-fatal rule appear.
4. Ensure the secret-handling contract states: secrets resolve through a provider interface with a
   required file provider; environment variables are not a permitted secret channel into the agent;
   all secret-bearing environment variables MUST be scrubbed before the agent sandbox is started;
   `$VAR` indirection is retained only for non-secret path values. Done when "Secret Handling" carries
   these clauses.
5. Ensure `linear_graphql` is retired in favour of the broker CLI. Done when the in-protocol tool is
   removed/superseded and no normative text depends on it.

## Cross-cutting sync

Config cheat sheet (6.4): secret-related entries change once 0005 lands the policy/`WORKFLOW.md`
split. Test matrix (17) and checklist (18): add broker-CLI and scope-enforcement conformance rows and
remove the `linear_graphql` extension rows. Coordinate with 0005–0008 so shared rows are added once.

## Anchor changes

- `linear_graphql` (client-side tool extension, Sections 10.5, 11.5, 17.5, 18.2) — removed, superseded
  by the `symphony` broker CLI.
- `$VAR` indirection for secret values (`tracker.api_key` in 5.3.1, Sections 6.1 and 15.3) — removed
  for secrets; retained for non-secret path values only.
- New anchors introduced: `symphony` (broker CLI), `scope_denied` (error/category code), the per-run
  broker socket concept (mechanics in 0004).
- Section 3.1 components — added `Privileged Operation Broker`; `Status Surface` and `Logging`
  renumbered to items 8 and 9.
- New subsection Section 10.8 "Privileged Operation Broker (`symphony` CLI)".
- Section 11.5 "Tracker Writes (Important Boundary)" — retitled to "Tracker Writes (Broker Boundary)"
  and reframed to the broker model (the full reader→read+write reversal continues in 0008).

## Status

Applied to `SPEC.md` on branch `broker-rearchitecture-0003-0009`.
