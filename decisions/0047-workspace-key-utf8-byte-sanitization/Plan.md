# Plan — 0047 Workspace-key sanitization operates on UTF-8 bytes

## Scope

`SPEC.md` Sections 4.2 ("Workspace Key") and 9.5 (Invariant 3), the corpus vector file
`conformance/vectors/workspace-key.json`, and the corpus `conformance/README.md` surfaced-findings
entry. Also updates decision 0046's `Plan.md` follow-on marker. No section renumbers; the rule is
clarified, not renamed. Sections 6.4, 17, and 18 are unaffected.

## Steps

1. **State the byte rule in Section 9.5, Invariant 3.** Ensure the invariant says sanitization
   operates on the identifier's UTF-8 encoding — replace every byte not in `[A-Za-z0-9._-]` with `_`,
   so a non-ASCII code point yields one `_` per byte — and that the identifier is not normalized
   first (the invariant is a safe directory name, not a reversible one). Done when the invariant
   names the UTF-8 byte as the unit and the non-normalization is explicit.

2. **State the byte rule in Section 4.2, Workspace Key.** Ensure the `Workspace Key` derivation says
   "every byte of its UTF-8 encoding not in `[A-Za-z0-9._-]`" rather than "any character". Done when
   Sections 4.2 and 9.5 agree on the unit.

3. **Add the non-ASCII vectors.** Ensure `conformance/vectors/workspace-key.json` includes a
   precomposed case (`café-01`, é = UTF-8 `C3 A9`, expecting `caf__-01`) and a decomposed case
   (`cafe` + U+0301, U+0301 = UTF-8 `CC 81`, expecting `cafe__-01`), and that its `description`
   states the UTF-8-byte rule. Done when both vectors are present and the file parses.

4. **Mark the finding resolved.** Ensure `conformance/README.md`'s surfaced-findings entry records
   that this gap is resolved by decision 0047 to the UTF-8 byte, rather than left open. Done when the
   entry cites 0047 and the chosen unit.

5. **Close the 0046 follow-on.** Ensure decision 0046's `Plan.md` step 4 and status point at 0047 as
   the resolving decision. Done when 0046 no longer lists the clarification as unresolved.

## Cross-cutting sync

- Sections 6.4, 17, 18: no change.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no change.

## Anchor changes

None. The `Workspace Key` derivation and Invariant 3 are clarified in place; no code-token or section
title is renamed or removed.

## Status

Applied to `SPEC.md` (Sections 4.2, 9.5), `conformance/vectors/workspace-key.json` (two non-ASCII
vectors added; description updated), `conformance/README.md` (finding marked resolved), and decision
0046's `Plan.md` (follow-on closed).
