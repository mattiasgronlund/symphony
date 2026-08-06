# Symphony Conformance Corpus

Language-neutral test vectors that make the deterministic subset of `SPEC.md`'s conformance
behavior (Section 17, Test and Validation Matrix) an objective pass/fail, identical in every
implementation language. The corpus is the shared enforcement mechanism referenced by the
multi-implementation strategy: an implementation runs it against its own binary and reports the
result in its Conformance Statement (see `CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 7 evidence).

The corpus grows in **slices**. Every slice so far covers only pure, host-independent behavior — no
sandbox, tracker, engine, filesystem, or network — so every implementation can run it on day one with
no harness infrastructure. Integration-dependent behaviors are deferred (see "Deferred" below).

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
  - `expect` (object) — the expected outputs: either the successful result, or `{ error: <class> }`
    naming the error class the behavior must raise for a failure vector.

## Harness contract (language-neutral)

A conforming harness is small and written in each implementation's own language. For every file and
every vector it MUST:

1. Invoke the implementation's realization of `function` with `given`.
2. Assert the result equals `expect` — or, when `expect` names an `error`, that the behavior fails
   and raises that error class.

Some functions carry an interpretation note beyond plain equality:

- `sort_for_dispatch` — `given.issues` is an unordered list; `expect.order` is the list of
  `identifier`s in the required dispatch order. Assert the produced order equals it.
- `resolve_config_defaults` — `expect.resolved` is a map of dotted config paths to values. Assert
  the resolved config equals each listed path; paths **not** listed are unconstrained (so
  Implementation-defined defaults are never pinned).
- `render_prompt` — `expect` is either `{ rendered: <string> }` (assert the rendered string equals
  it) or `{ error: <class> }` (assert rendering fails with that error class). Templates use
  Liquid-compatible syntax (Section 5.4).

The harness itself is not specified here — only the contract above. The corpus prescribes no test
framework, assertion library, or file-loading mechanism.

## What the corpus covers

Slice 1 — pure derivations (decision 0046):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/workspace-key.json` | `sanitize_workspace_key` | Core | Sections 4.2, 9.5 |
| `vectors/state-normalization.json` | `normalize_state` | Core | Section 4.2 |
| `vectors/config-defaults.json` | `resolve_config_defaults` | Core | Sections 6.4, 17.1 |
| `vectors/retry-backoff.json` | `retry_backoff_delay_ms` | Daemon | Section 8.4 |
| `vectors/available-slots.json` | `available_slots` | Daemon | Section 8.3 |
| `vectors/per-state-concurrency.json` | `per_state_concurrency_limit` | Daemon | Sections 8.3, 4.2 |
| `vectors/dispatch-ordering.json` | `sort_for_dispatch` | Daemon | Sections 8.2, 16.2 |

Slice 2 — prompt rendering (decision 0048):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/prompt-rendering.json` | `render_prompt` | Daemon | Sections 5.4, 5.5, 12.2 |

## Deferred to later slices

These behaviors are conformance-relevant but not purely deterministic from inputs alone; they need a
harness with fixtures or live services and belong with the `Real Integration Profile` (Section 17.8):

- Config **secret-provider resolution** and `$VAR` / `~` expansion (Section 17.1) — I/O-bound.
- **Workspace safety invariants** (Section 9.5, Invariants 1–2: cwd and root containment) — filesystem
  and process state.
- **Tracker read/write** surfaces, candidate eligibility over live issues (Section 8.2, 11).
- **Action-policy machine** outcomes and **message formulation** (Sections 9.8–9.12) — engine-side,
  covered by `VCSX-SPEC.md`'s own matrix.

## Surfaced findings

Authoring vectors exercises `SPEC.md` and surfaces under-specification. Per the multi-implementation
decision-log hygiene rule, a genuine gap becomes a decision rather than a guessed-at vector:

- **Non-ASCII workspace-key sanitization — resolved (decision 0047).** Section 9.5 Invariant 3 did
  not fix whether "character" is a byte, a Unicode code point, or a grapheme, so a precomposed vs.
  decomposed accented letter would sanitize differently and no non-ASCII vector could be authored.
  Decision 0047 fixes the unit to the **UTF-8 byte**: replace every UTF-8 byte not in
  `[A-Za-z0-9._-]` with `_` — identical in every language with no Unicode library.
  `vectors/workspace-key.json` now carries precomposed (`café-01` → `caf__-01`) and decomposed
  (`e`+U+0301 → `cafe__-01`) vectors.
- **Template syntax is a floor, not a mandate (open).** Section 5.4 says a "Liquid-compatible
  semantics are sufficient" engine, which pins the strict-failure MUSTs and the `template_render_error`
  class but leaves the concrete delimiter/filter syntax to the implementation. Because `WORKFLOW.md`
  is repository-owned and must render on any implementation Symphony targets, the template syntax is
  effectively a cross-implementation contract; the slice authors the reference vectors in Liquid
  syntax. Tightening "sufficient" to a normative shared syntax is a spec-clarification candidate.
- **`attempt` "null or absent" versus strict mode (open).** Section 5.4 lists `attempt` as
  `null`/absent on the first run, but strict variable checking says unknown variables MUST fail. Whether
  a template that reads `attempt` on the first run renders empty (known-but-null) or fails (absent =
  unknown) is undetermined, so no first-run `attempt` vector is authored; the slice tests `attempt`
  only with an integer value. A spec-clarification candidate.
