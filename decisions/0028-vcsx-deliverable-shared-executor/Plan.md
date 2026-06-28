# Plan — 0028 `vcsx` as an independent deliverable; one shared policy executor

## Scope

Affected anchors in `SPEC.md`:

- A new "VCS engine" deferral boundary, analogous to the Codex-app-server-protocol deferral the spec
  already makes — defers the engine **contract** (protocol, `ship`/`land`, the policy executor) to
  `vcsx` and does not duplicate the engine schema.
- Sections 9.7 "VCS Adapter", 9.8 "Git Automation and Work Branch", 9.9 "Broker Git Verbs", 9.10
  "Forge Adapter, Pull Requests, and Review Writes" — recast so the broker verbs are realized through
  the engine contract; relocate forge/transport neutrality into the engine's plugin layer.
- A statement of the **one-executor-two-front-ends** invariant.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Engine deferral boundary.** Ensure `SPEC.md` defers the VCS-engine *contract* to `vcsx` (its
   protocol, `ship`/`land`, the policy executor) and explicitly does not duplicate the engine schema,
   mirroring the existing Codex-protocol deferral. Done when the deferral is stated and no engine
   schema is restated in `SPEC.md`.

2. **Contract, not binary.** Ensure the spec requires conformance to the engine *contract* and names
   the binary only as the canonical realization (language-agnostic preserved). Done when no runtime or
   language is named normatively.

3. **One executor, two front-ends.** Ensure the spec states that interactive `ship`/`land` and the
   daemon execute the **same** engine policy executor over the **same** repository policy
   (decision 0029), differing only in initiator and `escalate` binding (decision 0030). Done when the
   invariant and the two front-ends are described.

4. **Recast broker verbs (Sections 9.7–9.10).** Ensure the broker's commit/push/pr/merge are
   described as realized through the engine contract, with forge/transport neutrality
   (GitHub/Forgejo/…) expressed as the engine's plugin selection rather than parallel Symphony
   adapters. Done when Sections 9.7–9.10 reference the engine contract and 0007/0022's adapter roles
   are reconciled into it.

5. **Packaging.** Ensure the spec notes `vcsx` is an independent deliverable, pinned like `archdoc`
   (a mise tool) and released on its own cadence. Done when the deliverable/packaging note is present
   without naming an implementation language.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** note the engine selection lives in repo config (decision 0029),
  not operator config.
- **Section 17 (test matrix):** add a **topology-equivalence** case — the same `repo.policy.toml`
  yields the same behavior through `vcsx ship` (interactive) and through the daemon.

## Anchor changes

New terms: **policy-graph executor**, **front-end**, the **engine deferral boundary**. Refines
decisions 0007 and 0022 (their VCS/forge adapter roles fold into the engine contract and its plugin
layer). Depends on decision 0027.

## Status

Accepted; `SPEC.md` application not started. Decision 0027 (parent) is Accepted, clearing the
dependency. Application is deferred: it must land in step with the companion `vcsx` spec so the
contract names stay identical across both documents, and 0028's spec text forward-references
decisions 0029–0030 (repo policy, the action-policy machine). Apply with those.
