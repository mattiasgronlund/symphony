---
name: decision-record
description: Create or revise a decision in DECISIONS.md and decisions/NNNN-short-slug/, including the folder mechanics, the reasoning bar a Background.md must clear, and how a re-evaluation or a review finding is logged. Use before making a substantive change to SPEC.md or the vcsx documents.
---

# Decision Record

Capture the reasoning behind a change to `SPEC.md`, `VCSX-SPEC.md`, or `VCSX-CONTRACT.md` so the
decision can be re-evaluated later without re-deriving its context. Capture it *before* making the
spec change, so the reasoning is never lost to a change that already landed.

## Required reading

`DECISIONS.md` and its States legend; `decisions/_template/`; the two or three most recent decision
folders, which set the voice and depth; the sections of the spec the decision touches.

## Workflow

1. Copy `decisions/_template/` to `decisions/NNNN-short-slug/`, using the next zero-padded number.
2. Write `Background.md` to the bar below.
3. Write `Plan.md` as declarative post-conditions addressed by stable identity — see "Addressing
   SPEC.md from a Plan.md" in `CLAUDE.md` (decision 0002). Record renamed or removed anchors
   append-only in the `Anchor changes` section.
4. Add or update the decision's chapter in `DECISIONS.md`, including its **State**.
5. Append the session to `Sessions.md`: the transcript filename without `.jsonl` under
   `~/.claude/projects/<project>/`, plus a short human name.
6. Make the spec change, then reconcile the cross-cutting sections named in `CLAUDE.md`.

## The bar for Background.md

- **Argue from the mechanism.** Lead with what the defect does — the concrete failure path, which
  call branches on the bad value, what ships broken. Cite a prior decision as support, never as the
  reason: a decision justified by "a previous decision said to" preserves no reasoning that survives
  the precedent being revisited.
- **Verify the claims the recommendation turns on.** Check them against the real artifact — the
  upstream schema, the tool, the document — before recommending. Flagging a fact as needing
  verification is good; doing the check is better.
- **Steelman the option not taken** and record why it loses, in its own terms rather than as a foil.
- **Name a reconsideration trigger**: the evidence that would reopen this, stated so a later reader
  can recognize it arriving.
- **Record measurements next to the claim they support**, with the tool and version, so a later
  reader can re-run them instead of taking the conclusion on trust. A measurement kept elsewhere
  becomes a moral.

## Re-evaluating a decision

Logged like any other decision: update the **State**, extend `Background.md` with the new reasoning
rather than erasing the old, and append the session.

## Review findings

When a review changes a decision, record the finding in `Background.md` rather than fixing it
quietly. Name the shape the defect had, and say whether it was introduced by the repair for a
previous one — a repair that reproduced the failure it was repairing is usually the more useful
finding, and the count of recurrences belongs in the text.

## Boundary

This skill governs the decision log, not the spec's prose. For the wording of a normative clause the
decision introduces, use the `spec-guarantee` skill.
