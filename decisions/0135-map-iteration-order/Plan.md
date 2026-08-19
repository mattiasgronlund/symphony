# Plan — 0135 The map a template can iterate, and the order it never had

## Scope

- `SPEC.md` — Section 12.2 (Rendering Rules), Section 17.1 (Workflow and Config Parsing),
  Section 18.1.3 (Daemon Conformance).
- `conformance/vectors/prompt-rendering.json` — the file-level description and three new vectors.
- `conformance/README.md` — one "Surfaced findings" entry.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. The decision fixes a behaviour the document
  had left unstated; it adds no `Implementation-defined` behaviour and no "MUST document"
  obligation, so no row is owed (`CLAUDE.md`, decision 0128).
- `conformance/vocabulary.json` — **no change**. No token is added, renamed or removed.
- `SPEC.md` Section 6.4 — **no change**. No configuration key is involved.

## Steps

1. **`SPEC.md` Section 12.2 (Rendering Rules) — the rendering rules fix the order a map iterates
   in.** Ensure the bullet list retains "Preserve nested arrays/maps (labels, blockers, metadata) so
   templates can iterate." and gains a following bullet requiring a map's entries to be yielded in
   ascending order of key compared by Unicode code point, each entry a two-element key/value pair
   with the key first, and a list to be yielded in list order. Keep the imperative register of the
   four bullets beside it; the section states rules rather than RFC 2119 clauses. *Done when:*
   Section 12.2 states an order for a map, the new bullet begins with a verb as its neighbours do,
   and no bullet is removed.
2. **`SPEC.md` Section 12.2 (Rendering Rules) — a `Note:` records what the comparison does not
   depend on.** Ensure the note states that comparing by code point makes the order independent of
   the host's locale, applies no Unicode normalization form, and that comparing the keys' UTF-8
   bytes yields the same order, so an implementation whose template engine hands it an unordered map
   can sort on the way out. Follow the aside label set the document already uses. *Done when:*
   Section 12.2 carries one `Note:` aside naming the locale, the normalization form and the UTF-8
   byte comparison, and it introduces no new `Implementation-defined` behaviour.
3. **`SPEC.md` Section 12.2 (Rendering Rules) — the reach of the order is stated.** Ensure a
   paragraph states that the rule governs the maps a template names by path — the `issue` object,
   whose fields are the ones Section 4.1.1 (Issue) defines, and `metadata` — and that a blocker ref
   is reached by iterating `blocked_by` and read by field name, so iterating a blocker ref's own
   fields is outside this contract and no order is fixed for it. *Done when:* the paragraph names
   `blocked_by`, cites Section 4.1.1 for the issue field set, and fixes no order for a blocker ref's
   own fields.
4. **`SPEC.md` Section 17.1 (Workflow and Config Parsing) — the matrix carries the order check.**
   Ensure a `Daemon Conformance` bullet sits with the three prompt-rendering bullets, the first of
   which is "Prompt template renders `issue` and `attempt`", asserting that a map iterates in
   ascending key order by Unicode code point with each entry a two-element key/value pair, key
   first, and that a list iterates in list order. *Done when:* Section 17.1 has four
   prompt-rendering bullets and the new one carries its `Daemon Conformance` marker.
5. **`SPEC.md` Section 18.1.3 (Daemon Conformance) — the checklist item covers the order.** Ensure
   the item that reads "Strict prompt rendering with `issue` and `attempt` variables, failing
   `template_render_error`" also requires map iteration in ascending key order, citing Section 12.2.
   *Done when:* the bullet names both the strict-failure behaviour and the iteration order, and no
   second bullet is added for it.
6. **`conformance/vectors/prompt-rendering.json` — the file-level `description` states the order.**
   Ensure it records that a map iterates in ascending key order by Unicode code point and that an
   entry is a two-element key/value pair with the key first, so a reader knows which sections the
   new vectors' expected values are read from. Ensure `spec_refs` still names Sections 5.4, 5.5 and
   12.2, which already cover the rule's home. *Done when:* the file parses and its description names
   the order and the entry shape.
7. **`conformance/vectors/prompt-rendering.json` — `iterate-metadata-map` pins the order and the
   entry shape.** A three-key `metadata` map supplied in an order that is not ascending — keys
   `zeta`, `mu`, `alpha` — rendered by a single-line template that emits both halves of each entry,
   expecting `[alpha=a][mu=m][zeta=z]`. Three keys rather than two, because two agree by chance one
   time in two. *Done when:* the vector exists with `id` `iterate-metadata-map`, its expected string
   is ascending by key, and its description states that a harness whose JSON parser reorders object
   keys still checks the order, since the expectation does not depend on the supplied order.
8. **`conformance/vectors/prompt-rendering.json` — `iterate-issue-object` pins the container.** A
   vector iterating the `issue` object itself and emitting each entry's key, over an issue carrying
   exactly the fields Section 4.1.1 (Issue) defines, expecting those field names in ascending order.
   *Done when:* the vector exists with `id` `iterate-issue-object`, its `given.issue` carries every
   Section 4.1.1 field and no other, and its description records that the expectation rests on that
   field set being the normalized record's.
9. **`conformance/vectors/prompt-rendering.json` — `iterate-metadata-map-non-ascii` separates code
   point order from a collation.** Keys `apple`, `år` and `ärlig`, whose code-point order differs
   from what a locale collation gives: en_US orders `år` before `ärlig`, and a Swedish tailoring
   orders both after `apple` in the other sequence, while ascending by code point gives `apple`,
   `ärlig`, `år`. *Done when:* the vector exists with `id` `iterate-metadata-map-non-ascii`, its
   non-ASCII code points are written as `\uXXXX` escapes so the file stays pure ASCII as the corpus
   requires, and its description records that the three keys sort the same way in NFC and NFD, so it
   tests the comparison rather than the normalization form.
10. **`conformance/README.md` — the gap is recorded as resolved under "Surfaced findings".** Ensure
    an entry states the gap in the terms the corpus meets it: `render_prompt` is a checked function
    whose output was unspecified for a map, `iterate-labels` already established iteration as
    in-contract, and Section 12.2 now fixes the order, the comparison and the entry shape, pinned by
    the three new vectors. *Done when:* the entry names decision 0135 and the three vector ids.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change; no configuration key is involved.
- `SPEC.md` Section 17 (test matrix) — step 4, one bullet in Section 17.1.
- `SPEC.md` Section 18 (implementation checklist) — step 5, one existing bullet in Section 18.1.3
  extended rather than a new one added.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed and none added. The decision creates no
  `Implementation-defined` behaviour and no "MUST document" obligation; it removes an unstated
  choice, which is the opposite direction from the rule decision 0128 wrote.
- `conformance/vocabulary.json` — unchanged. The decision adds no token.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. Prompt
  rendering is Symphony's, not the engine's.

## Anchor changes

None. No code token, error class, field name or section title is renamed or removed. Section 12.2
gains a bullet, a `Note:` aside and a paragraph; Sections 17.1 and 18.1.3 gain and extend one bullet
each; the corpus gains three vector ids — `iterate-metadata-map`, `iterate-issue-object` and
`iterate-metadata-map-non-ascii` — none of which replaces an existing one.

## Status

Applied to `SPEC.md` (Sections 12.2, 17.1, 18.1.3), `conformance/vectors/prompt-rendering.json` and
`conformance/README.md`. Issue #93.
