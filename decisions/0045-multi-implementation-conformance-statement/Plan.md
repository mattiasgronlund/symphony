# Plan — 0045 Multi-implementation conformance: the Conformance Statement

## Scope

Two deliverables:

- `CONFORMANCE-STATEMENT-TEMPLATE.md` at the repo root — the template each implementation copies into
  its own repo and fills. Created with this decision.
- A new normative section in `SPEC.md`, titled `Conformance Statement`, requiring a conforming
  implementation to publish one, and pointing consumers at it. Planned here, not yet applied.

No existing requirement is added, removed, or weakened: the Statement consolidates obligations that
`SPEC.md` already imposes (`Implementation-defined` / `MUST document` clauses, the Section 14.3
recovery-class assignment, the Section 1 / 9.6 trust-posture documentation, the Section 8.5 / 10.2
version floors) and pointers into 0043's profiles and Section 18.2's extensions. `VCSX-SPEC.md` and
`VCSX-CONTRACT.md` are unchanged.

## Steps

1. **Create the template.** Ensure `CONFORMANCE-STATEMENT-TEMPLATE.md` exists at the repo root with a
   fillable section for each contract-visible choice: identity and targeted revisions; the claimed
   layer profiles and deployment topology (`Broker Core Conformance`, `Daemon Conformance`,
   `engine-direct` / `interactive-agent` / `daemon`); the OPTIONAL extensions shipped with their
   config namespaces; the pinned engine `version_floor` and agent protocol floor; a
   pre-enumerated `Implementation-defined` / `MUST document` resolution table; a pre-enumerated
   Orchestrator Runtime State recovery-class table; the trust and safety posture; conformance-corpus
   and Real Integration Profile results; and known deviations. Done when the file exists and every
   `Implementation-defined` / `MUST document` obligation in `SPEC.md` has a row, and every
   Orchestrator Runtime State field (Section 4.1.8) has a row. *(Applied with this decision.)*

2. **Introduce the requirement in `SPEC.md`.** Add a new normative section titled
   `Conformance Statement`, placed after `Implementation Checklist (Definition of Done)` (the current
   last section). Ensure it states that a conforming implementation MUST publish a Conformance
   Statement; that the Statement MUST record the implementation's claimed profiles and topology
   (deferring the vocabulary to Section 3.4 and the test matrix), the OPTIONAL extensions shipped,
   the pinned engine and agent-protocol floors, a resolution for every `Implementation-defined` /
   `MUST document` obligation, the recovery class assigned each Orchestrator Runtime State field, and
   the trust and safety posture; and that `CONFORMANCE-STATEMENT-TEMPLATE.md` is the RECOMMENDED
   shape. Ensure the section names the Statement as the single home the scattered "MUST document"
   obligations publish to, without restating each obligation's substance. Done when the section
   exists, is reachable by its title, and adds no obligation not already present elsewhere in
   `SPEC.md`. *(Planned; not yet applied.)*

3. **Point the existing documentation obligations at the Statement.** Ensure Section 14.3's "the
   assignment MUST be documented" sentence, the Section 1 trust-and-safety-posture documentation
   clause, and the Section 9.6 sandbox-profile clause each name the Conformance Statement as where
   the documented choice is published (a pointer, not a restatement). Done when each of those
   clauses references the `Conformance Statement` section and none duplicates its content. *(Planned;
   not yet applied.)*

4. **Reference the Statement from the checklist.** Ensure Section 18 (Definition of Done) includes,
   under the shared `Both Layer Profiles` group, a single item requiring a published Conformance
   Statement, scoped as `Core Conformance`. Done when the checklist item exists and cites the
   `Conformance Statement` section. *(Planned; not yet applied.)*

## Cross-cutting sync

- Section 6.4 "Core Config Fields Summary (Cheat Sheet)": no change — the Statement records choices,
  not config fields.
- Section 17 "Test and Validation Matrix": no requirement change; the shared conformance corpus named
  in `Background.md` is a separate deliverable, not part of this edit.
- Section 18 "Implementation Checklist": changed by step 4 (one shared-profile item).
- Sections 1, 9.6, 14.3: changed by step 3 (pointers only).

## Anchor changes

Added — `Conformance Statement` (new `SPEC.md` section title, step 2);
`CONFORMANCE-STATEMENT-TEMPLATE.md` (new root file, step 1). Removed — none. Renamed — none.

## Status

All steps applied.

- Step 1: `CONFORMANCE-STATEMENT-TEMPLATE.md` created at the repo root.
- Step 2: Section 19 "Conformance Statement" added after Section 18, requiring a conforming
  implementation to publish one and enumerating what it MUST record; the format is
  `Implementation-defined` with the template named as the RECOMMENDED shape.
- Step 3: the Section 14.3 recovery-class-assignment sentence, the Section 1 trust-and-safety-posture
  clause, and the Section 9.6 sandbox-profile clause each now point at the Conformance Statement
  (Section 19) as pointers, not restatements.
- Step 4: Section 18.1.1 "Both Layer Profiles" gained one item requiring a published Conformance
  Statement, scoped `Core Conformance`.

Section citations verified at apply time: approval/user-input is Section 10.5, egress and sandbox
are Section 9.6, the agent protocol floor is in Section 10's preamble, and the deployment-declared
`version_floor` is Section 18.1.4. No existing section renumbered — Section 19 appends after the
prior last section (18).
