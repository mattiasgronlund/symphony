# Plan — NNNN <Decision title>

<!--
A detailed plan for how this decision is implemented in SPEC.md. Concrete enough to execute and to
check off later. Preserve SPEC.md's style and level of description (see CLAUDE.md).
-->

## Scope

<Which sections of SPEC.md are affected. New sections, edits, or removals. Name them by stable
identity (see Steps), not by line or paragraph position.>

## Steps

<!--
Address by stable identity, never by line/column or paragraph ordinal (see decision 0002):
- Prefer code-token identifiers (field/error/state/event/file names); then section titles; cite a
  section number only as a secondary hint, paired with its title, e.g. Section 8.4 "Retry and
  Backoff".
- Phrase each step as a declarative post-condition ("ensure X exists with Default: Z"), not an
  imperative positional diff. Quote a short unique nearby token when prose must be located.
- State a recognizable done-condition so the step is self-checking and idempotent on re-execution.
-->

1. <Target anchor (code-token or section title) + the end-state to ensure + done-condition.>
2. <...>

## Cross-cutting sync

<Updates needed in the config cheat sheet (6.4), test matrix (17), and checklist (18), if any.>

## Anchor changes

<!--
Append-only record of anchors this decision renames or removes, so stale references in other plans
can be chased. List code-token renames/removals and section retitles as old → new, or
removed/superseded-by. Do not maintain a separate registry of current anchors — SPEC.md is the source
of truth for what exists now (see decision 0002).
-->

None.

## Status

<Not started / In progress / Applied to SPEC.md. Link commits or PRs when relevant.>
