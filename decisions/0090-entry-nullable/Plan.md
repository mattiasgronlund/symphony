# Plan — 0090 `entry` is a described field, null exactly where no entry point was read

## Scope

`VCSX-SPEC.md`: Sections 8.2 "Result Envelope", 13.1 "Test Matrix", 13.2 "Implementation Checklist".
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/vectors/compose-envelope.json` and
`conformance/vcsx/README.md`.

No `VCSX-SPEC.md` Section 8.3 change: the exit code for this condition is `2`, as it already is, and
the reserved `1` keeps its meaning.

No `VCSX-CONTRACT.md` change: the result envelope is deferred to this document
(`VCSX-CONTRACT.md` Section 11).

## Steps

1. **`vcsx_version` (Section 8.2)** — ensure the field list carries a bullet stating that
   `vcsx_version` is the `MAJOR.MINOR` version of the engine that ran the invocation (Section 8.5).
   *Done when* the bullet exists and cites the version grammar.

2. **`entry` (Section 8.2)** — ensure the field list carries a bullet stating that `entry` is the
   Section 8.1 entry point the invocation ran, and that it is null **exactly where no Section 8.1 entry
   point was read** — `usage_or_config` carrying `arguments_unreadable` (Section 8.6), and nowhere
   else. Ensure the bullet states the boundary the two cases draw: an invocation decoded far enough to
   name an entry point reports it whatever failed afterwards, so a `ship` whose remaining arguments
   were unreadable carries `ship` and a first word that is not one of Section 8.1's ten carries null.
   Ensure the prose states why it is an "exactly where" rather than a "may be null", on the same
   ground the escalation rule below it is stated that way: a field a caller branches on before deciding
   anything else is enforceable only where both halves are fixed.
   *Done when* the bullet exists, the null case is named and bounded, and the two command-line shapes
   are distinguished.

3. **`message` (Section 8.2)** — ensure the field list carries a bullet stating that `message` is
   human-readable prose and that nothing parses it: every fact a consumer branches on has a field or a
   token of its own, so a consumer reading `message` for structure reads a surface no engine holds
   stable. *Done when* the bullet exists and states the no-parsing rule.

4. **Ordering (Section 8.2)** — ensure the three new bullets precede `status`, matching the order the
   example block already presents the fields in.
   *Done when* the field list reads `vcsx_version`, `entry`, `status`, `op`/`reason`/`class`,
   `escalation`, `outputs`, `message`, consumer-added fields.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Invocation contract" — an invocation whose arguments could not
  be decoded yields an envelope on stdout with `entry` null, `reason` `arguments_unreadable`, exit
  `2`; an invocation decoded far enough to name an entry point reports that entry point whatever failed
  after it; `entry` is non-null on every other path, including every other `usage_or_config` reason.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line so the envelope's
  described fields include the nullable `entry`.
- **Conformance Statement (Section 13.3)** — no new row: the field and its one null case are fixed
  rather than `Implementation-defined`.
- **`conformance/vcsx/vocabulary.json`** — replace the flat `envelope_fields` list with entries
  carrying a `token` and a `nullable` flag, so a generated envelope type takes its optionality from the
  registry rather than from the example.
- **`conformance/vcsx/vectors/compose-envelope.json`** — contribute the `entry`-nullability rows to the
  vector file decision 0089 introduces: `arguments_unreadable` with no entry point read yields a null
  `entry`; another `usage_or_config` reason keeps its entry; and `arguments_unreadable` reached after
  an entry point was read keeps it too, which is what bounds the null case by what was read rather
  than by the reason alone.

## Anchor changes

None. `vcsx_version`, `entry` and `message` are existing field names gaining descriptions; no token is
added, renamed or removed.

## Status

Applied to `VCSX-SPEC.md`.
