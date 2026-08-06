# Plan — 0053 Engine conformance corpus, first slice

## Scope

`VCSX-SPEC.md` Section 13.1 gains a pointer to the corpus and nothing else; no `VCSX-CONTRACT.md` or
`SPEC.md` edit. The corpus is a derived view over behaviors those documents already fix, so authoring
it changes no requirement: Section 13.1 keeps its role as the test matrix, and the corpus is the
machine-readable realization of its deterministic subset — the same relationship, and the same pointer,
decision 0046 established between `SPEC.md` Section 17 and `conformance/vectors/`.

The specification repository gains `conformance/vcsx/vectors/` and an extended
`conformance/vcsx/README.md`.

## Steps

1. **`conformance/vcsx/vectors/match-edge.json` exists.** Ensure it covers the Section 5.3 ladder
   (exact over `op:#class` over `#class`), the Section 13.1 matching bullets (an `op:#class` edge
   catches an unnamed reason of that class; a `#class` edge catches an otherwise-unmatched result; a
   lifecycle position matches exactly with no class fallback), the Section 5.4 built-in defaults
   (`fail` for `error`, `escalate` for `needs_caller`, continue for `done`), the benign no-op for an
   unmatched signal, and from-context disambiguation. Done when each of those behaviors has at least
   one vector and every trigger, edge key, and action resolves against `vocabulary.json`.
2. **`conformance/vcsx/vectors/base-resolution.json` exists.** Ensure it covers `fixed` as the default
   strategy, `by_prefix` longest-prefix-wins (including a case where a shorter prefix also matches, so
   first-match fails the vector), and the empty-prefix default as the catch-all. Done when only valid
   configurations appear — an invalid `by_prefix` map is a `validate_policy` vector, since Section 6.10
   catches it before resolution runs.
3. **`conformance/vcsx/vectors/exit-codes.json` exists.** Ensure all four Section 8.3 codes are pinned,
   with `2` documented as "the policy did not run" rather than an escalation. Done when the four codes
   are covered.
4. **`conformance/vcsx/vectors/policy-validation.json` exists.** Ensure each of Section 6.10's five
   conditions has at least one failing vector and, where the boundary is informative, a passing
   counterpart: duplicate edge and duplicate transition; unknown operation, lifecycle position, action,
   and hook; `by_prefix` without an empty-prefix default; a `set_state` binding without a capable
   consumer; and a `version_floor` above the running version. Done when all five conditions are
   represented.
5. **Every expected value is derived, none invented.** Ensure each file's `spec_refs` cite the sections
   its expectations are read from, and that no vector encodes a behavior the specification does not
   fix. Done when each of the three gaps found during authoring is recorded as a finding rather than
   resolved by a guessed-at vector.
6. **`conformance/vcsx/README.md` documents the vector artifact alongside the registry.** Ensure it
   states the vector schema, the harness contract and its two interpretation notes, the coverage table,
   the deferral list, and the findings; and that it explains why `proto_class` has no vector file. Done
   when a reader can write a harness from the README alone.
7. **`VCSX-SPEC.md` Section 13.1 "Test Matrix" points at the corpus.** Ensure its opening states that
   the deterministic, host-independent subset of its checks is published as a machine-readable,
   language-neutral vector corpus under `conformance/vcsx/` (RECOMMENDED), that an engine records the
   result in its Conformance Statement, and that the corpus does not restate or replace the checks
   below. Done when the pointer exists and the matrix bullets are otherwise unchanged.
8. **The Symphony corpus tree is left untouched.** Ensure `conformance/README.md` and
   `conformance/vectors/` are unchanged. Done when the change adds no files outside
   `conformance/vcsx/`.

## Out of scope

- **Resolving the three findings.** Unmatched lifecycle position, the class form of a concrete
  task-state event, and the absence of a reason token for configuration errors are each recorded as
  spec-clarification candidates, in the shape 0046 used before 0047 resolved its finding.
- **Integration-dependent behavior.** The `ship` and `land` sequences, plugin and checkout-mode
  behavior, message formulation, and hook execution need fixtures or live services and belong to a
  later slice.
- **A harness.** The corpus specifies a harness *contract*, not a harness in any language, exactly as
  decision 0046 did. The Rust harness belongs in the engine repository (decision 0049).
- **A `proto_class` vector file.** Deliberately omitted; `vocabulary.json` is that registry and
  `match_edge` exercises the lookup in composition.

## Cross-cutting sync

None in any specification. Within the repository, `conformance/vcsx/README.md` gains the vector
sections and is retitled from the registry alone to the tree as a whole; `vocabulary.json` is unchanged
and is now also the cross-check target for the `match_edge` vectors' tokens.

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (decision 0050) already carries an evidence row for the shared
token vocabulary. Ensure it also admits vector-run evidence, so an engine can record the corpus result
alongside the vocabulary check. Done when the evidence section covers both.

## Anchor changes

None. All files under `conformance/vcsx/vectors/` are new, and the README change is additive.

## Status

Applied — `conformance/vcsx/vectors/` (4 files, 49 vectors) is created,
`conformance/vcsx/README.md` is extended, and `VCSX-SPEC.md` Section 13.1 gains the corpus pointer.
