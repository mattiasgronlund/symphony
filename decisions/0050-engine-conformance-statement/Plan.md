# Plan — 0050 Publish an engine Conformance Statement

## Scope

`VCSX-SPEC.md` gains one subsection under Section 13 "Conformance". The specification repository gains
one new artifact, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. No change to `SPEC.md`,
`VCSX-CONTRACT.md`, or `CONFORMANCE-STATEMENT-TEMPLATE.md`: the Symphony Statement already defers
engine conformance to `VCSX-SPEC.md` Section 13, and that deferral now resolves to a real clause
instead of a matrix and a checklist alone.

## Steps

1. **`VCSX-SPEC.md` Section 13 "Conformance" gains a `Conformance Statement` subsection.** Ensure a
   subsection exists after the `Implementation Checklist`, requiring a conforming engine to publish a
   Conformance Statement and enumerating what it MUST record: the engine version and the
   major-stable surface it claims (Section 8.5); a resolution for every `Implementation-defined`
   behavior in this specification; any reason token added beyond the Section 4.3 registry with its
   proto class; the `need` vocabulary the engine emits (Section 8.4); and the capability descriptors
   its VCS and forge plugins advertise (Section 9.3). Ensure it closes by naming
   `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` as the RECOMMENDED shape and the Statement's own format as
   `Implementation-defined`. Done when the subsection exists and restates no obligation's substance,
   only its location.
2. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` exists in the specification repository.** Ensure it is a
   checklist of pointers into `VCSX-SPEC.md` with a fillable row per obligation, carrying: identity and
   targeted revisions; the engine version and declared major-stable surface; the five
   `Implementation-defined` resolutions (checkout-mode detection, `repo.policy.toml` discovery
   precedence, hook `run` unit form, entry-point argument encodings, escalation `detail`); added reason
   tokens with their proto class; the `need` vocabulary; VCS and forge plugin capability descriptors;
   and conformance evidence with known deviations. Done when every obligation named in Step 1 has
   exactly one row and the template restates no requirement's substance.
3. **The template carries the upstream-routing rule.** Ensure its deviations row states that a
   divergence reflecting a genuine specification gap opens a decision in the specification
   repository's log, per decision 0045's decision-log hygiene. Done when the row names that routing.
4. **Cross-reference from the Symphony template is verified, not edited.** Ensure
   `CONFORMANCE-STATEMENT-TEMPLATE.md`'s conformance-claim section still defers engine conformance to
   `VCSX-SPEC.md` Section 13 and that the deferral now resolves. Done when the existing text holds
   with no edit.

## Out of scope

- **Making the Statement a gate.** Section 13.1's test matrix and Section 13.2's implementation
  checklist keep their existing roles; the Statement is a published declaration, not a precondition
  for running the engine.
- **A machine-readable manifest.** Decision 0045 deferred one for Symphony and the same reasoning
  applies here; the token vocabulary that *is* worth making machine-readable is taken up separately as
  decision 0051.
- **Filling the template for the Rust engine.** That belongs in the engine repository (decision 0049),
  once it has resolutions to record.

## Cross-cutting sync

None in `SPEC.md`. Within `VCSX-SPEC.md` the addition is confined to Section 13; no operation, reason,
trigger, action, or `repo.policy.toml` key changes, so Section 14's alignment rule with
`VCSX-CONTRACT.md` is unaffected — no shared token is added, renamed, or removed.

## Anchor changes

None. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is a new file, and the new `VCSX-SPEC.md` subsection is
an addition under an existing section title.

## Status

Applied to `VCSX-SPEC.md` (Section 13) and the specification repository
(`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`).
