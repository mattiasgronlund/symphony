# Plan — 0001 Adopt a decision log

## Scope

This decision is about the repository's working process, not `SPEC.md` content. It therefore changes
repo scaffolding and `CLAUDE.md`, and does not edit any `SPEC.md` section.

## Steps

1. Add `DECISIONS.md` at the repo root: intro, state definitions, naming convention, and one chapter
   per decision.
2. Add `decisions/_template/` with `Background.md`, `Plan.md`, and `Sessions.md` skeletons to copy.
3. Seed `decisions/0001-adopt-decision-log/` as the first decision and a worked example of the
   format.
4. Document the decision-log workflow in `CLAUDE.md` so future sessions follow it.

## Cross-cutting sync

None in `SPEC.md` (no spec sections touched). The relevant sync is `CLAUDE.md` ↔ `DECISIONS.md`
staying consistent about the conventions.

## Status

Applied. `DECISIONS.md`, `decisions/_template/`, this folder, and the `CLAUDE.md` section all exist.
