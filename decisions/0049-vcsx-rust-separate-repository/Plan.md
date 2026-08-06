# Plan — 0049 Implement `vcsx` in Rust as a separate repository

## Scope

No `SPEC.md` or `VCSX-SPEC.md` edit. Both documents are deliberately neutral about the engine's
implementation language (`SPEC.md` Section 3.4 "Layers, the VCS Engine, and Deployment Topologies";
`VCSX-SPEC.md` Section 1.1 "What vcsx Is"), and this decision does not change that — it records a
choice made *outside* the normative text, exactly as decision 0045 established for contract-invisible
choices.

The plan therefore records the post-conditions the first engine repository must satisfy, and names the
follow-ons this decision deliberately does not take.

## Steps

1. **No normative edit to either specification.** Ensure `SPEC.md` Section 3.4 still states that the
   specification names no engine implementation or language normatively, and that `VCSX-SPEC.md`
   Section 1.1 remains language-neutral. Done when both hold and no edit is made.
2. **Separate repository.** Ensure the Rust engine lives in its own repository, with no
   specification-repository source on its build path and no engine source in this repository. Done
   when the engine builds from a clone of its own repository alone.
3. **Pinned toolchain.** Ensure the engine repository pins its Rust toolchain explicitly, so the
   `version_floor` guarantee (`VCSX-SPEC.md` Section 8.5) rests on a reproducible build. Done when a
   clean clone builds with the pinned toolchain and no implicit system Rust.
4. **Own decision log.** Ensure the engine repository carries its own decision log for
   contract-invisible choices, and that its introductory entry states the routing rule from 0045: a
   `VCSX-SPEC.md` / `VCSX-CONTRACT.md` change or gap routes a decision back to *this* log, while
   idiomatic Rust choices stay local. Done when that entry exists and names this decision as its
   parent.
5. **Exit codes re-derived, not carried.** Ensure every exit code the engine returns is derived from
   `VCSX-SPEC.md` Section 8.3 "Exit Codes" — `0` ok, `10` needs_caller, `20` error, `2` usage or
   configuration error — and not from the embedding repository's wrapper layer, whose numbering
   differs. Done when a test asserts each of the four codes against the Section 8.3 mapping.
6. **Envelope emitted regardless of exit code.** Ensure the result envelope
   (`VCSX-SPEC.md` Section 8.2 "Result Envelope") is written to stdout on every invocation, including
   failures, so the process entry point cannot return early through an error-propagation path that
   skips it. Done when a forced `error` and a forced usage error both still emit a parseable envelope.
7. **Execution-context labeling and the version floor carried from the first commit.** Ensure both
   constraints 0042 required survive into the Rust realization: policy edges and hooks carry
   `host_side` / `in_sandbox` labels (`VCSX-SPEC.md` Section 3.2), and `[engine]` `version_floor` is
   enforced fail-closed before the policy runs (Sections 6.2, 8.5). Done when a below-floor engine
   refuses with a usage/config result rather than executing.

## Out of scope

- **The crate layout, the async question, the error idiom, and the HTTP client.** These are
  contract-invisible under decision 0045 and belong in the engine repository's own decision log, not
  here.
- **Seeding from the embedding repository's wrapper layer.** Permitted as a design reference per
  0042's Option C and this decision's `Background.md`, but a build choice rather than a specification
  one. The one hard constraint — that its exit-code numbering must not be carried — is Step 5 above.
- **The three contract gaps this decision surfaced.** The engine's `Implementation-defined`
  obligations have no publication surface, the shared token vocabulary gains a third spelling across
  two repositories, and the no-embedding-consumer configuration is unnamed. Each needs its own
  decision and is taken up as 0050, 0051, and 0052 respectively.

## Cross-cutting sync

None. No config key, test-matrix row, or checklist item changes in either specification: this decision
schedules an implementation of an already-specified layer rather than redefining it.

## Anchor changes

None.

## Status

Applied — no specification edit required; the `DECISIONS.md` chapter is added and the decision folder
is recorded. Steps 2–7 are post-conditions on the engine repository, verified there rather than here.
