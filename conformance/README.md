# Symphony Conformance Corpus

Language-neutral test vectors that make the deterministic subset of `SPEC.md`'s conformance
behavior (Section 17, Test and Validation Matrix) an objective pass/fail, identical in every
implementation language. The corpus is the shared enforcement mechanism referenced by the
multi-implementation strategy: an implementation runs it against its own binary and reports the
result in its Conformance Statement (see `CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 7 evidence).

This is the **first slice**. It covers only pure, host-independent functions — no sandbox, tracker,
engine, filesystem, or network — so every implementation can run it on day one with no harness
infrastructure. Integration-dependent behaviors are deferred (see "Deferred" below).

## Layout

- `vectors/*.json` — one file per behavior, each a self-contained set of input/output vectors.

## Vector file schema

Each file is a JSON object:

- `function` (string) — the behavior under test. The harness dispatches on this name.
- `profile` (string) — the Section 17 validation profile the behavior belongs to
  (`Core Conformance` or `Daemon Conformance`).
- `spec_refs` (array of strings) — the `SPEC.md` sections the expected outputs are derived from,
  verbatim. Expected values are never invented; they are read from these sections.
- `description` (string) — what the function computes.
- `given` / `expect` (strings at the file level) — the human-readable shape of a vector's input and
  output for this function.
- `vectors` (array) — each with:
  - `id` (string) — unique within the file.
  - `description` (string, OPTIONAL) — what the case demonstrates.
  - `given` (object) — the inputs.
  - `expect` (object) — the expected outputs.

## Harness contract (language-neutral)

A conforming harness is small and written in each implementation's own language. For every file and
every vector it MUST:

1. Invoke the implementation's realization of `function` with `given`.
2. Assert the result equals `expect`.

Two functions carry an interpretation note beyond plain equality:

- `sort_for_dispatch` — `given.issues` is an unordered list; `expect.order` is the list of
  `identifier`s in the required dispatch order. Assert the produced order equals it.
- `resolve_config_defaults` — `expect.resolved` is a map of dotted config paths to values. Assert
  the resolved config equals each listed path; paths **not** listed are unconstrained (so
  Implementation-defined defaults are never pinned).

The harness itself is not specified here — only the contract above. The corpus prescribes no test
framework, assertion library, or file-loading mechanism.

## What this slice covers

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/workspace-key.json` | `sanitize_workspace_key` | Core | Sections 4.2, 9.5 |
| `vectors/state-normalization.json` | `normalize_state` | Core | Section 4.2 |
| `vectors/config-defaults.json` | `resolve_config_defaults` | Core | Sections 6.4, 17.1 |
| `vectors/retry-backoff.json` | `retry_backoff_delay_ms` | Daemon | Section 8.4 |
| `vectors/available-slots.json` | `available_slots` | Daemon | Section 8.3 |
| `vectors/per-state-concurrency.json` | `per_state_concurrency_limit` | Daemon | Sections 8.3, 4.2 |
| `vectors/dispatch-ordering.json` | `sort_for_dispatch` | Daemon | Sections 8.2, 16.2 |

## Deferred to later slices

These behaviors are conformance-relevant but not purely deterministic from inputs alone; they need a
harness with fixtures or live services and belong with the `Real Integration Profile` (Section 17.8):

- Config **secret-provider resolution** and `$VAR` / `~` expansion (Section 17.1) — I/O-bound.
- **Workspace safety invariants** (Section 9.5, Invariants 1–2: cwd and root containment) — filesystem
  and process state.
- **Tracker read/write** surfaces, candidate eligibility over live issues (Section 8.2, 11).
- **Action-policy machine** outcomes and **message formulation** (Sections 9.8–9.12) — engine-side,
  covered by `VCSX-SPEC.md`'s own matrix.
- **Prompt rendering** strictness (Section 17.1, Daemon) — deterministic but template-engine shaped;
  a candidate for the next pure slice.

## Surfaced findings

Authoring vectors exercises `SPEC.md` and surfaces under-specification. Per the multi-implementation
decision-log hygiene rule, a genuine gap becomes a decision rather than a guessed-at vector:

- **Non-ASCII workspace-key sanitization is under-specified.** Section 9.5 Invariant 3 replaces "any
  character not in `[A-Za-z0-9._-]`", but does not fix whether "character" is a byte, a Unicode code
  point, or a grapheme — and a precomposed vs. decomposed accented letter would then sanitize to a
  different length. Because implementations iterate strings differently by default, a non-ASCII
  vector would encode an answer the spec does not determine, so none is included. This is filed as a
  spec-clarification candidate.
