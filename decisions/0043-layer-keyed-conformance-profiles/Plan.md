# Plan — 0043 Layer-keyed conformance profiles

## Scope

`SPEC.md` Sections 3.4, 17 (intro and 17.1–17.7 scoping), 18.1, and 18.2, plus a profile declaration
on each OPTIONAL extension section. No requirement is added, removed, or weakened: Section 18.1's
bullets are regrouped under the layer that owns them, and Sections 17.1–17.7 gain a profile scope.
`VCSX-SPEC.md` and `VCSX-CONTRACT.md` are unchanged — engine conformance is deferred to
`VCSX-SPEC.md` Section 13, not restated.

## Steps

1. **Define the profile vocabulary.** In Section 17 "Test and Validation Matrix", ensure the
   `Validation profiles:` list defines `Broker Core Conformance` and `Daemon Conformance` as the two
   components of `Core Conformance`, alongside the existing `Extension Conformance` and
   `Real Integration Profile`, and that `Core Conformance` is stated as the umbrella over the two
   layer profiles rather than as a peer of them. Done when all four names are defined in one place and
   every later use of `Core conformance` in the document still reads true.

2. **Retire the blanket scoping sentence.** Ensure the sentence beginning "Unless otherwise noted,
   Sections 17.1 through 17.7 are" no longer assigns one profile to all seven subsections, and instead
   states that each subsection declares its profile and that bullets beginning "If … is implemented"
   remain `Extension Conformance`. Done when no sentence claims 17.1–17.7 are uniformly one profile.

3. **State topologies as compositions.** In Section 3.4 "Layers, the VCS Engine, and Deployment
   Topologies", ensure each topology names the profiles it composes: `engine-direct` = a conforming
   engine alone; `interactive-agent` = `Broker Core Conformance` + a conforming engine; `daemon` =
   `Broker Core Conformance` + `Daemon Conformance`, plus a conforming engine under the condition in
   step 5. Ensure the existing claim that the Broker Core "is independently conformant" resolves to
   `Broker Core Conformance` by name. Ensure the phrase "optionally driving the VCS Engine" is left
   unchanged. Done when each of the three topologies carries its composition and the independent-
   conformance claim names a profile.

4. **Regroup Section 18.1 by layer.** Ensure "18.1 REQUIRED for Conformance" contains three groups —
   Broker Core, Autonomous Daemon, and VCS Engine — with every existing bullet appearing under exactly
   one. Allocation:
   - `Broker Core Conformance`: the Privileged Operation Broker over a per-run socket with
     authorization scope and `scope_denied`; the per-run agent sandbox with scrubbed secret-bearing
     env; the outward-credential / repo-internal-integrity secret split; the executor and the
     always-present orchestrator↔executor seam; the workspace manager with sanitized per-issue
     workspaces; workspace lifecycle hooks at two trust levels with `hooks.timeout_ms`; repository
     object-store provisioning and `Repository Provisioning Failures`; the neutral agent runner
     contract with the `codex` and `claude_code` adapters, the turn-centric `run_turn` / `cancel` /
     `release` contract and capability descriptors; `codex.command`; the typed config layer's
     secret-provider resolution and `$` expansion; the trust-sourcing rule over the three
     configuration artifacts; the tracker *write* surface (`set_state` idempotence,
     `tracker_state_unreachable` / `tracker_state_conflict`, the write-capability descriptor and
     `tracker_unsupported_operation`, the `secret` | `none` auth mode).
   - `Daemon Conformance`: the polling orchestrator with single-authority mutable state; complete
     `fetch_candidate_issues` enumeration; the tracker *read* surface (candidate fetch, state refresh,
     terminal fetch); multi-repo routing with shared per-tracker polling and (repository, issue) keying;
     the exponential retry queue with continuation retries and `agent.max_retry_backoff_ms`;
     reconciliation that stops runs on terminal/non-active states; workflow path selection and the
     `WORKFLOW.md` loader; strict prompt rendering with `issue` and `attempt`; agent and effort
     selection from `default_agent` / `default_effort` with `agent_by_label`; operator-visible
     observability.
   - `VCS Engine`: the engine's plugin layer realizing push/back-merge and the forge operations; the
     forge plugin's one-PR-per-issue with its capability descriptor; the action-policy machine; message
     formulation; the repository-owned transition graph the machine binds `set_state` from.
   - The Section 3.4 layering bullet stays ungrouped as the statement the three groups realize.
   Done when the union of the three groups equals the prior flat list, no bullet appears twice, and
   `Enabler-not-enforcer layering` still heads the section.

5. **State the conditional engine requirement.** Ensure the VCS Engine group states that the engine
   layer is REQUIRED of any deployment performing a remote VCS or forge operation (push, back-merge,
   `create_pr`, merge), and that a conforming engine's own obligations are those of `VCSX-SPEC.md`
   Section 13 rather than anything restated here. Done when the condition and the deferral both
   appear and no engine test-matrix or checklist item is duplicated into `SPEC.md`.

6. **Scope Sections 17.1–17.7.** Ensure each subsection declares its profile, with item-level scoping
   only where a subsection is mixed:
   - 17.2 "Workspace Manager and Safety", 17.5 "Coding-Agent Adapters" — `Broker Core Conformance`.
   - 17.4 "Orchestrator Dispatch, Reconciliation, and Retry", 17.6 "Observability", 17.7 "CLI and Host
     Lifecycle" — `Daemon Conformance`.
   - 17.1 "Workflow and Config Parsing" — mixed: workflow-path and `WORKFLOW.md` parsing items are
     `Daemon Conformance`; secret-provider resolution and trust-sourced hook items are
     `Broker Core Conformance`.
   - 17.3 "Issue Tracker Client" — mixed, on the same read/write line as step 4.
   Done when each of the seven subsections carries a profile line and only 17.1 and 17.3 carry
   item-level scoping.

7. **Each OPTIONAL extension declares the profile it extends.** Ensure the extension sections name
   their profile and that Section 18.2 mirrors it: Sections 8.8, 8.9, 8.10, 9.11, 13.3, and 13.8
   extend `Daemon Conformance`; Sections 13.6 and 13.7 extend `Broker Core Conformance` (both are
   executor- and agent-event-scoped); Section 13.4 is scoped to whichever profile the deployment
   claims. Done when every OPTIONAL section names a profile and Section 18.2's corresponding bullet
   agrees with it.

## Cross-cutting sync

- Section 6.4 "Core Config Fields Summary (Cheat Sheet)": no change. It lists fields and defaults; the
  extension-owned namespaces (`budget.*`, `quota.*`, `compute.*`, `server.*`, `[tasks]`/`[driver]`)
  already carry their ownership, and profile membership is derivable from the owning section.
- Section 17: changed by steps 1, 2 and 6.
- Section 18: changed by steps 4, 5 and 7.
- Section 14.3 "State Recovery Classes" and the OPTIONAL extensions' "Core conformance does not
  require these fields" clauses: verify they still read true with `Core Conformance` as an umbrella;
  no edit expected.

## Anchor changes

Added — `Broker Core Conformance`, `Daemon Conformance` (profile names, Section 17); the three
layer groups under Section 18.1 "REQUIRED for Conformance".

Refined — `Core Conformance` keeps its name and becomes the umbrella over the two layer profiles;
no use of the token elsewhere in `SPEC.md` changes meaning.

Removed — none. Renamed — none.

## Status

Not started. Decision Accepted; the `SPEC.md` edit above is planned and not yet applied.
