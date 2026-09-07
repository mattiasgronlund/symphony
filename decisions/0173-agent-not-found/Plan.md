# Plan — 0173 One adapter's name in a normalized vocabulary

## Scope

`SPEC.md` Section 10.6 (Timeouts and Error Mapping) and `conformance/vocabulary.json`'s
`agent_error_categories` group.

Nothing else names the token: Section 17.5, Section 18, `CONFORMANCE-STATEMENT-TEMPLATE.md` and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` name no agent error category, which was checked.

## Steps

1. **Section 10.6's category is adapter-neutral.** Ensure the error-mapping list carries
   `agent_not_found` in place of `codex_not_found`, in the same position, with no condition stated —
   the list states none for any of its nine entries and this decision does not change that.
   Done when Section 10.6 lists `agent_not_found` and `codex_not_found` does not appear in
   `SPEC.md`.

2. **The registry follows.** Ensure `conformance/vocabulary.json`'s `agent_error_categories`
   entries carry `agent_not_found` in place of `codex_not_found`, in the same position. The group's
   `note` is correct as written — its general phrasing about "an agent adapter" is what this
   decision confirms — and its statement that Section 10.6 states no condition for any entry stays
   true.
   Done when the registry lists `agent_not_found` and no artifact outside `decisions/` carries the
   old spelling.

## Cross-cutting sync

- **Section 6.4, Section 17, Section 18** — unaffected. No configuration key changes, and no check
  or checklist item names an agent error category.
- **Conformance Statement templates** — no row owed and none affected. Section 10.6's
  MUST-document obligation is for categories an implementation defines *beyond* the nine, and its
  row (`Agent-runner error categories defined beyond Section 10.6's set`) names no specific token.
- **Conformance corpus vectors** — unaffected. No vector file asserts an agent error category.
- **`VCSX-SPEC.md`** — unaffected. The agent runner is not the engine's.

## Anchor changes

- `codex_not_found` → `agent_not_found` (Section 10.6, Timeouts and Error Mapping; and
  `conformance/vocabulary.json`'s `agent_error_categories`). A code-token identifier renamed. The
  old spelling survives only in decision 0102's `Background.md`, as a recorded measurement of the
  set as it stood, which is history and is not edited.

## Status

Applied to `SPEC.md` (Section 10.6's error-mapping list) and `conformance/vocabulary.json`
(`agent_error_categories`). Both steps. Outside `decisions/` and `DECISIONS.md`, the old spelling
no longer occurs.
