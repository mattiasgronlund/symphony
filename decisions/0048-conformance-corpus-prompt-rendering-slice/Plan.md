# Plan — 0048 Conformance corpus, prompt-rendering slice

## Scope

The corpus only; no `SPEC.md` change.

- `conformance/vectors/prompt-rendering.json` — the `render_prompt` vectors.
- `conformance/README.md` — the `expect` success-or-error union in the schema and harness contract,
  the coverage table (slice 2), the pruned "Deferred" list, and two surfaced findings.

## Steps

1. **Add the prompt-rendering vectors.** Ensure `conformance/vectors/prompt-rendering.json` defines
   `render_prompt` (profile `Daemon Conformance`, `spec_refs` Sections 5.4, 5.5, 12.2) with vectors
   covering: known-variable substitution, multi-field substitution, nested-list iteration,
   `attempt` as a present integer, unknown-variable failure (`template_render_error`), and
   unknown-filter failure (`template_render_error`). Templates are Liquid-compatible, single-line,
   delimiter-based. Done when the file parses and every expected value traces to its cited section.

2. **Document the `expect` union.** Ensure `conformance/README.md`'s vector-file schema and harness
   contract state that `expect` is either the successful result or `{ error: <class> }`, and that the
   harness asserts a raised error class for the latter. Add a `render_prompt` interpretation note.
   Done when the schema, step 2 of the contract, and the note all describe the union.

3. **Record the slice in coverage and prune "Deferred".** Ensure the coverage section lists slice 1
   (decision 0046) and slice 2 (decision 0048, the `render_prompt` row), and that "Prompt rendering"
   no longer appears under "Deferred to later slices". Done when the table carries the new row and the
   deferred list omits prompt rendering.

4. **Record the two findings.** Ensure "Surfaced findings" records the Section 5.4 syntax-floor gap
   and the `attempt` null/absent-versus-strict gap as open spec-clarification candidates. Done when
   both appear.

## Cross-cutting sync

- `SPEC.md`: no change. The two findings are candidates for follow-on clarification decisions, not
  part of this slice.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no change.

## Anchor changes

Added — `conformance/vectors/prompt-rendering.json`, the `render_prompt` function, and the `expect`
success-or-error union convention in the corpus schema. Removed — the "Prompt rendering" bullet from
the corpus "Deferred" list. Renamed — none.

## Status

Applied. `prompt-rendering.json` holds 6 vectors (corpus now 8 files / 39 vectors, all parsing); the
README documents the `expect` union, lists slice 2, prunes the deferred entry, and records the two
findings.
