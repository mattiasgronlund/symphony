# Plan — 0046 Conformance corpus, first slice

## Scope

A new `conformance/` tree, spec-adjacent (not normative `SPEC.md` prose):

- `conformance/README.md` — what the corpus is, the vector-file schema, the language-neutral harness
  contract, the profile scoping, what the slice covers, what is deferred, and surfaced findings.
- `conformance/vectors/*.json` — one file per pure behavior, expected outputs derived verbatim from
  the cited `SPEC.md` sections.

On acceptance, one normative pointer is added to `SPEC.md`; no existing section renumbers.

## Steps

1. **Create the vector files.** Ensure `conformance/vectors/` holds one JSON file per first-slice
   function — `sanitize_workspace_key`, `normalize_state`, `resolve_config_defaults`,
   `retry_backoff_delay_ms`, `available_slots`, `per_state_concurrency_limit`, `sort_for_dispatch` —
   each with `function`, `profile`, `spec_refs`, `description`, and a `vectors` array whose expected
   outputs are read from the `spec_refs` sections. Done when every file parses as JSON and every
   expected value traces to its cited section. *(Applied as a draft with this decision.)*

2. **Create the corpus README.** Ensure `conformance/README.md` documents the schema, the harness
   contract (invoke `function` with `given`, assert equality; note the `sort_for_dispatch` ordering
   and `resolve_config_defaults` dotted-path interpretations), the coverage table, the deferred
   behaviors, and the surfaced-findings section. Done when the README names every vector file and its
   deriving sections. *(Applied as a draft with this decision.)*

3. **Point Section 17 at the corpus (on acceptance).** Ensure Section 17 "Test and Validation
   Matrix" intro names the `conformance/` corpus as the RECOMMENDED machine-readable realization of
   the deterministic checks it lists, without making it a REQUIRED gate and without restating any
   check. Done when one sentence in Section 17's intro references the corpus and the
   `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 7 evidence row still reads true. *(Applied.)*

4. **Open the non-ASCII sanitization clarification (on acceptance).** Record a follow-on decision
   resolving whether "character" in Section 9.5 Invariant 3 (and Section 4.2 Workspace Key) is a
   byte, a Unicode code point, or a grapheme, then add the corresponding non-ASCII vector. Done when
   the ambiguity is resolved in `SPEC.md` and a vector encodes it. *(Planned; separate decision.)*

## Cross-cutting sync

- Section 17: changed by step 3 (one pointer sentence, on acceptance).
- Section 18, Section 6.4: no change.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no change — its Section 7 "Shared conformance corpus" evidence
  row already anticipates this corpus.

## Anchor changes

Added — `conformance/README.md`, `conformance/vectors/*.json` (new spec-adjacent tree). On
acceptance, a corpus pointer sentence in Section 17's intro. Removed — none. Renamed — none.

## Status

Steps 1–3 applied. Step 1: `conformance/vectors/` holds 7 files / 31 vectors, all parsing. Step 2:
`conformance/README.md` documents the schema, harness contract, coverage, deferrals, and surfaced
findings. Step 3: `SPEC.md` Section 17's intro points at the corpus as the RECOMMENDED
machine-readable realization of its deterministic checks. Step 4 (the non-ASCII sanitization
clarification) remains a separate follow-on decision.
