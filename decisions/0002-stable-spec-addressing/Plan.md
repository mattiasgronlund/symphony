# Plan — 0002 Stable addressing of SPEC.md from decision plans

## Scope

This decision is about the repository's working process — how `Plan.md` files address `SPEC.md` — not
`SPEC.md` content. It changes the `decisions/_template/Plan.md` skeleton and the `CLAUDE.md`
conventions, and edits no `SPEC.md` section.

## Steps

1. Establish the addressing conventions every `Plan.md` step follows:
   - Address by stable identity, in this order of preference: code-token identifiers (field names,
     error/category codes, state names, event names, file names) first; section titles next; section
     numbers only as a secondary navigation hint, always paired with the title, e.g. `Section 8.4
     "Retry and Backoff"`.
   - Never address by line/column or paragraph/bullet ordinal.
   - Phrase each step as a declarative post-condition ("ensure X exists with `Default: Z`") rather
     than an imperative positional diff. Where prose must be located, quote a short unique nearby
     token as the locator.
   - State a recognizable done-condition so the step is self-checking and idempotent under
     re-execution.
2. Add an `## Anchor changes` section to `decisions/_template/Plan.md`: an append-only list of
   code-token renames/removals and section retitles introduced by the decision (old → new, or
   removed/superseded-by), so stale references in other plans can be chased. Default content is
   `None.`
3. Document both conventions in `CLAUDE.md` (a short subsection under the decision-log guidance) so
   future sessions follow them.

## Cross-cutting sync

None in `SPEC.md` (no spec sections touched). The relevant sync is `CLAUDE.md` ↔
`decisions/_template/Plan.md` staying consistent about the conventions, and `DECISIONS.md` carrying
the chapter for this decision.

## Anchor changes

None. (This decision introduces the `Anchor changes` convention; it renames nothing in `SPEC.md`.)

## Status

Applied. `decisions/_template/Plan.md` carries the `Anchor changes` section, `CLAUDE.md` documents the
addressing and anchor-change conventions, and `DECISIONS.md` has the `0002` chapter.
