# Background — 0002 Stable addressing of SPEC.md from decision plans

## Context

Each decision under `decisions/` carries a `Plan.md` describing how it changes `SPEC.md`. We want
those plans to be as independent of one another as possible: re-executable in a different order, or
re-executable after another plan has inserted or removed text in the middle, without the addressing
silently pointing at the wrong place.

Positional addressing degrades fast under exactly these operations. Line and column numbers break on
any edit above the target. Paragraph or bullet ordinals break on any insert/remove before the
target. Even `SPEC.md`'s decimal section numbers are only *semi*-stable: `CLAUDE.md` requires
numbering to be kept contiguous and cross-references updated when sections are inserted or reordered,
so a plan that cites "Section 8.4" can come to point at a different section after an unrelated
decision inserts ahead of it.

A second, related problem: anchors themselves can change. A section can be retitled, and a code-token
identifier (a field name, error code, or state name) can be renamed or removed by a later decision.
A plan written against the old anchor then has a dangling reference.

## Options considered

### How to address locations

- **Positional (line/column, paragraph ordinal).** Rejected outright: degrades on any insert/remove
  or reorder, which is precisely the workload we expect.
- **Section number only (`8.4`).** Convenient for navigation but mutable under renumbering; a stale
  number fails silently by resolving to the wrong section.
- **Stable identity + declarative end-state (chosen).** Address by the most durable handle available
  — code-token identifiers first, section titles next, section numbers only as a secondary hint —
  and phrase each step as a convergent post-condition ("ensure X exists with default Z") rather than
  an imperative diff ("insert after paragraph 3"). Identity survives reordering; a declarative target
  is idempotent under re-execution and makes a moved/renamed anchor fail *loudly* (the post-condition
  cannot be satisfied) instead of being silently mis-applied.

### How to handle anchor renames/removals

- **A standalone anchor registry (a side file listing current valid anchors).** Rejected. For
  code-tokens and section titles, `SPEC.md` is already the source of truth for what currently exists;
  a second file restating that must be kept in sync, is unenforced, and rots — and a wrong registry
  is worse than none. It also reintroduces a shared mutable hotspot, the very coupling positional
  addressing forced on us.
- **Append-only rename/removal record, co-located with its cause (chosen).** The decision that
  performs a rename already has a `Plan.md`; record the event there in an `Anchor changes` section.
  This keeps a single source per fact (the rename lives with the reasoning that justified it), is
  append-only (renames are events, never edited later, so no conflict surface), and is derivable —
  the full history is a grep over `decisions/`, the same way `DECISIONS.md` is a thin index over the
  folders. It separates the two questions a registry conflates: "what anchors exist now?" (answer:
  `SPEC.md`) from "what did anchor `X` become?" (answer: the rename record).

## Decision and reasoning

Adopt stable-identity, declarative addressing for `Plan.md` steps, and record anchor renames/removals
append-only in the `Anchor changes` section of the decision that causes them. No standalone anchor
registry.

The reinforcing insight is that a declarative post-condition turns the rename problem into a feature:
if an anchor moved out from under a not-yet-applied plan, re-execution cannot satisfy the
post-condition and surfaces the conflict for re-evaluation, rather than auto-translating stale intent
through a map. A `Plan.md` already marked applied is a historical record, not a live query against
current `SPEC.md`, so the dangling-reference risk is confined to `Proposed` plans — a small window.

We would reconsider — specifically, add a *generated* (not hand-maintained) index of anchor changes —
if grepping the per-decision `Anchor changes` sections becomes painful at scale. Even then the
per-decision sections remain the source of truth and the index is derived from them.
