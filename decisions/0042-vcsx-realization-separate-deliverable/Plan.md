# Plan — 0042 Realize `vcsx` as a separate deliverable, engine-direct first

## Scope

No `SPEC.md` edit. This decision fixes realization and sequencing for a layer whose specified shape is
already settled and applied (0027, 0028, 0039, 0040), and `SPEC.md` already carries the text the
decision would otherwise have to add: Section 3.4 "Layers, the VCS Engine, and Deployment Topologies"
states the engine is an independent deliverable pinned as an external tool and released on its own
cadence, and Section 5.6 `repo.policy.toml` defers the field-level schema — including `[engine]`
`version_floor` — to the engine contract.

The plan therefore records verification post-conditions plus the constraints the first engine commits
must satisfy, and names the follow-on this decision deliberately does not take.

## Steps

1. **No normative `SPEC.md` edit.** Ensure Section 3.4 "Layers, the VCS Engine, and Deployment
   Topologies" still describes the `VCS Engine` as an independent deliverable pinned as an external
   tool, and Section 5.6 "`repo.policy.toml` (Repository Way of Working)" still defers the field-level
   schema to `VCSX-CONTRACT.md`. Done when both hold and no edit is made.
2. **Realization constraint.** Ensure the engine is developed as its own codebase, reached over the
   invocation contract in `VCSX-SPEC.md` Section 8 "The Engine Invocation Contract", with Symphony
   pinning it by `version_floor`. Done when the engine builds and runs with no Symphony source on its
   dependency path.
3. **Sequencing constraint.** Ensure the first topology realized is `engine-direct` (Section 3.4): the
   engine driven by an operator holding credentials, with no Broker Core and no daemon. Done when
   `ship` and `land` drive a real repository's `repo.policy.toml` end to end with no Symphony
   component present.
4. **Carry the execution-context labeling from the start.** Ensure engine operations and policy edges
   are labeled `host_side` / `in_sandbox` (`VCSX-SPEC.md` Section 3.2 "Execution Contexts (Trust)")
   even while `engine-direct` splits no policy across a sandbox boundary. Done when a policy edge can
   declare `context` and the engine honors it, with no consumer yet supplying a boundary.
5. **Carry the version pin from the start.** Ensure `[engine]` `version_floor` (`VCSX-SPEC.md`
   Sections 6.2 and 8.5) is read and enforced fail-closed — an engine below the floor refuses to run
   with a usage/config result — before any consumer depends on it. Done when a below-floor engine
   refuses rather than executing the policy.

## Out of scope

- **Per-topology conformance profiles.** Section 3.4 marks the VCS engine `OPTIONAL` while Section 18.1
  requires a VCS engine and the action-policy machine for Core Conformance; the two read as a
  contradiction until conformance is split per topology (broker-core / daemon / engine-direct), each
  with its own Section 17 / 18 subset. That split needs its own decision and `SPEC.md` edit; this
  decision only records that choosing `engine-direct` first makes it the next one to take.
- Seeding the engine from an existing wrapper layer (Option C in `Background.md`) is permitted but not
  required, and is a build choice rather than a specification one.

## Cross-cutting sync

None. No config key, test-matrix row, or checklist item changes: the config cheat sheet (Section 6.4),
test matrix (Section 17), and implementation checklist (Section 18) already describe the engine layer
this decision schedules rather than redefines.

## Anchor changes

None.

## Status

Applied — no `SPEC.md` edit required; the `DECISIONS.md` chapter is added and the decision folder is
recorded.
