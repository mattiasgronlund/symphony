# Plan — 0139 An obligation answered in full, and the heading that did not say so

## Scope

- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the `need` Vocabulary Emitted heading.
- `VCSX-SPEC.md` — **no change**. The obligation sentence is correct prose and is not edited to suit
  a counting tool.
- `scripts/validate_spec_consistency.py` — **no change**. No exemption is added; the obligation is
  real and is answered, so suppressing it would assert something false.
- `SPEC.md`, `CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/` — **no change**. Nothing Symphony
  owns is involved.

## Steps

1. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the answering section cites the obligation it
   answers.** Ensure the section titled "`need` Vocabulary Emitted" ends its heading with a
   parenthetical naming the `VCSX-SPEC.md` section whose obligation it discharges, so the
   whole-subsection form the validator counts can see it. Five subsection headings in the same
   file already carry such a parenthetical — the three reason-token subsections and the two
   plugin-backend subsections — and this is the only answering section without one. Ensure the
   section's body, its introductory sentence, and every row of its table are unchanged. *Done
   when:* the heading names its governing section, the table still lists the eight registry needs
   plus an `<other>` row, and `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0
   warnings.

   Note on addressing: this step deliberately does not quote the sibling headings, because each
   embeds a section citation of its own and a quotation of one reads as the plan attributing that
   section to this document — which is how the first draft of this step was written, and it drew
   eleven anchor-check findings that were all the same artifact.

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1 (test matrix), 13.2 (implementation checklist) and 13.3 (Conformance
  Statement obligations) — no change. The decision adds no obligation, removes none, and changes no
  behavior a matrix row could assert; it makes an existing answer countable.
- `SPEC.md` Sections 6.4, 17 and 18 — no change; nothing Symphony owns is involved.
- Neither Conformance Statement template gains or loses a row.

## Anchor changes

- **Changed:** the `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` section titled "`need` Vocabulary
  Emitted" gains a trailing parenthetical naming its governing section. Three decision plans cite
  the old title in prose — 0059, 0132 and 0134 — and none is edited: they are the record of what was
  true when written, and each remains findable by the unchanged part of the title.

No token is renamed or removed. Every `need` token, reason token and section number is spelled
exactly as before.

## Status

Applied to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. Closes the last standing validator warning;
supersedes no decision, and revisits the disposition recorded in decisions 0132 and 0134.
